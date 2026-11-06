"""Evaluasi data uji dan penyusunan tabel Bab IV (Subbab 3.9 dan 3.10)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .experiment import Bundle, load_pred, protocol_cols
from .metrics import macro, per_product_metrics
from .stats import average_over_seeds, holm, paired_diff, summarize


def eval_run(b: Bundle, run: str, split: str = "test", protocol: str = "T1",
             rows: pd.DataFrame | None = None) -> pd.DataFrame:
    """Metrik per produk untuk satu run. ``rows`` dapat dipakai untuk subset (misalnya kelompok usia)."""
    rows = b.rows(split) if rows is None else rows
    pred = load_pred(b.cfg, run, split)
    d = rows.merge(pred, on="rid", how="inner")
    if len(d) != len(rows):
        raise ValueError(f"Run {run}: prediksi {split} hanya mencakup {len(d)} dari {len(rows)} ulasan. "
                         "Run dibuat dari pembagian data lain, jalankan ulang run tersebut.")
    if not np.isfinite(d["score"].to_numpy(dtype=np.float64)).all():
        raise ValueError(f"Run {run}: ada skor NaN/inf pada prediksi {split}.")
    g, t = protocol_cols(protocol)
    return per_product_metrics(d["parent_asin"].to_numpy(), d["score"].to_numpy(), d[g].to_numpy(),
                               d[t].to_numpy(), d["rid"].to_numpy(), map_rel=b.cfg.map_relevant_grade)


def eval_config(b: Bundle, runs: list[str], split: str = "test", protocol: str = "T1",
                rows: pd.DataFrame | None = None) -> pd.DataFrame:
    """Rata-rata metrik per produk dari semua seed satu konfigurasi."""
    return average_over_seeds([eval_run(b, r, split, protocol, rows) for r in runs])


def expected_runs(cfg) -> dict[tuple, set[str]]:
    """Semua run final yang seharusnya sudah dibuat notebook 05-06 sesuai ``run_priority``,
    dikelompokkan per (code, scale, target)."""
    from .experiment import run_id
    MS, TG = cfg.main_scale, cfg.main_target
    todo = cfg.experiments_to_run()
    seeded = lambda c, sc, t: {run_id(c, sc, t, s) for s in cfg.seeds}
    exp = {("B0", MS, TG): {run_id("B0", MS, TG, 0)}}
    if "B1" in todo:
        exp[("B1", MS, TG)] = {run_id("B1", MS, TG, cfg.seed)}
    for c in ["U", "B2", "B3", "B4", "B5", "A1", "A2", "A3"]:
        if c in todo:
            exp[(c, MS, TG)] = seeded(c, MS, TG)
    for sc in cfg.scales_to_run():
        exp[("U", sc, TG)] = seeded("U", sc, TG)
    for t in cfg.targets_to_run():
        if t in ("T2", "T3"):                     # T1 = target utama, sudah tercakup di atas
            exp[("U", MS, t)] = seeded("U", MS, t)
    return exp


def check_complete(cfg, groups: dict) -> None:
    """Gagal keras jika run yang dijadwalkan belum ada, atau ada run seed lain (dari konfigurasi lama)
    yang akan ikut dirata-rata. Dengan begitu tabel Bab IV tidak diam-diam kehilangan atau
    kelebihan baris."""
    problems = []
    for k, want in expected_runs(cfg).items():
        have = set(groups.get(k, []))
        if have != want:
            problems.append(f"{k}: kurang {sorted(want - have)}, kelebihan {sorted(have - want)}")
    if problems:
        raise RuntimeError("Run tidak sesuai jadwal. Jalankan notebook 05-06, atau hapus folder run yang "
                           "kelebihan:\n  " + "\n  ".join(problems))
    print("Semua", len(expected_runs(cfg)), "konfigurasi yang dijadwalkan lengkap.")


def group_runs(results: pd.DataFrame) -> dict[tuple, list[str]]:
    """Kelompokkan run_id berdasarkan (code, scale, target) dengan mengabaikan seed dan run penalaan."""
    res = results[~results["run_id"].str.contains("_tune")]
    return {k: list(g["run_id"]) for k, g in res.groupby(["code", "scale", "target"])}


def comparison_table(b: Bundle, groups: dict, keys: list[tuple], protocol: str = "T1", n_boot: int = 1000,
                     split: str = "test") -> tuple[pd.DataFrame, dict]:
    """Tabel metrik dengan IK 95% untuk beberapa konfigurasi. Mengembalikan juga metrik per produk."""
    rows, pps = [], {}
    missing = [k for k in keys if k not in groups]
    if missing:
        print("Dilewati (tidak ada run):", missing)
    for key in keys:
        if key not in groups:
            continue
        pp = eval_config(b, groups[key], split, protocol)
        pps[key] = pp
        s = summarize(pp, n_boot)
        r = {"code": key[0], "scale": key[1], "target": key[2], "seeds": len(groups[key])}
        for _, m in s.iterrows():
            r[m["metric"]] = m["mean"]
            r[f"{m['metric']}_lo"] = m["lo"]
            r[f"{m['metric']}_hi"] = m["hi"]
            r[f"n_{m['metric']}"] = m["n"]
        rows.append(r)
    return pd.DataFrame(rows), pps


def paired_table(pps: dict, ref: tuple, others: list[tuple], metric: str = "ndcg@10", n_boot: int = 1000) -> pd.DataFrame:
    rows = []
    for o in others:
        if o not in pps or ref not in pps:
            continue
        d = paired_diff(pps[ref], pps[o], metric, n_boot)
        rows.append({"ref": ref[0], "vs": o[0], **d})
    tab = pd.DataFrame(rows)
    if len(tab):
        tab["p_holm"] = holm(tab["p"].to_numpy())
        tab["lebih_baik"] = (tab["lo"] > 0) & (tab["p_holm"] < 0.05)
    return tab


def age_groups(b: Bundle, edges: list[float]) -> pd.Series:
    """Kelompok usia ulasan (baru, menengah, lama) dengan batas dari data latih."""
    return pd.cut(b.df["age_days"], [-np.inf, edges[0], edges[1], np.inf], labels=["baru", "menengah", "lama"])


def by_subset(b: Bundle, runs: list[str], subsets: dict[str, pd.DataFrame], protocol: str = "T1") -> pd.DataFrame:
    rows = []
    for name, sub in subsets.items():
        pp = eval_config(b, runs, "test", protocol, sub)
        rows.append({"group": name, **macro(pp)})
    return pd.DataFrame(rows)


def pointwise_errors(b: Bundle, runs: list[str]) -> dict:
    """MAE dan RMSE terhadap ln(1 + v) khusus pembanding pointwise B4."""
    te = b.rows("test")
    errs = []
    for r in runs:
        d = te.merge(load_pred(b.cfg, r, "test"), on="rid")
        e = d["score"].to_numpy() - d["y_t1"].to_numpy()
        errs.append((np.abs(e).mean(), np.sqrt((e ** 2).mean())))
    e = np.array(errs)
    return {"mae": float(e[:, 0].mean()), "rmse": float(e[:, 1].mean()), "seeds": len(runs)}


R0_PERMUTATIONS = 20   # jumlah permutasi acak untuk baseline R0 (notebook 07 dan 00b)


def random_per_product(b: Bundle, protocol: str = "T1", split: str = "test", n_perm: int = 20,
                       seed: int = 0, rows: pd.DataFrame | None = None) -> pd.DataFrame:
    """Metrik per produk untuk urutan acak (R0), dirata-rata atas ``n_perm`` permutasi.

    Ini batas bawah yang harus dilampaui model. Pada produk dengan sedikit ulasan, NDCG@10 urutan
    acak pun sudah tinggi, jadi angka model hanya bermakna bila dibandingkan dengan R0."""
    rows = b.rows(split) if rows is None else rows
    g, t = protocol_cols(protocol)
    rng = np.random.default_rng(seed)
    pps = [per_product_metrics(rows["parent_asin"].to_numpy(), rng.random(len(rows)), rows[g].to_numpy(),
                               rows[t].to_numpy(), rows["rid"].to_numpy(), map_rel=b.cfg.map_relevant_grade)
           for _ in range(n_perm)]
    return average_over_seeds(pps)


def random_table(pp_r0: pd.DataFrame, n_perm: int, n_boot: int = 1000) -> pd.DataFrame:
    """Satu baris R0 dengan kolom yang sama seperti ``comparison_table`` (``tables/uji_acak.csv``)."""
    r = {"code": "R0 (acak)", "scale": None, "target": None, "seeds": n_perm}
    for _, m in summarize(pp_r0, n_boot).iterrows():
        r[m["metric"]], r[f"{m['metric']}_lo"], r[f"{m['metric']}_hi"], r[f"n_{m['metric']}"] = \
            m["mean"], m["lo"], m["hi"], m["n"]
    return pd.DataFrame([r])


def size_groups(rows: pd.DataFrame) -> pd.Series:
    """Kuartil ukuran produk (jumlah ulasan di ``rows``), indeks parent_asin."""
    size = rows.groupby("parent_asin").size()
    return pd.qcut(size.rank(method="first"), 4, labels=["Q1 kecil", "Q2", "Q3", "Q4 besar"]).rename("kelompok")


def size_table(pp_model: pd.DataFrame, pp_r0: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    """Metrik model per kuartil ukuran produk, berdampingan dengan urutan acak R0
    (``tables/uji_per_ukuran_produk.csv``)."""
    grp = size_groups(rows).reset_index()
    cols = ["ndcg@10", "spearman", "ap"]
    m = pp_model.merge(grp, on="parent_asin").groupby("kelompok", observed=True)[cols].mean()
    r = pp_r0.merge(grp, on="parent_asin").groupby("kelompok", observed=True)[["ndcg@10", "ap"]].mean()
    out = m.join(r.add_suffix("_acak"))
    out["n_produk"] = grp.groupby("kelompok", observed=True).size()
    out["median_ulasan"] = rows.groupby("parent_asin").size().groupby(size_groups(rows), observed=True).median()
    return out.round(4)
