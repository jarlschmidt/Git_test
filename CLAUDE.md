# Projekt: Dynamo-analyse (DTU)

**Status pr. 2026-09-07 (nyeste — nr. 85 modtaget, kun nr. 41 mangler nu):**
Bruger fandt og uploadede det rigtige nr. 85 (bæredygtig skibsfart, maj 2026,
fil "F_rdig_magasin_Dynamo_2026_02_Issue_1_1.pdf" — igen et misvisende filnavn,
verificeret som nr. 85 fra selve PDF'ens kolofon: "NR. 85 05 2026"). Læst med
`pdftotext -layout` og struktureret til 20 historier, tilføjet til
`data/stories.json` (nu 1.100 historier i alt). `STORY_UNCOVERED` er reduceret
til blot `[41]`. Issue-niveau-posten for nr. 85 i `data/issues_67_86.json` er
opgraderet til `confidence: "high"` med reelle institutter. Rapporten er nu
**66 sider**, og metode-/appendiksteksten er omskrevet, så den korrekt siger
"kun 1 nummer mangler" i stedet for at remse flere numre op. Med dette er
sessionens story-level-indsamling for 2015–2026 stort set komplet — kun nr. 41
(defunkt visningsplatform, emagstudio.win.dtu.dk) er reelt uopnåeligt uden en
ny kilde til netop det nummer.

**Status pr. 2026-09-07 (tidligere — bruger uploadede 3 af de 5 manglende numre):**
Bruger spurgte, om hun kunne sende de manglende numre (41, 83-86) direkte, og
uploadede derefter tre PDF'er: nr. 83 (2025), nr. 84 (marts 2026) og — vigtigt —
en fil navngivet "Dynamo_2026_03_Issuecompressed.pdf", som ved læsning viste sig
rent faktisk at være **nr. 86** (august 2026), ikke nr. 85 som filnavnet antydede.
Alle tre blev læst med `pdftotext -layout` (ikke `extract_issuu_text.py`, da issuu's
API netop afviste disse numre) og struktureret manuelt til historie-niveau: 22
historier for nr. 83 (kvantechips-tema), 24 for nr. 84 (AI-tema) og 21 for nr. 86
(vand-tema) — tilføjet til `data/stories.json` (nu 1.080 historier i alt, op fra
1.013). `STORY_UNCOVERED` i `build_html.py` er reduceret fra `[41, 83, 84, 85, 86]`
til `[41, 85]`. De tre numres issue-niveau-poster i `data/issues_67_86.json` er
opgraderet til `confidence: "high"` med reelle institutlister udledt af de nye
historier. Forsidens scope-linje/statistik er opdateret til "2015–2026" (var
"2015–2025"), da nr. 86's historier rykker den øvre grænse. Rapporten er vokset
fra 62 til 65 sider — udelukkende nyt, ægte indhold (Appendiks B + institutliste),
ikke whitespace. **Stadig manglende:** nr. 41 (defunkt platform) og det ægte nr. 85
(bruger har endnu ikke sendt det — pas på ikke at forveksle med filnavne, der
påstår "85" eller en bestemt måned; verificér altid nummeret fra selve PDF'ens
forside/kolofon, ikke filnavnet).

**Status pr. 2026-09-04 (tidligere — forsideredesign):** Bruger rapporterede en
konkret bug efter forrige forside-fix ("nederste 3.del er uden farve, teksten
går til kant") og krævede derefter et fuldstændigt redesign, ikke endnu et
patch ("jeg forventer at se en fuldstændig redesignet forside"). Root cause
på buggen: `.cover` i `template.html` havde stadig et gammelt negativt-margin
bleed-hack fra før `@page :first { margin: 0mm; }` blev indført — de to
regler modarbejdede hinanden og skubbede boksen ud over sidekanten. Løsning:
et reelt nyt visuelt layout, ikke bare fjernelse af den gamle regel — solid
navy-flade med en rød accent-bjælke, en dæmpet, overdimensioneret "21"-vandmærke-
tekst der udfylder det tomme rum midt på siden, og et tydeligt hvidt "datakort"
nederst der samler statistik-tiles og år-for-år-søjlediagrammet (løser buggen
ved design, ikke bare ved patch: det hvide kort har sin egen tydelige farve/
skygge, så "ingen farve nederst" ikke kan gentage sig). Forside-underteksten er
også omskrevet fra en metodetung sætning til et enkelt spørgsmål, som en
udenforstående kan følge. Verificeret visuelt via cover-only render før hele
to-pass-pipelinen blev kørt igen (62 sider, uændret). Committet og pushet.

**Status pr. 2026-09-02 (nyeste — historie-niveau):** Bruger afviste
issue-niveau-analysen som utilstrækkelig ("en analyse på baggrund af
forsider er jo mildest talt fesent... er der huller er rapporten
værdiløs") og krævede hver enkelt historie i magasinet, ikke kun
forsidetemaet. Løsning fundet: issuu.com gemmer internt et fuldt tekstlag
pr. side til sin søgefunktion, som kan trækkes ud direkte (se
`extract_issuu_text.py` — bruger issuu's uofficielle reader3-API, ikke en
dokumenteret offentlig API). Kørt for alle 46 numre 2015-2026: lykkedes for
41 (numre 42-82); 4 numre (83-86) gav 403 fra issuu's tekstlag-API, og nr.
41 ligger på en anden platform (emagstudio.win.dtu.dk, ikke længere
DNS-opløselig). De 41 numres tekst blev læst og struktureret til **1.013
historier** (titel, DTU-institut, emne, beskrivelse) i `data/stories.json`
via 6 parallelle baggrundsagenter. Samtidig blev de 36 dårligst dokumenterede
issue-niveau-numre (2005-2014, nr. 2-40) gen-researchet med den nu åbne
dtu.dk-adgang (DTU's eget mediebibliotek hoster de originale PDF'er af
gamle numre) — 19 af 36 blev opgraderet til reelt dokumenterede (primærkilde:
læst cover + indholdsfortegnelse), resten (mest nr. 22-32, 34-40) forbliver
ærligt "ikke fundet" efter udvidet søgning (yumpu.com og Wayback Machine er
blokeret af netværksproxyen — mulige næste skridt hvis adgang åbnes).

Rapporten er bygget om: institutanalysen viser nu 62 institutter/62% —
markant stærkere end de tidligere 7 nævninger — og der er tilføjet et helt
nyt "Appendiks B" med alle 1.013 historier. Rapporten er vokset til **48
sider** (op fra 13) — igen ægte nyt indhold (primært den lange, men
eksplicit ønskede, historie-liste), ikke whitespace.

**Vigtigt for næste session:** De midlertidige `data/stories_batch_*.json`-filer
er slettet efter merge til `data/stories.json` — kun sidstnævnte er kilden
fremover. Hvis flere numre skal historie-udtrækkes (fx nr. 83-86, hvis
issuu's API-blokering findes en vej rundt om), er mønstret: kør
`extract_issuu_text.py <slug> <outfile>`, læs outputtet, strukturér til
samme skema som `data/stories.json`, tilføj til filen, genkør build-kæden.

**Status pr. 2026-09-02 (tidligere — diagrammer):** Bruger bad om det modsatte af den
foregående minimalisme: en grundig rapport fuld af diagrammer, egnet til
senere at blive lavet om til et slideshow. Tilføjet: et stablet
år-for-år-tema-diagram (10 kategorier × 21 år), cirkeldiagrammer
(tema-fordeling, dokumentationsgrad), en linjegraf for oplagsudvikling, et
søjlediagram for institut-nævninger, og en ny sektion "Falder Dynamos temaer
sammen med det, der sker i verden?" — en tidslinje der kobler 10 kendte
verdensbegivenheder (COP15 2009, Fukushima 2011, Paris-aftalen 2015,
COVID-pandemien 2020, Ruslands invasion af Ukraine/energikrise 2022, ChatGPT
2022, EU's AI-forordning 2024, m.fl. — kilder i `data/world_events.json`) til
faktiske tal fra datasættet (fx "Digitalt, AI & Data topper i 2024, det
højeste antal i hele Dynamos historie for dette tema"). Alle kategori-farver
i diagrammerne er valideret med dataviz-skillets palette-validator (fast
rækkefølge, ingen regnbue, farveblindhedssikret) — se README.md. Rapporten
er nu 13 sider (op fra 10) — væksten er ægte nyt indhold/diagrammer, ikke
whitespace-spild; den tidligere no-forced-page-break-arkitektur holdt
stand under den større indholdsmængde.

**Status pr. 2026-09-02 (tidligere):** Rapporten er redesignet efter feedback om at den
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

**Nyt siden redesignet:** Appendiks-tabellen har nu en "Kilde"-kolonne med
klikbare links (issuu.com, dtu.dk, ing.dk m.fl.) pr. nummer, hentet fra
`source_urls` i `data/issues_*.json` (var indsamlet, men ikke vist i
rapporten før). Der er også en ny sektion "Temaerne og DTU's strategi
2026–2031" (efter Temaudvikling, før Institutter) der holder de 10
tema-kategorier op mod DTU's fem strategiske indsatsområder — data og
kildehenvisning i `data/dtu_strategy.json` (hentet fra dtu.dk 2026-09-02).
Ærligt om begrænsning: 2 af de 5 områder (uddannelse; videnskabeligt
lederskab/demokratisk ansvar) har ingen naturlig kobling til Dynamos
tema-taksonomi og er markeret som "–" i rapporten i stedet for tvunget ind.

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
