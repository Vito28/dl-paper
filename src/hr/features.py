"""Feature fusion (persamaan 3.4) dan baseline non-neural (B0, B1)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import scipy.sparse as sp

from .config import FORBIDDEN_FEATURES, STRUCT_FEATURES
from .pairs import PairSampler


def struct_matrix(df: pd.DataFrame, feats) -> np.ndarray:
    """Fitur terstruktur yang sudah distandardisasi (kolom z_*)."""
    feats = STRUCT_FEATURES if feats == "all" else list(feats)
    bad = set(feats) & FORBIDDEN_FEATURES
    assert not bad, f"Fitur terlarang masuk ke model: {bad}"
    if not feats:
        return np.zeros((len(df), 0), dtype=np.float16)
    return df[[f"z_{c}" for c in feats]].to_numpy(np.float16)


def fuse(emb: np.ndarray, df: pd.DataFrame, feats) -> np.ndarray:
    """x_i = [e_i ; z_i]. ``emb`` harus sejajar baris dengan ``df``."""
    assert len(emb) == len(df)
    return np.hstack([np.asarray(emb, dtype=np.float16), struct_matrix(df, feats)])


# ---------------------------------------------------------------- B0
def score_b0(df: pd.DataFrame) -> np.ndarray:
    """B0: ulasan diurutkan berdasarkan panjang isi (jumlah karakter)."""
    return df["review_length"].to_numpy(np.float64)


# ---------------------------------------------------------------- B1
def train_b1(X_train: sp.csr_matrix, y: np.ndarray, pid: np.ndarray, C: float, max_pairs: int,
             delta: float, seed: int):
    """Ranker linear pairwise pada TF-IDF + fitur.

    Regresi logistik tanpa intersep pada selisih vektor x_i - x_j adalah RankNet dengan pemberi
    skor linear s = w^T x (persamaan 2.12-2.14). Setengah pasangan dibalik agar kelasnya seimbang.
    """
    from sklearn.linear_model import LogisticRegression
    hi, lo = PairSampler(pid, y, max_pairs, delta, seed=seed).sample()
    rng = np.random.default_rng(seed)
    flip = rng.random(len(hi)) < 0.5
    a = np.where(flip, lo, hi)
    b = np.where(flip, hi, lo)
    D = X_train[a] - X_train[b]
    lab = (~flip).astype(np.int8)
    clf = LogisticRegression(C=C, fit_intercept=False, solver="liblinear", max_iter=200)
    clf.fit(D, lab)
    return clf


def score_linear(clf, X) -> np.ndarray:
    return np.asarray(X @ clf.coef_.ravel()).ravel()


def tfidf_plus_struct(vec, texts, df: pd.DataFrame) -> sp.csr_matrix:
    return sp.hstack([vec.transform(texts), sp.csr_matrix(struct_matrix(df, "all").astype(np.float32))]).tocsr()
