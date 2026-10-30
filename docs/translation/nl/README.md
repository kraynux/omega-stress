<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT-licentie (zie het bestand LICENSE) -->
<div align="center">
  <img src="../../assets/omega-stress.png" alt="Omega-Stress" width="384">
</div>

# 🗲 OMEGA-STRESS

**Werkplek voor gecontroleerde HTTP-belastingtests**

> Gemaakt door **kraynux** voor **Omega-server** 
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Officiële pagina: [OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; Voorbeeld: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface en geëxporteerde rapporten beschikbaar in **17 talen** — zie [Talen van de interface](#talen-van-de-interface).  
**Talen:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)



**Omega-Stress** is een lokale terminaltoepassing (TUI met [Textual](https://github.com/Textualize/textual) + scriptbare CLI) die HTTP-belastingtests op een gecontroleerde en herbruikbare manier aanstuurt: bevroren profielen, geschiedenis, opnieuw uitvoeren, gedetailleerde exports (JSON/CSV/HTML), uitdrukkelijke veiligheidsgrenzen.

Het project volgt de principes van **Clean Architecture**, met een duidelijke scheiding tussen bedrijfsdomein, orkestratie, infrastructuur en gebruikersinterface.
---

## Inhoud

- [Presentatie](#presentatie)
- [Functies](#functies)
- [Architectuur](#architectuur)
- [Vereisten](#vereisten)
- [Installatie](#installatie)
- [Gebruik](#starten)
- [Duurprofielen D1-D6](#duurprofielen-d1-d6-profielmodus)
- [Veiligheidsmodus](#veiligheidsmodus)
- [Lokale kalibratie](#lokale-kalibratie)
- [Configuratie](#configuratie)
- [Tests en kwaliteit](#tests-en-kwaliteit)
- [Verwijderen](#verwijderen)
- [Bekende beperkingen](#bekende-beperkingen)
- [Licentie](#licentie)

## Presentatie

### Doelen

## Wat Omega-Stress doet (doel V1)

- Drie gecontroleerde testfamilies: **Verzoekentest** (doorvoer), **Verbindingstest** (gelijktijdigheid), **Belastingtest** (geleidelijke opbouw).
- **8 intensiteitsniveaus** (Zwak/Laag/Gemiddeld/Hoog/Krachtig/Agressief/Heftig/Maximaal), met een pre-checkmodel in 3 treden (nooit vereist / optioneel vereist / verplicht vereist — zie [Testwaarden](#testwaarden)).
- **Twee duurmodi**: handmatig (1 tot 5 min, begrensd per niveau) of **benoemd profiel D1-D6** (vaste totale duur met opwarmen/oploop/plateau/afbouw — zie [Duurprofielen D1-D6](#duurprofielen-d1-d6-profielmodus)).
- **Veiligheidsmodus** (standaard actief, bij elke start uit te schakelen): lokale CPU-/geheugengrenzen voor de hostmachine, los van de drempels die het geteste doel beschermen — zie [Veiligheidsmodus](#veiligheidsmodus).
- **Blijvende lokale kalibratie**: meet de werkelijke capaciteit van de hostmachine (nooit van het doel) via een lokale loopbackserver, in treden van toenemende belasting — zie [Lokale kalibratie](#lokale-kalibratie).
- Bevroren, herbruikbare profielen die in de geschiedenis worden bijgehouden — **optioneel**: een test draait net zo goed in handmatige modus, helemaal zonder profiel, door direct een doel te kiezen of in te voeren.
- Uitdrukkelijke bevestiging van autorisatie verplicht vóór elke uitvoering op een niet vastgepind doel.
- Automatische stopdrempels, nooit een onbegrensde belasting.
- Gedetailleerde JSON-/CSV-/HTML-exports (treden, metingen per interval, oordeel, diagnose).
- Niet-interactieve CLI-modus voor automatisering (cron, CI), die precies dezelfde use cases aanroept als de TUI.
- Automatische aanpassing aan de terminal (thema + te vereenvoudigen weergaveprofiel).

## Wat het project niet doet

- Het vervangt geen netwerkscantool — vocabulaire en houding van het product zijn bewust „belastingtest”, nooit „scan”.
- Het bevat geen externe belastingengine (k6 enz.) — native generatie met `httpx`/asyncio.
- Het start nooit een uitvoering zonder grenzen en zonder bevestiging van autorisatie.
- Het is geen gedistribueerde belastingtool: de generatie draait op één machine, in één proces — zie [Bekende beperkingen](#bekende-beperkingen).

## Functies

- **Drie testfamilies**, elk met 8 intensiteitsniveaus (Zwak/Laag/Gemiddeld/Hoog/Krachtig/Agressief/Heftig/Maximaal) — zie de tabel [Belastingreferenties](#testwaarden) voor de exacte waarden van elk niveau.
- **Bevroren testprofielen**: naam, doel, familie, intensiteit, duur, foutdrempel — één keer aangemaakt, identiek opnieuw gestart vanuit de TUI of de CLI.
- **Benoemde duurprofielen D1-D6** („profiel”-modus), alternatief voor de handmatige modus: een vaste totale duur (1 tot 120 min) met opwarmen/oploop/plateau/afbouw, die ook de toegankelijke niveaus begrenst — zie [Duurprofielen D1-D6](#duurprofielen-d1-d6-profielmodus).
- **Veiligheidsmodus**, standaard aangevinkt op elk startscherm: stopt een test als de hostmachine (niet het doel) in gevaar lijkt. Bewust uit te schakelen, met een herinnering die het gekozen niveau vergelijkt met de laatst uitgevoerde kalibratie — zie [Veiligheidsmodus](#veiligheidsmodus).
- **Blijvende lokale kalibratie**: meet wat de machine werkelijk aankan (7 treden van toenemende belasting tegen een ingebouwde lokale loopbackserver), te raadplegen vanuit het scherm Kalibratie — zie [Lokale kalibratie](#lokale-kalibratie).
- **Vastgepinde doelen**: bij een vastgepind adres hoeft de autorisatie niet bij elke start opnieuw te worden aangevinkt; recente niet vastgepinde doelen blijven zichtbaar (hoogstens 10), zonder stilzwijgende autorisatie. Een vastgepind doel is op twee onafhankelijke manieren te gebruiken: direct, om een test in handmatige modus zonder profiel te starten, of als standaarddoel bij het aanmaken van een bevroren profiel.
- **Volledige geschiedenis**: elke uitvoering wordt vastgelegd (oordeel, metingen, tijdlijn per interval, gebruikte veiligheidsmodus); een uitvoering die aan een bevroren profiel gekoppeld is, kan identiek worden herhaald.
- **Gedetailleerde exports** in JSON (ruwe, opnieuw te importeren gegevens), CSV (tabelanalyse) of HTML (leesbaar rapport, met een thema naar keuze uit de 10 paletten van het project). Het HTML-rapport wordt geschreven in de taal die in de Instellingen gekozen is („Taal van de exports”, standaard die van de interface); JSON en CSV blijven data en worden niet vertaald.
- **Pre-check**: automatisch en verplicht vóór elke test op Heftig/Maximaal, optioneel (maar met extra duren als ontgrendeling) op Krachtig/Agressief, met een geldigheidsvenster (24 u).
- **Live volgen** van een lopende test: voortgangsbalk met betrouwbaar aftellen (resterende tijd direct berekend, nooit geschat), doorvoer/fouten/p95-latentie bij elk interval bijgewerkt, handmatig stoppen mogelijk zonder de toepassing te verlaten.
- **Centrale instellingen**: thema (10 Omega-paletten + alle ingebouwde Textual-thema's, 31 in totaal via het opdrachtenpalet), weergaveprofiel (automatisch of geforceerd), map voor exports en schermafbeeldingen, opschonen van doelen/geschiedenis.
- **Ingebouwde help** (toets `a`): sneltoetsen, beschrijving van elk scherm (inclusief Kalibratie en Veiligheidsmodus), referentietabel van de belastingwaarden en tabel van de duurprofielen D1-D6.
- **Scriptbare CLI** (`omega-stress profile|run|history|export|calibrate ...`), precies dezelfde use cases als de TUI, met `--json`-uitvoer voor automatisering.
- **Automatische aanpassing aan de terminal**: familie en grootte bij het opstarten gedetecteerd, thema en weergaverijkdom daarop afgestemd (zie [Ondersteunde terminals](#ondersteunde-terminals)).

## Architectuur

Clean Architecture + Ports & Adapters in 9 pakketten (`app/`, `core/`, `domain/`, `application/`, `ports/`, `infrastructure/`, `interfaces/`, `plugins/`, `shared/`).
Volledige details: `ARCHITECTURE.md`.

```text
src/omega_stress/
├── app/              Bootstrap en container voor dependency injection (handmatige bedrading, geen DI-framework)
├── core/             Gedeeld vocabulaire: opsommingen, basisuitzonderingen, Result/Ok/Err, systeemmogelijkheden
├── domain/           Pure bedrijfslogica: belasting, profielen, uitvoeringen, doelen, thema's, terminal — zonder I/O
├── application/      Orkestratie: commands (acties), queries (leesacties), uitvoeringspipeline (guards/hooks)
├── ports/            Protocol-/ABC-contracten die de adapters verwachten (repositories, exporteurs, belastinggenerator...)
├── infrastructure/   Concrete implementaties: SQLite, JSON-/CSV-/HTML-exporteurs, httpx/asyncio-generator, terminaldetectie, systeemsonde
├── interfaces/       Twee onafhankelijke presentatie-adapters: TUI (Textual) en CLI (argparse)
├── plugins/          Gereserveerd uitbreidingspunt (laden van plugins) — basisstructuur aanwezig, niet uitgewerkt in V1
└── shared/           Gedeelde hulpmiddelen zonder bedrijfsafhankelijkheid (injecteerbare klok, aanmaken van identificaties)
```

### Ontwerpprincipes

- `domain/` bevat geen I/O en geen afhankelijkheid van de infrastructuur — pure bedrijfslogica, volledig te testen zonder mocks.
- `application/` orkestreert de use cases via het domein en de ports, nooit rechtstreeks via een concrete klasse uit `infrastructure/`.
- `infrastructure/` implementeert de ports zonder ooit rechtstreeks door `application/` of `domain/` te worden geïmporteerd — alleen `interfaces/` en `app/` verwijzen ernaar.
- `interfaces/` mag nooit rechtstreeks `infrastructure/` of `subprocess` aanroepen: alleen via `application/` (commands/queries) en de eigen controllers.
- `ports/` definieert de contracten die de adapters verwachten (Protocol), nooit een implementatie.
- `core/` bundelt het vocabulaire dat alle lagen delen, zonder er ooit een bedrijfsregel met cijfers in vast te leggen (drempels, duren, presets — altijd in `domain/*/policies.py`).

De Dependency Rule (alleen van buitenste naar binnenste lagen) en de isolatie van externe technologieën (`textual`, `sqlite3`, `httpx`, `jinja2`, elk beperkt tot zijn aangewezen ingangspunt) worden bij elke uitvoering van `lint-imports` automatisch gecontroleerd (zie [Tests en kwaliteit](#tests-en-kwaliteit)).

## Vereisten

- Python ≥ 3.10
- [`uv`](https://github.com/astral-sh/uv) aanbevolen voor het beheer van de afhankelijkheden (anders standaard `pip`)

### Systeem

- Linux, bij voorkeur Arch Linux en compatibele distributies.
- Python 3.10 of nieuwer.
- Geen rootrechten nodig: Omega-Stress doet alleen uitgaande HTTP-aanroepen als gewone gebruiker.

## Installatie

Het officiële archief wordt geleverd in `.tar.gz`-formaat. Controleer de integriteit vóór de installatie:

```bash
sha256sum omega-stress.tar.gz
```

### Methode 1 — installatiescript

```bash
[ -d omega-stress ] && echo "ℹ️ Hier al uitgepakt, stap overgeslagen." || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress bestaat al, verplaatsen overgeslagen." || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### Methode 2 — robuuste volledige installatie

Deze opdracht kan ongewijzigd worden gekopieerd en geplakt en zonder fouten opnieuw worden uitgevoerd: elke stap slaat over wat al gedaan is.

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```
`install.sh`:

1. Maakt de virtuele omgeving `.venv` aan als die nog niet bestaat.
2. Installeert de afhankelijkheden (`pip install -e .`; `pyproject.toml` blijft de enige bron van waarheid).
3. Maakt `omega-stress.sh` en `install.sh` uitvoerbaar.
4. Voegt de alias `stress` toe aan `~/.bashrc` en `~/.zshrc` (zonder dubbel als hij er al staat).

## Installatie (ontwikkeling)

```bash
uv sync --all-extras
# of, zonder uv:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```


### Starten

```bash
cd ~/omega-stress
./omega-stress.sh

# of typ gewoon "stress" in een nieuwe terminal als de alias is aangemaakt
```

Het startscript:

1. Detecteert `.venv`, `venv` of de systeem-Python.
2. Zet `PYTHONPATH` op `src/`.
3. Start `python -m omega_stress` — zonder argument opent het de TUI; met een argument stuurt het door naar de CLI.

### Talen van de interface

De interface is beschikbaar in 17 talen: Frans, Engels, Spaans, Portugees (Brazilië), Italiaans, Duits, Nederlands, Pools, Russisch, vereenvoudigd Chinees, Vietnamees, Thai, Indonesisch, Japans, Koreaans, Hindi en Arabisch. De keuze gebeurt in de Instellingen („Langue / Language”) en geldt na een herstart van de interface; de variabele `OMEGA_STRESS_LANG` (bijvoorbeeld `OMEGA_STRESS_LANG=nl ./omega-stress.sh`) legt voor één sessie een taal op. Gestart vanuit omega-suite neemt omega-stress de taal van de suite over. Op een Linux-tekstconsole (TTY) worden talen met een niet-Latijns schrift voor die sessie in het Engels getoond. De opdrachtregel blijft in het Frans.

### Gebruik van de CLI

```bash
omega-stress profile list                                     # profielen weergeven
omega-stress profile create --name "API-peiling" --target-id t-1 \
    --family request --level bas --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # een profiel bevriezen

# Verplichte pre-check vóór elke start op Heftig/Maximaal (optioneel op Krachtig/Agressief)
omega-stress run precheck --target-id t-1 --target-url https://exemple.org --confirm

omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level bas --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level moyen --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://exemple.org \
    --level puissant --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# Profielmodus D1-D6, in plaats van --duration-minutes (sluiten elkaar uit)
# D4 (resilience) staat Agressief zonder voorwaarde toe, Heftig met versterkte bevestiging
omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text JE_CONFIRME_LA_CIBLE_AUTORISEE

# --unsafe schakelt de veiligheidsmodus uit (lokale CPU-/geheugengrenzen); standaard afwezig
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # herhaalt een uitvoering die aan een bevroren profiel gekoppeld is

omega-stress history list                                      # geschiedenis van de uitvoeringen
omega-stress history show <run-id>                              # details van een uitvoering

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # start een kalibratie van deze machine
omega-stress calibrate show                                     # toont de laatst bekende kalibratie
```

De waarden van `--level` (`faible`, `bas`, `moyen`, `haut`, `puissant`, `agressif`, `violent`, `maximum`) en de bevestigingstekst blijven in het Frans, net als de rest van de opdrachtregel.

`--confirm` is de opdrachtregelversie van het autorisatievakje in de TUI: verplicht voor elk doel dat nog niet als geautoriseerd is vastgepind. Gelijke waarden voor `--target-id`/`--target-url` duiden een handmatig (niet vastgepind) doel aan; gebruik de identificatie van een al vastgepind doel om `--confirm` niet bij elke start te hoeven opgeven.

Voeg `--json` toe aan `history`/`export`/`calibrate` voor machineleesbare uitvoer, bruikbaar in cron/CI.

### Algemeen verloop

1. Bij de eerste start biedt het startscherm: Profielen, Verzoekentest, Verbindingstest, Belastingtest, Geschiedenis, Doelen, Kalibratie, Instellingen, Help.
2. Op een testscherm blijft bovenaan een bevroren profiel (optioneel) te selecteren: twee manieren om doel en criteria op te geven, nooit gecombineerd in één start —
   - **met een profiel**: het selecteren vult doel/intensiteit/duur/foutdrempel vooraf in en het veld voor het handmatige doel verdwijnt (het heeft dan geen zin meer); de vooraf ingevulde waarden blijven vóór de start aan te passen;
   - **zonder profiel (handmatige modus)**: een vastgepind/recent doel uit de lijst kiezen of een nieuw invoeren, de autorisatie aanvinken als het nog niet als geautoriseerd is vastgepind, intensiteit/duur (handmatig of duurprofiel D1-D6)/foutdrempel met de hand instellen.

   In beide gevallen: de veiligheidsmodus actief laten of bewust uitschakelen, een pre-check uitvoeren als het niveau dat vereist, en dan de test starten.
3. Het resultaat verschijnt meteen (oordeel, metingen, tijdlijn), zonder via de Geschiedenis te gaan — een export wordt rechtstreeks op dit scherm aangeboden.
4. Een profiel kan worden bevroren om dezelfde test later identisch opnieuw te starten, vanuit het scherm Profielen of door hem te herhalen vanuit de Geschiedenis.

### Testwaarden

8 intensiteitsniveaus, identiek in de drie testfamilies (alleen de gestuurde grootheid verandert) — volledig overzicht:

| Testtype | Niveau | Gestuurde grootheid | Streefwaarde | Pre-check | Beschikbare duren (handmatige modus) |
|---|---|---|---|---|---|
| Verzoekentest | Zwak | Doorvoer | 250 verz./min (≈4,2 verz./s) | Nee | 1 tot 5 min |
| Verzoekentest | Laag | Doorvoer | 500 verz./min (≈8,3 verz./s) | Nee | 1 tot 5 min |
| Verzoekentest | Gemiddeld | Doorvoer | 1000 verz./min (≈16,7 verz./s) | Nee | 1 tot 5 min |
| Verzoekentest | Hoog | Doorvoer | 2000 verz./min (≈33,3 verz./s) | Nee | 1 tot 5 min |
| Verzoekentest | Krachtig | Doorvoer | 6000 verz./min (≈100 verz./s) | Optioneel | 1 tot 3 min (5 met geslaagde pre-check) |
| Verzoekentest | Agressief | Doorvoer | 10.000 verz./min (≈167 verz./s) | Optioneel | 1 tot 3 min (5 met geslaagde pre-check) |
| Verzoekentest | Heftig | Doorvoer | 15.000 verz./min (≈250 verz./s) | **Verplicht** | Alleen 1 tot 3 min |
| Verzoekentest | Maximaal | Doorvoer | 20.000 verz./min (≈333 verz./s) | **Verplicht** | Alleen 1 tot 3 min |
| Verbindingstest | Zwak | Gelijktijdige verbindingen | 25 verbindingen | Nee | 1 tot 5 min |
| Verbindingstest | Laag | Gelijktijdige verbindingen | 50 verbindingen | Nee | 1 tot 5 min |
| Verbindingstest | Gemiddeld | Gelijktijdige verbindingen | 100 verbindingen | Nee | 1 tot 5 min |
| Verbindingstest | Hoog | Gelijktijdige verbindingen | 200 verbindingen | Nee | 1 tot 5 min |
| Verbindingstest | Krachtig | Gelijktijdige verbindingen | 1000 verbindingen | Optioneel | 1 tot 3 min (5 met geslaagde pre-check) |
| Verbindingstest | Agressief | Gelijktijdige verbindingen | 2000 verbindingen | Optioneel | 1 tot 3 min (5 met geslaagde pre-check) |
| Verbindingstest | Heftig | Gelijktijdige verbindingen | 3500 verbindingen | **Verplicht** | Alleen 1 tot 3 min |
| Verbindingstest | Maximaal | Gelijktijdige verbindingen | 5000 verbindingen | **Verplicht** | Alleen 1 tot 3 min |
| Belastingtest (geleidelijke opbouw) | Zwak | Doorvoer, als oploop | piek 250 verz./min | Nee | 1 tot 5 min |
| Belastingtest (geleidelijke opbouw) | Laag | Doorvoer, als oploop | piek 500 verz./min | Nee | 1 tot 5 min |
| Belastingtest (geleidelijke opbouw) | Gemiddeld | Doorvoer, als oploop | piek 1000 verz./min | Nee | 1 tot 5 min |
| Belastingtest (geleidelijke opbouw) | Hoog | Doorvoer, als oploop | piek 2000 verz./min | Nee | 1 tot 5 min |
| Belastingtest (geleidelijke opbouw) | Krachtig | Doorvoer, als oploop | piek 6000 verz./min | Optioneel | 1 tot 3 min (5 met geslaagde pre-check) |
| Belastingtest (geleidelijke opbouw) | Agressief | Doorvoer, als oploop | piek 10.000 verz./min | Optioneel | 1 tot 3 min (5 met geslaagde pre-check) |
| Belastingtest (geleidelijke opbouw) | Heftig | Doorvoer, als oploop | piek 15.000 verz./min | **Verplicht** | Alleen 1 tot 3 min |
| Belastingtest (geleidelijke opbouw) | Maximaal | Doorvoer, als oploop | piek 20.000 verz./min | **Verplicht** | Alleen 1 tot 3 min |

- **Pre-check Nee**: de test start direct, zonder voorwaarde aan de duur.
- **Pre-check Optioneel** (Krachtig/Agressief): de test start zonder pre-check (duren van 1-3 min), maar een geslaagde pre-check ontgrendelt ook de duren van 4-5 min.
- **Pre-check Verplicht** (Heftig/Maximaal): de test start niet zonder een vooraf geslaagde pre-check; de duur blijft ook met pre-check begrensd op 3 min (hier bepaalt de pre-check de toegang tot het niveau, geen langere duur).

De kolom „Beschikbare duren” hierboven dekt alleen de **handmatige modus** (hoogstens 5 min). Daarboven maakt alleen de [profielmodus D1-D6](#duurprofielen-d1-d6-profielmodus) langere tests mogelijk (tot 120 min) — elk profiel D1-D6 bepaalt zelf welke niveaus bij die duur toegankelijk blijven (`free_max_level`/`reinforced_level`, zie de eigen tabel):

| Niveau | Max. duur in handmatige modus | Max. duur via een profiel D1-D6 |
|---|---|---|
| Zwak / Laag / Gemiddeld / Hoog | 5 min | 120 min (D6, alleen Verbindingen/Belasting); 60 min bij Verzoeken (D5, D6 niet compatibel met deze familie) |
| Krachtig | 5 min (3 min zonder pre-check) | 120 min met versterkte bevestiging (D6, Verbindingen/Belasting) of 60 min zonder (D5) |
| Agressief | 5 min (3 min zonder pre-check) | 60 min met versterkte bevestiging (D5) of 30 min zonder (D4) |
| Heftig | 3 min (pre-check verplicht) | 30 min met versterkte bevestiging (D4) of 15 min zonder (D3) |
| Maximaal | 3 min (pre-check verplicht) | hoogstens 5 min (alleen D1/D2 — geen enkel profiel D3-D6 biedt Maximaal aan, ook niet met bevestiging) |

Dezelfde tabel is rechtstreeks in de toepassing beschikbaar (Help → Belastingreferenties), altijd gegenereerd uit dezelfde referentiewaarden (`domain/load/presets.py`, `domain/load/policies.py`) — nooit met de hand gedupliceerd.

> Bij de Belastingtest in **handmatige modus** worden oploop en plateau automatisch aangepast aan de gekozen duur (met behoud van de verhoudingen van de preset): een test van 1 min doorloopt de hele curve, van 0 tot de piek, niet alleen het begin ervan. In **profielmodus D1-D6** zorgt de indeling van elk profiel in opwarmen/oploop/plateau/afbouw vanzelf voor dezelfde garantie — zie [Duurprofielen D1-D6](#duurprofielen-d1-d6-profielmodus).

### Navigatie

- Pijltjes omhoog/omlaag: de cursor verplaatsen.
- `Tab` / `Shift+Tab`: tussen de velden van een formulier bewegen.
- `Esc`: teruggaan (bevestiging om af te sluiten vanaf het startscherm).
- `a`: help tonen.
- `t`: van thema wisselen.
- `q`: afsluiten (met bevestiging).
- `r`: vernieuwt de weergave, handig na het wijzigen van de terminalgrootte.
- `Ctrl+P`: opdrachtenpalet (thema wisselen, schermafbeelding, hulp bij sneltoetsen).

Wissel van thema met `t`: Omega-Stress past op elk scherm automatisch kleuren en weergaverijkdom aan de gedetecteerde mogelijkheden van de terminal aan. Vanuit het opdrachtenpalet (`Ctrl+P` → Thema) worden alle 31 beschikbare thema's aangeboden (10 Omega-thema's + 21 in Textual ingebouwde thema's).

### Ondersteunde terminals

Vier weergaveprofielen, van het rijkste tot het meest vereenvoudigde: **Volledig**, **Standaard**, **Beperkt**, **Mono**. Het gekozen profiel is het strengste van de gedetecteerde terminalfamilie en de werkelijke venstergrootte (nooit rijker dan een van beide plafonds).

| Terminal | Standaardprofiel |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | Volledig |
| Konsole, GNOME Terminal, Terminator, xfce4-terminal | Standaard |
| urxvt, xterm | Beperkt |
| Linux-TTY | Mono |
| SSH (true color/256 kleuren gedetecteerd) | Beperkt |
| SSH (minimaal signaal) | Mono |
| Niet herkende terminal | Beperkt (voorzichtige terugval) |

Onder 80 kolommen × 24 regels verschijnt vóór het startscherm een waarschuwingsscherm (nooit blokkerend: de toepassing blijft bruikbaar, in vereenvoudigde modus). Konsole, GNOME Terminal en Terminator worden herkend aan hun eigen kenmerkende omgevingsvariabele (`KONSOLE_VERSION`, `GNOME_TERMINAL_SCREEN`/`GNOME_TERMINAL_SERVICE`, `TERMINATOR_UUID`) in plaats van aan `TERM`, die ze op de generieke compatibiliteitswaarde laten staan — xfce4-terminal zet tot nu toe geen bekend gelijkwaardig kenmerk en valt daarom alleen terug op datzelfde profiel Standaard als het een herkenbare waarde voor `TERM`/`TERM_PROGRAM` toont, anders op Beperkt.

### Interne paden en systeempaden

Standaard werkt Omega-Stress in zijn eigen map `var/`, relatief ten opzichte van de map van waaruit het wordt gestart (of `$OMEGA_STRESS_VAR_DIR` als die is ingesteld):

```text
var/db/app.db           # SQLite-database (profielen, doelen, geschiedenis)
var/settings.json       # opgeslagen instellingen (thema, weergaveprofiel, standaardmappen)
var/exports/            # standaardexports JSON/CSV/HTML
var/screenshots/        # standaard SVG-schermafbeeldingen (opdrachtenpalet)
var/audit.jsonl         # auditlog (één regel per uitvoering)
var/app.log             # toepassingslog
```

Een absoluut systeempad (bijv. `/var/exports/`) wordt nooit standaard gebruikt — de `/` aan het begin is dus betekenisvol: alleen een uitdrukkelijke export naar een door de gebruiker gekozen map (Instellingen of het Export-scherm) komt erbuiten.

## Duurprofielen D1-D6 (profielmodus)

Alternatief voor de handmatige modus (duur 1-5 min, begrensd per niveau): een **benoemd duurprofiel**, met een vaste totale duur en een interne indeling in 4 fasen (opwarmen, oploop, plateau, afbouw). Te kiezen op elk startscherm (schakelaar „Duurmodus: Handmatig / Profiel D1-D6”) en in de CLI via `--duration-preset`.

| Profiel | Totale duur | Opwarmen | Oploop | Plateau | Afbouw | Max. niveau zonder bevestiging | Extra niveau (versterkte bevestiging) | Compatibele families |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 min | 5 s | 10 s | 40 s | 5 s | Maximaal | — | Verzoeken, Verbindingen, Belasting |
| D2 (short) | 5 min | 15 s | 30 s | 4 min | 15 s | Maximaal | — | Verzoeken, Verbindingen, Belasting |
| D3 (standard) | 15 min | 30 s | 1 min 30 | 12 min 30 | 30 s | Heftig | — | Verzoeken, Verbindingen, Belasting |
| D4 (resilience) | 30 min | 1 min | 3 min | 25 min | 1 min | Agressief | Heftig | Verzoeken, Verbindingen, Belasting |
| D5 (extended) | 60 min | 2 min | 5 min | 51 min | 2 min | Krachtig | Agressief | Verzoeken, Verbindingen, Belasting |
| D6 (soak) | 120 min | 3 min | 10 min | 104 min | 3 min | Hoog | Krachtig | Verbindingen, Belasting (nooit Verzoeken) |

- Het „extra” niveau (D4-D6) is alleen toegankelijk door precies de op het scherm getoonde tekst van de versterkte bevestiging in te typen — nooit met een simpel selectievakje.
- D6 sluit de Verzoekentest uit: een doorvoertest wordt begrensd in volume, wat nooit zinvol is bij een profiel van 2 u dat gericht is op afwijkingen in de tijd.
- Dezelfde tabel is in de toepassing beschikbaar (Help → Duurprofielen D1-D6).

## Veiligheidsmodus

Een selectievakje op elk startscherm (standaard aangevinkt) dat **uitsluitend** de veiligheidsgrenzen schakelt die de machine beschermen waarop Omega-Stress draait (CPU/geheugen van de lokale generator):

- **Altijd actief, ongeacht deze instelling**: de drempels die het **geteste doel** beschermen (foutpercentage, latentie) — ze uitschakelen heeft voor het product nooit zin; dat is niet wat dit vakje dekt.
- **Veiligheidsmodus actief (standaard)**: een test stopt automatisch als de hostmachine zelf onder druk lijkt te staan (CPU van de generator ÉN totale CPU van de machine tegelijk hoog, niet een van beide afzonderlijk — de normale verzadiging van één kern is op zich nooit genoeg).
- **Veiligheidsmodus uit**: deze lokale veiligheidsgrens vervalt. Er verschijnt dan een herinnering die het gekozen niveau vergelijkt met de laatst bekende kalibratie van deze machine (zie [Lokale kalibratie](#lokale-kalibratie)) — die envelop overschrijden blijft mogelijk, maar de betrouwbaarheid van het resultaat en de stabiliteit van de machine worden dan de verantwoordelijkheid van de gebruiker.

Ook in de CLI beschikbaar via `--unsafe` (standaard afwezig = veiligheidsmodus actief).

## Lokale kalibratie

Meet de werkelijke capaciteit van **deze machine** (nooit van het geteste doel): een in Omega-Stress ingebouwde lokale loopbackserver krijgt in treden een toenemende belasting, gegenereerd door dezelfde `httpx`/asyncio-engine als de echte tests.

- 7 treden, van rust (achtergrondruis van het systeem) tot 2000 verbindingen / 12.000 verz./s, elk getoetst aan gezondheidsdrempels (CPU van de generator ÉN totaal, beschikbaar geheugen, foutpercentage, bereikte doorvoer) — de laatste 2 treden zijn voorwaardelijk en worden overgeslagen als de vorige trede niet gezond is.
- Levert een veilige envelop op (`VU_safe` / `RPS_safe`) uit de laatste gezonde trede, met een veiligheidsmarge (~30 % reserve) en een vertrouwensniveau dat groeit met de bereikte diepte.
- **Alleen meten in V1**: het resultaat wordt niet automatisch toegepast om een echte test te begrenzen — het dient als informatieve referentie, vooral wanneer de [Veiligheidsmodus](#veiligheidsmodus) uitgeschakeld is.
- Per machine opgeslagen (niet-invasieve vingerafdruk: besturingssysteem/architectuur/aantal kernen/RAM, nooit een hardwareadres), op elk moment te raadplegen zonder opnieuw te meten.

Bereikbaar via het scherm **Kalibratie** van de TUI (knop „De kalibratie starten”, voortgang seconde voor seconde getoond), of in de CLI:

```bash
omega-stress calibrate run     # start een nieuwe kalibratie
omega-stress calibrate show    # toont de laatst bekende kalibratie, zonder een nieuwe te starten
```

## Configuratie

Alles wordt ingesteld via het scherm **Instellingen** van de TUI (geen configuratiebestand om met de hand te bewerken):

- **Thema**: een van de 10 Omega-thema's, direct toegepast en opgeslagen.
- **Weergaveprofiel**: Automatisch (detectie bij het opstarten) of handmatig geforceerd (Volledig/Standaard/Beperkt/Mono).
- **Standaardmap voor exports**: vult het veld „bestemming” van het Export-scherm vooraf in.
- **Standaardmap voor schermafbeeldingen**: gebruikt door de opdracht „Schermafbeelding” van het palet (`Ctrl+P`).
- **Opschoningen**: recente doelen (nooit de vastgepinde), alle doelen (inclusief de vastgepinde en hun autorisaties) of de volledige geschiedenis — elk beschermd door een eigen bevestiging.

De instellingen worden opgeslagen in `var/settings.json`. De hoofdmap `var/` zelf kan worden omgeleid via de omgevingsvariabele `OMEGA_STRESS_VAR_DIR` (handig om meerdere instanties te scheiden, of voor de tests).

## Tests en kwaliteit

```bash
pytest
ruff check .
mypy src
lint-imports   # controleert de Dependency Rule (zie pyproject.toml [tool.importlinter])
```

De suite omvat meer dan 570 tests (unit, integratie, TUI, CLI). `lint-imports` laat de CI mislukken als de Dependency Rule of de isolatie van externe technologieën wordt geschonden — zie [Architectuur](#architectuur).

## Verwijderen

Omega-Stress raakt niets aan buiten de eigen map en een optionele aliasregel:

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

`install.sh` maakt geen systeempakket, dienst of bestand buiten `~/omega-stress/` aan — verdere verwijdering is niet nodig.

## Bekende beperkingen

- Belasting gegenereerd **binnen het eigen proces**, op één machine (`httpx`/asyncio): het is geen gedistribueerde tool — de werkelijke plafonds (zie [Testwaarden](#testwaarden)) liggen duidelijk lager dan bij een SaaS-dienst voor belastingtests (loader.io enz.), bewust, als gecontroleerde producthouding. Op bescheiden hardware kunnen de niveaus Agressief/Heftig/Maximaal van de Verbindingstest duidelijk meer werkelijke tijd nodig hebben dan de gekozen duur om de volledige beoogde belasting te versturen — dan begrenst de capaciteit van **deze machine**, niet die van het doel, de werkelijke doorvoer; gebruik de [Lokale kalibratie](#lokale-kalibratie) om redelijke waarden voor uw hardware te kennen.
- De automatische detectie van de terminalfamilie berust op omgevingsvariabelen: xfce4-terminal heeft tot nu toe geen bekend betrouwbaar kenmerk (zie [Ondersteunde terminals](#ondersteunde-terminals)).
- `plugins/` is een uitbreidingspunt dat de architectuur voorziet (laden van ingebouwde/externe plugins), niet uitgewerkt in V1: de basisstructuur bestaat, er wordt geen plugin meegeleverd.
- `var/` is relatief ten opzichte van de projectmap (niet XDG): bedoeld voor lokaal gebruik door één gebruiker, niet voor gedeeld gebruik door meerdere gebruikers op dezelfde machine.
- De Belastingtest (geleidelijke opbouw) in **handmatige modus** heeft geen afbouwtrede („cooldown”) na het plateau — alleen beschikbaar via een [duurprofiel D1-D6](#duurprofielen-d1-d6-profielmodus), dat de 4 fasen vanzelf bevat.
- Een geslaagde pre-check is niet aan een bepaald doel gebonden: hij blijft 24 u geldig voor elke volgende start op Heftig/Maximaal, niet alleen op het gecontroleerde doel.
- De [Lokale kalibratie](#lokale-kalibratie) meet, maar past haar veilige envelop nog niet automatisch toe om een echte test te begrenzen — een bewust apart, nog niet begonnen werk.

## Licentie

MIT — zie `LICENSE`.
