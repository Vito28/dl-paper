"""Uji kesetaraan aplikasi Gradio dengan pipeline, memakai keluaran smoke (jalankan run_notebooks_smoke.py dulu).

Aplikasi dibangun dari hasil smoke (encoder mini, model U skala E2) di folder sementara, lalu skor ulasan uji yang
dihitung lewat app/inference.py dibandingkan dengan pred_test.parquet buatan pipeline. Embedding juga dibandingkan
langsung dengan emb_blair.npy. Keduanya harus sama, karena aplikasi wajib menghitung skor seperti run yang dilaporkan.

    python -m tests.app_smoke
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "smoke" / "outputs" / "Synthetic"


def main() -> None:
    import json
    cfg = json.loads((OUT / "config.json").read_text())
    run = f"U_{cfg['main_scale']}_{cfg['main_target']}_s{cfg['seeds'][0]}"
    if not (OUT / "runs" / run / "model.pt").exists():
        sys.exit(f"{OUT / 'runs' / run} tidak ada. Jalankan dulu: python tests/run_notebooks_smoke.py notebooks")

    tmp = Path(tempfile.mkdtemp(prefix="app_smoke_"))
    try:
        app = tmp / "app"
        shutil.copytree(REPO / "app", app, ignore=shutil.ignore_patterns("artefak", "__pycache__"))
        subprocess.run([sys.executable, str(REPO / "tools" / "build_app.py"), "--hasil", str(OUT),
                        "--keluar", str(app), "--run", run], check=True, stdout=subprocess.DEVNULL)
        shutil.copy(OUT / "runs" / run / "model.pt", app / "artefak" / "model_U.pt")
        sys.path.insert(0, str(app))
        from inference import Pemeringkat, Ulasan

        df = pd.read_parquet(OUT / "reviews_split.parquet")
        te = df[df["split"] == "test"].sample(300, random_state=0)
        ulasan = [Ulasan(r.title, r.text, r.rating, bool(r.verified_purchase)) for r in te.itertuples()]
        m = Pemeringkat(app / "artefak", device="cpu")

        # 1. fitur terstruktur sama dengan kolom z_* pipeline
        from inference import fitur_terstruktur
        z, _ = fitur_terstruktur(ulasan, m.cfg)
        z_pipe = te[[f"z_{f}" for f in m.cfg["fitur"]]].to_numpy(np.float32)
        dz = float(np.abs(z - z_pipe).max())
        assert dz < 1e-4, f"fitur berbeda {dz}"

        # 2. embedding sama dengan emb_blair.npy
        idx = pd.read_parquet(OUT / "emb_index.parquet")
        pos = pd.Series(np.arange(len(idx)), index=idx["rid"].to_numpy())
        E = np.load(OUT / "emb_blair.npy", mmap_mode="r")
        e_pipe = np.asarray(E[pos.loc[te["rid"]].to_numpy()], dtype=np.float32)
        e_app = m.embedding(te["title"].tolist(), te["text"].tolist()).astype(np.float32)
        de = float(np.abs(e_app - e_pipe).max())
        assert de < 2e-3, f"embedding berbeda {de}"

        # 3. skor sama dengan pred_test.parquet
        s, _, detik = m.skor(ulasan)
        pred = te[["rid"]].merge(pd.read_parquet(OUT / "runs" / run / "pred_test.parquet"), on="rid", how="left")
        ds = float(np.abs(s - pred["score"].to_numpy()).max())
        assert ds < 1e-2, f"skor berbeda {ds}"
        print(f"run {run}, {len(te)} ulasan uji: selisih maksimum fitur {dz:.1e}, embedding {de:.1e}, "
              f"skor {ds:.1e} ({detik:.1f} detik)")

        # 4. NDCG@10 aplikasi sama dengan evaluasi pipeline (metrics.per_product_metrics)
        sys.path.insert(0, str(REPO / "src"))
        from hr.metrics import per_product_metrics
        from inference import evaluasi_urutan
        tg = pd.read_parquet(OUT / "targets.parquet", columns=["rid", "grade_t1", "y_t1"])
        pred_all = pd.read_parquet(OUT / "runs" / run / "pred_test.parquet")
        uji = df[df["split"] == "test"].merge(tg, on="rid").merge(pred_all, on="rid")
        pp = per_product_metrics(uji["parent_asin"], uji["score"], uji["grade_t1"], uji["y_t1"], uji["rid"])
        pp = pp.dropna(subset=["ndcg@10"]).set_index("parent_asin")
        n_cek = 0
        for pid, g in uji[uji["parent_asin"].isin(pp.index)].groupby("parent_asin"):
            if g["score"].duplicated().any():
                continue                                    # skor kembar diputus berbeda, lihat evaluasi_urutan
            ev = evaluasi_urutan(g["helpful_vote"].to_numpy(), g["score"].to_numpy(),
                                 g["review_length"].to_numpy(), m.cfg)
            assert np.array_equal(ev["tingkat"], g["grade_t1"].to_numpy()), pid
            assert abs(ev["model"] - pp.loc[pid, "ndcg@10"]) < 1e-9, (pid, ev["model"], pp.loc[pid, "ndcg@10"])
            n_cek += 1
        assert n_cek >= 20, n_cek
        print(f"NDCG@10 aplikasi = per_product_metrics pipeline pada {n_cek} produk uji")

        # 5. contoh produk asli: berkas berformat sama dengan ekspor Colab, dibuat dari produk uji smoke
        pilih = uji.groupby("parent_asin").filter(lambda g: 4 <= len(g) <= 12 and g["helpful_vote"].max() > 0)
        produk = []
        for pid in sorted(pilih["parent_asin"].unique())[:3]:
            g = pilih[pilih["parent_asin"] == pid].sample(frac=1, random_state=0)
            produk.append({"parent_asin": pid, "ulasan": [
                {"judul": r.title, "isi": r.text, "rating": float(r.rating), "terverifikasi": bool(r.verified_purchase),
                 "helpful_vote": int(r.helpful_vote), "skor_U_tersimpan": float(r.score)} for r in g.itertuples()]})
        (app / "artefak" / "contoh_produk_uji.json").write_text(json.dumps(
            {"kategori": cfg["category"], "run": run, "produk": produk}, indent=1))

        # 6. antarmuka: setiap contoh diurutkan lewat fungsi yang dipanggil tombol "Urutkan ulasan"
        import os
        os.environ["HR_APP_ARTEFAK"] = str(app / "artefak")
        import app as aplikasi
        assert sum(n.startswith("Produk uji asli") for n in aplikasi.CONTOH) == len(produk)
        for nama, c in aplikasi.CONTOH.items():
            tabel, _ = aplikasi.muat(nama)
            hasil, info = aplikasi.urutkan(tabel)
            assert len(hasil) == len(c["baris"]) and list(hasil["Peringkat"]) == list(range(1, len(hasil) + 1)), nama
            assert list(tabel.columns) == aplikasi.KOLOM and not any("vote" in k.lower() for k in aplikasi.KOLOM)
            if nama.startswith("Contoh buatan"):
                assert "NDCG@10" not in info and "Helpful votes asli" not in hasil.columns, (nama, info)
            if nama.startswith("Produk uji asli"):
                assert "NDCG@10" in info and "Helpful votes asli" in hasil.columns, (nama, info)
                p = next(x for x in produk if x["parent_asin"] in nama)
                tersimpan = {u["isi"][:157]: u["skor_U_tersimpan"] for u in p["ulasan"]}
                for r in hasil.itertuples():
                    isi = r[4][:-3] if r[4].endswith("...") else r[4]
                    assert abs(r.Skor - round(tersimpan[isi[:157]], 3)) <= 1.5e-3, (nama, r.Skor)
        print(f"antarmuka: {len(aplikasi.CONTOH)} contoh diurutkan, skor contoh asli = skor tersimpan")

        # 7. masukan tidak valid ditolak dengan pesan yang jelas
        baris = aplikasi.CONTOH[aplikasi.CONTOH_AWAL]["baris"]
        kasus = {"satu ulasan": baris[:1],
                 "rating 9": [baris[0], ["x", "teks", 9, True]],
                 "rating teks": [baris[0], ["x", "teks", "lima", True]]}
        for nama, b in kasus.items():
            try:
                aplikasi.urutkan(aplikasi._tabel(b))
                raise AssertionError(f"{nama}: seharusnya ditolak")
            except Exception as e:
                assert type(e).__name__ == "Error", (nama, repr(e))
        print(f"validasi: {len(kasus)} masukan tidak valid ditolak")

        # 8. helpful votes asli hanya diambil dari contoh asli, dan hanya jika seluruh tabel cocok dengan satu produk
        nama_asli = next(n for n in aplikasi.CONTOH if n.startswith("Produk uji asli"))
        asli = aplikasi.CONTOH[nama_asli]["baris"]
        hasil, info = aplikasi.urutkan(aplikasi._tabel(asli[:3]))         # sebagian baris dihapus: tetap dinilai
        assert "Helpful votes asli" in hasil.columns, info
        hasil, info = aplikasi.urutkan(aplikasi._tabel(asli + [["x", "ulasan tambahan", 5, True]]))
        assert "Helpful votes asli" not in hasil.columns and "tidak lagi sama persis" in info, info
        aplikasi.CONTOH["uji suara nol"] = {"baris": [], "keterangan": "", "suara": {
            aplikasi.kunci(r[0], r[1]): 0 for r in baris}}
        _, info = aplikasi.urutkan(aplikasi._tabel(baris))
        assert "tidak terdefinisi" in info, info
        del aplikasi.CONTOH["uji suara nol"]
        print("helpful votes asli: dicocokkan dari contoh asli, tabel yang diubah dan suara nol ditangani")
        print("APP SMOKE LULUS")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
