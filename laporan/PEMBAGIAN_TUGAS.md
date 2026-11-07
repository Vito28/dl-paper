# Daftar Pekerjaan untuk Pembagian Tugas

Daftar ini memuat semua pekerjaan proyek sampai 7 November 2026, sebagai bahan tabel **Pembagian Tugas** di
`LAPORAN.md` (kolom NIM, Nama, Peran, Rincian Pekerjaan). Kolom "Kontributor di git" diambil dari riwayat commit dan
hanya menjadi petunjuk awal, karena sebagian pekerjaan (diskusi, Colab, penulisan di luar repo) tidak tercatat di
git. Kelompok yang menentukan pembagian akhirnya.

## Paket pekerjaan

| No | Pekerjaan | Rincian | Hasil atau bukti | Kontributor di git | Status |
|---|---|---|---|---|---|
| 1 | Perumusan masalah dan kajian pustaka | Pemilihan topik, rumusan masalah, penelitian terkait, daftar pustaka Zotero | Naskah Bab I–II, `laporan/referensi/` | Vito, Dickson | Selesai, pustaka sedang dirapikan |
| 2 | Rancangan metode (Bab III) | Rancangan eksperimen, baseline B0–B5, ablasi, skala data, target T1–T3 | Naskah Bab III, `EXPERIMENTS.md` | Dickson, Vito | Selesai |
| 3 | Revisi naskah | Revisi Bab I–II dan penerapan catatan koreksi | `Revisi.docx`, catatan koreksi di arsip | Elvina, Dickson, Drew | Koreksi belum dimasukkan ke Word |
| 4 | Pengumpulan dan preprocessing data | Unduhan dataset, pembersihan teks, duplikat, pemeriksaan timestamp | `src/hr/data.py`, notebook 01–02 | Vito, Drew | Selesai |
| 5 | Exploratory Data Analysis | Sebaran label, jumlah kata, histogram fitur, korelasi, contoh ulasan | Notebook 02, `bahan_laporan.ipynb` bagian 2 | Vito, Drew | Selesai |
| 6 | Pembagian data dan pencegahan kebocoran | Pembagian per produk, pemeriksaan kebocoran, skala E1–E5 | `src/hr/split.py`, notebook 03 | Vito | Selesai |
| 7 | Pembentukan target dan model usia | Target T1/T2/T3, model Negative Binomial, kurva usia dan IK bootstrap | `src/hr/targets.py`, notebook 03 | Vito, Drew | Selesai |
| 8 | Ekstraksi embedding teks | Embedding BLaIR dan RoBERTa-base di GPU Colab | `src/hr/embed.py`, notebook 04 | Vito | Selesai |
| 9 | Pengembangan dan pelatihan model | MLP dengan loss RankNet, penalaan hiperparameter, early stopping | `src/hr/models.py`, `train.py`, `pairs.py`, notebook 05 | Vito | Selesai |
| 10 | Baseline dan eksperimen | Baseline B0–B5, ablasi A1–A3, skala data, strategi target | `src/hr/features.py`, notebook 05–06 | Vito | Selesai |
| 11 | Evaluasi dan statistik | Metrik, bootstrap, koreksi Holm, konsistensi per seed, urutan acak R0, analisis kesalahan | `metrics.py`, `stats.py`, `report.py`, notebook 07 | Vito, Drew | Selesai |
| 12 | Visualisasi | Semua grafik laporan | `src/hr/plots.py`, notebook 08, `bahan_laporan.ipynb` | Vito, Drew | Selesai |
| 13 | Rekayasa pipeline dan pengendalian mutu | Notebook Colab tunggal, penyimpanan di Drive, pemeriksaan galat, notebook rekonsiliasi, smoke test | `00_pipeline_lengkap`, `00b_rekonsiliasi`, `src/hr/stages.py`, `tools/`, `tests/` | Drew | Selesai |
| 14 | Menjalankan eksperimen | Run Colab sekitar 8,5 jam, run rekonsiliasi, run bahan laporan, pelatihan ulang untuk kurva 6c | `notebooks/FINISHED RUN/` | Drew | Selesai |
| 15 | Aplikasi Gradio dan deployment | Modul inferensi, antarmuka, contoh produk uji asli, hosting di Hugging Face Spaces (ZeroGPU), uji kesetaraan skor dan kecepatan | `app/`, `tools/build_app.py`, `tests/app_*.py`, https://huggingface.co/spaces/Nathjsn/pemeringkatan-ulasan-helpful | Drew | Selesai, tangkapan layar untuk laporan belum |
| 16 | Penulisan laporan | `LAPORAN.md` bagian 1–9 sesuai format Tugas, grafik laporan, kurva latih dan validasi (subbab 6c), cover, pembagian tugas, ekspor ke PDF | `laporan/LAPORAN.md`, `tools/gambar_laporan.py`, `notebooks/00c_kurva_latih.ipynb`, `tools/build_pdf.py` | Drew | Draf selesai. Belum: cover dan pembagian tugas |
| 17 | Pemeriksaan akhir dan pengumpulan | Audit format laporan, pemeriksaan angka laporan terhadap hasil run, repo dijadikan publik, tautan diperiksa | GitHub, `tools/build_pdf.py --final` | Drew | Audit format dan angka selesai. Repo belum publik. |

Notebook 09 (fine-tuning encoder) dan 10 (validasi label manusia) ada di kode tetapi belum dijalankan, sehingga tidak
dicantumkan sebagai pekerjaan selesai.

## Usulan pengelompokan per peran

| Peran | Paket pekerjaan |
|---|---|
| Data dan EDA | 4, 5, 6 |
| Pemodelan dan eksperimen | 7, 8, 9, 10 |
| Evaluasi dan analisis | 11, 12 |
| Rekayasa sistem dan deployment | 13, 14, 15 |
| Dokumentasi | 1, 2, 3, 16, 17 |

## Templat tabel untuk LAPORAN.md

| NIM | Nama | Peran | Rincian Pekerjaan |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
