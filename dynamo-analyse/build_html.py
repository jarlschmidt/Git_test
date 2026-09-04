#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, html, os
from datetime import date
from urllib.parse import urlparse
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, "data", "dataset.json"), encoding="utf-8") as f:
    D = json.load(f)
with open(os.path.join(BASE, "data", "dtu_institutes.json"), encoding="utf-8") as f:
    INSTITUTES = json.load(f)
with open(os.path.join(BASE, "data", "dtu_strategy.json"), encoding="utf-8") as f:
    STRATEGY = json.load(f)
with open(os.path.join(BASE, "data", "world_events.json"), encoding="utf-8") as f:
    WORLD_EVENTS = json.load(f)
STORIES_PATH = os.path.join(BASE, "data", "stories.json")
if os.path.exists(STORIES_PATH):
    with open(STORIES_PATH, encoding="utf-8") as f:
        STORIES = json.load(f)
else:
    STORIES = []

# Page numbers in the TOC are measured after a first render pass (see
# measure_toc.py) and cached here, since sections now flow freely across
# pages instead of one forced page break per section.
TOC_PAGES_PATH = os.path.join(BASE, "data", "toc_pages.json")
if os.path.exists(TOC_PAGES_PATH):
    with open(TOC_PAGES_PATH, encoding="utf-8") as f:
        TOC_PAGES = json.load(f)
else:
    TOC_PAGES = {}

issues = D["issues"]
eras = D["eras"]
era_cat = D["era_cat"]
cat_totals = D["cat_totals"]
conf_counts = D["conf_counts"]

def esc(s):
    return html.escape(str(s), quote=False)

TOTAL = len(issues)
# "Documented" = we found and described the issue (confidence high/medium/low),
# which is NOT the same as "has a single labeled theme" — a handful of issues
# are genuine general-interest numbers with no one cover theme (theme == ""),
# but they were still researched from a primary source, so they count here.
# This must stay in sync with conf_counts (high+medium+low), or the "andel
# dokumenteret" stat and its own donut chart would show two different numbers.
DOCUMENTED = sum(1 for i in issues if i.get("confidence") in ("high","medium","low"))
PCT_DOC = round(100*DOCUMENTED/TOTAL)

STORY_COUNT = len(STORIES)
STORY_ISSUE_NUMS = sorted(set(s["issue_number"] for s in STORIES))
STORY_ISSUE_COUNT = len(STORY_ISSUE_NUMS)
STORY_INST_COUNTER = Counter(s["institute"] for s in STORIES if s.get("institute"))
STORY_WITH_INST = sum(1 for s in STORIES if s.get("institute"))
STORY_INST_PCT = round(100*STORY_WITH_INST/STORY_COUNT) if STORY_COUNT else 0
STORY_UNCOVERED = [41, 83, 84, 85, 86]
STORY_COUNT_DA = f"{STORY_COUNT:,}".replace(",", ".")

# ---------- helpers to render CSS bar rows ----------
def bar_rows(pairs, max_val=None, color="var(--dtu-blue)", highlight_first=False, val_suffix=""):
    """pairs: list of (label, value)"""
    if not pairs:
        return "<p class='small'>Ingen data.</p>"
    mx = max_val or max(v for _, v in pairs) or 1
    out = ["<div class='barchart'>"]
    for i, (label, val) in enumerate(pairs):
        pct = max(2, round(100*val/mx))
        c = "var(--dtu-orange)" if (highlight_first and i == 0) else color
        out.append(
            f"<div class='barrow'><div class='lbl'>{esc(label)}</div>"
            f"<div class='track'><div class='fill' style='width:{pct}%; background:{c};'></div></div>"
            f"<div class='val'>{val}{val_suffix}</div></div>"
        )
    out.append("</div>")
    return "".join(out)

def stat_tile(big, label):
    return f"<div class='tile'><b>{esc(big)}</b><span class='lbl'>{esc(label)}</span></div>"

def domain_label(url):
    try:
        netloc = urlparse(url).netloc
        return netloc[4:] if netloc.startswith("www.") else netloc
    except ValueError:
        return url

def source_links(urls):
    if not urls:
        return "<span class='small'>–</span>"
    return " · ".join(f"<a class='src' href='{esc(u)}'>{esc(domain_label(u))}</a>" for u in urls)

# ---------- fixed categorical palette (validated: node scripts/validate_palette.js
# from the dataviz skill — 6 hues, all checks pass) ----------
# Every chart in the report that breaks down by theme-category uses this SAME
# category -> color mapping, assigned once in fixed rank order (never re-cycled
# per-chart), with anything past the top 6 folded into one grey "Øvrige temaer".
CAT_PALETTE = ["#fc7634", "#2f3eea", "#e83f48", "#1fd082", "#79238e", "#008835"]
OTHER_COLOR = "#9a9a91"
OTHER_LABEL = "Øvrige temaer"
_cats_by_count = sorted(cat_totals.items(), key=lambda x: -x[1])
TOP_CATS = [c for c, _ in _cats_by_count[:6]]
CAT_COLOR = {c: CAT_PALETTE[i] for i, c in enumerate(TOP_CATS)}

def cat_color(cat):
    return CAT_COLOR.get(cat, OTHER_COLOR)

# ---------- donut chart (inline SVG, stroke-dasharray technique) ----------
def donut_svg(pairs, size_mm=40, hole_num=None, hole_sub=None):
    """pairs: list of (label, color, value)."""
    total = sum(v for _, _, v in pairs) or 1
    r = 15.9155
    cum = 0.0
    arcs = []
    for _, color, val in pairs:
        pct = 100 * val / total
        if pct <= 0:
            continue
        dashoffset = 25 - cum
        arcs.append(
            f'<circle cx="21" cy="21" r="{r}" fill="transparent" stroke="{color}" '
            f'stroke-width="6.4" stroke-dasharray="{pct:.3f} {100-pct:.3f}" '
            f'stroke-dashoffset="{dashoffset:.3f}"/>'
        )
        cum += pct
    center = ""
    if hole_num is not None:
        center = f'<text x="21" y="20.5" text-anchor="middle" class="donut-num">{esc(hole_num)}</text>'
        if hole_sub:
            center += f'<text x="21" y="26" text-anchor="middle" class="donut-sub">{esc(hole_sub)}</text>'
    return (
        f'<svg viewBox="0 0 42 42" class="donut" width="{size_mm}mm" height="{size_mm}mm">'
        f'<circle cx="21" cy="21" r="{r}" fill="transparent" stroke="var(--grid)" stroke-width="6.4"/>'
        f'{"".join(arcs)}{center}</svg>'
    )

def donut_legend(pairs):
    """pairs: list of (label, color, value)."""
    total = sum(v for _, _, v in pairs) or 1
    rows = []
    for label, color, val in pairs:
        pct = round(100 * val / total)
        rows.append(
            f"<div class='donut-legend-row'><span class='sw' style='background:{color};'></span>"
            f"<span class='donut-legend-lbl'>{esc(label)}</span><b>{val}</b>"
            f"<span class='small'>({pct}%)</span></div>"
        )
    return "<div class='donut-legend'>" + "".join(rows) + "</div>"

def donut_with_legend(pairs, hole_num=None, hole_sub=None, size_mm=40):
    """pairs: list of (label, color, value)."""
    return (
        "<div class='donut-wrap'>"
        f"{donut_svg(pairs, size_mm=size_mm, hole_num=hole_num, hole_sub=hole_sub)}"
        f"{donut_legend(pairs)}"
        "</div>"
    )

# ---------- stacked year-by-year theme chart ----------
def year_cat_lookup(year):
    yc = D.get("year_cat", {})
    return yc.get(str(year), yc.get(year, {})) or {}

def stacked_year_chart(years):
    stack_order = TOP_CATS + [OTHER_LABEL]
    col_segs = {}
    max_total = 1
    for y in years:
        counts = year_cat_lookup(y)
        segs = [(c, counts.get(c, 0)) for c in TOP_CATS]
        other = sum(v for c, v in counts.items() if c not in TOP_CATS)
        segs.append((OTHER_LABEL, other))
        col_segs[y] = segs
        max_total = max(max_total, sum(v for _, v in segs))
    highlight = {2005, 2011, 2026}
    cols = []
    for y in years:
        parts = "".join(
            f'<div class="ybar-seg" style="height:{100*v/max_total:.2f}%; background:{cat_color(c)};"></div>'
            for c, v in col_segs[y] if v > 0
        )
        label = f"<span>{y}</span>" if y in highlight else "<span>&nbsp;</span>"
        cols.append(f'<div class="ybar-col"><div class="ybar-stack">{parts}</div>{label}</div>')
    legend_pairs = [(c, cat_color(c), sum(counts.get(c, 0) for counts in (year_cat_lookup(y) for y in years))) for c in stack_order]
    legend = "".join(
        f"<div class='donut-legend-row'><span class='sw' style='background:{color};'></span>"
        f"<span class='donut-legend-lbl'>{esc(label)}</span></div>"
        for label, color, _ in legend_pairs
    )
    return (
        f"<div class='ybar-chart'>{''.join(cols)}</div>"
        f"<div class='donut-legend donut-legend--row'>{legend}</div>"
    )

# ---------- simple honest line chart (few real data points, no interpolation guessing) ----------
def line_chart_svg(points, y_suffix="", w=170, h=42, pad=22, pad_top=8):
    vals = [v for _, v in points]
    mx, mn = max(vals), 0
    n = len(points)
    xs = [pad + (w - 2*pad) * i / (n - 1) if n > 1 else w / 2 for i in range(n)]
    ys = [pad_top + (h - pad_top) * (1 - (v - mn) / (mx - mn)) if mx > mn else h / 2 for v in vals]
    path = " ".join(f"{'M' if i == 0 else 'L'}{xs[i]:.1f},{ys[i]:.1f}" for i in range(n))
    area = path + f" L{xs[-1]:.1f},{h} L{xs[0]:.1f},{h} Z"
    dots = "".join(f'<circle cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="2" fill="var(--dtu-blue)"/>' for i in range(n))
    vlabels = "".join(
        f'<text x="{xs[i]:.1f}" y="{ys[i]-4:.1f}" font-size="4.6" font-weight="700" text-anchor="middle" fill="var(--dtu-navy)">{esc(f"{points[i][1]:,}".replace(",", "."))}{y_suffix}</text>'
        for i in range(n)
    )
    xlabels = "".join(
        f'<text x="{xs[i]:.1f}" y="{h+8}" font-size="3.6" text-anchor="middle" fill="var(--muted)">{esc(points[i][0])}</text>'
        for i in range(n)
    )
    return (
        f'<svg viewBox="0 0 {w} {h+12}" class="line-chart" preserveAspectRatio="none" style="width:100%; height:42mm;">'
        f'<path d="{area}" fill="var(--dtu-blue)" opacity="0.12" stroke="none"/>'
        f'<path d="{path}" fill="none" stroke="var(--dtu-blue)" stroke-width="1.1"/>'
        f'{dots}{vlabels}{xlabels}</svg>'
    )

# ---------- world-events correlation timeline ----------
def peak_year_for(cat):
    best_year, best_n = None, -1
    for y in range(2005, 2027):
        n = year_cat_lookup(y).get(cat, 0)
        if n > best_n:
            best_n, best_year = n, y
    return best_year, best_n

def world_events_timeline():
    rows = []
    for ev in WORLD_EVENTS:
        y = ev["year"]
        cat = ev["category"]
        n_this_year = year_cat_lookup(y).get(cat, 0)
        peak_y, peak_n = peak_year_for(cat)
        if peak_y == y and peak_n > 0:
            dynamo_note = f"<b>{esc(cat)}</b> topper i {y} ({peak_n} numre) — det højeste antal i hele Dynamos historie for dette tema."
        elif n_this_year > 0:
            dynamo_note = f"Dynamo bragte {n_this_year} nummer/numre om <b>{esc(cat)}</b> i {y}."
        else:
            dynamo_note = f"Ingen numre dokumenteret med tema <b>{esc(cat)}</b> i netop {y} (kan skyldes datadækningen, se metodeafsnittet)."
        rows.append(f"""
        <div class="tl-row-v">
          <div class="tl-year-col"><div class="tl-dot" style="background:{cat_color(cat)};"></div><b>{y}</b></div>
          <div class="tl-body">
            <p><b>{esc(ev['label'])}</b> — <a class="src" href="{esc(ev['source_url'])}">{esc(ev['source_title'])}</a></p>
            <p class="small">{dynamo_note}</p>
          </div>
        </div>""")
    return "<div class='timeline-v'>" + "".join(rows) + "</div>"

def year_track_html():
    year_counts = D["year_counts"]
    years = list(range(2005, 2027))
    mx = max(year_counts.get(str(y), year_counts.get(y, 0)) for y in years) or 1
    highlight = {2005, 2011, 2026}
    ticks = []
    for y in years:
        n = year_counts.get(str(y), year_counts.get(y, 0))
        h = max(14, round(100 * n / mx)) if n else 8
        cls = "ytick hi" if y in highlight else "ytick"
        label = f"<span>{y}</span>" if y in highlight else "<span>&nbsp;</span>"
        ticks.append(f"<div class='{cls}'><i style='height:{h}%;'></i>{label}</div>")
    return "<div class='yeartrack'>" + "".join(ticks) + "</div>"

# ================= COVER =================
today = date.today().strftime("%d. %B %Y")
cover = f"""
<div class="cover">
  <div class="cover-bignum">21</div>
  <div class="cover-top">
    <div class="eyebrow"><i></i>Medieanalyse · DTU</div>
    <h1>Dynamo gennem&nbsp;20&nbsp;år</h1>
    <div class="sub">Hvad har DTU fortalt om sig selv de sidste 21 år? En komplet gennemgang af profilmagasinet Dynamos historier, temaer og institutter — fra lanceringen i 2005 til i dag.</div>
  </div>
  <div class="cover-spacer"></div>
  <div class="cover-card">
    <div class="stats">
      {"".join(f'<div class="stat"><b>{esc(b)}</b><span class="lbl">{esc(l)}</span></div>' for b,l in [
          (TOTAL, "Numre udgivet"), (STORY_COUNT_DA, "Historier i fuld tekst"), (f"{PCT_DOC}%", "Numre tema-dokumenteret"), ("~4", "Numre pr. år")
      ])}
    </div>
    {year_track_html()}
    <p class="small caption">Numre pr. udgivelsesår, 2005–2026 (interpoleret hvor eksakt måned er ukendt)</p>
  </div>
  <div class="footline"><span>Kilder: issuu.com/dtudk · DTU nyhedsarkiv (dtu.dk)</span><span>{esc(today)}</span></div>
</div>
"""

# ================= TOC =================
# Fallback estimates are only used before the first measurement pass has run
# (see measure_pages.js / README) — after that, TOC_PAGES holds real numbers.
toc_items = [
    ("exec", "Executive summary", 3),
    ("metode", "Metode og datagrundlag", 3),
    ("historie", "Dynamo gennem tiden — historien", 3),
    ("temaer", "Temaer på tværs af 21 år", 4),
    ("temaeraar", "Temaer år for år", 4),
    ("verden", "Falder Dynamo sammen med verden?", 5),
    ("temaudvikling", "Temaudvikling: tre æraer", 5),
    ("strategi", "Temaerne og DTU's strategi 2026–2031", 6),
    ("institutter", "Institutter i Dynamo", 6),
    ("oplag", "Oplag og målgruppe over tid", 7),
    ("appendiks", "Appendiks A: alle katalogiserede numre", 8),
    ("appendiks-b", "Appendiks B: alle historier 2015–2026", 9),
    ("kilder", "Kilder og forbehold", 11),
]
toc = "<div class='section' id='sec-toc'><div class='kicker'>Indhold</div><h2>Indholdsfortegnelse</h2>"
toc += "".join(f"<div class='toc-row'><span>{esc(t)}</span><span>{TOC_PAGES.get(k, p)}</span></div>" for k,t,p in toc_items)
toc += "<p class='small' style='margin-top:8mm;'>Rapporten er søgbar (fuld tekst) — brug Ctrl/Cmd+F i din PDF-læser for at slå numre, temaer eller institutter op.</p>"
toc += "</div>"

# ================= EXEC SUMMARY =================
top3 = cat_totals if isinstance(cat_totals, list) else sorted(cat_totals.items(), key=lambda x: -x[1])
if isinstance(cat_totals, dict):
    top3 = sorted(cat_totals.items(), key=lambda x: -x[1])
top_cat_name, top_cat_n = top3[0]
second_name, second_n = top3[1]

exec_summary = f"""
<div class="section section--newpage" id="sec-exec">
<div class="kicker">Executive summary</div>
<h2>21 år, 86 numre, {STORY_COUNT_DA} historier — fra klimadebat til kunstig intelligens</h2>
<div class="tiles">
  {stat_tile(TOTAL, "Numre siden 2005")}
  {stat_tile(STORY_COUNT_DA, "Historier læst i fuld tekst")}
  {stat_tile(f"{len(STORY_INST_COUNTER)}", "Institutter/centre navngivet")}
  {stat_tile(f"{PCT_DOC}%", "Numre med dokumenteret tema")}
</div>
<div class="cols">
  <div class="col">
    <h3>Tre hovedpointer</h3>
    <div class="insight"><b>1. Klima og ressourcer er Dynamos rygrad.</b> {top_cat_n} af {DOCUMENTED} dokumenterede numre ({round(100*top_cat_n/DOCUMENTED)}%) kredser om klima, energi eller ressourceknaphed — temaet går igen fra den første klimavinkel i 2009 til energiøer (2022) og bæredygtige byggematerialer (2025).</div>
    <div class="insight"><b>2. Teknologibølgerne følger samfundsdebatten.</b> Cybersikkerhed (2023) afløses af bioteknologi og kvante (2023–24), som igen afløses af kunstig intelligens som fast tema i 2024–2026 — Dynamo fungerer som en art tidskapsel for hvilken teknologi der optog Danmark hvert år.</div>
    <div class="insight"><b>3. Historie-niveau afslører et helt andet institutbillede.</b> Set på forsidetema alene nævnes DTU-institutter næsten aldrig — men læses hver enkelt historie i fuld tekst (2015–2026), navngiver {STORY_INST_PCT}% af {STORY_COUNT_DA} historier et konkret institut, på tværs af {len(STORY_INST_COUNTER)} forskellige DTU-enheder. Se institutafsnittet.</div>
  </div>
  <div class="col">
    <h3>Top temaer, alle år</h3>
    {bar_rows(top3[:6], color="var(--dtu-blue)", highlight_first=True)}
    <p class="small">Andel af {DOCUMENTED} numre med dokumenteret tema. Se s.6 for fuld oversigt.</p>
  </div>
</div>
</div>"""

# ================= METHOD =================
conf_pairs = [
    ("Høj sikkerhed", conf_counts.get("high",0)),
    ("Middel sikkerhed", conf_counts.get("medium",0)),
    ("Lav sikkerhed", conf_counts.get("low",0)),
    ("Ikke fundet", conf_counts.get("not_found",0)),
]
method = f"""
<div class="section" id="sec-metode">
<div class="kicker">Metode</div>
<h2>Metode og datagrundlag</h2>
<p>Analysen bygger på to niveauer. For samtlige {TOTAL} numre af Dynamo (nr. 1, april 2005 – nr. 86, august 2026) er udgivelsesår og forsidetema forsøgt fastslået ("issue-niveau"). For {STORY_ISSUE_COUNT} af numrene (nr. {min(STORY_ISSUE_NUMS)}–{max(STORY_ISSUE_NUMS)}, 2015–2026) er der derudover gået et niveau dybere: hver enkelt historie i magasinet er læst og katalogiseret individuelt ("historie-niveau") — {STORY_COUNT_DA} historier med titel, DTU-institut (hvor nævnt), emne og en kort beskrivelse hver.</p>
<p><b>Historie-niveau (2015–2026):</b> issuu.com's visningsplatform gemmer internt et fuldt tekstlag pr. side til sin søgefunktion. Et lille udtræksscript (<code>extract_issuu_text.py</code>) henter dette tekstlag direkte fra issuu's egen API for hvert nummer — det er magasinets rigtige, fulde brødtekst, ikke kun forsidebeskrivelsen. Den udtrukne tekst er derefter læst nummer for nummer og struktureret til enkeltstående historier.</p>
<p><b>Issue-niveau (alle 86 numre):</b> forsidetema, udgivelsesår og evt. institutnavn er fastslået via issuu.com/dtudk (numre fra ca. 2015) samt DTU's eget mediebibliotek på dtu.dk, hvor de originale PDF'er af ældre numre (2005–2014) er hostet direkte — cover og indholdsfortegnelse er læst for hvert nummer, hvor PDF'en kunne lokaliseres.</p>
<div class="insight"><b>Begrænsning:</b> {len(STORY_UNCOVERED)} numre (nr. {', '.join(str(n) for n in STORY_UNCOVERED)}) har ikke kunnet historie-udtrækkes — enten fordi de ligger på en anden visningsplatform end issuu, eller fordi issuu's tekstlag-API afviste netop de numre — og har derfor kun issue-niveau-dokumentation. For 2005–2014 er {sum(1 for i in issues if i["year"]<=2014 and i.get("confidence")=="not_found")} af {sum(1 for i in issues if i["year"]<=2014)} numre fortsat udokumenterede efter udvidet søgning i DTU's mediebibliotek — et par lovende kilder (yumpu.com, Wayback Machine) var blokeret af netværksproxyen i analysemiljøet. Se dækningsgraden nedenfor.</div>
<div class="cols">
  <div class="col" style="flex:1.4;">
    <h3>Datadækning pr. sikkerhedsniveau</h3>
    {bar_rows(conf_pairs, color="var(--dtu-blue)")}
  </div>
  <div class="col">
    <h3>Andel dokumenteret</h3>
    {donut_with_legend([
        ("Høj", "#2f3eea", conf_counts.get("high",0)),
        ("Middel", "#6e78f0", conf_counts.get("medium",0)),
        ("Lav", "#acb2f7", conf_counts.get("low",0)),
        ("Ikke fundet", OTHER_COLOR, conf_counts.get("not_found",0)),
    ], hole_num=f"{PCT_DOC}%", hole_sub="dokumenteret")}
  </div>
</div>
<h3>Tema-taksonomi</h3>
<p class="small">Hvert dokumenteret nummer er kategoriseret efter nøgleord i tema og beskrivelse i én eller flere af 10 kategorier (Klima &amp; Energi, Vand/Miljø/Ressourcer, Sundhed &amp; Bioteknologi, Fødevarer &amp; Landbrug, Digitalt/AI/Data, Rum &amp; Klode, Materialer/Nano/Kvante, Transport/Byggeri/Byer, Forsvar &amp; Sikkerhed, Samfund &amp; Iværksætteri). Kategoriseringen er tekstbaseret og automatiseret — den fanger den dominerende vinkel, ikke nødvendigvis alle artikler i det enkelte nummer.</p>
</div>"""

# ================= HISTORY =================
history = f"""
<div class="section" id="sec-historie">
<div class="kicker">Historik</div>
<h2>Dynamo gennem tiden</h2>
<p>Dynamo blev lanceret <b>torsdag den 28. april 2005</b>, samtidig med DTU's årsberetning for 2004, ved universitetets årsfest. Magasinet var nyt: et "profilmagasin" rettet mod en bredere kreds af virksomheder, institutioner og borgere end DTU's daværende kommunikation, og blev samtidig den faste kontaktflade til DTU's Alumneforening. Daværende rektor Lars Pallesen skrev i lederen af nr. 1, at målgruppen var "en bredere kreds af virksomheder, institutioner og borgere, end den vi i dag har kontakt med".</p>
<p>Magasinet har siden udkommet med en bemærkelsesværdigt stabil kadence på ca. <b>fire numre om året</b> — en kvartalstakt, der ifølge en rektortale i 2011 fortsat blev omtalt som "vort kvartalsmagasin DYNAMO". Interpoleret på tværs af de {TOTAL} numre holder kadencen praktisk talt uden huller fra 2005 til 2026.</p>
<div class="quote">"Målgruppen er en bredere kreds af virksomheder, institutioner og borgere, end den vi i dag har kontakt med." — Rektor Lars Pallesen, leder i Dynamo nr. 1, april 2005</div>
<h3>Tre nedslag</h3>
<table>
<tr><th>År</th><th>Nedslag</th></tr>
<tr><td>2005</td><td>Nr. 1 udkommer som nyt "profil- og alumnemagasin" for DTU, målrettet erhvervsliv, myndigheder og borgere.</td></tr>
<tr><td>2009</td><td>Klimatema forud for COP15 — nummeret indeholder en DVD med højdepunkter fra DTU's Climate Change Conference og anbefalinger til danske politikere.</td></tr>
<tr><td>2011</td><td>Magasinet beskrives i rektors årsfest-tale som DTU's vigtigste eksterne kommunikationskanal, med et oplag på over 60.000 eksemplarer.</td></tr>
<tr><td>2020'erne</td><td>Skarpere, mere teknologispecifikke temaer pr. nummer (kvante, AI, droneforsvar) — og et markant lavere, mere målrettet oplag på ca. 16.000 modtagere.</td></tr>
</table>
</div>"""

# ================= THEMES ACROSS 21 YEARS =================
all_cats_sorted = sorted(cat_totals.items(), key=lambda x: -x[1]) if isinstance(cat_totals, dict) else cat_totals
donut_pairs_all = [(c, cat_color(c), n) for c, n in all_cats_sorted[:6]]
donut_pairs_all.append((OTHER_LABEL, OTHER_COLOR, sum(n for c, n in all_cats_sorted[6:])))
themes_page = f"""
<div class="section" id="sec-temaer">
<div class="kicker">Tema-analyse</div>
<h2>Temaer på tværs af 21 år</h2>
<p>Fordelingen nedenfor bygger på de {DOCUMENTED} numre, hvor et forsidetema kunne dokumenteres (ud af {TOTAL} numre i alt). Et nummer kan optræde i mere end én kategori, hvis temaet spænder over flere felter (fx "energiøer" tæller både klima/energi og infrastruktur).</p>
<div class="cols">
  <div class="col" style="flex:1.4;">
    {bar_rows(all_cats_sorted, color="var(--dtu-blue)", highlight_first=True)}
  </div>
  <div class="col">
    <h3>Andel af kategori-optællinger</h3>
    {donut_with_legend(donut_pairs_all, hole_num=str(sum(n for _,n in all_cats_sorted)), hole_sub="optællinger")}
  </div>
</div>
<div class="insight"><b>Klima &amp; energi er det mest genkommende tema i hele Dynamos historie</b> — fra den første klimafokuserede udgave i 2009 over "Energiøer" (2022) til bæredygtige byggematerialer (2025) og skibsfart (2025). Vand-, miljø- og ressourceknaphed er tæt følgende som nummer to, hvilket afspejler DTU's tunge forskningsprofil inden for miljøteknologi og ressourceøkonomi.</div>
</div>"""

# ================= THEMES YEAR BY YEAR =================
_all_years = list(range(2005, 2027))
year_by_year_page = f"""
<div class="section" id="sec-temaeraar">
<div class="kicker">Tema-analyse</div>
<h2>Temaer år for år</h2>
<p>Samme 10 kategorier som ovenfor, men brudt ud år for år i stedet for summeret over hele perioden — søjlerne viser, hvilke temaer der prægede Dynamo hvert enkelt år (kun de {DOCUMENTED} dokumenterede numre er talt med; se dækningsgraden i metodeafsnittet for hvorfor 2005–2014 er tyndere).</p>
{stacked_year_chart(_all_years)}
<div class="insight"><b>Bølgerne er tydelige, når man ser år for år:</b> klima &amp; energi optræder praktisk talt hvert år fra 2015 og frem, mens digitalt/AI/data og materialer/nano/kvante først for alvor tager fart efter 2020 — konsistent med tre-æra-opdelingen nedenfor, men med langt mere detalje om <i>hvornår</i> skiftet sker.</div>
</div>"""

# ================= DYNAMO AND WORLD EVENTS =================
world_events_page = f"""
<div class="section" id="sec-verden">
<div class="kicker">Dynamo og omverdenen</div>
<h2>Falder Dynamos temaer sammen med det, der sker i verden?</h2>
<p>Ti udvalgte, velkendte begivenheder fra 2005–2026 holdt op mod, hvor mange af de dokumenterede Dynamo-numre samme år faldt i den relaterede tema-kategori. Klima &amp; energi går igen flest gange nedenfor, fordi det også er langt Dynamos mest genkommende tema — men sammenfaldene med COP15 (2009), energikrisen efter Ruslands invasion af Ukraine (2022) og ChatGPT/ AI-forordningen (2022–2024) er slående konkrete.</p>
{world_events_timeline()}
</div>"""

# ================= ERA COMPARISON =================
era_titles = {
    "2005–2012": "2005–2012 · De første år",
    "2013–2019": "2013–2019 · Konsolidering",
    "2020–2026": "2020–2026 · Teknologibølger",
}
era_notes = {
    "2005–2012": "Sparsomt digitaliseret periode (kun 3 af 32 numre dokumenteret) — men det vi kan se, peger allerede på klima som gennemgående tema, drevet af COP15-forberedelserne i 2009.",
    "2013–2019": "Bredt tematisk spænd: vand, plastik, Arktis og kunstig intelligens optræder alle for første gang i denne periode.",
    "2020–2026": "Fuldt dokumenteret periode. Klar acceleration i teknologispecifikke temaer — cybersikkerhed, kvante, bioteknologi og AI afløser hinanden år for år.",
}
era_cols = []
for e in eras:
    pairs = sorted(era_cat.get(e, {}).items(), key=lambda x: -x[1])[:5]
    era_cols.append(f"""<div class="col">
      <h3>{esc(era_titles.get(e,e))}</h3>
      {bar_rows(pairs, color="var(--dtu-blue)") if pairs else "<p class='small'>Ingen dokumenterede numre i perioden.</p>"}
      <p class="small">{esc(era_notes.get(e,''))}</p>
    </div>""")

era_page = f"""
<div class="section" id="sec-temaudvikling">
<div class="kicker">Tema-analyse</div>
<h2>Temaudvikling: tre æraer</h2>
<p>De 21 år er delt i tre nogenlunde lige lange perioder for at vise, hvordan Dynamos tematiske fokus har flyttet sig — og hvor godt hver periode er dokumenteret i de tilgængelige kilder.</p>
<div class="cols">
{"".join(era_cols)}
</div>
</div>"""

# ================= STRATEGY ALIGNMENT =================
def issue_label(it):
    return f"nr. {it['issue_number']} ({it['year']}) — {it['theme']}"

strategy_rows = []
mapped_issue_numbers = set()
for area in STRATEGY["areas"]:
    cats = set(area["categories"])
    matches = [it for it in issues if cats & set(it.get("categories") or [])] if cats else []
    mapped_issue_numbers |= {it["issue_number"] for it in matches}
    examples = sorted(matches, key=lambda it: -it["year"])[:3]
    pct = round(100 * len(matches) / DOCUMENTED) if DOCUMENTED else 0
    strategy_rows.append(f"""
    <div class="strategy-row">
      <div class="strategy-head">
        <h3>{esc(area['name'])}</h3>
        {f"<div class='strategy-count'><b>{len(matches)}</b><span>af {DOCUMENTED} numre ({pct}%)</span></div>" if cats else "<div class='strategy-count strategy-count--none'><b>–</b><span>Ingen af de 10 tema-kategorier dækker dette område</span></div>"}
      </div>
      <p class="small">{esc(area['note'])}</p>
      {"<p class='small'><b>Eksempler:</b> " + "; ".join(esc(issue_label(it)) for it in examples) + "</p>" if examples else ""}
    </div>""")

strategy_covered_pct = round(100 * len(mapped_issue_numbers) / DOCUMENTED) if DOCUMENTED else 0

strategy_page = f"""
<div class="section" id="sec-strategi">
<div class="kicker">Strategi-kobling</div>
<h2>Temaerne og DTU's strategi 2026–2031</h2>
<p>DTU vedtog i 2026 en ny strategi med fem strategiske indsatsområder (se kilde nedenfor). Nedenfor er Dynamos 10 tema-kategorier holdt op mod de fem områder, for at vise hvor godt magasinets historiske tema-profil allerede understøtter den fremadrettede strategi.</p>
<div class="insight"><b>{len(mapped_issue_numbers)} af {DOCUMENTED} dokumenterede numre ({strategy_covered_pct}%)</b> har et tema, der falder inden for mindst ét af de tre teknologi-/erhvervsrettede indsatsområder nedenfor. De to resterende områder — uddannelse og videnskabeligt lederskab/demokratisk ansvar — er ikke emner, Dynamos forsidetemaer historisk beskriver, da magasinet er organiseret om forsknings- og samfundstemaer, ikke om uddannelses- eller governance-indsatser. Det er forventeligt snarere end en svaghed: strategien er ny (2026–2031), mens Dynamo dækker 21 år bagud, så koblingen viser <i>fremadrettet relevans</i>, ikke historisk eksekvering af strategien.</div>
{"".join(strategy_rows)}
<p class="small">Kilde: <a class="src" href="{esc(STRATEGY['source']['url'])}">{esc(STRATEGY['source']['title'])}</a>, hentet {esc(STRATEGY['source']['retrieved'])}.</p>
</div>"""

# ================= INSTITUTES =================
story_inst_pairs = STORY_INST_COUNTER.most_common()
inst_rows = "".join(f"<tr><td>{esc(name)}</td><td>{n}</td></tr>" for name, n in story_inst_pairs) if story_inst_pairs else "<tr><td colspan='2' class='small'>Ingen eksplicit institut-nævning fundet.</td></tr>"

institute_ref_rows = "".join(
    f"<tr><td>{esc(i['name'])}</td><td>{esc(i['focus'])}</td></tr>" for i in INSTITUTES
)

institutes_page = f"""
<div class="section" id="sec-institutter">
<div class="kicker">Institutter</div>
<h2>Institutter i Dynamo</h2>
<p>Set på forsidetema alene virker Dynamo redaktionelt bygget op om <b>temaer og samfundsudfordringer</b> frem for organisatorisk afsender — på issue-niveau (alle 86 numre) findes stort set ingen institut-nævninger i forsidebeskrivelserne. Læses hver enkelt historie i fuld tekst i stedet (nr. {min(STORY_ISSUE_NUMS)}–{max(STORY_ISSUE_NUMS)}, 2015–2026), viser billedet sig markant rigere: <b>{STORY_WITH_INST} af {STORY_COUNT_DA} historier ({STORY_INST_PCT}%)</b> navngiver et konkret DTU-institut eller -center, fordelt på {len(story_inst_pairs)} forskellige enheder.</p>
{bar_rows(story_inst_pairs[:15], color="var(--dtu-blue)")}
<p class="small">Top 15 af {len(story_inst_pairs)} institutter/centre, optalt pr. historie (2015–2026). Fuld liste nedenfor.</p>
<table><tr><th>Institut/center</th><th>Historier</th></tr>{inst_rows}</table>
<div class="insight"><b>Fortolkning:</b> Instituttavlen var altså ikke et hul i Dynamos indhold, men i den oprindelige analysemetode — magasinet navngiver rent faktisk institutter jævnligt, bare inde i de enkelte historier, ikke på forsiden eller i den korte temabeskrivelse. DTU Compute, DTU Fødevareinstituttet, DTU Elektro, DTU Space og DTU Fotonik er de hyppigst navngivne, hvilket afspejler både forskningsvolumen og hvilke institutter der hyppigt bidrager med "lette" historier (studenterprojekter, portrætter) ud over de tunge forskningsartikler.</div>
<h3>DTU's institutter og centre (reference, 2026)</h3>
<p class="small">Til reference: DTU's nuværende institutstruktur, som ethvert fremtidigt dybere tekstudtræk fra Dynamo bør mappes op imod. Bemærk at flere institutter er omdøbt eller fusioneret i perioden 2005–2026 (fx DTU Compute fra 2013, DTU Sustain og DTU Construct fra ca. 2022-23) — se metodenoten.</p>
<table><tr><th>Institut/center</th><th>Fokusområde</th></tr>{institute_ref_rows}</table>
</div>"""

# ================= CIRCULATION =================
circ_page = f"""
<div class="section" id="sec-oplag">
<div class="kicker">Oplag &amp; distribution</div>
<h2>Oplag og målgruppe over tid</h2>
<div class="tiles">
  {stat_tile("2005", "Lancering, profilmagasin")}
  {stat_tile("60.000+", "Oplag, 2011 (kvartalsmagasin)")}
  {stat_tile("16.000", "Modtagere, 2025/26")}
  {stat_tile("-73%", "Fald i oplag, 2011→2026")}
</div>
{line_chart_svg([("2011", 60000), ("2025/26", 16000)], y_suffix=" eks.")}
<p class="small">Kun to kendte datapunkter (2011 og 2025/26) — linjen mellem dem er en lige linje, ikke en målt udvikling år for år.</p>
{bar_rows([("2011", 60000), ("2025/26", 16000)], color="var(--dtu-blue)", val_suffix=" eks.")}
<p>Oplaget er faldet markant siden 2011 — men målgruppen er samtidig blevet skarpere defineret. I dag distribueres Dynamo annoncefrit og gratis til en navngivet kreds af beslutningstagere: bestyrelses- og direktionsmedlemmer i Danmarks største virksomheder, folketings- og EU-parlamentsmedlemmer, samt fonds- og rådsbestyrelser — suppleret af udlæg i landets læge- og tandlægevente­værelser. Faldet afspejler en generel branchetrend for trykte profilmagasiner: fra bredt oplag til stærkt målrettet distribution, understøttet af en digital udgave (issuu/iPad) siden omkring 2011.</p>
<p class="small">Kilde: <a class="src" href="https://www.inside.dtu.dk/kommunikation/nyheder-og-presse/dynamo">DTU Inside — Dynamo</a>: "Magasinet distribueres til 16.000 modtagere, heriblandt beslutningstagere i industrien, erhvervslivet og i den offentlige administration."</p>
<div class="insight"><b>Konsekvens for denne analyse:</b> Den skarpere målretning falder tidsmæssigt sammen med den periode (2020-2026), hvor Dynamos temaer bliver mest teknologispecifikke (kvante, AI, forsvar) — konsistent med en strategi om at tale direkte til beslutningstagere om aktuelle teknologipolitiske dagsordener frem for et bredt oplysningsformål.</div>
</div>"""

# ================= APPENDIX: FULL TABLE =================
def conf_label(c):
    return {"high":"Høj","medium":"Middel","low":"Lav","not_found":"Ikke fundet"}.get(c, c)

rows_html = []
for it in issues:
    if it.get("theme"):
        theme = esc(it["theme"])
    elif it.get("confidence") == "not_found":
        theme = "<span class='small'>Ikke dokumenteret</span>"
    else:
        # researched from a primary source, but genuinely no single cover theme
        # (a general-interest issue) — not the same thing as "not found"
        theme = "<span class='small'>Blandet nummer — ingen samlet forsidetema</span>"
    cats = it.get("categories") or []
    tags = "".join(f"<span class='tag'>{esc(c)}</span>" for c in cats if c != "Andet/uklassificeret")
    rows_html.append(
        f"<tr><td>{it['issue_number']}</td><td>{it['year']}</td>"
        f"<td>{theme}{('<br>'+tags) if tags else ''}</td>"
        f"<td>{conf_label(it.get('confidence','not_found'))}</td>"
        f"<td>{source_links(it.get('source_urls'))}</td></tr>"
    )

# One continuous table — it flows across as many pages as it needs, with the
# header row (<thead>) repeating automatically on every page via
# `display:table-header-group` (see template.html).
appendix_html = f"""
<div class="section" id="sec-appendiks">
<div class="kicker">Appendiks A</div>
<h2>Appendiks A: alle katalogiserede numre</h2>
<p class="small">"Kilde" linker til de sider (issuu.com/dtudk, DTU's nyhedsarkiv m.fl.), hvor nummerets forside/tema er dokumenteret — brug dem til at slå den fulde historie op.</p>
<table>
<thead><tr><th>Nr.</th><th>År</th><th>Tema</th><th>Sikkerhed</th><th>Kilde</th></tr></thead>
<tbody>
{''.join(rows_html)}
</tbody>
</table>
</div>"""

# ================= APPENDIX B: EVERY SINGLE STORY =================
NO_INST = "<span class='small'>–</span>"

def story_row(s):
    inst = esc(s["institute"]) if s.get("institute") else NO_INST
    return (
        f"<tr><td>{s['issue_number']}</td><td>{s['year']}</td><td>{esc(s['title'])}</td>"
        f"<td>{inst}</td><td>{esc(s.get('topic') or '–')}</td></tr>"
    )

story_rows_sorted = sorted(STORIES, key=lambda s: (s["issue_number"],))
story_rows_html = "".join(story_row(s) for s in story_rows_sorted)
stories_appendix_html = f"""
<div class="section" id="sec-appendiks-b">
<div class="kicker">Appendiks B</div>
<h2>Appendiks B: alle {STORY_COUNT_DA} historier, nr. {min(STORY_ISSUE_NUMS)}–{max(STORY_ISSUE_NUMS)} (2015–2026)</h2>
<p class="small">Hver enkelt historie i de {STORY_ISSUE_COUNT} numre, hvor Dynamos fulde tekst kunne udtrækkes (se metodeafsnittet) — ikke kun forsidetemaet. "Institut" er kun udfyldt, hvor historien selv navngiver et konkret DTU-institut eller -center; "–" betyder ingen specifik enhed nævnt (fx studenterprojekter eller eksterne samarbejder).</p>
<table>
<thead><tr><th>Nr.</th><th>År</th><th>Titel</th><th>Institut</th><th>Emne</th></tr></thead>
<tbody>
{story_rows_html}
</tbody>
</table>
</div>"""

# ================= SOURCES / LAST PAGE =================
sources_page = f"""
<div class="section" id="sec-kilder">
<div class="kicker">Kilder &amp; forbehold</div>
<h2>Kilder og forbehold</h2>
<p>Denne rapport er udarbejdet i to lag: et issue-niveau (forsidetema, udgivelsesår, kilde) for alle {TOTAL} numre, katalogiseret ud fra <b>issuu.com/dtudk</b> og de originale PDF'er i <b>DTU's mediebibliotek (dtu.dk)</b> — og et historie-niveau ({STORY_COUNT_DA} enkeltstående historier med titel, institut og emne) for de {STORY_ISSUE_COUNT} numre fra 2015–2026, hvor magasinets fulde tekst kunne udtrækkes fra issuu.com's interne søgeindeks (se metodeafsnittet). {len(STORY_UNCOVERED)} numre (nr. {', '.join(str(n) for n in STORY_UNCOVERED)}) samt hovedparten af 2005–2014 har kun issue-niveau-dokumentation. Kildelinks til hvert enkelt nummer findes i appendiks A; alle historier findes i appendiks B.</p>
<p>Koblingen til DTU's strategi (s. {TOC_PAGES.get("strategi", 5)}) er baseret på <a class="src" href="{esc(STRATEGY['source']['url'])}">{esc(STRATEGY['source']['title'])}</a>, hentet {esc(STRATEGY['source']['retrieved'])}.</p>
<p>Numre markeret "Ikke fundet" i appendiks eksisterer efter al sandsynlighed (Dynamos kvartalskadence er bekræftet uændret gennem hele perioden), men deres tema kunne ikke dokumenteres inden for de kilder, der var tilgængelige i analysemiljøet.</p>
<p class="small">Udarbejdet {esc(today)}. Data og metode kan genskabes/udvides ved fornyet adgang til DTU's fulde nyhedsarkiv og digitale magasinarkiv.</p>
</div>"""

CONTENT = (cover + toc + exec_summary + method + history + themes_page + year_by_year_page
    + world_events_page + era_page + strategy_page + institutes_page + circ_page
    + appendix_html + stories_appendix_html + sources_page)

with open(os.path.join(BASE, "template.html"), encoding="utf-8") as f:
    template = f.read()

final = template.replace("{{CONTENT}}", CONTENT)
out_path = os.path.join(BASE, "report.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(final)

print("Wrote", out_path, "-", len(CONTENT), "chars of content")
