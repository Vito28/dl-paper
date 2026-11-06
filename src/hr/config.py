"""Konfigurasi eksperimen.

Semua nilai yang harus ditetapkan sebelum eksperimen (kategori, seed, proporsi split,
skala data, grid hiperparameter, ambang relevansi) dikumpulkan di sini agar tidak
tersebar di notebook. Ubah nilai lewat ``Config(...)`` di sel pertama setiap notebook,
bukan dengan mengedit kode di tengah notebook.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

HF_RAW_URL = (
    "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/"
    "raw/review_categories/{category}.jsonl"
)

# Encoder yang dibandingkan. B5 memakai RoBERTa-base karena BLaIR dilatih lanjut dari model ini.
ENCODERS = {
    "blair": "hyp1231/blair-roberta-base",
    "roberta": "FacebookAI/roberta-base",
}

RAW_COLUMNS = [
    "rating", "title", "text", "asin", "parent_asin", "user_id",
    "timestamp", "helpful_vote", "verified_purchase",
]

# Fitur terstruktur (Subbab 3.3 dan 3.7). Usia ulasan dan helpful_vote TIDAK boleh masuk ke sini.
STRUCT_FEATURES = [
    "rating", "verified_purchase", "log_review_length", "log_word_count", "log_title_length",
]
FORBIDDEN_FEATURES = {"helpful_vote", "age_days", "log_age", "y_t1", "y_t3", "grade_t1", "grade_t3"}

# Registri eksperimen (Tabel 3.5). "priority" mengikuti usulan di kritik-reviewer.md:
# 1 = wajib, 2 = penting, 3 = opsional. Atur Config.run_priority untuk memilih yang dijalankan.
EXPERIMENTS = {
    "B0": dict(kind="heuristic", priority=1, desc="Urutan berdasarkan panjang isi ulasan"),
    "B1": dict(kind="sklearn", rep="tfidf", model="linear", loss="ranknet", feats="all", priority=1,
               desc="TF-IDF + fitur, ranker linear pairwise"),
    "B2": dict(kind="torch", rep="tfidf_svd", model="mlp", loss="ranknet", feats="all", priority=3,
               desc="TF-IDF (SVD 768) + fitur, MLP pairwise"),
    "B3": dict(kind="torch", rep="blair", model="linear", loss="ranknet", feats="all", priority=3,
               desc="BLaIR + fitur, ranker linear pairwise"),
    "B4": dict(kind="torch", rep="blair", model="mlp", loss="mse", feats="all", priority=1,
               desc="BLaIR + fitur, MLP pointwise MSE"),
    "B5": dict(kind="torch", rep="roberta", model="mlp", loss="ranknet", feats="all", priority=1,
               desc="RoBERTa-base beku + fitur, MLP pairwise"),
    "U": dict(kind="torch", rep="blair", model="mlp", loss="ranknet", feats="all", priority=1,
              desc="Model utama: BLaIR + fitur, MLP RankNet"),
    "A1": dict(kind="torch", rep="blair", model="mlp", loss="ranknet", feats=[], priority=3,
               desc="Ablasi: embedding saja"),
    "A2": dict(kind="torch", rep="blair", model="mlp", loss="ranknet", feats=["rating"], priority=3,
               desc="Ablasi: + rating"),
    "A3": dict(kind="torch", rep="blair", model="mlp", loss="ranknet",
               feats=["rating", "verified_purchase"], priority=3, desc="Ablasi: + verified_purchase"),
    # A4 = U (seluruh fitur), tidak dilatih ulang.
}
# Baris tabel perbandingan baseline (validasi di notebook 05, uji di notebook 07). Ablasi A1-A3 punya tabel sendiri.
BASELINE_CODES = ["B0", "B1", "B2", "B3", "B4", "B5", "U"]
SCALE_PRIORITY = {"E1": 2, "E2": 3, "E3": 2, "E4": 3, "E5": 2}
TARGET_PRIORITY = {"T1": 1, "T2": 3, "T3": 2}


def _default_root() -> Path:
    env = os.environ.get("HR_ROOT")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2]


@dataclass
class Config:
    # --- data
    category: str = "Video_Games"          # KEPUTUSAN KELOMPOK: kategori dipilih sebelum eksperimen
    root: Path = field(default_factory=_default_root)
    seed: int = 42
    product_sample_rate: float = 1.0       # <1.0 untuk mengambil sebagian produk saat membaca file besar
    min_reviews_per_product: int = 2
    split_frac: tuple = (0.8, 0.1, 0.1)
    max_eval_reviews: int = 200_000        # batas ulasan per partisi validasi/uji (diambil per produk utuh)
    max_train_reviews_per_product: int = 200
    scales: dict = field(default_factory=lambda: {
        "E1": 100_000, "E2": 250_000, "E3": 500_000, "E4": 750_000, "E5": 1_000_000})
    main_scale: str = "E3"                 # skala untuk perbandingan baseline, ablasi, dan target
    main_target: str = "T1"                # target untuk perbandingan utama (lihat EXPERIMENTS.md)
    # --- encoder
    encoders: dict = field(default_factory=lambda: dict(ENCODERS))
    max_len: int = 512
    embed_batch: int = 64
    # --- pasangan
    max_pairs_per_product: int = 100       # M pada persamaan (3.5)
    pair_delta: float = 0.0                # delta pada persamaan (3.5)
    age_window_grid: tuple = (0.25, 0.5, 1.0)   # Delta_a untuk T2, dalam satuan log(1 + hari)
    # --- pelatihan
    hidden: tuple = (256, 64)
    batch_pairs: int = 1024
    batch_points: int = 1024
    max_epochs: int = 30
    patience: int = 3
    weight_decay: float = 1e-5
    lr_grid: tuple = (1e-4, 3e-4, 1e-3)
    dropout_grid: tuple = (0.1, 0.2, 0.3)
    linear_c_grid: tuple = (0.1, 1.0, 10.0)
    seeds: tuple = (42, 43, 44)
    # --- target dan evaluasi
    map_relevant_grade: int = 2            # ulasan relevan untuk MAP jika g >= 2 (ditetapkan sebelum eksperimen)
    age_basis_grid: tuple = ("linear", 4, 6, 8)
    n_folds_age: int = 5
    age_bootstrap: int = 100
    eval_bootstrap: int = 1000
    run_priority: int = 3                  # 1 = wajib saja, 2 = + penting, 3 = semua
    # --- penyimpanan
    storage_mount: str | None = None       # mis. "/content/drive". Jika diisi, setiap akses path gagal keras
                                           # saat mount ini hilang, agar tidak diam-diam menulis ke disk instance

    # ------------------------------------------------------------------ paths
    def _root(self) -> Path:
        if self.storage_mount and not os.path.ismount(self.storage_mount):
            raise RuntimeError(
                f"{self.storage_mount} tidak ter-mount (Google Drive terputus atau sudah di-unmount). "
                "Berhenti agar data tidak tertulis ke disk instance yang hilang saat sesi berakhir. "
                "Restart runtime lalu jalankan ulang sel setup.")
        return Path(self.root)

    @property
    def data_dir(self) -> Path:
        return self._root() / "data"

    @property
    def raw_path(self) -> Path:
        return self.data_dir / "raw" / f"{self.category}.jsonl"

    @property
    def out_dir(self) -> Path:
        return self._root() / "outputs" / self.category

    def path(self, *parts: str) -> Path:
        """Path di dalam folder output kategori. Folder induk dibuat otomatis."""
        p = self.out_dir.joinpath(*parts)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def as_json(self) -> dict:
        """Pengaturan dalam bentuk yang sama persis dengan isi config.json (tuple menjadi list, dst.)."""
        return json.loads(json.dumps(asdict(self), default=str))

    def save(self) -> Path:
        p = self.path("config.json")
        p.write_text(json.dumps(self.as_json(), indent=2))
        return p

    def experiments_to_run(self) -> list[str]:
        return [k for k, v in EXPERIMENTS.items() if v["priority"] <= self.run_priority]

    def scales_to_run(self) -> list[str]:
        return [k for k, p in SCALE_PRIORITY.items() if p <= self.run_priority]

    def targets_to_run(self) -> list[str]:
        return [k for k, p in TARGET_PRIORITY.items() if p <= self.run_priority]


def smoke_config(root: Path) -> Config:
    """Konfigurasi uji cepat dengan data sintetis dan model mini. Dipakai jika HR_SMOKE=1.
    Hasilnya tidak bermakna secara ilmiah, hanya untuk memastikan semua notebook berjalan."""
    tiny = "hf-internal-testing/tiny-random-RobertaModel"
    return Config(category="Synthetic", root=Path(root) / "smoke", max_eval_reviews=10_000,
                  scales={"E1": 1500, "E2": 3000, "E3": 5000, "E4": 6000, "E5": 7000}, main_scale="E2",
                  encoders={"blair": tiny, "roberta": tiny}, max_len=64, embed_batch=32, max_epochs=3,
                  patience=2, lr_grid=(1e-3, 3e-3), dropout_grid=(0.1,), linear_c_grid=(1.0,), seeds=(42, 43),
                  age_basis_grid=("linear", 4), n_folds_age=3, age_bootstrap=3, eval_bootstrap=200,
                  age_window_grid=(0.5, 1.0))
