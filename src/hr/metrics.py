"""Metrik pemeringkatan per produk (Subbab 2.10, 3.8, dan 3.9).

Aturan yang ditetapkan sebelum eksperimen:
- NDCG@k (persamaan 2.19-2.20) dihitung pada produk dengan IDCG@k > 0.
- Spearman (persamaan 2.21) memakai peringkat rata-rata, untuk produk dengan >= 3 ulasan dan
  target tidak konstan.
- AP/MAP (persamaan 2.22-2.23) dengan relevan jika g >= ``map_rel``, untuk produk yang punya
  minimal satu ulasan relevan dan satu tidak relevan.
- Skor kembar diurutkan secara tetap berdasarkan hash identitas baris yang tidak berkaitan dengan label.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import rankdata


def tiebreak_key(rid: np.ndarray) -> np.ndarray:
    return (np.asarray(rid, dtype=np.uint64) * np.uint64(2654435761)) % np.uint64(2 ** 32)


def dcg(grades_in_order: np.ndarray, k: int) -> float:
    g = grades_in_order[:k].astype(np.float64)
    return float(np.sum((2.0 ** g - 1.0) / np.log2(np.arange(2, len(g) + 2))))


def per_product_metrics(pid, score, grade, target, rid, ks=(5, 10), map_rel: int = 2) -> pd.DataFrame:
    """Hitung semua metrik untuk setiap produk. Nilai NaN berarti produk tidak memenuhi syarat
    metrik tersebut."""
    pid = np.asarray(pid)
    score = np.asarray(score, dtype=np.float64)
    grade = np.asarray(grade)
    target = np.asarray(target, dtype=np.float64)
    tb = tiebreak_key(rid)
    srt = np.argsort(pid, kind="stable")
    pid_s = pid[srt]
    bounds = np.flatnonzero(np.r_[True, pid_s[1:] != pid_s[:-1], True])
    rows = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        idx = srt[a:b]
        n = len(idx)
        if n < 2:
            continue
        # urutan prediksi: skor menurun, kembar diputus dengan tiebreak_key
        o = idx[np.lexsort((tb[idx], -score[idx]))]
        g_pred = grade[o]
        g_ideal = np.sort(grade[idx])[::-1]
        r = {"parent_asin": pid_s[a], "n": n}
        for k in ks:
            idcg = dcg(g_ideal, k)
            r[f"ndcg@{k}"] = dcg(g_pred, k) / idcg if idcg > 0 else np.nan
        t = target[idx]
        if n >= 3 and np.ptp(t) > 0:
            rs, rt = rankdata(score[idx]), rankdata(t)
            r["spearman"] = float(np.corrcoef(rs, rt)[0, 1]) if np.ptp(rs) > 0 else 0.0
        else:
            r["spearman"] = np.nan
        rel = (g_pred >= map_rel).astype(np.float64)
        R = rel.sum()
        if 0 < R < n:
            prec = np.cumsum(rel) / np.arange(1, n + 1)
            r["ap"] = float(np.sum(prec * rel) / R)
        else:
            r["ap"] = np.nan
        rows.append(r)
    return pd.DataFrame(rows)


def macro(df: pd.DataFrame, metrics=("ndcg@10", "ndcg@5", "spearman", "ap")) -> dict:
    """Rata-rata makro (persamaan 3.8) beserta jumlah produk valid per metrik."""
    out = {}
    for m in metrics:
        v = df[m].dropna()
        name = "map" if m == "ap" else m
        out[name] = float(v.mean()) if len(v) else float("nan")
        out[f"n_{name}"] = int(len(v))
    return out


def coverage(df_eval_rows: pd.DataFrame, per_prod: pd.DataFrame) -> dict:
    """Berapa produk dan ulasan yang benar-benar tercakup NDCG (kritik reviewer nomor 4)."""
    sizes = df_eval_rows.groupby("parent_asin").size()
    valid = set(per_prod.loc[per_prod["ndcg@10"].notna(), "parent_asin"])
    return {
        "products_total": int(len(sizes)),
        "products_ndcg_valid": len(valid),
        "products_excluded_all_zero": int(len(sizes) - len(valid)),
        "reviews_total": int(sizes.sum()),
        "reviews_in_valid_products": int(sizes[sizes.index.isin(valid)].sum()),
    }
