---
title: Pemeringkatan Ulasan Helpful
sdk: gradio
sdk_version: 6.31.0
app_file: app.py
pinned: false
---

# Aplikasi Demo: Pemeringkatan Ulasan Berdasarkan Kebermanfaatan

Aplikasi Gradio untuk model U (BLaIR-RoBERTa-base yang dibekukan + 5 fitur terstruktur + MLP RankNet). Folder ini
mandiri dan dapat diunggah langsung sebagai Hugging Face Space.

## Isi folder

| Berkas | Keterangan |
|---|---|
| `app.py` | Antarmuka Gradio |
| `inference.py` | Langkah inferensi (pembersihan teks, fitur, embedding, skor) |
| `hr_inti.py` | **Dibangun otomatis** dari `src/hr` oleh `tools/build_app.py`. Jangan diedit. |
| `artefak/konfigurasi.json` | **Dibangun otomatis** dari hasil run (encoder, arsitektur, standardisasi) |
| `artefak/model_U.pt` | Bobot MLP U, disalin dari Drive (`outputs/Video_Games/runs/U_E3_T1_s42/model.pt`) |
| `requirements.txt` | Library dengan versi yang sama dengan run Colab |

Encoder BLaIR (`hyp1231/blair-roberta-base`, sekitar 500 MB) diunduh dari Hugging Face Hub saat aplikasi pertama
kali dijalankan.

## Menjalankan secara lokal

```bash
cd app
pip install -r requirements.txt
python app.py
```

## Memperbarui setelah kode atau hasil run berubah

```bash
python tools/build_app.py          # dari akar repo, menulis ulang hr_inti.py dan konfigurasi.json
python tools/build_app.py --check  # gagal jika berkas turunan usang
python -m tests.app_smoke          # skor aplikasi harus sama dengan skor pipeline pada data smoke
```

## Deploy ke Hugging Face Spaces

1. Buat Space baru dengan SDK Gradio.
2. Unggah seluruh isi folder `app/` (termasuk `artefak/`) ke repo Space.
3. Space membaca header di atas berkas ini, memasang `requirements.txt`, lalu menjalankan `app.py`.
