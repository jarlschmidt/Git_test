# Projekt: Dynamo-analyse (DTU)

**Status pr. 2026-09-02:** Rapporten er redesignet efter feedback om at den
oprindelige version var for rodet (massevis af tom plads, fordi hver
sektion tvang et sideskift uanset indholdsmængde). Nyt layout: sektioner
flyder frit over siderne, appendiks-tabellen er én løbende tabel med
gentaget header i stedet for manuelt splittede sider, forsiden er redesignet
til en ren, solid navy-baggrund (ikke en "mudret" flerfarvet gradient), og en
graf-bug hvor værdi-labels (fx "60000 eks.") blev skåret af ved siderandet er
rettet. Rapporten er faldet fra 16 til 10 sider — samme indhold, ingen
whitespace-spild. Se `dynamo-analyse/README.md` for detaljer om filer og den
nye to-pass build (sidetal i indholdsfortegnelsen måles nu efter et
prøvetryk, se `measure_toc.py`).

**dtu.dk-netværksadgang:** Bekræftet åben i denne session (`curl -sI
https://www.dtu.dk` → 200, rigtigt DTU-indhold). Den oprindelige
netværksblokering nævnt nedenfor er altså ophævet — men indholdsanalysen
(datakataloget i `data/issues_*.json`) er IKKE genkørt med den nye adgang
endnu; se "Kendt begrænsning" nedenfor for hvad det næste skridt er, hvis
brugeren beder om det.

## Opgaven

Bruger (jarsc@dtu.dk) ønsker en søgbar PDF-rapport i McKinsey-stil, der giver
et overblik over DTU's magasin *Dynamo* (udkommet siden 2005, ca. 4 numre/år,
nu ved nr. 86) — historier, temaer og institutter over årene.

Branch: `claude/dtu-dynamo-analysis-43pgcd` (fortsæt arbejdet her, ikke på en ny branch,
medmindre brugeren beder om det).

## Leveret indtil videre

- `dynamo-analyse/Dynamo_gennem_20_aar.pdf` — 16-siders søgbar rapport, DTU's
  officielle farver (rød #990000, orange, blå — fra designguide.dtu.dk), Arial.
- `dynamo-analyse/data/issues_*.json` — katalog over alle 86 numre (år, tema,
  beskrivelse, institutter, kilder, sikkerhedsniveau — high/medium/low/not_found).
- `dynamo-analyse/build_report.py` + `build_html.py` + `print_pdf.js` — pipeline
  der genererer rapporten fra rådata (Python aggregering → HTML → Playwright/
  Chromium print til PDF med søgbart tekstlag).
- `dynamo-analyse/context_notes.md` — research-noter (lancering 28/4-2005,
  oplagsudvikling 60.000→17.000, instituthistorik/omdøbninger).

## Kendt begrænsning (VIGTIG — tjek ved ny session)

Da rapporten blev lavet, var **www.dtu.dk, alumni.dtu.dk og inside.dtu.dk
blokeret af netværksproxyen** i miljøet, selvom brugeren havde forsøgt at åbne
for dtu.dk. Kun `issuu.com`/`isu.pub` og et separat DTU-nyhedsarkiv-værktøj
(Raffle MCP-connector) virkede. Det betyder:

- Kun 58% af de 86 numre (50 stk.) kunne temadokumenteres, og især 2005–2014
  er tyndt dækket (kun issuu.com fra ca. 2015 og frem er komplet).
- Institut-tagging er meget sparsom (kun 7 eksplicitte nævninger i alt) —
  Dynamo navngiver sjældent institutter i den tekst, der var tilgængelig.

**Hvis brugeren har opdateret miljøets netværkspolitik (Allowlist med
www.dtu.dk, alumni.dtu.dk, inside.dtu.dk osv. — se instrukser givet i chatten),
tjek om adgangen nu virker** (prøv fx `curl -sI https://www.dtu.dk` eller en
WebFetch). Hvis ja, er næste skridt at:

1. Genbesøge de "not_found"-numre i `data/issues_*.json` med direkte adgang
   til dtu.dk's fulde artikeltekst (ikke kun issuu-forsider) — særligt
   2005–2014-perioden.
2. Udtrække institut-nævninger fra fuldtekst-artikler i stedet for kun
   issuu-beskrivelser, for at styrke institut-analysen markant.
3. Genkøre `build_report.py` → `build_html.py` → `print_pdf.js` og levere en
   opdateret PDF (samme filnavn, ny commit).

## Andre præferencer fra brugeren

- Brug DTU's officielle røde, orange og blå farver primært (ikke generisk
  navy/blue-palette).
- Alt tekst i rapporten skal sættes i Arial.
