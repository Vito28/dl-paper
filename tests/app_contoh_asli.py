"""Uji contoh produk asli aplikasi dengan model U yang sebenarnya (butuh encoder BLaIR, sekitar 500 MB, dan
app/artefak/model_U.pt).

Untuk setiap ulasan di app/artefak/contoh_produk_uji.json, skor aplikasi harus sama dengan skor model U yang
tersimpan dari run (pred_test.parquet, dihitung di GPU T4 dengan fp16). Selisih kecil wajar karena presisi
berbeda, tetapi urutan di setiap produk harus sama.

    python -m tests.app_contoh_asli
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

APP = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP))
from inference import Pemeringkat, Ulasan, evaluasi_urutan  # noqa: E402


def main() -> None:
    data = json.loads((APP / "artefak" / "contoh_produk_uji.json").read_text())
    m = Pemeringkat(device="cpu")
    for p in data["produk"]:
        ul = [Ulasan(u["judul"], u["isi"], u["rating"], u["terverifikasi"]) for u in p["ulasan"]]
        s, mentah, _ = m.skor(ul)
        t = np.array([u["skor_U_tersimpan"] for u in p["ulasan"]])
        beda, rho = float(np.abs(s - t).max()), float(spearmanr(s, t).statistic)
        assert beda < 5e-3, f"{p['parent_asin']}: skor berbeda {beda}"
        assert rho > 0.999, f"{p['parent_asin']}: urutan berbeda (Spearman {rho})"
        v = np.array([u["helpful_vote"] for u in p["ulasan"]])
        ev = evaluasi_urutan(v, s, np.array([x["review_length"] for x in mentah]), m.cfg)
        print(f"{p['parent_asin']}: {len(ul)} ulasan, selisih skor maks {beda:.4f}, Spearman {rho:.5f}, "
              f"NDCG@10 U {ev['model']:.3f} / B0 {ev['panjang']:.3f} / acak {ev['acak']:.3f}")
    print("CONTOH ASLI LULUS")


if __name__ == "__main__":
    main()
