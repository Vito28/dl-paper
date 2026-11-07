"""DIBANGUN OTOMATIS oleh tools/build_app.py dari src/hr (versi 5edb1b71d80e). Jangan diedit langsung.

Salinan persis fungsi pipeline yang dibutuhkan saat inferensi, agar aplikasi menghitung skor dengan cara yang sama
dengan run yang dilaporkan.
"""
from __future__ import annotations

import html
import re

import numpy as np
import torch
import torch.nn as nn

_TAG = re.compile(r"<[^>]+>")
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WS = re.compile(r"\s+")


def clean_text(s) -> str:
    """Rapikan spasi, hapus karakter kendali dan sisa markup HTML. Huruf kapital, tanda baca,
    angka, dan kata negasi dipertahankan karena dibutuhkan encoder."""
    if not isinstance(s, str):
        return ""
    s = html.unescape(s)
    s = _TAG.sub(" ", s)
    s = _CTRL.sub(" ", s)
    return _WS.sub(" ", s).strip()


def _title_for_pair(title: str, max_words: int = 64) -> str:
    # judul sangat panjang dipotong agar truncation "only_second" selalu bisa memotong isi ulasan
    w = (title or "").split()
    return " ".join(w[:max_words])


class Scorer(nn.Module):
    """MLP pada persamaan (2.5)-(2.7). ``hidden=()`` menghasilkan ranker linear (B3)."""

    def __init__(self, d_in: int, hidden=(256, 64), dropout: float = 0.2):
        super().__init__()
        layers, prev = [], d_in
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU(), nn.Dropout(dropout)]
            prev = h
        layers.append(nn.Linear(prev, 1))      # lapisan keluaran tanpa aktivasi
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x.float()).squeeze(-1)


def grades(y: np.ndarray, q: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=np.float64)
    return (y[:, None] > np.asarray(q)[None, :]).sum(axis=1).astype(np.int8)


def dcg(grades_in_order: np.ndarray, k: int) -> float:
    g = grades_in_order[:k].astype(np.float64)
    return float(np.sum((2.0 ** g - 1.0) / np.log2(np.arange(2, len(g) + 2))))
