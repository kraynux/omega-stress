# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Regles metier du sous-domaine targets : epinglage et confirmation d'autorisation."""
from __future__ import annotations

from datetime import datetime

from omega_stress.core.results import Err, Ok, Result
from omega_stress.domain.errors import UnauthorizedTargetError
from omega_stress.domain.targets.models import PinnedTarget, Target


def pin(
    target: Target, *, authorization_confirmed: bool, now: datetime
) -> Result[PinnedTarget, UnauthorizedTargetError]:
    """Epingle une cible — ne peut reussir sans confirmation d'autorisation
    explicite (ARCHITECTURE.md §7). L'epinglage EST la confirmation
    persistee : une fois epinglee, les runs suivants sur cette cible
    n'exigent plus de recocher la case (voir ARCHITECTURE.md §7 et le
    Panneau de tests du plan produit)."""
    if not authorization_confirmed:
        return Err(
            UnauthorizedTargetError(
                f"Impossible d'epingler {target.address.base_url} sans confirmation "
                f"d'autorisation."
            )
        )
    return Ok(PinnedTarget(target=target, pinned_at=now, authorized_at=now))

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Porte l'unique regle metier non triviale du sous-domaine targets :
#   l'epinglage exige une confirmation d'autorisation explicite.
# Pourquoi dans domain/targets/ (charte) :
# - Regle de securite au sens de ARCHITECTURE.md §7, verifiee cote domaine
#   et non seulement cote UI.
# Ce qu'il ne contient PAS :
# - Aucune fonction unpin() : desepingler n'a pas de regle metier propre
#   (une simple suppression cote repository), donc pas de logique a
#   encapsuler ici — application/commands/unpin_target.py appelle
#   directement le port target_repository, sans passer par ce service.
# - Aucune persistance : retourne un PinnedTarget en memoire, la sauvegarde
#   est le role d'infrastructure/storage/sqlite/target_repository.py via
#   le port ports/target_repository.py.
# Points cles :
# - now est toujours un parametre explicite (pas de datetime.now() cache) :
#   testable sans mock, coherent avec Target/PinnedTarget
#   (domain/targets/models.py).
# - authorized_at == pinned_at dans ce chemin : l'epinglage et la
#   confirmation ont lieu dans le meme geste utilisateur en V1.
# Comment il sera utilise (apercu) :
# - application/commands/pin_target.py appelle pin() avec la valeur de la
#   case a cocher confirmee par l'utilisateur, puis persiste le resultat
#   via le port target_repository.
#---------------------------------------------------------------------->
