"""Evaluasi data uji dan penyusunan tabel Bab IV (Subbab 3.9 dan 3.10)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .experiment import Bundle, load_pred, protocol_cols
from .metrics import macro, per_product_metrics
from .stats import average_over_seeds, holm, paired_diff, summarize


def eval_run(b: Bundle, run: str, split: str = "test", protocol: str = "T1",
             rows: pd.DataFrame | None = None) -> pd.DataFrame:
    """Metrik per produk untuk satu run. ``rows`` dapat dipakai untuk subset (misalnya kelompok usia)."""
    rows = b.rows(split) if rows is None else rows
    pred = load_pred(b.cfg, run, split)
    d = rows.merge(pred, on="rid", how="inner")
    g, t = protocol_cols(protocol)
    return per_product_metrics(d["parent_asin"].to_numpy(), d["score"].to_numpy(), d[g].to_numpy(),
                               d[t].to_numpy(), d["rid"].to_numpy(), map_rel=b.cfg.map_relevant_grade)


def eval_config(b: Bundle, runs: list[str], split: str = "test", protocol: str = "T1",
                rows: pd.DataFrame | None = None) -> pd.DataFrame:
    """Rata-rata metrik per produk dari semua seed satu konfigurasi."""
    return average_over_seeds([eval_run(b, r, split, protocol, rows) for r in runs])


def group_runs(results: pd.DataFrame) -> dict[tuple, list[str]]:
    """Kelompokkan run_id berdasarkan (code, scale, target) dengan mengabaikan seed dan run penalaan."""
    res = results[~results["run_id"].str.contains("_tune")]
    return {k: list(g["run_id"]) for k, g in res.groupby(["code", "scale", "target"])}


def comparison_table(b: Bundle, groups: dict, keys: list[tuple], protocol: str = "T1", n_boot: int = 1000,
                     split: str = "test") -> tuple[pd.DataFrame, dict]:
    """Tabel metrik dengan IK 95% untuk beberapa konfigurasi. Mengembalikan juga metrik per produk."""
    rows, pps = [], {}
    for key in keys:
        if key not in groups:
            continue
        pp = eval_config(b, groups[key], split, protocol)
        pps[key] = pp
        s = summarize(pp, n_boot)
        r = {"code": key[0], "scale": key[1], "target": key[2], "seeds": len(groups[key])}
        for _, m in s.iterrows():
            r[m["metric"]] = m["mean"]
            r[f"{m['metric']}_lo"] = m["lo"]
            r[f"{m['metric']}_hi"] = m["hi"]
            r[f"n_{m['metric']}"] = m["n"]
        rows.append(r)
    return pd.DataFrame(rows), pps


def paired_table(pps: dict, ref: tuple, others: list[tuple], metric: str = "ndcg@10", n_boot: int = 1000) -> pd.DataFrame:
    rows = []
    for o in others:
        if o not in pps or ref not in pps:
            continue
        d = paired_diff(pps[ref], pps[o], metric, n_boot)
        rows.append({"ref": ref[0], "vs": o[0], **d})
    tab = pd.DataFrame(rows)
    if len(tab):
        tab["p_holm"] = holm(tab["p"].to_numpy())
        tab["lebih_baik"] = (tab["lo"] > 0) & (tab["p_holm"] < 0.05)
    return tab


def age_groups(b: Bundle, edges: list[float]) -> pd.Series:
    """Kelompok usia ulasan (baru, menengah, lama) dengan batas dari data latih."""
    return pd.cut(b.df["age_days"], [-np.inf, edges[0], edges[1], np.inf], labels=["baru", "menengah", "lama"])


def by_subset(b: Bundle, runs: list[str], subsets: dict[str, pd.DataFrame], protocol: str = "T1") -> pd.DataFrame:
    rows = []
    for name, sub in subsets.items():
        pp = eval_config(b, runs, "test", protocol, sub)
        rows.append({"group": name, **macro(pp)})
    return pd.DataFrame(rows)


def pointwise_errors(b: Bundle, runs: list[str]) -> dict:
    """MAE dan RMSE terhadap ln(1 + v) khusus pembanding pointwise B4."""
    te = b.rows("test")
    errs = []
    for r in runs:
        d = te.merge(load_pred(b.cfg, r, "test"), on="rid")
        e = d["score"].to_numpy() - d["y_t1"].to_numpy()
        errs.append((np.abs(e).mean(), np.sqrt((e ** 2).mean())))
    e = np.array(errs)
    return {"mae": float(e[:, 0].mean()), "rmse": float(e[:, 1].mean()), "seeds": len(runs)}
