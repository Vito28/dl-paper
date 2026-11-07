# Laporan Review Akademik dan Audit Referensi

**Naskah:** Pemeringkatan Helpfulness Ulasan Menggunakan Embedding BLaIR dan MLP pada Dataset Amazon Reviews 2023
**Berkas yang ditinjau:** `Review Helpfulness Ranking ... Dataset.docx` (Bab I–II) dan `... - Bab III.docx` (Bab I–III; Bab I–II identik dengan berkas pertama)
**Berkas hasil revisi:** `Review Helpfulness Ranking ... Dataset - Revisi.docx`
**Acuan format:** aturan template skripsi Universitas Mikroskil (dipulihkan dari riwayat git, commit `2c7f2c5`), yaitu Subbab 2.4 Gambar dan Tabel, 2.5 Persamaan Matematika, 2.6 Numbering, dan 2.7 Pengacuan Pustaka
**Tanggal review:** 29 Oktober 2026

---

## Output A — Laporan Review Akademik

Jenis masalah: **IL** = kesalahan ilmiah, **MT** = inkonsistensi metodologis, **AR** = kelemahan argumentasi, **RD** = masalah redaksional/format.
Tingkat kepentingan: **Tinggi** / **Sedang** / **Rendah**.

### A.1 Abstrak

| Bagian | Masalah | Jenis | Tingkat | Alasan | Tindakan |
|---|---|---|---|---|---|
| Abstrak dan Abstract | Masih berisi teks petunjuk template | RD | Tinggi | Wajib ada; 100–200 kata, satu paragraf | Ditulis ulang (ID 178 kata, EN 197 kata). Abstrak tidak mengklaim hasil karena eksperimen belum dilakukan. |
| Kata kunci | Masih placeholder | RD | Sedang | Template meminta 3–5 kata kunci | Diisi 5 kata kunci |

### A.2 Bab I

| Subbab | Masalah | Jenis | Tingkat | Alasan | Tindakan |
|---|---|---|---|---|---|
| 1.1 Latar Belakang | Terdiri atas 5 paragraf | RD | Tinggi | Ketentuan meminta tepat 3 paragraf | Disusun ulang menjadi 3 paragraf: masalah dan bias label → penelitian terdahulu dan *gap* → solusi BLaIR+MLP |
| 1.1 | Kemampuan BLaIR tidak dibedakan dari hipotesis | IL | Tinggi | Sumber asli hanya melaporkan *retrieval* dan rekomendasi | Kemampuan yang telah dilaporkan dan hipotesis untuk *helpfulness* kini dipisahkan secara eksplisit |
| 1.1 | Checkpoint dideskripsikan "diprapelatih pada judul ulasan" dan disitasi ke HORIZON [14 lama] | IL | Tinggi | Model card resmi menyatakan pelatihan pada pasangan (metadata item, konteks bahasa); HORIZON adalah sumber sekunder yang keliru | Diganti dengan model card resmi [15] dan publikasi BLaIR [2] |
| 1.1 | *Gap* belum dibangun dari bukti literatur | AR | Tinggi | Kebaruan kombinasi metode saja tidak cukup | Tiga *gap* kini diturunkan dari literatur: representasi umum [8, 11, 14]; usia sebagai fitur [6]; belum ada evaluasi pada produk baru |
| 1.1 | Kritik terhadap FCNN dengan *pairwise loss* tidak dibahas | AR | Tinggi | Nguyen et al. [14] mengkritik arsitektur yang persis dipakai penelitian ini | Kritik diakui dan dijawab dengan pembanding *pointwise* (B4) serta *baseline* |
| 1.1 | Bias label hanya dibahas dari sisi usia | AR | Sedang | Literatur juga mendokumentasikan bias posisi atau visibilitas [4, 5] | Ditambahkan dan diakui sebagai keterbatasan |
| 1.2 Rumusan Masalah | Satu kalimat majemuk dengan banyak tujuan | AR | Tinggi | Sulit diuji dan tidak tajam | Dipecah menjadi 3 rumusan masalah yang dapat diuji |
| 1.3 Tujuan | 5 butir tanpa padanan 1:1 dengan rumusan masalah; "mengimplementasikan" tidak terukur | MT | Sedang | Tujuan harus menjawab rumusan masalah dan memiliki indikator | 3 tujuan, masing-masing dengan indikator (NDCG@10 dan IK 95%, ablasi/skala, kurva usia) |
| 1.4 Manfaat | Belum dipisah teoretis/praktis; ada nada klaim | RD | Sedang | Diminta pedoman | Dipisah menjadi manfaat teoretis dan praktis, dirumuskan sebagai harapan |
| 1.5 Ruang Lingkup | Kategori data belum ditetapkan; bias posisi tidak disebut | MT | Sedang | Batasan harus konsisten dengan metode | Kriteria pemilihan kategori dan keterbatasan bias posisi ditambahkan |

### A.3 Bab II

| Subbab | Masalah | Jenis | Tingkat | Alasan | Tindakan |
|---|---|---|---|---|---|
| Seluruh bab | Persamaan ditulis sebagai teks tebal berbingkai, tidak bernomor, dan tidak dijelaskan | RD | Tinggi | Template mewajibkan Equation Editor, nomor di kanan berformat (bab.urut), dan penjelasan variabel | 23 persamaan Bab II dan 8 persamaan Bab III kini berupa persamaan Word asli (OMML), bernomor (2.1)–(2.23) dan (3.1)–(3.8), diikuti penjelasan simbol berformat "simbol = arti" |
| Struktur | Belum tersusun dari umum ke khusus; MLP tanpa persamaan; metrik tanpa rumus | AR | Tinggi | Pedoman kajian literatur | Disusun ulang: ulasan → bias → tugas → representasi → BLaIR → MLP → LTR → *dataset* → target → metrik → penelitian terdahulu |
| 2.5 BLaIR | Menyebut BLaIR sekadar *benchmark* lalu mencampur dengan checkpoint; [14] dipakai untuk detail teknis | IL | Tinggi | Lihat audit referensi | Penjelasan dipisah antara publikasi ACL 2026 (*benchmark* dan *dataset*) dan checkpoint (model card: RoBERTa-base, 12 lapisan, 768 dimensi, 512 token, [CLS] dengan normalisasi L2) |
| 2.5 | Tidak membahas kemungkinan tumpang tindih data prapelatihan BLaIR | MT | Sedang | BLaIR dilatih pada Amazon Reviews 2023, sehingga teks ulasan uji mungkin pernah terlihat oleh *encoder* (tanpa label) | Diakui sebagai keterbatasan; analisis sensitivitas dirancang di 3.6 |
| 2.7 LTR | Klaim *pairwise* perlu dijelaskan karena skor dihitung per ulasan | MT | Sedang | Diminta pedoman | Dijelaskan bahwa skor bersifat *pointwise*, tetapi *loss* didefinisikan per pasangan. Persamaan RankNet (2.12)–(2.14) diturunkan dari *cross-entropy*. |
| 2.10 Metrik | NDCG, Spearman, dan MAP tanpa definisi; Spearman tidak membahas nilai kembar | IL | Sedang | Target banyak bernilai 0 sehingga banyak nilai kembar | Rumus (2.19)–(2.23) ditambahkan; Spearman memakai peringkat rata-rata |
| 2.11 | Belum ada tabel komparatif penelitian terdahulu | AR | Tinggi | Diminta pedoman | Tabel 2.1 (12 penelitian) dan sintesis kritis ditambahkan |
| 2.8 (lama: Pemisahan Data) dan Kerangka Pemikiran | Isi metodologis berada di Bab II | RD | Rendah | Bab II untuk teori | Dipindahkan ke Bab III |

### A.4 Bab III

| Subbab | Masalah | Jenis | Tingkat | Alasan | Tindakan |
|---|---|---|---|---|---|
| Judul dan struktur bab | Memakai format S-2 ("METODOLOGI PENELITIAN": Sampling, Metode Pengumpulan Data, dan seterusnya) | RD | Tinggi | Template mewajibkan judul "TAHAPAN PELAKSANAAN" untuk S-1 | Diganti menjadi "BAB III TAHAPAN PELAKSANAAN" dengan subbab 3.1–3.11 per tahap |
| Keterpaduan | Rumusan masalah tidak dipetakan ke eksperimen | MT | Tinggi | Setiap rumusan masalah harus punya metode uji | Tabel 3.1 memetakan RM → tujuan → eksperimen → metrik; Subbab 3.10 menjelaskan cara menjawab tiap rumusan masalah |
| Ambang MAP | Ambang relevansi "dipilih" dengan data validasi | MT | Tinggi | Definisi metrik tidak boleh ditala berdasarkan kinerja model | Ambang ditetapkan sebelum eksperimen ($g \geq 2$); kuantil hanya dari data latih |
| *Baseline* | Tidak ada pembanding *pointwise* maupun *baseline* heuristik | MT | Tinggi | Tanpa B4, manfaat *pairwise* tidak teruji; tanpa B0, sulit menilai apakah model lebih baik dari heuristik panjang ulasan | B0 (panjang ulasan) dan B4 (*pointwise* MSE) ditambahkan |
| Konfigurasi MLP | Tidak membedakan nilai yang ditetapkan, ditala, dan direncanakan | MT | Sedang | Diminta pedoman | Tabel 3.4 diberi kolom status |
| Pembentukan *ranking* | Penanganan skor kembar dan acuan *ground truth* tidak dijelaskan | MT | Sedang | Diminta pedoman | Persamaan (3.7) ditambahkan beserta aturan skor kembar dan acuan |
| Diagram alir | Urutan "Evaluasi → Ranking" terbalik; tidak memuat kesimpulan | MT | Sedang | Diagram harus sesuai metode | Gambar 3.1 digambar ulang: alur bercabang target/fitur, setiap kotak diberi nomor subbab |
| Keterangan tabel | Judul tabel berada di bawah tabel dan memakai style Heading1 | RD | Tinggi | Template: judul tabel di atas tabel; style Heading1 mengacaukan daftar isi dan penomoran bab | Judul tabel dipindah ke atas dengan style "Judul Tabel" |
| Format umum | Judul bab tampil "1. BAB I"; nomor halaman Bab I tidak mulai dari 1; Daftar Lampiran berisi entri daftar isi | RD | Sedang | Format skripsi | Ketiganya diperbaiki |

---

## Output C — Audit Referensi dan Zotero

### C.1 Status integrasi Zotero

**Naskah asli tidak memiliki satu pun field Zotero** (tidak ada `ADDIN ZOTERO_ITEM` maupun `ZOTERO_BIBL`). Seluruh sitasi `[n]` dan daftar pustaka berupa teks biasa yang diketik manual, sehingga tidak ada field Zotero yang dapat dipertahankan.

Pada naskah revisi, sitasi tetap berupa teks biasa, tetapi sudah benar: penomoran IEEE sesuai urutan kemunculan pertama (template 2.7) dan daftar pustaka 1:1 dengan sitasi. Sitasi ini belum terhubung ke Zotero. Untuk menghubungkannya:

1. Impor `Referensi Skripsi (Zotero).bib` atau `.ris` ke Zotero (File → Import). Seluruh 30 entri sudah disertai DOI/URL.
2. Di Word, pilih style **IEEE** pada Zotero (Document Preferences).
3. Ganti setiap sitasi teks `[n]` dengan *Add/Edit Citation* menggunakan item yang sesuai. Urutan nomor pada naskah revisi akan identik dengan hasil Zotero karena mengikuti urutan kemunculan.
4. Hapus daftar pustaka teks, lalu sisipkan *Add/Edit Bibliography*.

Sitasi yang perlu dihubungkan manual: **semua** (naskah tidak pernah memakai field Zotero).

### C.2 Referensi lama

| Lama | Referensi | Status | Catatan | Nomor baru |
|---|---|---|---|---|
| [1] | Du et al., PLOS ONE 2019 | Dipertahankan; terverifikasi (Crossref) | — | [8] |
| [2] | Hou et al., ACL 2026 | Dipertahankan; terverifikasi | Versi ACL adalah *benchmark* dan tidak lagi memuat checkpoint `blair-roberta-base`. Hanya dipakai untuk *dataset* dan konteks *benchmark*. | [2] |
| [3] | Nayeem & Rafiei, EACL Findings 2023 | Dipertahankan; terverifikasi | *Dataset*-nya adalah TripAdvisor (bukan Amazon) dan kini dinyatakan demikian | [6] |
| [4] | Nguyen et al., ACL Findings 2023 | **Diperbaiki** | Urutan penulis salah. Yang benar: Nguyen, Wu, Dong, C.-D. Nguyen, Hai, Bing, Luu. | [14] |
| [5] | Ocampo Diaz & Ng, ACL 2018 | Dipertahankan; terverifikasi | — | [3] |
| [6] | Gasparetto et al., Information 2022 | Dipertahankan; terverifikasi | — | [18] |
| [7] | Vaswani et al., NeurIPS 2017 | **Diperbaiki** | Nomor halaman 5998–6008 tidak tercantum pada prosiding resmi, sehingga dihapus dan diganti URL resmi; nama penulis dilengkapi | [19] |
| [8] | Devlin et al., NAACL 2019 | Dipertahankan; terverifikasi | — | [20] |
| [9] | Glorot et al., AISTATS 2011 | Dipertahankan | Tidak memiliki DOI (PMLR) | [23] |
| [10] | Srivastava et al., JMLR 2014 | Dipertahankan | Tidak memiliki DOI (JMLR) | [24] |
| [11] | Burges et al., ICML 2005 | Dipertahankan; terverifikasi | Juga dipakai sebagai sumber bentuk *gain* $2^g-1$ pada NDCG | [16] |
| [12] | Pittman et al., NTR 2020 | **Diperbaiki** | Dua penulis hilang: T. Liss dan R. Gueorguieva | [28] |
| [13] | Järvelin & Kekäläinen, TOIS 2002 | **Diperbaiki** | Diakritik nama dipulihkan | [29] |
| [14] | Goel et al., HORIZON (ACL Findings 2026) | **Dihapus** | Sumber sekunder yang hanya *memakai* BLaIR dan mendeskripsikannya secara keliru ("*pretrained on Amazon review titles*"). Diganti sumber primer. | — |
| — | Tautan "[Buka paper]" pada setiap entri | **Dihapus** | Bukan bagian format IEEE | — |
| — | Urutan nomor | **Diperbaiki** | Naskah lama menyitasi [5] sebelum [4], dan [14] sebelum [6]–[13]. Ini melanggar aturan urutan kemunculan. | — |

### C.3 Referensi baru (semua diverifikasi melalui Crossref, ACL Anthology, atau halaman penerbit)

| No | Referensi | Alasan ditambahkan |
|---|---|---|
| [1] | Mudambi & Schuff, MIS Quarterly 2010 | Definisi dan faktor penentu *helpfulness* (studi klasik) |
| [4] | Liu et al., EMNLP-CoNLL 2007 | Bukti tiga bias pada *helpful votes* |
| [5] | Alzate et al., Computers in Human Behavior 2024 | Bukti bias visibilitas/posisi terhadap suara |
| [7] | Duru & Sunar, Entropy 2025 *(PDF dari kelompok)* | Amazon Reviews 2023: dominasi suara nol; TF-IDF vs Transformer |
| [9] | Mitra & Jenamani, IP&M 2021 | Pendekatan multi-perspektif CNN/LSTM |
| [10] | Fan et al., WWW 2019 | PRH-Net, *helpfulness* yang memperhitungkan produk |
| [11] | Bilal & Almazroi, Electronic Commerce Research 2023 | BERT untuk *helpfulness* (klasifikasi) |
| [12] | Liu et al., ACL 2021 | Tugas MRHP (pemeringkatan per produk) |
| [13] | Nguyen et al., EMNLP 2022 | MRHP dengan *contrastive learning* |
| [15] | Model card `hyp1231/blair-roberta-base` (Hugging Face, 2024) | Sumber primer spesifikasi checkpoint (lihat catatan preprint) |
| [17] | Manning et al., Introduction to IR 2008 | TF-IDF dan MAP |
| [21] | Muennighoff et al., MTEB, EACL 2023 | *Benchmark embedding* umum |
| [22] | Rumelhart et al., Nature 1986 | *Backpropagation* untuk MLP |
| [25] | Kingma & Ba, ICLR 2015 | Optimizer Adam |
| [26] | Liu, FnTIR 2009 | Taksonomi *pointwise/pairwise/listwise* |
| [27] | Wang et al., Scientific Reports 2025 *(PDF dari kelompok)* | Penggunaan Amazon Reviews 2023 dan NDCG@K pada penelitian terbaru |
| [30] | Spearman, Am. J. Psychology 1904 | Korelasi peringkat |

Catatan tentang PDF yang ditemukan kelompok: ketiganya dipakai. `Bridging_Language...pdf` adalah [2], sedangkan Entropy 2025 dan Scientific Reports 2025 adalah [7] dan [27]. Scientific Reports 2025 relevansinya terbatas (rekomendasi multimodal), sehingga hanya dipakai untuk konteks *dataset* dan metrik.

### C.4 Hal yang perlu diputuskan atau dikonfirmasi ke pembimbing

1. **Larangan preprint (template 2.7).** Checkpoint `blair-roberta-base` berasal dari arXiv:2403.03952 **v1** (2024). Versi peer-reviewed (ACL 2026) tidak lagi memuat checkpoint maupun persamaan *contrastive loss*-nya. Oleh karena itu, naskah revisi menyitasi model card resmi sebagai dokumentasi teknis (diizinkan template sebagai "website resmi lembaga"). Persamaan *contrastive loss* BLaIR sengaja tidak dimasukkan. Jika pembimbing mengizinkan preprint, v1 dapat ditambahkan sebagai sumber persamaan tersebut. Makalah RoBERTa (arXiv:1907.11692) juga preprint dan karena itu tidak disitasi.
2. **Anjuran 70% referensi terbitan 5 tahun terakhir.** Saat ini 13 dari 30 referensi (43%) terbit 2021–2026. Naskah lama: 5 dari 14 (36%). Referensi teori dasar (RankNet, dropout, NDCG, Spearman) memang klasik. Untuk mendekati 70%, tambahkan penelitian *helpfulness* 2021–2026 yang dibaca langsung oleh kelompok, dan pertimbangkan pustaka Dosen Tetap Mikroskil sesuai anjuran template.
3. **Batas waktu data latih BLaIR.** Batas waktu ini diperlukan untuk analisis sensitivitas di 3.6, tetapi belum dapat diverifikasi dari sumber resmi.

---

## Output D — Evaluasi Akhir

1. **Argumentasi dan *gap*.** Kini dibangun dari bukti, bukan asumsi. Bagian terkuat adalah *gap* label (bias paparan [4–6]). Bagian terlemah adalah *gap* "belum ada evaluasi product-disjoint": klaim ini dibatasi pada "penelitian yang dikaji" karena tidak dapat dibuktikan bahwa tidak ada sama sekali.
2. **Kesesuaian BLaIR dan MLP.** Kesesuaian BLaIR masih hipotesis yang masuk akal (domain pelatihan sama), dan kini dinyatakan demikian. Risiko yang perlu disadari: Nguyen et al. [14] menunjukkan kelemahan FCNN dengan *pairwise loss*. Jika U tidak mengungguli B4 atau B3, temuan itu tetap sah dan harus dilaporkan.
3. **Metodologi.** Kuat dalam pencegahan kebocoran (product-disjoint, statistik hanya dari data latih, target *out-of-fold*, ambang tetap). Risiko terbesar adalah **cakupan**: kombinasi B0–B4, A1–A4, E1–E5, T1–T3, dan ≥3 *seed* menghasilkan puluhan run. Untuk skripsi S-1, prioritaskan U, B1, B3, B4, E1–E5, serta T1 vs T3; perlakukan sisanya sebagai tambahan bila waktu cukup.
4. **Validitas evaluasi.** NDCG@10 makro dengan *bootstrap* tingkat produk sudah tepat. Keterbatasan yang tidak dapat diatasi: label tetap bergantung pada *helpful votes*, dan bias posisi tidak dapat dikoreksi karena urutan tampil tidak tersedia.
5. **Konsistensi Bab I–III.** RM1–RM3 → Tujuan 1–3 → Tabel 3.1 → eksperimen → Subbab 3.10 kini saling terkait. Definisi *helpfulness*, unit *ranking* (`parent_asin`), dan fitur masukan sama di semua bab.
6. **Bahasa.** Formal dan langsung, tanpa kalimat pembuka generik. Istilah asing dicetak miring secara otomatis dan konsisten, nama variabel data memakai huruf monospace.
7. **Kesiapan.** Siap ditinjau pembimbing sebagai proposal (Bab I–III), dengan tiga syarat:
   - **Sebelum dikirim, buka di Microsoft Word dan setujui *Update Fields*** saat diminta, agar daftar isi dan nomor halaman diperbarui. Persamaan perlu dicek visual di Word karena pratinjau di lingkungan kerja ini tidak dapat merender persamaan.
   - Kategori data harus diputuskan (lihat Ruang Lingkup butir 1).
   - Butir C.4 perlu dikonfirmasi ke pembimbing.

Hal yang belum dapat diverifikasi: nilai *learning rate*, ukuran *batch*, *epoch*, dan batas pasangan $M$ (ditandai "direncanakan/ditala"); batas waktu data latih BLaIR; satuan `timestamp` pada berkas yang benar-benar diunduh (dokumentasi tidak menyatakannya secara eksplisit).
