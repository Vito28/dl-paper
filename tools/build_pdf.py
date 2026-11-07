"""LAPORAN.md -> HTML (markdown-it, CommonMark + tabel GFM) -> PDF (WeasyPrint), sesuai format laporan Tugas.

    python tools/build_pdf.py laporan/LAPORAN.md laporan/LAPORAN.pdf [--final]

Butuh markdown-it-py, beautifulsoup4, dan weasyprint (tidak ada di requirements.txt karena hanya untuk laporan).

- Komentar HTML dibuang sebelum dirender.
- Penanda ⟦...⟧ diberi warna. Dengan --final, pembuatan gagal jika masih ada penanda atau berkas gambar yang hilang.
- Daftar Isi tulisan tangan diganti daftar yang dibangun dari judul h1-h3, lengkap dengan nomor halaman.
- Daftar Gambar dan Daftar Tabel memakai judul dari tabel di Markdown, dengan nomor halaman dari posisi keterangan.
- Cover (sebelum div page-break pertama) tanpa nomor halaman, Bagian Awal bernomor romawi, Bagian A mulai dari 1, dan
  Bagian B berada di halaman terakhir tersendiri.
"""
import re, sys, pathlib
from markdown_it import MarkdownIt
from bs4 import BeautifulSoup, NavigableString

src = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]).resolve()
final = "--final" in sys.argv

text = src.read_text(encoding="utf-8")
text = re.sub(r"<!--.*?-->\s*", "", text, flags=re.S)          # comments never reach the PDF
todos = re.findall(r"⟦[^⟧]*⟧", text)
if todos:
    print(f"PERINGATAN: {len(todos)} penanda ⟦…⟧ tersisa:", *todos, sep="\n  ", file=sys.stderr)
    if final:
        sys.exit(1)
text = re.sub(r"(⟦[^⟧]*⟧)", r'<mark class="todo">\1</mark>', text)

md = MarkdownIt("gfm-like", {"html": True, "linkify": True, "typographer": False})
soup = BeautifulSoup(md.render(text), "html.parser")

def slug(s, used):
    b = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "h"
    s, i = b, 2
    while s in used:
        s, i = f"{b}-{i}", i + 1
    used.add(s)
    return s

# ---- split into cover / front / main at the page-break divs -------------------------------
breaks = [d for d in soup.find_all("div") if "page-break-after" in (d.get("style") or "")]
assert len(breaks) >= 3, "expected 3 page-break divs (after cover, after Bagian Awal, before Bagian B)"
parts = {"cover": [], "front": [], "main": []}
order = ["cover", "front", "main"]
k = 0
for node in list(soup.contents):
    if any(node is b for b in breaks[:2]):
        k += 1
        node.extract()
        continue
    parts[order[k]].append(node.extract())
for name in order:
    sec = soup.new_tag("section", attrs={"class": name})
    for n in parts[name]:
        sec.append(n)
    soup.append(sec)

# empty table header rows (the cover table "| | |") are dropped
for thead in soup.find_all("thead"):
    if not thead.get_text(strip=True):
        thead.decompose()

# ---- ids for headings ---------------------------------------------------------------------
used = set()
for h in soup.find_all(["h1", "h2", "h3", "h4"]):
    h["id"] = slug(h.get_text(), used)

# ---- figures: <p><img></p> + <p><em>Gambar N. …</em></p> -> <figure> -----------------------
figs = {}
for p in soup.find_all("p"):
    img = p.find("img")
    if img and p.get_text(strip=True) == "":
        cap = p.find_next_sibling()
        fig = soup.new_tag("figure")
        p.insert_before(fig)
        fig.append(img.extract())
        p.decompose()
        img["class"] = "fig-" + pathlib.Path(img["src"]).stem
        if cap is not None and cap.name == "p" and re.match(r"Gambar \d+\.", cap.get_text(strip=True)):
            n = int(re.match(r"Gambar (\d+)", cap.get_text(strip=True)).group(1))
            fc = soup.new_tag("figcaption", id=f"gambar-{n}")
            for c in list(cap.contents):
                fc.append(c.extract())
            cap.decompose()
            fig.append(fc)
            figs[n] = fc
        else:
            print("PERINGATAN: gambar tanpa keterangan:", img["src"], file=sys.stderr)

# ---- table captions: <p><strong>Tabel N. …</strong></p> directly before a table ------------
tabs = {}
for p in soup.find_all("p"):
    t = p.get_text(strip=True)
    m = re.match(r"Tabel (\d+)\.", t)
    if m and p.find("strong") and len(p.contents) == 1:
        nxt = p.find_next_sibling()
        if nxt is None or nxt.name != "table":
            continue
        n = int(m.group(1))
        p["id"] = f"tabel-{n}"
        p["class"] = "table-caption"
        tabs[n] = p
        wrap = soup.new_tag("div", attrs={"class": "tablewrap"})
        p.insert_before(wrap)
        wrap.append(p.extract())
        wrap.append(nxt.extract())
missing = []
for img in soup.find_all("img"):
    if not (src.parent / img["src"]).exists():
        missing.append(img["src"])
        print("PERINGATAN: berkas gambar tidak ada:", img["src"], file=sys.stderr)
if missing and final:
    sys.exit(1)
for tb in soup.find_all("table"):
    if tb.find_parent("div", class_="tablewrap") is None and not tb.find_parent("section", class_=["cover", "front"]):
        print("PERINGATAN: tabel tanpa judul 'Tabel N.':",
              tb.get_text(" ", strip=True)[:70], file=sys.stderr)
    ncol = len(tb.find("tr").find_all(["th", "td"]))
    longest = max(len(c.get_text()) for c in tb.find_all(["th", "td"]))
    if ncol >= 5 or longest > 40:
        tb["class"] = "wide"
    rows = [tr.find_all(["th", "td"]) for tr in tb.find_all("tr")]
    for c in range(ncol):
        col = [r[c] for r in rows if c < len(r)]
        if max(len(x.get_text(strip=True)) for x in col) <= 18:   # short/numeric column: never break inside
            for x in col:
                x["class"] = "nw"
    w = tb.find_parent("div", class_="tablewrap")
    if w is not None and len(rows) <= 16:
        w["class"] = "tablewrap keep"

# ---- Bagian Awal lists -------------------------------------------------------------------
def section_after(h2):
    """Nodes after an h2 up to the next h2/h1."""
    nodes = []
    for s in h2.next_siblings:
        if getattr(s, "name", None) in ("h1", "h2"):
            break
        nodes.append(s)
    return nodes

def manual_titles(h2):
    titles = {}
    for s in section_after(h2):
        if getattr(s, "name", None) == "table":
            for tr in s.find_all("tr")[1:]:
                td = tr.find_all("td")
                m = re.search(r"(\d+)", td[0].get_text())
                if m:
                    titles[int(m.group(1))] = td[1]
    return titles

def replace_section(h2, new):
    for s in section_after(h2):
        s.extract()
    h2.insert_after(new)

front = soup.find("section", class_="front")
h_isi = front.find("h2", string=re.compile("Daftar Isi"))
h_gbr = front.find("h2", string=re.compile("Daftar Gambar"))
h_tbl = front.find("h2", string=re.compile("Daftar Tabel"))

def entry(href, label, level, roman):
    tr = soup.new_tag("tr", attrs={"class": f"l{level}"})
    t = soup.new_tag("td", attrs={"class": "t"})
    a = soup.new_tag("a", href=f"#{href}")
    for c in list(label.contents):
        a.append(c.extract() if not isinstance(c, NavigableString) else NavigableString(str(c)))
    t.append(a)
    pg = soup.new_tag("td", attrs={"class": "p"})
    pa = soup.new_tag("a", href=f"#{href}", attrs={"class": "pg roman" if roman else "pg"})
    pg.append(pa)
    tr.append(t); tr.append(pg)
    return tr

for h2, store, word in ((h_gbr, figs, "Gambar"), (h_tbl, tabs, "Tabel")):
    titles = manual_titles(h2)
    if set(titles) != set(store):
        print(f"PERINGATAN: Daftar {word} {sorted(titles)} tidak cocok dengan keterangan {sorted(store)}",
              file=sys.stderr)
    ul = soup.new_tag("table", attrs={"class": "lot"})
    for n in sorted(store):
        lab = soup.new_tag("span")
        lab.append(f"{word} {n}. ")
        src_lab = titles.get(n)
        if src_lab is not None:
            for c in list(src_lab.contents):
                lab.append(c.extract())
        else:
            lab.append(store[n].get_text().split(". ", 1)[1].rstrip(".*"))
        ul.append(entry(store[n]["id"], lab, 1, False))
    replace_section(h2, ul)

ul = soup.new_tag("table", attrs={"class": "toc"})
for h in soup.find_all(["h1", "h2", "h3"]):
    if h is h_isi or h.find_parent("section", class_="cover"):
        continue
    lvl = int(h.name[1]) - (0 if h.find_parent("section", class_="front") else 0)
    roman = h.find_parent("section", class_="front") is not None
    lab = soup.new_tag("span")
    for c in h.contents:
        lab.append(c.__copy__() if not isinstance(c, NavigableString) else NavigableString(str(c)))
    ul.append(entry(h["id"], lab, lvl, roman))
replace_section(h_isi, ul)

CSS = r"""
@page { size: A4; margin: 3cm 2.5cm 2.5cm 3cm;
  @bottom-center { content: counter(page); font: 10pt 'Liberation Serif', serif; } }
@page cover { @bottom-center { content: none; } }
@page front { @bottom-center { content: counter(page, lower-roman); } }
section.cover   { page: cover; }
@page :nth(1 of front) { counter-reset: page 1; }
@page :nth(1 of main)  { counter-reset: page 1; }
section.front   { page: front; break-before: page; }
section.main    { page: main; break-before: page; }
html { font-family: 'Liberation Serif', 'Times New Roman', 'DejaVu Serif', serif; font-size: 11.5pt;
       line-height: 1.4; text-align: justify; hyphens: manual; }
h1, h2, h3, h4 { text-align: left; break-after: avoid; line-height: 1.2; }
h1 { font-size: 16pt; margin: 0 0 .6em; }
h2 { font-size: 13.5pt; margin: 1.1em 0 .4em; }
h3 { font-size: 12pt; margin: 1em 0 .3em; }
h4 { font-size: 11.5pt; font-style: italic; margin: .9em 0 .3em; }
section.front h2 { break-before: page; font-size: 15pt; text-align: center; }
section.front h2:first-child { break-before: auto; }
/* cover */
section.cover { text-align: center; padding-top: 4cm; }
section.cover h1 { font-size: 20pt; margin-bottom: 2cm; text-align: center; }
section.cover table { margin: 0 auto; font-size: 12pt; border: none; width: 80%; }
section.cover ul { list-style: none; margin: 0 auto; padding: 0; width: 75%; font-size: 12pt; text-align: left; }
section.cover li { margin: 0 0 .7em; }
section.cover td { border: none; text-align: left; padding: 4pt 6pt; }
/* tables */
.tablewrap { margin: .8em 0 1em; }
.table-caption { break-after: avoid; margin-bottom: .3em; text-align: left; }
table { border-collapse: collapse; font-size: 9pt; line-height: 1.25; text-align: left; max-width: 100%; }
table.wide { width: 100%; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { background: #e8e8e8; }
th, td { border: .5pt solid #555; padding: 2pt 4pt; vertical-align: top; overflow-wrap: break-word; }
th.nw, td.nw { white-space: nowrap; }
.tablewrap.keep { break-inside: avoid; }
/* figures */
figure { margin: .8em 0 1em; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; max-height: 11cm; width: auto; height: auto; }
figure img.fig-arsitektur_model { max-height: 13.5cm; }
figure img.fig-kurva_pelatihan_semua_seed { max-height: 18cm; }
figure img.fig-uji_confusion_matrix_B4, figure img.fig-age_kurva { max-height: 8.5cm; }
figcaption { font-size: 10pt; text-align: center; margin-top: .3em; }
/* code */
pre { font-size: 8pt; line-height: 1.25; background: #f4f4f4; border: .5pt solid #ccc; padding: 5pt 7pt;
      white-space: pre-wrap; overflow-wrap: anywhere; text-align: left; break-inside: avoid; }
code { font-family: 'DejaVu Sans Mono', 'Liberation Mono', monospace; font-size: .85em; }
pre code { font-size: 1em; }
a { color: #1a4f9c; text-decoration: none; overflow-wrap: anywhere; }
mark.todo { background: #ffe14d; }
ol, ul { text-align: left; }
/* generated lists (Daftar Isi / Gambar / Tabel) */
table.toc, table.lot { width: 100%; border: none; font-size: 10.5pt; line-height: 1.3; }
table.toc td, table.lot td { border: none; padding: 1pt 0; }
table.toc tr:not(.l1) td, table.lot td { overflow: hidden; }
td.t a { color: inherit; }
td.t a::after { content: leader('. '); }
td.p { width: 2.2em; text-align: right; vertical-align: bottom; }
td.p a.pg { color: inherit; }
td.p a.pg::after { content: target-counter(attr(href), page); }
td.p a.pg.roman::after { content: target-counter(attr(href), page, lower-roman); }
table.lot td.t { padding-left: 4.4em; text-indent: -4.4em; }
table.toc tr.l1 td { font-weight: bold; padding-top: .45em; }
table.toc tr.l2 td.t { padding-left: 1.2em; }
table.toc tr.l3 td.t { padding-left: 2.6em; }
table.toc tr.l3 td { font-size: 10pt; }
"""
html = ("<!DOCTYPE html><html lang='id'><head><meta charset='utf-8'><title>Laporan Proyek UAS</title>"
        f"<style>{CSS}</style></head><body>{soup}</body></html>")
out.with_suffix(".html").write_text(html, encoding="utf-8")   # for debugging only
from weasyprint import HTML
HTML(string=html, base_url=str(src.parent) + "/").write_pdf(str(out))   # gambar/… resolves against the .md folder
print("ok", out, "| gambar:", len(figs), "tabel:", len(tabs), "| penanda:", len(todos))
