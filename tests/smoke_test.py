"""Uji cepat seluruh alur dengan data sintetis (tanpa unduhan dataset, tanpa GPU).

Jalankan dari root repo:  python -m tests.smoke_test
Tambahkan --hf untuk ikut menguji ekstraksi embedding dan fine-tuning dengan model mini dari
Hugging Face (butuh internet, sekitar 1 MB).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hr import data, features, human, metrics, models, split, stats, targets  # noqa: E402
from hr.config import Config  # noqa: E402
from hr.pairs import PairSampler  # noqa: E402
from hr.synthetic import synthetic  # noqa: E402
from hr.train import EvalSet, predict, train_scorer  # noqa: E402

def main(use_hf: bool = False) -> None:
    tmp = Path(tempfile.mkdtemp())
    cfg = Config(root=tmp, category="Synthetic", max_eval_reviews=10_000,
                 scales={"E1": 1500, "E2": 3000, "E3": 5000}, main_scale="E2", max_epochs=3, patience=2,
                 age_bootstrap=3, eval_bootstrap=200)
    raw = synthetic()
    df, rep = data.preprocess(raw, cfg)
    assert rep["drop_duplicate"] >= 5 and "<br" not in " ".join(df["text"].head(50))
    print("preprocess", {k: v for k, v in rep.items() if k != "timestamp_check"})
    print("describe", data.describe(df))

    df = split.split_products(df, cfg)
    df, leak = split.leakage_checks(df)
    df, cap = split.cap_eval(df, cfg)
    df = split.make_scales(df, cfg)
    assert df[df.in_E1].index.isin(df[df.in_E2].index).all(), "skala tidak bertingkat"
    print(split.scale_report(df, cfg))
    df = split.apply_standardizer(df, split.fit_standardizer(df))

    tr, va, te = (df[df.split == s].reset_index(drop=True) for s in ("train", "val", "test"))
    kind, tab = targets.select_basis(tr, va, ["linear", 4], steps=150)
    print(tab)
    full = targets.fit_age_model(tr, basis_kind=kind, steps=200)
    noage = targets.fit_age_model(tr, use_age=False, steps=200)
    summ = targets.age_effect_summary(full, noage)
    assert summ["lr_stat"] > 0 and summ["loglik_gain_share"] > 0, summ
    # dihitung ulang dari angka yang tersimpan (dipakai notebook rekonsiliasi) harus sama persis
    assert targets.age_effect_stats(summ["loglik_full"], summ["loglik_noage"], summ["df"]) == \
        {k: summ[k] for k in ("lr_stat", "df", "p_value_lr", "loglik_gain_share")}
    ages = np.logspace(0, 3.5, 20)
    curve = targets.age_curve(full, ages)
    assert curve[-1] > curve[0], "data sintetis punya efek usia positif"
    boots = targets.bootstrap_age_curve(tr, full, ages, n_boot=2, seed=0, steps=100)
    assert boots.shape == (2, 20)
    tab = targets.age_curve_table(full, boots, ages)
    assert list(tab.columns) == ["age_days", "ratio", "lo", "hi", "di_luar_ik"]
    f_oof = targets.oof_age_component(tr, kind, n_folds=3, seed=0, steps=100)
    assert not np.isnan(f_oof).any()
    f_bar = float(f_oof.mean())
    for d, f in ((tr, f_oof), (va, full.f(va.log_age.to_numpy())), (te, full.f(te.log_age.to_numpy()))):
        d["y_t1"] = targets.target_t1(d.helpful_vote)
        d["y_t3"] = targets.target_t3(d.helpful_vote, f, f_bar)
    q1 = targets.fit_grade_thresholds(tr.y_t1)
    q3 = targets.fit_grade_thresholds(tr.y_t1, tr.y_t3)
    for d in (tr, va, te):
        d["grade_t1"] = targets.grades(d.y_t1, q1)
        d["grade_t3"] = targets.grades(d.y_t3, q3)
    assert (tr.grade_t1[tr.helpful_vote == 0] == 0).all()
    print("grade shares T1", np.bincount(tr.grade_t1, minlength=5) / len(tr),
          "T3", np.bincount(tr.grade_t3, minlength=5) / len(tr))

    # pasangan
    ps = PairSampler(tr.parent_asin.to_numpy(), tr.y_t1.to_numpy(), max_pairs=20, seed=0)
    hi, lo = ps.sample()
    assert (tr.y_t1.to_numpy()[hi] > tr.y_t1.to_numpy()[lo]).all()
    assert (tr.parent_asin.to_numpy()[hi] == tr.parent_asin.to_numpy()[lo]).all()
    per = pd.Series(tr.parent_asin.to_numpy()[hi]).value_counts()
    assert per.max() <= 20
    ps2 = PairSampler(tr.parent_asin.to_numpy(), tr.y_t1.to_numpy(), 20, log_age=tr.log_age.to_numpy(),
                      age_window=0.5, seed=0)
    h2, l2 = ps2.sample()
    assert (np.abs(tr.log_age.to_numpy()[h2] - tr.log_age.to_numpy()[l2]) < 0.5).all()
    print("pairs", ps.stats(tr.parent_asin.to_numpy()))

    # loss: RankNet umum dengan target 1 sama dengan bentuk sederhana
    s1, s2 = torch.randn(50), torch.randn(50)
    assert torch.allclose(models.ranknet_loss(s1, s2), models.ranknet_loss_general(s1, s2, torch.ones(50)), atol=1e-6)

    # metrik: urutan sempurna memberi NDCG 1, urutan terbalik < 1
    g = np.array([3, 2, 0, 1])
    pp = metrics.per_product_metrics(["a"] * 4, [4, 3, 1, 2], g, g.astype(float), np.arange(4))
    assert abs(pp["ndcg@10"].iloc[0] - 1) < 1e-12 and abs(pp["spearman"].iloc[0] - 1) < 1e-12
    pp = metrics.per_product_metrics(["a"] * 4, [1, 2, 4, 3], g, g.astype(float), np.arange(4))
    assert pp["ndcg@10"].iloc[0] < 1 and pp["spearman"].iloc[0] < 0
    # AP: relevan (g>=2) di posisi 1 dan 3 -> (1/1 + 2/3)/2
    pp = metrics.per_product_metrics(["a"] * 4, [4, 3, 2, 1], np.array([2, 0, 3, 1]), np.zeros(4) + [1, 0, 2, 0.5],
                                     np.arange(4))
    assert abs(pp["ap"].iloc[0] - (1 + 2 / 3) / 2) < 1e-12

    # fitur dan pelatihan dengan embedding acak berkorelasi target
    rng = np.random.default_rng(0)
    def fake_emb(d):
        e = rng.normal(size=(len(d), 32)).astype(np.float32)
        e[:, 0] += d.y_t1.to_numpy()
        return e / np.linalg.norm(e, axis=1, keepdims=True)
    trs = tr[tr.in_E2].reset_index(drop=True)
    Xtr = features.fuse(fake_emb(trs), trs, "all")
    Xva = features.fuse(fake_emb(va), va, "all")
    Xte = features.fuse(fake_emb(te), te, "all")
    assert Xtr.shape[1] == 32 + 5
    ves = EvalSet(Xva, va.parent_asin.to_numpy(), va.rid.to_numpy(), va.grade_t1.to_numpy(), va.y_t1.to_numpy())
    for loss in ("ranknet", "mse"):
        model, hist, best = train_scorer(Xtr, trs.y_t1.to_numpy(), trs.parent_asin.to_numpy(), ves, loss=loss,
                                         max_epochs=3, patience=2, max_pairs=20, verbose=False, device="cpu")
        assert len(hist) >= 1 and np.isfinite(best)
        print(loss, "best val NDCG@10", round(best, 4))
    # pencatatan sisi latih (Subbab 6c) tidak boleh mengubah lintasan pelatihan
    tes_ = EvalSet(Xtr, trs.parent_asin.to_numpy(), trs.rid.to_numpy(), trs.grade_t1.to_numpy(), trs.y_t1.to_numpy())
    kw = dict(max_epochs=3, patience=2, max_pairs=20, verbose=False, device="cpu", seed=7)
    m0, h0, b0_ = train_scorer(Xtr, trs.y_t1.to_numpy(), trs.parent_asin.to_numpy(), ves, **kw)
    m1, h1, b1_ = train_scorer(Xtr, trs.y_t1.to_numpy(), trs.parent_asin.to_numpy(), ves, train_eval=tes_, **kw)
    sama = [c for c in h0.columns if c != "seconds"]
    assert h0[sama].equals(h1[sama]) and b0_ == b1_, "train_eval mengubah pelatihan"
    assert all(torch.equal(a, b) for a, b in zip(m0.state_dict().values(), m1.state_dict().values()))
    for c in ("train_loss_eval", "train_pair_acc", "val_pair_acc", "train_ndcg@10"):
        assert c in h1 and h1[c].between(0, 10).all(), c
    print("train_eval: riwayat dan bobot identik, metrik sisi latih", h1[["train_pair_acc", "val_pair_acc"]].round(3).values.tolist())
    lin, _, _ = train_scorer(Xtr, trs.y_t1.to_numpy(), trs.parent_asin.to_numpy(), ves, hidden=(),
                             max_epochs=2, verbose=False, device="cpu")
    s_te = predict(model, Xte, "cpu")
    pp_u = metrics.per_product_metrics(te.parent_asin, s_te, te.grade_t1, te.y_t1, te.rid)
    pp_b0 = metrics.per_product_metrics(te.parent_asin, features.score_b0(te), te.grade_t1, te.y_t1, te.rid)
    print("test U", metrics.macro(pp_u), "\ncoverage", metrics.coverage(te, pp_u))
    print(stats.summarize(pp_u, 200))
    d = stats.paired_diff(pp_u, pp_b0, n_boot=200)
    print("U - B0", d)
    print("holm", stats.holm([0.01, 0.04, 0.03]))

    # B1 sklearn pada TF-IDF
    from hr import embed
    vec = embed.fit_tfidf(embed.review_text(trs), max_features=500)
    Xs_tr = features.tfidf_plus_struct(vec, embed.review_text(trs), trs)
    Xs_va = features.tfidf_plus_struct(vec, embed.review_text(va), va)
    clf = features.train_b1(Xs_tr, trs.y_t1.to_numpy(), trs.parent_asin.to_numpy(), C=1.0, max_pairs=20,
                            delta=0.0, seed=0)
    pp_b1 = metrics.per_product_metrics(va.parent_asin, features.score_linear(clf, Xs_va), va.grade_t1, va.y_t1, va.rid)
    print("B1 val", metrics.macro(pp_b1))
    svd = embed.fit_svd(Xs_tr[:, :-5], n_components=16)
    assert svd.transform(Xs_va[:, :-5]).shape[1] == 16

    # validasi manusia
    blind, key = human.make_sheet(te, n_products=8, per_product=4)
    assert "helpful_vote" not in blind.columns and len(blind) == len(key)
    a = rng.integers(1, 6, size=100)
    b = np.clip(a + rng.integers(-1, 2, size=100), 1, 5)
    print("kappa", round(human.weighted_kappa(a, b), 3),
          "alpha", round(human.krippendorff_alpha_interval(np.vstack([a, b])), 3))
    assert human.weighted_kappa(a, a) == 1.0

    if use_hf:
        from hr import finetune
        tiny = "hf-internal-testing/tiny-random-RobertaModel"
        mm = embed.extract_embeddings(va.head(50), tiny, tmp / "emb.npy", max_len=64, batch_size=16)
        assert mm.shape[0] == 50 and np.allclose(np.linalg.norm(mm.astype(np.float32), axis=1), 1, atol=1e-2)
        Ztr = features.struct_matrix(trs, "all").astype(np.float32)
        Zva = features.struct_matrix(va, "all").astype(np.float32)
        ft, tok, fh, fb = finetune.finetune(tiny, trs.head(300), trs.y_t1.to_numpy()[:300], Ztr[:300],
                                            va.head(200), Zva[:200], va.grade_t1.to_numpy()[:200],
                                            va.y_t1.to_numpy()[:200], max_len=64, epochs=1, eval_every=5, products_per_step=4, grad_accum=1,
                                            device="cpu")
        print("finetune", fh.tail(2).to_dict("records"))
        assert fh["step"].max() > 0, "fine-tuning tidak melakukan langkah optimisasi"
    print("\nSMOKE TEST LULUS")


if __name__ == "__main__":
    main(use_hf="--hf" in sys.argv)
