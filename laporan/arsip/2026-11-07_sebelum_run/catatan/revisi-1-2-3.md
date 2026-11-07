# Dokumentasi Revisi Bab I–III

Dokumen ini menjelaskan perubahan pada naskah **"Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset"**. Isinya: daftar perubahan, sitasi yang ditambah, dihapus, atau diperbaiki, dan bukti bahwa setiap kalimat yang disitasi benar-benar ada di sumbernya, lengkap dengan nomor halaman.

| Berkas | Isi |
|---|---|
| `documents/... Dataset - Revisi.docx` | Naskah hasil revisi (Abstrak, Bab I–III, Daftar Pustaka) |
| `documents/Laporan Review Akademik dan Audit Referensi.md` | Tabel audit per subbab (masalah, jenis, tingkat, tindakan) |
| `documents/Referensi Skripsi (Zotero).bib` / `.ris` | 30 referensi untuk diimpor ke Zotero |
| `revisi-1-2-3.md` | Dokumen ini |

Berkas naskah asli **tidak diubah**.

**Cara membaca nomor halaman:**
- **"Hlm. naskah"** adalah nomor halaman pada `... - Revisi.docx`, dihitung setelah Daftar Isi diperbarui; Bab I dimulai di halaman 1.
- **"Hlm. sumber"** adalah nomor halaman yang **tercetak** pada jurnal atau prosiding. Untuk artikel bernomor artikel (PLOS ONE, MDPI, Scientific Reports), yang dipakai adalah nomor halaman di dalam PDF artikel.
- Kutipan asli disalin apa adanya (bahasa Inggris) dari PDF resmi.

---

## 1. Ringkasan perubahan

### Format (sesuai template skripsi Mikroskil)
- **Persamaan.** Semua rumus kini memakai Equation Editor Word (bukan teks tebal berbingkai).
  - Nomornya di kanan dengan format (bab.urut): (2.1)–(2.23) di Bab II dan (3.1)–(3.8) di Bab III.
  - Setiap rumus diikuti kata "dengan", lalu satu baris per simbol berformat "simbol = arti" (mengikuti contoh "Dimana: r = Jari-jari Bola" di template, tetapi tanpa titik dua).
- **Judul tabel** dipindah ke **atas** tabel dan memakai style "Judul Tabel". Sebelumnya berada di bawah dengan style Heading1, yang merusak daftar isi.
- **Judul bab** tidak lagi tampil "1. BAB I".
- **Nomor halaman** Bab I dimulai dari 1. Daftar Isi, Daftar Gambar, dan Daftar Tabel dibuat ulang.
- **Bab III** diganti menjadi **"TAHAPAN PELAKSANAAN"** (format S-1), dengan subbab 3.1–3.11 per tahap. Sebelumnya bab ini memakai format S-2 "Metodologi Penelitian".
- **Istilah asing** dicetak miring, dan nama kolom data memakai huruf monospace.

### Isi
- **Abstrak** ditulis ulang (ID 174 kata, EN 188 kata) dan tidak mengklaim hasil, karena eksperimen belum dijalankan.
- **Latar belakang** diringkas dari 5 menjadi **3 paragraf**: masalah dan bias label → penelitian terdahulu dan celah → solusi yang diusulkan.
- **Rumusan masalah** dipecah menjadi **3 RM**. **Tujuan** dibuat 1:1 dengan RM dan diberi indikator.
- **Manfaat** dipisah menjadi teoretis dan praktis.
- **Bab II** disusun ulang dari umum ke khusus:
  - 23 persamaan baru: TF-IDF, attention, embedding [CLS] dengan normalisasi L2, MLP, ReLU, dropout, Adam, RankNet, Negative Binomial, NDCG, Spearman, AP, dan MAP.
  - Tabel 2.1 berisi perbandingan 12 penelitian terdahulu.
- **Bab III:**
  - Diagram alir baru (Gambar 3.1).
  - Tabel 3.1 memetakan RM → tujuan → eksperimen → metrik.
  - Pembanding baru: **B0** (panjang ulasan) dan **B4** (*pointwise* MSE).
  - Ambang relevansi MAP **ditetapkan sebelum eksperimen**, tidak lagi dipilih dari data validasi.

Rincian lengkap per subbab ada di `documents/Laporan Review Akademik dan Audit Referensi.md` (Output A).

---

## 2. Perubahan sitasi

### 2.1 Dihapus

| Referensi lama | Alasan |
|---|---|
| [14 lama] Goel et al., HORIZON (ACL Findings 2026) | Sumber sekunder yang hanya *memakai* BLaIR dan menyebut checkpoint-nya "*pretrained on Amazon review titles*". Ini tidak sesuai dokumentasi resmi, yang menyatakan pelatihan pada pasangan (*item metadata, language context*). Diganti dengan sumber primer [15]. |
| Tautan "[Buka paper]" di setiap entri | Bukan bagian dari format IEEE. |

### 2.2 Diperbaiki

| Referensi | Kesalahan | Perbaikan |
|---|---|---|
| Nguyen et al., ACL Findings 2023 (sekarang [14]) | Urutan penulis salah | Nguyen, Wu, Dong, C.-D. Nguyen, Hai, Bing, Luu |
| Pittman et al., NTR 2020 (sekarang [28]) | Dua penulis hilang | Ditambah T. Liss dan R. Gueorguieva |
| Järvelin & Kekäläinen (sekarang [29]) | Diakritik hilang | Ditulis "Järvelin", "Kekäläinen" |
| Vaswani et al. (sekarang [19]) | Halaman 5998–6008 tidak ada di prosiding resmi | Diganti URL resmi NeurIPS; nama penulis dilengkapi |
| Urutan nomor | [5] muncul sebelum [4], dan [14] sebelum [6]–[13] | Dinomori ulang sesuai urutan kemunculan pertama (aturan IEEE di template) |

### 2.3 Ditambahkan (17 referensi baru)

| No | Referensi | Dipakai untuk |
|---|---|---|
| [1] | Mudambi & Schuff, *MIS Quarterly* 2010 | Definisi dan faktor penentu *helpfulness* |
| [4] | Liu et al., EMNLP-CoNLL 2007 | Tiga bias pada *helpful votes* |
| [5] | Alzate et al., *Computers in Human Behavior* 2024 | Bias visibilitas/posisi ulasan |
| [7] | Duru & Sunar, *Entropy* 2025 *(PDF dari kelompok)* | Distribusi `helpful_vote` dan perbandingan TF-IDF vs Transformer |
| [9] | Mitra & Jenamani, *IP&M* 2021 | Pendekatan multi-perspektif (CNN/LSTM/sintaksis) |
| [10] | Fan et al., WWW 2019 | *Helpfulness* yang memperhitungkan metadata produk |
| [11] | Bilal & Almazroi, *Electronic Commerce Research* 2023 | BERT untuk klasifikasi *helpfulness* |
| [12] | Liu et al., ACL 2021 | Tugas MRHP (pemeringkatan ulasan per produk) |
| [13] | Nguyen et al., EMNLP 2022 | MRHP dengan *contrastive learning* |
| [15] | Model card `hyp1231/blair-roberta-base` | Spesifikasi checkpoint yang dipakai |
| [17] | Manning et al., *Introduction to IR* 2008 | TF-IDF dan MAP |
| [21] | Muennighoff et al., MTEB, EACL 2023 | *Benchmark embedding* umum |
| [22] | Rumelhart et al., *Nature* 1986 | *Backpropagation* |
| [25] | Kingma & Ba, ICLR 2015 | Optimizer Adam |
| [26] | Liu, *FnTIR* 2009 | Pembagian *pointwise/pairwise/listwise* |
| [27] | Wang et al., *Scientific Reports* 2025 *(PDF dari kelompok)* | Pemakaian Amazon Reviews 2023 dan NDCG@K |
| [30] | Spearman, *Am. J. Psychology* 1904 | Korelasi peringkat |

Referensi lama yang tetap dipakai (dengan nomor baru): [2] Hou et al., [3] Ocampo Diaz & Ng, [6] Nayeem & Rafiei, [8] Du et al., [14] Nguyen et al. 2023, [16] Burges et al., [18] Gasparetto et al., [19] Vaswani et al., [20] Devlin et al., [23] Glorot et al., [24] Srivastava et al., [28] Pittman et al., dan [29] Järvelin & Kekäläinen.

---

## 3. Bukti kutipan per referensi

Status: ✅ = kalimat sumber ditemukan dan halamannya dicek langsung di PDF resmi. 🟡 = dicek dari abstrak resmi (halaman pertama artikel), karena teks lengkap berbayar atau tidak dapat diakses. ⚠️ = belum dapat dicek ulang dan perlu dicek manual (lihat Bagian 7).

### [1] Mudambi & Schuff (2010), *MIS Quarterly* 34(1), 185–200 🟡
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Kebermanfaatan ulasan dipengaruhi kedalaman isi, ekstremitas rating, dan jenis produk (1.1; juga 2.1) | 1, 6 | "*review extremity, review depth, and product type affect the perceived helpfulness of the review. Product type moderates the effect of review extremity on the helpfulness of the review.*" | 185 (abstrak) |
| Ulasan bermanfaat = ulasan yang membantu konsumen dalam keputusan pembelian; kedalaman berpengaruh positif (2.1) | 6 | "*what makes customer reviews helpful to a consumer in the process of making a purchase decision*" … "*review depth has a positive effect on the helpfulness of the review*" | 185 (abstrak) |

### [2] Hou et al. (2026), ACL 2026, hlm. 3251–3265 ✅
PDF: <https://aclanthology.org/2026.acl-long.147.pdf>. Berkas `documents/Bridging_Language_...pdf` adalah versi arXiv v2 dengan isi yang sama.

| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Amazon Reviews 2023 memuat >570 juta ulasan, ±48 juta item (1.1; 2.8) | 1, 12 | "*a new large-scale Amazon Reviews 2023 dataset with over 570 million reviews and 48 million items*" | 3251 (abstrak) |
| … dalam 33 kategori | 1, 12 | Tabel 1, baris "#Categories": Amazon'23 = **33**; #Reviews 571,544,897; #Items 48,185,153 | 3253 |
| BLaIR (ACL) adalah *benchmark* untuk *sequential recommendation, collaborative filtering, product search* (2.5) | 8 | "*a unified benchmark covering sequential recommendation, collaborative filtering, and product search*" | 3251 (abstrak) |
| Peringkat encoder pada rekomendasi hanya sedikit berkorelasi dengan MTEB (2.4) | 8 | "*The ranking on BLaIR shows little correlation with MTEB … we observe a correlation coefficient of −0.476 with p = 0.233*" | 3257 |
| Kegunaan BLaIR yang dilaporkan terbatas pada rekomendasi dan pencarian (2.11) | 17 | Abstrak hanya mencakup tiga tugas di atas; tidak ada tugas *helpfulness* | 3251 |
| Data diambil dari situs resmi (3.2) | 19 | "*Amazon Reviews 2023 dataset: https://amazon-reviews-2023.github.io*" | 3251 |

### [3] Ocampo Diaz & Ng (2018), ACL 2018, hlm. 698–708 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Penelitian *helpfulness* menaksir dan mengurutkan ulasan (1.1) | 1 | "*a review helpfulness prediction system could substantially save people's time by allowing them to focus on the most helpful reviews*" | 698 |
| Definisi label, *dataset*, dan protokol beragam sehingga hasil sulit dibandingkan (2.1) | 6 | "*Empirical comparisons are complicated for at least two reasons. First, historically, systems have been trained on different datasets … Second, researchers have not built on the successes of each other*" | 698 |

### [4] Liu et al. (2007), EMNLP-CoNLL, hlm. 334–342 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Tiga bias: *imbalance vote*, *winner circle*, *early bird* (1.1; 2.2) | 1, 6 | "*users' votes at Amazon have three kinds of biases as follows: (1) imbalance vote bias, (2) winner circle bias, and (3) early bird bias*" | 334 |
| *Imbalance*: pengguna lebih sering memberi suara positif | 6 | "*At the Amazon site, users tend to value others' opinions positively rather than negatively*" (Bagian 3.1.1) | 335 |
| *Winner circle*: ulasan teratas terus memperoleh suara | 6 | "*the top two reviews hold more than 250 and 140 votes … This is so-called the 'winner circle' bias: the more votes a review gains, the more default authority it would appear*" | 336 |
| *Early bird*: ulasan yang terbit lebih awal mendapat lebih banyak suara | 6 | "*the earlier a review is posted, the more votes it will get … reviews posted earlier are exposed to users for a longer time … We call this 'early bird' bias*" | 336 |

### [5] Alzate et al. (2024), *Computers in Human Behavior* 153, art. 108088 ⚠️
| Kalimat di naskah | Hlm. naskah | Status |
|---|---|---|
| Posisi tampil (visibilitas) berpengaruh kuat terhadap peluang memperoleh suara, terutama pada pengurutan "paling membantu"; visibilitas diukur sebagai kebalikan posisi (1.1; 2.2) | 1, 6 | Isinya sudah dicek di sesi sebelumnya lewat repositori Universidad Pública de Navarra (<https://academica-e.unavarra.es/handle/2454/48016>; versi *accepted manuscript*, akses terbuka). Repositori itu tidak bisa diakses dari lingkungan kerja ini saat dokumen ini ditulis, jadi **halaman belum dicatat**. Cek bagian *Abstract* dan *Results*. |

### [6] Nayeem & Rafiei (2023), EACL Findings, hlm. 1684–1692 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Suara langka pada ulasan baru (*cold-start*) dan produk kurang populer (1.1; 2.2) | 1, 6 | "*the helpfulness votes suffer from scarcity for less popular products and recently submitted (a.k.a., cold-start) reviews*" | 1684 (abstrak) |
| Ulasan lama mengakumulasi lebih banyak suara walau belum tentu paling relevan | 1, 6 | "*Older reviews are more likely to accumulate more helpfulness votes than newer reviews but are not necessarily the most relevant*" | 1686 |
| Informasi waktu dipakai sebagai **fitur masukan** (1.1) | 2 | "*Let td be the relative age of a review in days … ht = MLP(td)*" (pers. 5) | 1686 |
| *Dataset* berasal dari TripAdvisor (Tabel 2.1) | 15 | "*we build our dataset by scraping reviews from TripAdvisor*" | 1685 |

### [7] Duru & Sunar (2025), *Entropy* 27(12), 1202 ✅ *(PDF dari kelompok)*
Nomor halaman yang dipakai adalah nomor tercetak "x of 37". PDF kelompok berisi 1 halaman sampul, jadi halaman PDF = halaman tercetak + 1.

| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Sebagian besar ulasan belum memperoleh *helpful vote*; distribusi menceng (1.1; 2.8) | 1, 12 | "*helpful_vote … ranges from 0 to an integer maximum, which is 2169 … the majority of reviews, over 40,000, have not received any helpful votes*" (dari ±71.500 ulasan, hlm. 10) | 13 |
| Data yang dipakai adalah Amazon Reviews 2023 | 8, 12 | "*(https://amazon-reviews-2023.github.io/ …) The dataset used forms part of the collection gathered by McAuley Lab*" | 3 |
| Membandingkan TF-IDF, *embedding* statis, Transformer; kinerja tertinggi pada Transformer (2.4) | 8 | "*Bag of Words, TF-IDF, GloVe, FastText*" (hlm. 3); "*Transformer-based models … achieve the highest accuracy (92%)*" (abstrak, hlm. 1) | 1, 3 |

### [8] Du et al. (2019), *PLOS ONE* 14(12), e0226902 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| 30 fitur berbasis konten, enam domain Amazon, fitur semantik paling dominan (1.1) | 1 | "*the 30 most frequently used content-based features … helpfulness prediction on six domains of the largest publicly available Amazon 5-core dataset … semantics plays a dominant role in predicting informative reviews*" | 1 (abstrak) |

### [9] Mitra & Jenamani (2021), *IP&M* 58(3), 102538 🟡
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Menggabungkan perspektif leksikal, sekuensial, dan struktural melalui CNN, LSTM, dan fitur sintaksis (1.1) | 1 | Abstrak: d-CNN untuk perspektif leksikal (*n-gram*), LSTM untuk perspektif sekuensial, dan 14 fitur statistik sintaksis untuk perspektif struktural | Abstrak (hlm. 1 artikel) |

Teks lengkap berbayar (Elsevier). Abstrak dicek lewat katalog BITS Pilani: <https://dspace.bits-pilani.ac.in/items/d31b3f8e-b220-45f5-b38f-bea6774e24e6>.

### [10] Fan et al. (2019), WWW '19, hlm. 2715–2721 🟡
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Representasi yang memperhitungkan metadata produk meningkatkan kinerja pada Amazon dan Yelp (1.1) | 1 | "*the helpfulness of a review should be fully aware of the metadata … of its target product … two large-scale datasets … in Amazon and Yelp … our approach can achieve state-of-the-art performance*" | 2715 (abstrak) |
| PRH-Net untuk tugas identifikasi dan regresi (2.3) | 7 | "*Experiments are conducted on two different tasks: helpfulness identification and regression of online reviews*" | 2715 (abstrak) |

### [11] Bilal & Almazroi (2023), *Electronic Commerce Research* 23(4), 2737–2757 🟡
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| BERT *fine-tuned* mengungguli *bag-of-words*; klasifikasi biner ulasan Yelp; panjang sekuens berpengaruh (1.1; 2.3) | 1, 7 | "*The evaluations performed using Yelp shopping reviews show that fine-tuned BERT-based classifiers outperform bag-of-words approaches in classifying helpful and unhelpful reviews … the sequence length … has a significant impact on classification performance*" | 2737 (abstrak) |

Teks lengkap tersedia gratis di PMC: <https://pmc.ncbi.nlm.nih.gov/articles/PMC9051848/>.

### [12] Liu et al. (2021), ACL-IJCNLP, hlm. 5927–5936 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Memperkenalkan tugas MRHP (2.3) | 7 | "*This paper proposes a new task Multimodal Review Helpfulness Prediction (MRHP)*" | 5927 (abstrak) |
| Dirumuskan sebagai pemeringkatan (1.1) | 1 | "*we formulate the helpfulness prediction as a ranking problem and employ a pairwise ranking objective*" | 5928 |
| Dievaluasi dengan MAP dan NDCG (1.1) | 1 | "*we adopt two authoritative ranking-based metrics … Mean Average Precision (MAP) and Normalized Discounted Cumulative Gain (NDCG@N)*" | 5933 |

### [13] Nguyen et al. (2022), EMNLP 2022, hlm. 10085–10096 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| MRHP dengan *contrastive learning* adaptif (2.3) | 7 | Judul: "*Adaptive Contrastive Learning on Multimodal Transformer for Review Helpfulness Predictions*" | 10085 |
| Evaluasi dengan MAP dan NDCG (1.1) | 1 | Tabel hasil dengan kolom "MAP N@3 N@5" | 10090 |

### [14] Nguyen et al. (2023), ACL Findings 2023, hlm. 1670–1696 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Penelitian MRHP umumnya memakai FCNN + *pairwise loss*, dan kombinasi ini kurang tegas memisahkan ulasan (1.1; 2.7) | 2 | "*Previous studies commonly employ fully-connected neural networks (FCNNs) as the final score predictor and pairwise loss as the training objective. However, FCNNs have been shown to perform inefficient splitting for review features, making the model difficult to clearly differentiate helpful from unhelpful reviews*" | 1670 (abstrak) |
| Objektif *listwise* memberi generalisasi lebih baik (2.7) | 12 | "*pairwise objective … possibly induces low generalization during testing … a listwise optimization objective that enhances model generalization*" | 1670 (abstrak) |
| Representasi teks: fastText dan GloVe (1.1) | 2 | "*we leverage pretrained word embeddings with fastText embedding … and 300-dimensional GloVe word vectors*" | 1675 |
| *Helpful votes* dipetakan ke tingkat relevansi bertingkat (2.3; 2.9) | 7, 13 | "*We divide the helpfulness votes of the reviews into 5 partitions, i.e. [1, 2), [2, 4), [4, 8), [8, 16), and [16, ∞), corresponding to 5 helpfulness scores*" | 1675 |
| Diukur dengan MAP dan NDCG | 7 | "*we report Mean Average Precision (MAP) and Normalized Discounted Cumulative Gain (NDCG@N)*" | 1675 |

### [15] Model card `hyp1231/blair-roberta-base` (Hugging Face) ✅
Sumber: <https://huggingface.co/hyp1231/blair-roberta-base> (README dan `config.json`). Halaman web, jadi tidak ada nomor halaman.

| Kalimat di naskah | Hlm. naskah | Bukti dari sumber |
|---|---|---|
| Dilatih lanjut dari RoBERTa-base pada Amazon Reviews 2023 dengan pasangan metadata item dan konteks bahasa (1.1; 2.5) | 2, 8 | README: "*pre-trained on Amazon Reviews 2023 dataset … grounded on pairs of (item metadata, language context)*"; "*Finetuned from model: roberta-base*" |
| Menghasilkan representasi item untuk rekomendasi dan pencarian (1.1; 2.5; 2.11) | 2, 8, 17 | README: "*derive strong item text representations, for both recommendation and retrieval*" |
| RoBERTa-base adalah model awal tempat BLaIR dilatih lanjut, sehingga dipakai sebagai pembanding B5 (1.1) | 2 | README: "*Finetuned from model: roberta-base*"; tag `base_model: FacebookAI/roberta-base` |
| 12 lapisan, dimensi 768, maksimum 512 token (2.5) | 9 | `config.json`: `"num_hidden_layers": 12`, `"hidden_size": 768`, `"max_position_embeddings": 514` (512 token + 2 posisi khusus RoBERTa); README: `max_length=512` |
| *Embedding* dari *hidden state* lapisan terakhir di token pertama, lalu dinormalisasi L2 (2.5, pers. 2.6–2.7) | 9 | README: `last_hidden_state[:, 0]` lalu `embeddings / embeddings.norm(dim=1, keepdim=True)` |

### [16] Burges et al. (2005), ICML '05, hlm. 89–96 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| RankNet: peluang $P_{ij}$ = fungsi logistik dari selisih skor (2.7, pers. 2.12) | 11 | "*oij ≡ f(xi) − f(xj) … the map from outputs to probabilities are modeled using a logistic function … Pij ≡ e^oij / (1 + e^oij)*" (pers. 2) | 91 |
| *Loss* = *cross-entropy* antara $P_{ij}$ dan $\bar{P}_{ij}$ (pers. 2.13–2.14) | 11 | "*We will use the cross entropy cost function Cij ≡ −P̄ij log Pij − (1 − P̄ij) log(1 − Pij)*" (pers. 1, 3) | 91 |
| Bentuk *gain* $2^g-1$ pada NDCG (2.10) | 14 | "*NDCG … (2^r(j) − 1)/log(1 + j)*" (pers. 16) | 94 |

### [17] Manning, Raghavan & Schütze (2008), *Introduction to Information Retrieval* ⚠️ (halaman)
| Kalimat di naskah | Hlm. naskah | Lokasi di sumber |
|---|---|---|
| TF-IDF memberi bobot tinggi pada istilah yang sering di dokumen tetapi jarang di korpus (2.4, pers. 2.1) | 7 | Subbab **6.2.2 "Tf-idf weighting"**: bobot tertinggi bila istilah sering muncul dalam sedikit dokumen |
| MAP (2.10, pers. 2.22–2.23) | 15 | Subbab **8.4 "Evaluation of ranked retrieval results"**, definisi *Mean Average Precision* |

Isi kedua subbab ini adalah materi standar buku tersebut, tetapi **nomor halaman edisi cetak belum dicek di sini**: situs nlp.stanford.edu tidak dapat diakses dari lingkungan kerja ini. Cek lewat versi daring gratis: <https://nlp.stanford.edu/IR-book/>.

### [18] Gasparetto et al. (2022), *Information* 13(2), 83 ✅ (kalimat diperbaiki)
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Metode *shallow learning* dengan fitur seperti TF-IDF masih populer dalam praktik dan lazim dijadikan *baseline* kuat (2.4) | 8 | "*Shallow learning methods are still popular in many practical contexts, or as strong baselines.*" | 2 |
| (konteks TF-IDF) | — | "*TF is often weighted by inverse document frequency (IDF), which lessens the effect of common words*" | 8 |

> **Koreksi saat verifikasi.** Kalimat versi pertama ("TF-IDF bersifat jarang, efisien, dan mudah direproduksi") **tidak dinyatakan eksplisit** oleh sumber. Sumber justru menyebut ukuran vektor TF-IDF "*may still be excessively large*". Kalimat itu sudah diganti dengan rumusan di atas, yang sesuai dengan teks sumber.

### [19] Vaswani et al. (2017), NeurIPS ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| *Self-attention* mempelajari hubungan antartoken tanpa rekurensi (2.4) | 8 | "*the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely*"; "*a self-attention layer connects all positions with a constant number of sequentially executed operations*" | 1, 6 (halaman PDF) |

### [20] Devlin et al. (2019), NAACL, hlm. 4171–4186 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Prapelatihan bidireksional menghasilkan representasi yang dapat dipindahkan ke berbagai tugas (2.4) | 8 | "*BERT is designed to pretrain deep bidirectional representations … the pre-trained BERT model can be finetuned with just one additional output layer to create state-of-the-art models for a wide range of tasks*" | 4171 |

### [21] Muennighoff et al. (2023), MTEB, EACL, hlm. 2014–2037 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Kinerja di *benchmark* umum seperti MTEB tidak menjamin kinerja di domain tertentu (2.4) | 8 | "*We find that no particular text embedding method dominates across all tasks*" | 2014 |

Catatan: kalimat di naskah didukung bersama oleh [2] (hlm. 3257), yang menunjukkan secara langsung bahwa peringkat MTEB tidak berkorelasi dengan peringkat pada rekomendasi.

### [22] Rumelhart, Hinton & Williams (1986), *Nature* 323, 533–536 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| *Backpropagation* merambatkan gradien galat dari lapisan keluaran ke lapisan sebelumnya (2.6) | 9 | "*We describe a new learning procedure, back-propagation … repeatedly adjusts the weights … so as to minimize a measure of the difference between the actual output vector of the net and the desired output vector*" (hlm. 533); "*The backward pass which propagates derivatives from the top layer back to the bottom one*" (hlm. 534) | 533–534 |

### [23] Glorot, Bordes & Bengio (2011), AISTATS, hlm. 315–323 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| ReLU mendukung representasi jarang dan mempermudah pelatihan jaringan dalam (2.6) | 10 | "*creating sparse representations with true zeros … deep rectifier networks can reach their best performance without requiring any unsupervised pre-training*" | 315 |

### [24] Srivastava et al. (2014), *JMLR* 15, 1929–1958 ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| *Dropout* menonaktifkan unit secara acak sehingga unit tidak saling bergantung berlebihan (2.6) | 10 | "*The key idea is to randomly drop units (along with their connections) from the neural network during training. This prevents units from co-adapting too much.*" | 1929 |

### [25] Kingma & Ba (2015), ICLR ✅
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Adam memakai estimasi momen pertama dan kedua gradien (2.6) | 10 | "*computes individual adaptive learning rates for different parameters from estimates of first and second moments of the gradients*" | 1 (arXiv:1412.6980v9, versi ICLR) |

### [26] Liu (2009), *Foundations and Trends in IR* 3(3), 225–331 🟡
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| *Learning to rank* dibagi menjadi tiga kelompok (2.7) | 11 | "*the existing learning-to-rank algorithms are reviewed and categorized into three approaches: the pointwise, pairwise, and listwise approaches*" | 225 (abstrak) |

### [27] Wang et al. (2025), *Scientific Reports* 15, 28960 ✅ *(PDF dari kelompok)*
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Amazon Reviews 2023 dipakai untuk *sequential recommendation* (2.8) | 12 | "*The data that support the findings of this study were obtained from the publicly available Amazon Reviews 2023 dataset*" | 13 |
| … dengan evaluasi NDCG@K | 12 | "*We adopt three widely used ranking-based evaluation metrics, HR@K (H@K), NDCG@K (N@K), Recall@K*" | 9 |

### [28] Pittman et al. (2020), *Nicotine & Tobacco Research* 22(8), 1390–1398 🟡
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| Poisson mengasumsikan varians = rata-rata; Negative Binomial menambah parameter dispersi sehingga cocok untuk data *overdispersed* (2.9) | 13 | Abstrak: "*overdispersion (variance larger than expected)*" … "*In the absence of zero-inflation, the NB model fits smoking data well, which is typically overdispersed*" | 1390 (abstrak) |

Asumsi "varians = rata-rata" pada Poisson dijelaskan di bagian *Methods*. Teks lengkapnya gratis di PMC (<https://pmc.ncbi.nlm.nih.gov/articles/PMC7364829/>), tetapi halamannya belum dicatat di sini.

### [29] Järvelin & Kekäläinen (2002), *ACM TOIS* 20(4), 422–446 🟡
| Kalimat di naskah | Hlm. naskah | Bukti dari sumber | Hlm. sumber |
|---|---|---|---|
| NDCG memberi bobot lebih pada dokumen relevan di posisi awal dan dinormalisasi terhadap urutan ideal (2.10) | 14 | "*applies a discount factor to the relevance scores in order to devaluate late-retrieved documents. The third one computes the relative-to-the-ideal performance*" | 422 (abstrak) |

### [30] Spearman (1904), *Am. J. Psychology* 15(1), 72–101 ⚠️
| Kalimat di naskah | Hlm. naskah | Status |
|---|---|---|
| Korelasi peringkat Spearman mengukur kesesuaian monotonik antarurutan (2.10, pers. 2.20–2.21) | 15 | Definisi ini standar, tetapi teks artikel 1904 (JSTOR) **tidak dapat diakses** dari lingkungan kerja ini, sehingga halamannya belum dicatat. Cek lewat akses JSTOR kampus. |

### Tabel 2.1 (Perbandingan Penelitian Terdahulu, hlm. 15)
Setiap baris merangkum penelitian yang sama dengan bukti di atas: [1], [4], [8], [10], [9], [12], [13], [11], [6], [14], [7], [2]. Isi kolom *dataset*, metode, dan metrik diambil dari halaman yang tercantum pada tabel-tabel di atas.

---

## 4. Koreksi naskah yang dilakukan saat verifikasi

Kalimat-kalimat berikut sudah diperbaiki di `... - Revisi.docx`. Nomor sitasi tidak berubah.

| Lokasi | Sebelum | Sesudah | Alasan |
|---|---|---|---|
| 2.4 (hlm. 8) | "Representasi TF-IDF bersifat jarang, efisien, dan mudah direproduksi, sehingga lazim dijadikan baseline [18]." | "Metode *shallow learning* dengan fitur seperti TF-IDF masih populer dalam banyak konteks praktis dan lazim dipakai sebagai *baseline* yang kuat [18]." | Sumber hanya menyatakan "*still popular … or as strong baselines*" (hlm. 2) |
| 1.1 (hlm. 2) | "… kemampuan yang telah dilaporkan … pencarian serta rekomendasi produk **[2]**" | "Kemampuan yang sudah dilaporkan untuk model ini adalah menghasilkan representasi item dan konteks untuk pencarian serta rekomendasi produk **[15]**." | Versi ACL 2026 [2] adalah *benchmark* LLM dan tidak membahas checkpoint BLaIR; kemampuan checkpoint dinyatakan di model card [15] |
| 1.1, 1.1 (paragraf 3), 2.5, 2.11 | "dilatih pada pasangan **ulasan dan produk**" / "menghubungkan **teks ulasan** dengan informasi produk" | "pasangan **konteks bahasa dan metadata item**" / "menghubungkan **konteks bahasa dari Amazon Reviews 2023** dengan metadata produk" | Model card [15] hanya menyebut "*(item metadata, language context)*", tanpa kata "ulasan" |
| 2.11 (hlm. 17) | "… belum dievaluasi untuk helpfulness [2]" | "… kegunaan yang dilaporkan terbatas pada rekomendasi dan pencarian produk [2], [15]" | Klaim "belum pernah" tidak bisa dibuktikan oleh satu sumber; yang bisa dibuktikan adalah cakupan tugas yang dilaporkan |

---

## 5. Revisi tahap 2 (format tabel, tanda baca, bahasa, rumus)

### 5.1 Tabel
Semua delapan tabel kini memakai format yang sama:
- Lebar tabel sama dengan lebar teks (15,5 cm) dan posisinya di tengah.
- **Kolom "No"** ditambahkan pada Tabel 3.2, 3.3, 3.4, 3.6, dan 3.7. Tabel 2.1 sudah punya kolom No, Tabel 3.1 memakai kolom "RM", dan Tabel 3.5 memakai kolom "Kode".
- Padding sel 0,1 cm atas-bawah dan 0,19 cm kiri-kanan (standar Word), sehingga teks tidak menempel ke garis.
- Baris judul kolom dicetak tebal, rata tengah, berlatar abu-abu, dan diulang otomatis jika tabel berlanjut ke halaman berikutnya.
- Isi sel rata atas, termasuk kolom nomor, agar nomor sejajar dengan baris pertama teks.
- Kolom bernomor dan kolom berisi label pendek (misalnya "Ya/Tidak" dan "RM1") dibuat rata tengah. Kolom berisi kalimat dibuat rata kiri.
- Huruf 10 pt dengan spasi tunggal. Judul tabel tetap di atas tabel dan tidak terpisah dari tabelnya.

### 5.1b Judul subbab
- Nomor subbab (1.1, 2.3, 2.4.1, dan seterusnya) kini dimulai tepat di margin kiri, sejajar dengan tepi kiri paragraf di bawahnya. Sebelumnya nomor menjorok 0,64 cm.
- Teks judul subbab dimulai di 1,25 cm, sama dengan indentasi baris pertama paragraf.

### 5.2 Titik dua dan titik koma
- **Bab I–III tidak lagi memuat titik dua (:) maupun titik koma (;)**. Ini sudah dicek otomatis pada teks docx. Kalimat yang dulu memakai keduanya dipecah menjadi beberapa kalimat atau disambung dengan "yaitu", "dan", atau "sedangkan".
- Keterangan rumus memakai format "simbol = arti" tanpa titik koma di akhir baris.
- Isi tabel tidak lagi memakai titik koma. Contohnya, "{0,1; 0,2; 0,3}" menjadi "0,1, 0,2, atau 0,3".
- Teks di dalam Gambar 3.1 (diagram alir) juga sudah dibersihkan.
- Yang **tetap** memakai titik dua:
  - Label template "Kata kunci:" dan "Keywords:" di halaman abstrak, karena merupakan format wajib template.
  - Alamat web `https://...` dan judul resmi artikel di Daftar Pustaka. Judul artikel tidak boleh diubah.
  - Notasi matematika di dalam rumus.

### 5.3 Bahasa
Seluruh teks Abstrak dan Bab I–III ditulis ulang supaya lebih luwes dan mudah dibaca:
- Kalimat panjang dipecah menjadi kalimat-kalimat pendek.
- Kata yang kaku diganti dengan padanan yang lebih umum, misalnya "menggunakan" → "memakai", "sebagaimana" → "seperti", "diestimasi" → "diperkirakan" (di bagian yang bukan istilah teknis), dan "proksi" → "perkiraan".
- **Isi klaim dan sitasinya tidak berubah.** Setiap kalimat bersitasi dicek ulang terhadap kutipan sumber di Bagian 3. Nomor halaman naskah pada Bagian 3 tetap berlaku karena tidak ada kalimat bersitasi yang pindah halaman.

### 5.4 Rumus
Ke-31 rumus diperiksa ulang langsung dari docx (struktur OMML dibaca ulang menjadi teks):
- Semua rumus benar secara matematis dan sesuai sumbernya:
  - RankNet (2.12)–(2.14) sesuai pers. 1–3 Burges et al. (hlm. 91).
  - DCG (2.19) memakai gain $2^{g}-1$ sesuai pers. 16 Burges et al. (hlm. 94).
  - Dropout (2.8) sesuai Srivastava et al.
  - Adam (2.9)–(2.11) sesuai Kingma & Ba.
  - Varians Negative Binomial (2.16) memakai bentuk NB2, $\mu + \kappa\mu^2$.
- Satu perbaikan: TF-IDF (2.1) kini memakai $\log$, bukan $\ln$, mengikuti Manning et al. (basis logaritma tidak memengaruhi urutan bobot).
- Penomoran tetap urut, yaitu (2.1)–(2.23) dan (3.1)–(3.8). Semua rujukan "persamaan (x.y)" di teks dan tabel menunjuk ke nomor yang benar.

### 5.5 Pemeriksaan sitasi pada docx
Pemeriksaan otomatis pada `... - Revisi.docx`:
- Ada 30 nomor sitasi di teks, dan semuanya muncul di Daftar Pustaka.
- Nomor pertama kali muncul berurutan [1] → [30], sesuai aturan IEEE di template.
- Daftar Pustaka bernomor urut [1]–[30], tanpa entri yang tidak disitasi.

## 6. Revisi tahap 3 (tindak lanjut kritik reviewer)

Rincian kritiknya ada di `kritik-reviewer.md`. Perubahan yang **sudah** dimasukkan ke naskah:

| No | Kritik | Perubahan di naskah | Lokasi |
|---|---|---|---|
| 1 | Klaim manfaat domain BLaIR belum bisa dibuktikan tanpa pembanding arsitektur yang sama | Baseline **B5** ditambahkan, yaitu RoBERTa-base dibekukan + fitur + MLP *pairwise*. Ekstraksinya persis sama dengan BLaIR. Disebut juga di Abstrak, RM1, Tujuan 1, Tabel 3.1, Tabel 3.5, Subbab 3.6, 3.10, dan Gambar 3.1 | Bab I, II, III |
| 2 | Mekanisme hipotesis BLaIR lemah | Ditambahkan pengakuan bahwa dugaan ini belum kuat dan baru bisa dibuktikan lewat eksperimen (U vs B5) | 1.1 paragraf 3 |
| 3 | Risiko baseline panjang ulasan (B0) | Dinyatakan bahwa panjang ulasan dikenal sebagai prediktor kuat, dan bila U tidak jauh lebih baik dari B0 hasilnya dilaporkan apa adanya | 3.10 |
| 4 | Bias seleksi evaluasi (produk tanpa suara terbuang) | Ditambahkan butir Ruang Lingkup tentang cakupan evaluasi. Manfaat praktis tidak lagi menjanjikan kinerja pada produk tanpa suara. Jumlah produk dan ulasan yang gugur wajib dilaporkan | 1.4, 1.5, 3.9 |
| 5 | Kelemahan konsep koreksi usia (T3) | Paragraf baru tentang ketidaksamaan skala dan masalah identifikasi. T3 tidak lagi dianggap "lebih benar", hanya dibandingkan | 2.9 |
| 6 | Analisis sensitivitas tumpang tindih data BLaIR tidak bisa dijalankan | Rencana analisis dihapus dan diganti pernyataan keterbatasan | 2.5, 3.6, 3.10 |
| 7 | Eksperimen terlalu banyak | **Belum diubah di naskah.** Usulan pemangkasan dicatat di `kritik-reviewer.md` untuk didiskusikan dengan kelompok | — |

Tidak ada sitasi baru. Klaim "RoBERTa-base adalah model awal BLaIR" disitasi ke model card [15], dan buktinya sudah ditambahkan di Bagian 3. Urutan nomor sitasi [1]–[30] tidak berubah. Nomor halaman di Bagian 3 sudah disesuaikan (dua kalimat bergeser satu halaman). Bab I–III tetap tanpa titik dua dan titik koma.

## 7. Hal yang masih perlu dicek manual oleh kelompok

1. **[5] Alzate et al.** Catat halaman untuk klaim "visibilitas = kebalikan posisi ulasan" dan "efek lebih kuat pada pengurutan *most helpful*". Sumbernya versi *accepted manuscript* di academica-e.unavarra.es.
2. **[17] Manning et al.** Catat halaman edisi cetak untuk subbab 6.2.2 (TF-IDF) dan 8.4 (MAP).
3. **[28] Pittman et al.** Catat halaman untuk kalimat tentang asumsi varians = rata-rata pada Poisson (bagian *Methods*, PMC7364829).
4. **[30] Spearman.** Catat halaman definisi korelasi peringkat (akses JSTOR).
5. **[9], [10], [26], [29]** baru dicek dari abstrak. Isinya sudah sesuai, tetapi bila pembimbing meminta halaman isi, buka teks lengkapnya lewat akses perpustakaan.

## 8. Cara memverifikasi ulang
- PDF ACL Anthology dapat diunduh dari `https://aclanthology.org/<ID>.pdf`, dengan ID = bagian akhir DOI. Contoh: `2023.findings-acl.106`.
- Untuk artikel prosiding, nomor halaman tercetak = halaman pertama di daftar pustaka + (halaman PDF − 1).
- Cari kutipan bahasa Inggris pada tabel di atas dengan Ctrl+F di PDF.
