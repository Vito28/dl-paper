"""Menjalankan seluruh tahap dalam satu notebook (``00_pipeline_lengkap.ipynb``).

Setiap sel kode tahap diawali ``%%tahap N``. Magic ini:
- melewati sel jika tahap N tidak dipilih (``mulai_dari_tahap`` dan kotak centang tahap opsional);
- saat berpindah ke tahap baru, menghapus variabel tahap sebelumnya dan cache keluaran agar RAM
  tidak menumpuk. Notebook 01-10 aslinya berjalan di kernel terpisah, dan setiap tahap memuat
  ulang masukannya dari penyimpanan, jadi tidak ada tahap yang bergantung pada variabel tahap lain;
- jika sel gagal, menaikkan error sehingga "Run all" berhenti di sel itu, tidak lanjut diam-diam.
"""
from __future__ import annotations

import gc
import sys


def setup(start: int, optional: dict[int, bool] | None = None) -> None:
    """Daftarkan magic ``%%tahap``. Panggil di baris TERAKHIR sel pengaturan: semua nama yang sudah
    ada saat itu (cfg, np, pd, ...) dipertahankan ketika berpindah tahap."""
    from IPython import get_ipython
    ip = get_ipython()
    if ip is None:
        raise RuntimeError("hr.stages hanya bisa dipakai di dalam notebook.")
    optional = optional or {}
    keep = set(ip.user_ns) | {"_", "__", "___"}
    state = {"stage": None}

    def selected(n: int) -> bool:
        return n >= start and optional.get(n, True)

    def clean() -> None:
        ns = ip.user_ns
        for name in [k for k in ns if k not in keep]:
            del ns[name]
        ip.run_line_magic("reset", "-f out")       # cache Out[] menahan DataFrame besar
        gc.collect()
        if "torch" in sys.modules and sys.modules["torch"].cuda.is_available():
            sys.modules["torch"].cuda.empty_cache()

    def tahap(line: str, cell: str) -> None:
        n = int(line.split()[0])
        if not selected(n):
            print(f"[tahap {n:02d} dilewati]")
            return
        if state["stage"] != n:
            clean()
            state["stage"] = n
        res = ip.run_cell(cell)
        if not res.success:
            raise RuntimeError(f"Tahap {n:02d} gagal (lihat error di atas). Perbaiki penyebabnya lalu jalankan "
                               "ulang dari sel ini, atau atur mulai_dari_tahap dan jalankan semua.") from None

    ip.register_magic_function(tahap, magic_kind="cell", magic_name="tahap")
    chosen = [n for n in range(1, 11) if selected(n)]
    print("tahap yang akan dijalankan:", chosen)
