# Dynamo gennem 20 år — indholdsanalyse

Analyse af DTU's profilmagasin *Dynamo* (nr. 1, 2005 – nr. 86, 2026): historier, temaer,
institutter og oplagsudvikling over 21 år.

## Filer

- **`Dynamo_gennem_20_aar.pdf`** — den færdige, søgbare rapport (16 sider, McKinsey-inspireret layout, DTU's officielle farver).
- `report.html` — den fuldt genererede HTML, som PDF'en er printet fra (kan åbnes direkte i en browser).
- `template.html` — layout/CSS-skabelonen (uden indhold).
- `build_report.py` — samler de fire rå datakataloger i `data/`, interpolerer manglende år, tema-kategoriserer og skriver `data/dataset.json`.
- `build_html.py` — injicerer `data/dataset.json` i `template.html` og skriver `report.html`.
- `print_pdf.js` — bruger Playwright/Chromium til at printe `report.html` til søgbar PDF med korrekt sidetal-fod.
- `data/issues_01_20.json`, `issues_21_44.json`, `issues_45_66.json`, `issues_67_86.json` — katalog over hvert Dynamo-nummer (år, tema, beskrivelse, institutter, kilder, sikkerhedsniveau), indsamlet fra issuu.com/dtudk og DTU's nyhedsarkiv.
- `data/dtu_institutes.json` — DTU's nuværende institutter/centre (reference for institut-mapping).
- `context_notes.md` — research-noter (historik, oplagstal, instituthistorik/omdøbninger).

## Gendan/opdater rapporten

```
python3 build_report.py   # -> data/dataset.json
python3 build_html.py     # -> report.html
node print_pdf.js         # -> Dynamo_gennem_20_aar.pdf (kræver playwright + chromium)
```

## Kendte begrænsninger

- www.dtu.dk, alumni.dtu.dk og inside.dtu.dk var blokeret for direkte hentning i det miljø,
  analysen blev lavet i — kun issuu.com og et indekseret nyhedsarkiv var tilgængelige.
  Derfor er 2005–2014 markant tyndere dokumenteret end 2015–2026 (se metodeafsnittet i rapporten).
- Institut-tagging er baseret på eksplicitte nævninger i den tilgængelige forsidetekst —
  Dynamo navngiver sjældent institutter direkte, så denne dimension er tyndere end tema-dimensionen.
