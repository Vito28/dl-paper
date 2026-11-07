# DL PAPER

**Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset**

Paper kelompok mata kuliah Deep Learning, ditargetkan untuk publikasi di JuTISI (Sinta 3).

## Tentang penelitian

Ulasan produk yang benar-benar membantu sering tenggelam di antara ribuan ulasan lain. Penelitian ini mengurutkan ulasan
dalam satu produk berdasarkan seberapa membantu ulasan tersebut, dengan `helpful_vote` sebagai label lemah.

- **Data**: Amazon Reviews 2023 (McAuley Lab), dibagi per produk (*product-disjoint*) agar model diuji pada produk yang belum pernah dilihat.
- **Model utama (U)**: embedding teks dari BLaIR-RoBERTa-base, digabung dengan fitur terstruktur (rating, *verified purchase*, panjang ulasan), lalu dinilai oleh MLP yang dilatih dengan loss *pairwise* RankNet.
- **Pembanding**: panjang ulasan (B0), TF-IDF linear dan MLP (B1, B2), BLaIR linear (B3), BLaIR *pointwise* (B4), dan RoBERTa-base (B5).
- **Pertanyaan penelitian**:
  1. Seberapa baik model utama dibanding *baseline*?
  2. Bagaimana pengaruh fitur terstruktur dan ukuran data latih?
  3. Bagaimana usia ulasan memengaruhi jumlah *helpful votes*, dan apakah target yang dikoreksi usia mengubah hasil?
- **Evaluasi**: NDCG@5/10, Spearman, dan MAP per produk, dengan interval kepercayaan *bootstrap*.

## Struktur repo

| Folder | Isi |
|---|---|
| `src/hr/` | Library pipeline |
| `notebooks/` | Notebook 01–10, notebook gabungan `00_pipeline_lengkap`, `00b_rekonsiliasi`, dan catatan run selesai (`FINISHED RUN/`) |
| `tools/`, `tests/` | Pembuat notebook gabungan dan uji *smoke* |
| `laporan/` | Laporan, referensi, dan arsip dokumen lama (lihat `laporan/README.md`) |
| `EXPERIMENTS.md` | Protokol eksperimen dan aturan yang dikunci di kode |
