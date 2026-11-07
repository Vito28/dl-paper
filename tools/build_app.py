"""Bangun berkas turunan aplikasi Gradio di app/ dari kode dan hasil run.

Aplikasi di app/ harus mandiri (folder itu yang diunggah ke Hugging Face Spaces), tetapi langkah inferensinya
wajib sama persis dengan pipeline. Karena itu dua berkas di app/ TIDAK ditulis tangan:

- app/hr_inti.py              salinan persis clean_text (data.py), _title_for_pair (embed.py), Scorer
                              (models.py), grades (targets.py), dan dcg (metrics.py), diambil langsung dari src/hr.
- app/artefak/konfigurasi.json encoder, panjang token, arsitektur, urutan fitur, rata-rata/simpangan baku
                              standardisasi (split_report.json), dan ambang tingkat relevansi (thresholds.json).

Bobot model (app/artefak/model_U.pt) disalin manual dari Drive:
outputs/<kategori>/runs/<run>/model.pt.

    python tools/build_app.py           # tulis ulang kedua berkas
    python tools/build_app.py --check   # gagal jika salah satunya usang (dipakai tests/run_notebooks_smoke.py)
    python tools/build_app.py --hasil <folder hasil run> --keluar <folder app>   # misalnya untuk uji smoke
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from hr import data, embed, metrics, models, targets  # noqa: E402
from hr.config import STRUCT_FEATURES  # noqa: E402

HASIL_BAWAAN = REPO / "notebooks" / "FINISHED RUN" / "hasil_video_games"
KELUAR_BAWAAN = REPO / "app"
RUN_BAWAAN = "U_E3_T1_s42"   # model utama, seed 42 (NDCG@10 validasi terbaik di antara tiga seed)


def inti_source() -> str:
    src_data = inspect.getsource(data)
    konstanta = [line for line in src_data.splitlines() if re.match(r"_(TAG|CTRL|WS) = ", line)]
    assert len(konstanta) == 3, konstanta
    bagian = [inspect.getsource(data.clean_text), inspect.getsource(embed._title_for_pair),
              inspect.getsource(models.Scorer), inspect.getsource(targets.grades), inspect.getsource(metrics.dcg)]
    isi = "\n".join(konstanta) + "\n\n\n" + "\n\n".join(bagian)
    digest = hashlib.sha256(isi.encode()).hexdigest()[:12]
    return f'''"""DIBANGUN OTOMATIS oleh tools/build_app.py dari src/hr (versi {digest}). Jangan diedit langsung.

Salinan persis fungsi pipeline yang dibutuhkan saat inferensi, agar aplikasi menghitung skor dengan cara yang sama
dengan run yang dilaporkan.
"""
from __future__ import annotations

import html
import re

import numpy as np
import torch
import torch.nn as nn

{isi}'''


def konfigurasi(hasil: Path, run: str) -> dict:
    cfg = json.loads((hasil / "config.json").read_text())
    std = json.loads((hasil / "split_report.json").read_text())["standardizer"]
    hp = json.loads((hasil / "best_hparams.json").read_text())
    emb = json.loads((hasil / "emb_blair.json").read_text())
    thr = json.loads((hasil / "thresholds.json").read_text())
    if emb["model"] != cfg["encoders"]["blair"] or emb.get("pooling") != "cls+l2":
        raise ValueError(f"emb_blair.json tidak sesuai config.json: {emb}")
    if set(std) != set(STRUCT_FEATURES):
        raise ValueError(f"Fitur standardisasi {sorted(std)} berbeda dari STRUCT_FEATURES {STRUCT_FEATURES}")
    return {
        "kategori": cfg["category"],
        "run": run,
        "encoder": emb["model"],
        "max_len": emb["max_len"],
        "pooling": emb["pooling"],
        "hidden": cfg["hidden"],
        "dropout": hp["dropout"],
        "fitur": list(STRUCT_FEATURES),
        "standardisasi": {f: std[f] for f in STRUCT_FEATURES},
        "ambang_tingkat": thr["q_t1"],          # tingkat relevansi 0-4 dari ln(1 + helpful votes), untuk NDCG
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hasil", type=Path, default=HASIL_BAWAAN)
    ap.add_argument("--keluar", type=Path, default=KELUAR_BAWAAN)
    ap.add_argument("--run", default=RUN_BAWAAN)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    target = {a.keluar / "hr_inti.py": inti_source(),
              a.keluar / "artefak" / "konfigurasi.json":
                  json.dumps(konfigurasi(a.hasil, a.run), indent=2, ensure_ascii=False) + "\n"}
    for path, text in target.items():
        if a.check:
            if not path.exists() or path.read_text() != text:
                sys.exit(f"{path} usang. Jalankan: python tools/build_app.py")
            print(f"{path.relative_to(a.keluar.parent)} sesuai dengan sumbernya")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            print("ditulis", path)


if __name__ == "__main__":
    main()
