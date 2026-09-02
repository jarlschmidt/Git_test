#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re, html, os
from collections import defaultdict, Counter

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

def load(fn):
    p = os.path.join(DATA, fn)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)

issues = []
for fn in ["issues_01_20.json", "issues_21_44.json", "issues_45_66.json", "issues_67_86.json"]:
    issues += load(fn)

# de-dup by issue_number, keep richest record
by_num = {}
for it in issues:
    n = it.get("issue_number")
    if n is None:
        continue
    if n not in by_num:
        by_num[n] = it
    else:
        # prefer higher confidence / richer description
        rank = {"high": 3, "medium": 2, "low": 1, "not_found": 0}
        if rank.get(it.get("confidence"), 0) > rank.get(by_num[n].get("confidence"), 0):
            by_num[n] = it

issues = [by_num[k] for k in sorted(by_num.keys())]

# ---- Interpolate year where missing, anchored on issue #1 = 2005 (Q2), ~4/year ----
ANCHOR_ISSUE, ANCHOR_YEAR = 1, 2005.33  # end of April
def interp_year(n):
    return ANCHOR_YEAR + (n - ANCHOR_ISSUE) / 4.0

for it in issues:
    if not it.get("year"):
        it["year"] = round(interp_year(it["issue_number"]))
    it["year"] = int(it["year"])

# ---- Theme taxonomy ----
TAXONOMY = [
    ("Klima & Energi", ["klima","energi","co2","vind","sol","fusion","brint","hydrogen","vedvarende",
                         "climate","energy","wind","solar","fossil","power-to-x","energiø"]),
    ("Vand, Miljø & Ressourcer", ["vand","plast","ressource","genanvend","forurening","miljø",
                                   "water","plastic","resource","pollution","recycl","environment","scarcity","knap"]),
    ("Sundhed & Bioteknologi", ["sundhed","kræft","medicin","immunterapi","parkinson","biotek","sygdom","diagnos",
                                 "health","cancer","medicine","biotech","disease","immunotherapy","bakterie","bacteria",
                                 "antibiotik","imaging","life science"]),
    ("Fødevarer & Landbrug", ["fødevare","landbrug","protein","fisk","akvakultur","sult","tang","seaweed",
                               "food","farming","agriculture","hunger","fish"]),
    ("Digitalt, AI & Data", ["kunstig intelligens"," ai ","ai-","data","digital","algoritm","matematik",
                              "artificial intelligence","mathematics","computer"]),
    ("Rum & Klode", ["rum","satellit","arktis","is-","space","satellite","arctic","solsystem","universe"]),
    ("Materialer, Nano & Kvante", ["materiale","nano","kvante","quantum","robot","print","materials","synkrotron","røntgen","x-ray"]),
    ("Transport, Byggeri & Byer", ["transport","trafik","byg","infrastruktur","smart cities","elbil","traffic",
                                     "construction","maritime","shipping","by-udvikling"]),
    ("Forsvar & Sikkerhed", ["forsvar","sikkerhed","drone","cyber","security","defense","defence"]),
    ("Samfund & Iværksætteri", ["iværksætter","innovation","økonomi","samfund","entrepreneurship","economy",
                                  "society","mangelsamfund"]),
]

def categorize(it):
    if it.get("confidence") == "not_found" or not str(it.get("theme","")).strip():
        return []
    # description is real magazine-content summary for documented issues (safe to match);
    # for not_found issues it's analyst commentary instead, so it's excluded above.
    text = (str(it.get("theme","")) + " " + str(it.get("description",""))).lower()
    # substring matching (Danish compounds a la "materialeinnovation" need it), but scrub
    # known false-positive containers first (e.g. "kræft" inside "bekræftet"/"bekræfte").
    text = text.replace("bekræft", " ")
    hits = []
    for cat, kws in TAXONOMY:
        for kw in kws:
            if kw in text:
                hits.append(cat)
                break
    return hits or ["Andet/uklassificeret"]

for it in issues:
    it["categories"] = categorize(it)

documented = [it for it in issues if it.get("confidence") in ("high","medium","low") and it.get("theme")]
not_found = [it for it in issues if it.get("confidence") == "not_found" or not it.get("theme")]

# ---- Era split ----
def era(y):
    if y <= 2012: return "2005–2012"
    if y <= 2019: return "2013–2019"
    return "2020–2026"

ERAS = ["2005–2012", "2013–2019", "2020–2026"]

era_counts_total = Counter()
era_counts_documented = Counter()
for it in issues:
    era_counts_total[era(it["year"])] += 1
for it in documented:
    era_counts_documented[era(it["year"])] += 1

era_cat = {e: Counter() for e in ERAS}
for it in documented:
    e = era(it["year"])
    for c in it["categories"]:
        era_cat[e][c] += 1

cat_totals = Counter()
for it in documented:
    for c in it["categories"]:
        cat_totals[c] += 1

# issues per calendar year (all issues, using interpolated/actual year) for timeline
year_counts = Counter(it["year"] for it in issues)
min_y, max_y = min(year_counts), max(year_counts)

# institutes
inst_counter = Counter()
for it in issues:
    for i in it.get("institutes", []) or []:
        inst_counter[i.strip()] += 1

# confidence breakdown
conf_counts = Counter(it.get("confidence","not_found") for it in issues)

print(json.dumps({
    "total_issues": len(issues),
    "documented": len(documented),
    "not_found": len(not_found),
    "year_range": [min_y, max_y],
    "cat_totals": cat_totals.most_common(),
    "era_counts_total": dict(era_counts_total),
    "era_counts_documented": dict(era_counts_documented),
    "inst_counter": inst_counter.most_common(),
    "conf_counts": dict(conf_counts),
}, ensure_ascii=False, indent=2))

# Save normalized dataset for the HTML builder
with open(os.path.join(DATA, "dataset.json"), "w", encoding="utf-8") as f:
    json.dump({
        "issues": issues,
        "era_cat": {e: dict(era_cat[e]) for e in ERAS},
        "era_counts_total": dict(era_counts_total),
        "era_counts_documented": dict(era_counts_documented),
        "cat_totals": dict(cat_totals),
        "year_counts": dict(year_counts),
        "inst_counter": dict(inst_counter),
        "conf_counts": dict(conf_counts),
        "eras": ERAS,
        "taxonomy_order": [c for c,_ in TAXONOMY] + ["Andet/uklassificeret"],
    }, f, ensure_ascii=False, indent=2)

print("\nWrote dataset.json")
