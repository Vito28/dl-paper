# Koreksi Naskah Revisi · Abstrak, Bab I, dan Bab II

Daftar koreksi untuk `Review Helpfulness Ranking ... - Revisi.docx` versi commit `c72154e` ("revisi").
Berkas Word **tidak diubah**. Salin teks koreksi ke Word secara manual.

Aturan naskah yang dipakai (lihat `revisi-1-2-3.md`):
- Badan teks Bab I–III tidak memakai titik dua (:) atau titik koma (;).
- Penjelasan persamaan memakai kata "dengan" (huruf kecil, tanpa titik dua), lalu satu baris per simbol
  dengan format `simbol = arti`.

Kolom **Teks sekarang** dikutip dari dokumen. Simbol matematika ditulis ulang dengan Unicode. Ketik
bagian persamaan sebagai objek persamaan Word, bukan teks biasa.

---

## A. Kesalahan isi

### A1. Rumusan Masalah (1.2), RM3. Tata bahasa membalik makna

**Teks sekarang**
> Seberapa kuat hubungan usia ulasan dengan jumlah helpful votes, dan bagaimana pengaruh kualitas
> pemeringkatan setelah penyesuaian target secara aproksimatif terhadap usia ulasan jika dievaluasi
> menggunakan acuan yang sama?

**Teks koreksi**
> Seberapa kuat hubungan usia ulasan dengan jumlah helpful votes, dan bagaimana perubahan kualitas
> pemeringkatan ketika target disesuaikan secara aproksimatif terhadap usia ulasan, jika dievaluasi
> menggunakan acuan yang sama?

**Alasan.** "Pengaruh kualitas pemeringkatan" berarti kualitas pemeringkatan yang memengaruhi sesuatu.
Yang diteliti adalah kebalikannya, yaitu pengaruh penyesuaian target terhadap kualitas pemeringkatan.

### A2. Target Terkoreksi Usia (2.9.3). Prosedur pemusatan tidak sesuai dengan kode

**Teks sekarang**
> Pada setiap fold, fungsi usia dan nilai pemusatannya dihitung dari bagian data pelatihan fold tersebut.

**Teks koreksi**
> Pada setiap fold, fungsi usia diestimasi dari bagian data pelatihan fold tersebut. Nilai pemusatan
> f̄ dihitung satu kali sebagai rata-rata komponen usia out-of-fold pada seluruh data latih, lalu dipakai
> untuk data latih, validasi, dan uji.

Baris simbol di bawah persamaan (2.18) juga disesuaikan.

| Teks sekarang | Teks koreksi |
|---|---|
| `f̄ = rata-rata f pada data latih` | `f̄ = rata-rata komponen usia out-of-fold pada data latih` |

**Alasan.** Kode (`notebooks/03`, `f_bar = f_oof.mean()`) memakai satu nilai f̄ dari seluruh komponen
usia out-of-fold, seperti yang sudah ditulis di daftar simbol (2.18). Kalimat Elvina menyebut nilai
pemusatan per fold, yang bertentangan dengan daftar simbol tersebut dan dengan hasil eksperimen
Video_Games yang sudah selesai. Dampaknya pada urutan dalam produk dapat diabaikan, tetapi naskah dan
kode harus sama.

### A3. Model Hitung (2.9.2). Simbol didefinisikan dua kali dan saling bertentangan

Masalahnya:
- μᵢ dan κ didefinisikan di bawah (2.16) **dan** lagi di bawah (2.17).
- κ > 0 di (2.16), tetapi di (2.17) "Poisson adalah kasus khusus saat κ = 0".
- Ada teks penjelasan yang diketik di dalam objek persamaan ("E(Vᵢ∣Xᵢ): rata-rata kondisional ...",
  dan ada titik dua di dalamnya).
- Ada kode LaTeX mentah `\(\kappa\)` di badan teks.

**Teks koreksi (seluruh blok setelah persamaan 2.16)**

> Var(Vᵢ ∣ Xᵢ) = μᵢ + κμᵢ²  (2.16)
>
> dengan
> - Vᵢ = jumlah helpful votes ulasan ke-i
> - Xᵢ = informasi usia, produk, dan kovariat ulasan ke-i yang digunakan dalam model hitung
> - μᵢ = E(Vᵢ ∣ Xᵢ), yaitu rata-rata kondisional jumlah helpful votes ulasan ke-i
> - κ = parameter dispersi, dengan κ > 0
>
> Parameterisasi ini mendekati regresi Poisson ketika κ mendekati nol. Kesesuaian Negative Binomial
> tetap perlu diperiksa melalui diagnostik model, termasuk kecocokannya terhadap proporsi nilai nol.

Ketik "κ" di kalimat terakhir sebagai simbol atau persamaan sebaris, bukan `\(\kappa\)`. Pada baris
μᵢ, hanya "μᵢ" dan "E(Vᵢ ∣ Xᵢ)" yang berada di objek persamaan. Kata "yaitu rata-rata ..." ditulis
sebagai teks biasa.

**Teks koreksi (daftar simbol setelah persamaan 2.17)**. Hapus baris κ karena κ tidak muncul di
(2.17) dan sudah didefinisikan di (2.16).

> dengan
> - μᵢ = rata-rata kondisional jumlah helpful votes ulasan ke-i, seperti pada persamaan (2.16)
> - γₚ₍ᵢ₎ = efek produk induk p(i) tempat ulasan ke-i berada
> - aᵢ = usia ulasan ke-i dalam hari
> - f(·) = fungsi usia yang bisa berbentuk linear atau spline
> - cᵢ, β = vektor kovariat nonteks (rating, status pembelian terverifikasi, dan panjang ulasan) beserta koefisiennya

### A4. Regularisasi dan Optimisasi (2.6.2). Simbol ã tidak didefinisikan

Persamaan (2.8) sekarang ã⁽ˡ⁾ = r⁽ˡ⁾ ⊙ a⁽ˡ⁾ / q, dengan r_j⁽ˡ⁾ ∼ Bernoulli(q). Daftar simbolnya belum
menjelaskan ã⁽ˡ⁾ dan a⁽ˡ⁾.

**Teks koreksi (daftar simbol setelah persamaan 2.8)**

> dengan
> - ã⁽ˡ⁾ = aktivasi lapisan ke-l setelah dropout
> - a⁽ˡ⁾ = aktivasi lapisan ke-l sebelum dropout
> - r⁽ˡ⁾ = vektor masker biner pada lapisan ke-l dengan elemen r_j⁽ˡ⁾
> - q = peluang suatu unit tetap aktif, sehingga laju dropout adalah 1 − q
> - ⊙ = perkalian elemen demi elemen
>
> Pembagian dengan q mempertahankan nilai harapan aktivasi selama pelatihan. Pada inferensi, dropout
> dinonaktifkan tanpa penskalaan tambahan.

Kalimat terakhir saat ini berada di paragraf yang berisi objek persamaan. Pastikan kalimat itu teks
biasa, dan hanya "q" yang berupa persamaan sebaris.

### A5. Abstrak. Tidak sesuai dengan RM1 yang baru

RM1 sudah diubah menjadi "... dan RoBERTa-base?", tetapi abstrak masih memakai frasa lama.

| Bagian | Teks sekarang | Teks koreksi |
|---|---|---|
| Abstrak | ... model linear, dan RoBERTa-base tanpa pelatihan domain, serta diuji ... | ... model linear, dan RoBERTa-base, serta diuji ... |
| Abstract | ... review-length, TF-IDF, linear, and plain RoBERTa-base baselines ... | ... review-length, TF-IDF, linear, and RoBERTa-base baselines ... |

---

## B. Pelanggaran aturan titik dua dan titik koma

### B1. "Dengan:" menjadi "dengan" (23 tempat)

Elvina mengganti "dengan" menjadi "Dengan:" di bawah persamaan. Kembalikan ke **"dengan"** (huruf kecil,
tanpa titik dua) di semua tempat berikut.

| Bab | Di bawah persamaan | Subbab |
|---|---|---|
| II | (2.1) | TF-IDF |
| II | (2.2) | Embedding Kontekstual Berbasis Transformer |
| II | (2.4) | BLaIR dan Checkpoint BLaIR-RoBERTa-Base |
| II | (2.5), (2.7) | Arsitektur dan Propagasi Maju |
| II | (2.8), (2.11) | Regularisasi dan Optimisasi |
| II | (2.14) | Learning to Rank dan RankNet |
| II | (2.15) | Target Mentah |
| II | (2.16), (2.17) | Model Hitung untuk Hubungan Usia dan Helpful Votes |
| II | (2.18) | Target Terkoreksi Usia |
| II | (2.20), (2.21), (2.23) | Metrik Evaluasi Pemeringkatan |
| III | (3.1), (3.2) | Preprocessing dan Rekayasa Fitur |
| III | (3.3) | Pembentukan Target Helpfulness |
| III | (3.4), (3.5), (3.6) | Feature Fusion dan Perancangan MLP |
| III | (3.7) | Pembentukan Ranking |
| III | (3.8) | Rancangan Eksperimen dan Evaluasi |

Daftar simbol di bawahnya juga diberi indentasi ulang dengan campuran spasi dan tab yang berbeda-beda.
Samakan semuanya (satu tab sebelum dan sesudah tanda "=").

### B2. Tujuan (1.3), butir 3. Titik dua

**Teks sekarang**
> ... lalu membandingkan tiga strategi pelatihan: penggunaan target mentah, pembentukan pasangan ulasan
> dengan usia berdekatan (age-matched pairs), dan penggunaan target yang disesuaikan secara aproksimatif
> terhadap usia ulasan.

**Teks koreksi**
> ... lalu membandingkan tiga strategi pelatihan, yaitu penggunaan target mentah, pembentukan pasangan
> ulasan dengan usia berdekatan (age-matched pairs), dan penggunaan target yang disesuaikan secara
> aproksimatif terhadap usia ulasan.

### B3. Dataset Amazon Reviews 2023 (2.8). Titik koma

**Teks sekarang**
> Angka jumlah ulasan dan item tersebut merupakan ukuran keseluruhan dataset; ukuran subset yang digunakan
> dalam eksperimen dilaporkan secara terpisah.

**Teks koreksi**
> Angka jumlah ulasan dan item tersebut merupakan ukuran keseluruhan dataset, sedangkan ukuran subset yang
> digunakan dalam eksperimen dilaporkan secara terpisah.

---

## C. Perbaikan kecil

### C1. Learning to Rank dan RankNet (2.7). Kalimat diawali "Sedangkan" dan spasi ganda

**Teks sekarang**
> Dalam penelitian ini, pasangan disusun sehingga yᵢ > yⱼ. Sedangkan pasangan dengan target yang sama
> tidak digunakan. Dengan  Pᵢⱼ = 1, persamaan (2.13) disederhanakan menjadi persamaan (2.14).

**Teks koreksi**
> Dalam penelitian ini, pasangan disusun sehingga yᵢ > yⱼ, dan pasangan dengan target yang sama tidak
> digunakan. Dengan P̄ᵢⱼ = 1, persamaan (2.13) disederhanakan menjadi persamaan (2.14).

Pakai simbol target pasangan yang sama dengan persamaan (2.13) di dokumen (P̄ᵢⱼ atau Pᵢⱼ).

### C2. "CheckPoint" menjadi "checkpoint"

| Subbab | Teks sekarang | Teks koreksi |
|---|---|---|
| Latar Belakang (1.1) | ... perbandingan kedua CheckPoint digunakan ... | ... perbandingan kedua checkpoint digunakan ... |
| BLaIR dan Checkpoint BLaIR-RoBERTa-Base | Menurut dokumentasi CheckPoint, embedding diambil ... yaitu token [CLS] yang pada tokenizer RoBERTa ditulis sebagai `<s>` pada RoBERTa, kemudian ... | Menurut dokumentasi checkpoint, embedding diambil ... yaitu token [CLS], yang pada tokenizer RoBERTa ditulis sebagai `<s>`, kemudian ... |

Pada kalimat kedua, "pada RoBERTa" juga muncul dua kali.

### C3. Spasi ganda

| Subbab | Teks sekarang | Teks koreksi |
|---|---|---|
| Prediksi dan Pemeringkatan Helpfulness Ulasan | ... MAP serta NDCG [14].␣␣Penelitian ini ... | ... MAP serta NDCG [14]. Penelitian ini ... |
| Dataset Amazon Reviews 2023 (2.8) | ... memuat atribut␣␣rating, title, ... | ... memuat atribut rating, title, ... |
| Learning to Rank dan RankNet (2.7) | Dengan␣␣Pᵢⱼ = 1 | sudah tercakup di C1 |

### C4. Tata letak (periksa di Word)

- Pada persamaan (2.1)–(2.5) dan (2.16), tab sebelum nomor persamaan berubah menjadi spasi, sehingga
  nomor persamaan kemungkinan tidak rata kanan. Kembalikan ke tab seperti persamaan lain.
- Persamaan (2.1) memakai "×" sedangkan yang lain memakai "·". Pilih satu dan samakan.
- Daftar isi kemungkinan belum diperbarui (dokumen bertambah dari sekitar 37 ke 43 halaman). Klik kanan
  daftar isi lalu *Update Field → Update entire table*.
