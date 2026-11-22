#!/usr/bin/env bash
# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
# ==============================================================================
# Script de lancement - OMEGA-STRESS TUI/CLI
# Contrairement a omega-fire.sh (nftables/fail2ban), aucun privilege
# particulier n'est requis ici : Omega-Stress ne fait que des appels HTTP
# sortants en tant qu'utilisateur normal, jamais d'operation systeme.
# ==============================================================================

set -e

# Contrats d'interconnexion (2026-11-21) : `synchro jeton` sort du JSON lu par omega-connect, sans bannière.
# Charge distribuée (2026-11-21) : `worker` et `coordinateur` aussi (le mode poussé les lance par SSH).
# Copie embarquee par omega-suite (<suite>/vendor/omega-stress) : pas de .venv a elle, omega-suite l'installe dans
# le sien ; son etat est celui de l'onglet omega-stress de la suite (<suite>/var/stress). Decision de l'auteur,
# 2026-11-22 : omega-stress fait partie d'omega-suite, s'y reconnait, s'y met a jour et sert a la charge distribuee.
suite_context() {
    local here="$1" suite
    [ "$(basename "$(dirname "$here")")" = "vendor" ] || return 1
    [ -d "$here/.venv" ] || [ -d "$here/venv" ] && return 1
    suite="$(cd "$here/../.." && pwd)"
    [ -f "$suite/omega-suite.sh" ] && [ -x "$suite/.venv/bin/python" ] || return 1
    VENV_PYTHON="$suite/.venv/bin/python"
    export OMEGA_STRESS_VAR_DIR="${OMEGA_STRESS_VAR_DIR:-${OMEGA_SUITE_VAR_DIR:-$suite/var}/stress}"
    return 0
}

if [ "${1:-}" = "synchro" ] || [ "${1:-}" = "worker" ] || [ "${1:-}" = "coordinateur" ]; then
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    if suite_context "$SCRIPT_DIR"; then
        :
    elif [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
        VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
    elif [ -x "$SCRIPT_DIR/venv/bin/python" ]; then
        VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
    else
        VENV_PYTHON="$(command -v python3)"
    fi
    export PYTHONPATH="$SCRIPT_DIR/src"
    # var/ d'omega-stress est relatif au dossier courant : toujours celui d'omega-stress (correctif
    # 2026-11-21 : lances par omega-connect ou par SSH, `worker`/`coordinateur` ecrivaient ailleurs).
    cd "$SCRIPT_DIR"
    exec "$VENV_PYTHON" -m omega_stress "$@"
fi

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
if suite_context "$SCRIPT_DIR"; then
    :
elif [ -d ".venv" ]; then
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
