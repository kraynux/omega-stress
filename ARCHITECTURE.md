# Omega-Stress — Charte d'architecture technique complète

Ce document est normatif. Toute règle qu'il contient prime sur une préférence individuelle ou une facilité ponctuelle de développement. Une dérogation doit être proposée comme modification tracée de cette charte (voir §12), jamais faite silencieusement dans le code.

## 0. Portée et généalogie

La suite `omega-` prévoit **4 outils** d'administration système en terminal au total. **`omega-fire`** (pare-feu/fail2ban/monitoring) est le premier, en v3.0, terminé. `omega-stress` est le deuxième, en cours de conception. Les deux outils suivants restent à définir. Chaque outil est développé **indépendamment**, avec sa propre interface (TUI et/ou CLI) et son propre cycle de vie — aucune fusion de code n'est prévue tant que la suite n'est pas complète. Une **interface unificatrice**, qui appellera les 4 outils, est prévue une fois l'ensemble terminé ; c'est une raison supplémentaire de garder les `ports/` et les `application/commands/`+`queries/` de chaque outil comme une surface d'appel propre et stable (pensée « library-callable »), même si rien ne l'appelle de l'extérieur en V1 — et de garder la cohérence visuelle (thèmes) et de format (exports) entre outils dès maintenant, pour que la fusion future n'ait pas à rattraper des divergences accumulées.

Cette charte a été **délibérément alignée sur l'architecture réelle et déjà éprouvée d'omega-fire** (`~/OF-DEV/omega-fire/`, charte source : `system-prompt-omega-fire-architecture-complete.md`) plutôt que reconduite depuis une version antérieure plus simple à 4 couches (`domain/application/infrastructure/presentation`) — décision prise le 2026-08-23 après constat qu'omega-fire existait déjà concrètement et suivait un patron à 9 paquets nettement plus riche, en particulier un pipeline d'exécution avec guards/hooks directement pertinent pour les exigences de sécurité propres à omega-stress (seuils d'arrêt, confirmation d'autorisation, détection de goulot d'étranglement local).

**Ce qui est repris à l'identique de la structure d'omega-fire** : les 9 paquets racine (`app/`, `application/`, `core/`, `domain/`, `infrastructure/`, `interfaces/`, `plugins/`, `ports/`, `shared/`), la Dependency Rule, le split CQRS `commands/`/`queries/`, le pipeline `executor/planner/steps/guards/hooks`, la hiérarchie d'exceptions par couche, la chaîne capacités (probe → registre → guard → projection), le principe « toute action importante passe par le pipeline ».

**Ce qui est adapté au domaine du test de charge (pas une copie aveugle)** — chaque écart est justifié et daté ici :

| Écart | Raison | Date |
|---|---|---|
| `pipeline/rollback.py` → `pipeline/abort.py`, `RollbackError` → `AbortError`, `RollbackGuard` → `ThresholdGuard` | Un run de charge déjà exécuté ne se « défait » pas comme une règle firewall appliquée à tort : l'équivalent fonctionnel est l'arrêt automatique **en cours de run** sur seuil dépassé, pas une annulation a posteriori. | 2026-08-23 |
| Pas de `infrastructure/backends/` avec plusieurs implémentations concurrentes | Décision de cadrage produit : génération de charge native unique en `httpx`/asyncio, sans moteur externe ni pluralité de backends. `infrastructure/runner/` suffit. | 2026-08-23 |
| `plugins/` présent mais **vide en V1** (aucun builtin/external) | Aucun axe d'extension identifié pour la V1 (pas de protocole alternatif, pas de format d'export tiers). Structure posée pour cohérence de suite et extensions futures, pas peuplée prématurément. | 2026-08-23 |
| `domain/reports/` ne contient pas les templates Jinja2 (contrairement à la mention `+ templates Jinja2` dans la charte source d'omega-fire) | Cohérent avec la règle déjà figée d'omega-stress : `jinja2` n'est importé que dans `infrastructure/exporters/html_exporter.py`. Les templates sont un détail de format concret, pas une règle métier. | 2026-08-23 |
| Interfaces en deux adaptateurs pleins (`interfaces/tui/` en Textual + `interfaces/cli/` scriptable), pas un seul CLI/menu Rich | omega-stress vise un TUI riche (Textual, widgets, live) *et* un mode non interactif scriptable pour cron/CI — deux adaptateurs de présentation à parité stricte, alors qu'omega-fire n'a construit que `interfaces/cli/` (menu Rich). | 2026-08-23 |

Aucune extraction en paquet partagé (`omega-shared`) n'est faite à ce stade malgré l'existence des deux outils : le point commun avéré aujourd'hui est le **catalogue de thèmes visuels** (`Projet/themes.txt`), pas le code d'architecture — les deux outils ont des modèles de thème différents (`rich.theme.Theme` chez omega-fire, `textual.theme.Theme` chez omega-stress). Une extraction reste envisageable plus tard si un troisième outil confirme un besoin de code partagé réel.

---

## 1. Contexte et objectif

Omega-Stress est une application locale TUI + CLI de test de charge HTTP encadré (débit, connexions simultanées, montée progressive), écrite en Python, structurée selon **Clean Architecture** et **Ports & Adapters**, alignée sur le gabarit de suite `omega-`.

Objectif architectural principal : garder un **cœur métier stable, testable et indépendant** des détails techniques comme `httpx`, `sqlite3`, `Textual` ou le format d'export.

Règle directrice : **les dépendances de code pointent toujours vers l'intérieur**. Aucune couche interne ne doit connaître une couche plus externe.

## 2. Arborescence du projet

```text
omega-stress/
├── pyproject.toml
├── uv.lock
├── README.md
├── ARCHITECTURE.md
├── LICENSE
├── .gitignore
├── .editorconfig
├── run.py
├── src/
│   └── omega_stress/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app/
│       │   ├── bootstrap.py
│       │   ├── dependency_container.py
│       │   └── lifecycle.py
│       ├── core/
│       │   ├── capability.py
│       │   ├── capability_registry.py
│       │   ├── constants.py
│       │   ├── enums.py
│       │   ├── exceptions.py
│       │   ├── models.py
│       │   ├── results.py
│       │   └── audit.py
│       ├── domain/
│       │   ├── errors.py
│       │   ├── targets/
│       │   │   ├── models.py
│       │   │   ├── service.py
│       │   │   ├── validation.py
│       │   │   └── exceptions.py
│       │   ├── profiles/
│       │   │   ├── models.py
│       │   │   ├── service.py
│       │   │   ├── validation.py
│       │   │   └── exceptions.py
│       │   ├── load/
│       │   │   ├── models.py
│       │   │   ├── policies.py
│       │   │   ├── presets.py
│       │   │   ├── builders.py
│       │   │   ├── validators.py
│       │   │   └── exceptions.py
│       │   ├── runs/
│       │   │   ├── models.py
│       │   │   ├── service.py
│       │   │   ├── validators.py
│       │   │   └── exceptions.py
│       │   ├── reports/
│       │   │   ├── models.py
│       │   │   ├── service.py
│       │   │   └── builders.py
│       │   ├── terminal/
│       │   │   ├── models.py
│       │   │   ├── policies.py
│       │   │   ├── service.py
│       │   │   └── exceptions.py
│       │   └── theme/
│       │       ├── models.py
│       │       ├── policies.py
│       │       └── service.py
│       ├── application/
│       │   ├── exceptions.py
│       │   ├── commands/
│       │   │   ├── create_profile.py
│       │   │   ├── freeze_profile.py
│       │   │   ├── pin_target.py
│       │   │   ├── unpin_target.py
│       │   │   ├── run_precheck.py
│       │   │   ├── run_request_load.py
│       │   │   ├── run_connection_load.py
│       │   │   ├── run_ramp_load.py
│       │   │   ├── replay_run.py
│       │   │   ├── export_run_report.py
│       │   │   ├── select_theme.py
│       │   │   └── select_render_profile.py
│       │   ├── queries/
│       │   │   ├── list_profiles.py
│       │   │   ├── list_targets.py
│       │   │   ├── list_history.py
│       │   │   ├── get_run_details.py
│       │   │   └── detect_terminal.py
│       │   ├── dto/
│       │   │   ├── profile_dto.py
│       │   │   ├── run_dto.py
│       │   │   ├── export_dto.py
│       │   │   ├── target_dto.py
│       │   │   ├── terminal_dto.py
│       │   │   └── mappers.py
│       │   ├── pipeline/
│       │   │   ├── executor.py
│       │   │   ├── planner.py
│       │   │   ├── steps.py
│       │   │   ├── abort.py
│       │   │   ├── degraded_mode.py
│       │   │   ├── guards/
│       │   │   │   ├── authorization_guard.py
│       │   │   │   ├── precheck_guard.py
│       │   │   │   ├── threshold_guard.py
│       │   │   │   └── capability_guard.py
│       │   │   └── hooks/
│       │   │       ├── audit_hook.py
│       │   │       ├── metrics_hook.py
│       │   │       └── notification_hook.py
│       │   └── services/
│       │       ├── run_replayer.py
│       │       ├── history_query_service.py
│       │       └── theme_selection_service.py
│       ├── ports/
│       │   ├── load_runner.py
│       │   ├── profile_repository.py
│       │   ├── target_repository.py
│       │   ├── run_repository.py
│       │   ├── export_repository.py
│       │   ├── report_exporter.py
│       │   ├── terminal_detector.py
│       │   ├── system_probe.py
│       │   ├── settings_store.py
│       │   └── run_progress_notifier.py
│       ├── infrastructure/
│       │   ├── exceptions.py
│       │   ├── config/
│       │   │   ├── settings.py
│       │   │   ├── loader.py
│       │   │   ├── env.py
│       │   │   ├── paths.py
│       │   │   └── defaults.py
│       │   ├── storage/
│       │   │   ├── sqlite/
│       │   │   │   ├── connection.py
│       │   │   │   ├── schema.py
│       │   │   │   ├── migrations.py
│       │   │   │   ├── profile_repository.py
│       │   │   │   ├── target_repository.py
│       │   │   │   ├── run_repository.py
│       │   │   │   └── export_repository.py
│       │   │   └── files/
│       │   │       └── json_settings_store.py
│       │   ├── runner/
│       │   │   ├── httpx_load_generator.py
│       │   │   ├── async_worker.py
│       │   │   ├── result_parser.py
│       │   │   └── engine_params.py
│       │   ├── terminal/
│       │   │   ├── raw_capabilities.py
│       │   │   ├── detector.py
│       │   │   └── fallback_resolver.py
│       │   ├── probe/
│       │   │   ├── local_probe.py
│       │   │   ├── limits_reader.py
│       │   │   └── env_reader.py
│       │   ├── exporters/
│       │   │   ├── json_exporter.py
│       │   │   ├── csv_exporter.py
│       │   │   ├── html_exporter.py
│       │   │   ├── html_theme_resolver.py
│       │   │   └── templates/
│       │   │       └── report.html.jinja
│       │   └── logging/
│       │       ├── app_logger.py
│       │       ├── audit_logger.py
│       │       └── config.py
│       ├── interfaces/
│       │   ├── exceptions.py
│       │   ├── tui/
│       │   │   ├── app.py
│       │   │   ├── controllers/
│       │   │   │   ├── startup_controller.py
│       │   │   │   ├── profile_controller.py
│       │   │   │   ├── load_controller.py
│       │   │   │   ├── history_controller.py
│       │   │   │   ├── theme_controller.py
│       │   │   │   └── render_profile_controller.py
│       │   │   ├── screens/
│       │   │   │   ├── splash.py
│       │   │   │   ├── home.py
│       │   │   │   ├── profiles.py
│       │   │   │   ├── profile_wizard.py
│       │   │   │   ├── request_panel.py
│       │   │   │   ├── connection_panel.py
│       │   │   │   ├── ramp_panel.py
│       │   │   │   ├── history.py
│       │   │   │   ├── run_details.py
│       │   │   │   ├── export_dialog.py
│       │   │   │   ├── settings_screen.py
│       │   │   │   └── terminal_warning.py
│       │   │   ├── widgets/
│       │   │   │   ├── stat_card.py
│       │   │   │   ├── progress_panel.py
│       │   │   │   ├── history_table.py
│       │   │   │   ├── profile_list.py
│       │   │   │   ├── target_picker.py
│       │   │   │   ├── authorization_checkbox.py
│       │   │   │   ├── theme_badge.py
│       │   │   │   ├── render_profile_badge.py
│       │   │   │   └── notification_bar.py
│       │   │   ├── presenters/
│       │   │   │   ├── profile_presenter.py
│       │   │   │   ├── run_presenter.py
│       │   │   │   ├── history_presenter.py
│       │   │   │   └── theme_presenter.py
│       │   │   ├── rendering/
│       │   │   │   ├── render_profile_resolver.py
│       │   │   │   ├── stylesheet_loader.py
│       │   │   │   └── textual_theme_builder.py
│       │   │   └── styles/
│       │   │       ├── base.tcss
│       │   │       ├── complete.tcss
│       │   │       ├── standard.tcss
│       │   │       ├── reduced.tcss
│       │   │       └── mono.tcss
│       │   └── cli/
│       │       ├── main.py
│       │       ├── commands/
│       │       │   ├── run_command.py
│       │       │   ├── profile_command.py
│       │       │   ├── history_command.py
│       │       │   └── export_command.py
│       │       └── formatters/
│       │           └── text_formatter.py
│       ├── plugins/
│       │   ├── loader.py
│       │   ├── manager.py
│       │   ├── exceptions.py
│       │   ├── builtin/        # vide en V1
│       │   └── external/       # réservé aux plugins tiers, vide en V1
│       └── shared/
│           ├── clock.py
│           ├── ids.py
│           └── typing.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
├── docs/
│   ├── product-spec.md
│   ├── user-flow.md
│   ├── terminal-compatibility.md
│   ├── theme-policy.md
│   ├── report-format.md
│   ├── profile-model.md
│   ├── storage-model.md
│   └── decisions/
└── var/
    ├── db/app.db
    ├── settings.json
    └── exports/
```

Chaque sous-paquet contient son propre `__init__.py` (omis ci-dessus pour la lisibilité) — paquets réguliers, pas de namespace packages implicites.

### Détails de `src/omega_stress/`

#### `app/`
Rôle : assembler et démarrer l'application, injection de dépendances, cycle de vie. **Jamais de logique métier.**
- `bootstrap.py` — point d'assemblage (câble ports ↔ adaptateurs concrets).
- `dependency_container.py` — conteneur DI explicite et simple (pas de framework DI tiers — cohérent avec la préférence de légèreté du projet, mais le câblage manuel lui-même est une fonction assumée de cette couche, comme chez omega-fire).
- `lifecycle.py` — ouverture/fermeture de la connexion SQLite, flush des settings, hooks de démarrage/arrêt.

#### `core/`
Rôle : définir le langage transverse du système. **Pas d'appels système, pas de SQL, pas de rendu.**
- `capability.py` / `capability_registry.py` — modèle générique de capacité (`AVAILABLE`/`DEGRADED`/`MISSING`/`DISQUALIFIED`) réutilisé pour **deux** familles distinctes : capacité du terminal (couleur, taille, emoji) et capacité système locale (CPU/RAM/fd libres pour tenir la charge demandée). Un seul registre consolidé, deux sources de sondage (voir §4).
- `enums.py` — `TestFamily` (REQUEST/CONNECTION/RAMP), `IntensityLevel` (BAS/MOYEN/HAUT/MAXIMUM), `RenderProfile` (COMPLETE/STANDARD/REDUCED/MONO), `RunVerdict` (SUCCESS/DEGRADED/AUTO_STOPPED/FAILED), `CapabilityStatus`.
- `constants.py` — constantes réellement transverses et non métier (nom d'app, version, nom de dossier d'export par défaut). **Les tables de bornage métier (intensité/durée/seuils) restent en `domain/load/policies.py`, jamais ici.**
- `exceptions.py` — `OmegaStressError` (racine absolue), `CapabilityRegistryError`, `ConfigurationError`.
- `models.py` — value objects transverses (dataclass `Capability`).
- `results.py` — `Result[T, E]` générique (`Ok`/`Err`), utilisé par toutes les couches internes.
- `audit.py` — forme générique d'un événement d'audit (horodatage, action, confirmation d'autorisation, issue), consommée par `application/pipeline/hooks/audit_hook.py` et sérialisée par `infrastructure/logging/audit_logger.py`.

#### `domain/` (par sous-domaine)
Rôle : porter la logique métier pure. **Jamais de commandes shell, pas de Textual/Rich, pas de SQL brut, pas de httpx.**
- `errors.py` — `DomainError` (racine) et les sous-types transverses à plusieurs sous-domaines : `ValidationError`, `ThresholdExceededError`, `UnauthorizedTargetError`, `PrecheckRequiredError`, `IncompatibleTerminalError` (détail en §5.2). Chaque sous-domaine peut ajouter ses propres exceptions spécifiques dans son `exceptions.py`, héritées de `DomainError`.
- `targets/` — `Target`, `PinnedTarget`, `TargetAddress` (value object) ; règles d'épinglage et de validation d'adresse.
- `profiles/` — `Profile`, étapes de profil ; règles de création, gel (freeze), duplication.
- `load/` — `LoadPlan`, `RampStep` ; **`policies.py`** (paliers d'intensité, durées autorisées, seuils d'arrêt, règles de gating du pré-check — l'ex-`load_presets.py`) ; **`presets.py`** (valeurs concrètes des 4 niveaux × 3 familles de test) ; `builders.py` (construction de rampe) ; `validators.py` (validation de plan, évaluation de seuil).
- `runs/` — `LoadRun`, `LoadResult`, événements de run ; règles de transition d'état d'un run (pas l'exécution elle-même, qui vit dans `application/pipeline/`).
- `reports/` — `ExportJob` ; construction du **contenu logique** d'un rapport (résumé, paliers, verdict, diagnostic) — pas de format concret, pas de Jinja2 (voir §0, tableau des écarts).
- `terminal/` — `TerminalProfile` ; **`policies.py`** (matrice famille de terminal → profil de rendu, paliers de taille — l'ex-`terminal_presets.py`) ; `service.py` (`terminal_policy_service`).
- `theme/` — `ThemePolicy` ; **`policies.py`** (catalogue des 10 thèmes TUI + 5 thèmes export, règle de dégradation par luminance — l'ex-`theme_presets.py`, contenu figé dans `Projet/themes.txt`) ; `service.py` (`theme_compatibility_service`).

**Règle de placement des politiques :** toute table qui encode une règle métier de sécurité ou de produit (paliers d'intensité, durées, seuils, matrice terminal, catalogue de thèmes, fréquence d'échantillonnage) vit dans le `policies.py` du sous-domaine concerné — jamais dans `infrastructure/`, jamais dans `interfaces/`, jamais dans un `domain/policies/` générique unique (contrairement à une version antérieure de cette charte : le placement par sous-domaine, comme chez omega-fire, remplace le dossier plat `domain/policies/`).

#### `application/`
Rôle : orchestrer les cas d'usage, valider les requêtes, gérer le mode dégradé, les guards et les hooks. **Jamais de rendu, jamais d'I/O directe (toujours via un port).**
- `commands/` — une action qui change un état (`create_profile`, `run_request_load`, `export_run_report`…).
- `queries/` — une lecture sans effet de bord (`list_profiles`, `list_history`, `get_run_details`, `detect_terminal`…).
- `dto/` — objets de transfert vers `interfaces/`, jamais d'entités de domaine exposées telles quelles. `mappers.py` fait la conversion entité ↔ DTO.
- `pipeline/` — voir §4. Toute action risquée (lancer un test de charge) passe par ici.
- `services/` — orchestration transversale à plusieurs commands/queries (`run_replayer`, `history_query_service`, `theme_selection_service`).
- `exceptions.py` — `ApplicationError`, `UseCaseExecutionError`, `CapabilityUnavailableError`, `PermissionDeniedError`, `PartialExecutionError`, `AbortError` (voir §0), `RunnerFailureError` (voir §5.2 pour la justification de son placement ici plutôt que dans `infrastructure/`).

#### `ports/`
Rôle : définir les contrats attendus par le cœur applicatif. **Pas d'implémentation concrète, pas de dépendance à un outil précis.**
`load_runner`, `profile_repository`, `target_repository`, `run_repository`, `export_repository`, `report_exporter`, `terminal_detector`, `system_probe`, `settings_store`, `run_progress_notifier`. Un port est défini par le besoin de l'application, jamais par la capacité d'une techno existante (ne pas concevoir un port qui ressemble à l'API SQLite ou à l'API httpx).

#### `infrastructure/`
Rôle : implémenter la technique réelle. **Tous les appels système, fichiers, SQLite, réseau passent ici.**
- `config/` — `settings.py`, `loader.py`, `env.py`, `paths.py`, `defaults.py`.
- `storage/sqlite/` — seul endroit où `sqlite3` est importé. `storage/files/` — `json_settings_store.py`.
- `runner/` — seul endroit où `httpx` est importé (`httpx_load_generator.py`). Le runner s'exécute comme tâche asynchrone **in-process** (pas de processus séparé en V1), piloté par `async_worker.py`, publiant sa progression via `application/ports/run_progress_notifier.py` implémenté ici.
- `terminal/` — signaux bruts (variables d'environnement, taille détectée) ; ne décide jamais du profil de rendu, cette décision appartient à `domain/terminal/service.py`.
- `probe/` — sondage système local (CPU/RAM/fd) pour `core/capability_registry.py`.
- `exporters/` — sérialisation concrète JSON/CSV/HTML. `html_exporter.py` est seul point du projet où `jinja2` est importé ; `html_theme_resolver.py` fait un lookup pur dans `domain/theme/policies.py`, aucun import Jinja2.
- `logging/` — journal applicatif technique et journal d'audit structuré (consommé par `pipeline/hooks/audit_hook.py`).
- `exceptions.py` — `InfrastructureError`, `StorageError`, `ParseError`, `AdapterConfigurationError` (`RunnerFailureError` vit dans `application/exceptions.py`, voir §5.2).

#### `interfaces/`
Rôle : gérer l'interaction utilisateur. **Jamais de décision métier, pas de SQL, pas de logique backend.** Deux adaptateurs à parité stricte, tous deux consommateurs des mêmes `application/commands/` et `application/queries/` — aucune règle métier ne doit exister dans l'un sans exister, de la même façon, dans l'autre.
- `tui/` — Textual. `textual` n'est importé que sous `interfaces/tui/`, jamais dans `interfaces/cli/`. `rendering/textual_theme_builder.py` construit les objets `textual.theme.Theme` à partir de `domain/theme/policies.py` — seul endroit, avec le reste de `tui/`, où thème et API Textual sont combinés.
- `cli/` — scriptable, sans Textual. Une commande CLI appelle un `command`/`query` existant, jamais une logique réécrite pour l'occasion. `cli/formatters/text_formatter.py` joue le rôle des `presenters` du TUI pour une sortie texte/JSON.
- `exceptions.py` — `InterfaceError`, `UserInputError`, `RenderError`.

#### `plugins/`
Rôle : étendre le système dynamiquement sans modifier le cœur. **V1 : structure posée, aucun plugin builtin ni external.** `loader.py`/`manager.py` existent pour cohérence de suite mais ne découvrent rien tant qu'aucun axe d'extension n'est confirmé (voir §0).
- `exceptions.py` — `PluginError`, `PluginLoadError`, `PluginActivationError`.

#### `shared/`
Rôle : utilitaires transverses non métier. **Jamais de fourre-tout métier, jamais de logique de pipeline ou d'UI.**
`clock.py`, `ids.py`, `typing.py`. (`result.py` a migré vers `core/results.py` pour suivre le placement omega-fire — un `Result` est un concept de langage transverse, pas un simple utilitaire.)

---

## 3. Règles de dépendance strictes

- `domain/` ne dépend d'aucune autre couche.
- `application/` peut dépendre de `domain/`, `core/` et `ports/`, **jamais d'un adaptateur concret d'infrastructure**.
- `infrastructure/` implémente les contrats de `ports/` et peut utiliser `domain/`/`core/` si nécessaire.
- `interfaces/` appelle `application/` (commands/queries) et affiche le résultat, **sans logique métier**.
- `shared/` ne contient jamais de logique métier déguisée.
- `plugins/` n'impose jamais sa logique au domaine.
- `app/` assemble et ne décide rien du métier.
- Pas d'import `textual`/`textual_image` en dehors de `interfaces/tui/`. Pas d'import `sqlite3`/`httpx`/`jinja2` en dehors de `infrastructure/` (fichiers uniques désignés en §2).

**Violation = défaut d'architecture bloquant, pas un détail de style.**

## 4. Chaînes fonctionnelles obligatoires

### Capacités
1. Détection technique : `infrastructure/terminal/raw_capabilities.py` (capacité terminal) et `infrastructure/probe/` (capacité système locale).
2. Consolidation : `core/capability_registry.py`.
3. Autorisation : `application/pipeline/guards/capability_guard.py` (refuse Haut/Maximum si le système local ne peut pas tenir la charge ; refuse un rendu incompatible sans fallback).
4. Projection visuelle : `interfaces/tui/rendering/render_profile_resolver.py`, `interfaces/tui/widgets/render_profile_badge.py`.

Une capacité `MISSING` ou `DISQUALIFIED` n'est **jamais** traitée comme disponible.

### Exécution métier (lancement d'un run)
Toute action importante (lancer un test requêtes/connexions/charge, relancer un run, exporter) **doit passer par** `application/pipeline/`.

Le pipeline gère, dans l'ordre :
1. `guards/authorization_guard.py` — cible confirmée ou déjà épinglée-autorisée, sinon refus immédiat (`UnauthorizedTargetError`).
2. `guards/precheck_guard.py` — pré-check obligatoire et validé pour Haut/Maximum, sinon refus (`PrecheckRequiredError`).
3. `guards/capability_guard.py` — capacité système suffisante (voir chaîne Capacités ci-dessus).
4. `planner.py` — construit le plan d'exécution (paliers, rampe) à partir de `domain/load/builders.py`.
5. `executor.py` — exécute via le port `load_runner`, publie la progression (1 point/s, constante dans `domain/load/policies.py`) via `run_progress_notifier`.
6. `guards/threshold_guard.py`, évalué en continu pendant `executor.py` — dépassement de seuil ⇒ `pipeline/abort.py` déclenche l'arrêt automatique du run (pas un rollback : le run s'arrête, il ne s'annule pas rétroactivement — voir §0).
7. `degraded_mode.py` — signale si le générateur local devient lui-même le goulot d'étranglement (débit demandé vs réel, voir Export détaillé du plan produit).
8. `hooks/audit_hook.py`, `hooks/metrics_hook.py`, `hooks/notification_hook.py` — après exécution (ou en cours pour les métriques).

**Aucun appel réseau direct ne doit contourner `load_runner` (port).**

### Exports
1. `domain/reports/` construit le contenu logique (résumé, paliers, verdict, diagnostic).
2. `infrastructure/exporters/` écrit le format concret (JSON, CSV, HTML).
3. `interfaces/` propose le format et le chemin à l'utilisateur.

### Persistance
- Les fichiers runtime (base SQLite, settings, exports) restent dans `var/`.
- Les migrations SQLite sont versionnées (`infrastructure/storage/sqlite/migrations.py`).
- Les chemins de runtime ne sont jamais codés en dur dans le métier (`infrastructure/config/paths.py` est la seule source).

## 5. Gestion des exceptions inter-couches

### 5.1 Deux catégories d'échecs, deux traitements différents
- **Échec métier attendu** (seuil dépassé, cible non autorisée, plan invalide, pré-check manquant) : valeur de retour typée via `core/results.py` (`Result[T, DomainError]`), pas une exception Python. Tout command/query qui peut échouer pour une raison métier prévisible retourne un `Result`.
- **Échec technique inattendu** (bug, ressource indisponible) : exception Python classique, traduite à chaque frontière de couche (voir §5.3), jusqu'au filet de sécurité en présentation (§5.4).

### 5.2 Hiérarchie d'exceptions

| Couche | Racine | Sous-types |
|---|---|---|
| `core/exceptions.py` | `OmegaStressError` | `CapabilityRegistryError`, `ConfigurationError` |
| `domain/errors.py` | `DomainError` | `ValidationError`, `ThresholdExceededError`, `UnauthorizedTargetError`, `PrecheckRequiredError`, `IncompatibleTerminalError` (+ exceptions spécifiques par sous-domaine) |
| `application/exceptions.py` | `ApplicationError` | `UseCaseExecutionError`, `CapabilityUnavailableError`, `PermissionDeniedError`, `PartialExecutionError`, `AbortError`, `RunnerFailureError` |
| `infrastructure/exceptions.py` | `InfrastructureError` | `StorageError`, `ParseError`, `AdapterConfigurationError` |
| `interfaces/exceptions.py` | `InterfaceError` | `UserInputError`, `RenderError` |
| `plugins/exceptions.py` | `PluginError` | `PluginLoadError`, `PluginActivationError` |

Les types `DomainError` sont sérialisables (pas d'objet d'infrastructure attaché) : le verdict d'un run (« dégradation », « échec », « arrêt automatique ») est construit à partir de ces types, pas d'un message d'exception libre.

`RunnerFailureError` vit dans `application/exceptions.py` et non `infrastructure/exceptions.py` malgré son nom : c'est le seul type technique qu'`application/pipeline/executor.py` doit connaître par son nom pour produire un verdict `FAILED` (voir §5.3), et la Dependency Rule interdit à `application/` d'importer `infrastructure/` — le placer dans `infrastructure/` créerait mécaniquement la violation qu'`import-linter` a effectivement détectée en pratique lors de la construction du pipeline (2026-08-24). Les trois autres types d'`infrastructure/exceptions.py` ne sont jamais catchés nommément par `application/` : ils remontent tels quels jusqu'au filet de sécurité de présentation (§5.4).

### 5.3 Frontière infrastructure : traduction obligatoire
Aucune exception spécifique à une techno ne franchit la frontière d'un port sans traduction — `sqlite3.Error` → `StorageError` ; `httpx.ConnectError`/timeout → `ThresholdExceededError` (si c'est un critère d'arrêt) ou `RunnerFailureError` (sinon). Cette traduction est la responsabilité de l'adaptateur : un command/query ne contient jamais de `except sqlite3...`/`except httpx...`.

### 5.4 Filet de sécurité en présentation
`interfaces/` ne traite que des `DomainError`/`ApplicationError` déjà traduites, jamais une exception technique brute. Point d'arrêt unique dans `interfaces/tui/app.py` (et son équivalent `interfaces/cli/main.py`) : toute exception non prévue y est interceptée, journalisée, affichée comme erreur générique — jamais de trace Python brute à l'écran. Ce filet ne doit jamais devenir un moyen déguisé de gérer un échec métier prévisible : s'il se déclenche souvent pour un même cas, ce cas doit être requalifié en `DomainError` explicite.

## 6. Convention de nommage du code

Vocabulaire produit = « test » (Test requêtes, Test connexions, Test charge, Pré-check, Profil, Run, Historique, Export) — celui de l'UI, de la documentation, des DTO et logs utilisateur.

Vocabulaire code = `load`/`ramp`, **jamais `test_*` ni `*_test.py` hors de `tests/`** (motifs de découverte pytest par défaut, risque de collecte accidentelle).

| Concept produit | Racine technique | Exemple |
|---|---|---|
| Test de charge en général | `load` | `domain/load/models.py`, `ports/load_runner.py` |
| Test charge (montée progressive) | `ramp` | `application/commands/run_ramp_load.py`, `interfaces/tui/screens/ramp_panel.py` |
| Test requêtes | `request` + `load` | `run_request_load.py`, `request_panel.py` |
| Test connexions | `connection` + `load` | `run_connection_load.py`, `connection_panel.py` |
| Pré-check | `precheck` (jamais `scan`) | `run_precheck.py` |

Aucun fichier ne contient le mot `scan`. Un port et son adaptateur peuvent partager le même nom de fichier dans des dossiers différents (`ports/profile_repository.py` / `infrastructure/storage/sqlite/profile_repository.py`) — seul cas de duplication de nom toléré ; la classe concrète est préfixée par sa techno (`SqliteProfileRepository`, pas `ProfileRepository`).

## 7. Règle d'autorisation de cible

Aucun run ne démarre sans confirmation explicite d'autorisation sur la cible (`interfaces/tui/widgets/authorization_checkbox.py`), sauf cible déjà épinglée avec autorisation déjà confirmée. Vérifiée côté `application/pipeline/guards/authorization_guard.py`, pas seulement côté UI : l'UI peut désactiver le bouton de lancement, le guard refuse quand même un plan non confirmé, indépendamment de l'écran ou de la commande CLI appelante.

## 8. Système de thèmes et de rendu — catalogue partagé de la suite

Catalogue figé, **identique** entre omega-stress et omega-fire (source d'autorité : `Projet/themes.txt`, extrait du code réel d'omega-fire) : 10 thèmes TUI, 5 thèmes export HTML. Vit dans `domain/theme/policies.py`.

**Deux décisions indépendantes, jamais mélangées dans un même fichier :**
- **Thème (couleur)** — choix manuel parmi 10, touche `t`. `domain/theme/policies.py` → `application/commands/select_theme.py` → `interfaces/tui/controllers/theme_controller.py` → `interfaces/tui/presenters/theme_presenter.py` → `interfaces/tui/widgets/theme_badge.py`.
- **Profil de rendu (structure)** — `complete`/`standard`/`reduced`/`mono`, décidé automatiquement depuis la capacité terminal détectée (§4, chaîne Capacités). `domain/terminal/policies.py` → `application/commands/select_render_profile.py` → `interfaces/tui/controllers/render_profile_controller.py` → `interfaces/tui/rendering/render_profile_resolver.py`.

Piège de nommage à connaître : le thème `omega-mono` (palette, choix manuel) ≠ le profil de rendu `mono` (dégradation automatique). Chacun des 10 thèmes doit rester dégradable en `reduced`/`mono` via la règle générique de conversion par luminance de `domain/theme/policies.py` (détail complet dans `Projet/themes.txt`), pas via 20 palettes maintenues à la main.

Thème d'export HTML : champ indépendant du panneau « Sortie », `omega-base` par défaut, pas de correspondance automatique thème TUI → thème export.

## 9. Règles de test

- Tout objet de `domain/` et `core/` est testable sans mock, avec des objets Python standard uniquement.
- Tout command/query de `application/` est testable en injectant de faux ports (fakes/stubs), sans SQLite réel, sans Textual, sans réseau.
- Un test d'infrastructure (ex. `SqliteProfileRepository`) teste l'implémentation du port, pas une logique métier qu'il ne doit pas contenir.
- Le pipeline (`application/pipeline/`) est testable guard par guard, avec des fakes de capacité/seuil, sans exécuter de vraie charge réseau.
- Un test e2e TUI est le seul niveau où `interfaces/tui/` est exercée de bout en bout ; un test e2e CLI, le seul niveau pour `interfaces/cli/`.
- `pyproject.toml` restreint la découverte pytest à `testpaths = ["tests"]`.

## 10. Anti-patterns interdits

- Importer `textual`/`textual_image` hors de `interfaces/tui/`, ou `sqlite3`/`httpx`/`jinja2` hors des fichiers uniques désignés en §2/§10.
- Mettre une table de seuils/presets dans `infrastructure/` ou `interfaces/` plutôt que dans le `policies.py` du sous-domaine concerné.
- Laisser un écran (`interfaces/tui/screens/`) calculer une rampe, valider un seuil, ou décider si un pré-check est obligatoire.
- Écrire dans une commande CLI une règle qui n'existe pas déjà, à l'identique, dans un command/query appelé aussi par le TUI.
- Lancer un run (ou toute action risquée) sans passer par `application/pipeline/`.
- Faire dépendre un command/query d'une classe concrète d'infrastructure plutôt que d'un port.
- Nommer un fichier `test_*.py`/`*_scan*.py` hors de `tests/`.
- Dupliquer une table de bornage entre `domain/<sous-domaine>/policies.py` et un autre endroit du code.
- Peupler `plugins/builtin`/`plugins/external` sans axe d'extension confirmé (voir §0).

## 11. Vérification continue

- `ruff` + `mypy` en CI sur chaque commit, aucune exception silencieuse.
- Un contrôle d'imports entre couches (`import-linter` ou règle `ruff` équivalente) fait échouer la CI si `domain`/`core` importent une couche externe, ou si `application` importe `infrastructure`/`interfaces`.
- Toute PR ajoutant un fichier dans `infrastructure/` avec une valeur numérique de seuil/durée/intensité est refusée en revue et redirigée vers le `policies.py` du sous-domaine concerné.

## 12. Évolution de cette charte

Cette charte peut être modifiée, jamais contournée silencieusement. Toute dérogation proposée doit : (1) être documentée ici ou dans `docs/decisions/` avec sa justification, (2) indiquer explicitement quelle règle elle assouplit, (3) être datée. En l'absence d'une telle modification tracée, le code prime la charte n'existe pas — c'est la charte qui prime le code.
