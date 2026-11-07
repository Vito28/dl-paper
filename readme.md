# DL PAPER

**Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset**

Paper kelompok mata kuliah Deep Learning, ditargetkan untuk publikasi di JuTISI (Sinta 3).

## Tautan dan hasil utama

- **Laporan tugas:** [`laporan/LAPORAN.md`](laporan/LAPORAN.md)
- **Aplikasi demo (Gradio, Hugging Face Spaces):** https://huggingface.co/spaces/Nathjsn/pemeringkatan-ulasan-helpful
- **Hasil utama (kategori Video_Games, data uji, 3.827 produk):** NDCG@10 model U **0,715** (IK 95% 0,707–0,723),
  dibanding urutan acak 0,499 dan urutan menurut panjang ulasan (B0) 0,702. RoBERTa-base asli (B5) sedikit lebih baik,
  yaitu 0,720. Angka lengkap ada di `notebooks/FINISHED RUN/hasil_video_games/tables/`.

## Cara menjalankan

```bash
pip install -r requirements.txt
python -m tests.smoke_test                       # uji cepat dengan data sintetis, CPU, tanpa unduhan
python tests/run_notebooks_smoke.py notebooks    # jalankan semua notebook dengan data sintetis
```

Run penuh dijalankan di Google Colab (GPU T4, sekitar 8,5 jam) dengan mengunggah
`notebooks/00_pipeline_lengkap.ipynb`, yang sudah memuat seluruh kode, lalu **Run all**. Hasil disimpan di Google Drive
(`MyDrive/dl-paper/outputs/<kategori>/`). Aplikasi demo dapat dijalankan lokal dengan `cd app && python app.py`.

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
| `notebooks/` | Notebook 01–10, notebook gabungan `00_pipeline_lengkap`, `00b_rekonsiliasi`, `00c_kurva_latih`, dan catatan run selesai (`FINISHED RUN/`) |
| `app/` | Aplikasi demo Gradio yang di-*deploy* ke Hugging Face Spaces |
| `tools/`, `tests/` | Pembuat notebook gabungan, berkas aplikasi, grafik dan PDF laporan, serta uji *smoke* |
| `laporan/` | Laporan, referensi, dan arsip dokumen lama (lihat `laporan/README.md`) |
| `EXPERIMENTS.md` | Protokol eksperimen dan aturan yang dikunci di kode |
