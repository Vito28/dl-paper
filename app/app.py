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

from contoh import KOLOM, muat_contoh
from inference import Pemeringkat, Ulasan, evaluasi_urutan

MAKS_ULASAN = 100          # di CPU encoder memproses sekitar 2 ulasan per detik; di ZeroGPU 100 ulasan < 1 detik

CONTOH = muat_contoh()
CONTOH_AWAL = next(iter(CONTOH))
model = Pemeringkat()
cfg = model.cfg


def _kosong(v) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v)) or (isinstance(v, str) and not v.strip())


def _teks(v) -> str:
    return "" if _kosong(v) else str(v).strip()


def _bool(v) -> bool:
    if isinstance(v, str):
        return v.strip().lower() in {"ya", "y", "true", "1", "yes"}
    return bool(v) and not (isinstance(v, float) and math.isnan(v))


def _tabel(baris) -> pd.DataFrame:
    return pd.DataFrame(baris, columns=KOLOM)


def baca_tabel(tabel: pd.DataFrame) -> tuple[list[Ulasan], list[float] | None, list[str]]:
    """Ubah tabel masukan menjadi daftar ulasan, helpful votes asli (None jika tidak lengkap), dan catatan."""
    ulasan, suara, catatan = [], [], []
    for i, r in enumerate(tabel.itertuples(index=False), start=1):
        r = list(r) + [None] * (len(KOLOM) - len(r))
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
        if _kosong(r[4]):
            suara.append(None)
        else:
            try:
                v = float(r[4])
            except (TypeError, ValueError):
                raise gr.Error(f"Helpful votes pada baris {i} harus berupa bilangan bulat ≥ 0 atau dikosongkan.")
            if v < 0 or v != int(v):
                raise gr.Error(f"Helpful votes pada baris {i} harus bilangan bulat ≥ 0, bukan {v:g}.")
            suara.append(v)
        ulasan.append(Ulasan(judul, isi, rating, _bool(r[3])))
    terisi = [v is not None for v in suara]
    if any(terisi) and not all(terisi):
        catatan.append("helpful votes asli hanya diisi sebagian, sehingga evaluasi NDCG@10 dilewati")
    return ulasan, (suara if suara and all(terisi) else None), catatan


@GPU
def urutkan(tabel: pd.DataFrame):
    """Urutkan ulasan satu produk dari yang paling bermanfaat menurut model U. Jika helpful votes asli diisi untuk
    semua ulasan, urutan model juga dinilai dengan NDCG@10 terhadap suara itu."""
    ulasan, suara, catatan = baca_tabel(tabel)
    if len(ulasan) < 2:
        raise gr.Error("Masukkan sedikitnya dua ulasan berisi teks untuk produk yang sama.")
    if len(ulasan) > MAKS_ULASAN:
        raise gr.Error(f"Paling banyak {MAKS_ULASAN} ulasan sekali proses.")

    skor, mentah, detik = model.skor(ulasan)
    urut = np.argsort(-skor, kind="stable")
    pjg = np.array([m["review_length"] for m in mentah])
    peringkat_b0 = np.empty(len(pjg), dtype=int)
    peringkat_b0[np.argsort(-pjg, kind="stable")] = np.arange(1, len(pjg) + 1)
    ev = evaluasi_urutan(np.array(suara), skor, pjg, cfg) if suara is not None else None

    hasil = []
    for k, j in enumerate(urut):
        u = ulasan[j]
        baris = {"Peringkat": k + 1, "Skor": round(float(skor[j]), 3), "Judul": u.judul,
                 "Isi ulasan": u.isi if len(u.isi) <= 160 else u.isi[:157] + "...",
                 "Jumlah kata": mentah[j]["word_count"], "Rating": f"{u.rating:g}",
                 "Terverifikasi": "ya" if u.terverifikasi else "tidak",
                 "Peringkat menurut panjang (B0)": int(peringkat_b0[j])}
        if suara is not None:
            baris["Helpful votes asli"] = int(suara[j])
            baris["Peringkat menurut suara asli"] = int(1 + sum(v > suara[j] for v in suara))
        hasil.append(baris)

    info = [f"**{len(ulasan)} ulasan diurutkan dalam {detik:.1f} detik.** Skor hanya bermakna relatif di dalam "
            "satu produk. Makin tinggi skornya, makin bermanfaat ulasan itu menurut model."]
    if suara is not None and ev is None:
        info.append("Semua ulasan bernilai 0 helpful votes, sehingga NDCG@10 tidak terdefinisi (sama seperti pada "
                    "evaluasi laporan, produk seperti ini tidak dinilai).")
    elif ev is not None:
        info.append(
            f"**Dibandingkan dengan helpful votes asli (NDCG@10, 1 = urutan sempurna):** model U **{ev['model']:.3f}**, "
            f"urutan menurut panjang (B0) {ev['panjang']:.3f}, urutan acak rata-rata {ev['acak']:.3f}. "
            "Ini hanya satu produk, sehingga angkanya bisa jauh dari rata-rata data uji di laporan "
            "(model U 0,715, B0 0,702, acak 0,499).")
    if catatan:
        info.append("Catatan: " + "; ".join(catatan) + ".")
    return pd.DataFrame(hasil), "\n\n".join(info)


def muat(nama: str):
    c = CONTOH[nama]
    return _tabel(c["baris"]), c["keterangan"]


def kosongkan():
    return _tabel([["", "", 5, True, None], ["", "", 5, True, None]]), "Tabel dikosongkan. Isi sedikitnya dua ulasan."


DESKRIPSI = f"""
# Pemeringkatan Ulasan Produk Berdasarkan Kebermanfaatan

Masukkan beberapa ulasan untuk **satu produk**, atau pilih contoh di bawah, lalu klik **Urutkan ulasan**. Model
mengurutkan ulasan dari yang paling bermanfaat bagi pembaca.

**Model U.** Judul dan isi ulasan diubah menjadi embedding oleh encoder **BLaIR-RoBERTa-base** yang dibekukan
(`{cfg['encoder']}`), digabung dengan lima fitur terstruktur (rating, pembelian terverifikasi, dan tiga fitur
panjang), lalu diberi skor oleh MLP 773-256-64-1 yang dilatih dengan loss pemeringkatan berpasangan RankNet.
Model dilatih pada kategori **{cfg['kategori']}** dari Amazon Reviews 2023 dengan label *helpful votes* (run
`{cfg['run']}`). Pada data uji, NDCG@10 model ini 0,715, sedangkan urutan acak 0,499.

**Cara membaca hasil.** Kolom *Peringkat menurut panjang (B0)* menunjukkan urutan jika ulasan hanya diurutkan
menurut panjangnya, sebagai pembanding. Jika kolom *Helpful votes asli* diisi untuk semua ulasan, aplikasi juga
menghitung NDCG@10 urutan model terhadap suara itu, dengan cara yang sama seperti evaluasi di laporan.

**Batasan.** Ulasan sebaiknya berbahasa Inggris, dan model paling sesuai untuk produk gim video. Helpful votes
adalah label yang lemah, karena ulasan yang lebih lama sempat dibaca lebih banyak orang. Karena itu skor model
adalah perkiraan, bukan penilaian pasti.
"""

with gr.Blocks(title="Pemeringkatan Ulasan Helpful") as demo:
    gr.Markdown(DESKRIPSI)
    with gr.Row():
        pilihan = gr.Dropdown(list(CONTOH), value=CONTOH_AWAL, label="Contoh produk", scale=3)
        tombol_muat = gr.Button("Muat contoh", scale=1)
    keterangan_contoh = gr.Markdown(CONTOH[CONTOH_AWAL]["keterangan"])
    masukan = gr.Dataframe(value=_tabel(CONTOH[CONTOH_AWAL]["baris"]), headers=KOLOM,
                           datatype=["str", "str", "number", "bool", "number"], interactive=True,
                           label="Ulasan satu produk (tambah, ubah, atau hapus baris sesuai kebutuhan)")
    with gr.Row():
        tombol = gr.Button("Urutkan ulasan", variant="primary", scale=2)
        tombol_kosong = gr.Button("Kosongkan tabel", scale=1)
    keterangan = gr.Markdown()
    keluaran = gr.Dataframe(label="Hasil, dari ulasan paling bermanfaat menurut model", interactive=False)

    tombol.click(urutkan, inputs=masukan, outputs=[keluaran, keterangan])
    tombol_muat.click(muat, inputs=pilihan, outputs=[masukan, keterangan_contoh])
    pilihan.change(muat, inputs=pilihan, outputs=[masukan, keterangan_contoh])
    tombol_kosong.click(kosongkan, outputs=[masukan, keterangan_contoh])

if __name__ == "__main__":
    demo.launch()
