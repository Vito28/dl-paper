"""Penghubung antar notebook: memuat data hasil tahap sebelumnya, menjalankan satu konfigurasi
eksperimen, dan menyimpan hasilnya dengan nama yang konsisten.

Setiap run disimpan di ``outputs/<kategori>/runs/<run_id>/`` berisi:
- ``result.json``   konfigurasi dan metrik validasi terbaik
- ``history.csv``   loss dan NDCG@10 per epoch (untuk grafik loss)
- ``pred_val.parquet`` dan ``pred_test.parquet``  skor per ulasan (rid, score)
- ``model.pt``      bobot model terbaik

Metrik data uji TIDAK dihitung di sini. Notebook 07 menghitungnya sekali setelah semua keputusan
diambil.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import EXPERIMENTS, Config
from .embed import check_embeddings
from .features import fuse
from .train import EvalSet, predict, train_scorer


def protocol_cols(target: str) -> tuple[str, str]:
    """Kolom (grade, target kontinu) untuk evaluasi. T1 dan T2 memakai relevansi mentah."""
    return ("grade_t3", "y_t3") if target == "T3" else ("grade_t1", "y_t1")


@dataclass
class Bundle:
    cfg: Config
    df: pd.DataFrame                       # semua baris yang punya embedding, sudah berisi target
    pos: pd.Series                         # rid -> posisi baris pada berkas embedding
    _emb: dict = field(default_factory=dict)

    def emb(self, rep: str) -> np.ndarray:
        if rep not in self._emb:
            path = self.cfg.path(f"emb_{rep}.npy")
            model = self.cfg.encoders.get(rep)          # None untuk tfidf_svd
            check_embeddings(path, self.pos.index.to_numpy(), model)
            self._emb[rep] = np.load(path, mmap_mode="r")
        return self._emb[rep]

    def rows(self, split: str, scale: str | None = None) -> pd.DataFrame:
        d = self.df[self.df["split"] == split]
        if scale is not None:
            d = d[d[f"in_{scale}"]]
        return d

    def X(self, rows: pd.DataFrame, rep: str, feats) -> np.ndarray:
        e = np.asarray(self.emb(rep)[self.pos.loc[rows["rid"]].to_numpy()])
        return fuse(e, rows, feats)

    def eval_set(self, rows: pd.DataFrame, X: np.ndarray, target: str) -> EvalSet:
        g, t = protocol_cols(target)
        return EvalSet(X, rows["parent_asin"].to_numpy(), rows["rid"].to_numpy(),
                       rows[g].to_numpy(), rows[t].to_numpy())


def load_bundle(cfg: Config) -> Bundle:
    df = pd.read_parquet(cfg.path("reviews_split.parquet"))
    tg = pd.read_parquet(cfg.path("targets.parquet"))
    idx = pd.read_parquet(cfg.path("emb_index.parquet"))
    df = df.merge(tg, on="rid", how="inner")
    df = df[df["rid"].isin(idx["rid"])].reset_index(drop=True)
    pos = pd.Series(np.arange(len(idx)), index=idx["rid"].to_numpy())
    return Bundle(cfg, df, pos)


def run_id(code: str, scale: str, target: str, seed: int, extra: str = "") -> str:
    return f"{code}_{scale}_{target}_s{seed}{('_' + extra) if extra else ''}"


def run_torch(b: Bundle, code: str, *, scale: str, target: str, seed: int, lr: float, dropout: float,
              age_window: float | None = None, rep: str | None = None, extra: str = "",
              overwrite: bool = False, verbose: bool = True) -> dict:
    """Jalankan satu eksperimen torch (B2-B5, U, A1-A3, E*, T*)."""
    cfg = b.cfg
    spec = EXPERIMENTS[code]
    rep = rep or spec["rep"]
    rid_ = run_id(code, scale, target, seed, extra)
    out = cfg.out_dir / "runs" / rid_
    tr, va, te = b.rows("train", scale), b.rows("val"), b.rows("test")
    if (out / "result.json").exists() and not overwrite:
        old = json.loads((out / "result.json").read_text())
        want = {"rep": rep, "feats": spec["feats"], "model": spec["model"], "loss": spec["loss"], "lr": lr,
                "dropout": dropout, "age_window": age_window, "train_reviews": len(tr)}
        diff = {k: (old.get(k), v) for k, v in want.items() if old.get(k) != v}
        if diff:
            # Nama run tidak memuat lr/dropout. Tanpa pemeriksaan ini, run lama dengan hiperparameter
            # atau data berbeda akan dipakai ulang diam-diam.
            raise ValueError(f"Run {rid_} sudah ada dengan pengaturan berbeda (lama, baru): {diff}. "
                             "Hapus folder run tersebut atau panggil dengan overwrite=True.")
        return old
    out.mkdir(parents=True, exist_ok=True)

    y_col = "y_t3" if target == "T3" else "y_t1"
    Xtr, Xva, Xte = (b.X(d, rep, spec["feats"]) for d in (tr, va, te))
    hidden = cfg.hidden if spec["model"] == "mlp" else ()
    t0 = time.time()
    model, hist, best = train_scorer(
        Xtr, tr[y_col].to_numpy(), tr["parent_asin"].to_numpy(), b.eval_set(va, Xva, target),
        loss=spec["loss"], hidden=hidden, dropout=dropout, lr=lr, weight_decay=cfg.weight_decay,
        max_epochs=cfg.max_epochs, patience=cfg.patience, batch_pairs=cfg.batch_pairs,
        batch_points=cfg.batch_points, max_pairs=cfg.max_pairs_per_product, delta=cfg.pair_delta,
        log_age_train=tr["log_age"].to_numpy() if target == "T2" else None,
        age_window=age_window if target == "T2" else None, seed=seed, map_rel=cfg.map_relevant_grade,
        verbose=verbose)
    device = next(model.parameters()).device.type
    hist.to_csv(out / "history.csv", index=False)
    for name, d, X in (("val", va, Xva), ("test", te, Xte)):
        pd.DataFrame({"rid": d["rid"].to_numpy(), "score": predict(model, X, device)}).to_parquet(
            out / f"pred_{name}.parquet", index=False)
    torch.save(model.state_dict(), out / "model.pt")
    res = {"run_id": rid_, "code": code, "rep": rep, "feats": spec["feats"], "model": spec["model"],
           "loss": spec["loss"], "scale": scale, "target": target, "seed": seed, "lr": lr, "dropout": dropout,
           "age_window": age_window, "train_reviews": len(tr), "train_products": int(tr["parent_asin"].nunique()),
           "best_val_ndcg@10": best, "epochs_run": int(len(hist)),
           "best_epoch": int(hist.loc[hist["val_ndcg@10"].idxmax(), "epoch"]),
           "minutes": (time.time() - t0) / 60}
    (out / "result.json").write_text(json.dumps(res, indent=2, default=str))
    return res


def save_scores(cfg: Config, run: str, meta: dict, val_rows, val_scores, test_rows, test_scores) -> None:
    """Simpan skor untuk baseline non-torch (B0, B1) dalam format yang sama."""
    out = cfg.out_dir / "runs" / run
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"rid": val_rows["rid"].to_numpy(), "score": val_scores}).to_parquet(out / "pred_val.parquet", index=False)
    pd.DataFrame({"rid": test_rows["rid"].to_numpy(), "score": test_scores}).to_parquet(out / "pred_test.parquet", index=False)
    (out / "result.json").write_text(json.dumps({"run_id": run, **meta}, indent=2, default=str))


def results_table(cfg: Config) -> pd.DataFrame:
    rows = [json.loads(p.read_text()) for p in sorted((cfg.out_dir / "runs").glob("*/result.json"))]
    return pd.DataFrame(rows)


def load_pred(cfg: Config, run: str, split: str) -> pd.DataFrame:
    return pd.read_parquet(cfg.out_dir / "runs" / run / f"pred_{split}.parquet")
