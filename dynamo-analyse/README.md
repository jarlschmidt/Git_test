# Dynamo gennem 20 år — indholdsanalyse

Analyse af DTU's profilmagasin *Dynamo* (nr. 1, 2005 – nr. 86, 2026): historier, temaer,
institutter og oplagsudvikling over 21 år.

## Filer

- **`Dynamo_gennem_20_aar.pdf`** — den færdige, søgbare rapport (48 sider, McKinsey-inspireret layout, DTU's officielle farver). To dokumentationsniveauer: issue-niveau (forsidetema) for alle 86 numre, og historie-niveau (hver enkelt artikel, med institut og emne) for 1.013 historier i de 41 numre 2015–2026, hvor magasinets fulde tekst kunne udtrækkes.
- `report.html` — den fuldt genererede HTML, som PDF'en er printet fra (kan åbnes direkte i en browser).
- `template.html` — layout/CSS-skabelonen (uden indhold).
- `build_report.py` — samler de fire rå issue-datakataloger i `data/`, interpolerer manglende år, tema-kategoriserer og skriver `data/dataset.json`.
- `extract_issuu_text.py` — trækker den fulde, læsbare brødtekst ud af et issuu.com-nummer (bruger issuu's interne tekstlag-API til sin egen søgefunktion, ikke en offentlig dokumenteret API — se filens docstring). Kørt manuelt pr. nummer for 2015–2026; output blev læst og struktureret til `data/stories.json`.
- `build_html.py` — injicerer `data/dataset.json` + `data/stories.json` i `template.html` og skriver `report.html`.
- `print_pdf.js` — bruger Playwright/Chromium til at printe `report.html` til søgbar PDF med korrekt sidetal-fod.
- `measure_toc.py` — læser en trykt PDF og finder den fysiske side, hvert kapitel rent faktisk starter på (sektionerne har ikke længere tvungne sideskift, så siderne kendes først efter layout); skriver `data/toc_pages.json`, som `build_html.py` bruger til at vise korrekte sidetal i indholdsfortegnelsen.
- `data/issues_01_20.json`, `issues_21_44.json`, `issues_45_66.json`, `issues_67_86.json` — issue-niveau katalog over hvert Dynamo-nummer (år, tema, beskrivelse, institutter, kilder, sikkerhedsniveau), indsamlet fra issuu.com/dtudk og DTU's mediebibliotek (originale PDF'er).
- `data/stories.json` — historie-niveau katalog: 1.013 enkeltstående historier (nummer, år, titel, institut, emne) fra numrene 2015–2026, udtrukket via `extract_issuu_text.py` og struktureret manuelt pr. nummer.
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
Alle farver (både brand-farverne i `template.html` og kategori-paletten i
`build_html.py`) er DTU's officielle sekundærfarver med eksakte hex-værdier
fra designguide.dtu.dk/colours (rød #990000, navy #030f4f, blå #2f3eea,
orange #fc7634, samt rød #e83f48, grøn #1fd082/#008835 og lilla #79238e i
diagrammerne).

## Kendte begrænsninger

- 5 numre (41, 83, 84, 85, 86) kunne ikke historie-udtrækkes — enten fordi de ligger på en
  anden visningsplatform end issuu (41), eller fordi issuu's tekstlag-API afviste netop de
  numre (83, 84, 85, 86) — de har derfor kun issue-niveau-dokumentation (forsidetema), ikke
  historie-niveau.
- For 2005–2014 er 16 af 39 numre fortsat udokumenterede efter udvidet søgning i DTU's
  mediebibliotek (www.dtu.dk var oprindeligt netværksblokeret; adgangen er siden åbnet og
  36 numre er genresearchet med primærkilde-PDF'er). To lovende kilder for de resterende
  huller — yumpu.com og Wayback Machine — er blokeret af netværksproxyen i analysemiljøet.
- Institut-tagging på issue-niveau (alle 86 numre) er stadig sparsom, da forsidetemaer
  sjældent navngiver institutter direkte — men historie-niveau (2015–2026) viser et markant
  rigere billede: 69% af 1.013 historier navngiver et konkret DTU-institut. Se institutafsnittet
  i rapporten.
