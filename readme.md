# DL PAPER

Kode eksperimen untuk paper **Review Helpfulness Ranking Using BLaIR Embeddings and MLP on the Amazon Reviews 2023 Dataset**
(target publikasi JuTISI, Sinta 3).

Penelitian ini mengurutkan ulasan dalam satu produk berdasarkan seberapa membantu ulasan tersebut, dengan `helpful_vote`
sebagai label lemah. Model utama memakai embedding BLaIR-RoBERTa-base ditambah fitur terstruktur, lalu dinilai oleh MLP
yang dilatih dengan loss *pairwise* RankNet. Model ini dibandingkan dengan baseline B0–B5 pada data Amazon Reviews 2023
yang dibagi per produk, dan dievaluasi dengan NDCG@5/10, Spearman, dan MAP. Penelitian ini juga menganalisis pengaruh
usia ulasan terhadap jumlah *helpful votes*.

- Naskah, review, dan referensi ada di branch `documents`.
- Branch `main` berisi kode eksperimen untuk Bab IV.

```
notebooks/        10 notebook berurutan (01–08 wajib, 09–10 opsional) + settings.py
src/hr/           modul bersama: data, split, target, embedding, pasangan, model, loss, training, metrik, statistik, grafik
tests/            uji cepat dengan data sintetis
EXPERIMENTS.md    protokol eksperimen, keluaran untuk Bab IV, dan catatan keselarasan dengan Bab III
```

Mulai dari `EXPERIMENTS.md`.
