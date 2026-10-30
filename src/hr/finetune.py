"""Fine-tuning encoder dengan objektif pemeringkatan (eksperimen opsional, kritik-reviewer.md 3.3).

Encoder (BLaIR atau RoBERTa-base) tidak dibekukan dan dilatih bersama kepala MLP dengan loss
RankNet. Setiap langkah mengambil beberapa produk, lalu beberapa ulasan dari setiap produk, dan
loss dihitung pada semua pasangan di dalam produk dengan y_i - y_j > delta.
"""
from __future__ import annotations

import copy
import time

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

from .embed import _title_for_pair
from .metrics import macro, per_product_metrics


class EncoderRanker(nn.Module):
    def __init__(self, model_name: str, n_struct: int, hidden=(256, 64), dropout: float = 0.2):
        super().__init__()
        from transformers import AutoModel
        self.encoder = AutoModel.from_pretrained(model_name)
        d = self.encoder.config.hidden_size + n_struct
        layers = []
        for h in hidden:
            layers += [nn.Linear(d, h), nn.ReLU(), nn.Dropout(dropout)]
            d = h
        layers.append(nn.Linear(d, 1))
        self.head = nn.Sequential(*layers)

    def forward(self, enc: dict, z: torch.Tensor) -> torch.Tensor:
        h = self.encoder(**enc).last_hidden_state[:, 0]
        h = F.normalize(h, dim=-1)                       # sama dengan versi beku: [CLS] + L2
        return self.head(torch.cat([h, z], dim=-1).float()).squeeze(-1)


def _within_product_ranknet(s: torch.Tensor, y: torch.Tensor, grp: torch.Tensor, delta: float):
    same = grp[:, None] == grp[None, :]
    better = (y[:, None] - y[None, :]) > delta
    mask = same & better
    if mask.sum() == 0:
        return None
    diff = s[:, None] - s[None, :]
    return F.softplus(-diff[mask]).mean()


class ProductBatcher:
    def __init__(self, df: pd.DataFrame, y: np.ndarray, products_per_step: int, reviews_per_product: int,
                 seed: int):
        self.rng = np.random.default_rng(seed)
        self.groups = [np.asarray(ix) for ix in df.groupby("parent_asin").indices.values() if len(ix) >= 2]
        self.y = y
        self.P, self.R = products_per_step, reviews_per_product

    def __iter__(self):
        order = self.rng.permutation(len(self.groups))
        for i in range(0, len(order), self.P):
            idx, grp = [], []
            for k, g in enumerate(order[i:i + self.P]):
                rows = self.groups[g]
                pick = self.rng.choice(rows, size=min(self.R, len(rows)), replace=False)
                idx.append(pick)
                grp.append(np.full(len(pick), k))
            yield np.concatenate(idx), np.concatenate(grp)


@torch.no_grad()
def score_frame(model: EncoderRanker, tok, df: pd.DataFrame, Z: np.ndarray, max_len: int, device: str,
                batch: int = 128) -> np.ndarray:
    model.eval()
    titles = [_title_for_pair(t) for t in df["title"]]
    texts = df["text"].tolist()
    order = np.argsort([len(t) for t in texts])
    out = np.zeros(len(df), dtype=np.float32)
    for i in range(0, len(df), batch):
        ix = order[i:i + batch]
        enc = tok([titles[j] for j in ix], [texts[j] for j in ix], truncation="only_second",
                  max_length=max_len, padding=True, return_tensors="pt").to(device)
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=device == "cuda"):
            s = model(enc, torch.as_tensor(Z[ix], device=device, dtype=torch.float32))
        out[ix] = s.float().cpu().numpy()
    return out


def finetune(model_name: str, train_df: pd.DataFrame, y_train: np.ndarray, Z_train: np.ndarray,
             val_df: pd.DataFrame, Z_val: np.ndarray, val_grade: np.ndarray, val_target: np.ndarray, *,
             max_len: int = 256, epochs: int = 2, products_per_step: int = 16, reviews_per_product: int = 8,
             lr_encoder: float = 2e-5, lr_head: float = 1e-3, weight_decay: float = 0.01,
             grad_accum: int = 2, delta: float = 0.0, eval_every: int = 1000, seed: int = 42,
             device: str | None = None, map_rel: int = 2):
    from transformers import AutoTokenizer, get_linear_schedule_with_warmup
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(seed)
    tok = AutoTokenizer.from_pretrained(model_name)
    model = EncoderRanker(model_name, Z_train.shape[1]).to(device)
    opt = torch.optim.AdamW([
        {"params": model.encoder.parameters(), "lr": lr_encoder},
        {"params": model.head.parameters(), "lr": lr_head},
    ], weight_decay=weight_decay)
    batcher = ProductBatcher(train_df.reset_index(drop=True), y_train, products_per_step, reviews_per_product, seed)
    steps_per_epoch = int(np.ceil(len(batcher.groups) / products_per_step))
    total = max(1, epochs * steps_per_epoch // grad_accum)
    sched = get_linear_schedule_with_warmup(opt, int(0.06 * total), total)
    scaler = torch.amp.GradScaler("cuda", enabled=device == "cuda")
    titles = [_title_for_pair(t) for t in train_df["title"]]
    texts = train_df["text"].tolist()

    def run_eval():
        s = score_frame(model, tok, val_df, Z_val, max_len, device)
        pp = per_product_metrics(val_df["parent_asin"].to_numpy(), s, val_grade, val_target,
                                 val_df["rid"].to_numpy(), map_rel=map_rel)
        return macro(pp)

    hist, best, best_state, step = [], -np.inf, None, 0
    t0 = time.time()
    for ep in range(epochs):
        model.train()
        running = []
        for k, (idx, grp) in enumerate(batcher):
            enc = tok([titles[j] for j in idx], [texts[j] for j in idx], truncation="only_second",
                      max_length=max_len, padding=True, return_tensors="pt").to(device)
            z = torch.as_tensor(Z_train[idx], device=device, dtype=torch.float32)
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=device == "cuda"):
                s = model(enc, z)
            loss = _within_product_ranknet(s.float(), torch.as_tensor(y_train[idx], device=device),
                                           torch.as_tensor(grp, device=device), delta)
            if loss is None:
                continue
            scaler.scale(loss / grad_accum).backward()
            running.append(loss.item())
            if (k + 1) % grad_accum == 0:
                scaler.unscale_(opt)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(opt)
                scaler.update()
                opt.zero_grad()
                sched.step()
                step += 1
                if step % eval_every == 0:
                    m = run_eval()
                    hist.append({"epoch": ep + 1, "step": step, "train_loss": float(np.mean(running)),
                                 "val_ndcg@10": m["ndcg@10"], "minutes": (time.time() - t0) / 60})
                    print(hist[-1])
                    running = []
                    if m["ndcg@10"] > best:
                        best, best_state = m["ndcg@10"], copy.deepcopy(model.state_dict())
                    model.train()
        m = run_eval()
        hist.append({"epoch": ep + 1, "step": step, "train_loss": float(np.mean(running)) if running else np.nan,
                     "val_ndcg@10": m["ndcg@10"], "minutes": (time.time() - t0) / 60})
        print(hist[-1])
        if m["ndcg@10"] > best:
            best, best_state = m["ndcg@10"], copy.deepcopy(model.state_dict())
    model.load_state_dict(best_state)
    return model, tok, pd.DataFrame(hist), best
