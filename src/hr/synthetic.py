"""Data sintetis berformat Amazon Reviews 2023, khusus untuk uji cepat (HR_SMOKE=1)."""
from __future__ import annotations

import numpy as np
import pandas as pd

WORDS = ("good bad great battery screen fast slow cheap price quality broke works love hate return "
         "size fits sound game controller disc graphics fun boring update").split()


def synthetic(n_products: int = 400, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    t_end = pd.Timestamp("2023-09-01").value // 10 ** 6
    for p in range(n_products):
        n = int(rng.integers(2, 40))
        pop = rng.normal(0, 1)
        for i in range(n):
            age = float(rng.exponential(700))
            length = int(rng.integers(3, 120))
            text = " ".join(rng.choice(WORDS, size=length))
            mu = np.exp(-1.0 + pop + 0.35 * np.log1p(age) - 1.2 + 0.4 * np.log1p(length) / 3)
            votes = int(rng.negative_binomial(2, 2 / (2 + mu)))
            rows.append({"rating": float(rng.integers(1, 6)), "title": " ".join(rng.choice(WORDS, size=4)),
                         "text": text + (" <br /> " if i % 7 == 0 else ""), "asin": f"A{p}-{i % 3}",
                         "parent_asin": f"P{p}", "user_id": f"U{rng.integers(1e6)}",
                         "timestamp": int(t_end - age * 86_400_000), "helpful_vote": votes,
                         "verified_purchase": bool(rng.random() < 0.8)})
    df = pd.DataFrame(rows)
    return pd.concat([df, df.iloc[:5]], ignore_index=True)   # duplikat sengaja
