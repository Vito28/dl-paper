"""Ekstraksi embedding (Subbab 2.5 dan 3.6) dan representasi TF-IDF (Subbab 2.4).

Embedding diambil dari token [CLS] (``<s>`` pada RoBERTa) lapisan terakhir lalu dinormalisasi L2,
sesuai dokumentasi checkpoint BLaIR (persamaan 2.3 dan 2.4). RoBERTa-base untuk B5 memakai
prosedur yang persis sama.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd


def _title_for_pair(title: str, max_words: int = 64) -> str:
    # judul sangat panjang dipotong agar truncation "only_second" selalu bisa memotong isi ulasan
    w = (title or "").split()
    return " ".join(w[:max_words])


def token_length_stats(df: pd.DataFrame, model_name: str, max_len: int, n: int = 50_000, seed: int = 0) -> dict:
    """Proporsi ulasan yang terpotong batas token (Subbab 3.2)."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_name)
    s = df.sample(min(n, len(df)), random_state=seed)
    enc = tok([_title_for_pair(t) for t in s["title"]], s["text"].tolist(), truncation=False)
    lens = np.array([len(x) for x in enc["input_ids"]])
    return {"sampled": int(len(lens)), "median_tokens": float(np.median(lens)),
            "p95_tokens": float(np.quantile(lens, 0.95)), "share_truncated": float((lens > max_len).mean())}


def extract_embeddings(df: pd.DataFrame, model_name: str, out_path: Path, max_len: int = 512,
                       batch_size: int = 64, device: str | None = None, fp16: bool = True) -> np.memmap:
    """Hitung embedding sekali tanpa gradien dan simpan sebagai memmap float16.

    Baris ke-k pada berkas sesuai baris ke-k ``df`` (urutkan ``df`` berdasarkan ``rid`` sebelum
    memanggil). Ekstraksi bisa dilanjutkan jika terputus karena progres disimpan setiap 200 batch.
    """
    import torch
    import torch.nn.functional as F
    from transformers import AutoModel, AutoTokenizer

    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path = out_path.with_suffix(".json")
    n = len(df)
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).to(device).eval()
    dim = model.config.hidden_size                  # 768 untuk BLaIR-RoBERTa-Base dan RoBERTa-base
    mode = "r+" if out_path.exists() else "w+"
    mm = np.lib.format.open_memmap(out_path, mode=mode, dtype=np.float16, shape=(n, dim))
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {"done": 0}
    if fp16 and device == "cuda":
        model = model.half()

    titles = [_title_for_pair(t) for t in df["title"].tolist()]
    texts = df["text"].tolist()
    order = np.argsort([len(t) for t in texts], kind="stable")  # batch berisi panjang mirip = padding sedikit
    t0 = time.time()
    start = meta["done"]
    with torch.inference_mode():
        for b, i in enumerate(range(start, n, batch_size)):
            idx = order[i:i + batch_size]
            enc = tok([titles[j] for j in idx], [texts[j] for j in idx], truncation="only_second",
                      max_length=max_len, padding=True, return_tensors="pt").to(device)
            h = model(**enc).last_hidden_state[:, 0]
            h = F.normalize(h.float(), dim=-1)
            mm[idx] = h.cpu().numpy().astype(np.float16)
            if b % 200 == 0:
                mm.flush()
                meta.update(done=i + len(idx), model=model_name, max_len=max_len, pooling="cls+l2",
                            rows=n, elapsed_s=time.time() - t0)
                meta_path.write_text(json.dumps(meta))
                print(f"\r{i + len(idx)}/{n} ({(i + len(idx)) / max(time.time() - t0, 1e-9):.0f} ulasan/detik)", end="")
    mm.flush()
    meta.update(done=n, model=model_name, max_len=max_len, pooling="cls+l2", rows=n,
                elapsed_s=time.time() - t0, device=device)
    meta_path.write_text(json.dumps(meta))
    print("\nselesai")
    return mm


def load_embeddings(path: Path) -> np.ndarray:
    return np.load(path, mmap_mode="r")


# ---------------------------------------------------------------- TF-IDF
def fit_tfidf(train_texts, max_features: int = 200_000):
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(min_df=5, max_df=0.9, ngram_range=(1, 2), max_features=max_features,
                          sublinear_tf=True, dtype=np.float32)
    vec.fit(train_texts)
    return vec


def review_text(df: pd.DataFrame) -> list[str]:
    return (df["title"].fillna("") + " . " + df["text"].fillna("")).tolist()


def fit_svd(X_train, n_components: int = 768, seed: int = 42):
    """Untuk B2. TF-IDF diperkecil ke 768 dimensi agar sebanding dengan embedding BLaIR."""
    from sklearn.decomposition import TruncatedSVD
    svd = TruncatedSVD(n_components=n_components, algorithm="randomized", n_iter=5, random_state=seed)
    svd.fit(X_train)
    return svd
