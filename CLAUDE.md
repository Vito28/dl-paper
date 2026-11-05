# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Research code and manuscript for a Deep Learning course paper (target journal: JuTISI, Sinta 3): **ranking product reviews by helpfulness within each product** using frozen BLaIR-RoBERTa-base embeddings + structured features, scored by an MLP trained with pairwise RankNet loss, on Amazon Reviews 2023. `helpful_vote` is a weak label. Prose, docstrings, notebook text, and output filenames are in **Indonesian**. Match that when editing them.

The spec the code follows is **the revised Bab III** (`documents/... - Revisi.docx`), not `agent.md`. `agent.md` is the older draft design, and its baseline codes (B4/B5) mean different things. `EXPERIMENTS.md` is the authoritative protocol. It covers notebook order, which output file feeds which Bab IV table, rules locked in code, and implementation decisions not yet written into Bab III.

## Commands

Run from the repo root (`dl-paper/`):

```bash
pip install -r requirements.txt
python -m tests.smoke_test                      # module-level test on synthetic data, CPU, no download
python -m tests.smoke_test --hf                 # + embedding extraction & fine-tuning with a tiny HF model (needs internet)
python tests/run_notebooks_smoke.py notebooks           # execute all 10 notebooks with HR_SMOKE=1
python tests/run_notebooks_smoke.py notebooks 03 05     # only notebooks whose names start with these prefixes
```

There is no pytest suite or linter. `tests/smoke_test.py` is a single script of `assert`s. Smoke runs write to `smoke/` (gitignored), and their numbers mean nothing scientifically. Real runs write to `data/` and `outputs/` (also gitignored). Set `HR_ROOT` to relocate them, e.g. to Google Drive on Colab.

## Storage (Colab / Google Drive)

`notebooks/settings.py` detects Colab and mounts Google Drive automatically. It also runs a write/read test and a free-space check (`HR_MIN_FREE_GB`, default 10). Then it sets `cfg.root` to `HR_DRIVE_ROOT` (default `/content/drive/MyDrive/dl-paper`) and `cfg.storage_mount="/content/drive"`. Everything lives under that root, including the raw JSONL. Each Colab notebook runs on its own runtime, so Drive is the only channel between notebooks.

`Config._root()` raises if `storage_mount` isn't mounted. This keeps writes from silently landing on instance disk. The last cell of every notebook is `finish()`, which calls `drive.flush_and_unmount()`. Outside Colab, the root is `HR_ROOT` or the repo root. With `HR_SMOKE=1` it is always `smoke/`.

Colab runs `git clone` against GitHub, so local changes only reach Colab after they are pushed.

## Fail-loud guards

The code raises an error rather than continuing quietly in these cases:
- a truncated download, or a raw file that doesn't match `manifest_raw.json`;
- more than 5% invalid rows;
- a scale in `cfg.scales` larger than the available training data;
- an embedding file whose rid fingerprint, model, or completeness doesn't match (`embed.check_embeddings`, which `Bundle.emb` calls on every load);
- a cached run whose hyperparameters or training size differ from the current call (`run_torch`);
- zero training pairs, or a NaN loss or NaN scores;
- predictions that don't cover every evaluation row;
- runs that are missing or left over from an older config (`report.check_complete`, called at the top of notebook 07).

Preserve these when editing. If a cached run or embedding is stale, delete its folder or file rather than bypassing the check.

## Architecture

**`src/hr/`** is the library. **`notebooks/01–10`** are thin drivers that run in order, and each one reads the previous one's artifacts from `outputs/<category>/`. Notebooks add `src/` and `notebooks/` to `sys.path` themselves and import `cfg` from `notebooks/settings.py`.

- **Configuration lives in one place.** `notebooks/settings.py` builds the `Config` (`src/hr/config.py`) that every notebook uses. `HR_SMOKE=1` swaps in `smoke_config()` (synthetic data, tiny encoder, small scales). Change settings there, not inside notebooks.
- **Experiment registry.** `EXPERIMENTS` in `config.py` defines the codes from Table 3.5: B0–B5 baselines, U the main model, A1–A3 feature ablations. Each entry sets `rep` (`blair` / `roberta` / `tfidf` / `tfidf_svd`), `model` (mlp / linear), `loss` (ranknet / mse), `feats`, and `priority`. `run_priority` (1–3) selects which experiments, scales (`SCALE_PRIORITY`: E1–E5 = 100k…1M training reviews), and targets (`TARGET_PRIORITY`) actually run. A4 is the same as U and is not retrained.
- **Targets** (`targets.py`, with equation numbers from Bab II/III in docstrings):
  - **T1** = `log1p(helpful_vote)`.
  - **T2** = T1, but training pairs are restricted to an age window Δa (`pairs.PairSampler(age_window=...)`).
  - **T3** = T1 minus an age component from a Negative Binomial count model with fixed product effects and a spline in log age. For train rows it is computed **out-of-fold**, with folds grouped by product.
  - T1 is turned into relevance grades 0–4 using training-set quartiles of the positive values. T3 thresholds are chosen so the grade proportions match T1.
- **Pipeline data flow:**
  - `data.preprocess` →
  - `split.split_products` (product-disjoint 80/10/10 on `parent_asin`) → `leakage_checks` → `cap_eval` → `make_scales` (nested E1⊂…⊂E5) → standardizer fit on train →
  - `reviews_split.parquet` + `targets.parquet` →
  - `embed.extract_embeddings` (CLS + L2 norm, float16 memmap `emb_{rep}.npy` + `emb_index.parquet`). This step is resumable, checkpointing every 200 batches.
- **Running experiments.** `experiment.load_bundle(cfg)` joins these artifacts. `Bundle.X(rows, rep, feats)` = embedding rows fused with the structured features (`features.fuse`). `experiment.run_torch` trains one config and writes `outputs/<cat>/runs/<code>_<scale>_<target>_s<seed>[_extra]/` containing `result.json`, `history.csv`, `pred_val.parquet`, `pred_test.parquet`, and `model.pt`. It **skips runs whose `result.json` exists** unless `overwrite=True`. Non-torch baselines (B0, B1) use `save_scores` to write the same format.
- **Evaluation.** `metrics.per_product_metrics` computes NDCG@5/10, Spearman, and AP per `parent_asin`. `stats` handles the per-product bootstrap, paired differences, and Holm correction. `report` builds the Bab IV tables from saved predictions.

## Invariants enforced in code (don't break these)

- **No leakage into features.** `helpful_vote`, age columns, and target/grade columns are in `FORBIDDEN_FEATURES` and checked with `assert`. `review_age` is never a model input. Only `STRUCT_FEATURES` (rating, verified_purchase, 3 log-length features) are fused.
- **Train-only fitting.** Standardization, TF-IDF, SVD, the age model, and relevance thresholds are fit on training data only.
- **Test set is evaluated only in notebook 07, once.** Notebooks 05–06 save test scores but must not compute test metrics. Hyperparameter tuning uses validation NDCG@10 only, and U's best hparams are reused for all MLP models.
- **Fixed in advance:** MAP relevance threshold is `grade >= 2`. Tied scores are broken by a hash of the row id (`metrics.tiebreak_key`), never by label.
- **Seeds:** results are averaged over `cfg.seeds`, then bootstrapped per product. The main comparisons are U vs B5 and U vs B1.

## Manuscript conventions (for edits to Bab I–III text)

Per `revisi-1-2-3.md`: the chapter body text contains **no colons (:) or semicolons (;)**. Formula explanations follow the format "dengan" + one line per symbol as `simbol = arti`. Every citation is backed by a page-referenced quote in `revisi-1-2-3.md`. `kritik-reviewer.md` holds the self-review and the proposed experiment cuts, which the group has not yet decided on.
