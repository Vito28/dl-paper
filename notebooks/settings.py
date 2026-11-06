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

Pemakaian
---------
- Notebook 01-10: ``from settings import cfg`` memakai ``DEFAULTS`` di bawah.
- ``00_pipeline_lengkap.ipynb``: formulir Colab memanggil ``configure(...)`` dengan nilai pilihan.

Pengaturan disimpan di ``outputs/<kategori>/config.json`` saat pertama dipakai. Jika kemudian
pengaturan berubah (selain ``run_priority``) sementara hasil lama masih ada, ``configure`` berhenti
dengan error agar hasil dari dua pengaturan berbeda tidak tercampur diam-diam.
"""
import importlib.util
import json
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


def connect_drive(drive_root: str | None = None) -> Path:
    """Mount Google Drive, pastikan folder proyek bisa ditulis dan dibaca, lalu kembalikan path-nya."""
    from google.colab import drive
    if not os.path.ismount(DRIVE_MOUNT):
        drive.mount(DRIVE_MOUNT)
    if not os.path.ismount(DRIVE_MOUNT):
        raise RuntimeError(f"Google Drive gagal di-mount di {DRIVE_MOUNT}.")
    root = Path(drive_root or os.environ.get("HR_DRIVE_ROOT", f"{DRIVE_MOUNT}/MyDrive/dl-paper"))
    if not str(root.resolve()).startswith(DRIVE_MOUNT + "/"):
        raise RuntimeError(f"Folder {root} berada di luar Google Drive ({DRIVE_MOUNT}).")
    if not root.parent.is_dir():
        raise RuntimeError(f"Folder induk {root.parent} tidak ada di Drive. Periksa folder Drive yang dipilih.")
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


# Pengaturan bawaan untuk notebook 01-10. 00_pipeline_lengkap.ipynb mengubahnya lewat formulir Colab.
DEFAULTS = dict(
    category="Video_Games",   # KEPUTUSAN KELOMPOK: kategori Amazon Reviews 2023 yang dipakai
    run_priority=3,           # 1 = wajib saja, 2 = + penting, 3 = semua eksperimen Bab III
    main_scale="E3",          # skala untuk baseline, ablasi, dan strategi target
    main_target="T1",         # target perbandingan utama
)
_NOT_COMPARED = {"root", "storage_mount", "run_priority"}   # boleh berubah tanpa membatalkan hasil lama
_cfg: Config | None = None


def _check_saved(c: Config) -> None:
    """Simpan pengaturan saat pertama dipakai, atau gagal keras jika berbeda dari pengaturan yang
    menghasilkan keluaran yang sudah ada."""
    p = c.out_dir / "config.json"
    if not p.exists():
        c.save()
        return
    old, new = json.loads(p.read_text()), c.as_json()
    diff = {k: (old.get(k), v) for k, v in new.items() if k not in _NOT_COMPARED and old.get(k) != v}
    if diff:
        lines = "\n".join(f"  {k}: tersimpan={a!r}, sekarang={b!r}" for k, (a, b) in diff.items())
        raise RuntimeError(
            f"Pengaturan berbeda dari yang menghasilkan keluaran di {c.out_dir}:\n{lines}\n"
            "Kembalikan pengaturan tersebut, pilih folder Drive lain, atau hapus folder itu untuk mulai dari awal.")


def configure(drive_root: str | None = None, **overrides) -> Config:
    """Bangun konfigurasi dari DEFAULTS + ``overrides`` (nama field ``Config``) dan sambungkan penyimpanan."""
    global _cfg
    if SMOKE:
        c = smoke_config(ROOT)                     # uji cepat selalu memakai pengaturan mini yang tetap
    else:
        unknown = set(overrides) - set(Config.__dataclass_fields__)
        if unknown:
            raise TypeError(f"Pengaturan tidak dikenal: {sorted(unknown)}")
        kw = {**DEFAULTS, **overrides}
        if IN_COLAB:
            c = Config(root=connect_drive(drive_root), storage_mount=DRIVE_MOUNT, **kw)
        else:
            c = Config(**kw)                       # root = HR_ROOT atau root repo
    _check_saved(c)
    _cfg = c
    print("penyimpanan:", c.root, "(Google Drive)" if c.storage_mount else "(disk lokal)")
    return c


def configure_saved(category: str, drive_root: str | None = None) -> Config:
    """Bangun konfigurasi dari ``outputs/<category>/config.json`` run yang sudah ada (dipakai
    ``00b_rekonsiliasi.ipynb``), sehingga pengaturannya pasti sama dengan yang menghasilkan keluaran."""
    global _cfg
    if SMOKE:
        c = smoke_config(ROOT)
    else:
        root = connect_drive(drive_root) if IN_COLAB else Config().root
        p = Path(root) / "outputs" / category / "config.json"
        if not p.exists():
            raise FileNotFoundError(f"{p} tidak ada. Periksa kategori dan folder Drive, atau jalankan pipeline dulu.")
        saved = json.loads(p.read_text())
        kw = {k: v for k, v in saved.items() if k not in ("root", "storage_mount")}
        for k, f in Config.__dataclass_fields__.items():
            if k in kw and isinstance(f.default, tuple):
                kw[k] = tuple(kw[k])               # config.json menyimpan tuple sebagai list
        c = Config(root=Path(root), storage_mount=DRIVE_MOUNT if IN_COLAB else None, **kw)
    _check_saved(c)                                # tetap gagal keras jika ada field yang tidak cocok
    _cfg = c
    print("penyimpanan:", c.root, "(Google Drive)" if c.storage_mount else "(disk lokal)")
    return c


def __getattr__(name):
    # ``from settings import cfg`` di notebook 01-10 membangun konfigurasi bawaan saat pertama diminta.
    if name == "cfg":
        return _cfg if _cfg is not None else configure()
    raise AttributeError(name)


def finish() -> None:
    """Panggil di akhir notebook. Di Colab, memaksa semua tulisan tersinkron ke Drive sebelum runtime
    ditutup. Setelah ini akses path apa pun akan gagal keras sampai sel pengaturan dijalankan ulang."""
    if IN_COLAB and not SMOKE and os.path.ismount(DRIVE_MOUNT):
        from google.colab import drive
        drive.flush_and_unmount()
        print("Semua hasil sudah tersinkron ke Google Drive.")
    else:
        print("Selesai. Hasil ada di", _cfg.root if _cfg is not None else "(belum dikonfigurasi)")
