# Protokol Eksperimen untuk Bab IV

Dokumen ini menjelaskan langkah eksperimen yang diimplementasikan di folder `notebooks/` dan `src/hr/`. Isinya mengikuti
**Bab III versi revisi** (branch `documents`, berkas `... - Revisi.docx`), bukan `agent.md` versi lama. Perbedaan keduanya
dijelaskan di Bagian 4.

---

## 1. Urutan notebook

Jalankan berurutan. Setiap notebook membaca keluaran notebook sebelumnya dari `outputs/<kategori>/`.

| No | Notebook | Bab III | Isi | Butuh GPU |
|---|---|---|---|---|
| 01 | `01_pengumpulan_data` | 3.2 | Unduh *User Reviews*, catat URL, ukuran, jumlah baris, dan SHA-256 | Tidak |
| 02 | `02_preprocessing_eda` | 3.2, 3.3 | Validasi tipe, cek satuan `timestamp`, data kosong, normalisasi teks, duplikat, fitur panjang, usia. Statistik deskriptif dan grafik EDA | Tidak |
| 03 | `03_split_dan_target` | 3.4, 3.5, 2.9 | *Product-disjoint split*, cek kebocoran, subset bertingkat E1–E5, standardisasi. Model Negative Binomial usia (RM3), target T1/T3 *out-of-fold*, tingkat relevansi 0–4 | Disarankan |
| 04 | `04_ekstraksi_embedding` | 3.6 | Embedding [CLS] + L2 dari BLaIR dan RoBERTa-base, disimpan float16 | **Ya** |
| 05 | `05_training_baseline_dan_model_utama` | 3.7, Tabel 3.5 | Visualisasi *loss function*, statistik pasangan, B0, B1 (penalaan C), penalaan *learning rate* × *dropout* untuk U, training akhir U, B2–B5 dengan beberapa *seed* | **Ya** |
| 06 | `06_ablasi_skala_target` | Tabel 3.5 | A1–A3, E1–E5, T2 (penalaan Δa), T3 | **Ya** |
| 07 | `07_evaluasi_data_uji` | 3.9, 3.10 | **Satu kali.** Cakupan evaluasi, tabel RM1–RM3 dengan IK 95% *bootstrap*, selisih berpasangan + koreksi Holm, per kelompok usia, ukuran produk, panjang ulasan, analisis kesalahan | Tidak |
| 08 | `08_visualisasi` | — | Grafik Bab IV (300 dpi): kurva loss, NDCG@10 per epoch, baseline, ablasi, skala, usia | Tidak |
| 09 | `09_finetuning_encoder_opsional` | — | *Fine-tuning* BLaIR dan RoBERTa-base dengan RankNet, dibandingkan dengan versi beku pada E1 | **Ya**, ≥16 GB |
| 10 | `10_validasi_label_manusia_opsional` | — | Lembar anotasi buta, kesepakatan antarpenilai (kappa, alpha), perbandingan T1/T3/model dengan penilaian manusia | Tidak |

Notebook 09 dan 10 adalah arah pengembangan dari `kritik-reviewer.md` (branch `documents`), belum ada di Bab III.

## 2. Keluaran untuk Bab IV

Semua keluaran ada di `outputs/<kategori>/`.

| Bab IV | Berkas |
|---|---|
| Deskripsi data dan preprocessing | `preprocess_report.json`, `describe.json`, `tables/eda_usia_vs_vote.csv`, `tables/eda_token.json`, `figures/eda_distribusi.png` |
| Pembagian data dan skala | `split_report.json`, `tables/split_dan_skala.csv`, `tables/sebaran_tingkat_relevansi.csv` |
| Pasangan pelatihan | `tables/pasangan.csv` |
| Penalaan hiperparameter | `tables/penalaan_U.csv`, `best_hparams.json` |
| Proses training | `runs/*/history.csv`, `figures/training_loss_ndcg.png`, `figures/loss_function.png` |
| RM1 baseline | `tables/uji_baseline.csv`, `tables/uji_selisih_berpasangan.csv`, `tables/uji_b4_mae_rmse.json`, `figures/uji_baseline.png` |
| Cakupan evaluasi | `tables/uji_cakupan.json` |
| RM2 ablasi dan skala | `tables/uji_ablasi.csv`, `tables/uji_skala.csv`, `figures/uji_ablasi_skala.png` |
| RM3 usia | `age_model.json` (uji LR, *deviance*), `tables/age_pemilihan_basis.csv`, `tables/age_kurva.csv`, `tables/uji_target.csv`, `tables/uji_per_kelompok_usia.csv`, `figures/age_kurva.png`, `figures/usia.png` |
| Analisis kesalahan | `tables/uji_per_ukuran_produk.csv`, `tables/uji_per_panjang_ulasan.csv`, `tables/uji_produk_terburuk.csv` |
| Opsional | `tables/uji_finetuning.csv`, `tables/manusia_*.csv/json` |

## 3. Aturan yang dikunci di kode

- **Kebocoran.**
  - `helpful_vote`, usia, dan target tidak bisa masuk ke matriks fitur (`FORBIDDEN_FEATURES` diperiksa dengan `assert`).
  - Standardisasi, TF-IDF, SVD, model usia, dan ambang relevansi hanya dihitung dari data latih.
  - T3 untuk data latih dihitung *out-of-fold*, dengan fold dikelompokkan per produk.
- **Data uji** hanya dievaluasi di notebook 07. Notebook 05–06 menyimpan skor uji tetapi tidak menghitung metriknya.
- **Ambang MAP**: relevan jika g ≥ 2, ditetapkan sebelum eksperimen.
- **Skor kembar** diurutkan berdasarkan hash identitas baris, bukan berdasarkan label.
- **Penalaan** hanya memakai NDCG@10 validasi. Hiperparameter terbaik U dipakai untuk semua model MLP agar perbandingannya adil.
- **Seed**: hasil adalah rata-rata metrik per produk dari semua *seed*, lalu di-*bootstrap* per produk (1.000 kali).
- **Uji perbandingan**: dua perbandingan utama adalah U vs B5 dan U vs B1. Semua p-value dikoreksi Holm.

## 4. Apakah `agent.md` sudah lengkap? Belum.

| No | Kekurangan di `agent.md` | Penanganan |
|---|---|---|
| 1 | Kode *baseline* berbeda dengan Bab III revisi. Di `agent.md`, B4 = BLaIR + MLP dan B5 = BLaIR + fitur. Di Bab III, B0–B5 dan U punya arti lain | Kode mengikuti Bab III (`src/hr/config.py`, `EXPERIMENTS`) |
| 2 | Tidak ada B0 (panjang ulasan), B4 *pointwise*, dan B5 RoBERTa-base | Ditambahkan |
| 3 | Ambang MAP dan batas relevansi "dipilih dengan validation set". Ini mengubah definisi metrik berdasarkan kinerja | Ambang tetap g ≥ 2. Kuantil hanya dari data latih |
| 4 | Tidak ada protokol penalaan, jumlah *seed*, *bootstrap*, uji berpasangan, koreksi perbandingan berganda, maupun pelaporan cakupan produk yang terevaluasi | Ditambahkan (notebook 05 dan 07) |
| 5 | Tidak ada pemetaan langkah ke tabel dan gambar Bab IV, atau perekaman kurva loss | Bagian 2, `history.csv`, dan notebook 08 |
| 6 | Rencana analisis sensitivitas tumpang tindih data BLaIR | Tidak diimplementasikan karena tidak bisa dijalankan (lihat Bab III 3.6 revisi) |
| 7 | Eksperimen 4 varian keempat (target terkoreksi + pembobotan pasangan lintas usia), penyeimbangan kelompok usia dalam *mini-batch*, dan *oracle model* dengan usia | **Belum diimplementasikan** karena tidak ada di Bab III revisi. Bisa ditambahkan jika kelompok memutuskan memakainya |
| 8 | Tidak ada *fine-tuning* dan validasi label manusia | Notebook 09 dan 10 (opsional) |

## 5. Hal di kode yang perlu diselaraskan dengan Bab III

Keputusan berikut diambil saat implementasi dan **belum tertulis** di naskah. Sebaiknya didiskusikan lalu dimasukkan ke Bab III.

1. **B1, B2, dan B3 ikut memakai 5 fitur terstruktur.** Tujuannya agar selisih dengan U hanya berasal dari representasi atau model. Tabel 3.5 saat ini hanya menulis "TF-IDF dengan model linear" dan sejenisnya.
2. **Target perbandingan utama = T1** (`main_target`). Ruang Lingkup butir 3 masih menyebut target terkoreksi usia sebagai "target utama", padahal setelah revisi tahap 3, T3 hanya dibandingkan dan tidak dianggap lebih benar.
3. **Skala utama = E3** (`main_scale`) untuk *baseline*, ablasi, dan strategi target. Bab III hanya menyebut E3 untuk *grid search*.
4. **Batas ukuran data evaluasi**: validasi dan uji masing-masing dibatasi sekitar 200.000 ulasan, dengan produk diambil utuh secara acak (`max_eval_reviews`).
5. **Batas 200 ulasan per produk di data latih** (`max_train_reviews_per_product`) agar produk sangat besar tidak mendominasi.
6. **Ambang tingkat relevansi T3** dipilih sebagai kuantil T3 pada data latih sehingga proporsi setiap tingkat sama dengan T1.
7. **Model Negative Binomial** diestimasi pada data latih skala terbesar (E5). Efek produk adalah parameter tetap dengan regularisasi L2 kecil. Kovariatnya rating, `verified_purchase`, dan log panjang ulasan.
8. **Kelompok usia** baru, menengah, dan lama memakai tertil usia di data latih.

## 6. Cara menjalankan

1. Atur `notebooks/settings.py`. Yang wajib diputuskan kelompok adalah **kategori** dan **`run_priority`** (lihat usulan prioritas di `kritik-reviewer.md`).
2. Di Google Colab, jalankan sel Colab di awal setiap notebook dan simpan `HR_ROOT` di Google Drive.
3. Jalankan notebook 01 → 08. Notebook 09 dan 10 opsional.

**Uji cepat sebelum memakai data asli** (tanpa GPU, sekitar 2 menit):
```
pip install -r requirements.txt
python -m tests.smoke_test                       # uji modul dengan data sintetis
python -m tests.smoke_test --hf                  # + embedding dan fine-tuning dengan model mini
python tests/run_notebooks_smoke.py notebooks    # jalankan ke-10 notebook dengan data sintetis (HR_SMOKE=1)
```
Mode uji cepat menulis ke folder `smoke/` dan hasilnya tidak bermakna secara ilmiah.

**Perkiraan biaya komputasi** untuk data asli belum diukur, karena kode baru diuji dengan data sintetis. Bagian terberat adalah:
- Notebook 04: dua encoder × sekitar 1,4 juta ulasan pada 512 token.
- Notebook 06: skala E5 dengan beberapa *seed*.
- Notebook 09: *fine-tuning*.

Notebook 04 mencetak kecepatan ekstraksi (ulasan per detik) sehingga sisa waktunya bisa diperkirakan setelah beberapa menit. Ekstraksi bisa dilanjutkan jika sesi Colab terputus.
