# Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset

## A. Fokus Penelitian

Penelitian ini bertujuan mengembangkan model untuk mengurutkan ulasan produk berdasarkan tingkat *helpfulness* menggunakan representasi teks dari BLaIR-RoBERTa-Base dan Multi-Layer Perceptron (MLP).

Fokus utama penelitian adalah:

1. Mengukur kemampuan BLaIR-RoBERTa-Base dan MLP dalam menghasilkan ranking *helpfulness*.
2. Menguji generalisasi model pada produk yang tidak ditemukan selama training (*unseen products*).
3. Menganalisis pengaruh peningkatan ukuran training dari 100.000 hingga 1.000.000 review.
4. Mengukur hubungan usia review dengan jumlah *helpful votes* dan menggunakan hasilnya untuk membentuk target ranking yang terkoreksi paparan, tanpa menggunakan `review_age` sebagai fitur input model utama ketika inferensi.
5. Mengevaluasi kontribusi embedding BLaIR dan fitur terstruktur melalui perbandingan baseline dan eksperimen ablasi.

Model menghasilkan satu skor ranking untuk setiap review, kemudian mengurutkan review di dalam kelompok produk yang sama.

---

## B. Skema Penelitian

1. **Amazon Reviews 2023 — User Reviews**  
   `title`, `text`, `rating`, `verified_purchase`, `timestamp`, `helpful_vote`, `parent_asin`, dan `asin`.

2. **Data Preprocessing dan Pembentukan Target**  
   Pembersihan, deduplikasi, validasi timestamp, perhitungan usia review, target `log(1 + helpful_vote)`, product-disjoint split 80/10/10, serta sampling tanpa SMOTE.

3. **BLaIR-RoBERTa-Base**  
   `title + text` → tokenizer → encoder → pooling → embedding teks.

4. **Feature Fusion**  
   Embedding teks digabungkan dengan `rating`, `verified_purchase`, panjang review, jumlah kata, dan panjang judul. `review_age` tidak menjadi input model utama.

5. **Multi-Layer Perceptron**  
   Input → Dense 256 → ReLU → Dropout → Dense 64 → ReLU → satu ranking score. Training menggunakan *pairwise ranking loss* bergaya RankNet.

6. **Review Helpfulness Ranking**  
   Review diurutkan berdasarkan skor prediksi di dalam setiap `parent_asin`.

7. **Evaluasi dan Analisis**  
   NDCG@5, NDCG@10, Spearman, dan MAP; MAE/RMSE khusus baseline regresi. Analisis mencakup generalisasi produk baru, bias usia review, ablasi fitur, serta lima skala data training.

---

## C. Metodologi Penelitian

### Tahap 1 — Pengumpulan Dataset

Penelitian menggunakan **Amazon Reviews 2023**, dengan fokus pada data **User Reviews**.

Sumber dataset: <https://amazon-reviews-2023.github.io/>

Kolom yang digunakan meliputi:

| Kolom | Fungsi |
|---|---|
| `title` | Judul review |
| `text` | Isi review |
| `rating` | Rating yang diberikan reviewer |
| `verified_purchase` | Status pembelian terverifikasi |
| `timestamp` | Waktu publikasi review |
| `helpful_vote` | Jumlah helpful votes yang tercatat |
| `parent_asin` | Identitas produk induk dan unit ranking |
| `asin` | Identitas item atau varian produk |

Data **Item Metadata tidak diprioritaskan pada model dan eksperimen utama** karena penelitian masih berada pada tahap perencanaan. Metadata dapat ditambahkan kemudian untuk analisis kategori atau eksperimen lanjutan, tetapi ketidaktersediaannya tidak menghambat model utama.

### Tahap 2 — Preprocessing, Target, dan Pembagian Data

Preprocessing mencakup:

1. Memeriksa nilai kosong pada `title`, `text`, `timestamp`, `helpful_vote`, dan identitas produk.
2. Menghapus duplikasi berdasarkan identitas review atau kombinasi atribut yang relevan.
3. Membersihkan teks tanpa menghilangkan informasi semantik penting.
4. Memvalidasi tipe data dan rentang nilai `rating`, `verified_purchase`, dan `helpful_vote`.
5. Mengubah `timestamp` ke format waktu yang konsisten. Satuan timestamp harus diperiksa; contoh resmi Amazon Reviews 2023 menggunakan Unix timestamp dalam milidetik.
6. Menghitung `review_length`, `word_count`, dan `title_length`.
7. Menghitung `review_age` untuk pengendalian bias usia selama training dan analisis.
8. Membentuk target relevansi dari `helpful_vote`.
9. Membagi data berdasarkan kelompok produk.
10. Menyiapkan sampling training dan pasangan ranking tanpa SMOTE.

#### 2.1 Target helpfulness

Struktur standar Amazon Reviews 2023 menyediakan `helpful_vote`, tetapi tidak menyediakan `total_votes` yang dibutuhkan untuk menghitung *helpfulness ratio* secara valid. Oleh karena itu, target observasi awal (*raw target*) ditetapkan sebagai:

$$
y_i = \log(1 + v_i)
$$

dengan:

- \(y_i\) adalah target relevansi review ke-\(i\);
- \(v_i\) adalah nilai `helpful_vote` review ke-\(i\);
- \(\log\) adalah logaritma natural.

Transformasi logaritmik mengurangi dominasi review dengan jumlah vote sangat besar tanpa mengubah urutannya. Target ini merupakan proksi *helpfulness* yang teramati pada snapshot dataset, bukan ukuran sempurna atas kualitas intrinsik review. Target mentah digunakan sebagai baseline, sedangkan target utama model ranking yang dikendalikan terhadap paparan didefinisikan pada Bagian 2.2.

Review dengan `helpful_vote = 0` tetap dipertahankan sebagai target bernilai nol. Review tersebut dapat dipasangkan dengan review dari produk yang sama yang memiliki target lebih tinggi. Meskipun demikian, nilai nol tidak ditafsirkan sebagai bukti mutlak bahwa review tidak berguna, karena review mungkin belum memiliki cukup kesempatan untuk menerima vote.

`helpful_vote` dan target turunannya tidak boleh dimasukkan kembali sebagai fitur input model.

#### 2.2 Pengukuran dan pengendalian pengaruh usia review

Usia review dihitung sebagai:

$$
review\_age_i = T_{ref} - timestamp_i
$$

`T_ref` adalah waktu referensi snapshot atau waktu evaluasi yang ditetapkan secara konsisten dan tidak boleh mendahului waktu publikasi review.

Jumlah *helpful votes* bersifat kumulatif. Review lama biasanya memiliki kesempatan lebih panjang untuk menerima vote daripada review baru. Karena itu, penelitian tidak hanya mengelompokkan review berdasarkan usia, tetapi juga **mengukur besarnya hubungan antara `review_age` dan `helpful_vote`**. Istilah "pengaruh" pada bagian ini berarti asosiasi setelah mengendalikan perbedaan produk dan kovariat yang tersedia; tanpa eksperimen atau riwayat waktu pemberian vote, hasilnya tidak boleh diklaim sebagai efek kausal.

Karena model utama tidak menerima `review_age` ketika inferensi, model tidak dapat secara langsung mengetahui bahwa sebuah review baru atau lama. Sebagai gantinya, usia review diperlakukan sebagai variabel paparan/pengganggu (*exposure/confounding variable*) selama pembentukan target, penyusunan data training, dan evaluasi agar model lebih banyak mempelajari kualitas review daripada lamanya kesempatan memperoleh vote.

Analisis pengaruh usia dilakukan dengan protokol berikut:

1. Menggunakan `review_age_days` dan transformasi `log(1 + review_age_days)` karena hubungan usia dan vote kemungkinan tidak linear.
2. Menyajikan distribusi `helpful_vote`, proporsi vote nol, median/mean vote, dan korelasi Spearman terhadap usia, baik secara keseluruhan maupun per kelompok usia.
3. Mengestimasi model hitung Negative Binomial (atau Poisson bila tidak terjadi overdispersi) dengan bentuk umum:

$$
\log E[v_i] = \alpha_{p(i)} + f(\log(1 + age_i)) + \boldsymbol{\beta}^{\top}\mathbf{x}_i
$$

dengan \(\alpha_{p(i)}\) sebagai efek produk, \(f(\cdot)\) sebagai fungsi usia yang dapat berbentuk spline, dan \(\mathbf{x}_i\) sebagai kovariat nonteks seperti `rating`, `verified_purchase`, dan panjang review. Efek produk diperlukan agar hubungan usia tidak hanya mencerminkan perbedaan popularitas antarproduk.
4. Melaporkan koefisien/kurva usia beserta interval kepercayaan, perubahan vote yang diharapkan ketika usia bertambah, serta peningkatan *deviance explained* atau *pseudo-R²* ketika komponen usia ditambahkan.
5. Menentukan bentuk fungsi usia dan hyperparameter hanya dari training/validation. Test set digunakan sekali untuk mengukur generalisasi hasil analisis.

Hasil estimasi tersebut kemudian digunakan untuk membandingkan tiga strategi target/training:

1. **Target mentah:** \(y_i=\log(1+v_i)\), sebagai baseline.
2. **Age-matched pairs:** pasangan ranking diprioritaskan dari produk yang sama dan usia yang sama atau berdekatan.
3. **Target terkoreksi usia:** komponen paparan yang diprediksi oleh model usia dikurangi dari target mentah:

$$
y_i^{adj} = \log(1+v_i) - \widehat{f}(\log(1+age_i))
$$

Nilai \(\widehat{f}\) untuk data training harus dihasilkan secara *out-of-fold* agar target terkoreksi tidak mengalami kebocoran. Model usia untuk validation dan test hanya boleh dipasang pada training set. Target terkoreksi dapat bernilai negatif dan tetap dapat digunakan untuk menentukan arah pasangan RankNet. Bila NDCG dihitung terhadap target terkoreksi, target diubah menjadi tingkat relevansi nonnegatif berdasarkan batas kuantil yang dipelajari dari training set.

Selama training, kelompok usia juga diseimbangkan agar review lama tidak mendominasi mini-batch. Proporsi pasangan lintas usia dicatat, dan pembatasan atau pembobotannya dipilih melalui validation set. Performa dilaporkan secara keseluruhan dan terpisah untuk review baru, menengah, dan lama; batas kelompok usia ditentukan dari training/validation, bukan test set.

Model utama tetap hanya menerima teks dan fitur yang tersedia saat inferensi. Output utamanya adalah skor ranking *intrinsic helpfulness* yang telah dikurangi bias lama paparan. Untuk transparansi, hasil terhadap target mentah dan target terkoreksi usia harus sama-sama dilaporkan.

Perlu dibedakan antara dua tujuan prediksi:

- **Ranking kualitas intrinsik tanpa `review_age`:** dapat dilakukan menggunakan target terkoreksi usia; inilah tujuan utama penelitian.
- **Prediksi jumlah vote kumulatif pada waktu tertentu:** membutuhkan `review_age` atau horizon prediksi pada tahap kalibrasi, misalnya dengan menambahkan kembali komponen \(\widehat{f}(age)\). Tanpa informasi usia/horizon, jumlah vote kumulatif tidak dapat diprediksi secara terkalibrasi karena kesempatan paparan tidak diketahui.

Dataset tidak menyediakan riwayat waktu untuk setiap helpful vote. Karena itu, jumlah vote historis pada saat review pertama diterbitkan tidak dapat direkonstruksi secara pasti. Keterbatasan ini harus dinyatakan dalam laporan hasil.

#### 2.3 Product-disjoint split

Data dibagi berdasarkan `parent_asin`, bukan secara acak per baris:

- Training: 80% kelompok produk.
- Validation: 10% kelompok produk.
- Testing: 10% kelompok produk.

Proporsi tersebut merupakan konfigurasi awal. Jumlah review pada setiap split tidak harus tepat 80/10/10 karena pembagian dilakukan pada tingkat produk.

Produk pada validation dan test set tidak boleh muncul pada training. `asin` juga diperiksa untuk mencegah varian yang berhubungan tersebar pada split berbeda. Deduplikasi lintas split dilakukan sebelum eksperimen untuk mencegah kebocoran data.

Validation digunakan untuk tuning hyperparameter, pemilihan model, batas kelompok usia, threshold MAP, dan aturan pembentukan pasangan. Test set hanya digunakan untuk evaluasi akhir.

#### 2.4 Penanganan ketimpangan data

Penelitian tidak menggunakan SMOTE karena sampel sintetis pada embedding dan kelompok produk dapat menghasilkan pasangan ranking yang tidak alami.

Strategi yang digunakan adalah:

- mempertahankan distribusi asli pada validation dan test set;
- mengendalikan sampling pada training;
- memilih pasangan dengan target berbeda dari produk yang sama;
- membatasi jumlah pasangan dari satu produk agar produk besar tidak mendominasi;
- menjaga representasi review dengan target dan usia yang berbeda;
- mencatat distribusi target, produk, dan kelompok usia pada setiap split.

### Tahap 3 — Ekstraksi Embedding BLaIR-RoBERTa-Base

Judul dan isi review digabungkan menjadi input teks:

`Review title + review text → tokenizer → BLaIR-RoBERTa-Base → pooling → embedding`

Encoder BLaIR dibekukan pada eksperimen utama agar kebutuhan komputasi lebih rendah dan embedding dapat disimpan ke disk. Fine-tuning penuh dapat menjadi eksperimen lanjutan.

Dimensi embedding, panjang token maksimum, truncation, dan metode pooling harus mengikuti checkpoint BLaIR yang benar-benar digunakan dan dicatat untuk reproduktibilitas. Embedding tidak boleh memanfaatkan target, vote, umur review, atau informasi masa depan.

### Tahap 4 — Feature Fusion

Embedding teks digabungkan dengan fitur yang tersedia pada saat inferensi:

| Fitur | Penggunaan |
|---|---|
| BLaIR embedding | Representasi semantik judul dan isi review |
| `rating` | Rating yang diberikan reviewer |
| `verified_purchase` | Status pembelian terverifikasi |
| `review_length` | Jumlah karakter isi review |
| `word_count` | Jumlah kata isi review |
| `title_length` | Jumlah karakter judul |

Fitur numerik dinormalisasi menggunakan parameter yang hanya dipelajari dari training set. Fitur kategorikal dikodekan sesuai tipe datanya. Transformasi yang sama kemudian diterapkan pada validation dan test set.

Fitur yang tidak digunakan sebagai input adalah `helpful_vote`, target relevansi, total vote, proporsi helpfulness, `review_age`, dan atribut lain yang tidak tersedia atau tidak diizinkan ketika model digunakan.

### Tahap 5 — Training Multi-Layer Perceptron

Konfigurasi awal MLP adalah:

| Komponen | Konfigurasi |
|---|---|
| Input | BLaIR embedding + fitur terstruktur |
| Hidden layer 1 | 256 neuron |
| Aktivasi 1 | ReLU |
| Dropout | 0,2 |
| Hidden layer 2 | 64 neuron |
| Aktivasi 2 | ReLU |
| Output | Satu ranking score |
| Optimizer | Adam |
| Loss | Pairwise RankNet-style loss |

Untuk pasangan review \(i\) dan \(j\) dari produk yang sama dengan \(y_i > y_j\), model diarahkan agar:

$$
s_i > s_j
$$

Salah satu bentuk loss yang dapat digunakan adalah:

$$
\mathcal{L}_{ij} = \log\left(1 + \exp\left(-(s_i-s_j)\right)\right)
$$

Pasangan dengan target sama tidak digunakan sebagai pasangan preferensi. Pembentukan pasangan mempertimbangkan ukuran produk dan kelompok usia review sebagaimana ditetapkan pada Tahap 2. Seluruh hyperparameter dipilih berdasarkan validation set.

### Tahap 6 — Pembentukan Ranking Review

MLP menghasilkan satu skor untuk setiap review. Review kemudian dikelompokkan berdasarkan `parent_asin` dan diurutkan dari skor tertinggi ke terendah.

Ranking tidak dilakukan dengan mencampurkan review dari produk berbeda. Evaluasi utama dilakukan pada produk yang tidak pernah muncul selama training, sehingga mengukur kemampuan generalisasi model pada produk baru.

### Tahap 7 — Evaluasi Model

| Metrik | Penggunaan |
|---|---|
| NDCG@5 | Kualitas lima review teratas |
| NDCG@10 | Metrik utama kualitas sepuluh review teratas |
| Spearman | Korelasi urutan prediksi dan target per produk |
| MAP | Ranking menggunakan definisi relevansi biner |
| MAE/RMSE pada `log1p(vote)` | Prediksi jumlah vote oleh baseline regresi dan model terkalibrasi; bukan skor ranking mentah |
| Negative Binomial deviance | Kecocokan model hitung dan kontribusi komponen usia |

Ketentuan evaluasi:

1. Metrik ranking dihitung per produk, kemudian diagregasikan menggunakan macro-average agar produk besar tidak mendominasi.
2. Perbandingan model dengan target mentah menggunakan definisi relevansi mentah yang sama. Perbandingan model terkoreksi usia menggunakan tingkat relevansi terkoreksi yang sama. Nilai dari dua protokol target tersebut dilaporkan pada tabel terpisah dan tidak dibandingkan secara langsung.
3. Batas kuantil untuk relevansi terkoreksi dan threshold relevansi biner untuk MAP ditetapkan menggunakan training/validation, bukan test set.
4. Spearman hanya dihitung pada produk dengan jumlah review dan variasi target yang memadai.
5. MAE/RMSE tidak dihitung langsung dari skor ranking mentah MLP.
6. Produk dengan terlalu sedikit review, target konstan, atau tanpa pasangan relevan ditangani dengan aturan yang ditetapkan sebelum evaluasi.
7. Jumlah produk valid untuk setiap metrik harus dilaporkan.
8. Hasil dianalisis berdasarkan kelompok usia review dan jumlah review per produk.
9. Untuk mengukur manfaat informasi usia terhadap akurasi jumlah vote, MAE/RMSE pada `log1p(vote)` dibandingkan antara model tanpa usia, model terkalibrasi pada horizon/usia yang diketahui, dan *oracle model* dengan usia.
10. Analisis per kategori hanya dilakukan apabila Item Metadata ditambahkan pada tahap lanjutan.

---

## D. Rancangan Eksperimen

### Eksperimen 1 — Pengaruh Skala Training

| Eksperimen | Jumlah Review Training |
|---|---:|
| E1 | 100.000 |
| E2 | 250.000 |
| E3 | 500.000 |
| E4 | 750.000 |
| E5 | 1.000.000 |

Angka tersebut adalah jumlah review training, bukan jumlah keseluruhan dataset. Produk dialokasikan ke split terlebih dahulu, kemudian review dipilih dari training pool tanpa memindahkan produk ke validation atau test set.

Subset dibuat bertingkat (*nested sampling*) jika memungkinkan: seluruh sampel E1 menjadi bagian E2, seluruh sampel E2 menjadi bagian E3, dan seterusnya. Validation dan test set harus sama untuk seluruh skala.

### Eksperimen 2 — Perbandingan Baseline

| Model | Representasi | Metode |
|---|---|---|
| B1 | TF-IDF | Linear ranker |
| B2 | TF-IDF | MLP ranker |
| B3 | BLaIR embedding | Linear ranker |
| B4 | BLaIR embedding | MLP ranker |
| B5 | BLaIR embedding + fitur terstruktur | MLP ranker |

B4 adalah model utama berbasis teks, sedangkan B5 mengukur manfaat fitur terstruktur. Seluruh model menggunakan target, product-disjoint split, test set, dan protokol evaluasi yang sama.

Baseline regresi dapat ditambahkan secara terpisah untuk menghasilkan MAE dan RMSE. Baseline tersebut bukan pengganti baseline ranking.

### Eksperimen 3 — Feature Ablation

Eksperimen ablasi membandingkan:

1. BLaIR embedding saja.
2. Embedding + `rating`.
3. Embedding + `rating` + `verified_purchase`.
4. Embedding + seluruh fitur terstruktur yang tersedia saat inferensi.

`review_age` tidak dimasukkan dalam ablasi fitur produksi karena keputusan penelitian menetapkan bahwa model yang diluncurkan tidak bergantung pada umur review.

### Eksperimen 4 — Pengendalian Bias Usia Review

Eksperimen ini membandingkan:

1. Training dengan target mentah dan pembentukan pasangan biasa.
2. Training dengan target mentah, tetapi pasangan diprioritaskan pada usia sama atau berdekatan.
3. Training dengan target terkoreksi usia secara *out-of-fold*.
4. Training dengan target terkoreksi usia dan pembobotan pasangan lintas usia yang dipilih melalui validation set.

Semua varian menggunakan arsitektur dan fitur inferensi yang sama. Dengan demikian, perbedaan hasil mengukur dampak strategi pengendalian bias usia, bukan manfaat memberikan usia review kepada model.

Sebelum membandingkan model ranking, eksperimen melaporkan kurva hubungan usia-vote, interval kepercayaan, dan kontribusi tambahan usia terhadap *deviance explained* atau *pseudo-R²*. Hasil ranking kemudian dilaporkan untuk keseluruhan test set serta secara terpisah pada kelompok review baru, menengah, dan lama, menggunakan target mentah dan relevansi terkoreksi usia.

Sebagai analisis tambahan, sebuah *oracle/upper-bound model* yang menerima `review_age` dapat dilatih khusus untuk mengukur seberapa besar akurasi prediksi vote meningkat ketika usia diketahui. Model ini **bukan model produksi** dan tidak dibandingkan sebagai konfigurasi utama; selisih performanya menunjukkan informasi prediktif yang hilang ketika `review_age` tidak tersedia saat inferensi.

### Eksperimen 5 — Generalisasi ke Produk Baru

Evaluasi dilakukan pada produk yang tidak pernah muncul selama training. Analisis mencakup:

- NDCG@5 dan NDCG@10 per produk;
- Spearman dan MAP sesuai kriteria evaluasi;
- performa berdasarkan jumlah review per produk;
- performa berdasarkan kelompok usia review;
- perbandingan baseline, model utama, dan varian pengendalian usia.

---

## E. Pertanyaan Penelitian

1. Bagaimana kinerja kombinasi BLaIR-RoBERTa-Base dan MLP dalam melakukan review helpfulness ranking pada Amazon Reviews 2023?
2. Apakah embedding BLaIR meningkatkan kualitas ranking dibandingkan representasi TF-IDF?
3. Bagaimana kontribusi `rating`, `verified_purchase`, dan fitur panjang teks terhadap kualitas ranking?
4. Bagaimana peningkatan jumlah data training dari 100.000 hingga 1.000.000 review memengaruhi performa ranking?
5. Seberapa baik model melakukan generalisasi pada produk yang tidak pernah digunakan dalam training?
6. Seberapa kuat hubungan `review_age` dengan jumlah *helpful votes* setelah mengendalikan perbedaan produk dan kovariat yang tersedia?
7. Sejauh mana target terkoreksi usia dan strategi pembentukan pasangan mengurangi bias kesempatan memperoleh vote tanpa menjadikan `review_age` sebagai fitur model produksi?

---

## F. Kontribusi yang Diharapkan

1. Implementasi BLaIR-RoBERTa-Base sebagai representasi teks untuk review helpfulness ranking menggunakan MLP.
2. Evaluasi generalisasi berbasis product-disjoint split.
3. Perbandingan representasi TF-IDF dan BLaIR menggunakan baseline ranking yang konsisten.
4. Estimasi empiris hubungan usia review dengan jumlah *helpful votes* serta protokol target terkoreksi usia tanpa ketergantungan pada `review_age` ketika model utama digunakan.

Kontribusi tersebut masih berupa rancangan yang harus dibuktikan melalui eksperimen, bukan klaim bahwa model yang diusulkan telah mengungguli metode lain.

---

## G. Catatan Implementasi dan Reproduksibilitas

- Gunakan `parent_asin` sebagai unit pengelompokan produk dan ranking.
- Pastikan `parent_asin` tidak bocor antar-split dan periksa hubungan varian melalui `asin`.
- Tetapkan seed untuk pembagian data, sampling review, pembentukan pasangan, dan inisialisasi model.
- Simpan identitas produk pada setiap split serta daftar sampel pada E1–E5.
- Pelajari normalisasi dan encoding hanya dari training set.
- Lakukan tuning hanya pada validation set; jangan mengubah target, threshold, atau protokol berdasarkan test set.
- Simpan embedding BLaIR agar ekstraksi tidak perlu diulang untuk setiap eksperimen.
- Catat checkpoint, tokenizer, pooling, panjang token, hyperparameter, waktu ekstraksi, waktu training, RAM, VRAM, dan penyimpanan.
- Gunakan validation dan test set yang sama untuk seluruh eksperimen skala training.
- Laporkan distribusi helpful votes, proporsi target nol, usia review, jumlah review per produk, dan jumlah produk valid untuk setiap metrik.
- Dokumentasikan aturan pasangan lintas usia dan hasil analisis sensitivitasnya.
- Simpan model usia, pembagian fold, dan prediksi *out-of-fold* yang digunakan untuk membentuk target terkoreksi.
- Laporkan hasil baseline tanpa usia, model utama dengan target terkoreksi, dan *oracle model* yang menggunakan usia secara terpisah agar fungsi masing-masing tidak tertukar.
- Laporkan keterbatasan `helpful_vote` sebagai proksi kualitas serta tidak tersedianya histori waktu pemberian vote.

**Fokus akhir:** mengukur hubungan usia review dengan perolehan *helpful votes*, lalu menghasilkan sistem ranking kualitas review yang dapat diterapkan pada produk baru tanpa membutuhkan `review_age` ketika inferensi. Jika tujuan berubah menjadi prediksi jumlah vote kumulatif pada horizon tertentu, usia atau horizon harus tersedia pada tahap kalibrasi.
