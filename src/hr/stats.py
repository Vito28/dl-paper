"""Ketidakpastian dan perbandingan model (Subbab 3.9).

Bootstrap dilakukan pada tingkat produk (parent_asin) sehingga ulasan dalam satu produk tetap
terkumpul. Perbandingan dua model memakai selisih metrik per produk pada produk yang valid untuk
kedua model.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def bootstrap_mean(values: np.ndarray, n_boot: int = 1000, seed: int = 0, alpha: float = 0.05) -> dict:
    v = np.asarray(values, dtype=np.float64)
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return {"mean": np.nan, "lo": np.nan, "hi": np.nan, "n": 0}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(v), size=(n_boot, len(v)))
    means = v[idx].mean(axis=1)
    return {"mean": float(v.mean()), "lo": float(np.quantile(means, alpha / 2)),
            "hi": float(np.quantile(means, 1 - alpha / 2)), "n": int(len(v))}


def summarize(per_prod: pd.DataFrame, n_boot: int = 1000, seed: int = 0,
              metrics=("ndcg@10", "ndcg@5", "spearman", "ap")) -> pd.DataFrame:
    rows = []
    for m in metrics:
        r = bootstrap_mean(per_prod[m].to_numpy(), n_boot, seed)
        rows.append({"metric": "map" if m == "ap" else m, **r})
    return pd.DataFrame(rows)


def paired_diff(pp_a: pd.DataFrame, pp_b: pd.DataFrame, metric: str = "ndcg@10", n_boot: int = 1000,
                seed: int = 0) -> dict:
    """Selisih rata-rata (A - B) dengan IK 95% bootstrap dan p-value dua sisi."""
    m = pp_a[["parent_asin", metric]].merge(pp_b[["parent_asin", metric]], on="parent_asin",
                                            suffixes=("_a", "_b")).dropna()
    d = (m[f"{metric}_a"] - m[f"{metric}_b"]).to_numpy()
    if len(d) == 0:
        return {"diff": np.nan, "lo": np.nan, "hi": np.nan, "p": np.nan, "n": 0}
    rng = np.random.default_rng(seed)
    boots = d[rng.integers(0, len(d), size=(n_boot, len(d)))].mean(axis=1)
    p = 2 * min((boots <= 0).mean(), (boots >= 0).mean())
    return {"diff": float(d.mean()), "lo": float(np.quantile(boots, 0.025)),
            "hi": float(np.quantile(boots, 0.975)), "p": float(min(p, 1.0)), "n": int(len(d)),
            "win": int((d > 0).sum()), "tie": int((d == 0).sum()), "loss": int((d < 0).sum())}


def holm(pvals) -> np.ndarray:
    """Koreksi Holm untuk perbandingan berganda (kritik reviewer nomor 8)."""
    p = np.asarray(pvals, dtype=np.float64)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (len(p) - rank) * p[i])
        adj[i] = min(running, 1.0)
    return adj


def average_over_seeds(pps: list[pd.DataFrame]) -> pd.DataFrame:
    """Rata-rata metrik per produk dari beberapa seed sebelum bootstrap."""
    cat = pd.concat(pps, ignore_index=True)
    return cat.groupby("parent_asin", as_index=False).mean(numeric_only=True)


def groupwise(per_prod: pd.DataFrame, group: pd.Series, metric: str = "ndcg@10") -> pd.DataFrame:
    """Rata-rata metrik per kelompok (misalnya ukuran produk)."""
    d = per_prod.merge(group.rename("group").reset_index(), on="parent_asin")
    return d.groupby("group")[metric].agg(["mean", "count"]).reset_index()
