# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Hook : notifications utilisateur ponctuelles (arret automatique, goulot d'etranglement)."""
from __future__ import annotations

from collections.abc import Callable

NotificationSink = Callable[[str], None]
"""Destination d'un message de notification, fournie par l'appelant
(typiquement interfaces/tui/widgets/notification_bar.py en production) —
local a ce module, meme principe que AuditSink dans audit_hook.py."""


def notify_auto_stop(reason: str, *, sink: NotificationSink) -> None:
    sink(f"Arret automatique : {reason}")


def notify_local_bottleneck(*, sink: NotificationSink) -> None:
    sink(
        "Le generateur local semble devenir le goulot d'etranglement "
        "(debit observe significativement inferieur au debit demande)."
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Construit des messages de notification ponctuels destines a
#   l'utilisateur, sur deux evenements du pipeline : arret automatique et
#   goulot d'etranglement local detecte.
# Pourquoi dans application/pipeline/hooks/ (charte) :
# - Point d'integration nomme du pipeline (ARCHITECTURE.md §4, etape 8),
#   sans dependance a Textual : NotificationSink reste une simple
#   fonction, jamais un import de interfaces/tui/ ici.
# Ce qu'il ne contient PAS :
# - Aucun rendu (pas de couleur, pas de style) : le sink concret
#   (interfaces/tui/widgets/notification_bar.py) decide de la
#   presentation, ce fichier ne fournit que le texte du message.
# - Aucune decision de QUAND notifier (c'est
#   application/pipeline/executor.py qui appelle ces fonctions au bon
#   moment, en reaction a abort_run() ou a
#   degraded_mode.py::is_local_bottleneck()).
# Points cles :
# - Les messages sont en francais, coherents avec le vocabulaire produit
#   normatif (plan_omega-stress_v5.md, "Positionnement terminologique").
# Comment il sera utilise (apercu) :
# - application/pipeline/executor.py appelle notify_auto_stop() apres
#   application/pipeline/abort.py::abort_run(), et notify_local_bottleneck()
#   des qu'un IntervalSample declenche
#   application/pipeline/degraded_mode.py::is_local_bottleneck().
#---------------------------------------------------------------------->
