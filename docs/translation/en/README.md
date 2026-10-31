<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT License (see LICENSE file) -->
<div align="center">
  <img src="../../assets/omega-stress.png" alt="Omega-Stress" width="384">
</div>

# 🗲 OMEGA-STRESS

**Controlled HTTP load testing station**

> Built by [kraynux](https://github.com/kraynux) for [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Official page: [OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; Preview: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface and exported reports available in **17 languages** — see [Interface languages](#interface-languages).  
**Languages:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)



**Omega-Stress** is a local terminal application (a [Textual](https://github.com/Textualize/textual) TUI + a scriptable CLI) that drives HTTP load tests in a controlled, reusable way: frozen profiles, history, reruns, detailed exports (JSON/CSV/HTML), explicit safety bounds.

The project follows the principles of **Clean Architecture**, with a clear separation between the business domain, orchestration, infrastructure and the user interface.
---

## Table of contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#launching)
- [Duration profiles D1-D6](#duration-profiles-d1-d6-profile-mode)
- [Safety mode](#safety-mode)
- [Local calibration](#local-calibration)
- [Configuration](#configuration)
- [Tests and quality](#tests-and-quality)
- [Uninstalling](#uninstalling)
- [Known limitations](#known-limitations)
- [License](#license)

## Overview

### Goals

## What Omega-Stress does (V1 target)

- Three controlled test families: **Requests test** (throughput), **Connections test** (concurrency), **Load test** (gradual ramp-up).
- **8 intensity levels** (Low/Light/Medium/High/Powerful/Aggressive/Violent/Maximum), with a 3-tier pre-check model (never gated / optionally gated / mandatorily gated — see [Test values](#test-values)).
- **Two duration modes**: manual (1 to 5 min, bounded per level) or **named profile D1-D6** (fixed total duration with warm-up/ramp/plateau/cool-down — see [Duration profiles D1-D6](#duration-profiles-d1-d6-profile-mode)).
- **Safety mode** (on by default, can be turned off at each launch): local CPU/memory safeguards for the host machine, separate from the thresholds that protect the tested target — see [Safety mode](#safety-mode).
- **Persistent local calibration**: measures the real capacity of the host machine (never the target) through a local loopback server, in stages of increasing load — see [Local calibration](#local-calibration).
- Frozen, reusable, logged profiles — **optional**: a test runs just as well in manual mode, with no profile at all, by directly choosing/entering a target.
- Explicit authorization confirmation required before any run on a target that is not pinned.
- Automatic stop thresholds, never an unbounded load.
- Detailed JSON/CSV/HTML exports (stages, per-interval metrics, verdict, diagnosis).
- Non-interactive CLI mode for automation (cron, CI), calling exactly the same use cases as the TUI.
- Automatic adaptation to the terminal (theme + degradable rendering profile).

## What the project does not do

- It does not replace a network scanning tool — the product vocabulary and stance are deliberately "load testing", never "scanning".
- It implements no external load engine (k6, etc.) — native `httpx`/asyncio generation.
- It never starts a run without bounds and authorization confirmation.
- It is not a distributed load tool: generation runs on a single machine, in a single process — see [Known limitations](#known-limitations).

## Features

- **Three test families**, each with 8 intensity levels (Low/Light/Medium/High/Powerful/Aggressive/Violent/Maximum) — see the [Load references](#test-values) table for the exact values of each level.
- **Frozen test profiles**: name, target, family, intensity, duration, error threshold — created once, rerun identically from the TUI or the CLI.
- **Named duration profiles D1-D6** ("profile" mode), an alternative to manual mode: a fixed total duration (1 to 120 min) with warm-up/ramp/plateau/cool-down, which also bounds the accessible levels — see [Duration profiles D1-D6](#duration-profiles-d1-d6-profile-mode).
- **Safety mode**, checked by default on every launch screen: stops a test if the host machine (not the target) seems to be in danger. Can be turned off knowingly, with a reminder comparing the chosen level to the last calibration performed — see [Safety mode](#safety-mode).
- **Persistent local calibration**: measures what the machine can really handle (7 stages of increasing load against a built-in local loopback server), viewable from the Calibration screen — see [Local calibration](#local-calibration).
- **Pinned targets**: a pinned address no longer needs the authorization box to be checked at each launch; recent unpinned targets stay visible (10 at most) with no implicit authorization. A pinned target can be used in two independent ways: directly, to launch a test in manual mode without any profile, or as the default target when creating a frozen profile.
- **Complete history**: each run is logged (verdict, metrics, per-interval timeline, safety mode used); a run linked to a frozen profile can be replayed identically.
- **Detailed exports** in JSON (raw re-importable data), CSV (tabular analysis) or HTML (readable report, with a theme chosen among the project's 10 palettes). The HTML report is written in the language chosen in Settings ("Export language", by default the interface language); JSON and CSV stay data and are not translated.
- **Pre-check**, automatic and mandatory before any Violent/Maximum test, optional (but unlocking longer durations) on Powerful/Aggressive, with a validity window (24 h).
- **Live monitoring** of a running test: progress gauge with a reliable countdown (remaining time computed directly, never estimated), throughput/errors/p95 latency updated at each interval, manual stop possible without leaving the application.
- **Centralized settings**: theme (10 Omega palettes + all built-in Textual themes, 31 in total through the command palette), rendering profile (automatic or forced), export and screenshot folders, purge of targets/history.
- **Built-in help** (`a` key): keyboard shortcuts, description of each screen (including Calibration and Safety mode), reference table of load values and table of duration profiles D1-D6.
- **Scriptable CLI** (`omega-stress profile|run|history|export|calibrate ...`), exactly the same use cases as the TUI, with `--json` output available for automation.
- **Automatic adaptation to the terminal**: family and size detected at startup, theme and display richness adjusted accordingly (see [Supported terminals](#supported-terminals)).

## Architecture

Clean Architecture + Ports & Adapters in 9 packages (`app/`, `core/`, `domain/`, `application/`, `ports/`, `infrastructure/`, `interfaces/`, `plugins/`, `shared/`).
Full details: `ARCHITECTURE.md`.

```text
src/omega_stress/
├── app/              Bootstrap and dependency-injection container (manual wiring, no DI framework)
├── core/             Cross-cutting vocabulary: enumerations, root exceptions, Result/Ok/Err, system capabilities
├── domain/           Pure business logic: load, profiles, runs, targets, themes, terminal — no I/O
├── application/      Orchestration: commands (actions), queries (reads), execution pipeline (guards/hooks)
├── ports/            Protocol/ABC contracts expected by the adapters (repositories, exporters, load generator...)
├── infrastructure/   Concrete implementations: SQLite, JSON/CSV/HTML exporters, httpx/asyncio generator, terminal detection, system probe
├── interfaces/       Two independent presentation adapters: TUI (Textual) and CLI (argparse)
├── plugins/          Reserved extension point (plugin loading) — scaffolding present, not implemented in V1
└── shared/           Cross-cutting utilities with no business dependency (injectable clock, identifier generation)
```

### Design principles

- `domain/` contains no I/O and no dependency on the infrastructure — pure business logic, fully testable without mocks.
- `application/` orchestrates the use cases through the domain and the ports, never directly through a concrete class of `infrastructure/`.
- `infrastructure/` implements the ports without ever being imported directly by `application/` or `domain/` — only `interfaces/` and `app/` reference it.
- `interfaces/` must never call `infrastructure/` directly nor `subprocess`: only through `application/` (commands/queries) and its own controllers.
- `ports/` defines the contracts expected by the adapters (Protocol), never an implementation.
- `core/` holds the vocabulary shared by all layers, without ever encoding a quantified business rule (thresholds, durations, presets — always in `domain/*/policies.py`).

The Dependency Rule (outer layers → inner ones only) and the isolation of third-party technologies (`textual`, `sqlite3`, `httpx`, `jinja2`, each confined to its designated entry point) are checked automatically at each run of `lint-imports` (see [Tests and quality](#tests-and-quality)).

## Requirements

- Python ≥ 3.10
- [`uv`](https://github.com/astral-sh/uv) recommended for dependency management (otherwise standard `pip`)

### System

- Linux, primarily Arch Linux and compatible distributions.
- Python 3.10 or later.
- No root privilege required: Omega-Stress only makes outgoing HTTP calls as a normal user.

## Installation

The official archive is provided in `.tar.gz` format. Check its integrity before installing:

```bash
sha256sum omega-stress.tar.gz
```

### Method 1 — installation script

```bash
[ -d omega-stress ] && echo "ℹ️ Already extracted here, step skipped." || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress already exists, move skipped." || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### Method 2 — resilient full installation

This command can be copied and pasted as is and run again without error: each step skips what has already been done.

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```
`install.sh`:

1. Creates the `.venv` virtual environment if it does not already exist.
2. Installs the dependencies (`pip install -e .`; `pyproject.toml` remains the single source of truth).
3. Makes `omega-stress.sh` and `install.sh` executable.
4. Adds the `stress` alias to `~/.bashrc` and `~/.zshrc` (no duplicate if already present).

## Installation (development)

```bash
uv sync --all-extras
# or, without uv:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```


### Launching

```bash
cd ~/omega-stress
./omega-stress.sh

# or simply type "stress" in a new terminal if the alias was created
```

The launcher:

1. Detects `.venv`, `venv` or the system Python.
2. Sets `PYTHONPATH` to `src/`.
3. Runs `python -m omega_stress` — with no argument it opens the TUI; with an argument it dispatches to the CLI.

### Interface languages

The interface is available in 17 languages: French, English, Spanish, Portuguese (Brazil), Italian, German, Dutch, Polish, Russian, Simplified Chinese, Vietnamese, Thai, Indonesian, Japanese, Korean, Hindi and Arabic. The choice is made in Settings ("Langue / Language") and takes effect after the interface restarts; the `OMEGA_STRESS_LANG` variable (for example `OMEGA_STRESS_LANG=en ./omega-stress.sh`) forces a language for one session. When launched from omega-suite, omega-stress uses the suite's language. On a Linux text console (TTY), languages with a non-Latin script are shown in English for the session. The command line stays in French.

### Using the CLI

```bash
omega-stress profile list                                     # list the profiles
omega-stress profile create --name "API probe" --target-id t-1 \
    --family request --level bas --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # freeze a profile

# Mandatory pre-check before any Violent/Maximum run (optional on Powerful/Aggressive)
omega-stress run precheck --target-id t-1 --target-url https://exemple.org --confirm

omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level bas --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level moyen --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://exemple.org \
    --level puissant --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# Profile mode D1-D6, instead of --duration-minutes (mutually exclusive)
# D4 (resilience) allows Aggressive unconditionally, Violent with reinforced confirmation
omega-stress run request --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text JE_CONFIRME_LA_CIBLE_AUTORISEE

# --unsafe turns off safety mode (local CPU/memory safeguards); absent by default
omega-stress run connection --target-id t-1 --target-url https://exemple.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # replays a run linked to a frozen profile

omega-stress history list                                      # run history
omega-stress history show <run-id>                              # details of a run

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # runs a calibration of this machine
omega-stress calibrate show                                     # shows the last known calibration
```

The `--level` values (`faible`, `bas`, `moyen`, `haut`, `puissant`, `agressif`, `violent`, `maximum`) and the confirmation text stay in French, like the rest of the command line.

`--confirm` is the command-line equivalent of the TUI's authorization checkbox: required for any target that is not already pinned-authorized. Identical `--target-id`/`--target-url` values mean a manual (unpinned) target; use the identifier of an already pinned target to avoid `--confirm` at each launch.

Add `--json` to `history`/`export`/`calibrate` for machine-readable output, usable in cron/CI.

### General flow

1. At first launch, the home screen offers: Profiles, Requests test, Connections test, Load test, History, Targets, Calibration, Settings, Help.
2. From a test screen, a frozen profile (optional) can still be selected at the top of the screen: two ways to fill in the target and the criteria, never combined on the same launch —
   - **with a profile**: selecting it pre-fills target/intensity/duration/error threshold and the manual target field disappears (it no longer applies); the pre-filled values can still be edited before launching;
   - **without a profile (manual mode)**: choose a pinned/recent target from the list or enter a new one, check the authorization box if it is not already pinned-authorized, set intensity/duration (manual or duration profile D1-D6)/error threshold by hand.

   In both cases: leave safety mode on or turn it off knowingly, run a pre-check if the level requires it, then launch the test.
3. The result is shown immediately (verdict, metrics, timeline), without going back through History — an export is offered directly from this screen.
4. A profile can be frozen to rerun the same test identically later, from the Profiles screen or by replaying it from History.

### Test values

8 intensity levels, identical in the three test families (only the driven dimension changes) — full grid:

| Test type | Level | Driven dimension | Target value | Pre-check | Available durations (manual mode) |
|---|---|---|---|---|---|
| Requests test | Low | Throughput | 250 req/min (≈4.2 req/s) | No | 1 to 5 min |
| Requests test | Light | Throughput | 500 req/min (≈8.3 req/s) | No | 1 to 5 min |
| Requests test | Medium | Throughput | 1000 req/min (≈16.7 req/s) | No | 1 to 5 min |
| Requests test | High | Throughput | 2000 req/min (≈33.3 req/s) | No | 1 to 5 min |
| Requests test | Powerful | Throughput | 6000 req/min (≈100 req/s) | Optional | 1 to 3 min (5 if pre-check passed) |
| Requests test | Aggressive | Throughput | 10,000 req/min (≈167 req/s) | Optional | 1 to 3 min (5 if pre-check passed) |
| Requests test | Violent | Throughput | 15,000 req/min (≈250 req/s) | **Mandatory** | 1 to 3 min only |
| Requests test | Maximum | Throughput | 20,000 req/min (≈333 req/s) | **Mandatory** | 1 to 3 min only |
| Connections test | Low | Concurrent connections | 25 connections | No | 1 to 5 min |
| Connections test | Light | Concurrent connections | 50 connections | No | 1 to 5 min |
| Connections test | Medium | Concurrent connections | 100 connections | No | 1 to 5 min |
| Connections test | High | Concurrent connections | 200 connections | No | 1 to 5 min |
| Connections test | Powerful | Concurrent connections | 1000 connections | Optional | 1 to 3 min (5 if pre-check passed) |
| Connections test | Aggressive | Concurrent connections | 2000 connections | Optional | 1 to 3 min (5 if pre-check passed) |
| Connections test | Violent | Concurrent connections | 3500 connections | **Mandatory** | 1 to 3 min only |
| Connections test | Maximum | Concurrent connections | 5000 connections | **Mandatory** | 1 to 3 min only |
| Load test (gradual ramp-up) | Low | Throughput, ramped | peak 250 req/min | No | 1 to 5 min |
| Load test (gradual ramp-up) | Light | Throughput, ramped | peak 500 req/min | No | 1 to 5 min |
| Load test (gradual ramp-up) | Medium | Throughput, ramped | peak 1000 req/min | No | 1 to 5 min |
| Load test (gradual ramp-up) | High | Throughput, ramped | peak 2000 req/min | No | 1 to 5 min |
| Load test (gradual ramp-up) | Powerful | Throughput, ramped | peak 6000 req/min | Optional | 1 to 3 min (5 if pre-check passed) |
| Load test (gradual ramp-up) | Aggressive | Throughput, ramped | peak 10,000 req/min | Optional | 1 to 3 min (5 if pre-check passed) |
| Load test (gradual ramp-up) | Violent | Throughput, ramped | peak 15,000 req/min | **Mandatory** | 1 to 3 min only |
| Load test (gradual ramp-up) | Maximum | Throughput, ramped | peak 20,000 req/min | **Mandatory** | 1 to 3 min only |

- **Pre-check No**: the test starts directly, with no duration condition.
- **Pre-check Optional** (Powerful/Aggressive): the test starts without a pre-check (durations 1-3 min), but a passed pre-check also unlocks durations of 4-5 min.
- **Pre-check Mandatory** (Violent/Maximum): the test does not start without a previously passed pre-check; the duration stays capped at 3 min even with a pre-check (here the pre-check controls access to the level, not a longer duration).

The "Available durations" column above only covers **manual mode** (5 min at most). Beyond that, only [profile mode D1-D6](#duration-profiles-d1-d6-profile-mode) allows longer tests (up to 120 min) — each D1-D6 profile itself sets which levels remain accessible at that duration (`free_max_level`/`reinforced_level`, see its own table):

| Level | Max duration in manual mode | Max duration through a D1-D6 profile |
|---|---|---|
| Low / Light / Medium / High | 5 min | 120 min (D6, Connections/Load only); 60 min on Requests (D5, D6 not compatible with this family) |
| Powerful | 5 min (3 min without pre-check) | 120 min with reinforced confirmation (D6, Connections/Load) or 60 min without (D5) |
| Aggressive | 5 min (3 min without pre-check) | 60 min with reinforced confirmation (D5) or 30 min without (D4) |
| Violent | 3 min (mandatory pre-check) | 30 min with reinforced confirmation (D4) or 15 min without (D3) |
| Maximum | 3 min (mandatory pre-check) | 5 min at most (D1/D2 only — no D3-D6 profile offers Maximum, even with confirmation) |

This same table is available directly in the application (Help → Load references), always generated from the same reference values (`domain/load/presets.py`, `domain/load/policies.py`) — never duplicated by hand.

> On Load test in **manual mode**, the ramp and the plateau are automatically scaled to the chosen duration (keeping the preset's proportions): a 1-min test explores the whole curve, from 0 to the peak, not just its very beginning. In **profile mode D1-D6**, the same guarantee is provided natively by each profile's warm-up/ramp/plateau/cool-down split — see [Duration profiles D1-D6](#duration-profiles-d1-d6-profile-mode).

### Navigation

- Up/down arrows: move the cursor.
- `Tab` / `Shift+Tab`: move between the fields of a form.
- `Esc`: go back (exit confirmation from the home screen).
- `a`: show help.
- `t`: change theme.
- `q`: quit (with confirmation).
- `r`: refreshes the display, useful after resizing the terminal.
- `Ctrl+P`: command palette (change theme, screenshot, shortcut help).

Switch between themes with `t`: Omega-Stress automatically adapts the colors and the display richness to the detected capabilities of the terminal, from any screen. From the command palette (`Ctrl+P` → Theme), all 31 available themes are offered (10 Omega themes + 21 built-in Textual themes).

### Supported terminals

Four rendering profiles, from richest to most degraded: **Complete**, **Standard**, **Reduced**, **Mono**. The selected profile is the more restrictive of the detected terminal family and the actual window size (never richer than either of the two ceilings).

| Terminal | Default profile |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | Complete |
| Konsole, GNOME Terminal, Terminator, xfce4-terminal | Standard |
| urxvt, xterm | Reduced |
| Linux TTY | Mono |
| SSH (true color/256 colors detected) | Reduced |
| SSH (minimal signal) | Mono |
| Unrecognized terminal | Reduced (cautious fallback) |

Below 80 columns × 24 rows, a warning screen is shown before the home screen (never blocking: the application stays usable, in degraded mode). Konsole, GNOME Terminal and Terminator are recognized through their own characteristic environment variable (`KONSOLE_VERSION`, `GNOME_TERMINAL_SCREEN`/`GNOME_TERMINAL_SERVICE`, `TERMINATOR_UUID`) rather than `TERM`, which they leave at its generic compatibility value — xfce4-terminal sets no known equivalent marker to date and therefore falls back to this same Standard profile only if it exposes a recognizable `TERM`/`TERM_PROGRAM` value, Reduced otherwise.

### Internal paths and system paths

By default, Omega-Stress works in its own `var/` folder, relative to the directory it is launched from (or `$OMEGA_STRESS_VAR_DIR` if set):

```text
var/db/app.db           # SQLite database (profiles, targets, history)
var/settings.json       # persisted settings (theme, rendering profile, default folders)
var/exports/            # default JSON/CSV/HTML exports
var/screenshots/        # default SVG screenshots (command palette)
var/audit.jsonl         # audit log (one line per run)
var/app.log             # application log
```

An absolute system path (e.g. `/var/exports/`) is never used by default — the leading `/` is therefore significant: only an explicit export to a folder chosen by the user (Settings or the Export screen) leaves it.

## Duration profiles D1-D6 (profile mode)

An alternative to manual mode (duration 1-5 min bounded per level): a **named duration profile**, with a fixed total duration and an internal split into 4 phases (warm-up, ramp, plateau, cool-down). Selectable on each launch screen (toggle "Duration mode: Manual / Profile D1-D6") and in the CLI through `--duration-preset`.

| Profile | Total duration | Warm-up | Ramp | Plateau | Cool-down | Max level without confirmation | Extra level (reinforced confirmation) | Compatible families |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 min | 5 s | 10 s | 40 s | 5 s | Maximum | — | Requests, Connections, Load |
| D2 (short) | 5 min | 15 s | 30 s | 4 min | 15 s | Maximum | — | Requests, Connections, Load |
| D3 (standard) | 15 min | 30 s | 1 min 30 | 12 min 30 | 30 s | Violent | — | Requests, Connections, Load |
| D4 (resilience) | 30 min | 1 min | 3 min | 25 min | 1 min | Aggressive | Violent | Requests, Connections, Load |
| D5 (extended) | 60 min | 2 min | 5 min | 51 min | 2 min | Powerful | Aggressive | Requests, Connections, Load |
| D6 (soak) | 120 min | 3 min | 10 min | 104 min | 3 min | High | Powerful | Connections, Load (never Requests) |

- The "extra" level (D4-D6) is only accessible by typing exactly the reinforced confirmation text shown on screen — never a simple checkbox.
- D6 excludes the Requests test: a throughput test is bounded by volume, which is never relevant to a 2-hour profile focused on drift over time.
- This same table is available in the application (Help → Duration profiles D1-D6).

## Safety mode

A checkbox, present on every launch screen (checked by default), which toggles **only** the safeguards that protect the machine running Omega-Stress (CPU/memory of the local generator):

- **Always active, whatever this setting**: the thresholds that protect the **tested target** (error rate, latency) — turning them off never makes product sense; that is not what this box covers.
- **Safety mode on (default)**: a test stops automatically if the host machine itself seems under pressure (generator CPU AND overall machine CPU high at the same time, not one of the two in isolation — the normal saturation of a single core is never enough on its own).
- **Safety mode off**: this local safeguard is removed. A reminder is then shown, comparing the chosen level to the last known calibration for this machine (see [Local calibration](#local-calibration)) — going beyond that envelope remains possible, but the reliability of the result and the stability of the machine become the user's responsibility.

Also available in the CLI through `--unsafe` (absent by default = safety mode on).

## Local calibration

Measures the real capacity of **this machine** (never the tested target): a local loopback server built into Omega-Stress receives an increasing load in stages, generated by the same `httpx`/asyncio engine as real tests.

- 7 stages, from idle (system background noise) up to 2000 connections / 12,000 req/s, each assessed against health thresholds (generator AND overall CPU, available memory, error rate, throughput reached) — the last 2 stages are conditional, skipped if the previous stage is not healthy.
- Produces a safe envelope (`VU_safe` / `RPS_safe`) from the last healthy stage, with a safety margin (~30 % reserve) and a confidence level that grows with the depth reached.
- **Measurement only in V1**: the result is not applied automatically to cap a real test — it serves as an informative reference, especially when [Safety mode](#safety-mode) is turned off.
- Persisted per machine (non-invasive fingerprint: OS/architecture/number of cores/RAM, never a hardware address), viewable at any time without running a new measurement.

Available from the **Calibration** screen of the TUI ("Run the calibration" button, progress shown second by second), or in the CLI:

```bash
omega-stress calibrate run     # runs a new calibration
omega-stress calibrate show    # shows the last known calibration, without running a new one
```

## Configuration

Everything is set from the TUI's **Settings** screen (no configuration file to edit by hand):

- **Theme**: one of the 10 Omega themes, applied immediately and persisted.
- **Rendering profile**: Automatic (detection at startup) or forced manually (Complete/Standard/Reduced/Mono).
- **Default export folder**: pre-fills the "destination" field of the Export screen.
- **Default screenshot folder**: used by the palette's "Screenshot" command (`Ctrl+P`).
- **Purges**: recent targets (never pinned ones), all targets (including pinned ones and their authorizations), or the whole history — each protected by a dedicated confirmation.

Settings are persisted in `var/settings.json`. The `var/` root itself can be redirected through the `OMEGA_STRESS_VAR_DIR` environment variable (useful to isolate several instances, or for tests).

## Tests and quality

```bash
pytest
ruff check .
mypy src
lint-imports   # checks the Dependency Rule (see pyproject.toml [tool.importlinter])
```

The suite covers more than 570 tests (unit, integration, TUI, CLI). `lint-imports` fails the CI if the Dependency Rule or the isolation of third-party technologies is violated — see [Architecture](#architecture).

## Uninstalling

Omega-Stress touches nothing outside its own folder and an optional alias line:

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

No system package, service or file outside `~/omega-stress/` is created by `install.sh` — no further uninstallation is needed.

## Known limitations

- **In-process** load generation, on a single machine (`httpx`/asyncio): this is not a distributed tool — the real ceilings (see [Test values](#test-values)) are clearly more modest than a SaaS load testing service (loader.io, etc.), deliberately, as a controlled product stance. On modest hardware, the Aggressive/Violent/Maximum levels of the Connections test can take noticeably more real time than the selected duration to send the whole targeted load — it is then the capacity of **this machine**, not of the target, that limits the real throughput; use [Local calibration](#local-calibration) to find reasonable values for your hardware.
- Automatic detection of the terminal family relies on environment variables: xfce4-terminal has no known reliable marker to date (see [Supported terminals](#supported-terminals)).
- `plugins/` is an extension point planned by the architecture (loading of built-in/external plugins), not implemented in V1: the scaffolding exists, no plugin is shipped.
- `var/` is relative to the project folder (not XDG): designed for local single-user use, not for multi-user sharing on the same machine.
- The Load test (gradual ramp-up) in **manual mode** has no ramp-down ("cooldown") stage after the plateau — only available through a [duration profile D1-D6](#duration-profiles-d1-d6-profile-mode), which includes the 4 phases natively.
- A passed pre-check is not tied to a specific target: it stays valid for 24 h for any following Violent/Maximum launch, not only on the pre-checked target.
- [Local calibration](#local-calibration) measures, but does not yet automatically apply its safe envelope to cap a real test — a deliberately separate piece of work, not started.

## License

MIT — see `LICENSE`.
