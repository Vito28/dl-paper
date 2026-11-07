# TODO

Diperbarui 7 November 2026 (setelah audit format laporan). Pembagian pekerjaan lengkap ada di `laporan/PEMBAGIAN_TUGAS.md`.

## Aplikasi Gradio (`app/`)

- [x] Antarmuka, langkah inferensi, dan berkas turunan otomatis (`tools/build_app.py`)
- [x] Uji kesetaraan dengan pipeline pada data smoke (`python -m tests.app_smoke`): selisih fitur 0, embedding 0,
      skor < 1e-8
- [x] Salin bobot model U dari Drive `outputs/Video_Games/runs/U_E3_T1_s42/model.pt` ke `app/artefak/model_U.pt`
      (dimuat strict, 214.657 parameter)
- [x] Uji aplikasi secara lokal dengan encoder BLaIR asli dan bobot di atas (5 ulasan contoh sekitar 1–2 detik,
      20 ulasan sekitar 5 detik di CPU laptop 8 thread; urutan masuk akal)
- [x] Buat Hugging Face Space (SDK Gradio, ZeroGPU, publik):
      https://huggingface.co/spaces/Nathjsn/pemeringkatan-ulasan-helpful
- [x] Isi LAPORAN.md bagian 7d: tautan Space dan waktu inferensi di Space
- [x] Pilihan contoh produk, kolom helpful votes asli, dan NDCG@10 terhadap suara asli (sudah di Space)
- [x] Contoh produk data uji asli (3 produk, 11/12/36 ulasan) dari `tools/ekspor_contoh_produk_uji.py`. Skor aplikasi
      sama dengan skor tersimpan (selisih ≤ 0,0014, urutan identik; `python -m tests.app_contoh_asli`). Satu produk
      terpilih dikecualikan karena isi ulasannya tidak pantas untuk demo publik (alasan dicatat di berkas JSON).
- [ ] Tangkapan layar aplikasi untuk LAPORAN.md bagian 7d (`laporan/gambar/aplikasi_gradio.png`)
- [ ] Jika `app/` berubah, unggah ulang ke Space: `hf upload Nathjsn/pemeringkatan-ulasan-helpful app . --repo-type space --exclude "__pycache__/*" --exclude "**/__pycache__/*"`

## Laporan (`laporan/LAPORAN.md`)

- [x] Isi Bagian A 1–9 dari hasil run dan `bahan_laporan.ipynb`
- [x] Gambar resolusi 300 dpi di `laporan/gambar/`
- [x] Audit terhadap `Format Laporan Tugas Pembelajaran Mendalam.pdf`: label cover, Daftar Isi/Gambar/Tabel, judul
      bagian 6, semua tabel berjudul, padanan metrik (6a), fitur unik 1 diganti pelatihan berpasangan RankNet, alasan
      U tetap model utama walaupun B5 lebih baik (5d), cuplikan kode pasangan dan inferensi aplikasi (8a)
- [x] Grafik dari tabel hasil digambar ulang dengan koma desimal dan label Indonesia (`python tools/gambar_laporan.py`)
- [x] Subbab 6c: `notebooks/00c_kurva_latih.ipynb` dijalankan di Colab. Hasil di `notebooks/FINISHED RUN/kurva_latih/`,
      grafik digambar ulang ke `laporan/gambar/kurva_latih_validasi.png`, angka masuk ke 6c dan 6e
- [ ] Cover (kelompok)
- [ ] Tabel Pembagian Tugas (kelompok, bahan di `laporan/PEMBAGIAN_TUGAS.md`)
- [ ] Daftar pustaka: tambahkan RoBERTa, Efron & Tibshirani (bootstrap), dan Holm ke Zotero (sedang dikerjakan)
- [ ] Ekspor ke satu PDF dengan urutan Cover, Bagian Awal, Bagian A, Bagian B:
      `python tools/build_pdf.py laporan/LAPORAN.md laporan/LAPORAN.pdf --final` (gagal selama masih ada ⟦…⟧)

## Naskah jurnal

- [ ] Masukkan koreksi Bab I–III ke Word. Catatannya ada di
      `laporan/arsip/2026-11-07_sebelum_run/catatan/koreksi/`

## Repo dan pengumpulan

- [ ] Jadikan repo GitHub publik, karena tautan di Bagian B harus bisa dibuka tanpa meminta akses. Sebelumnya,
      putuskan apakah riwayat git perlu dibersihkan: commit `86bf655` memuat `tmp/uts-review/report-text.txt` dengan
      nama dan NIM anggota. Berkasnya sudah dihapus dari repo, tetapi masih ada di riwayat.
- [x] Hapus `tmp/uts-review/` dan format UTS dari `documents/` (format yang berlaku adalah format Tugas di
      `laporan/referensi/pedoman/`)
- [ ] Periksa bahwa angka di laporan, kode, dan aplikasi konsisten

## Untuk UAS (semua kategori)

- [ ] Perbaiki penyimpanan embedding. Berkas `emb_blair.npy` dan `emb_roberta.npy` di Drive berukuran 0 byte
      karena ditulis lewat memmap. Hasil Video_Games tetap sah, tetapi tahap 05–06 atau kategori lain tidak bisa
      dijalankan dari Drive tanpa ekstraksi ulang (sekitar 3 jam per encoder).
- [ ] Jalankan pipeline untuk kategori lain
- [ ] Notebook 09 (fine-tuning encoder) dan 10 (validasi label manusia) belum pernah dijalankan
