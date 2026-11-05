"""Pelatihan pemberi skor (Subbab 3.7) dengan early stopping berdasarkan NDCG@10 validasi."""
from __future__ import annotations

import copy
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
import torch

from .metrics import macro, per_product_metrics
from .models import Scorer, pointwise_mse, ranknet_loss
from .pairs import PairSampler


@dataclass
class EvalSet:
    """Data evaluasi beserta label yang dibutuhkan metrik."""
    X: np.ndarray
    pid: np.ndarray
    rid: np.ndarray
    grade: np.ndarray
    target: np.ndarray


def set_seed(seed: int) -> None:
    import random
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


@torch.no_grad()
def predict(model: torch.nn.Module, X, device: str, batch: int = 65536) -> np.ndarray:
    model.eval()
    out = []
    for i in range(0, len(X), batch):
        xb = torch.as_tensor(np.asarray(X[i:i + batch]), device=device)
        out.append(model(xb).float().cpu().numpy())
    s = np.concatenate(out) if out else np.zeros(0)
    if not np.isfinite(s).all():
        raise FloatingPointError(f"{(~np.isfinite(s)).sum()} skor prediksi NaN/inf. Model divergen.")
    return s


def evaluate_scores(es: EvalSet, scores: np.ndarray, map_rel: int = 2) -> tuple[dict, pd.DataFrame]:
    pp = per_product_metrics(es.pid, scores, es.grade, es.target, es.rid, map_rel=map_rel)
    return macro(pp), pp


def train_scorer(X_train: np.ndarray, y_train: np.ndarray, pid_train: np.ndarray, val: EvalSet, *,
                 loss: str = "ranknet", hidden=(256, 64), dropout: float = 0.2, lr: float = 3e-4,
                 weight_decay: float = 1e-5, max_epochs: int = 30, patience: int = 3,
                 batch_pairs: int = 1024, batch_points: int = 1024, max_pairs: int = 100,
                 delta: float = 0.0, log_age_train: np.ndarray | None = None,
                 age_window: float | None = None, seed: int = 42, map_rel: int = 2,
                 device: str | None = None, verbose: bool = True):
    """Latih Scorer. Mengembalikan (model terbaik, riwayat per epoch, metrik validasi terbaik).

    Riwayat berisi loss latih, loss validasi (pada pasangan validasi yang tetap), dan NDCG@10
    validasi setiap epoch. Riwayat ini dipakai untuk grafik loss di Bab IV.
    """
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    set_seed(seed)
    Xt = torch.as_tensor(np.ascontiguousarray(X_train), device=device)
    model = Scorer(Xt.shape[1], hidden=hidden, dropout=dropout).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

    sampler = PairSampler(pid_train, y_train, max_pairs, delta, log_age_train, age_window, seed=seed)
    yt = torch.as_tensor(np.asarray(y_train, dtype=np.float32), device=device)
    # pasangan validasi tetap untuk memantau loss validasi
    vs = PairSampler(val.pid, val.target, max_pairs, delta, seed=seed + 999)
    v_hi, v_lo = vs.sample()

    best, best_state, bad, hist = -np.inf, None, 0, []
    for ep in range(1, max_epochs + 1):
        model.train()
        t0 = time.time()
        losses = []
        if loss == "ranknet":
            hi, lo = sampler.sample()
            hi_t = torch.as_tensor(hi, device=device)
            lo_t = torch.as_tensor(lo, device=device)
            for i in range(0, len(hi_t), batch_pairs):
                bh, bl = hi_t[i:i + batch_pairs], lo_t[i:i + batch_pairs]
                l = ranknet_loss(model(Xt[bh]), model(Xt[bl]))
                opt.zero_grad()
                l.backward()
                opt.step()
                losses.append(l.item())
            n_pairs = len(hi)
            if n_pairs == 0:
                raise ValueError("Tidak ada pasangan latih (semua target sama dalam setiap produk, atau "
                                 "age_window terlalu sempit). Model tidak akan belajar apa pun.")
        elif loss == "mse":
            perm = torch.randperm(len(Xt), device=device)
            for i in range(0, len(perm), batch_points):
                b = perm[i:i + batch_points]
                l = pointwise_mse(model(Xt[b]), yt[b])
                opt.zero_grad()
                l.backward()
                opt.step()
                losses.append(l.item())
            n_pairs = 0
        else:
            raise ValueError(loss)

        if not losses or not np.isfinite(losses).all():
            raise FloatingPointError(f"Loss latih tidak valid pada epoch {ep} (kosong atau NaN/inf). "
                                     "Coba learning rate lebih kecil.")
        scores = predict(model, val.X, device)
        m, _ = evaluate_scores(val, scores, map_rel)
        with torch.no_grad():
            model.eval()
            sv = torch.as_tensor(scores, device=device)
            vloss = float(ranknet_loss(sv[torch.as_tensor(v_hi, device=device)],
                                       sv[torch.as_tensor(v_lo, device=device)])) if len(v_hi) else float("nan")
        rec = {"epoch": ep, "train_loss": float(np.mean(losses)) if losses else float("nan"),
               "val_ranknet_loss": vloss, "val_ndcg@10": m["ndcg@10"], "val_ndcg@5": m["ndcg@5"],
               "val_spearman": m["spearman"], "val_map": m["map"], "pairs": n_pairs,
               "seconds": time.time() - t0}
        hist.append(rec)
        if verbose:
            print(f"epoch {ep:2d}  train {rec['train_loss']:.4f}  val_loss {vloss:.4f}  "
                  f"val NDCG@10 {m['ndcg@10']:.4f}")
        if m["ndcg@10"] > best + 1e-6:
            best, best_state, bad = m["ndcg@10"], copy.deepcopy(model.state_dict()), 0
        else:
            bad += 1
            if bad >= patience:
                break
    if best_state is None:
        raise ValueError("NDCG@10 validasi NaN di setiap epoch: tidak ada produk validasi dengan IDCG > 0.")
    model.load_state_dict(best_state)
    del Xt
    return model, pd.DataFrame(hist), best
