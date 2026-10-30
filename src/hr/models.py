"""Pemberi skor (Subbab 2.6 dan 3.7) dan fungsi loss (Subbab 2.7)."""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


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


# ---------------------------------------------------------------- loss
def ranknet_loss(s_hi: torch.Tensor, s_lo: torch.Tensor) -> torch.Tensor:
    """Persamaan (2.14) dan (3.6): ln(1 + exp(-(s_i - s_j))) untuk pasangan dengan y_i > y_j.
    softplus(-x) adalah bentuk yang stabil secara numerik dari ln(1 + exp(-x))."""
    return F.softplus(-(s_hi - s_lo)).mean()


def ranknet_loss_general(s_i: torch.Tensor, s_j: torch.Tensor, p_target: torch.Tensor) -> torch.Tensor:
    """Persamaan (2.13), cross-entropy dengan peluang target sembarang. Dipakai untuk pengujian."""
    return F.binary_cross_entropy_with_logits(s_i - s_j, p_target)


def pointwise_mse(s: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Objektif pointwise untuk B4."""
    return F.mse_loss(s, y)
