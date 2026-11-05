"""Pembagian data product-disjoint dan subset skala E1 sampai E5 (Subbab 3.4)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import STRUCT_FEATURES, Config


def split_products(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Acak daftar parent_asin dengan seed tetap, lalu alokasikan 80/10/10 per produk."""
    rng = np.random.default_rng(cfg.seed)
    prods = np.sort(df["parent_asin"].unique())
    perm = rng.permutation(len(prods))
    n_tr = int(round(cfg.split_frac[0] * len(prods)))
    n_va = int(round(cfg.split_frac[1] * len(prods)))
    split = np.empty(len(prods), dtype=object)
    split[perm[:n_tr]] = "train"
    split[perm[n_tr:n_tr + n_va]] = "val"
    split[perm[n_tr + n_va:]] = "test"
    m = dict(zip(prods, split))
    out = df.copy()
    out["split"] = out["parent_asin"].map(m)
    return out


def leakage_checks(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Pemeriksaan otomatis setelah alokasi. Baris validasi/uji yang bocor dibuang, baris latih
    tidak diubah."""
    rep = {}
    by = {s: set(df.loc[df["split"] == s, "parent_asin"]) for s in ("train", "val", "test")}
    rep["parent_overlap"] = {
        "train_val": len(by["train"] & by["val"]),
        "train_test": len(by["train"] & by["test"]),
        "val_test": len(by["val"] & by["test"]),
    }
    assert sum(rep["parent_overlap"].values()) == 0, "parent_asin muncul di dua partisi"

    asin_splits = df.groupby("asin")["split"].nunique()
    shared_asin = set(asin_splits[asin_splits > 1].index)
    rep["asin_in_multiple_splits"] = len(shared_asin)

    train_hash = set(df.loc[df["split"] == "train", "text_hash"])
    leak = (df["split"] != "train") & (df["asin"].isin(shared_asin) | df["text_hash"].isin(train_hash))
    rep["eval_rows_dropped_for_leakage"] = int(leak.sum())
    df = df[~leak]
    # buang lagi produk evaluasi yang tinggal < 2 ulasan
    sizes = df.groupby("parent_asin")["rid"].transform("size")
    small = (df["split"] != "train") & (sizes < 2)
    rep["eval_rows_dropped_small_after_leak"] = int(small.sum())
    return df[~small].copy(), rep


def cap_eval(df: pd.DataFrame, cfg: Config) -> tuple[pd.DataFrame, dict]:
    """Batasi ukuran validasi/uji dengan mengambil produk utuh secara acak."""
    rep = {}
    rng = np.random.default_rng(cfg.seed + 1)
    keep = np.ones(len(df), dtype=bool)
    for s in ("val", "test"):
        sub = df[df["split"] == s]
        if len(sub) <= cfg.max_eval_reviews:
            rep[s] = {"products": int(sub["parent_asin"].nunique()), "reviews": len(sub), "capped": False}
            continue
        sizes = sub.groupby("parent_asin").size()
        order = rng.permutation(sizes.index.to_numpy())
        cum = sizes.loc[order].cumsum()
        chosen = set(cum[cum <= cfg.max_eval_reviews].index)
        drop = (df["split"] == s) & ~df["parent_asin"].isin(chosen)
        keep &= ~drop.to_numpy()
        rep[s] = {"products": len(chosen), "reviews": int(sizes.loc[list(chosen)].sum()), "capped": True}
    return df[keep].copy(), rep


def make_scales(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Subset bertingkat (nested). Produk latih diacak sekali, setiap produk dibatasi paling banyak
    ``max_train_reviews_per_product`` ulasan, lalu skala Ek diambil sebagai awalan urutan yang sama.
    Karena itu E1 selalu bagian dari E2, E2 bagian dari E3, dan seterusnya."""
    rng = np.random.default_rng(cfg.seed + 2)
    tr = df[df["split"] == "train"][["rid", "parent_asin"]].copy()
    tr["u"] = rng.random(len(tr))
    tr = tr.sort_values(["parent_asin", "u"])
    tr["k"] = tr.groupby("parent_asin").cumcount()
    tr = tr[tr["k"] < cfg.max_train_reviews_per_product]
    prods = tr["parent_asin"].unique()
    prod_rank = dict(zip(prods[rng.permutation(len(prods))], range(len(prods))))
    tr["prank"] = tr["parent_asin"].map(prod_rank)
    tr = tr.sort_values(["prank", "k"]).reset_index(drop=True)
    tr["order"] = np.arange(len(tr))
    out = df.copy()
    pos = pd.Series(tr["order"].to_numpy(), index=tr["rid"].to_numpy())
    out["train_order"] = out["rid"].map(pos)          # NaN untuk validasi/uji atau yang terpotong batas
    short = {name: n for name, n in cfg.scales.items() if n > len(tr)}
    if short:
        # Tanpa ini, skala besar diam-diam sama dengan skala di bawahnya dan kurva skala (RM2) menjadi datar.
        raise ValueError(f"Data latih hanya {len(tr)} ulasan (setelah batas {cfg.max_train_reviews_per_product} "
                         f"per produk), tidak cukup untuk {short}. Pilih kategori lebih besar atau ubah cfg.scales.")
    for name, n in cfg.scales.items():
        col = out["train_order"] < n
        # buang produk yang hanya terambil satu ulasan di ujung awalan
        cnt = out[col].groupby("parent_asin")["rid"].transform("size")
        single = cnt[cnt < 2].index
        col.loc[single] = False
        out[f"in_{name}"] = col.fillna(False).astype(bool)
    return out


def scale_report(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    rows = []
    for name in cfg.scales:
        sub = df[df[f"in_{name}"]]
        rows.append({"scale": name, "reviews": len(sub), "products": sub["parent_asin"].nunique(),
                     "zero_vote_share": float((sub["helpful_vote"] == 0).mean())})
    for s in ("val", "test"):
        sub = df[df["split"] == s]
        rows.append({"scale": s, "reviews": len(sub), "products": sub["parent_asin"].nunique(),
                     "zero_vote_share": float((sub["helpful_vote"] == 0).mean())})
    return pd.DataFrame(rows)


def fit_standardizer(df: pd.DataFrame) -> dict:
    """Persamaan (3.2). Rata-rata dan simpangan baku hanya dari data latih."""
    tr = df[df["split"] == "train"]
    return {c: (float(tr[c].mean()), float(tr[c].std() or 1.0)) for c in STRUCT_FEATURES}


def apply_standardizer(df: pd.DataFrame, stats: dict) -> pd.DataFrame:
    out = df.copy()
    for c, (m, s) in stats.items():
        out[f"z_{c}"] = ((out[c].astype(np.float64) - m) / s).astype(np.float32)
    return out
