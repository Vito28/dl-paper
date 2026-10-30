"""Satu-satunya tempat mengubah konfigurasi untuk SEMUA notebook.

Di Google Colab, simpan data dan hasil di Google Drive agar tidak hilang saat sesi berakhir:
    from google.colab import drive; drive.mount("/content/drive")
    import os; os.environ["HR_ROOT"] = "/content/drive/MyDrive/dl-paper"
Jalankan dua baris itu SEBELUM sel setup notebook.
"""
import os
from pathlib import Path

from hr.config import Config, smoke_config

ROOT = Path(__file__).resolve().parents[1]
SMOKE = os.environ.get("HR_SMOKE") == "1"     # 1 = uji cepat dengan data sintetis dan model mini

cfg = smoke_config(ROOT) if SMOKE else Config(
    category="Video_Games",   # KEPUTUSAN KELOMPOK: kategori Amazon Reviews 2023 yang dipakai
    run_priority=3,           # 1 = wajib saja, 2 = + penting, 3 = semua eksperimen Bab III
    main_scale="E3",          # skala untuk baseline, ablasi, dan strategi target
    main_target="T1",         # target perbandingan utama
)
