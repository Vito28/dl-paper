"""Pengumpulan dan preprocessing data (Subbab 3.2 dan 3.3)."""
from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from .config import HF_RAW_URL, RAW_COLUMNS, Config

MS_PER_DAY = 86_400_000
# Rentang waktu Amazon Reviews 2023 menurut Hou et al. (Tabel 1): Juni 1996 sampai September 2023.
VALID_MIN = pd.Timestamp("1995-01-01")
VALID_MAX = pd.Timestamp("2023-12-31")

try:  # orjson jauh lebih cepat untuk jutaan baris, tetapi opsional
    import orjson as _json

    def _loads(line: bytes):
        return _json.loads(line)
except ImportError:  # pragma: no cover
    def _loads(line: bytes):
        return json.loads(line)


# ---------------------------------------------------------------- 3.2 pengumpulan
def download_raw(cfg: Config, chunk: int = 1 << 22) -> dict:
    """Unduh berkas User Reviews kategori terpilih, lalu catat ukuran dan checksum."""
    url = HF_RAW_URL.format(category=cfg.category)
    dest = cfg.raw_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        tmp = dest.with_suffix(".part")
        with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
            total = int(r.headers.get("Content-Length", 0))
            done, t0 = 0, time.time()
            while True:
                buf = r.read(chunk)
                if not buf:
                    break
                f.write(buf)
                done += len(buf)
                if total:
                    print(f"\r{done / 1e9:.2f}/{total / 1e9:.2f} GB", end="")
        tmp.rename(dest)
        print(f"\nselesai dalam {time.time() - t0:.0f} detik")
    sha = hashlib.sha256()
    n_lines = 0
    with open(dest, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            sha.update(block)
            n_lines += block.count(b"\n")
    manifest = {
        "category": cfg.category,
        "url": url,
        "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "bytes": dest.stat().st_size,
        "rows": n_lines,
        "sha256": sha.hexdigest(),
    }
    cfg.path("manifest_raw.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def _keep_product(parent_asin: str, rate: float) -> bool:
    if rate >= 1.0:
        return True
    h = int(hashlib.md5(parent_asin.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return h < rate


def load_reviews(cfg: Config, limit: int | None = None) -> pd.DataFrame:
    """Baca JSONL baris demi baris. Pengambilan sampel dilakukan per produk (bukan per baris)
    supaya daftar ulasan setiap produk tetap utuh."""
    cols = {c: [] for c in RAW_COLUMNS}
    with open(cfg.raw_path, "rb") as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            r = _loads(line)
            pa = r.get("parent_asin") or ""
            if not _keep_product(pa, cfg.product_sample_rate):
                continue
            for c in RAW_COLUMNS:
                cols[c].append(r.get(c))
    return pd.DataFrame(cols)


# ---------------------------------------------------------------- 3.3 preprocessing
_TAG = re.compile(r"<[^>]+>")
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WS = re.compile(r"\s+")


def clean_text(s) -> str:
    """Rapikan spasi, hapus karakter kendali dan sisa markup HTML. Huruf kapital, tanda baca,
    angka, dan kata negasi dipertahankan karena dibutuhkan encoder."""
    if not isinstance(s, str):
        return ""
    s = html.unescape(s)
    s = _TAG.sub(" ", s)
    s = _CTRL.sub(" ", s)
    return _WS.sub(" ", s).strip()


def check_timestamp_unit(ts: pd.Series) -> dict:
    """Langkah 2. Coba satuan milidetik lalu detik, pilih yang rentang tanggalnya masuk akal."""
    ts = pd.to_numeric(ts, errors="coerce").dropna()
    out = {}
    for unit in ("ms", "s"):
        d = pd.to_datetime(ts, unit=unit, errors="coerce")
        ok = d.between(VALID_MIN, VALID_MAX).mean()
        out[unit] = {"min": str(d.min()), "max": str(d.max()), "share_in_range": float(ok)}
    unit = "ms" if out["ms"]["share_in_range"] >= out["s"]["share_in_range"] else "s"
    out["chosen"] = unit
    if out[unit]["share_in_range"] < 0.99:
        raise ValueError(f"Satuan timestamp tidak meyakinkan: {out}")
    return out


def preprocess(df: pd.DataFrame, cfg: Config) -> tuple[pd.DataFrame, dict]:
    """Langkah preprocessing pada Subbab 3.3. Mengembalikan data bersih dan laporan jumlah baris."""
    rep = {"rows_raw": len(df)}
    df = df.copy()

    # 1. tipe dan rentang
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["helpful_vote"] = pd.to_numeric(df["helpful_vote"], errors="coerce")
    df["verified_purchase"] = df["verified_purchase"].map(
        {True: 1, False: 0, "true": 1, "false": 0, "True": 1, "False": 0})
    bad = (~df["rating"].between(1, 5)) | df["helpful_vote"].isna() | (df["helpful_vote"] < 0) \
        | df["verified_purchase"].isna()
    rep["drop_invalid_type"] = int(bad.sum())
    df = df[~bad]
    df["helpful_vote"] = df["helpful_vote"].astype(np.int64)
    df["verified_purchase"] = df["verified_purchase"].astype(np.int8)

    # 2. satuan timestamp
    rep["timestamp_check"] = check_timestamp_unit(df["timestamp"])
    factor = 1 if rep["timestamp_check"]["chosen"] == "ms" else 1000
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce") * factor
    dt = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
    bad = ~dt.between(VALID_MIN, VALID_MAX)
    rep["drop_invalid_timestamp"] = int(bad.sum())
    df = df[~bad]
    df["timestamp"] = df["timestamp"].astype(np.int64)

    # 3. data kosong
    df["text"] = df["text"].map(clean_text)       # 4. normalisasi teks
    df["title"] = df["title"].map(clean_text)
    empty = df["parent_asin"].isna() | (df["parent_asin"].astype(str).str.len() == 0) | (df["text"].str.len() == 0)
    rep["drop_empty"] = int(empty.sum())
    df = df[~empty]

    # 5. duplikasi
    before = len(df)
    df = df.drop_duplicates(subset=["user_id", "parent_asin", "timestamp", "text"])
    rep["drop_duplicate"] = before - len(df)

    # 6. fitur panjang (persamaan 3.2 memakai log(1+x) lalu standardisasi di split.py)
    df["review_length"] = df["text"].str.len()
    df["word_count"] = df["text"].str.split().str.len()
    df["title_length"] = df["title"].str.len()
    for c in ("review_length", "word_count", "title_length"):
        df[f"log_{c}"] = np.log1p(df[c].astype(np.float64))

    # usia ulasan (persamaan 3.1). T_ref = timestamp valid terbesar.
    t_ref = int(df["timestamp"].max())
    df["age_days"] = (t_ref - df["timestamp"]) / MS_PER_DAY
    df["log_age"] = np.log1p(df["age_days"])
    rep["t_ref"] = str(pd.to_datetime(t_ref, unit="ms"))

    # produk dengan sedikitnya dua ulasan
    sizes = df.groupby("parent_asin")["text"].transform("size")
    keep = sizes >= cfg.min_reviews_per_product
    rep["drop_small_product"] = int((~keep).sum())
    df = df[keep]

    # identitas baris yang stabil dan tidak berkaitan dengan label
    df = df.sort_values(["parent_asin", "timestamp", "user_id"], kind="stable").reset_index(drop=True)
    df["rid"] = np.arange(len(df), dtype=np.int64)
    df["text_hash"] = pd.util.hash_pandas_object(df["text"].str.lower(), index=False).astype(np.uint64)
    rep["rows_clean"] = len(df)
    rep["products_clean"] = int(df["parent_asin"].nunique())
    return df, rep


def describe(df: pd.DataFrame) -> dict:
    """Statistik deskriptif untuk Bab IV (Subbab 3.2)."""
    v = df["helpful_vote"]
    per_prod = df.groupby("parent_asin").size()
    return {
        "reviews": len(df),
        "products": int(per_prod.size),
        "zero_vote_share": float((v == 0).mean()),
        "vote_mean": float(v.mean()),
        "vote_median": float(v.median()),
        "vote_p99": float(v.quantile(0.99)),
        "vote_max": int(v.max()),
        "reviews_per_product_median": float(per_prod.median()),
        "reviews_per_product_p99": float(per_prod.quantile(0.99)),
        "age_days_median": float(df["age_days"].median()),
        "products_all_zero_share": float((df.groupby("parent_asin")["helpful_vote"].max() == 0).mean()),
        "spearman_age_vote": float(df[["age_days", "helpful_vote"]].rank().corr().iloc[0, 1]),
    }


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
