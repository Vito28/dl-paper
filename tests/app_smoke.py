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
        print("APP SMOKE LULUS")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
