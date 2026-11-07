"""Aplikasi demo Gradio: pemeringkatan ulasan produk berdasarkan kebermanfaatan (model U).

Jalankan lokal dengan `python app.py`. Di Hugging Face Spaces, berkas ini dijalankan otomatis.
"""
from __future__ import annotations

# ZeroGPU di Hugging Face Spaces: `spaces` wajib diimpor sebelum torch. Di luar Spaces paket ini tidak perlu
# ada, dan dekoratornya diganti fungsi identitas sehingga aplikasi tetap berjalan di CPU.
try:
    import spaces
    GPU = spaces.GPU(duration=15)   # diukur: 0,6 detik saat cold start, < 0,1 detik setelahnya
except ImportError:
    def GPU(fn):
        return fn

import math

import gradio as gr
import numpy as np
import pandas as pd

from inference import Pemeringkat, Ulasan

MAKS_ULASAN = 50           # di CPU encoder memproses sekitar 2 ulasan per detik, jadi jumlah ulasan dibatasi
KOLOM = ["Judul", "Isi ulasan", "Rating (1-5)", "Pembelian terverifikasi"]

# Contoh buatan untuk sebuah gim fiktif (bukan ulasan asli dari dataset).
CONTOH = pd.DataFrame([
    ["Five Stars", "Great game", 5, True],
    ["Fun but the campaign is short",
     "I finished the story in about six hours on normal difficulty. Combat feels tight and the boss fights are "
     "creative, but there is little reason to replay. Online co-op adds some value if you have friends who own it. "
     "Wait for a sale unless you only care about the campaign.", 4, True],
    ["Do not buy the digital deluxe edition",
     "The deluxe edition only adds two cosmetic skins and a soundtrack you can stream for free. The base game is the "
     "same. Save your money.", 2, True],
    ["Love it", "My son plays it every day after school.", 5, False],
    ["Crashes on older consoles",
     "On the original console model the game crashes when loading the third area. Clearing the system cache and "
     "reinstalling fixed it for me, and the latest patch improved loading times. On the newer model it runs smoothly "
     "at a stable frame rate. Check your hardware before buying.", 3, True],
], columns=KOLOM)

model = Pemeringkat()
cfg = model.cfg


def _teks(v) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    return str(v).strip()


def _bool(v) -> bool:
    if isinstance(v, str):
        return v.strip().lower() in {"ya", "y", "true", "1", "yes"}
    return bool(v) and not (isinstance(v, float) and math.isnan(v))


@GPU
def urutkan(tabel: pd.DataFrame):
    """Urutkan ulasan satu produk dari yang paling bermanfaat menurut model U."""
    ulasan, catatan = [], []
    for i, r in enumerate(tabel.itertuples(index=False), start=1):
        judul, isi = _teks(r[0]), _teks(r[1])
        if not isi:
            if judul:
                catatan.append(f"baris {i} dilewati karena isi ulasan kosong")
            continue
        try:
            rating = float(r[2])
        except (TypeError, ValueError):
            raise gr.Error(f"Rating pada baris {i} harus berupa angka 1 sampai 5.")
        if not 1 <= rating <= 5:
            raise gr.Error(f"Rating pada baris {i} harus 1 sampai 5, bukan {rating:g}.")
        ulasan.append(Ulasan(judul, isi, rating, _bool(r[3])))
    if len(ulasan) < 2:
        raise gr.Error("Masukkan sedikitnya dua ulasan berisi teks untuk produk yang sama.")
    if len(ulasan) > MAKS_ULASAN:
        raise gr.Error(f"Paling banyak {MAKS_ULASAN} ulasan sekali proses.")

    skor, mentah, detik = model.skor(ulasan)
    urut = np.argsort(-skor, kind="stable")
    pjg = np.array([m["review_length"] for m in mentah])
    peringkat_b0 = np.empty(len(pjg), dtype=int)
    peringkat_b0[np.argsort(-pjg, kind="stable")] = np.arange(1, len(pjg) + 1)
    hasil = pd.DataFrame([{
        "Peringkat": k + 1,
        "Skor": round(float(skor[j]), 3),
        "Judul": ulasan[j].judul,
        "Isi ulasan": ulasan[j].isi if len(ulasan[j].isi) <= 160 else ulasan[j].isi[:157] + "...",
        "Jumlah kata": mentah[j]["word_count"],
        "Rating": f"{ulasan[j].rating:g}",
        "Terverifikasi": "ya" if ulasan[j].terverifikasi else "tidak",
        "Peringkat menurut panjang (B0)": int(peringkat_b0[j]),
    } for k, j in enumerate(urut)])
    info = (f"{len(ulasan)} ulasan diurutkan dalam {detik:.1f} detik. Skor hanya bermakna relatif di dalam satu "
            "produk. Makin tinggi skornya, makin bermanfaat ulasan itu menurut model.")
    if catatan:
        info += " Catatan: " + "; ".join(catatan) + "."
    return hasil, info


DESKRIPSI = f"""
# Pemeringkatan Ulasan Produk Berdasarkan Kebermanfaatan

Masukkan beberapa ulasan untuk **satu produk**. Model mengurutkan ulasan dari yang paling bermanfaat bagi pembaca.

**Model U.** Judul dan isi ulasan diubah menjadi embedding oleh encoder **BLaIR-RoBERTa-base** yang dibekukan
(`{cfg['encoder']}`), digabung dengan lima fitur terstruktur (rating, pembelian terverifikasi, dan tiga fitur
panjang), lalu diberi skor oleh MLP 773-256-64-1 yang dilatih dengan loss pemeringkatan berpasangan RankNet.
Model dilatih pada kategori **{cfg['kategori']}** dari Amazon Reviews 2023 dengan label *helpful votes* (run
`{cfg['run']}`). Pada data uji, NDCG@10 model ini 0,715, sedangkan urutan acak 0,499.

Kolom terakhir hasil menunjukkan urutan menurut panjang ulasan saja (baseline B0), sebagai pembanding.
Batasan: ulasan sebaiknya berbahasa Inggris, dan model paling sesuai untuk produk gim video. Helpful votes adalah
label yang lemah, sehingga skor model adalah perkiraan, bukan penilaian pasti.
"""

with gr.Blocks(title="Pemeringkatan Ulasan Helpful") as demo:
    gr.Markdown(DESKRIPSI)
    masukan = gr.Dataframe(value=CONTOH, headers=KOLOM, datatype=["str", "str", "number", "bool"],
                           interactive=True, label="Ulasan satu produk (tambah atau ubah baris sesuai kebutuhan)")
    with gr.Row():
        tombol = gr.Button("Urutkan ulasan", variant="primary")
        kosongkan = gr.Button("Kosongkan tabel")
        contoh = gr.Button("Muat contoh")
    keterangan = gr.Markdown()
    keluaran = gr.Dataframe(label="Hasil, dari ulasan paling bermanfaat", interactive=False)

    tombol.click(urutkan, inputs=masukan, outputs=[keluaran, keterangan])
    kosongkan.click(lambda: pd.DataFrame([["", "", 5, True], ["", "", 5, True]], columns=KOLOM), outputs=masukan)
    contoh.click(lambda: CONTOH, outputs=masukan)

if __name__ == "__main__":
    demo.launch()
