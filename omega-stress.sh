#!/usr/bin/env bash
# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
# ==============================================================================
# Script de lancement - OMEGA-STRESS TUI/CLI
# Contrairement a omega-fire.sh (nftables/fail2ban), aucun privilege
# particulier n'est requis ici : Omega-Stress ne fait que des appels HTTP
# sortants en tant qu'utilisateur normal, jamais d'operation systeme.
# ==============================================================================

set -e

# Couleurs pour le terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${WHITE}${NC}"
echo -e "${WHITE}DÉMARRAGE DE L'APPLICATION${NC}"
echo -e "${WHITE}${NC}"
echo -e "${WHITE}    ░▒▓█████████████████████████▓▒░${NC}"
echo -e "${WHITE}    ░▒▓ Ω M E G A - S T R E S S ▓▒░${NC}"
echo -e "${WHITE}    ░▒▓█████████████████████████▓▒░${NC}"
echo -e "${WHITE}${NC}"

# 1. Détection du répertoire racine du projet
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 2. Détection de l'interpréteur Python (.venv ou venv ou système)
if [ -d ".venv" ]; then
    VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
elif [ -d "venv" ]; then
    VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
else
    VENV_PYTHON="$(which python3)"
fi

if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "${RED}❌ Erreur : Aucun interpréteur Python trouvé.${NC}"
    echo -e "${YELLOW}   Lancez d'abord ./install.sh, ou créez un environnement virtuel manuellement.${NC}"
    exit 1
fi

# 3. Confirmation
echo -e "${GREEN}✔ Interpréteur détecté : ${VENV_PYTHON}${NC}\n"

# 4. Exécution du point d'entrée officiel (module omega_stress)
export PYTHONPATH="$SCRIPT_DIR/src"
exec "$VENV_PYTHON" -m omega_stress "$@"
