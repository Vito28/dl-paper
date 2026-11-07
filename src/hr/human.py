"""Validasi label dengan penilaian manusia (eksperimen opsional, laporan/arsip/2026-11-07_sebelum_run/catatan/kritik-reviewer.md 3.2)."""
from __future__ import annotations

import numpy as np
import pandas as pd

RUBRIC = """Nilai setiap ulasan dengan skala 1 sampai 5 untuk pertanyaan
"Seberapa membantu ulasan ini bagi calon pembeli untuk memutuskan membeli produk tersebut?"
1 = tidak membantu sama sekali, 2 = sedikit membantu, 3 = cukup membantu, 4 = membantu, 5 = sangat membantu.
Nilai setiap ulasan secara mandiri. Jangan berdiskusi dengan penilai lain sebelum semua selesai.
Jumlah suara, tanggal, dan skor model sengaja tidak ditampilkan."""


def make_sheet(test_df: pd.DataFrame, n_products: int = 80, per_product: int = 6, min_reviews: int = 4,
               seed: int = 7) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ambil produk dari data uji secara bertingkat menurut ukuran produk, lalu beberapa ulasan per produk.

    Mengembalikan (lembar anotasi tanpa label, kunci rahasia item_id -> rid)."""
    rng = np.random.default_rng(seed)
    sizes = test_df.groupby("parent_asin").size()
    sizes = sizes[sizes >= min_reviews]
    strata = pd.qcut(sizes.rank(method="first"), 4, labels=False)
    chosen = []
    for s in range(4):
        pool = strata[strata == s].index.to_numpy()
        chosen += list(rng.choice(pool, size=min(len(pool), n_products // 4), replace=False))
    rows = []
    for p_code, p in enumerate(chosen):
        g = test_df[test_df["parent_asin"] == p]
        pick = g.sample(min(per_product, len(g)), random_state=int(rng.integers(1 << 31)))
        for _, r in pick.iterrows():
            rows.append({"product_code": f"P{p_code:03d}", "rid": int(r["rid"]),
                         "title": r["title"], "text": r["text"]})
    sheet = pd.DataFrame(rows).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    sheet = sheet.sort_values("product_code", kind="stable").reset_index(drop=True)
    sheet["item_id"] = [f"I{i:04d}" for i in range(len(sheet))]
    key = sheet[["item_id", "rid", "product_code"]].copy()
    blind = sheet[["item_id", "product_code", "title", "text"]].copy()
    blind["score_1_5"] = ""
    return blind, key


def weighted_kappa(a, b, k: int = 5) -> float:
    """Cohen's kappa berbobot kuadratik untuk dua penilai pada skala 1..k."""
    a = np.asarray(a, dtype=int) - 1
    b = np.asarray(b, dtype=int) - 1
    O = np.zeros((k, k))
    for i, j in zip(a, b):
        O[i, j] += 1
    W = np.array([[(i - j) ** 2 for j in range(k)] for i in range(k)]) / (k - 1) ** 2
    E = np.outer(O.sum(1), O.sum(0)) / O.sum()
    return float(1 - (W * O).sum() / (W * E).sum())


def krippendorff_alpha_interval(ratings: np.ndarray) -> float:
    """Alpha Krippendorff (metrik interval). ``ratings`` berukuran (penilai, item), NaN = kosong."""
    R = np.asarray(ratings, dtype=np.float64)
    units = [R[:, j][~np.isnan(R[:, j])] for j in range(R.shape[1])]
    units = [u for u in units if len(u) >= 2]
    n = sum(len(u) for u in units)
    if n == 0:
        return float("nan")
    Do_num = sum(((u[:, None] - u[None, :]) ** 2).sum() / (len(u) - 1) for u in units)
    allv = np.concatenate(units)
    De = ((allv[:, None] - allv[None, :]) ** 2).sum() / (n * (n - 1))
    Do = Do_num / n
    return float(1 - Do / De) if De > 0 else float("nan")
