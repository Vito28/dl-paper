"""Inferensi model U untuk aplikasi Gradio.

Langkahnya sama dengan pipeline (src/hr), dan fungsi intinya disalin otomatis ke hr_inti.py:
1. Judul dan isi dibersihkan dengan ``clean_text`` (preprocessing, data.py).
2. Lima fitur terstruktur dihitung dari teks bersih, diubah dengan ln(1 + x) untuk fitur panjang, lalu
   distandardisasi dengan rata-rata dan simpangan baku data latih (konfigurasi.json).
3. Judul (paling banyak 64 kata) dan isi ditokenisasi sebagai pasangan teks, maksimum 512 token, dan hanya isi
   yang dipotong (embed.extract_embeddings). Embedding = token pertama lapisan terakhir, dinormalisasi L2.
4. Embedding dan fitur disimpan sebagai float16 seperti di pipeline (features.fuse), digabung, lalu diberi skor
   oleh MLP U. Ulasan diurutkan dari skor tertinggi.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from hr_inti import Scorer, _title_for_pair, clean_text

# HR_APP_ARTEFAK dapat menunjuk folder artefak lain, misalnya hasil smoke untuk pengujian.
ARTEFAK = Path(os.environ.get("HR_APP_ARTEFAK") or Path(__file__).resolve().parent / "artefak")


@dataclass
class Ulasan:
    judul: str
    isi: str
    rating: float
    terverifikasi: bool


def fitur_terstruktur(ulasan: list[Ulasan], cfg: dict) -> tuple[np.ndarray, list[dict]]:
    """Fitur z (n x 5) dalam urutan cfg["fitur"], ditambah nilai mentahnya untuk ditampilkan."""
    mentah = []
    for u in ulasan:
        judul, isi = clean_text(u.judul), clean_text(u.isi)
        mentah.append({
            "rating": float(u.rating),
            "verified_purchase": 1.0 if u.terverifikasi else 0.0,
            "review_length": len(isi),
            "word_count": len(isi.split()),
            "title_length": len(judul),
        })
    nilai = {
        "rating": [m["rating"] for m in mentah],
        "verified_purchase": [m["verified_purchase"] for m in mentah],
        "log_review_length": [np.log1p(m["review_length"]) for m in mentah],
        "log_word_count": [np.log1p(m["word_count"]) for m in mentah],
        "log_title_length": [np.log1p(m["title_length"]) for m in mentah],
    }
    std = cfg["standardisasi"]
    z = np.column_stack([(np.asarray(nilai[f], dtype=np.float64) - std[f][0]) / std[f][1] for f in cfg["fitur"]])
    return z.astype(np.float32), mentah


class Pemeringkat:
    def __init__(self, artefak: Path = ARTEFAK, device: str | None = None):
        from transformers import AutoModel, AutoTokenizer

        artefak = Path(artefak)
        self.cfg = json.loads((artefak / "konfigurasi.json").read_text())
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tok = AutoTokenizer.from_pretrained(self.cfg["encoder"])
        enc = AutoModel.from_pretrained(self.cfg["encoder"]).to(self.device).eval()
        self.encoder = enc.half() if self.device == "cuda" else enc     # sama dengan run (fp16 hanya di GPU)
        d_in = self.encoder.config.hidden_size + len(self.cfg["fitur"])
        self.mlp = Scorer(d_in, hidden=tuple(self.cfg["hidden"]), dropout=self.cfg["dropout"])
        state = torch.load(artefak / "model_U.pt", map_location="cpu", weights_only=True)
        self.mlp.load_state_dict(state, strict=True)                     # gagal keras jika arsitektur berbeda
        self.mlp.to(self.device).eval()

    @torch.inference_mode()
    def embedding(self, judul: list[str], isi: list[str], batch: int = 16) -> np.ndarray:
        judul = [_title_for_pair(clean_text(t)) for t in judul]
        isi = [clean_text(t) for t in isi]
        out = np.empty((len(isi), self.encoder.config.hidden_size), dtype=np.float16)
        urut = np.argsort([len(t) for t in isi], kind="stable")          # panjang mirip = padding sedikit
        for i in range(0, len(isi), batch):
            b = urut[i:i + batch]
            enc = self.tok([judul[k] for k in b], [isi[k] for k in b], truncation="only_second",
                           max_length=self.cfg["max_len"], padding=True, return_tensors="pt").to(self.device)
            h = F.normalize(self.encoder(**enc).last_hidden_state[:, 0].float(), dim=-1)
            out[b] = h.cpu().numpy().astype(np.float16)
        return out

    @torch.inference_mode()
    def skor(self, ulasan: list[Ulasan]) -> tuple[np.ndarray, list[dict], float]:
        """Skor setiap ulasan (makin tinggi makin bermanfaat), fitur mentah, dan waktu proses dalam detik."""
        t0 = time.time()
        z, mentah = fitur_terstruktur(ulasan, self.cfg)
        e = self.embedding([u.judul for u in ulasan], [u.isi for u in ulasan])
        x = np.hstack([e.astype(np.float16), z.astype(np.float16)])      # sama dengan features.fuse
        s = self.mlp(torch.as_tensor(x, device=self.device)).float().cpu().numpy()
        if not np.isfinite(s).all():
            raise FloatingPointError("Skor NaN/inf. Periksa berkas model.")
        return s, mentah, time.time() - t0
