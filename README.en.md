<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT License (see LICENSE file) -->
<div align="center">
  <img src="docs/assets/omega-stress.png" alt="Omega-Stress" width="256">
</div>

# 🗲 OMEGA-STRESS

**Controlled HTTP load-testing workstation**

> Developed by **kraynux** for **Omega-server**  
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Official page: [OMEGA-STRESS](https://kraynux.snake-mackarel.ts.net/omega-stress/) &nbsp; Preview: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-stress/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

**Languages:**  
[Français](README.md) · [English](README.en.md) · [Español](README.es.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md)



**Omega-Stress** is a local terminal application (Textual [TUI](https://github.com/Textualize/textual) + scriptable CLI) for running controlled and reusable HTTP load tests: fixed profiles, history, replay, detailed exports (JSON/CSV/HTML), and explicit safety limits.

The project follows **Clean Architecture** principles, with a clear separation between the business domain, orchestration, infrastructure, and user interface.


---

## Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [D1-D6 Duration Profiles](#d1-d6-duration-profiles-profile-mode)
- [Safety Mode](#safety-mode)
- [Local Calibration](#local-calibration)
- [Configuration](#configuration)
- [Testing and Quality](#testing-and-quality)
- [Uninstallation](#uninstallation)
- [Known Limitations](#known-limitations)
- [License](#license)

## Overview

### Goals

## What Omega-Stress does (V1 target)

- Three controlled test families: **Request Test** (throughput), **Connection Test** (concurrency), and **Load Test** (progressive ramp-up).
- **Eight intensity levels** (Low/Basic/Medium/High/Powerful/Aggressive/Violent/Maximum), with a three-tier pre-check model (never gated / optionally gated / mandatory gate — see [Test Values](#test-values)).
- **Two duration modes**: manual (1 to 5 minutes, bounded by level) or a named **D1-D6 profile** (fixed total duration with warm-up/ramp/plateau/cooldown — see [D1-D6 Duration Profiles](#d1-d6-duration-profiles-profile-mode)).
- **Safety Mode** (enabled by default and disableable at each launch): local CPU/memory safeguards for the host machine, separate from the thresholds protecting the tested target — see [Safety Mode](#safety-mode).
- **Persistent local calibration**: measures the actual capacity of the host machine (never the target) through a loopback server, using increasing load stages — see [Local Calibration](#local-calibration).
- Fixed, reusable, historical profiles.
- Explicit authorization confirmation required before every run against a target that is not pinned.
- Automatic stop thresholds; unbounded load is never allowed.
- Detailed JSON/CSV/HTML exports (stages, per-interval metrics, verdict, diagnosis).
- Non-interactive CLI mode for automation (cron, CI), invoking exactly the same use cases as the TUI.
- Automatic terminal adaptation (theme plus degradable rendering profile).

## What the project does not do

- It does not replace a network scanner — the product vocabulary and posture deliberately use “load test”, never “scan”.
- It does not implement an external load engine (k6, etc.) — load generation is native `httpx`/asyncio.
- It never starts a run without limits and authorization confirmation.
- It is not a distributed load-testing tool: generation runs on one machine, in one process — see [Known Limitations](#known-limitations).

## Features

- **Three test families**, each with eight intensity levels (Low/Basic/Medium/High/Powerful/Aggressive/Violent/Maximum); see the [Load Reference](#test-values) table for exact values.
- **Fixed test profiles**: name, target, family, intensity, duration, and error threshold — created once and replayed identically from the TUI or CLI.
- **Named D1-D6 duration profiles** (“profile” mode), an alternative to manual mode: a fixed total duration (1 to 120 minutes) with warm-up/ramp/plateau/cooldown, also limiting the levels that can be used — see [D1-D6 Duration Profiles](#d1-d6-duration-profiles-profile-mode).
- **Safety Mode**, checked by default on every launch screen: stops a test if the host machine, not the target, appears to be in danger. It can be disabled knowingly, with a reminder comparing the selected level with the latest calibration — see [Safety Mode](#safety-mode).
- **Persistent local calibration**: measures what the machine can actually sustain (seven increasing load stages against an integrated loopback server), available from the Calibration screen — see [Local Calibration](#local-calibration).
- **Pinned targets**: a pinned address does not require authorization to be checked again at every launch; recent unpinned targets remain visible (maximum 10) without implying authorization.
- **Complete history**: every run is logged (verdict, metrics, per-interval timeline, Safety Mode status); a run linked to a fixed profile can be replayed identically.
- **Detailed exports** in JSON (re-importable raw data), CSV (tabular analysis), or HTML (readable report, with a choice of the project's 10 palettes).
- **Automatic pre-check** mandatory before any Violent/Maximum test and optional (but unlocking additional durations) for Powerful/Aggressive, with a 24-hour validity window.
- **Live monitoring** of a running test: progress bar with reliable countdown (remaining time calculated directly, never estimated), throughput/errors/p95 latency updated at every interval, and manual stopping without leaving the application.
- **Centralized settings**: theme (10 Omega palettes plus all built-in Textual themes, 31 in total through the command palette), rendering profile (automatic or forced), export and screenshot directories, and target/history cleanup.
- **Built-in help** (`a` key): keyboard shortcuts, description of every screen (including Calibration and Safety Mode), load reference table, and D1-D6 duration-profile table.
- **Scriptable CLI** (`omega-stress profile|run|history|export|calibrate ...`), with exactly the same use cases as the TUI and `--json` output for automation.
- **Automatic terminal adaptation**: terminal family and size detected at startup, with theme and display richness adjusted accordingly (see [Supported Terminals](#supported-terminals)).

## Architecture

Clean Architecture + Ports & Adapters across nine packages (`app/`, `core/`, `domain/`, `application/`, `ports/`, `infrastructure/`, `interfaces/`, `plugins/`, `shared/`).
Full details: `ARCHITECTURE.md`.

```text
src/omega_stress/
├── app/              Bootstrap and dependency-injection container (manual wiring, no DI framework)
├── core/             Cross-cutting vocabulary: enums, root exceptions, Result/Ok/Err, system capabilities
├── domain/           Pure business logic: load, profiles, runs, targets, themes, terminal — no I/O
├── application/      Orchestration: commands, queries, execution pipeline (guards/hooks)
├── ports/            Protocol/ABC contracts expected by adapters (repositories, exporters, load generator...)
├── infrastructure/   Concrete implementations: SQLite, JSON/CSV/HTML exporters, httpx/asyncio generator, terminal detection, system probe
├── interfaces/       Two independent presentation adapters: TUI (Textual) and CLI (argparse)
├── plugins/          Reserved extension point (plugin loading) — scaffolding exists, not implemented in V1
└── shared/           Cross-cutting utilities without business dependencies (injectable clock, ID generation)
```

### Design principles

- `domain/` contains no I/O or infrastructure dependency: pure business logic, fully testable without mocks.
- `application/` orchestrates use cases through the domain and ports, never directly through a concrete `infrastructure/` class.
- `infrastructure/` implements ports and is never imported directly by `application/` or `domain/`; only `interfaces/` and `app/` reference it.
- `interfaces/` must never call `infrastructure/` or `subprocess` directly: only `application/` commands/queries and its own controllers.
- `ports/` defines adapter contracts (Protocol), never implementations.
- `core/` contains vocabulary shared by all layers, without encoding numeric business rules there (thresholds, durations and presets always belong in `domain/*/policies.py`).

The Dependency Rule (outer layers may depend only on inner layers) and third-party technology isolation (`textual`, `sqlite3`, `httpx`, and `jinja2` each confined to their designated entry point) are checked automatically every time `lint-imports` runs (see [Testing and Quality](#testing-and-quality)).

## Requirements

- Python ≥ 3.10
- [`uv`](https://github.com/astral-sh/uv) recommended for dependency management (standard `pip` also works)

### System

- Linux, primarily Arch Linux and compatible distributions.
- Python 3.10 or later.
- No root privileges required: Omega-Stress only makes outgoing HTTP calls as a normal user.

## Installation

The official archive is supplied as `.tar.gz`. Verify its integrity before installation:

```bash
sha256sum omega-stress.tar.gz
```

### Method 1 — installation script

```bash
[ -d omega-stress ] && echo "ℹ️ Already extracted here; skipping step." || tar -xzf omega-stress.tar.gz
[ -d ~/omega-stress ] && echo "ℹ️ ~/omega-stress already exists; skipping move." || mv omega-stress ~/
cd ~/omega-stress/
chmod +x install.sh
./install.sh
```

### Method 2 — resilient complete installation

This command can be copied and pasted as-is and safely rerun: each step skips work that has already been completed.

```bash
( [ -d omega-stress ] || tar -xzf omega-stress.tar.gz ) && \
( [ -d ~/omega-stress ] || mv omega-stress ~/ ) && \
cd ~/omega-stress && chmod +x install.sh && ./install.sh
```

`install.sh`:

1. Creates the `.venv` virtual environment if it does not already exist.
2. Installs dependencies (`pip install -e .`; `pyproject.toml` remains the single source of truth).
3. Makes `omega-stress.sh` and `install.sh` executable.
4. Adds the `stress` alias to `~/.bashrc` and `~/.zshrc` without duplicating it.

## Development installation

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

1. Detects `.venv`, `venv`, or system Python.
2. Sets `PYTHONPATH` to `src/`.
3. Runs `python -m omega_stress`: with no argument it opens the TUI; with an argument it dispatches to the CLI.

### CLI usage

```bash
omega-stress profile list                                     # list profiles
omega-stress profile create --name "API Probe" --target-id t-1 \
    --family request --level basic --duration-minutes 1 --max-error-rate 0.05
omega-stress profile freeze <profile-id>                       # freeze a profile

# Mandatory pre-check before every Violent/Maximum launch (optional for Powerful/Aggressive)
omega-stress run precheck --target-id t-1 --target-url https://example.org --confirm

omega-stress run request --target-id t-1 --target-url https://example.org \
    --level basic --duration-minutes 1 --max-error-rate 0.05 --confirm
omega-stress run connection --target-id t-1 --target-url https://example.org \
    --level medium --duration-minutes 3 --max-error-rate 0.05 --confirm
omega-stress run ramp --target-id t-1 --target-url https://example.org \
    --level powerful --duration-minutes 3 --max-error-rate 0.05 --confirm --precheck-validated

# D1-D6 profile mode instead of --duration-minutes (mutually exclusive)
# D4 (resilience) allows Aggressive without conditions and Violent with reinforced confirmation
omega-stress run request --target-id t-1 --target-url https://example.org \
    --level violent --duration-preset d4 --max-error-rate 0.05 --confirm \
    --precheck-validated --confirmation-text I_CONFIRM_THE_AUTHORIZED_TARGET

# --unsafe disables Safety Mode (local CPU/memory safeguards); absent by default
omega-stress run connection --target-id t-1 --target-url https://example.org \
    --level violent --duration-minutes 1 --max-error-rate 0.05 --confirm \
    --precheck-validated --unsafe

omega-stress run replay <run-id> --confirm                     # replay a run linked to a frozen profile

omega-stress history list                                      # run history
omega-stress history show <run-id>                              # run details

omega-stress export <run-id> --format html --destination var/exports --theme omega-base

omega-stress calibrate run                                      # calibrate this machine
omega-stress calibrate show                                     # show the latest known calibration
```

`--confirm` is the command-line equivalent of the TUI authorization checkbox. It is required for any target that is not already pinned and authorized. Identical `--target-id`/`--target-url` values indicate a manual, non-pinned target; use the identifier of an already pinned target to avoid `--confirm` on every launch.

Add `--json` to `history`, `export`, or `calibrate` for machine-readable output suitable for cron/CI.

### General workflow

1. On first launch, the home screen offers: Profiles, Request Test, Connection Test, Load Test, History, Targets, Calibration, Settings, and Help.
2. From a test screen: choose or enter a target, check authorization if it is not already pinned and authorized, set intensity/duration (manual or D1-D6 profile)/error threshold, keep Safety Mode enabled or knowingly disable it, run a pre-check if required by the level, then start the test.
3. The result appears immediately (verdict, metrics, timeline), without returning through History; an export can be launched directly from this screen.
4. A profile can be frozen to replay the same test identically later, from Profiles or by replaying it from History.

### Test values

Eight intensity levels are identical across the three test families; only the controlled dimension changes:

| Test type | Level | Controlled dimension | Target value | Pre-check | Available durations (manual mode) |
|---|---|---|---|---|---|
| Request Test | Low | Throughput | 250 req/min (≈4.2 req/s) | No | 1 to 5 min |
| Request Test | Basic | Throughput | 500 req/min (≈8.3 req/s) | No | 1 to 5 min |
| Request Test | Medium | Throughput | 1000 req/min (≈16.7 req/s) | No | 1 to 5 min |
| Request Test | High | Throughput | 2000 req/min (≈33.3 req/s) | No | 1 to 5 min |
| Request Test | Powerful | Throughput | 6000 req/min (≈100 req/s) | Optional | 1 to 3 min (5 if pre-check validated) |
| Request Test | Aggressive | Throughput | 10,000 req/min (≈167 req/s) | Optional | 1 to 3 min (5 if pre-check validated) |
| Request Test | Violent | Throughput | 15,000 req/min (≈250 req/s) | **Mandatory** | 1 to 3 min only |
| Request Test | Maximum | Throughput | 20,000 req/min (≈333 req/s) | **Mandatory** | 1 to 3 min only |
| Connection Test | Low | Concurrent connections | 25 connections | No | 1 to 5 min |
| Connection Test | Basic | Concurrent connections | 50 connections | No | 1 to 5 min |
| Connection Test | Medium | Concurrent connections | 100 connections | No | 1 to 5 min |
| Connection Test | High | Concurrent connections | 200 connections | No | 1 to 5 min |
| Connection Test | Powerful | Concurrent connections | 1000 connections | Optional | 1 to 3 min (5 if pre-check validated) |
| Connection Test | Aggressive | Concurrent connections | 2000 connections | Optional | 1 to 3 min (5 if pre-check validated) |
| Connection Test | Violent | Concurrent connections | 3500 connections | **Mandatory** | 1 to 3 min only |
| Connection Test | Maximum | Concurrent connections | 5000 connections | **Mandatory** | 1 to 3 min only |
| Load Test (progressive ramp) | Low | Throughput, ramped | peak 250 req/min | No | 1 to 5 min |
| Load Test (progressive ramp) | Basic | Throughput, ramped | peak 500 req/min | No | 1 to 5 min |
| Load Test (progressive ramp) | Medium | Throughput, ramped | peak 1000 req/min | No | 1 to 5 min |
| Load Test (progressive ramp) | High | Throughput, ramped | peak 2000 req/min | No | 1 to 5 min |
| Load Test (progressive ramp) | Powerful | Throughput, ramped | peak 6000 req/min | Optional | 1 to 3 min (5 if pre-check validated) |
| Load Test (progressive ramp) | Aggressive | Throughput, ramped | peak 10,000 req/min | Optional | 1 to 3 min (5 if pre-check validated) |
| Load Test (progressive ramp) | Violent | Throughput, ramped | peak 15,000 req/min | **Mandatory** | 1 to 3 min only |
| Load Test (progressive ramp) | Maximum | Throughput, ramped | peak 20,000 req/min | **Mandatory** | 1 to 3 min only |

- **Pre-check: No**: the test starts directly, with no duration condition.
- **Optional pre-check** (Powerful/Aggressive): the test can start without a pre-check for 1–3 minutes; a validated pre-check also unlocks 4–5-minute durations.
- **Mandatory pre-check** (Violent/Maximum): the test cannot start without a previously validated pre-check; even with one, duration remains capped at 3 minutes. Here the pre-check controls access to the level, not an extended duration.

The “Available durations” column above covers **manual mode** only (1–5 minutes maximum). For longer tests, only [D1-D6 profile mode](#d1-d6-duration-profiles-profile-mode) supports durations up to 120 minutes; each profile defines which levels remain available at that duration (`free_max_level`/`reinforced_level`).

| Level | Maximum manual duration | Maximum duration through a D1-D6 profile |
|---|---|---|
| Low / Basic / Medium / High | 5 min | 120 min (D6, Connection/Load only); 60 min for Request Tests (D5; D6 is incompatible with this family) |
| Powerful | 5 min (3 without pre-check) | 120 min with reinforced confirmation (D6, Connection/Load) or 60 min without it (D5) |
| Aggressive | 5 min (3 without pre-check) | 60 min with reinforced confirmation (D5) or 30 min without it (D4) |
| Violent | 3 min (pre-check mandatory) | 30 min with reinforced confirmation (D4) or 15 min without it (D3) |
| Maximum | 3 min (pre-check mandatory) | 5 min maximum (D1/D2 only; no D3-D6 profile offers Maximum, even with confirmation) |

The same table is available directly in the application (Help → Load Reference), generated from the same reference values (`domain/load/presets.py`, `domain/load/policies.py`) and never manually duplicated.

> In manual **Load Test** mode, ramp and plateau are automatically scaled to the selected duration (preset proportions are preserved): a one-minute test explores the entire curve from zero to peak, rather than only its beginning. In **D1-D6 profile mode**, the same guarantee is provided by each profile's native warm-up/ramp/plateau/cooldown phases; see [D1-D6 Duration Profiles](#d1-d6-duration-profiles-profile-mode).

### Navigation

- Up/down arrows: move the cursor.
- `Tab` / `Shift+Tab`: move between form fields.
- `Esc`: go back (exit confirmation from the home screen).
- `a`: show help.
- `t`: change theme.
- `q`: quit with confirmation.
- `r`: refresh the display, useful after resizing the terminal.
- `Ctrl+P`: command palette (change theme, take a screenshot, show shortcut help).

Switch themes with `t`: Omega-Stress automatically adapts colors and display richness to the detected terminal capabilities from any screen. From the command palette (`Ctrl+P` → Theme), all 31 available themes are offered (10 Omega themes plus 21 built into Textual).

### Supported terminals

Four rendering profiles, from richest to most degraded: **Complete**, **Standard**, **Reduced**, **Mono**. The selected profile is the more restrictive of the detected terminal family and the actual window size.

| Terminal | Default profile |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | Complete |
| Konsole, GNOME Terminal, Terminator, xfce4-terminal | Standard |
| urxvt, xterm | Reduced |
| Linux TTY | Mono |
| SSH (true color/256 colors detected) | Reduced |
| SSH (minimal signal) | Mono |
| Unrecognized terminal | Reduced (cautious fallback) |

Below 80 columns × 24 rows, a warning screen appears before the home screen (never blocking: the application remains usable in degraded mode). Konsole, GNOME Terminal, and Terminator are recognized through their characteristic environment variables (`KONSOLE_VERSION`, `GNOME_TERMINAL_SCREEN`/`GNOME_TERMINAL_SERVICE`, `TERMINATOR_UUID`) rather than `TERM`, which they leave at a generic compatibility value. xfce4-terminal has no known equivalent marker at present and therefore falls back to the same Standard profile only when it exposes a recognizable `TERM`/`TERM_PROGRAM` value, and to Reduced otherwise.

### Internal and system paths

By default, Omega-Stress uses its own `var/` directory, relative to the directory from which it is launched (or `$OMEGA_STRESS_VAR_DIR` if defined):

```text
var/db/app.db           # SQLite database (profiles, targets, history)
var/settings.json       # persisted settings (theme, rendering profile, default directories)
var/exports/            # default JSON/CSV/HTML exports
var/screenshots/        # default SVG screenshots (command palette)
var/audit.jsonl         # audit log (one line per run)
var/app.log             # application log
```

An absolute system path (for example `/var/exports/`) is never used by default: the leading `/` therefore matters. Only an explicit export to a directory chosen by the user (Settings or Export screen) leaves the project directory.

## D1-D6 Duration Profiles (profile mode)

An alternative to manual mode (1–5 minutes bounded by level): a **named duration profile** with a fixed total duration and four internal phases (warm-up, ramp, plateau, cooldown). It can be selected on every launch screen (toggle “Duration mode: Manual / D1-D6 Profile”) and in the CLI through `--duration-preset`.

| Profile | Total duration | Warm-up | Ramp | Plateau | Cooldown | Maximum level without confirmation | Additional level (reinforced confirmation) | Compatible families |
|---|---|---|---|---|---|---|---|---|
| D1 (quick) | 1 min | 5 s | 10 s | 40 s | 5 s | Maximum | — | Request, Connection, Load |
| D2 (short) | 5 min | 15 s | 30 s | 4 min | 15 s | Maximum | — | Request, Connection, Load |
| D3 (standard) | 15 min | 30 s | 1 min 30 | 12 min 30 | 30 s | Violent | — | Request, Connection, Load |
| D4 (resilience) | 30 min | 1 min | 3 min | 25 min | 1 min | Aggressive | Violent | Request, Connection, Load |
| D5 (extended) | 60 min | 2 min | 5 min | 51 min | 2 min | Powerful | Aggressive | Request, Connection, Load |
| D6 (soak) | 120 min | 3 min | 10 min | 104 min | 3 min | High | Powerful | Connection, Load (never Request) |

- The additional level (D4-D6) is accessible only by entering exactly the reinforced confirmation text shown on screen; a simple checkbox is never enough.
- D6 excludes Request Test: a throughput test is volume-bounded and is not meaningful for a two-hour profile focused on drift over time.
- The same table is available in the application (Help → D1-D6 Duration Profiles).

## Safety Mode

A checkbox present on every launch screen (checked by default) that controls **only** the safeguards protecting the machine running Omega-Stress (CPU/memory of the local generator):

- **Always active regardless of this setting**: thresholds protecting the **tested target** (error rate and latency). Disabling them would never make product sense; they are not covered by this checkbox.
- **Safety Mode active (default)**: a test stops automatically if the host machine itself appears under pressure (generator CPU and total machine CPU high at the same time; one alone is never sufficient).
- **Safety Mode disabled**: the local safeguard is removed. A reminder then compares the selected level with the latest known calibration for this machine (see [Local Calibration](#local-calibration)). Exceeding that envelope remains possible, but result reliability and machine stability become the user's responsibility.

Also available in the CLI through `--unsafe` (absent by default means Safety Mode is active).

## Local Calibration

Measures the actual capacity of **this machine** (never the tested target): an integrated Omega-Stress loopback server receives increasing load stages generated by the same `httpx`/asyncio engine as real tests.

- Seven stages, from idle (system background noise) up to 2000 connections / 12,000 req/s, each assessed against health thresholds (generator and global CPU, available memory, error rate, achieved throughput). The final two stages are conditional and skipped if the preceding stage is unhealthy.
- Produces a safe envelope (`VU_safe` / `RPS_safe`) from the last healthy stage, with a safety margin (approximately 30% reserve) and increasing confidence based on the depth reached.
- **Measurement only in V1**: the result is not automatically applied to cap a real test; it is an informational reference, especially when [Safety Mode](#safety-mode) is disabled.
- Persisted per machine using a non-invasive fingerprint (OS/architecture/core count/RAM, never a hardware address), and viewable at any time without repeating the measurement.

Available from the TUI **Calibration** screen (“Run calibration”, with second-by-second progress) or through the CLI:

```bash
omega-stress calibrate run     # run a new calibration
omega-stress calibrate show    # show the latest known calibration without running a new one
```

## Configuration

Everything can be configured from the TUI **Settings** screen; no configuration file needs to be edited manually:

- **Theme**: choose from the 10 Omega themes; applied immediately and persisted.
- **Rendering profile**: Automatic (detected at startup) or manually forced (Complete/Standard/Reduced/Mono).
- **Default export directory**: pre-fills the destination field on the Export screen.
- **Default screenshot directory**: used by the command-palette “Screenshot” command (`Ctrl+P`).
- **Cleanup**: recent targets (never pinned ones), all targets (including pinned targets and their authorizations), or the complete history; each action has its own confirmation.

Settings are persisted in `var/settings.json`. The `var/` root itself can be redirected through `OMEGA_STRESS_VAR_DIR`, useful for isolating multiple instances or tests.

## Testing and Quality

```bash
pytest
ruff check .
mypy src
lint-imports   # checks the Dependency Rule (see [tool.importlinter] in pyproject.toml)
```

The suite contains more than 570 tests (unit, integration, TUI, and CLI). `lint-imports` fails CI if the Dependency Rule or third-party technology isolation is violated; see [Architecture](#architecture).

## Uninstallation

Omega-Stress does not touch anything outside its own directory and one optional alias line:

```bash
rm -rf ~/omega-stress
sed -i '/alias stress=/d' ~/.bashrc ~/.zshrc
```

No system package, service, or file outside `~/omega-stress/` is created by `install.sh`; no additional uninstallation is required.

## Known Limitations

- **In-process load generation** on one machine (`httpx`/asyncio): this is not a distributed tool. Real limits (see [Test Values](#test-values)) are deliberately much lower than those of SaaS load-testing services such as loader.io. On modest hardware, Aggressive/Violent/Maximum Connection Tests may take considerably longer in real time than the selected duration to emit the full target load; the capacity of **this machine**, not the target, then limits actual throughput. Use [Local Calibration](#local-calibration) to identify reasonable values for your hardware.
- Automatic terminal-family detection relies on environment variables; xfce4-terminal currently has no known reliable marker (see [Supported Terminals](#supported-terminals)).
- `plugins/` is an architectural extension point for builtin/external plugin loading, not implemented in V1: scaffolding exists, but no plugin is shipped.
- `var/` is relative to the project directory (not XDG): intended for local single-user use, not multi-user sharing on the same machine.
- Manual **Load Test** mode has no cooldown stage after the plateau; cooldown is available only through a [D1-D6 duration profile](#d1-d6-duration-profiles-profile-mode), which includes all four phases natively.
- A validated pre-check is not bound to a specific target: it remains valid for 24 hours for any subsequent Violent/Maximum launch, not only the pre-checked target.
- [Local Calibration](#local-calibration) measures but does not yet automatically apply its safe envelope to cap a real test; this is a deliberately separate, not-yet-started work item.

## License

MIT — see `LICENSE`.
