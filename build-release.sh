#!/usr/bin/env bash
# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
# ==============================================================================
# Construit l'archive distribuable omega-stress.tar.gz : copie le projet
# (sans artefacts dev/runtime), vendore omega-lib (dependance obligatoire
# non publiee sur PyPI, voir install.sh), archive le tout dans ../dist/.
# Meme convention que omega-serv/omega-track/omega-fuzz (build-release.sh).
# Outil de maintenance, jamais lui-meme inclus dans l'archive generee.
#
# `docs/` exclu (retour utilisateur) : ne contient que le logo utilise
# par le rendu README sur GitHub (docs/assets/omega-stress.png, ~2.6 Mo) -
# jamais lu par le code, inutile a une installation reelle.
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
ok()   { echo -e "${GREEN}✅ $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OMEGA_LIB_SRC="${OMEGA_LIB_SRC:-$HOME/DEV/LIB/omega-lib}"
DIST_DIR="${DIST_DIR:-$PROJECT_ROOT/../dist}"
ARCHIVE_NAME="omega-stress.tar.gz"

if [ ! -d "$OMEGA_LIB_SRC" ]; then
    err "omega-lib introuvable : $OMEGA_LIB_SRC (definissez OMEGA_LIB_SRC si le chemin differe)."
    exit 1
fi

STAGING_DIR="$(mktemp -d)"
trap 'rm -rf "$STAGING_DIR"' EXIT
DEST="$STAGING_DIR/omega-stress"
mkdir -p "$DEST"

info "Copie du projet omega-stress..."
rsync -a \
    --exclude='.venv/' --exclude='venv/' \
    --exclude='__pycache__/' --exclude='*.pyc' \
    --exclude='.pytest_cache/' --exclude='.mypy_cache/' --exclude='.ruff_cache/' \
    --exclude='.import_linter_cache/' --exclude='*.egg-info/' \
    --exclude='.git/' --exclude='.claude/' \
    --exclude='docs/' \
    --exclude='var/db/*' --exclude='var/exports/*' --exclude='var/screenshots/*' \
    --exclude='var/calibrations/*' --exclude='var/settings.json' \
    --exclude='var/*.log' --exclude='var/*.jsonl' \
    --exclude='*~' --exclude='*.bak' --exclude='*.swp' \
    --exclude='.coverage' --exclude='htmlcov/' \
    --exclude='build-release.sh' --exclude='omega-stress.tar.gz' --exclude='dist/' \
    "$PROJECT_ROOT/" "$DEST/"

info "Vendoring d'omega-lib (dependance obligatoire, non publiee sur PyPI)..."
mkdir -p "$DEST/vendor/omega-lib"
rsync -a \
    --exclude='.venv/' --exclude='__pycache__/' --exclude='*.pyc' \
    --exclude='.pytest_cache/' --exclude='.mypy_cache/' --exclude='.ruff_cache/' \
    --exclude='*.egg-info/' --exclude='.git/' --exclude='tests/' \
    "$OMEGA_LIB_SRC/" "$DEST/vendor/omega-lib/"

info "Archivage..."
mkdir -p "$DIST_DIR"
tar -C "$STAGING_DIR" -czf "$DIST_DIR/$ARCHIVE_NAME" omega-stress

ok "Archive generee : $DIST_DIR/$ARCHIVE_NAME"
echo "sha256sum :"
sha256sum "$DIST_DIR/$ARCHIVE_NAME"
