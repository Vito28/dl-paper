# Kritik Reviewer dan Arah Penelitian

Dokumen ini adalah bahan diskusi kelompok. Isinya:
- **Bagian 1** berisi kritik yang kemungkinan besar diajukan reviewer (pembimbing, penguji, atau reviewer jurnal) terhadap Bab I–III, beserta status tindak lanjutnya.
- **Bagian 2** berisi usulan pemangkasan eksperimen. Bagian ini **belum diterapkan** di naskah dan perlu diputuskan bersama.
- **Bagian 3** membahas kelayakan tiga arah pengembangan: koreksi bias, validasi label manusia, dan *fine-tuning* BLaIR.
- **Bagian 4** berisi rekomendasi untuk target publikasi di JuTISI.

> **Catatan.** Penilaian ini ditulis oleh pihak yang ikut merevisi naskah, jadi tidak sepenuhnya netral. Anggap sebagai *self-review*, bukan pengganti masukan pembimbing.

---

## 1. Kritik utama

### Ringkasan penilaian

| Sudut pandang | Nilai | Catatan |
|---|---|---|
| Kebaruan ide | 6/10 | Memakai encoder yang sudah ada ditambah MLP. Bagian paling orisinal adalah koreksi usia pada target. |
| Metodologi | 7/10 | Kuat dalam pencegahan kebocoran. Celah terbesarnya (tidak ada pembanding RoBERTa) sudah ditutup dengan B5. |
| Validitas evaluasi | 6/10 | Cakupan evaluasi terbatas pada produk yang ulasannya punya suara. Keterbatasan ini kini sudah diakui di naskah. |
| Kajian pustaka | 7/10 | 30 referensi relevan dan terverifikasi. Baru 13 dari 30 yang terbit dalam 5 tahun terakhir. |
| Kelayakan untuk S-1 / proyek satu semester | 5/10 | Jumlah eksperimen terlalu banyak (lihat Bagian 2). |
| Penulisan | 8/10 | Rapi, konsisten, dan tanpa titik dua atau titik koma. |

### Rincian kritik

| No | Kritik | Kenapa penting | Status |
|---|---|---|---|
| 1 | **Belum ada pembanding RoBERTa-base.** BLaIR hanya dibandingkan dengan TF-IDF, sehingga kalau BLaIR menang, belum jelas apakah karena pelatihan domain Amazon atau sekadar karena Transformer lebih kuat dari TF-IDF. | Judul dan RM1 bertumpu pada klaim manfaat BLaIR. Tanpa pembanding ini, klaim tersebut tidak bisa dibuktikan. | ✅ **Sudah diperbaiki.** Ditambahkan **B5**, yaitu RoBERTa-base dibekukan + fitur + MLP *pairwise*, dengan prosedur ekstraksi yang persis sama. RoBERTa-base adalah model awal BLaIR, sehingga selisih U dan B5 = sumbangan pelatihan domain. |
| 2 | **Mekanisme hipotesis lemah.** BLaIR dilatih mencocokkan teks dengan produk, sedangkan kebermanfaatan berkaitan dengan seberapa informatif sebuah ulasan. | Reviewer akan bertanya kenapa BLaIR seharusnya membantu. | ✅ **Sudah disesuaikan.** Naskah kini mengakui dugaan ini belum kuat dan baru bisa dibuktikan lewat U vs B5. |
| 3 | **Panjang ulasan (B0) bisa jadi baseline yang sangat kuat.** Kedalaman ulasan, yang diukur dari jumlah kata, adalah salah satu prediktor helpfulness yang paling konsisten. | Ada kemungkinan nyata model U hanya sedikit lebih baik dari B0. | ✅ **Sudah disesuaikan.** Subbab 3.10 menyatakan bahwa hasil seperti itu dilaporkan apa adanya sebagai temuan. |
| 4 | **Bias seleksi evaluasi.** Produk yang semua ulasannya bernilai 0 tidak bisa dievaluasi (IDCG = 0), sehingga hasil lebih mewakili produk ramai. Ini bertentangan dengan klaim manfaat untuk "produk baru tanpa suara". | Klaim manfaat praktis tampak lebih besar daripada yang bisa dibuktikan. | ✅ **Sudah disesuaikan.** Ada butir baru di Ruang Lingkup, manfaat praktis dilunakkan, dan jumlah produk serta ulasan yang gugur wajib dilaporkan. |
| 5 | **Koreksi usia (T3) masih bisa dipertanyakan.** (a) Komponen usia ada di skala log-rata-rata Negative Binomial, sedangkan target di skala ln(1+v). (b) Ulasan lama mungkin memang lebih bermanfaat, dan koreksi ikut menghapus efek itu. | T3 bisa saja hanya "berbeda", bukan "lebih benar". | ✅ **Sudah disesuaikan.** Ada paragraf baru di 2.9, dan T3 kini hanya dibandingkan dengan T1, tidak diklaim lebih benar. Cara membuktikan mana yang lebih valid dibahas di Bagian 3.2. |
| 6 | **Analisis sensitivitas tumpang tindih data BLaIR tidak bisa dijalankan.** BLaIR dilatih pada Amazon Reviews 2023 sendiri (data sampai September 2023), sehingga tidak ada ulasan "setelah batas waktu". | Rencana yang tidak bisa dijalankan akan dipertanyakan saat sidang. | ✅ **Sudah diperbaiki.** Rencana dihapus dan diganti pernyataan keterbatasan. |
| 7 | **Eksperimen terlalu banyak** untuk satu semester, sekitar 20 konfigurasi × 3 *seed*. | Risiko terbesar proyek ini adalah tidak selesai, bukan hasil yang jelek. | ⏳ **Belum diubah di naskah.** Usulan ada di Bagian 2 untuk didiskusikan. |
| 8 | **Perbandingan berganda tanpa koreksi statistik.** Banyak pasangan model dibandingkan dengan IK 95% masing-masing. | Sebagian perbedaan "signifikan" bisa muncul karena kebetulan. | ⏳ Belum. Bisa diatasi dengan menetapkan satu perbandingan utama (U vs B5 dan U vs B1) dan menyebut sisanya eksploratif, atau dengan koreksi Holm. |
| 9 | **Kebaruan inkremental.** Kontribusinya adalah "menguji encoder yang sudah ada pada tugas baru". | Cukup untuk S-1 dan jurnal Sinta 3, tetapi kurang untuk S-2 atau jurnal bereputasi lebih tinggi. | ⏳ Tergantung arah yang dipilih (Bagian 3). |

---

## 2. Usulan pemangkasan eksperimen (untuk didiskusikan)

Rancangan di naskah saat ini:

| Kelompok | Konfigurasi | Jumlah |
|---|---|---|
| *Baseline* | B0, B1, B2, B3, B4, B5 | 6 |
| Model utama | U | 1 |
| Ablasi | A1–A4 | 4 |
| Skala data | E1–E5 | 5 |
| Strategi target | T1–T3 | 3 |
| **Total** | | **19 konfigurasi**, dan model neural masing-masing ≥3 *seed* |

Usulan tiga tingkat prioritas:

| Prioritas | Eksperimen | Alasan |
|---|---|---|
| **1. Wajib** (menjawab RM1) | U, B0, B1, B4, B5 | Inti klaim: BLaIR vs RoBERTa vs TF-IDF vs panjang ulasan, ditambah *pairwise* vs *pointwise* |
| **2. Penting** (menjawab RM2 dan RM3) | E1, E3, E5 (tiga skala, bukan lima), T1 vs T3 | Tiga titik sudah cukup untuk melihat tren skala. T2 dihapus karena paling lemah secara konsep. |
| **3. Opsional** (bila waktu cukup) | B2, B3, A1–A4, E2, E4, T2 | Menambah kedalaman, tetapi bukan penentu kesimpulan |

Dengan prioritas 1 dan 2 saja, jumlahnya sekitar **10 konfigurasi**, kira-kira setengah dari rancangan sekarang.

Hal yang perlu diputuskan kelompok:
- [ ] Setuju dengan tiga tingkat prioritas ini, atau ada eksperimen yang ingin dipertahankan?
- [ ] Skala data cukup 3 titik (E1, E3, E5), atau tetap 5?
- [ ] T2 (*age-matched pairs*) dihapus atau dijadikan opsional?
- [ ] Jumlah *seed*: 3 untuk semua, atau 3 hanya untuk U dan B5, sisanya 1?
- [ ] Perbandingan utama yang diuji ketat: U vs B5 dan U vs B1?

Setelah diputuskan, Bab III (Tabel 3.1, 3.5, Subbab 3.9 dan 3.10, serta Gambar 3.1) perlu disesuaikan.

---

## 3. Kelayakan tiga arah pengembangan

Ringkasan:

| Arah | Kelayakan untuk proyek ini | Nilai tambah | Rekomendasi |
|---|---|---|---|
| 3.1 Merumuskan koreksi bias secara formal | Rendah | Tinggi (level S-2 atau paper) | Jangan sekarang |
| 3.2 Validasi dengan label manusia | **Tinggi** | **Tinggi** | **Paling disarankan** |
| 3.3 *Fine-tuning* BLaIR dengan objektif pemeringkatan | Sedang | Sedang | Opsional, bila GPU dan waktu cukup |

### 3.1 Merumuskan koreksi bias secara formal

**Idenya.** Mengganti koreksi usia yang sekarang (mengurangi komponen usia dari target) dengan metode yang punya dasar teori. Contohnya *inverse propensity weighting* (IPW), yaitu memberi bobot pada setiap ulasan berdasarkan peluangnya untuk dilihat orang.

**Kenapa sulit untuk proyek ini:**
- IPW membutuhkan data **paparan**, misalnya posisi tampil ulasan atau berapa kali ulasan dilihat. Amazon Reviews 2023 tidak menyediakan data itu.
- Kalau peluang paparan hanya diperkirakan dari usia ulasan, asumsinya sangat kuat dan sulit dipertahankan di depan reviewer. Pada dasarnya hasilnya akan mirip dengan T3 sekarang, hanya dengan nama yang lebih rumit.
- Membuktikan bahwa sebuah metode benar-benar "mengurangi bias" butuh data pembanding yang tidak bias, dan itu tidak tersedia.

**Kesimpulan.** Arah ini cocok untuk tesis S-2 atau paper lanjutan, terutama jika ada data paparan. Untuk proyek ini, cukup pertahankan T3 sebagai pembanding yang jujur seperti sekarang.

### 3.2 Validasi dengan label manusia

**Idenya.** Sebagian ulasan dinilai manual oleh manusia, lalu hasilnya dipakai untuk menjawab dua pertanyaan:
1. Target mana yang lebih mendekati penilaian manusia, T1 (suara mentah) atau T3 (terkoreksi usia)? Ini langsung menjawab kritik nomor 5.
2. Apakah urutan dari model (U, B5, B0) cocok dengan urutan menurut manusia?

**Kenapa layak:**
- Tidak butuh GPU tambahan, hanya waktu anotasi.
- Bisa dikerjakan oleh anggota kelompok sendiri.
- Untuk reviewer jurnal, label manusia sangat meningkatkan kepercayaan pada hasil, karena kelemahan terbesar penelitian ini justru ada pada label.

**Gambaran rancangan** (angka di bawah adalah perkiraan awal untuk didiskusikan):
- **Sampel.** Sekitar 50–100 produk dari **data uji**, masing-masing 5–10 ulasan, sehingga totalnya sekitar 300–600 ulasan.
- **Penilai.** 2–3 anggota kelompok yang menilai secara terpisah.
- **Cara menilai.**
  - Skala 1–5 ("seberapa membantu ulasan ini untuk memutuskan membeli"), atau
  - Mengurutkan ulasan di dalam satu produk. Cara ini lebih cocok dengan tugas pemeringkatan.
- **Syarat penting.** Penilai **tidak boleh melihat** jumlah suara, tanggal, dan skor model, supaya penilaiannya tidak terpengaruh.
- **Kesepakatan antarpenilai.** Diukur dengan Cohen's kappa (2 penilai) atau Krippendorff's alpha (3 penilai). Jika kesepakatannya rendah, itu juga temuan yang layak dilaporkan.
- **Analisis.** Hitung korelasi Spearman dan NDCG antara urutan manusia dengan T1, T3, dan setiap model.

**Keterbatasan yang perlu ditulis.**
- Penilai adalah penulis sendiri, bukan pembeli sebenarnya.
- Sampelnya kecil dibandingkan seluruh data.

Jika arah ini dipilih, perlu ditambahkan: satu rumusan masalah atau perluasan RM3, satu subbab di Bab III, dan rujukan tentang metode anotasi serta kesepakatan antarpenilai. Rujukan baru harus dicari dan diverifikasi dulu.

### 3.3 *Fine-tuning* BLaIR dengan objektif pemeringkatan

**Idenya.** Encoder BLaIR tidak lagi dibekukan, tetapi ikut dilatih bersama MLP dengan *loss* RankNet. Tujuannya melihat apakah encoder yang disesuaikan untuk tugas ini lebih baik daripada yang dibekukan.

**Yang perlu dipertimbangkan:**
- **Biaya komputasi naik drastis.** Embedding tidak bisa lagi dihitung sekali lalu dipakai ulang, karena setiap epoch harus menjalankan seluruh Transformer. Pada GPU tunggal, ini biasanya hanya realistis untuk subset data (misalnya sekitar 100.000 ulasan) dan panjang teks yang dipotong (misalnya 256 token).
- **Agar adil, RoBERTa-base juga harus di-*fine-tune*.** Kalau tidak, perbandingan U vs B5 kembali tidak seimbang. Akibatnya jumlah run bertambah dua kali.
- **Risiko *overfitting*** pada label yang berisik (*helpful votes*) lebih tinggi.
- Bilal dan Almazroi [11] sudah menunjukkan BERT yang di-*fine-tune* efektif untuk *helpfulness*, jadi hasilnya kemungkinan besar lebih baik. Namun, kebaruannya terbatas.

**Kesimpulan.** Layak sebagai eksperimen tambahan bila GPU dan waktu tersedia. Arah ini tidak menjawab kelemahan terbesar penelitian (validitas label), jadi prioritasnya di bawah validasi manusia.

---

## 4. Rekomendasi untuk target JuTISI

1. **Kunci eksperimen inti** (Bagian 2, prioritas 1 dan 2).
2. **Tambahkan validasi label manusia** dalam skala kecil (Bagian 3.2). Ini pembeda paling kuat dibandingkan paper sejenis, dan biayanya murah.
3. *Fine-tuning* BLaIR hanya dikerjakan jika langkah 1 dan 2 selesai lebih cepat dari rencana.
4. Koreksi bias formal (IPW) disimpan untuk penelitian lanjutan dan disebut di bagian Simpulan atau saran.

Hal penting dari template JuTISI (`documents/JutisiTemplate2022F.doc`) yang memengaruhi rencana:
- Naskah wajib memuat **hasil dan pembahasan**. Proposal tanpa hasil tidak akan diterima.
- Panjang naskah **7–15 halaman (3.500–7.500 kata)** termasuk pustaka. Bab I–III versi skripsi harus dipadatkan menjadi Pendahuluan dan Metode.
- Judul berbahasa Indonesia, **maksimal 12 kata, tanpa singkatan**. "BLaIR" dan "MLP" tidak boleh ada di judul.
- Sitasi berganda ditulis "[2], [3], [4]–[6]".
- Pustaka minimal 12, diusahakan terbit 10 tahun terakhir. Saat ini 19 dari 30 referensi (63%) memenuhi syarat itu.
- Status akreditasi, biaya, dan waktu tunggu JuTISI belum dicek. Pastikan di situs resmi jurnal sebelum mengirim.
