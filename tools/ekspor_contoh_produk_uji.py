"""Ekspor ulasan asli beberapa produk DATA UJI untuk contoh di aplikasi Gradio (app/artefak/contoh_produk_uji.json).

Jalankan di Google Colab (salin isi berkas ini ke satu sel), karena data lengkap ada di Google Drive. Produk dipilih
acak dengan seed tetap dari produk data uji yang memenuhi syarat, sehingga pilihannya dapat diulang dan tidak
dipilih-pilih. Skor model U yang tersimpan (pred_test.parquet run U_E3_T1_s42) ikut diekspor agar aplikasi dapat
diperiksa menghasilkan skor yang sama.
"""
import json
import pathlib

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

try:
    from google.colab import drive, files
    drive.mount("/content/drive")
    OUT = pathlib.Path("/content/drive/MyDrive/dl-paper/outputs/Video_Games")
except ImportError:
    files = None
    OUT = pathlib.Path("outputs/Video_Games")
RUN = "U_E3_T1_s42"
SEED = 42
JUMLAH = {"biasa": (3, 6, 12), "panjang": (1, 25, 40)}    # jenis: (jumlah produk, ulasan minimum, ulasan maksimum)

kolom = ["rid", "parent_asin", "title", "text", "rating", "verified_purchase", "helpful_vote"]
uji = pq.read_table(OUT / "reviews_split.parquet", columns=kolom + ["split"],
                    filters=[("split", "==", "test")]).to_pandas()
skor = pd.read_parquet(OUT / "runs" / RUN / "pred_test.parquet")
uji = uji.merge(skor, on="rid", how="inner")
assert uji["score"].notna().all() and len(uji) > 0

per = uji.groupby("parent_asin").agg(n=("rid", "size"), maks=("helpful_vote", "max"),
                                     ragam=("helpful_vote", "nunique"))
layak = per[(per["maks"] >= 3) & (per["ragam"] >= 3)]
rng = np.random.default_rng(SEED)
produk = []
for jenis, (k, lo, hi) in JUMLAH.items():
    calon = np.sort(layak[(layak["n"] >= lo) & (layak["n"] <= hi)].index.to_numpy())
    print(f"{jenis}: {len(calon)} produk uji memenuhi syarat, dipilih {k}")
    for pid in rng.choice(calon, size=k, replace=False):
        g = uji[uji["parent_asin"] == pid].sample(frac=1, random_state=SEED)   # acak, bukan urutan waktu
        produk.append({"parent_asin": str(pid), "jenis": jenis, "ulasan": [
            {"judul": r.title, "isi": r.text, "rating": float(r.rating), "terverifikasi": bool(r.verified_purchase),
             "helpful_vote": int(r.helpful_vote), "skor_U_tersimpan": float(r.score)} for r in g.itertuples()]})
        v = g["helpful_vote"].to_numpy()
        print(f"  {pid}: {len(g)} ulasan, helpful votes {sorted(v.tolist(), reverse=True)}")

hasil = {"kategori": "Video_Games", "run": RUN, "seed": SEED, "sumber": "Amazon Reviews 2023 (McAuley Lab), data uji",
         "produk": produk}
path = pathlib.Path("/content/contoh_produk_uji.json" if files else "contoh_produk_uji.json")
path.write_text(json.dumps(hasil, ensure_ascii=False, indent=1))
print("ditulis", path, f"({path.stat().st_size / 1e3:.0f} KB)")
if files:
    files.download(str(path))
