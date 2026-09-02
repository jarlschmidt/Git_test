#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finds which physical PDF page each report chapter actually starts on, by
running pdftotext over a trial print of the report and searching for each
chapter's heading text. Writes data/toc_pages.json, which build_html.py
reads on its next run to print correct page numbers in the table of
contents.

Sections no longer force one-chapter-per-page (see template.html), so the
real page for a chapter can only be known after the content is laid out —
hence this two-pass build: build_html.py -> print_pdf.js -> measure_toc.py
-> build_html.py -> print_pdf.js.
"""
import json, os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, "Dynamo_gennem_20_aar.pdf")

HEADINGS = {
    "exec": "86 numre",
    "metode": "Metode og datagrundlag",
    "historie": "Dynamo gennem tiden",
    "temaer": "Temaer på tværs af 21 år",
    "temaeraar": "Temaer år for år",
    "verden": "Falder Dynamos temaer sammen med",
    "temaudvikling": "Temaudvikling: tre æraer",
    "strategi": "Temaerne og DTU's strategi 2026",
    "institutter": "Institutter i Dynamo",
    "oplag": "Oplag og målgruppe over tid",
    "appendiks": "Appendiks A: alle katalogiserede numre",
    "appendiks-b": "Appendiks B: alle",
    "kilder": "Kilder og forbehold",
}

out = subprocess.run(["pdftotext", "-layout", PDF, "-"], capture_output=True, text=True, check=True)
pages = out.stdout.split("\f")

result = {}
for key, needle in HEADINGS.items():
    found = None
    # skip page 1 (cover) and page 2 (TOC itself, which also lists this text)
    for i, page_text in enumerate(pages[2:], start=3):
        if needle in page_text:
            found = i
            break
    if found:
        result[key] = found
    else:
        print(f"WARNING: heading not found for '{key}' ({needle!r})")

with open(os.path.join(BASE, "data", "toc_pages.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("Wrote data/toc_pages.json:", result)
