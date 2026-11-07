"""Gambar ulang grafik laporan yang berasal dari tabel hasil run, dengan koma desimal dan label berbahasa Indonesia.

Sumber angka hanya tabel di notebooks/FINISHED RUN/hasil_video_games/tables/, sehingga grafik selalu sama dengan
tabel di LAPORAN.md. Keluaran ditulis ke laporan/gambar/ dengan nama berkas yang sama seperti grafik dari run.

    python tools/gambar_laporan.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FuncFormatter, MaxNLocator  # noqa: E402

AKAR = Path(__file__).resolve().parents[1]
TAB = AKAR / "notebooks" / "FINISHED RUN" / "hasil_video_games" / "tables"
OUT = AKAR / "laporan" / "gambar"

BIRU, MERAH, ABU, HIJAU = "#4C72B0", "#C44E52", "#9A9A9A", "#55A868"
plt.rcParams.update({"font.family": "serif", "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
                     "legend.fontsize": 10, "axes.spines.top": False, "axes.spines.right": False})


def koma(v: float, desimal: int | None = None) -> str:
    t = f"{v:g}" if desimal is None else f"{v:.{desimal}f}"
    return t.replace(".", ",")


def sumbu_koma(ax, desimal: int | None = None) -> None:
    """Koma desimal pada sumbu y. Sumbu x berisi kategori atau sudah diberi label sendiri."""
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: koma(round(v, 6), desimal)))


def ribuan(v: float) -> str:
    return f"{int(v):,}".replace(",", ".")


def simpan(fig, nama: str) -> None:
    fig.savefig(OUT / nama, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("ditulis", OUT / nama)


def batang_ik(ax, label, m, lo, hi, warna, angka=True):
    x = np.arange(len(label))
    ax.bar(x, m, color=warna)
    ax.errorbar(x, m, yerr=[m - lo, hi - m], fmt="none", ecolor="black", capsize=3, lw=1)
    ax.set_xticks(x, label)
    if angka:
        for xi, hi_i, mi in zip(x, hi, m):
            ax.text(xi, hi_i + 0.004, koma(mi, 3), ha="center", va="bottom", fontsize=9)


def uji_baseline() -> None:
    t = pd.read_csv(TAB / "uji_baseline.csv")
    r0 = pd.read_csv(TAB / "uji_acak.csv")
    lab = ["R0"] + t["code"].tolist()
    m = np.r_[r0["ndcg@10"], t["ndcg@10"]]
    lo = np.r_[r0["ndcg@10_lo"], t["ndcg@10_lo"]]
    hi = np.r_[r0["ndcg@10_hi"], t["ndcg@10_hi"]]
    warna = [ABU] + [MERAH if c == "U" else BIRU for c in t["code"]]
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    batang_ik(ax, lab, m, lo, hi, warna)
    ax.set_ylim(0.45, 0.76)
    ax.set_ylabel("NDCG@10 uji (IK 95%)")
    ax.set_xlabel("model")
    sumbu_koma(ax, 2)
    simpan(fig, "uji_baseline.png")


def uji_ablasi_skala() -> None:
    ab = pd.read_csv(TAB / "uji_ablasi.csv")
    assert ab["code"].tolist() == ["A1", "A2", "A3", "A4 (= U)"], ab["code"].tolist()
    sk = pd.read_csv(TAB / "uji_skala.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 3.6), gridspec_kw={"width_ratios": [1, 1.1]})
    batang_ik(a, ab["code"], ab["ndcg@10"].to_numpy(), ab["ndcg@10_lo"].to_numpy(), ab["ndcg@10_hi"].to_numpy(),
              [MERAH if "U" in c else BIRU for c in ab["code"]])
    a.set_ylim(0.68, 0.735)
    a.set_ylabel("NDCG@10 uji (IK 95%)")
    a.set_title("Ablasi fitur (skala E3)")
    sumbu_koma(a, 2)
    b.plot(sk["reviews"], sk["ndcg@10"], marker="o", color=BIRU)
    b.fill_between(sk["reviews"], sk["ndcg@10_lo"], sk["ndcg@10_hi"], color=BIRU, alpha=0.2, label="IK 95%")
    for x, y, s in zip(sk["reviews"], sk["ndcg@10"], sk["scale"]):
        b.annotate(f"{s}\n{koma(y, 3)}", (x, y), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9)
    b.set_xscale("log")
    tanda = [1e5, 2.5e5, 5e5, 1e6]       # 750.000 tidak diberi label agar tidak bertumpuk dengan 1 juta
    b.set_xticks(tanda, [koma(v / 1e6) + " juta" for v in tanda])
    b.minorticks_off()
    b.set_xlabel("jumlah ulasan latih (sumbu logaritmik)")
    b.set_ylabel("NDCG@10 uji")
    b.set_ylim(0.69, 0.74)
    b.set_title("Pengaruh jumlah data latih (model U)")
    b.legend(loc="lower right", frameon=False)
    sumbu_koma(b, 2)
    fig.tight_layout()
    simpan(fig, "uji_ablasi_skala.png")


def usia() -> None:
    g = pd.read_csv(TAB / "uji_per_kelompok_usia.csv").query("protokol_relevansi == 'T1'")
    kel = ["baru", "menengah", "lama"]
    nama = {"T1": "T1, suara mentah", "T2": "T2, pasangan berusia berdekatan", "T3": "T3, disesuaikan usia"}
    warna = {"T1": BIRU, "T2": HIJAU, "T3": MERAH}
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    w = 0.26
    for k, tg in enumerate(["T1", "T2", "T3"]):
        sub = g[g["target"] == tg].set_index("group").reindex(kel)
        x = np.arange(3) + (k - 1) * w
        ax.bar(x, sub["ndcg@10"], width=w, color=warna[tg], label=nama[tg])
        for xi, yi in zip(x, sub["ndcg@10"]):
            ax.text(xi, yi + 0.004, koma(yi, 3), ha="center", va="bottom", fontsize=8.5)
    ax.set_xticks(np.arange(3), ["ulasan baru", "ulasan menengah", "ulasan lama"])
    ax.set_ylim(0.60, 0.80)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5, steps=[1, 2, 5, 10]))
    ax.set_ylabel("NDCG@10 uji (acuan suara mentah)")
    ax.set_xlabel("kelompok usia ulasan")
    ax.legend(title="target pelatihan", loc="upper left", bbox_to_anchor=(1.0, 1.0), frameon=False)
    sumbu_koma(ax, 2)
    simpan(fig, "usia.png")


def uji_ukuran_produk() -> None:
    t = pd.read_csv(TAB / "uji_per_ukuran_produk.csv")
    lab = [f"kuartil {i + 1}\nmedian {koma(m)}" for i, m in enumerate(t["median_ulasan"])]
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    w = 0.38
    x = np.arange(len(t))
    for dx, kol, warna, nm in ((-w / 2, "ndcg@10", MERAH, "model U"), (w / 2, "ndcg@10_acak", ABU, "urutan acak (R0)")):
        ax.bar(x + dx, t[kol], width=w, color=warna, label=nm)
        for xi, yi in zip(x + dx, t[kol]):
            ax.text(xi, yi + 0.01, koma(yi, 3), ha="center", va="bottom", fontsize=9)
    ax.set_xticks(x, lab)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("NDCG@10 uji")
    ax.set_xlabel("kuartil ukuran produk (median jumlah ulasan uji per produk)")
    ax.legend(loc="upper right", frameon=False)
    sumbu_koma(ax, 1)
    simpan(fig, "uji_ukuran_produk.png")


def age_kurva() -> None:
    c = pd.read_csv(TAB / "age_kurva.csv")
    assert not c["di_luar_ik"].any(), "titik kurva usia di luar IK-nya sendiri"
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.plot(c["age_days"], c["ratio"], color=MERAH, label="taksiran")
    ax.fill_between(c["age_days"], c["lo"], c["hi"], color=MERAH, alpha=0.2, label="IK 95%")
    ax.axhline(1.0, color="grey", lw=0.8, ls="--")
    ax.set_xscale("log")
    ax.set_yscale("log")
    hari = [1, 7, 30, 365, 5 * 365, 25 * 365]
    ax.set_xticks(hari, ["1 hari", "1 minggu", "30 hari", "1 tahun", "5 tahun", "25 tahun"])
    ax.minorticks_off()
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: koma(v) if v < 1 else ribuan(v)))
    ax.set_xlabel("usia ulasan (sumbu logaritmik)")
    ax.set_ylabel("rasio rata-rata suara\nterhadap usia 30 hari")
    ax.legend(loc="upper left", frameon=False)
    simpan(fig, "age_kurva.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for f in (uji_baseline, uji_ablasi_skala, usia, uji_ukuran_produk, age_kurva):
        f()
