# Penyesuaian Bab III dengan Kode dan Hasil Eksperimen

Bab III tidak diubah isinya oleh revisi `c72154e`. Bagian berikut sudah tertulis di Bab III sebelumnya,
tetapi berbeda dengan kode yang menghasilkan eksperimen Video_Games. Perbedaannya ditemukan dan diperbaiki
di kode saat pemeriksaan hasil run (lihat `EXPERIMENTS.md` bagian 5 butir 9–11). Berkas Word **tidak
diubah**. Salin teks koreksi ke Word secara manual.

Semua teks koreksi mengikuti aturan naskah, yaitu tanpa titik dua atau titik koma di badan teks dan
dengan format "dengan" + `simbol = arti`.

---

## 1. Pembentukan Target Helpfulness (3.5). Deviance tidak dapat dipakai untuk membandingkan model

**Teks sekarang**
> Model hitung pada persamaan (2.17) diestimasi dengan Negative Binomial. Bentuk fungsi usianya (linear atau
> spline) dipilih berdasarkan deviance pada data validasi. Hasilnya dilaporkan dalam bentuk kurva usia dengan
> interval kepercayaan 95%, perubahan rata-rata suara saat usia bertambah, dan tambahan deviance explained
> dibandingkan model tanpa komponen usia. Hasil ini menjawab bagian pertama rumusan masalah ketiga.

**Teks koreksi**
> Model hitung pada persamaan (2.17) diestimasi dengan Negative Binomial. Bentuk fungsi usianya (linear atau
> spline) dipilih berdasarkan log-likelihood terbesar pada data validasi. Deviance tidak dipakai untuk
> membandingkan model karena nilainya bergantung pada parameter dispersi κ, sedangkan setiap model
> mengestimasi κ masing-masing. Hasilnya dilaporkan dalam bentuk kurva usia dengan interval kepercayaan 95%
> dari bootstrap pada tingkat produk, perubahan rata-rata suara saat usia bertambah, uji rasio likelihood
> terhadap model tanpa komponen usia, dan pseudo-R² McFadden terhadap model tanpa komponen usia. Hasil ini
> menjawab bagian pertama rumusan masalah ketiga.

**Alasan.** Pada run Video_Games, "tambahan deviance explained" bernilai −0,6%, seolah-olah usia
memperburuk model. Padahal uji rasio likelihood sangat kuat (LR = 59.764, df = 5, p ≈ 0). Penyebabnya,
deviance kedua model dihitung dengan κ yang berbeda. Ukuran yang benar, pseudo-R² McFadden
1 − LL_dengan usia / LL_tanpa usia, bernilai 0,029. Basis yang terpilih tetap sama (spline 4 knot) dengan
kedua kriteria.

Jika rumus pseudo-R² perlu ditulis sebagai persamaan, gunakan bentuk berikut.

> R²_McF = 1 − ℓ_usia / ℓ_tanpa usia  (3.x)
>
> dengan
> - ℓ_usia = log-likelihood model hitung dengan komponen usia
> - ℓ_tanpa usia = log-likelihood model hitung tanpa komponen usia

---

## 2. Tabel 3.6 Metrik dan Aturan Evaluasi, baris 6

| | Metrik | Peran | Aturan |
|---|---|---|---|
| **Sekarang** | Deviance Negative Binomial | Kecocokan model hitung usia | Dibandingkan dengan model tanpa komponen usia |
| **Koreksi** | Uji rasio likelihood dan pseudo-R² McFadden | Sumbangan komponen usia pada model hitung | Model dengan dan tanpa komponen usia dibandingkan melalui log-likelihood |

---

## 3. Tabel 3.5 Matriks Eksperimen Penelitian

### 3a. Baris A1–A4. Jelaskan bahwa A4 adalah model U

**Teks sekarang (kolom Konfigurasi)**
> Embedding saja, lalu ditambah rating, verified_purchase, dan seluruh fitur

**Teks koreksi (kolom Konfigurasi)**
> Embedding saja (A1), ditambah rating (A2), ditambah verified_purchase (A3), dan seluruh fitur (A4, sama
> dengan model U sehingga tidak dilatih ulang)

**Alasan.** Kode hanya melatih A1–A3. A4 adalah model U dan dilaporkan sebagai "A4 (= U)" di tabel
ablasi. Penamaan A1–A4 di bagian lain naskah tetap benar.

### 3b. Baris baru R0 (letakkan di atas B0)

| Kode | Konfigurasi | Tujuan Perbandingan | Menjawab |
|---|---|---|---|
| R0 | Urutan acak, dirata-rata atas 20 permutasi | Batas bawah kinerja tanpa informasi apa pun | RM1 |

**Alasan.** Pada produk dengan sedikit ulasan, NDCG@10 urutan acak pun sudah tinggi. Pada Video_Games,
R0 bernilai 0,499 secara keseluruhan dan 0,822 pada kuartil produk terkecil (median 2 ulasan). Tanpa R0,
angka model tidak dapat ditafsirkan. Contohnya, NDCG@10 model U yang tinggi pada produk kecil (0,881)
sebagian besar berasal dari kebetulan, sedangkan selisih terbesar terhadap R0 justru ada pada produk besar
(+0,38).

Tambahkan juga satu kalimat setelah Tabel 3.5.
> Urutan acak R0 tidak dilatih dan hanya dipakai sebagai batas bawah, termasuk pada analisis menurut ukuran
> produk.

---

## 4. Rancangan Eksperimen dan Evaluasi (3.9). Dua acuan relevansi belum dijelaskan

Notebook 07 mengevaluasi model T1, T2, dan T3 pada **dua** acuan relevansi, yaitu tingkat relevansi dari
target mentah dan dari target terkoreksi usia. Bab I dan Bab II yang baru sudah menyebut "acuan evaluasi
yang sama", tetapi Bab III belum menjelaskannya.

**Teks sekarang**
> Rancangan eksperimen ditunjukkan pada Tabel 3.5. Semua model dalam satu perbandingan memakai partisi,
> sampel, target, dan protokol evaluasi yang sama.

**Teks koreksi**
> Rancangan eksperimen ditunjukkan pada Tabel 3.5. Semua model dalam satu perbandingan memakai partisi,
> sampel, target, dan protokol evaluasi yang sama. Model dengan target T1, T2, dan T3 dievaluasi pada dua
> acuan relevansi yang sama, yaitu tingkat relevansi dari target mentah dan tingkat relevansi dari target
> terkoreksi usia. Hasil kedua acuan dilaporkan dalam tabel terpisah dan tidak dibandingkan langsung.

---

## 5. Aturan "model lebih baik" (3.9). Perlu keputusan kelompok

**Teks sekarang**
> Sebuah model baru dinyatakan lebih baik jika interval kepercayaan selisihnya tidak memuat nol dan arah
> perbedaannya sama di semua seed.

Kode memakai aturan yang berbeda. Sebuah model dinyatakan lebih baik jika interval kepercayaan 95%
selisihnya tidak memuat nol **dan** p-value setelah koreksi Holm di bawah 0,05. Koreksi Holm dipakai
karena U dibandingkan dengan enam baseline sekaligus. Kode **tidak** memeriksa arah selisih per seed,
karena skor per produk dirata-rata atas seed sebelum bootstrap.

**Pilihan A (disarankan). Sesuaikan naskah dengan kode**
> Sebuah model baru dinyatakan lebih baik jika interval kepercayaan 95% selisihnya tidak memuat nol dan
> p-value setelah koreksi Holm untuk perbandingan berganda kurang dari 0,05. Metrik per produk
> dirata-ratakan atas seed sebelum bootstrap.

**Pilihan B. Sesuaikan kode dengan naskah.** Kode ditambah pemeriksaan arah selisih untuk setiap seed.
Pemeriksaan ini dapat dijalankan dari prediksi yang sudah tersimpan tanpa melatih ulang model. Kalimat
tentang koreksi Holm tetap perlu ditambahkan, karena kode sudah memakainya.

Dengan Pilihan A, hasil Video_Games tetap seperti di `tables/uji_selisih_berpasangan.csv`. Pilihan B belum
diperiksa. Perbandingan yang paling mungkin berubah adalah U vs B2 (selisih +0,003, p = 0,046).
