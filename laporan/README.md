# Folder laporan

Satu-satunya folder untuk laporan dan dokumen pendukungnya. Kode ada di `src/`, `notebooks/`, `tools/`, dan `tests/`.

```
laporan/
├── README.md                  peta folder ini
├── LAPORAN.md                 laporan tugas mata kuliah (ditulis ulang dari awal, 7 Nov 2026)
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
| Versi library, EDA tambahan, arsitektur, analisis kesalahan | keluaran `bahan_laporan.ipynb` di Drive, `outputs/Video_Games/laporan/` |
| Protokol eksperimen dan aturan yang dikunci di kode | `EXPERIMENTS.md` di akar repo |
| Struktur laporan | `referensi/pedoman/Format Laporan Tugas Pembelajaran Mendalam.pdf` |

## Gambar

`gambar/` berisi grafik dari run Video_Games (`notebooks/FINISHED RUN/hasil_video_games/figures/`). Grafik buatan
`bahan_laporan.ipynb` disalin dari `outputs/Video_Games/laporan/figures/` di Drive ke `gambar/` dengan nama yang sama.

## Keputusan yang berlaku

- Aplikasi demo memakai Gradio di Hugging Face Spaces.
- Ini Proyek 1, jadi butir format "pengembangan dari Tugas Proyek 2" tidak dipakai.
- Hanya kategori Video_Games yang dijalankan. Semua kategori direncanakan untuk UAS.
- Repo akan dibuat publik agar tautan GitHub bisa dibuka tanpa meminta akses.
