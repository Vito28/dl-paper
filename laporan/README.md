# Folder laporan

Satu-satunya folder untuk laporan dan dokumen pendukungnya. Kode ada di `src/`, `notebooks/`, `tools/`, dan `tests/`.

```
laporan/
├── README.md                  peta folder ini
├── LAPORAN.md                 laporan tugas mata kuliah (ditulis ulang dari awal, 7 Nov 2026)
├── PEMBAGIAN_TUGAS.md         daftar pekerjaan sebagai bahan tabel Pembagian Tugas
├── bahan_laporan.ipynb        notebook Colab untuk angka, tabel, dan grafik yang butuh runtime
├── gambar/                    gambar yang dirujuk LAPORAN.md
├── referensi/
│   ├── Referensi Skripsi (Zotero).bib / .ris    daftar pustaka Zotero
│   ├── pustaka/               PDF artikel rujukan
│   └── pedoman/               format laporan mata kuliah dan template jurnal JuTISI
└── arsip/
    └── 2026-11-07_sebelum_run/   naskah dan catatan lama (dibekukan, jangan dipakai sebagai sumber)
```

## Sumber isi laporan

| Isi | Sumber |
|---|---|
| Angka hasil eksperimen | `notebooks/FINISHED RUN/hasil_video_games/` (tabel, gambar, JSON) |
| Kurva latih dan validasi (subbab 6c) | `notebooks/FINISHED RUN/kurva_latih/` (pelatihan ulang U *seed* 42 oleh `notebooks/00c_kurva_latih.ipynb`) |
| Versi library, EDA tambahan, arsitektur, analisis kesalahan | keluaran `bahan_laporan.ipynb` di Drive, `outputs/Video_Games/laporan/` |
| Protokol eksperimen dan aturan yang dikunci di kode | `EXPERIMENTS.md` di akar repo |
| Struktur laporan | `referensi/pedoman/Format Laporan Tugas Pembelajaran Mendalam.pdf` |

## Gambar

`gambar/` berisi grafik dari run Video_Games (`notebooks/FINISHED RUN/hasil_video_games/figures/`). Grafik buatan
`bahan_laporan.ipynb` disalin dari `outputs/Video_Games/laporan/figures/` di Drive ke `gambar/` dengan nama yang sama.

Lima grafik yang berasal langsung dari tabel hasil (`uji_baseline`, `uji_ablasi_skala`, `usia`, `uji_ukuran_produk`,
`age_kurva`) digambar ulang dengan koma desimal dan label Indonesia oleh `python tools/gambar_laporan.py`, yang hanya
membaca `notebooks/FINISHED RUN/hasil_video_games/tables/`. `kurva_latih_validasi.png` (subbab 6c) berasal dari
`notebooks/00c_kurva_latih.ipynb`.

## PDF

`python tools/build_pdf.py laporan/LAPORAN.md laporan/LAPORAN.pdf [--final]` (butuh `markdown-it-py`,
`beautifulsoup4`, dan `weasyprint`). Daftar Isi, Daftar Gambar, dan Daftar Tabel dibangun ulang dengan nomor halaman.
Dengan `--final`, pembuatan PDF gagal selama masih ada penanda ⟦…⟧.

## Keputusan yang berlaku

- Aplikasi demo memakai Gradio di Hugging Face Spaces.
- Ini Proyek 1, jadi butir format "pengembangan dari Tugas Proyek 2" tidak dipakai.
- Format yang berlaku adalah `Format Laporan Tugas Pembelajaran Mendalam.pdf`, bukan format UTS.
- Fitur unik 1 adalah pelatihan berpasangan RankNet untuk label yang tidak seimbang, dan fitur unik 2 adalah fusi
  embedding dengan fitur terstruktur. Target yang disesuaikan usia (T3) dilaporkan sebagai skenario di subbab 6d.
- U tetap model utama walaupun B5 lebih baik, karena desain dikunci sebelum data uji dilihat (alasan di subbab 5d).
- Hanya kategori Video_Games yang dijalankan. Semua kategori direncanakan untuk UAS.
- Repo akan dibuat publik agar tautan GitHub bisa dibuka tanpa meminta akses.
