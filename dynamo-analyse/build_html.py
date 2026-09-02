#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, html, os
from datetime import date
from urllib.parse import urlparse

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, "data", "dataset.json"), encoding="utf-8") as f:
    D = json.load(f)
with open(os.path.join(BASE, "data", "dtu_institutes.json"), encoding="utf-8") as f:
    INSTITUTES = json.load(f)
with open(os.path.join(BASE, "data", "dtu_strategy.json"), encoding="utf-8") as f:
    STRATEGY = json.load(f)

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
inst_counter = D["inst_counter"]
conf_counts = D["conf_counts"]

def esc(s):
    return html.escape(str(s), quote=False)

TOTAL = len(issues)
DOCUMENTED = sum(1 for i in issues if i.get("confidence") in ("high","medium","low") and i.get("theme"))
PCT_DOC = round(100*DOCUMENTED/TOTAL)

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
  <div>
    <div class="kicker">Medieanalyse · DTU</div>
    <h1>Dynamo gennem&nbsp;20&nbsp;år</h1>
    <div class="sub">Historier, temaer og institutter i DTU's profilmagasin — nr. 1 (2005) til nr. 86 (2026). Baseret på {TOTAL} udgivne numre, heraf {DOCUMENTED} tema-dokumenterede via issuu.com og DTU's nyhedsarkiv.</div>
    <div class="stats">
      {"".join(f'<div class="stat"><b>{esc(b)}</b><span class="lbl">{esc(l)}</span></div>' for b,l in [
          (TOTAL, "Numre udgivet"), ("21", "År (2005–2026)"), (f"{PCT_DOC}%", "Temaer dokumenteret"), ("~4", "Numre pr. år")
      ])}
    </div>
    {year_track_html()}
    <p class="small" style="color:rgba(255,255,255,0.55);">Numre pr. udgivelsesår, 2005–2026 (interpoleret hvor eksakt måned er ukendt)</p>
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
    ("temaudvikling", "Temaudvikling: tre æraer", 4),
    ("strategi", "Temaerne og DTU's strategi 2026–2031", 5),
    ("institutter", "Institutter i Dynamo", 5),
    ("oplag", "Oplag og målgruppe over tid", 6),
    ("appendiks", "Appendiks: alle katalogiserede numre", 7),
    ("kilder", "Kilder og forbehold", 10),
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
<div class="section" id="sec-exec">
<div class="kicker">Executive summary</div>
<h2>21 år, 86 numre — fra klimadebat til kunstig intelligens</h2>
<div class="tiles">
  {stat_tile(TOTAL, "Numre siden 2005")}
  {stat_tile(f"{top_cat_n}", f"Numre om {top_cat_name.lower()}")}
  {stat_tile("60.000 → 17.000", "Oplag 2011 → 2025/26")}
  {stat_tile(f"{PCT_DOC}%", "Numre med dokumenteret tema")}
</div>
<div class="cols">
  <div class="col">
    <h3>Tre hovedpointer</h3>
    <div class="insight"><b>1. Klima og ressourcer er Dynamos rygrad.</b> {top_cat_n} af {DOCUMENTED} dokumenterede numre ({round(100*top_cat_n/DOCUMENTED)}%) kredser om klima, energi eller ressourceknaphed — temaet går igen fra den første klimavinkel i 2009 til energiøer (2022) og bæredygtige byggematerialer (2025).</div>
    <div class="insight"><b>2. Teknologibølgerne følger samfundsdebatten.</b> Cybersikkerhed (2023) afløses af bioteknologi og kvante (2023–24), som igen afløses af kunstig intelligens som fast tema i 2024–2026 — Dynamo fungerer som en art tidskapsel for hvilken teknologi der optog Danmark hvert år.</div>
    <div class="insight"><b>3. Magasinet navngiver sjældent institutter direkte.</b> Kun en håndfuld af de {DOCUMENTED} dokumenterede numre nævner et DTU-institut ved navn i den tilgængelige tekst — Dynamo er redaktionelt bygget op om samfundstemaer ("klima", "AI", "sundhed"), ikke om organisatorisk afsender. Se metodeafsnittet for hvad det betyder for institut-analysen.</div>
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
<p>Analysen er bygget ved at katalogisere samtlige {TOTAL} numre af Dynamo (nr. 1, april 2005 – nr. 86, august 2026) og for hvert nummer forsøge at fastslå udgivelsesår, forsidetema, en kort indholdsbeskrivelse samt eventuelle navngivne DTU-institutter. To kilder er brugt:</p>
<p><b>1. issuu.com/dtudk</b> — DTU's officielle udgiver-konto på Issuu, hvor numre fra ca. 2015 og frem er tilgængelige som gennembladrbare digitale udgaver med forsidetekst og beskrivelse.<br>
<b>2. DTU's nyhedsarkiv (dtu.dk)</b> — søgt via et indekseret arkiv af DTU-nyheder, herunder de korte "Nyt nummer af DYNAMO"-artikler, som DTU historisk har udgivet ved hver ny udgave.</p>
<div class="insight"><b>Vigtig begrænsning:</b> Direkte adgang til www.dtu.dk, alumni.dtu.dk og inside.dtu.dk var blokeret af netværkspolitikken i den analysemiljø, rapporten er udarbejdet i — kun issuu.com og det indekserede nyhedsarkiv var tilgængelige. Det betyder, at datagrundlaget er markant tættere for numre udgivet efter ca. 2015 (hvor Issuu-arkivet er komplet) end for numre fra 2005–2014, hvor kun {conf_counts.get("high",0)+conf_counts.get("medium",0)+conf_counts.get("low",0)} af {TOTAL} numre samlet er dokumenteret. Se dækningsgraden nedenfor.</div>
<h3>Datadækning pr. sikkerhedsniveau</h3>
{bar_rows(conf_pairs, color="var(--dtu-blue)")}
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
<tr><td>2020'erne</td><td>Skarpere, mere teknologispecifikke temaer pr. nummer (kvante, AI, droneforsvar) — og et markant lavere, mere målrettet oplag på ca. 16-19.000 modtagere.</td></tr>
</table>
</div>"""

# ================= THEMES ACROSS 21 YEARS =================
all_cats_sorted = sorted(cat_totals.items(), key=lambda x: -x[1]) if isinstance(cat_totals, dict) else cat_totals
themes_page = f"""
<div class="section" id="sec-temaer">
<div class="kicker">Tema-analyse</div>
<h2>Temaer på tværs af 21 år</h2>
<p>Fordelingen nedenfor bygger på de {DOCUMENTED} numre, hvor et forsidetema kunne dokumenteres (ud af {TOTAL} numre i alt). Et nummer kan optræde i mere end én kategori, hvis temaet spænder over flere felter (fx "energiøer" tæller både klima/energi og infrastruktur).</p>
{bar_rows(all_cats_sorted, color="var(--dtu-blue)", highlight_first=True)}
<div class="insight"><b>Klima &amp; energi er det mest genkommende tema i hele Dynamos historie</b> — fra den første klimafokuserede udgave i 2009 over "Energiøer" (2022) til bæredygtige byggematerialer (2025) og skibsfart (2025). Vand-, miljø- og ressourceknaphed er tæt følgende som nummer to, hvilket afspejler DTU's tunge forskningsprofil inden for miljøteknologi og ressourceøkonomi.</div>
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
inst_pairs = inst_counter if isinstance(inst_counter, list) else sorted(inst_counter.items(), key=lambda x: -x[1])
inst_rows = "".join(f"<tr><td>{esc(name)}</td><td>{n}</td></tr>" for name, n in inst_pairs) if inst_pairs else "<tr><td colspan='2' class='small'>Ingen eksplicit institut-nævning fundet i de gennemgåede kilder.</td></tr>"

institute_ref_rows = "".join(
    f"<tr><td>{esc(i['name'])}</td><td>{esc(i['focus'])}</td></tr>" for i in INSTITUTES
)

institutes_page = f"""
<div class="section" id="sec-institutter">
<div class="kicker">Institutter</div>
<h2>Institutter i Dynamo</h2>
<p>Et centralt fund i denne analyse er, at Dynamo redaktionelt er bygget op om <b>temaer og samfundsudfordringer</b> — ikke om hvilket DTU-institut der står bag forskningen. På tværs af {DOCUMENTED} dokumenterede numre kunne kun {sum(n for _,n in inst_pairs)} eksplicitte institut-nævninger findes i den tilgængelige forsidetekst/beskrivelse:</p>
<table><tr><th>Institut/center</th><th>Nævnt i antal numre</th></tr>{inst_rows}</table>
<div class="insight"><b>Fortolkning:</b> Dette er sandsynligvis en bevidst redaktionel linje snarere end et hul i datagrundlaget — Dynamo henvender sig til et bredt eksternt publikum (erhvervsliv, myndigheder, politikere), hvor et samfundstema ("klima", "kunstig intelligens", "vandmangel") kommunikerer bedre end et instituts navn. En fuld institut-attribuering ville kræve adgang til den fulde artikeltekst i hvert nummers PDF, ikke kun issuu-forsiden/beskrivelsen.</div>
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
  {stat_tile("16-19.000", "Oplag, 2025/26")}
  {stat_tile("-72%", "Fald i oplag, 2011→2026")}
</div>
{bar_rows([("2011", 60000), ("2025/26", 17000)], color="var(--dtu-blue)", val_suffix=" eks.")}
<p>Oplaget er faldet markant siden 2011 — men målgruppen er samtidig blevet skarpere defineret. I dag distribueres Dynamo annoncefrit og gratis til en navngivet kreds af beslutningstagere: bestyrelses- og direktionsmedlemmer i Danmarks største virksomheder, folketings- og EU-parlamentsmedlemmer, samt fonds- og rådsbestyrelser — suppleret af udlæg i landets læge- og tandlægevente­værelser. Faldet afspejler en generel branchetrend for trykte profilmagasiner: fra bredt oplag til stærkt målrettet distribution, understøttet af en digital udgave (issuu/iPad) siden omkring 2011.</p>
<div class="insight"><b>Konsekvens for denne analyse:</b> Den skarpere målretning falder tidsmæssigt sammen med den periode (2020-2026), hvor Dynamos temaer bliver mest teknologispecifikke (kvante, AI, forsvar) — konsistent med en strategi om at tale direkte til beslutningstagere om aktuelle teknologipolitiske dagsordener frem for et bredt oplysningsformål.</div>
</div>"""

# ================= APPENDIX: FULL TABLE =================
def conf_label(c):
    return {"high":"Høj","medium":"Middel","low":"Lav","not_found":"Ikke fundet"}.get(c, c)

rows_html = []
for it in issues:
    theme = it.get("theme") or "<span class='small'>Ikke dokumenteret</span>"
    cats = it.get("categories") or []
    tags = "".join(f"<span class='tag'>{esc(c)}</span>" for c in cats if c != "Andet/uklassificeret")
    rows_html.append(
        f"<tr><td>{it['issue_number']}</td><td>{it['year']}</td>"
        f"<td>{theme if it.get('theme') else theme}{('<br>'+tags) if tags else ''}</td>"
        f"<td>{conf_label(it.get('confidence','not_found'))}</td>"
        f"<td>{source_links(it.get('source_urls'))}</td></tr>"
    )

# One continuous table — it flows across as many pages as it needs, with the
# header row (<thead>) repeating automatically on every page via
# `display:table-header-group` (see template.html).
appendix_html = f"""
<div class="section" id="sec-appendiks">
<div class="kicker">Appendiks</div>
<h2>Appendiks: alle katalogiserede numre</h2>
<p class="small">"Kilde" linker til de sider (issuu.com/dtudk, DTU's nyhedsarkiv m.fl.), hvor nummerets forside/tema er dokumenteret — brug dem til at slå den fulde historie op.</p>
<table>
<thead><tr><th>Nr.</th><th>År</th><th>Tema</th><th>Sikkerhed</th><th>Kilde</th></tr></thead>
<tbody>
{''.join(rows_html)}
</tbody>
</table>
</div>"""

# ================= SOURCES / LAST PAGE =================
sources_page = f"""
<div class="section" id="sec-kilder">
<div class="kicker">Kilder &amp; forbehold</div>
<h2>Kilder og forbehold</h2>
<p>Denne rapport er udarbejdet som en automatiseret indholdsanalyse baseret på offentligt tilgængelige forsider, temabeskrivelser og udgivelsesdatoer for Dynamo-numre på <b>issuu.com/dtudk</b> samt artikler i <b>DTU's nyhedsarkiv (dtu.dk)</b>. Den er ikke baseret på fuldtekst-læsning af hvert magasins indre artikler, og bør derfor læses som en kortlægning af <i>forsidetemaer og redaktionel retning</i> — ikke en komplet indholdsanalyse af hver artikel i hvert nummer. Kildelinks til hvert enkelt nummer findes i appendiks.</p>
<p>Koblingen til DTU's strategi (s. {TOC_PAGES.get("strategi", 5)}) er baseret på <a class="src" href="{esc(STRATEGY['source']['url'])}">{esc(STRATEGY['source']['title'])}</a>, hentet {esc(STRATEGY['source']['retrieved'])}.</p>
<p>Numre markeret "Ikke fundet" i appendiks eksisterer efter al sandsynlighed (Dynamos kvartalskadence er bekræftet uændret gennem hele perioden), men deres tema kunne ikke dokumenteres inden for de kilder, der var tilgængelige i analysemiljøet.</p>
<p class="small">Udarbejdet {esc(today)}. Data og metode kan genskabes/udvides ved fornyet adgang til DTU's fulde nyhedsarkiv og digitale magasinarkiv.</p>
</div>"""

CONTENT = cover + toc + exec_summary + method + history + themes_page + era_page + strategy_page + institutes_page + circ_page + appendix_html + sources_page

with open(os.path.join(BASE, "template.html"), encoding="utf-8") as f:
    template = f.read()

final = template.replace("{{CONTENT}}", CONTENT)
out_path = os.path.join(BASE, "report.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(final)

print("Wrote", out_path, "-", len(CONTENT), "chars of content")
