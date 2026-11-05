"""Satu-satunya tempat mengubah konfigurasi untuk SEMUA notebook.

Penyimpanan
-----------
- **Di Google Colab**, Google Drive di-mount otomatis saat sel setup dijalankan. SEMUA data
  (unduhan mentah ``data/raw``, parquet, embedding, run, tabel, grafik) disimpan di
  ``HR_DRIVE_ROOT`` (bawaan ``/content/drive/MyDrive/dl-paper``). Setiap notebook Colab berjalan di
  runtime terpisah, jadi Drive adalah satu-satunya tempat notebook saling bertukar hasil.
  Jika Drive gagal di-mount, tidak bisa ditulisi, atau terputus di tengah jalan, kode berhenti
  dengan error, tidak diam-diam menulis ke disk instance.
- **Di luar Colab**, data disimpan di ``HR_ROOT`` jika diatur, atau di root repo.
- Cache model Hugging Face (``~/.cache/huggingface``) tetap di instance dan diunduh ulang per sesi.

Variabel lingkungan opsional: ``HR_DRIVE_ROOT`` (folder di Drive), ``HR_MIN_FREE_GB`` (batas ruang
kosong minimum di Drive, bawaan 10), ``HR_SMOKE=1`` (uji cepat dengan data sintetis, selalu lokal).
"""
import importlib.util
import os
import shutil
import uuid
from pathlib import Path

from hr.config import Config, smoke_config

ROOT = Path(__file__).resolve().parents[1]
SMOKE = os.environ.get("HR_SMOKE") == "1"     # 1 = uji cepat dengan data sintetis dan model mini
try:
    IN_COLAB = importlib.util.find_spec("google.colab") is not None
except ModuleNotFoundError:                   # paket "google" sama sekali tidak terpasang
    IN_COLAB = False
DRIVE_MOUNT = "/content/drive"


def connect_drive() -> Path:
    """Mount Google Drive, pastikan folder proyek bisa ditulis dan dibaca, lalu kembalikan path-nya."""
    from google.colab import drive
    if not os.path.ismount(DRIVE_MOUNT):
        drive.mount(DRIVE_MOUNT)
    if not os.path.ismount(DRIVE_MOUNT):
        raise RuntimeError(f"Google Drive gagal di-mount di {DRIVE_MOUNT}.")
    root = Path(os.environ.get("HR_DRIVE_ROOT", f"{DRIVE_MOUNT}/MyDrive/dl-paper"))
    if not str(root.resolve()).startswith(DRIVE_MOUNT + "/"):
        raise RuntimeError(f"HR_DRIVE_ROOT={root} berada di luar Google Drive ({DRIVE_MOUNT}).")
    if not root.parent.is_dir():
        raise RuntimeError(f"Folder induk {root.parent} tidak ada di Drive. Periksa HR_DRIVE_ROOT.")
    root.mkdir(parents=True, exist_ok=True)

    probe = root / f".tulis_uji_{uuid.uuid4().hex}"
    token = uuid.uuid4().hex
    probe.write_text(token)
    ok = probe.read_text() == token
    probe.unlink()
    if not ok:
        raise RuntimeError(f"Uji tulis-baca di {root} gagal.")

    usage = shutil.disk_usage(root)
    if usage.total > 0:
        free_gb, min_gb = usage.free / 1e9, float(os.environ.get("HR_MIN_FREE_GB", "10"))
        print(f"Google Drive: {free_gb:.1f} GB kosong dari {usage.total / 1e9:.1f} GB")
        if free_gb < min_gb:
            raise RuntimeError(
                f"Ruang kosong Drive {free_gb:.1f} GB < {min_gb:.0f} GB. Unggahan Drive yang melebihi kuota "
                "bisa gagal tanpa error, jadi kosongkan Drive dulu (atau atur HR_MIN_FREE_GB jika yakin cukup).")
    else:
        print("Google Drive: ruang kosong tidak bisa dibaca, pemeriksaan kuota dilewati.")
    return root


def finish() -> None:
    """Panggil di akhir notebook. Di Colab, memaksa semua tulisan tersinkron ke Drive sebelum runtime
    ditutup. Setelah ini akses path apa pun akan gagal keras sampai sel setup dijalankan ulang."""
    if IN_COLAB and not SMOKE and os.path.ismount(DRIVE_MOUNT):
        from google.colab import drive
        drive.flush_and_unmount()
        print("Semua hasil sudah tersinkron ke Google Drive.")
    else:
        print("Selesai. Hasil ada di", cfg.root)


_settings = dict(
    category="Video_Games",   # KEPUTUSAN KELOMPOK: kategori Amazon Reviews 2023 yang dipakai
    run_priority=3,           # 1 = wajib saja, 2 = + penting, 3 = semua eksperimen Bab III
    main_scale="E3",          # skala untuk baseline, ablasi, dan strategi target
    main_target="T1",         # target perbandingan utama
)

if SMOKE:
    cfg = smoke_config(ROOT)
elif IN_COLAB:
    cfg = Config(root=connect_drive(), storage_mount=DRIVE_MOUNT, **_settings)
else:
    cfg = Config(**_settings)   # root = HR_ROOT atau root repo

print("penyimpanan:", cfg.root, "(Google Drive)" if cfg.storage_mount else "(disk lokal)")
