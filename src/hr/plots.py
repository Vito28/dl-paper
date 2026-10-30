"""Grafik untuk Bab IV. Semua gambar disimpan 300 dpi sesuai syarat JuTISI."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({"font.family": "serif", "font.size": 10, "figure.dpi": 110,
                     "axes.spines.top": False, "axes.spines.right": False})


def save(fig, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    return path


def vote_distribution(votes: np.ndarray, ax=None):
    ax = ax or plt.subplots(figsize=(5, 3.2))[1]
    v = np.asarray(votes)
    bins = np.r_[0, np.unique(np.round(np.logspace(0, np.log10(max(v.max(), 2)), 30))), v.max() + 1]
    ax.hist(v, bins=bins, color="#4C72B0")
    ax.set_xscale("symlog")
    ax.set_yscale("log")
    ax.set_xlabel("helpful_vote")
    ax.set_ylabel("jumlah ulasan")
    ax.set_title(f"Sebaran helpful_vote (nol = {np.mean(v == 0):.1%})")
    return ax


def simple_hist(x, xlabel: str, title: str, log_y: bool = False, bins: int = 50, ax=None):
    ax = ax or plt.subplots(figsize=(5, 3.2))[1]
    ax.hist(np.asarray(x), bins=bins, color="#4C72B0")
    if log_y:
        ax.set_yscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("frekuensi")
    ax.set_title(title)
    return ax


def age_curve(ages, curve, lo=None, hi=None, ref_days: float = 30.0, ax=None):
    ax = ax or plt.subplots(figsize=(5, 3.2))[1]
    ax.plot(ages, curve, color="#C44E52")
    if lo is not None:
        ax.fill_between(ages, lo, hi, color="#C44E52", alpha=0.2, label="IK 95%")
        ax.legend()
    ax.axhline(1.0, color="grey", lw=0.8, ls="--")
    ax.set_xscale("log")
    ax.set_xlabel("usia ulasan (hari)")
    ax.set_ylabel(f"rasio rata-rata suara vs usia {ref_days:.0f} hari")
    ax.set_title("Hubungan usia ulasan dan helpful votes")
    return ax


def loss_curves(hist: pd.DataFrame, title: str = "", axes=None):
    if axes is None:
        fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    from matplotlib.ticker import MaxNLocator
    axes[0].plot(hist["epoch"], hist["train_loss"], marker="o", label="latih (loss objektif model)")
    axes[0].plot(hist["epoch"], hist["val_ranknet_loss"], marker="s", label="validasi (loss RankNet)")
    axes[0].set_xlabel("epoch")
    axes[0].set_ylabel("loss")
    axes[0].legend(fontsize=8)
    axes[1].plot(hist["epoch"], hist["val_ndcg@10"], marker="o", color="#55A868")
    best = hist["val_ndcg@10"].idxmax()
    axes[1].axvline(hist.loc[best, "epoch"], color="grey", ls="--", lw=0.8)
    axes[1].set_xlabel("epoch")
    axes[1].set_ylabel("NDCG@10 validasi")
    for ax in axes:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if title:
        axes[0].figure.suptitle(title)
    return axes


def bar_ci(tab: pd.DataFrame, label_col: str, metric_label: str = "NDCG@10", ax=None, highlight=None):
    """``tab`` berisi kolom label, mean, lo, hi."""
    ax = ax or plt.subplots(figsize=(6, 3.4))[1]
    x = np.arange(len(tab))
    colors = ["#C44E52" if highlight is not None and l == highlight else "#4C72B0" for l in tab[label_col]]
    ax.bar(x, tab["mean"], color=colors)
    ax.errorbar(x, tab["mean"], yerr=[tab["mean"] - tab["lo"], tab["hi"] - tab["mean"]], fmt="none",
                ecolor="black", capsize=3, lw=1)
    ax.set_xticks(x, tab[label_col])
    ax.set_ylabel(metric_label)
    lo = float(np.nanmin(tab["lo"]))
    ax.set_ylim(max(0.0, lo - 0.05), None)
    return ax


def scale_curve(tab: pd.DataFrame, ax=None):
    """``tab`` berisi kolom reviews, mean, lo, hi."""
    ax = ax or plt.subplots(figsize=(5, 3.2))[1]
    ax.plot(tab["reviews"], tab["mean"], marker="o")
    ax.fill_between(tab["reviews"], tab["lo"], tab["hi"], alpha=0.2)
    ax.set_xscale("log")
    ax.set_xlabel("jumlah ulasan latih")
    ax.set_ylabel("NDCG@10 uji")
    ax.set_title("Pengaruh ukuran data latih")
    return ax


def grouped_bars(tab: pd.DataFrame, group_col: str, series_col: str, value_col: str = "mean", ax=None):
    ax = ax or plt.subplots(figsize=(6, 3.4))[1]
    groups = list(tab[group_col].unique())
    series = list(tab[series_col].unique())
    w = 0.8 / len(series)
    for k, s in enumerate(series):
        sub = tab[tab[series_col] == s].set_index(group_col).reindex(groups)
        ax.bar(np.arange(len(groups)) + k * w - 0.4 + w / 2, sub[value_col], width=w, label=str(s))
    ax.set_xticks(np.arange(len(groups)), groups)
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), frameon=False)
    return ax
