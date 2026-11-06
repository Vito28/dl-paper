"""Pembentukan target dan model hitung usia (Subbab 2.9 dan 3.5).

Model hitung pada persamaan (2.17)::

    ln mu_i = gamma_p(i) + f(ln(1 + a_i)) + beta^T c_i,   Var(v_i) = mu_i + kappa mu_i^2

diestimasi dengan maximum likelihood Negative Binomial (NB2). Efek produk gamma_p dimasukkan
sebagai parameter tetap per produk (embedding), sehingga model tetap bisa dipakai untuk ratusan
ribu ulasan. Fungsi usia f memakai basis spline yang dipusatkan terhadap data latih model,
sehingga f bernilai rata-rata nol dan konstanta seluruhnya diserap oleh efek produk.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import SplineTransformer

COVARIATES = ["rating", "verified_purchase", "log_review_length"]


# ---------------------------------------------------------------- target mentah
def target_t1(votes) -> np.ndarray:
    """Persamaan (2.15)."""
    return np.log1p(np.asarray(votes, dtype=np.float64))


# ---------------------------------------------------------------- basis usia
class AgeBasis:
    """Basis fungsi usia f(ln(1 + a)). ``kind`` = "linear" atau jumlah knot spline."""

    def __init__(self, kind):
        self.kind = kind

    def fit(self, log_age: np.ndarray) -> "AgeBasis":
        x = np.asarray(log_age, dtype=np.float64).reshape(-1, 1)
        if self.kind == "linear":
            self.mu_, self.sd_ = float(x.mean()), float(x.std() or 1.0)
            B = (x - self.mu_) / self.sd_
        else:
            self.spl_ = SplineTransformer(n_knots=int(self.kind), degree=3, extrapolation="linear",
                                          include_bias=False)
            B = self.spl_.fit_transform(x)
        self.center_ = B.mean(axis=0)
        return self

    def transform(self, log_age: np.ndarray) -> np.ndarray:
        x = np.asarray(log_age, dtype=np.float64).reshape(-1, 1)
        B = (x - self.mu_) / self.sd_ if self.kind == "linear" else self.spl_.transform(x)
        return (B - self.center_).astype(np.float32)


# ---------------------------------------------------------------- NB2 dengan efek produk
def nb_loglik(y: torch.Tensor, mu: torch.Tensor, log_kappa: torch.Tensor) -> torch.Tensor:
    r = torch.exp(-log_kappa)                     # r = 1 / kappa
    return (torch.lgamma(y + r) - torch.lgamma(r) - torch.lgamma(y + 1)
            + r * (torch.log(r) - torch.log(r + mu)) + y * (torch.log(mu) - torch.log(r + mu)))


def nb_deviance(y: np.ndarray, mu: np.ndarray, kappa: float) -> float:
    y = np.asarray(y, dtype=np.float64)
    mu = np.asarray(mu, dtype=np.float64)
    r = 1.0 / kappa
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = np.where(y > 0, y * np.log(y / mu), 0.0)
    t2 = (y + r) * np.log((y + r) / (mu + r))
    return float(2.0 * np.sum(t1 - t2))


@dataclass
class FitResult:
    basis: AgeBasis | None
    w: np.ndarray              # koefisien basis usia
    beta: np.ndarray           # koefisien kovariat
    cov_stats: dict            # standardisasi kovariat
    kappa: float
    loglik: float
    deviance: float
    gamma: dict                # efek produk (parent_asin -> nilai)

    def f(self, log_age: np.ndarray) -> np.ndarray:
        if self.basis is None:
            return np.zeros(len(log_age), dtype=np.float64)
        return self.basis.transform(log_age).astype(np.float64) @ self.w


def _cov_matrix(df: pd.DataFrame, stats: dict | None):
    X = df[COVARIATES].to_numpy(dtype=np.float64)
    if stats is None:
        stats = {"mu": X.mean(0), "sd": X.std(0) + 1e-9}
    return ((X - stats["mu"]) / stats["sd"]).astype(np.float32), stats


def fit_age_model(df: pd.DataFrame, basis_kind="linear", use_age: bool = True, steps: int = 400,
                  lr: float = 0.05, l2_gamma: float = 1e-4, device: str | None = None,
                  verbose: bool = False, basis: AgeBasis | None = None) -> FitResult:
    """Estimasi NB2 dengan efek produk. ``use_age=False`` memberi model pembanding tanpa usia.
    ``basis`` = basis usia yang sudah di-fit (dipakai bootstrap agar knot spline tidak berpindah)."""
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    y = torch.tensor(df["helpful_vote"].to_numpy(np.float32), device=device)
    pid_codes, prods = pd.factorize(df["parent_asin"])
    pid = torch.tensor(pid_codes, device=device, dtype=torch.long)
    C_np, cov_stats = _cov_matrix(df, None)
    C = torch.tensor(C_np, device=device)
    if use_age and basis is None:
        basis = AgeBasis(basis_kind).fit(df["log_age"].to_numpy())
    basis = basis if use_age else None
    B = torch.tensor(basis.transform(df["log_age"].to_numpy()), device=device) if use_age else None

    # inisialisasi efek produk dari rata-rata suara produk
    pm = df.groupby(pid_codes)["helpful_vote"].mean().to_numpy()
    gamma = torch.nn.Parameter(torch.tensor(np.log(pm + 0.1), dtype=torch.float32, device=device))
    beta = torch.nn.Parameter(torch.zeros(C.shape[1], device=device))
    w = torch.nn.Parameter(torch.zeros(B.shape[1], device=device)) if use_age else None
    log_kappa = torch.nn.Parameter(torch.zeros((), device=device))
    params = [gamma, beta, log_kappa] + ([w] if use_age else [])
    opt = torch.optim.Adam(params, lr=lr)
    n = len(df)
    for step in range(steps):
        opt.zero_grad()
        eta = gamma[pid] + C @ beta + (B @ w if use_age else 0.0)
        mu = torch.exp(eta.clamp(-20, 15))
        ll = nb_loglik(y, mu, log_kappa).sum()
        loss = -ll / n + l2_gamma * (gamma ** 2).mean()
        loss.backward()
        opt.step()
        if verbose and step % 100 == 0:
            print(step, float(-ll / n), float(torch.exp(log_kappa)))
    with torch.no_grad():
        eta = gamma[pid] + C @ beta + (B @ w if use_age else 0.0)
        mu = torch.exp(eta.clamp(-20, 15))
        ll = float(nb_loglik(y, mu, log_kappa).sum())
        kappa = float(torch.exp(log_kappa))
        dev = nb_deviance(df["helpful_vote"].to_numpy(), mu.cpu().numpy(), kappa)
    return FitResult(basis=basis, w=(w.detach().cpu().numpy().astype(np.float64) if use_age else np.zeros(0)),
                     beta=beta.detach().cpu().numpy().astype(np.float64), cov_stats=cov_stats, kappa=kappa,
                     loglik=ll, deviance=dev, gamma=dict(zip(prods, gamma.detach().cpu().numpy())))


def heldout_fit(fit: FitResult, df: pd.DataFrame, steps: int = 300, lr: float = 0.05,
                device: str | None = None) -> dict:
    """Log-likelihood dan deviance pada produk baru (validasi). f, beta, dan kappa dibekukan, hanya
    efek produk baru yang diestimasi karena merupakan parameter pengganggu."""
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    y = torch.tensor(df["helpful_vote"].to_numpy(np.float32), device=device)
    pid_codes, _ = pd.factorize(df["parent_asin"])
    pid = torch.tensor(pid_codes, device=device, dtype=torch.long)
    C_np, _ = _cov_matrix(df, fit.cov_stats)
    fixed = torch.tensor(C_np @ fit.beta.astype(np.float32) + fit.f(df["log_age"].to_numpy()).astype(np.float32),
                         device=device)
    pm = df.groupby(pid_codes)["helpful_vote"].mean().to_numpy()
    gamma = torch.nn.Parameter(torch.tensor(np.log(pm + 0.1), dtype=torch.float32, device=device))
    lk = torch.tensor(np.log(fit.kappa), dtype=torch.float32, device=device)
    opt = torch.optim.Adam([gamma], lr=lr)
    for _ in range(steps):
        opt.zero_grad()
        mu = torch.exp((gamma[pid] + fixed).clamp(-20, 15))
        (-nb_loglik(y, mu, lk).mean()).backward()
        opt.step()
    with torch.no_grad():
        mu_t = torch.exp((gamma[pid] + fixed).clamp(-20, 15))
        ll = float(nb_loglik(y, mu_t, lk).sum())
        mu = mu_t.cpu().numpy()
    return {"loglik": ll, "deviance": nb_deviance(df["helpful_vote"].to_numpy(), mu, fit.kappa)}


def select_basis(train: pd.DataFrame, val: pd.DataFrame, grid, **kw) -> tuple[object, pd.DataFrame]:
    """Pilih bentuk fungsi usia (linear atau spline) dengan log-likelihood data validasi terbesar.
    Bukan deviance, karena setiap basis punya kappa sendiri dan deviance NB dengan kappa berbeda
    tidak bisa dibandingkan (lihat ``age_effect_stats``). Deviance tetap dicatat sebagai informasi."""
    rows = []
    for kind in grid:
        fit = fit_age_model(train, basis_kind=kind, **kw)
        ho = heldout_fit(fit, val)
        if not np.isfinite(ho["loglik"]):
            raise ValueError(f"log-likelihood validasi basis {kind} tidak valid: {ho['loglik']}")
        rows.append({"basis": str(kind), "train_loglik": fit.loglik, "val_loglik": ho["loglik"],
                     "train_deviance": fit.deviance, "val_deviance": ho["deviance"], "kappa": fit.kappa})
    tab = pd.DataFrame(rows)
    best = tab.loc[tab["val_loglik"].idxmax(), "basis"]
    best = "linear" if best == "linear" else int(best)
    return best, tab


def age_effect_stats(loglik_full: float, loglik_noage: float, df: int) -> dict:
    """Kontribusi komponen usia untuk RM3, dihitung dari log-likelihood saja.

    Deviance NB bergantung pada dispersi kappa, dan model dengan dan tanpa usia masing-masing punya
    kappa sendiri. Selisih kedua deviance itu karena itu tidak bermakna (bisa negatif walaupun usia
    jelas memperbaiki model). Ukuran yang dipakai adalah uji rasio likelihood dan pseudo-R2 McFadden
    terhadap model tanpa usia, ``1 - LL_full / LL_noage`` (bagian log-likelihood yang diperbaiki usia)."""
    from scipy.stats import chi2
    if not (np.isfinite(loglik_full) and np.isfinite(loglik_noage) and loglik_noage < 0):
        raise ValueError(f"log-likelihood tidak valid: full={loglik_full}, tanpa usia={loglik_noage}")
    lr_stat = 2.0 * (loglik_full - loglik_noage)
    return {"lr_stat": float(lr_stat), "df": int(df), "p_value_lr": float(chi2.sf(lr_stat, df)),
            "loglik_gain_share": float(1.0 - loglik_full / loglik_noage)}


def age_effect_summary(full: FitResult, noage: FitResult) -> dict:
    """Ringkasan untuk RM3. ``deviance_full`` dan ``deviance_noage`` masing-masing dihitung dengan
    kappa modelnya sendiri, jadi JANGAN dibandingkan langsung (lihat ``age_effect_stats``)."""
    return {
        "loglik_full": full.loglik, "loglik_noage": noage.loglik,
        **age_effect_stats(full.loglik, noage.loglik, len(full.w)),
        "deviance_full": full.deviance, "deviance_noage": noage.deviance,
        "kappa_full": full.kappa,
    }


def age_curve(fit: FitResult, ages_days: np.ndarray, ref_days: float = 30.0) -> np.ndarray:
    """Efek multiplikatif usia terhadap rata-rata suara, relatif terhadap usia acuan.
    Nilai 2,0 berarti rata-rata suara yang diharapkan dua kali lipat dibanding ulasan berusia ``ref_days``."""
    la = np.log1p(np.asarray(ages_days, dtype=np.float64))
    return np.exp(fit.f(la) - fit.f(np.log1p(np.array([ref_days])))[0])


def bootstrap_age_curve(train: pd.DataFrame, full: FitResult, ages_days, n_boot: int, seed: int,
                        **kw) -> np.ndarray:
    """Kurva usia hasil bootstrap pada tingkat produk, untuk IK kurva ``full``.

    Setiap ulangan mengambil ulang produk (dengan pengembalian) dari SELURUH ``train``, yaitu data yang
    sama dengan yang dipakai ``full``, dan memakai basis usia ``full`` (knot spline tetap). Dengan begitu
    sebaran bootstrap berpusat pada estimasi yang sama dengan kurva yang dilaporkan."""
    if full.basis is None:
        raise ValueError("bootstrap_age_curve butuh model dengan komponen usia.")
    rng = np.random.default_rng(seed)
    base = train[["parent_asin", "helpful_vote", "log_age", *COVARIATES]]
    codes, prods = pd.factorize(base["parent_asin"])
    order = np.argsort(codes, kind="stable")
    base = base.iloc[order].reset_index(drop=True)
    counts = np.bincount(codes)
    starts = np.r_[0, np.cumsum(counts)[:-1]]
    curves = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(prods), size=len(prods))
        idx = np.concatenate([np.arange(starts[p], starts[p] + counts[p]) for p in pick])
        sample = base.iloc[idx].copy()
        # produk yang terambil lebih dari sekali dianggap produk berbeda
        sample["parent_asin"] = np.repeat(np.arange(len(pick)), counts[pick])
        fit = fit_age_model(sample, basis=full.basis, **kw)
        curves.append(age_curve(fit, ages_days))
    return np.vstack(curves)


def age_curve_table(full: FitResult, boots: np.ndarray, ages_days) -> pd.DataFrame:
    """Tabel kurva usia (``tables/age_kurva.csv``): rasio dari ``full`` dan IK 95% persentil bootstrap.
    Kolom ``di_luar_ik`` menandai titik yang estimasinya keluar dari IK-nya sendiri, dan jumlahnya
    dicetak, karena hal itu menandakan bootstrap tidak sejalan dengan estimasi."""
    ages = np.asarray(ages_days, dtype=np.float64)
    ratio = age_curve(full, ages)
    lo, hi = np.quantile(boots, [0.025, 0.975], axis=0)
    tab = pd.DataFrame({"age_days": ages, "ratio": ratio, "lo": lo, "hi": hi})
    tab["di_luar_ik"] = (ratio < lo) | (ratio > hi)
    n_out = int(tab["di_luar_ik"].sum())
    print(f"IK kurva usia dari {len(boots)} ulangan bootstrap. Titik di luar IK-nya sendiri: {n_out} dari {len(tab)}"
          + ("" if n_out == 0 else ". PERIKSA sebelum dilaporkan."))
    return tab


# ---------------------------------------------------------------- target terkoreksi usia
def oof_age_component(train: pd.DataFrame, basis_kind, n_folds: int, seed: int, **kw) -> np.ndarray:
    """f-hat out-of-fold untuk data latih. Fold dikelompokkan per produk."""
    rng = np.random.default_rng(seed)
    prods = train["parent_asin"].unique()
    fold_of = dict(zip(prods, rng.integers(0, n_folds, size=len(prods))))
    fold = train["parent_asin"].map(fold_of).to_numpy()
    out = np.full(len(train), np.nan)
    for k in range(n_folds):
        tr = train[fold != k]
        fit = fit_age_model(tr, basis_kind=basis_kind, **kw)
        idx = np.where(fold == k)[0]
        out[idx] = fit.f(train["log_age"].to_numpy()[idx])
    if not np.isfinite(out).all():
        raise ValueError(f"{(~np.isfinite(out)).sum()} komponen usia out-of-fold kosong/NaN "
                         "(ada fold tanpa produk?). Target T3 tidak bisa dibentuk.")
    return out


def target_t3(votes, f_hat: np.ndarray, f_bar: float) -> np.ndarray:
    """Persamaan (2.18)."""
    return target_t1(votes) - (np.asarray(f_hat) - f_bar)


# ---------------------------------------------------------------- tingkat relevansi
def fit_grade_thresholds(y_train_t1: np.ndarray, y_train_target: np.ndarray | None = None) -> np.ndarray:
    """Persamaan (3.3).

    T1 dan T2: q1 = 0, sedangkan q2..q4 adalah kuartil target positif pada data latih.
    T3: ambang dipilih sebagai kuantil target T3 pada data latih sehingga proporsi setiap tingkat
    sama dengan proporsi tingkat T1. Dengan begitu kedua protokol memiliki sebaran tingkat yang setara.
    """
    y1 = np.asarray(y_train_t1, dtype=np.float64)
    pos = y1[y1 > 0]
    q_t1 = np.concatenate([[0.0], np.quantile(pos, [0.25, 0.5, 0.75])])
    if y_train_target is None:
        return q_t1
    g1 = grades(y1, q_t1)
    shares = np.array([(g1 < m).mean() for m in range(1, 5)])
    return np.quantile(np.asarray(y_train_target, dtype=np.float64), shares)


def grades(y: np.ndarray, q: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=np.float64)
    return (y[:, None] > np.asarray(q)[None, :]).sum(axis=1).astype(np.int8)
