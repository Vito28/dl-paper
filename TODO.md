# TODO

Diperbarui 7 November 2026. Pembagian pekerjaan lengkap ada di `laporan/PEMBAGIAN_TUGAS.md`.

## Aplikasi Gradio (`app/`)

- [x] Antarmuka, langkah inferensi, dan berkas turunan otomatis (`tools/build_app.py`)
- [x] Uji kesetaraan dengan pipeline pada data smoke (`python -m tests.app_smoke`): selisih fitur 0, embedding 0,
      skor < 1e-8
- [x] Salin bobot model U dari Drive `outputs/Video_Games/runs/U_E3_T1_s42/model.pt` ke `app/artefak/model_U.pt`
      (dimuat strict, 214.657 parameter)
- [x] Uji aplikasi secara lokal dengan encoder BLaIR asli dan bobot di atas (5 ulasan contoh sekitar 1–2 detik,
      20 ulasan sekitar 5 detik di CPU laptop 8 thread; urutan masuk akal)
- [ ] Buat Hugging Face Space (SDK Gradio), unggah isi `app/`, lalu catat tautannya
- [ ] Isi LAPORAN.md bagian 7d: tautan Space, tangkapan layar, dan waktu inferensi di CPU Spaces

## Laporan (`laporan/LAPORAN.md`)

- [x] Isi Bagian A 1–9 dari hasil run dan `bahan_laporan.ipynb`
- [x] Gambar resolusi 300 dpi di `laporan/gambar/`
- [ ] Cover (kelompok)
- [ ] Tabel Pembagian Tugas (kelompok, bahan di `laporan/PEMBAGIAN_TUGAS.md`)
- [ ] Daftar pustaka: tambahkan RoBERTa, Efron & Tibshirani (bootstrap), dan Holm ke Zotero (sedang dikerjakan)
- [ ] Ekspor ke satu PDF dengan urutan Cover, Bagian Awal, Bagian A, Bagian B

## Naskah jurnal

- [ ] Masukkan koreksi Bab I–III ke Word. Catatannya ada di
      `laporan/arsip/2026-11-07_sebelum_run/catatan/koreksi/`

## Repo dan pengumpulan

- [ ] Commit perubahan yang belum di-commit, setelah pemiliknya dipastikan: reorganisasi `laporan/`, serta
      perubahan di `src/hr/config.py`, `src/hr/finetune.py`, `src/hr/human.py`, notebook 00/00b/09/10, dan
      `readme.md`
- [ ] Jadikan repo GitHub publik, karena tautan di Bagian B harus bisa dibuka tanpa meminta akses
- [ ] Periksa bahwa angka di laporan, kode, dan aplikasi konsisten

## Untuk UAS (semua kategori)

- [ ] Perbaiki penyimpanan embedding. Berkas `emb_blair.npy` dan `emb_roberta.npy` di Drive berukuran 0 byte
      karena ditulis lewat memmap. Hasil Video_Games tetap sah, tetapi tahap 05–06 atau kategori lain tidak bisa
      dijalankan dari Drive tanpa ekstraksi ulang (sekitar 3 jam per encoder).
- [ ] Jalankan pipeline untuk kategori lain
- [ ] Notebook 09 (fine-tuning encoder) dan 10 (validasi label manusia) belum pernah dijalankan
