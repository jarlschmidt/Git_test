# Dynamo gennem 20 år — indholdsanalyse

Analyse af DTU's profilmagasin *Dynamo* (nr. 1, 2005 – nr. 86, 2026): historier, temaer,
institutter og oplagsudvikling over 21 år.

## Filer

- **`Dynamo_gennem_20_aar.pdf`** — den færdige, søgbare rapport (13 sider, McKinsey-inspireret layout, DTU's officielle farver, rig på diagrammer — søjler, cirkeldiagrammer, et stablet år-for-år-tema-diagram, en oplags-linjegraf og en tidslinje der kobler Dynamos temaer til verdensbegivenheder).
- `report.html` — den fuldt genererede HTML, som PDF'en er printet fra (kan åbnes direkte i en browser).
- `template.html` — layout/CSS-skabelonen (uden indhold).
- `build_report.py` — samler de fire rå datakataloger i `data/`, interpolerer manglende år, tema-kategoriserer og skriver `data/dataset.json`.
- `build_html.py` — injicerer `data/dataset.json` i `template.html` og skriver `report.html`.
- `print_pdf.js` — bruger Playwright/Chromium til at printe `report.html` til søgbar PDF med korrekt sidetal-fod.
- `measure_toc.py` — læser en trykt PDF og finder den fysiske side, hvert kapitel rent faktisk starter på (sektionerne har ikke længere tvungne sideskift, så siderne kendes først efter layout); skriver `data/toc_pages.json`, som `build_html.py` bruger til at vise korrekte sidetal i indholdsfortegnelsen.
- `data/issues_01_20.json`, `issues_21_44.json`, `issues_45_66.json`, `issues_67_86.json` — katalog over hvert Dynamo-nummer (år, tema, beskrivelse, institutter, kilder, sikkerhedsniveau), indsamlet fra issuu.com/dtudk og DTU's nyhedsarkiv.
- `data/dtu_institutes.json` — DTU's nuværende institutter/centre (reference for institut-mapping).
- `data/dtu_strategy.json` — DTU's fem strategiske indsatsområder (Strategi 2026–2031, se kildelink i filen) og hvilke af rapportens 10 tema-kategorier der understøtter hvert område.
- `data/world_events.json` — ti velkendte verdensbegivenheder 2005–2026 (med kildelink pr. begivenhed), hver koblet til én af rapportens tema-kategorier, brugt i "Falder Dynamo sammen med verden?"-tidslinjen.
- `data/toc_pages.json` — cachede, målte sidetal til indholdsfortegnelsen (se `measure_toc.py`).
- `context_notes.md` — research-noter (historik, oplagstal, instituthistorik/omdøbninger).

## Gendan/opdater rapporten

Layoutet lader sektioner flyde frit hen over siderne (ingen tvunget sideskift pr.
afsnit), så rapporten ikke er fuld af blanke halvsider — det betyder til gengæld,
at de rigtige sidetal til indholdsfortegnelsen først kendes, efter rapporten er
trykt én gang. Kør derfor build-kæden to gange:

```
python3 build_report.py   # -> data/dataset.json
python3 build_html.py     # -> report.html (1. pass, omtrentlige/gamle sidetal)
node print_pdf.js         # -> Dynamo_gennem_20_aar.pdf (kræver playwright + chromium)
python3 measure_toc.py    # -> data/toc_pages.json (måler rigtige sidetal)
python3 build_html.py     # -> report.html (2. pass, korrekte sidetal)
node print_pdf.js         # -> Dynamo_gennem_20_aar.pdf (endelig)
```

## Diagrammer og farver

Alle diagrammer (søjler, cirkeldiagrammer, det stablede år-for-år-diagram) deler
samme faste kategori→farve-mapping (`CAT_COLOR` i `build_html.py`): de 6 største
tema-kategorier får hver sin farve i fast rækkefølge, resten samles under grå
"Øvrige temaer". Paletten er valideret med `dataviz`-skillets
`scripts/validate_palette.js` (fast farverækkefølge, ingen regnbue, adskillelse
under farveblindhed) — ændres kategori-farverne, bør paletten valideres igen.

## Kendte begrænsninger

- www.dtu.dk, alumni.dtu.dk og inside.dtu.dk var blokeret for direkte hentning i det miljø,
  analysen blev lavet i — kun issuu.com og et indekseret nyhedsarkiv var tilgængelige.
  Derfor er 2005–2014 markant tyndere dokumenteret end 2015–2026 (se metodeafsnittet i rapporten).
- Institut-tagging er baseret på eksplicitte nævninger i den tilgængelige forsidetekst —
  Dynamo navngiver sjældent institutter direkte, så denne dimension er tyndere end tema-dimensionen.
