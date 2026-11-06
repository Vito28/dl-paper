"""Bangun notebooks/00_pipeline_lengkap.ipynb dari notebook 01-10, dan notebooks/00b_rekonsiliasi.ipynb.

Notebook 01-10 adalah sumbernya, dan kode src/hr + notebooks/settings.py ditanam di sel pertama
(repo privat, jadi Colab tidak bisa meng-clone). Jangan mengedit 00_pipeline_lengkap.ipynb secara
langsung: ubah notebook aslinya atau kodenya, lalu jalankan ulang skrip ini.

    python tools/build_merged_notebook.py           # tulis ulang kedua notebook
    python tools/build_merged_notebook.py --check   # gagal jika salah satunya sudah usang
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NB_DIR = REPO / "notebooks"
OUT = NB_DIR / "00_pipeline_lengkap.ipynb"
OUT_REKON = NB_DIR / "00b_rekonsiliasi.ipynb"

# Ukuran berkas User Reviews (GB) menurut repositori Hugging Face McAuley-Lab/Amazon-Reviews-2023.
CATEGORIES = {
    "All_Beauty": 0.33, "Amazon_Fashion": 1.05, "Appliances": 0.93, "Arts_Crafts_and_Sewing": 3.95,
    "Automotive": 8.73, "Baby_Products": 2.95, "Beauty_and_Personal_Care": 11.02, "Books": 20.12,
    "CDs_and_Vinyl": 3.29, "Cell_Phones_and_Accessories": 9.34, "Clothing_Shoes_and_Jewelry": 27.81,
    "Digital_Music": 0.08, "Electronics": 22.62, "Gift_Cards": 0.05, "Grocery_and_Gourmet_Food": 5.97,
    "Handmade_Products": 0.29, "Health_and_Household": 11.40, "Health_and_Personal_Care": 0.23,
    "Home_and_Kitchen": 31.41, "Industrial_and_Scientific": 2.35, "Kindle_Store": 15.80,
    "Magazine_Subscriptions": 0.03, "Movies_and_TV": 8.39, "Musical_Instruments": 1.56,
    "Office_Products": 5.78, "Patio_Lawn_and_Garden": 7.75, "Pet_Supplies": 8.35, "Software": 1.87,
    "Sports_and_Outdoors": 9.26, "Subscription_Boxes": 0.01, "Tools_and_Home_Improvement": 12.78,
    "Toys_and_Games": 7.32, "Unknown": 29.93, "Video_Games": 2.68,
}

INTRO = """# Pipeline Lengkap · Review Helpfulness Ranking (BLaIR + MLP)

Satu notebook berisi seluruh tahap 01–10 (dibangun otomatis dari notebook 01–10 oleh
`tools/build_merged_notebook.py`, jangan diedit langsung).

**Cara pakai di Google Colab**
1. *Runtime → Change runtime type → GPU* (tahap 04–06 dan 09 butuh GPU).
2. Isi formulir **Pengaturan** di bawah.
3. *Runtime → Run all*. Izinkan akses Google Drive saat diminta.

**Penyimpanan.** Semua data dan hasil, termasuk unduhan mentah, disimpan di folder Drive yang dipilih
(bawaan `MyDrive/dl-paper`), bukan di instance. Jika Drive gagal di-mount atau terputus, notebook berhenti
dengan error.

**Melanjutkan setelah runtime terputus.** Setiap tahap memuat masukannya dari Drive, dan run yang sudah
selesai tidak diulang. Atur `mulai_dari_tahap` ke tahap yang terputus, lalu *Run all* lagi. Ekstraksi
embedding (tahap 04) melanjutkan dari titik terakhir. Jangan mengubah pengaturan lain di tengah jalan:
jika berbeda dari pengaturan yang menghasilkan keluaran lama, notebook berhenti dengan error.

**Jika satu tahap gagal**, *Run all* berhenti di sel itu. Pesan error menjelaskan penyebabnya.

**Ukuran berkas per kategori (GB):** """ + " · ".join(
    f"{k} {str(round(v, 1)).replace('.', ',')}" for k, v in CATEGORIES.items()) + """.
Berkas besar bisa melebihi RAM Colab. Untuk kategori besar, kecilkan `ambil_sebagian_produk` (produk diambil
utuh secara acak). Skala E5 butuh sekitar 1 juta ulasan latih setelah batas 200 ulasan per produk, jadi
kategori kecil butuh skala yang lebih kecil."""

# Berkas kode yang ditanam di notebook gabungan, sehingga Colab tidak perlu meng-clone repo (repo privat).
EMBED = ["requirements.txt", "notebooks/settings.py"] + sorted(
    str(p.relative_to(REPO)) for p in (REPO / "src" / "hr").glob("*.py"))


def bootstrap_source() -> str:
    files = {rel: (REPO / rel).read_text(encoding="utf-8") for rel in EMBED}
    digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()[:12]
    body = "\n".join(f"    {rel!r}: {text!r}," for rel, text in files.items())
    return f"""#@title 1 · Siapkan kode (tertanam di notebook ini, tanpa clone repo)
# Kode src/hr dan notebooks/settings.py ditanam di sel ini oleh tools/build_merged_notebook.py
# (versi {digest}). Di Colab, kode ditulis ke /content/hr_kode setiap sesi. Data TIDAK disimpan di sana.
import os, sys, json, shutil, hashlib, subprocess, tempfile
from pathlib import Path
_KODE = {{
{body}
}}
_VERSI = {digest!r}
assert hashlib.sha256(json.dumps(_KODE, sort_keys=True).encode()).hexdigest()[:12] == _VERSI, "kode tertanam rusak"
try:
    import google.colab  # noqa: F401
    IN_COLAB = True
except ImportError:
    IN_COLAB = False
if IN_COLAB or os.environ.get("HR_EMBEDDED") == "1":
    ROOT = Path(os.environ.get("HR_KODE_DIR") or
                ("/content/hr_kode" if IN_COLAB else tempfile.mkdtemp(prefix="hr_kode_"))).resolve()
    # Saat sel ini dijalankan ulang, direktori kerja kernel masih di dalam ROOT (os.chdir di bawah).
    # Pindah keluar dulu sebelum ROOT dihapus, agar pip tidak berjalan di direktori yang sudah tiada.
    ROOT.parent.mkdir(parents=True, exist_ok=True)
    os.chdir(ROOT.parent)
    shutil.rmtree(ROOT, ignore_errors=True)            # buang kode sesi sebelumnya
    for rel, text in _KODE.items():
        (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / rel).write_text(text, encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(ROOT / "requirements.txt")],
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        raise RuntimeError("pip install gagal:\\n" + (r.stderr or r.stdout)[-3000:])
    os.chdir(ROOT / "notebooks")
    sumber = "tertanam"
else:                                                  # di luar Colab: pakai kode repo tempat notebook berada
    ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
    sumber = "repo lokal"
for _m in [m for m in sys.modules if m in ("hr", "settings") or m.startswith("hr.")]:
    del sys.modules[_m]                                # sel dijalankan ulang: muat kode baru, bukan versi lama
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "notebooks")]
del _KODE
print("kode:", ROOT, f"({{sumber}}, versi {{_VERSI}})")"""


cat_list = ", ".join(f'"{k}"' for k in CATEGORIES)
FORM = f'''#@title 2 · Pengaturan {{ display-mode: "form" }}
#@markdown ### Data
kategori = "Video_Games"  #@param [{cat_list}] {{allow-input: true}}
ambil_sebagian_produk = 1.0  #@param {{type:"slider", min:0.05, max:1.0, step:0.05}}
#@markdown ### Eksperimen
#@markdown `run_priority`: 1 = wajib saja, 2 = + penting, 3 = semua eksperimen Bab III
run_priority = 3  #@param [1, 2, 3] {{type:"raw"}}
skala_utama = "E3"  #@param ["E1", "E2", "E3", "E4", "E5"]
target_utama = "T1"  #@param ["T1", "T3"]
#@markdown Jumlah ulasan latih untuk skala E1–E5 (5 angka naik, dipisah koma):
skala_E1_sampai_E5 = "100000, 250000, 500000, 750000, 1000000"  #@param {{type:"string"}}
seeds = "42, 43, 44"  #@param {{type:"string"}}
max_epochs = 30  #@param {{type:"integer"}}
patience = 3  #@param {{type:"integer"}}
batas_ulasan_validasi_uji = 200000  #@param {{type:"integer"}}
#@markdown ### Tahap yang dijalankan
mulai_dari_tahap = 1  #@param [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] {{type:"raw"}}
jalankan_09_finetuning = False  #@param {{type:"boolean"}}
jalankan_10_label_manusia = False  #@param {{type:"boolean"}}
#@markdown ### Penyimpanan
folder_drive = "/content/drive/MyDrive/dl-paper"  #@param {{type:"string"}}

import json
import numpy as np, pandas as pd
pd.set_option("display.width", 160)


def _ints(text, name):
    try:
        return [int(x) for x in str(text).replace(" ", "").split(",") if x]
    except ValueError:
        raise ValueError(f"{{name}} harus berisi bilangan bulat dipisah koma, bukan {{text!r}}") from None


_skala = _ints(skala_E1_sampai_E5, "skala_E1_sampai_E5")
if len(_skala) != 5 or any(a >= b for a, b in zip(_skala, _skala[1:])) or _skala[0] <= 0:
    raise ValueError(f"skala_E1_sampai_E5 harus 5 angka positif yang naik, bukan {{_skala}}")
_seeds = _ints(seeds, "seeds")
if not _seeds or len(set(_seeds)) != len(_seeds):
    raise ValueError(f"seeds harus berisi minimal satu angka tanpa duplikat, bukan {{_seeds}}")
if max_epochs < 1 or patience < 1 or batas_ulasan_validasi_uji < 1000:
    raise ValueError("max_epochs dan patience minimal 1, batas_ulasan_validasi_uji minimal 1000")

import settings
from settings import SMOKE, finish
cfg = settings.configure(
    drive_root=folder_drive, category=kategori, product_sample_rate=float(ambil_sebagian_produk),
    run_priority=int(run_priority), main_scale=skala_utama, main_target=target_utama,
    scales=dict(zip(["E1", "E2", "E3", "E4", "E5"], _skala)), seeds=tuple(_seeds),
    max_epochs=int(max_epochs), patience=int(patience), max_eval_reviews=int(batas_ulasan_validasi_uji))
print("kategori:", cfg.category, "| output:", cfg.out_dir, "| SMOKE:", SMOKE)
print("eksperimen:", cfg.experiments_to_run(), "| skala:", cfg.scales_to_run(), "| target:", cfg.targets_to_run())
import torch
if not torch.cuda.is_available() and not SMOKE:
    print("PERINGATAN: tidak ada GPU. Tahap 04-06 dan 09 akan sangat lambat. Runtime → Change runtime type → GPU.")
del torch

from hr import stages
stages.setup(start=int(mulai_dari_tahap), optional={{9: bool(jalankan_09_finetuning), 10: bool(jalankan_10_label_manusia)}})'''

OUTRO_MD = "## Selesai\nMemastikan semua hasil sudah tersinkron ke Google Drive sebelum runtime ditutup."


def _src(cell) -> str:
    s = cell["source"]
    return "".join(s) if isinstance(s, list) else s


def _demote(md: str) -> str:
    out, fence = [], False
    for line in md.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
        out.append("#" + line if not fence and re.match(r"#+ ", line) else line)
    return "\n".join(out)


def _md(src, cid):
    return {"cell_type": "markdown", "metadata": {}, "source": src, "id": cid}


def _code(src, cid, form=False):
    meta = {"cellView": "form"} if form else {}
    return {"cell_type": "code", "metadata": meta, "execution_count": None, "outputs": [], "source": src, "id": cid}


def build() -> dict:
    cells = [_md(INTRO, "intro"), _code(bootstrap_source(), "bootstrap", form=True), _code(FORM, "pengaturan", form=True)]
    sources = sorted(p for p in NB_DIR.glob("[0-9][0-9]_*.ipynb") if p != OUT)
    assert [p.name[:2] for p in sources] == [f"{i:02d}" for i in range(1, 11)], [p.name for p in sources]
    meta = None
    for p in sources:
        n = int(p.name[:2])
        nb = json.loads(p.read_text())
        meta = meta or nb["metadata"]
        c = nb["cells"]
        # struktur yang diharapkan: judul, petunjuk Colab, setup, ..., markdown + finish()
        assert "Google Colab" in _src(c[1]), p.name
        assert "from settings import" in _src(c[2]), p.name
        assert _src(c[-1]).strip() == "finish()", p.name
        body = c[3:-2]
        cells.append(_md(_demote(_src(c[0])), f"t{n:02d}c00"))
        for i, cell in enumerate(body, start=3):
            cid = f"t{n:02d}c{i:02d}"
            if cell["cell_type"] == "markdown":
                cells.append(_md(_demote(_src(cell)), cid))
            else:
                cells.append(_code(f"%%tahap {n}\n" + _src(cell), cid))
    cells += [_md(OUTRO_MD, "selesai_md"), _code("finish()", "selesai")]
    meta = {**meta, "accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4", "toc_visible": True}}
    return {"cells": cells, "metadata": meta, "nbformat": 4, "nbformat_minor": 5}


REKON_INTRO = """# Rekonsiliasi Hasil Run Lama

Memperbarui keluaran run `00_pipeline_lengkap.ipynb` yang sudah selesai agar sama dengan kode versi
terbaru, **tanpa menjalankan ulang pipeline** (dibangun otomatis oleh `tools/build_merged_notebook.py`,
jangan diedit langsung). Aman dijalankan berulang kali. Berkas yang diubah dicadangkan sekali sebagai
`<nama>.sebelum_rekonsiliasi.<ekstensi>` di folder yang sama.

Perbaikan yang diterapkan:
1. **`age_model.json`.** `deviance_reduction_share` dihapus karena salah (deviance model dengan dan tanpa usia
   dihitung dengan dispersi κ yang berbeda, jadi selisihnya tidak bermakna dan bisa negatif). Diganti
   `loglik_gain_share` = 1 − LL_dengan_usia / LL_tanpa_usia, dihitung dari log-likelihood yang sudah tersimpan.
2. **Pemilihan basis usia** sekarang memakai log-likelihood validasi, bukan deviance (alasan yang sama).
   Notebook ini menghitung ulang pemilihannya. Jika basis terpilih **sama**, target T3 dan semua hasil tetap
   berlaku dan hanya `tables/age_pemilihan_basis.csv` yang diperbarui. Jika **berbeda**, notebook berhenti
   dan menjelaskan tahap yang harus dijalankan ulang.
3. **IK kurva usia** (`tables/age_kurva.csv`). Bootstrap lama mengambil ulang subset sekitar 300 ribu ulasan
   dan memindahkan knot spline di setiap ulangan, sehingga IK tidak berpusat pada kurva yang dilaporkan
   (sebagian titik berada di luar IK-nya sendiri). Sekarang bootstrap memakai seluruh data latih dan knot
   tetap. Kurva (estimasi titik) tidak berubah dan diperiksa sama dengan yang lama. Jika tabel sudah
   dibuat dengan bootstrap baru, langkah ini tidak diulang.
4. **Skor validasi B0** ditambahkan ke `result.json` B0, lalu `tables/validasi_baseline.csv` (hanya B0–B5 dan
   U, tanpa ablasi) dan `tables/validasi_semua.csv` dibuat ulang (sebelumnya B0 tampil NaN).
5. **Urutan acak R0** sebagai batas bawah: `tables/uji_acak.csv` baru, dan kolom R0 ditambahkan ke
   `tables/uji_per_ukuran_produk.csv` (kolom model U diperiksa sama dengan yang lama).
6. **Grafik** `age_kurva.png`, `usia.png` (sumbu y logaritmik), `uji_baseline.png` (dengan R0), dan
   `uji_ukuran_produk.png` (dengan R0) digambar ulang.
7. **Konsistensi per seed** ditambahkan ke `tables/uji_selisih_berpasangan.csv` (kolom `selisih_per_seed`,
   `seed_searah`, `n_pasangan_seed`, `searah_semua_seed`). Selisih gabungan, IK, p-value Holm, dan
   keputusan `lebih_baik` dihitung ulang dan diperiksa sama dengan tabel lama sebelum kolom baru ditulis.

Angka hasil uji yang sudah ada tidak berubah. Langkah 3 butuh GPU (sekitar 10–20 menit, hanya pada
rekonsiliasi pertama).

**Cara pakai di Google Colab:** runtime GPU, isi kategori dan folder Drive yang sama dengan run lama,
lalu *Runtime → Run all*."""

REKON_FORM = f'''#@title 2 · Run yang direkonsiliasi {{ display-mode: "form" }}
kategori = "Video_Games"  #@param [{cat_list}] {{allow-input: true}}
folder_drive = "/content/drive/MyDrive/dl-paper"  #@param {{type:"string"}}

import json, shutil
import numpy as np, pandas as pd
pd.set_option("display.width", 160)
import settings
from settings import SMOKE, finish
cfg = settings.configure_saved(kategori, drive_root=folder_drive)   # pengaturan diambil dari config.json run lama
print("kategori:", cfg.category, "| output:", cfg.out_dir, "| SMOKE:", SMOKE)
from hr import targets, features, plots, experiment as X, report as R
from hr.train import evaluate_scores
from hr.config import BASELINE_CODES
T = lambda name: cfg.path("tables", name)
F = lambda name: cfg.path("figures", name)
diubah = []


def cadangkan(p):
    """Salin berkas sekali sebelum diubah. Cadangan yang sudah ada tidak ditimpa (isinya versi asli)."""
    b = p.with_name(p.stem + ".sebelum_rekonsiliasi" + p.suffix)
    if p.exists() and not b.exists():
        shutil.copy2(p, b)
    diubah.append(p.name)'''

REKON_AGE = '''#@title 3 · age_model.json: ganti deviance_reduction_share dengan loglik_gain_share
p = cfg.path("age_model.json")
summ = json.loads(p.read_text())
stats = targets.age_effect_stats(summ["loglik_full"], summ["loglik_noage"], summ["df"])
if not np.isclose(stats["lr_stat"], summ["lr_stat"], rtol=1e-9):
    raise RuntimeError(f"lr_stat tersimpan ({summ['lr_stat']}) tidak cocok dengan log-likelihood tersimpan. "
                       "age_model.json tidak konsisten. Jalankan ulang tahap 03.")
# urutan kunci sama dengan keluaran tahap 03 versi baru
fixed = {"loglik_full": summ["loglik_full"], "loglik_noage": summ["loglik_noage"], **stats,
         "deviance_full": summ["deviance_full"], "deviance_noage": summ["deviance_noage"],
         "kappa_full": summ["kappa_full"], "basis": summ["basis"], "beta": summ["beta"]}
if fixed != summ:
    cadangkan(p)
    p.write_text(json.dumps(fixed, indent=2, default=str))
    print("diperbarui:", p)
else:
    print("sudah sesuai, tidak diubah:", p)
pd.Series(fixed)'''

REKON_BASIS = '''#@title 4 · Pemilihan basis usia dengan log-likelihood validasi
largest = list(cfg.scales)[-1]
cols = sorted({"split", f"in_{largest}", "parent_asin", "helpful_vote", "log_age", *targets.COVARIATES})
df = pd.read_parquet(cfg.path("reviews_split.parquet"), columns=cols)
tr = df[(df.split == "train") & df[f"in_{largest}"]].reset_index(drop=True)   # sama dengan tahap 03
va = df[df.split == "val"].reset_index(drop=True)
del df
best_kind, basis_tab = targets.select_basis(tr, va, cfg.age_basis_grid)
del va                                          # tr dipakai lagi di sel berikutnya
p = cfg.path("tables", "age_pemilihan_basis.csv")
cadangkan(p)
basis_tab.to_csv(p, index=False)
display(basis_tab)
lama = json.loads(cfg.path("age_model.json").read_text())["basis"]
if str(best_kind) != str(lama):
    raise RuntimeError(
        f"Basis terpilih berubah: {lama} (run lama, dipilih dari deviance) menjadi {best_kind} (log-likelihood "
        "validasi). Target T3 harus dibentuk ulang: hapus folder runs/ yang namanya berisi '_T3_' lalu jalankan "
        "00_pipeline_lengkap.ipynb dengan pengaturan yang sama dan mulai_dari_tahap = 3. Embedding dan run T1/T2 "
        "dipakai ulang. Sel berikut tidak dijalankan.")
print(f"basis terpilih tetap {best_kind}: target T3 dan semua hasil yang bergantung padanya tetap berlaku.")'''

REKON_CURVE = '''#@title 5 · IK kurva usia: bootstrap pada seluruh data latih dengan knot tetap
am = json.loads(cfg.path("age_model.json").read_text())
full = targets.fit_age_model(tr, basis_kind=best_kind)          # model yang sama dengan tahap 03
if not np.isclose(full.loglik, am["loglik_full"], rtol=1e-4):
    raise RuntimeError(f"Fit ulang model usia memberi log-likelihood {full.loglik}, bukan {am['loglik_full']} "
                       "seperti di age_model.json. Data latih berubah sejak run lama. Jalankan ulang dari tahap 03.")
p = T("age_kurva.csv")
old = pd.read_csv(p)
ages = old["age_days"].to_numpy()                                # grid usia yang sama dengan run lama
if not np.allclose(targets.age_curve(full, ages), old["ratio"], rtol=1e-3):
    raise RuntimeError("Kurva usia hasil fit ulang berbeda dari age_kurva.csv. Jalankan ulang dari tahap 03.")
if "di_luar_ik" in old.columns:
    # sudah dibuat dengan bootstrap versi baru: jangan diulang, karena hasil GPU bisa sedikit berbeda
    curve_tab = old
    print("sudah sesuai, tidak diubah:", p)
else:
    boots = targets.bootstrap_age_curve(tr, full, ages, n_boot=cfg.age_bootstrap, seed=cfg.seed)
    curve_tab = targets.age_curve_table(full, boots, ages)
    cadangkan(p)
    curve_tab.to_csv(p, index=False)
    ax = plots.age_curve(curve_tab["age_days"], curve_tab["ratio"], curve_tab["lo"], curve_tab["hi"])
    cadangkan(F("age_kurva.png"))
    plots.save(ax.figure, F("age_kurva.png"))
    del boots
del tr, full
curve_tab.round(4)'''

REKON_B0 = '''#@title 6 · Skor validasi B0 dan tabel validasi
MS, TG = cfg.main_scale, cfg.main_target
run = X.run_id("B0", MS, TG, 0)
rp = cfg.out_dir / "runs" / run / "result.json"
meta = json.loads(rp.read_text())
b = X.load_bundle(cfg)
va = b.rows("val")
score = features.score_b0(va)
saved = X.load_pred(cfg, run, "val")
# skor dihitung ulang dengan kode yang sama, dan harus identik dengan prediksi B0 yang tersimpan
if not (np.array_equal(saved["rid"].to_numpy(), va["rid"].to_numpy())
        and np.allclose(saved["score"].to_numpy(), score)):
    raise RuntimeError(f"Skor B0 yang dihitung ulang berbeda dari {run}/pred_val.parquet. Data validasi berubah "
                       "sejak run lama. Jalankan ulang dari tahap 05.")
m = evaluate_scores(b.eval_set(va, np.zeros((len(va), 1)), TG), score, cfg.map_relevant_grade)[0]
if meta.get("best_val_ndcg@10") is None:
    cadangkan(rp)
    rp.write_text(json.dumps({**meta, "best_val_ndcg@10": m["ndcg@10"]}, indent=2, default=str))
    print("diperbarui:", rp)
elif not np.isclose(meta["best_val_ndcg@10"], m["ndcg@10"]):
    raise RuntimeError(f"best_val_ndcg@10 B0 tersimpan {meta['best_val_ndcg@10']} berbeda dari {m['ndcg@10']}.")
else:
    print("sudah sesuai, tidak diubah:", rp)
del va                                          # b dipakai lagi di sel berikutnya

for name, tab, kw in (("validasi_baseline.csv", X.validation_table(cfg, MS, TG, BASELINE_CODES), {}),
                      ("validasi_semua.csv", X.validation_table(cfg), {"index": False})):
    p = cfg.path("tables", name)
    cadangkan(p)
    tab.to_csv(p, **kw)
    print(name); display(tab)'''

REKON_R0 = '''#@title 7 · Urutan acak R0, tabel ukuran produk, dan grafik
groups = R.group_runs(X.results_table(cfg))
R.check_complete(cfg, groups)
te = b.rows("test")
N_PERM = R.R0_PERMUTATIONS if not SMOKE else 3                  # sama dengan notebook 07
pp_r0 = R.random_per_product(b, TG, n_perm=N_PERM, seed=cfg.seed)
r0_tab = R.random_table(pp_r0, N_PERM, cfg.eval_bootstrap)
cadangkan(T("uji_acak.csv"))
r0_tab.to_csv(T("uji_acak.csv"), index=False)
display(r0_tab[["code", "seeds", "ndcg@10", "ndcg@10_lo", "ndcg@10_hi", "ndcg@5", "spearman", "map"]].round(4))

pp_u = R.eval_config(b, groups[("U", MS, TG)])
size_tab = R.size_table(pp_u, pp_r0, te)
p = T("uji_per_ukuran_produk.csv")
old = pd.read_csv(p).set_index("kelompok")
cols = ["ndcg@10", "spearman", "ap"]
if not np.allclose(old[cols].to_numpy(), size_tab[cols].to_numpy(), atol=1e-4):
    raise RuntimeError("Metrik model U per ukuran produk berbeda dari tabel lama. Prediksi atau data uji berubah.")
cadangkan(p)
size_tab.to_csv(p)
display(size_tab)
del te, pp_r0, pp_u                             # b dan groups dipakai lagi di sel berikutnya

for name, make in (("uji_baseline.png", lambda: plots.baseline_figure(pd.read_csv(T("uji_baseline.csv")),
                                                                    pd.read_csv(T("uji_acak.csv"))).figure),
                   ("usia.png", lambda: plots.age_figure(pd.read_csv(T("age_kurva.csv")),
                                                         pd.read_csv(T("uji_per_kelompok_usia.csv")))),
                   ("uji_ukuran_produk.png", lambda: plots.size_figure(pd.read_csv(T("uji_per_ukuran_produk.csv"))).figure)):
    cadangkan(F(name))
    plots.save(make(), F(name))
    print("digambar ulang:", F(name))'''

REKON_SEED = '''#@title 8 · Konsistensi per seed pada perbandingan berpasangan (data uji)
keys = [(c, MS, TG) for c in BASELINE_CODES]
others = [k for k in keys if k[0] != "U"]
_, pps = R.comparison_table(b, groups, keys, TG, cfg.eval_bootstrap)
pair_tab = R.paired_table(pps, ("U", MS, TG), others, "ndcg@10", cfg.eval_bootstrap)
p = T("uji_selisih_berpasangan.csv")
old = pd.read_csv(p)
core = ["diff", "lo", "hi", "p", "p_holm"]
if (old["vs"].tolist() != pair_tab["vs"].tolist()
        or not np.allclose(old[core].to_numpy(), pair_tab[core].to_numpy(), rtol=0, atol=1e-9)
        or old["lebih_baik"].astype(bool).tolist() != pair_tab["lebih_baik"].tolist()):
    raise RuntimeError("Selisih berpasangan yang dihitung ulang berbeda dari uji_selisih_berpasangan.csv. "
                       "Prediksi atau data uji berubah sejak run lama. Jalankan ulang dari tahap 07.")
pair_tab = R.add_seed_consistency(pair_tab, b, groups, ("U", MS, TG), others, "ndcg@10", TG)
new_cols = ["selisih_per_seed", "seed_searah"]
if all(c in old.columns for c in new_cols) and all(old[c].tolist() == pair_tab[c].tolist() for c in new_cols):
    print("sudah sesuai, tidak diubah:", p)
else:
    cadangkan(p)
    pair_tab.to_csv(p, index=False)
    print("diperbarui:", p)
del b, pps
pair_tab[["vs", "diff", "lo", "hi", "p_holm", "lebih_baik", "selisih_per_seed", "seed_searah",
          "n_pasangan_seed", "searah_semua_seed"]].round(4)'''

REKON_END = '''#@title 9 · Selesai
print("berkas yang ditulis ulang (cadangan *.sebelum_rekonsiliasi.* di folder yang sama):", sorted(set(diubah)))
finish()'''


def build_reconcile() -> dict:
    meta = build()["metadata"]
    cells = [_md(REKON_INTRO, "intro"), _code(bootstrap_source(), "bootstrap", form=True),
             _code(REKON_FORM, "pengaturan", form=True), _code(REKON_AGE, "age_model", form=True),
             _code(REKON_BASIS, "basis_usia", form=True), _code(REKON_CURVE, "kurva_usia", form=True),
             _code(REKON_B0, "validasi_b0", form=True), _code(REKON_R0, "acak_r0", form=True),
             _code(REKON_SEED, "konsistensi_seed", form=True), _code(REKON_END, "selesai", form=True)]
    return {"cells": cells, "metadata": meta, "nbformat": 4, "nbformat_minor": 5}


def render(nb: dict) -> str:
    return json.dumps(nb, indent=1, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    targets = {OUT: build(), OUT_REKON: build_reconcile()}
    for path, nb in targets.items():
        text = render(nb)
        if "--check" in sys.argv:
            if not path.exists() or path.read_text() != text:
                sys.exit(f"{path.name} usang. Jalankan: python tools/build_merged_notebook.py")
            print(f"{path.name} sesuai dengan sumbernya")
        else:
            path.write_text(text)
            print("ditulis", path, f"({len(nb['cells'])} sel)")
