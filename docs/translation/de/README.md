<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT-Lizenz (siehe Datei LICENSE) -->
<div align="center">
  <img src="../../assets/omega-stress.png" alt="Omega-Stress" width="384">
</div>

# 🗲 OMEGA-STRESS

**Arbeitsplatz für kontrollierte HTTP-Lasttests**

> Entwickelt von **kraynux** für **Omega-server** 
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Offizielle Seite: [OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; Vorschau: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Oberfläche und exportierte Berichte in **17 Sprachen** verfügbar — siehe [Sprachen der Oberfläche](#sprachen-der-oberfläche).  
**Sprachen:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)



**Omega-Stress** ist eine lokale Terminalanwendung (TUI mit [Textual](https://github.com/Textualize/textual) + skriptfähige CLI), die HTTP-Lasttests kontrolliert und wiederverwendbar steuert: eingefrorene Profile, Verlauf, Wiederholung, ausführliche Exporte (JSON/CSV/HTML), ausdrückliche Sicherheitsgrenzen.

Das Projekt folgt den Prinzipien der **Clean Architecture**, mit einer klaren Trennung zwischen Fachdomäne, Orchestrierung, Infrastruktur und Benutzeroberfläche.
---

## Inhaltsverzeichnis

- [Überblick](#überblick)
- [Funktionen](#funktionen)
- [Architektur](#architektur)
- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Verwendung](#start)
- [Dauerprofile D1-D6](#dauerprofile-d1-d6-profilmodus)
- [Sicherheitsmodus](#sicherheitsmodus)
- [Lokale Kalibrierung](#lokale-kalibrierung)
- [Konfiguration](#konfiguration)
- [Tests und Qualität](#tests-und-qualität)
- [Deinstallation](#deinstallation)
- [Bekannte Einschränkungen](#bekannte-einschränkungen)
- [Lizenz](#lizenz)

## Überblick

### Ziele

## Was Omega-Stress tut (Ziel V1)

- Drei kontrollierte Testfamilien: **Anfragetest** (Durchsatz), **Verbindungstest** (Gleichzeitigkeit), **Lasttest** (schrittweiser Anstieg).
- **8 Intensitätsstufen** (Schwach/Niedrig/Mittel/Hoch/Stark/Aggressiv/Heftig/Maximal), mit einem dreistufigen Pre-Check-Modell (nie verlangt / optional verlangt / zwingend verlangt — siehe [Testwerte](#testwerte)).
- **Zwei Dauermodi**: manuell (1 bis 5 min, je Stufe begrenzt) oder **benanntes Profil D1-D6** (feste Gesamtdauer mit Aufwärmen/Rampe/Plateau/Abklingen — siehe [Dauerprofile D1-D6](#dauerprofile-d1-d6-profilmodus)).
- **Sicherheitsmodus** (standardmäßig aktiv, bei jedem Start abschaltbar): lokale CPU-/Speicher-Schutzgrenzen für den Host-Rechner, getrennt von den Schwellenwerten, die das getestete Ziel schützen — siehe [Sicherheitsmodus](#sicherheitsmodus).
- **Dauerhafte lokale Kalibrierung**: misst die tatsächliche Kapazität des Host-Rechners (nie des Ziels) über einen lokalen Loopback-Server, in Stufen steigender Last — siehe [Lokale Kalibrierung](#lokale-kalibrierung).
- Eingefrorene, wiederverwendbare, im Verlauf erfasste Profile — **optional**: Ein Test läuft genauso gut im manuellen Modus, ganz ohne Profil, indem man direkt ein Ziel auswählt oder eingibt.
- Ausdrückliche Autorisierungsbestätigung vor jedem Lauf auf ein nicht angeheftetes Ziel zwingend.
- Automatische Abbruchschwellen, nie eine unbegrenzte Last.
- Ausführliche JSON-/CSV-/HTML-Exporte (Stufen, Metriken pro Intervall, Urteil, Diagnose).
- Nicht interaktiver CLI-Modus für die Automatisierung (cron, CI), der genau dieselben Anwendungsfälle aufruft wie die TUI.
- Automatische Anpassung an das Terminal (Theme + reduzierbares Rendering-Profil).

## Was das Projekt nicht tut

- Es ersetzt kein Netzwerkscan-Werkzeug — Produktvokabular und Haltung lauten bewusst „Lasttest“, nie „Scan“.
- Es implementiert keine externe Last-Engine (k6 usw.) — native Erzeugung mit `httpx`/asyncio.
- Es startet keinen Lauf ohne Grenzen und ohne Autorisierungsbestätigung.
- Es ist kein verteiltes Lastwerkzeug: Die Erzeugung läuft auf einem einzigen Rechner, in einem einzigen Prozess — siehe [Bekannte Einschränkungen](#bekannte-einschränkungen).

## Funktionen

- **Drei Testfamilien**, jede mit 8 Intensitätsstufen (Schwach/Niedrig/Mittel/Hoch/Stark/Aggressiv/Heftig/Maximal) — siehe die Tabelle [Lastrichtwerte](#testwerte) für die exakten Werte jeder Stufe.
- **Eingefrorene Testprofile**: Name, Ziel, Familie, Intensität, Dauer, Fehlerschwelle — einmal angelegt, identisch erneut gestartet aus der TUI oder der CLI.
- **Benannte Dauerprofile D1-D6** („Profil“-Modus), Alternative zum manuellen Modus: eine feste Gesamtdauer (1 bis 120 min) mit Aufwärmen/Rampe/Plateau/Abklingen, die auch die zugänglichen Stufen begrenzt — siehe [Dauerprofile D1-D6](#dauerprofile-d1-d6-profilmodus).
- **Sicherheitsmodus**, auf jedem Startbildschirm standardmäßig aktiviert: bricht einen Test ab, wenn der Host-Rechner (nicht das Ziel) gefährdet erscheint. Bewusst abschaltbar, mit einem Hinweis, der die gewählte Stufe mit der letzten durchgeführten Kalibrierung vergleicht — siehe [Sicherheitsmodus](#sicherheitsmodus).
- **Dauerhafte lokale Kalibrierung**: misst, was der Rechner wirklich verkraftet (7 Stufen steigender Last gegen einen eingebauten lokalen Loopback-Server), einsehbar im Bildschirm Kalibrierung — siehe [Lokale Kalibrierung](#lokale-kalibrierung).
- **Angeheftete Ziele**: Bei einer angehefteten Adresse muss die Autorisierung nicht bei jedem Start erneut angehakt werden; nicht angeheftete neuere Ziele bleiben sichtbar (höchstens 10), ohne stillschweigende Autorisierung. Ein angeheftetes Ziel lässt sich auf zwei unabhängige Arten nutzen: direkt, um einen Test im manuellen Modus ohne Profil zu starten, oder als Standardziel beim Anlegen eines eingefrorenen Profils.
- **Vollständiger Verlauf**: Jeder Lauf wird protokolliert (Urteil, Metriken, Zeitverlauf pro Intervall, verwendeter Sicherheitsmodus); ein Lauf, der an ein eingefrorenes Profil gebunden ist, kann identisch wiederholt werden.
- **Ausführliche Exporte** als JSON (rohe, wieder importierbare Daten), CSV (tabellarische Auswertung) oder HTML (lesbarer Bericht, mit einem Theme aus den 10 Paletten des Projekts). Der HTML-Bericht wird in der in den Einstellungen gewählten Sprache geschrieben („Sprache der Exporte“, standardmäßig die der Oberfläche); JSON und CSV bleiben Daten und werden nicht übersetzt.
- **Pre-Check**: automatisch und zwingend vor jedem Test auf Heftig/Maximal, optional (schaltet aber längere Dauern frei) auf Stark/Aggressiv, mit Gültigkeitsfenster (24 h).
- **Live-Verfolgung** eines laufenden Tests: Fortschrittsanzeige mit zuverlässigem Countdown (Restzeit direkt berechnet, nie geschätzt), Durchsatz/Fehler/p95-Latenz in jedem Intervall aktualisiert, manueller Abbruch möglich, ohne die Anwendung zu verlassen.
- **Zentrale Einstellungen**: Theme (10 Omega-Paletten + alle eingebauten Textual-Themes, insgesamt 31 über die Befehlspalette), Rendering-Profil (automatisch oder erzwungen), Export- und Bildschirmfoto-Ordner, Bereinigung der Ziele/des Verlaufs.
- **Eingebaute Hilfe** (Taste `a`): Tastenkürzel, Beschreibung jedes Bildschirms (einschließlich Kalibrierung und Sicherheitsmodus), Referenztabelle der Lastwerte und Tabelle der Dauerprofile D1-D6.
- **Skriptfähige CLI** (`omega-stress profile|run|history|export|calibrate ...`), exakt dieselben Anwendungsfälle wie die TUI, mit `--json`-Ausgabe für die Automatisierung.
- **Automatische Anpassung an das Terminal**: Familie und Größe beim Start erkannt, Theme und Darstellungsreichtum entsprechend angepasst (siehe [Unterstützte Terminals](#unterstützte-terminals)).

## Architektur

Clean Architecture + Ports & Adapters in 9 Paketen (`app/`, `core/`, `domain/`, `application/`, `ports/`, `infrastructure/`, `interfaces/`, `plugins/`, `shared/`).
Vollständige Details: `ARCHITECTURE.md`.

```text
src/omega_stress/
├── app/              Bootstrap und Container für Dependency Injection (manuelle Verdrahtung, kein DI-Framework)
├── core/             Übergreifendes Vokabular: Aufzählungen, Wurzel-Ausnahmen, Result/Ok/Err, Systemfähigkeiten
├── domain/           Reine Fachlogik: Last, Profile, Läufe, Ziele, Themes, Terminal — ohne E/A
├── application/      Orchestrierung: commands (Aktionen), queries (Abfragen), Ausführungspipeline (guards/hooks)
├── ports/            Von den Adaptern erwartete Protocol-/ABC-Verträge (Repositories, Exporter, Lastgenerator...)
├── infrastructure/   Konkrete Implementierungen: SQLite, JSON-/CSV-/HTML-Exporter, httpx/asyncio-Generator, Terminalerkennung, Systemsonde
├── interfaces/       Zwei unabhängige Präsentationsadapter: TUI (Textual) und CLI (argparse)
├── plugins/          Reservierter Erweiterungspunkt (Laden von Plugins) — Grundgerüst vorhanden, in V1 nicht umgesetzt
└── shared/           Übergreifende Hilfsmittel ohne fachliche Abhängigkeit (injizierbare Uhr, Erzeugung von Kennungen)
```

### Entwurfsprinzipien

- `domain/` enthält weder E/A noch eine Abhängigkeit von der Infrastruktur — reine Fachlogik, vollständig ohne Mocks testbar.
- `application/` orchestriert die Anwendungsfälle über die Domäne und die Ports, nie direkt über eine konkrete Klasse aus `infrastructure/`.
- `infrastructure/` implementiert die Ports, ohne je direkt von `application/` oder `domain/` importiert zu werden — nur `interfaces/` und `app/` verweisen darauf.
- `interfaces/` darf nie direkt `infrastructure/` oder `subprocess` aufrufen: nur über `application/` (commands/queries) und die eigenen Controller.
- `ports/` definiert die von den Adaptern erwarteten Verträge (Protocol), nie eine Implementierung.
- `core/` bündelt das gemeinsame Vokabular aller Schichten, ohne darin je eine bezifferte Fachregel zu kodieren (Schwellenwerte, Dauern, Presets — immer in `domain/*/policies.py`).

Die Dependency Rule (nur von äußeren zu inneren Schichten) und die Isolierung der Fremdtechnologien (`textual`, `sqlite3`, `httpx`, `jinja2`, jede auf ihren vorgesehenen Einstiegspunkt beschränkt) werden bei jedem Lauf von `lint-imports` automatisch geprüft (siehe [Tests und Qualität](#tests-und-qualität)).

## Voraussetzungen

- Python ≥ 3.10
- [`uv`](https://github.com/astral-sh/uv) für die Verwaltung der Abhängigkeiten empfohlen (sonst normales `pip`)

### System

- Linux, vorrangig Arch Linux und kompatible Distributionen.
- Python 3.10 oder neuer.
- Keine Root-Rechte nötig: Omega-Stress führt nur ausgehende HTTP-Aufrufe als normaler Benutzer aus.

## Installation

Das offizielle Archiv wird im Format `.tar.gz` bereitgestellt. Prüfen Sie vor der Installation seine Integrität:

```bash
sha256sum omega-stress.tar.gz
```

### Methode 1 — Installationsskript

```bash
[ -d omega-stress ] && echo "ℹ️ Hier bereits entpackt, Schritt übersprungen." || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress existiert bereits, Verschieben übersprungen." || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### Methode 2 — robuste Komplettinstallation

Dieser Befehl kann unverändert kopiert und eingefügt und ohne Fehler erneut ausgeführt werden: Jeder Schritt überspringt, was schon erledigt ist.

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```
`install.sh`:

1. Legt die virtuelle Umgebung `.venv` an, falls sie noch nicht existiert.
2. Installiert die Abhängigkeiten (`pip install -e .`; `pyproject.toml` bleibt die einzige maßgebliche Quelle).
3. Macht `omega-stress.sh` und `install.sh` ausführbar.
4. Fügt den Alias `stress` zu `~/.bashrc` und `~/.zshrc` hinzu (ohne Duplikat, falls schon vorhanden).

## Installation (Entwicklung)

```bash
uv sync --all-extras
# oder, ohne uv:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```


### Start

```bash
cd ~/omega-stress
./omega-stress.sh

# oder einfach "stress" in einem neuen Terminal eingeben, falls der Alias angelegt wurde
```

Der Starter:

1. Erkennt `.venv`, `venv` oder das System-Python.
2. Setzt `PYTHONPATH` auf `src/`.
3. Startet `python -m omega_stress` — ohne Argument öffnet er die TUI; mit einem Argument leitet er an die CLI weiter.

### Sprachen der Oberfläche

Die Oberfläche ist in 17 Sprachen verfügbar: Französisch, Englisch, Spanisch, Portugiesisch (Brasilien), Italienisch, Deutsch, Niederländisch, Polnisch, Russisch, vereinfachtes Chinesisch, Vietnamesisch, Thailändisch, Indonesisch, Japanisch, Koreanisch, Hindi und Arabisch. Die Auswahl erfolgt in den Einstellungen („Langue / Language“) und gilt nach einem Neustart der Oberfläche; die Variable `OMEGA_STRESS_LANG` (zum Beispiel `OMEGA_STRESS_LANG=de ./omega-stress.sh`) erzwingt eine Sprache für eine Sitzung. Aus omega-suite gestartet, übernimmt omega-stress die Sprache der Suite. Auf einer Linux-Textkonsole (TTY) werden Sprachen mit nicht lateinischer Schrift für die Sitzung auf Englisch angezeigt. Die Kommandozeile bleibt auf Französisch.

### Verwendung der CLI

```bash
omega-stress profile list                                     # Profile auflisten
omega-stress profile create --name "API-Prüfung" --target-id t-1 \
    --family request --level bas --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # ein Profil einfrieren

# Zwingender Pre-Check vor jedem Start auf Heftig/Maximal (optional auf Stark/Aggressiv)
omega-stress run precheck --target-id t-1 --target-url https://exemple.org --confirm

omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level bas --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level moyen --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://exemple.org \
    --level puissant --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# Profilmodus D1-D6 statt --duration-minutes (schließen sich gegenseitig aus)
# D4 (resilience) erlaubt Aggressiv ohne Bedingung, Heftig mit verstärkter Bestätigung
omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text JE_CONFIRME_LA_CIBLE_AUTORISEE

# --unsafe schaltet den Sicherheitsmodus ab (lokale CPU-/Speicher-Schutzgrenzen); standardmäßig nicht gesetzt
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # wiederholt einen Lauf, der an ein eingefrorenes Profil gebunden ist

omega-stress history list                                      # Verlauf der Läufe
omega-stress history show <run-id>                              # Details eines Laufs

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # startet eine Kalibrierung dieses Rechners
omega-stress calibrate show                                     # zeigt die letzte bekannte Kalibrierung
```

Die Werte von `--level` (`faible`, `bas`, `moyen`, `haut`, `puissant`, `agressif`, `violent`, `maximum`) und der Bestätigungstext bleiben auf Französisch, wie die übrige Kommandozeile.

`--confirm` ist das Kommandozeilen-Gegenstück zum Autorisierungskästchen der TUI: Pflicht für jedes Ziel, das nicht bereits als autorisiert angeheftet ist. Gleiche Werte für `--target-id`/`--target-url` kennzeichnen ein manuelles (nicht angeheftetes) Ziel; verwenden Sie die Kennung eines bereits angehefteten Ziels, um `--confirm` bei jedem Start zu vermeiden.

Fügen Sie `--json` zu `history`/`export`/`calibrate` hinzu, um eine maschinenlesbare Ausgabe für cron/CI zu erhalten.

### Allgemeiner Ablauf

1. Beim ersten Start bietet der Startbildschirm: Profile, Anfragetest, Verbindungstest, Lasttest, Verlauf, Ziele, Kalibrierung, Einstellungen, Hilfe.
2. Auf einem Testbildschirm bleibt oben ein eingefrorenes Profil (optional) auswählbar: zwei Wege, Ziel und Kriterien anzugeben, nie im selben Start kombiniert —
   - **mit einem Profil**: Die Auswahl füllt Ziel/Intensität/Dauer/Fehlerschwelle vor, und das Feld für das manuelle Ziel verschwindet (es ist dann gegenstandslos); die vorbefüllten Werte bleiben vor dem Start änderbar;
   - **ohne Profil (manueller Modus)**: ein angeheftetes/neueres Ziel aus der Liste wählen oder ein neues eingeben, die Autorisierung anhaken, falls es noch nicht als autorisiert angeheftet ist, Intensität/Dauer (manuell oder Dauerprofil D1-D6)/Fehlerschwelle von Hand einstellen.

   In beiden Fällen: den Sicherheitsmodus aktiv lassen oder bewusst abschalten, einen Pre-Check ausführen, falls die Stufe ihn verlangt, und dann den Test starten.
3. Das Ergebnis erscheint sofort (Urteil, Metriken, Zeitverlauf), ohne Umweg über den Verlauf — ein Export wird direkt auf diesem Bildschirm angeboten.
4. Ein Profil kann eingefroren werden, um denselben Test später identisch erneut zu starten, über den Bildschirm Profile oder durch Wiederholung aus dem Verlauf.

### Testwerte

8 Intensitätsstufen, in den drei Testfamilien identisch (nur die gesteuerte Größe ändert sich) — vollständige Übersicht:

| Testart | Stufe | Gesteuerte Größe | Zielwert | Pre-Check | Verfügbare Dauern (manueller Modus) |
|---|---|---|---|---|---|
| Anfragetest | Schwach | Durchsatz | 250 Anfr./min (≈4,2 Anfr./s) | Nein | 1 bis 5 min |
| Anfragetest | Niedrig | Durchsatz | 500 Anfr./min (≈8,3 Anfr./s) | Nein | 1 bis 5 min |
| Anfragetest | Mittel | Durchsatz | 1000 Anfr./min (≈16,7 Anfr./s) | Nein | 1 bis 5 min |
| Anfragetest | Hoch | Durchsatz | 2000 Anfr./min (≈33,3 Anfr./s) | Nein | 1 bis 5 min |
| Anfragetest | Stark | Durchsatz | 6000 Anfr./min (≈100 Anfr./s) | Optional | 1 bis 3 min (5 mit bestandenem Pre-Check) |
| Anfragetest | Aggressiv | Durchsatz | 10.000 Anfr./min (≈167 Anfr./s) | Optional | 1 bis 3 min (5 mit bestandenem Pre-Check) |
| Anfragetest | Heftig | Durchsatz | 15.000 Anfr./min (≈250 Anfr./s) | **Zwingend** | Nur 1 bis 3 min |
| Anfragetest | Maximal | Durchsatz | 20.000 Anfr./min (≈333 Anfr./s) | **Zwingend** | Nur 1 bis 3 min |
| Verbindungstest | Schwach | Gleichzeitige Verbindungen | 25 Verbindungen | Nein | 1 bis 5 min |
| Verbindungstest | Niedrig | Gleichzeitige Verbindungen | 50 Verbindungen | Nein | 1 bis 5 min |
| Verbindungstest | Mittel | Gleichzeitige Verbindungen | 100 Verbindungen | Nein | 1 bis 5 min |
| Verbindungstest | Hoch | Gleichzeitige Verbindungen | 200 Verbindungen | Nein | 1 bis 5 min |
| Verbindungstest | Stark | Gleichzeitige Verbindungen | 1000 Verbindungen | Optional | 1 bis 3 min (5 mit bestandenem Pre-Check) |
| Verbindungstest | Aggressiv | Gleichzeitige Verbindungen | 2000 Verbindungen | Optional | 1 bis 3 min (5 mit bestandenem Pre-Check) |
| Verbindungstest | Heftig | Gleichzeitige Verbindungen | 3500 Verbindungen | **Zwingend** | Nur 1 bis 3 min |
| Verbindungstest | Maximal | Gleichzeitige Verbindungen | 5000 Verbindungen | **Zwingend** | Nur 1 bis 3 min |
| Lasttest (schrittweiser Anstieg) | Schwach | Durchsatz, als Rampe | Spitze 250 Anfr./min | Nein | 1 bis 5 min |
| Lasttest (schrittweiser Anstieg) | Niedrig | Durchsatz, als Rampe | Spitze 500 Anfr./min | Nein | 1 bis 5 min |
| Lasttest (schrittweiser Anstieg) | Mittel | Durchsatz, als Rampe | Spitze 1000 Anfr./min | Nein | 1 bis 5 min |
| Lasttest (schrittweiser Anstieg) | Hoch | Durchsatz, als Rampe | Spitze 2000 Anfr./min | Nein | 1 bis 5 min |
| Lasttest (schrittweiser Anstieg) | Stark | Durchsatz, als Rampe | Spitze 6000 Anfr./min | Optional | 1 bis 3 min (5 mit bestandenem Pre-Check) |
| Lasttest (schrittweiser Anstieg) | Aggressiv | Durchsatz, als Rampe | Spitze 10.000 Anfr./min | Optional | 1 bis 3 min (5 mit bestandenem Pre-Check) |
| Lasttest (schrittweiser Anstieg) | Heftig | Durchsatz, als Rampe | Spitze 15.000 Anfr./min | **Zwingend** | Nur 1 bis 3 min |
| Lasttest (schrittweiser Anstieg) | Maximal | Durchsatz, als Rampe | Spitze 20.000 Anfr./min | **Zwingend** | Nur 1 bis 3 min |

- **Pre-Check Nein**: Der Test startet direkt, ohne Bedingung an die Dauer.
- **Pre-Check Optional** (Stark/Aggressiv): Der Test startet ohne Pre-Check (Dauern 1-3 min), ein bestandener Pre-Check schaltet aber zusätzlich die Dauern 4-5 min frei.
- **Pre-Check Zwingend** (Heftig/Maximal): Der Test startet nicht ohne vorher bestandenen Pre-Check; die Dauer bleibt auch mit Pre-Check auf 3 min begrenzt (hier regelt der Pre-Check den Zugang zur Stufe, keine längere Dauer).

Die Spalte „Verfügbare Dauern“ oben deckt nur den **manuellen Modus** ab (höchstens 5 min). Darüber hinaus erlaubt nur der [Profilmodus D1-D6](#dauerprofile-d1-d6-profilmodus) längere Tests (bis 120 min) — jedes Profil D1-D6 legt selbst fest, welche Stufen bei dieser Dauer zugänglich bleiben (`free_max_level`/`reinforced_level`, siehe seine eigene Tabelle):

| Stufe | Max. Dauer im manuellen Modus | Max. Dauer über ein Profil D1-D6 |
|---|---|---|
| Schwach / Niedrig / Mittel / Hoch | 5 min | 120 min (D6, nur Verbindungen/Last); 60 min bei Anfragen (D5, D6 mit dieser Familie nicht kompatibel) |
| Stark | 5 min (3 min ohne Pre-Check) | 120 min mit verstärkter Bestätigung (D6, Verbindungen/Last) oder 60 min ohne (D5) |
| Aggressiv | 5 min (3 min ohne Pre-Check) | 60 min mit verstärkter Bestätigung (D5) oder 30 min ohne (D4) |
| Heftig | 3 min (Pre-Check zwingend) | 30 min mit verstärkter Bestätigung (D4) oder 15 min ohne (D3) |
| Maximal | 3 min (Pre-Check zwingend) | höchstens 5 min (nur D1/D2 — kein Profil D3-D6 bietet Maximal an, auch nicht mit Bestätigung) |

Dieselbe Tabelle steht direkt in der Anwendung zur Verfügung (Hilfe → Lastrichtwerte), stets aus denselben Referenzwerten erzeugt (`domain/load/presets.py`, `domain/load/policies.py`) — nie von Hand dupliziert.

> Beim Lasttest im **manuellen Modus** werden Rampe und Plateau automatisch an die gewählte Dauer angepasst (die Proportionen des Presets bleiben erhalten): Ein Test von 1 min durchläuft die ganze Kurve von 0 bis zur Spitze, nicht nur ihren Anfang. Im **Profilmodus D1-D6** sorgt die Aufteilung jedes Profils in Aufwärmen/Rampe/Plateau/Abklingen von sich aus für dieselbe Garantie — siehe [Dauerprofile D1-D6](#dauerprofile-d1-d6-profilmodus).

### Navigation

- Pfeiltasten nach oben/unten: den Cursor bewegen.
- `Tab` / `Umschalt+Tab`: zwischen den Feldern eines Formulars wechseln.
- `Esc`: zurückgehen (Bestätigung zum Beenden auf dem Startbildschirm).
- `a`: Hilfe anzeigen.
- `t`: Theme wechseln.
- `q`: beenden (mit Bestätigung).
- `r`: aktualisiert die Anzeige, nützlich nach einer Größenänderung des Terminals.
- `Ctrl+P`: Befehlspalette (Theme wechseln, Bildschirmfoto, Hilfe zu den Tastenkürzeln).

Wechseln Sie mit `t` zwischen den Themes: Omega-Stress passt Farben und Darstellungsreichtum auf jedem Bildschirm automatisch an die erkannten Fähigkeiten des Terminals an. Über die Befehlspalette (`Ctrl+P` → Theme) werden alle 31 verfügbaren Themes angeboten (10 Omega-Themes + 21 in Textual eingebaute Themes).

### Unterstützte Terminals

Vier Rendering-Profile, vom reichsten bis zum am stärksten reduzierten: **Vollständig**, **Standard**, **Reduziert**, **Mono**. Gewählt wird das strengere Profil aus erkannter Terminalfamilie und tatsächlicher Fenstergröße (nie reicher als eine der beiden Obergrenzen).

| Terminal | Standardprofil |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | Vollständig |
| Konsole, GNOME Terminal, Terminator, xfce4-terminal | Standard |
| urxvt, xterm | Reduziert |
| Linux-TTY | Mono |
| SSH (True Color/256 Farben erkannt) | Reduziert |
| SSH (minimales Signal) | Mono |
| Nicht erkanntes Terminal | Reduziert (vorsichtiger Rückfall) |

Unter 80 Spalten × 24 Zeilen erscheint vor dem Startbildschirm ein Warnbildschirm (nie blockierend: Die Anwendung bleibt im reduzierten Modus nutzbar). Konsole, GNOME Terminal und Terminator werden über ihre eigene charakteristische Umgebungsvariable erkannt (`KONSOLE_VERSION`, `GNOME_TERMINAL_SCREEN`/`GNOME_TERMINAL_SERVICE`, `TERMINATOR_UUID`) statt über `TERM`, das sie auf seinem generischen Kompatibilitätswert belassen — xfce4-terminal setzt bisher keine bekannte gleichwertige Markierung und fällt daher nur dann auf dasselbe Profil Standard zurück, wenn es einen erkennbaren `TERM`-/`TERM_PROGRAM`-Wert liefert, sonst auf Reduziert.

### Interne Pfade und Systempfade

Standardmäßig arbeitet Omega-Stress in seinem eigenen Ordner `var/`, relativ zum Verzeichnis, aus dem es gestartet wird (oder `$OMEGA_STRESS_VAR_DIR`, falls gesetzt):

```text
var/db/app.db           # SQLite-Datenbank (Profile, Ziele, Verlauf)
var/settings.json       # gespeicherte Einstellungen (Theme, Rendering-Profil, Standardordner)
var/exports/            # Standardordner für JSON-/CSV-/HTML-Exporte
var/screenshots/        # Standardordner für SVG-Bildschirmfotos (Befehlspalette)
var/audit.jsonl         # Audit-Protokoll (eine Zeile pro Lauf)
var/app.log             # Anwendungsprotokoll
```

Ein absoluter Systempfad (z. B. `/var/exports/`) wird nie standardmäßig verwendet — der führende `/` ist also bedeutsam: Nur ein ausdrücklicher Export in einen vom Nutzer gewählten Ordner (Einstellungen oder Export-Bildschirm) verlässt ihn.

## Dauerprofile D1-D6 (Profilmodus)

Alternative zum manuellen Modus (Dauer 1-5 min, je Stufe begrenzt): ein **benanntes Dauerprofil** mit fester Gesamtdauer und interner Aufteilung in 4 Phasen (Aufwärmen, Rampe, Plateau, Abklingen). Auswählbar auf jedem Startbildschirm (Umschalter „Dauermodus: Manuell / Profil D1-D6“) und in der CLI über `--duration-preset`.

| Profil | Gesamtdauer | Aufwärmen | Rampe | Plateau | Abklingen | Max. Stufe ohne Bestätigung | Zusätzliche Stufe (verstärkte Bestätigung) | Kompatible Familien |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 min | 5 s | 10 s | 40 s | 5 s | Maximal | — | Anfragen, Verbindungen, Last |
| D2 (short) | 5 min | 15 s | 30 s | 4 min | 15 s | Maximal | — | Anfragen, Verbindungen, Last |
| D3 (standard) | 15 min | 30 s | 1 min 30 | 12 min 30 | 30 s | Heftig | — | Anfragen, Verbindungen, Last |
| D4 (resilience) | 30 min | 1 min | 3 min | 25 min | 1 min | Aggressiv | Heftig | Anfragen, Verbindungen, Last |
| D5 (extended) | 60 min | 2 min | 5 min | 51 min | 2 min | Stark | Aggressiv | Anfragen, Verbindungen, Last |
| D6 (soak) | 120 min | 3 min | 10 min | 104 min | 3 min | Hoch | Stark | Verbindungen, Last (nie Anfragen) |

- Die „zusätzliche“ Stufe (D4-D6) ist nur zugänglich, wenn man genau den auf dem Bildschirm angezeigten Text der verstärkten Bestätigung eintippt — nie über ein einfaches Kontrollkästchen.
- D6 schließt den Anfragetest aus: Ein Durchsatztest wird über das Volumen begrenzt, was bei einem 2-Stunden-Profil, das auf das Driften über die Zeit zielt, nie sinnvoll ist.
- Dieselbe Tabelle steht in der Anwendung zur Verfügung (Hilfe → Dauerprofile D1-D6).

## Sicherheitsmodus

Ein Kontrollkästchen auf jedem Startbildschirm (standardmäßig aktiviert), das **ausschließlich** die Schutzgrenzen umschaltet, die den Rechner schützen, auf dem Omega-Stress läuft (CPU/Speicher des lokalen Generators):

- **Immer aktiv, unabhängig von dieser Einstellung**: die Schwellenwerte, die das **getestete Ziel** schützen (Fehlerquote, Latenz) — sie abzuschalten ergibt für das Produkt nie Sinn; das deckt dieses Kästchen nicht ab.
- **Sicherheitsmodus aktiv (Standard)**: Ein Test bricht automatisch ab, wenn der Host-Rechner selbst unter Druck zu stehen scheint (CPU des Generators UND Gesamt-CPU des Rechners gleichzeitig hoch, nicht eines von beiden allein — die normale Auslastung eines einzelnen Kerns reicht allein nie aus).
- **Sicherheitsmodus aus**: Diese lokale Schutzgrenze entfällt. Dann erscheint ein Hinweis, der die gewählte Stufe mit der letzten bekannten Kalibrierung dieses Rechners vergleicht (siehe [Lokale Kalibrierung](#lokale-kalibrierung)) — diese Hülle zu überschreiten bleibt möglich, doch die Zuverlässigkeit des Ergebnisses und die Stabilität des Rechners liegen dann in der Verantwortung des Nutzers.

Auch in der CLI über `--unsafe` verfügbar (standardmäßig nicht gesetzt = Sicherheitsmodus aktiv).

## Lokale Kalibrierung

Misst die tatsächliche Kapazität **dieses Rechners** (nie des getesteten Ziels): Ein in Omega-Stress eingebauter lokaler Loopback-Server erhält in Stufen eine steigende Last, erzeugt von derselben `httpx`/asyncio-Engine wie die echten Tests.

- 7 Stufen, vom Ruhezustand (Grundrauschen des Systems) bis zu 2000 Verbindungen / 12.000 Anfr./s, jede gegen Gesundheitsschwellen bewertet (CPU des Generators UND gesamt, verfügbarer Speicher, Fehlerquote, erreichter Durchsatz) — die letzten 2 Stufen sind bedingt und werden übersprungen, wenn die vorige Stufe nicht gesund ist.
- Ergibt eine sichere Hülle (`VU_safe` / `RPS_safe`) aus der letzten gesunden Stufe, mit Sicherheitsmarge (~30 % Reserve) und einer Vertrauensstufe, die mit der erreichten Tiefe wächst.
- **In V1 nur Messung**: Das Ergebnis wird nicht automatisch angewendet, um einen echten Test zu begrenzen — es dient als informativer Richtwert, vor allem wenn der [Sicherheitsmodus](#sicherheitsmodus) abgeschaltet ist.
- Pro Rechner gespeichert (nicht invasiver Fingerabdruck: Betriebssystem/Architektur/Anzahl der Kerne/RAM, nie eine Hardwareadresse), jederzeit einsehbar, ohne neu zu messen.

Erreichbar über den Bildschirm **Kalibrierung** der TUI (Schaltfläche „Kalibrierung starten“, Fortschritt sekundengenau angezeigt) oder in der CLI:

```bash
omega-stress calibrate run     # startet eine neue Kalibrierung
omega-stress calibrate show    # zeigt die letzte bekannte Kalibrierung, ohne neu zu messen
```

## Konfiguration

Alles wird im Bildschirm **Einstellungen** der TUI eingestellt (keine Konfigurationsdatei von Hand zu bearbeiten):

- **Theme**: eines der 10 Omega-Themes, sofort angewendet und gespeichert.
- **Rendering-Profil**: Automatisch (Erkennung beim Start) oder manuell erzwungen (Vollständig/Standard/Reduziert/Mono).
- **Standard-Exportordner**: füllt das Feld „Ziel“ des Export-Bildschirms vor.
- **Standardordner für Bildschirmfotos**: wird vom Befehl „Bildschirmfoto“ der Palette verwendet (`Ctrl+P`).
- **Bereinigungen**: neuere Ziele (nie die angehefteten), alle Ziele (einschließlich der angehefteten und ihrer Autorisierungen) oder der gesamte Verlauf — jede durch eine eigene Bestätigung geschützt.

Die Einstellungen werden in `var/settings.json` gespeichert. Das Wurzelverzeichnis `var/` selbst lässt sich über die Umgebungsvariable `OMEGA_STRESS_VAR_DIR` umleiten (nützlich, um mehrere Instanzen zu trennen, oder für Tests).

## Tests und Qualität

```bash
pytest
ruff check .
mypy src
lint-imports   # prüft die Dependency Rule (siehe pyproject.toml [tool.importlinter])
```

Die Suite umfasst mehr als 570 Tests (Unit, Integration, TUI, CLI). `lint-imports` lässt die CI fehlschlagen, wenn die Dependency Rule oder die Isolierung der Fremdtechnologien verletzt wird — siehe [Architektur](#architektur).

## Deinstallation

Omega-Stress verändert nichts außerhalb seines eigenen Ordners und einer optionalen Alias-Zeile:

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

`install.sh` legt weder Systempakete noch Dienste noch Dateien außerhalb von `~/omega-stress/` an — eine weitere Deinstallation ist nicht nötig.

## Bekannte Einschränkungen

- Lasterzeugung **im eigenen Prozess**, auf einem einzigen Rechner (`httpx`/asyncio): Es ist kein verteiltes Werkzeug — die tatsächlichen Obergrenzen (siehe [Testwerte](#testwerte)) sind deutlich bescheidener als bei einem SaaS-Lasttestdienst (loader.io usw.), bewusst, als kontrollierte Produkthaltung. Auf bescheidener Hardware können die Stufen Aggressiv/Heftig/Maximal des Verbindungstests deutlich mehr reale Zeit als die gewählte Dauer brauchen, um die gesamte vorgesehene Last abzugeben — dann begrenzt die Kapazität **dieses Rechners**, nicht die des Ziels, den tatsächlichen Durchsatz; nutzen Sie die [Lokale Kalibrierung](#lokale-kalibrierung), um vernünftige Werte für Ihre Hardware zu kennen.
- Die automatische Erkennung der Terminalfamilie beruht auf Umgebungsvariablen: xfce4-terminal hat bisher keine bekannte zuverlässige Markierung (siehe [Unterstützte Terminals](#unterstützte-terminals)).
- `plugins/` ist ein von der Architektur vorgesehener Erweiterungspunkt (Laden eingebauter/externer Plugins), in V1 nicht umgesetzt: Das Grundgerüst existiert, es wird kein Plugin mitgeliefert.
- `var/` ist relativ zum Projektordner (nicht XDG): gedacht für lokale Einzelnutzung, nicht für die gemeinsame Nutzung durch mehrere Benutzer auf demselben Rechner.
- Der Lasttest (schrittweiser Anstieg) im **manuellen Modus** hat nach dem Plateau keine Abstiegsstufe („Cooldown“) — nur über ein [Dauerprofil D1-D6](#dauerprofile-d1-d6-profilmodus) verfügbar, das die 4 Phasen von sich aus enthält.
- Ein bestandener Pre-Check ist nicht an ein bestimmtes Ziel gebunden: Er bleibt 24 h für jeden folgenden Start auf Heftig/Maximal gültig, nicht nur für das geprüfte Ziel.
- Die [Lokale Kalibrierung](#lokale-kalibrierung) misst, wendet ihre sichere Hülle aber noch nicht automatisch an, um einen echten Test zu begrenzen — ein bewusst getrenntes, noch nicht begonnenes Vorhaben.

## Lizenz

MIT — siehe `LICENSE`.
