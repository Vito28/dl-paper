"""Pembentukan pasangan pelatihan (persamaan 3.5).

Pasangan (i, j) hanya dibentuk di dalam produk yang sama dengan y_i - y_j > delta. Setiap produk
dibatasi paling banyak M pasangan yang diambil acak, dan pasangan diambil ulang setiap epoch.
Untuk T2 (age-matched pairs), selisih ln(1 + usia) kedua ulasan harus di bawah ``age_window``.
"""
from __future__ import annotations

import numpy as np


class PairSampler:
    def __init__(self, pid: np.ndarray, y: np.ndarray, max_pairs: int, delta: float = 0.0,
                 log_age: np.ndarray | None = None, age_window: float | None = None, seed: int = 0,
                 oversample: int = 4):
        self.y = np.asarray(y, dtype=np.float64)
        self.max_pairs = int(max_pairs)
        self.delta = float(delta)
        self.log_age = None if log_age is None else np.asarray(log_age, dtype=np.float64)
        self.age_window = age_window
        self.rng = np.random.default_rng(seed)
        self.oversample = oversample
        codes = np.unique(np.asarray(pid), return_inverse=True)[1]
        self.order = np.argsort(codes, kind="stable")      # posisi baris dikelompokkan per produk
        sizes = np.bincount(codes)
        starts = np.r_[0, np.cumsum(sizes)[:-1]]
        ok = sizes >= 2
        self.sizes, self.starts = sizes[ok], starts[ok]
        self.k = np.minimum(self.max_pairs, self.sizes * (self.sizes - 1) // 2)

    def sample(self) -> tuple[np.ndarray, np.ndarray]:
        """Kembalikan (hi, lo): posisi baris dengan y[hi] > y[lo] + delta."""
        d = np.maximum(self.k * self.oversample, 4)
        g = np.repeat(np.arange(len(self.sizes)), d)
        s = self.sizes[g]
        a = (self.rng.random(len(g)) * s).astype(np.int64)
        b = (self.rng.random(len(g)) * (s - 1)).astype(np.int64)
        b += b >= a                                          # pastikan a != b
        ia = self.order[self.starts[g] + a]
        ib = self.order[self.starts[g] + b]
        diff = self.y[ia] - self.y[ib]
        keep = np.abs(diff) > self.delta
        if self.log_age is not None and self.age_window is not None:
            keep &= np.abs(self.log_age[ia] - self.log_age[ib]) < self.age_window
        ia, ib, diff, g = ia[keep], ib[keep], diff[keep], g[keep]
        hi = np.where(diff > 0, ia, ib)
        lo = np.where(diff > 0, ib, ia)
        # hapus duplikat, lalu ambil paling banyak k pasangan per produk
        n = len(self.y) + 1
        key = hi.astype(np.int64) * n + lo
        _, first = np.unique(key, return_index=True)
        hi, lo, g = hi[first], lo[first], g[first]
        perm = self.rng.permutation(len(g))
        hi, lo, g = hi[perm], lo[perm], g[perm]
        srt = np.argsort(g, kind="stable")
        hi, lo, g = hi[srt], lo[srt], g[srt]
        grp_start = np.r_[0, np.flatnonzero(np.diff(g)) + 1]
        rank = np.arange(len(g)) - np.repeat(grp_start, np.diff(np.r_[grp_start, len(g)]))
        take = rank < self.k[g]
        hi, lo = hi[take], lo[take]
        perm = self.rng.permutation(len(hi))
        return hi[perm], lo[perm]

    def stats(self, pid: np.ndarray) -> dict:
        """Ringkasan satu kali pengambilan pasangan, untuk dicatat di Bab IV."""
        hi, lo = self.sample()
        pid = np.asarray(pid)
        return {"pairs": int(len(hi)),
                "products_with_pairs": int(len(np.unique(pid[hi]))),
                "products_eligible": int(len(self.sizes)),
                "mean_target_gap": float(np.mean(self.y[hi] - self.y[lo])) if len(hi) else float("nan")}
