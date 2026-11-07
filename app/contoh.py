"""Contoh produk untuk aplikasi demo.

Ada dua jenis contoh.
- Contoh buatan: ulasan fiktif yang ditulis untuk demo, tanpa helpful votes.
- Contoh asli: ulasan asli dari produk **data uji** Amazon Reviews 2023 (kategori Video_Games), dibaca dari
  artefak/contoh_produk_uji.json jika berkas itu ada. Produk data uji tidak pernah dilihat model saat pelatihan,
  sehingga urutan model dapat dibandingkan secara jujur dengan suara pembaca sebenarnya.

Helpful votes bukan masukan model dan tidak muncul di tabel masukan. Untuk contoh asli, helpful votes disimpan
terpisah di "suara" (pasangan (judul, isi) -> helpful votes) dan hanya dipakai untuk evaluasi setelah pemeringkatan.
"""
from __future__ import annotations

import json
from pathlib import Path

KOLOM = ["Judul", "Isi ulasan", "Rating (1-5)", "Pembelian terverifikasi"]

# (judul, isi, rating, terverifikasi)
_BUATAN = {
    "Contoh buatan 1: gim aksi fiktif (5 ulasan)": [
        ("Five Stars", "Great game", 5, True),
        ("Fun but the campaign is short",
         "I finished the story in about six hours on normal difficulty. Combat feels tight and the boss fights are "
         "creative, but there is little reason to replay. Online co-op adds some value if you have friends who own "
         "it. Wait for a sale unless you only care about the campaign.", 4, True),
        ("Do not buy the digital deluxe edition",
         "The deluxe edition only adds two cosmetic skins and a soundtrack you can stream for free. The base game is "
         "the same. Save your money.", 2, True),
        ("Love it", "My son plays it every day after school.", 5, False),
        ("Crashes on older consoles",
         "On the original console model the game crashes when loading the third area. Clearing the system cache and "
         "reinstalling fixed it for me, and the latest patch improved loading times. On the newer model it runs "
         "smoothly at a stable frame rate. Check your hardware before buying.", 3, True),
    ],
    "Contoh buatan 2: headset gaming fiktif (8 ulasan)": [
        ("Good", "Works fine.", 4, True),
        ("Comfortable for long sessions, mic is average",
         "I have used this headset for about three months, mostly four to five hour sessions. The memory foam pads "
         "do not press on my glasses, which was my main concern. Positional audio is clear enough to hear footsteps "
         "in shooters. The microphone picks up keyboard noise, so friends asked me to use push-to-talk.", 4, True),
        ("Broke after two weeks", "The left ear cup stopped working after two weeks. Very disappointed.", 1, True),
        ("Five Stars", "Awesome sound!!!", 5, True),
        ("Read this if you play on console",
         "The box says it works with every console, but on my console the chat audio only works through the "
         "included 3.5 mm adapter, not over USB. Game sound works over USB. Once I switched to the adapter "
         "everything worked, including the mute button. The manual does not mention this.", 3, True),
        ("Cheap feel", "Plastic headband creaks when you move. Sound is ok for the price.", 3, False),
        ("Gift", "Bought it for my nephew, he likes it.", 5, True),
        ("Better than my old headset",
         "Bass is stronger than my previous headset and the cable is braided and long enough to reach my couch. "
         "The volume wheel is easy to find without looking. No software is needed, it just works.", 5, True),
    ],
    "Contoh buatan 3: kontroler nirkabel fiktif (12 ulasan)": [
        ("Perfect", "Perfect controller.", 5, True),
        ("Stick drift after six months",
         "The left stick started drifting after about six months of daily use. Recalibrating in the settings menu "
         "helped for a week. Support offered a replacement but I had to pay for shipping. The buttons and triggers "
         "still feel great, so the stick quality is the real problem.", 2, True),
        ("Battery life is the best part",
         "I charge it about once a week with two hours of play per day. The charging cable is USB-C and the light "
         "turns green when full. It takes about three hours to charge completely.", 5, True),
        ("ok", "its ok", 3, False),
        ("Does not work with my PC out of the box",
         "Bluetooth pairing with my PC kept disconnecting. The fix was installing the driver from the manufacturer's "
         "website and updating the controller firmware, which needs the cable. After that it has been stable for a "
         "month. On the console it paired instantly.", 4, True),
        ("Great", "Love the color!", 5, True),
        ("Too heavy for small hands",
         "My daughter has small hands and finds it heavy after an hour. For adult hands it is comfortable.", 3, True),
        ("Five Stars", "Excellent", 5, True),
        ("Comparison with the official controller",
         "I own both. This one has better grip texture and back paddles you can remap without software. The official "
         "one has better vibration and a slightly lower input delay that I only notice in rhythm games. For half "
         "the price this is the better deal for most people.", 4, True),
        ("Arrived damaged", "Box was crushed and the D-pad was stuck. Returned it.", 1, True),
        ("Works", "Works as described.", 4, True),
        ("Back paddles are a game changer",
         "Being able to jump and reload without taking my thumbs off the sticks made a real difference in shooters. "
         "Mapping takes ten seconds with the button combo in the manual.", 5, True),
    ],
}

BERKAS_ASLI = Path(__file__).resolve().parent / "artefak" / "contoh_produk_uji.json"


def kunci(judul, isi) -> tuple[str, str]:
    """Kunci pencocokan ulasan dengan helpful votes asli. Sel kosong dianggap teks kosong."""
    return tuple("" if v is None or (isinstance(v, float) and v != v) else str(v).strip() for v in (judul, isi))


def muat_contoh() -> dict[str, dict]:
    """Nama contoh -> {"baris": baris tabel, "keterangan": teks penjelasan, "suara": helpful votes asli per
    kunci(judul, isi), atau None untuk contoh buatan}."""
    contoh = {nama: {"baris": [list(x) for x in u], "suara": None,
                     "keterangan": "Ulasan fiktif yang ditulis untuk demo, tanpa helpful votes asli."}
              for nama, u in _BUATAN.items()}
    if BERKAS_ASLI.exists():
        data = json.loads(BERKAS_ASLI.read_text())
        for i, p in enumerate(data["produk"], start=1):   # produk yang dikecualikan sudah dihapus dari berkas
            nama = f"Produk uji asli {i}: {p['parent_asin']} ({len(p['ulasan'])} ulasan)"
            baris = [[u["judul"], u["isi"], u["rating"], u["terverifikasi"]] for u in p["ulasan"]]
            suara = {kunci(u["judul"], u["isi"]): u["helpful_vote"] for u in p["ulasan"]}
            if len(suara) != len(baris):
                raise ValueError(f"{p['parent_asin']}: ada ulasan kembar (judul, isi), helpful votes tidak bisa dicocokkan")
            contoh[nama] = {"baris": baris, "suara": suara, "keterangan": (
                f"Ulasan asli produk `{p['parent_asin']}` dari data uji Amazon Reviews 2023 (kategori "
                f"{data['kategori']}), yang tidak pernah dilihat model saat pelatihan. Helpful votes asli tidak "
                f"diberikan ke model. Setelah ulasan diurutkan, suara itu ditampilkan di hasil agar urutan model dapat "
                f"dibandingkan dengan suara pembaca. Urutan baris di tabel diacak. Halaman produk: "
                f"https://www.amazon.com/dp/{p['parent_asin']}")}
    return contoh
