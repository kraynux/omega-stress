# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation fichier JSON du port CalibrationRepository — un
fichier par empreinte machine, voir document produit, "Persistance et
compatibilite"."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from omega_stress.domain.calibration.models import (
    CalibrationEnvelope,
    CalibrationFingerprint,
    CalibrationResult,
    CalibrationStageResult,
)
from omega_stress.domain.calibration.service import compute_fingerprint_hash
from omega_stress.infrastructure.exceptions import StorageError


class JsonCalibrationStore:
    """Implemente ports/calibration_repository.py::CalibrationRepository.
    Meme patron que json_settings_store.py (relit/reecrit le fichier
    entier, aucune ecriture atomique — usage mono-utilisateur local,
    frequence d'ecriture triviale), mais UN fichier par empreinte plutot
    qu'un magasin cle-valeur unique."""

    def __init__(self, calibrations_dir: Path) -> None:
        self._calibrations_dir = calibrations_dir

    def save(self, result: CalibrationResult) -> None:
        path = self._path_for(compute_fingerprint_hash(result.fingerprint))
        try:
            self._calibrations_dir.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as handle:
                json.dump(_serialize_result(result), handle, indent=2, sort_keys=True)
        except OSError as exc:
            raise StorageError(f"Echec d'ecriture du calibrage vers {path} : {exc}") from exc

    def load(self, fingerprint_hash: str) -> CalibrationResult | None:
        path = self._path_for(fingerprint_hash)
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Echec de lecture du calibrage depuis {path} : {exc}") from exc
        return _deserialize_result(raw)

    def _path_for(self, fingerprint_hash: str) -> Path:
        return self._calibrations_dir / f"{fingerprint_hash}.json"


def _serialize_result(result: CalibrationResult) -> dict:
    return {
        "fingerprint": _serialize_fingerprint(result.fingerprint),
        "started_at": result.started_at.isoformat(),
        "duration_seconds": result.duration_seconds,
        "stages": [_serialize_stage_result(s) for s in result.stages],
        "envelope": _serialize_envelope(result.envelope),
        "overall_stop_reason": result.overall_stop_reason,
    }


def _serialize_fingerprint(fingerprint: CalibrationFingerprint) -> dict:
    return {
        "schema_version": fingerprint.schema_version,
        "engine_version": fingerprint.engine_version,
        "python_version": fingerprint.python_version,
        "os_name": fingerprint.os_name,
        "architecture": fingerprint.architecture,
        "logical_cpu_count": fingerprint.logical_cpu_count,
        "total_ram_mb": fingerprint.total_ram_mb,
        "open_files_soft_limit": fingerprint.open_files_soft_limit,
        "workers_mode": fingerprint.workers_mode,
        "scenario_id": fingerprint.scenario_id,
    }


def _serialize_stage_result(stage_result: CalibrationStageResult) -> dict:
    return {
        "stage_id": stage_result.stage_id,
        "vu_target": stage_result.vu_target,
        "rps_target": stage_result.rps_target,
        "rps_achieved": stage_result.rps_achieved,
        "error_rate": stage_result.error_rate,
        "peak_cpu_percent_generator": stage_result.peak_cpu_percent_generator,
        "peak_cpu_percent_global": stage_result.peak_cpu_percent_global,
        "memory_available_percent_min": stage_result.memory_available_percent_min,
        "is_healthy": stage_result.is_healthy,
        "stop_reason": stage_result.stop_reason,
    }


def _serialize_envelope(envelope: CalibrationEnvelope | None) -> dict | None:
    if envelope is None:
        return None
    return {
        "vu_safe": envelope.vu_safe,
        "rps_safe": envelope.rps_safe,
        "connections_safe": envelope.connections_safe,
        "margin_applied": envelope.margin_applied,
        "last_healthy_stage_id": envelope.last_healthy_stage_id,
        "first_degraded_stage_id": envelope.first_degraded_stage_id,
        "confidence": envelope.confidence,
    }


def _deserialize_result(raw: dict) -> CalibrationResult:
    return CalibrationResult(
        fingerprint=_deserialize_fingerprint(raw["fingerprint"]),
        started_at=datetime.fromisoformat(raw["started_at"]),
        duration_seconds=raw["duration_seconds"],
        stages=tuple(_deserialize_stage_result(s) for s in raw["stages"]),
        envelope=_deserialize_envelope(raw["envelope"]),
        overall_stop_reason=raw["overall_stop_reason"],
    )


def _deserialize_fingerprint(raw: dict) -> CalibrationFingerprint:
    return CalibrationFingerprint(
        schema_version=raw["schema_version"],
        engine_version=raw["engine_version"],
        python_version=raw["python_version"],
        os_name=raw["os_name"],
        architecture=raw["architecture"],
        logical_cpu_count=raw["logical_cpu_count"],
        total_ram_mb=raw["total_ram_mb"],
        open_files_soft_limit=raw["open_files_soft_limit"],
        workers_mode=raw["workers_mode"],
        scenario_id=raw["scenario_id"],
    )


def _deserialize_stage_result(raw: dict) -> CalibrationStageResult:
    return CalibrationStageResult(
        stage_id=raw["stage_id"],
        vu_target=raw["vu_target"],
        rps_target=raw["rps_target"],
        rps_achieved=raw["rps_achieved"],
        error_rate=raw["error_rate"],
        peak_cpu_percent_generator=raw["peak_cpu_percent_generator"],
        peak_cpu_percent_global=raw["peak_cpu_percent_global"],
        memory_available_percent_min=raw["memory_available_percent_min"],
        is_healthy=raw["is_healthy"],
        stop_reason=raw["stop_reason"],
    )


def _deserialize_envelope(raw: dict | None) -> CalibrationEnvelope | None:
    if raw is None:
        return None
    return CalibrationEnvelope(
        vu_safe=raw["vu_safe"],
        rps_safe=raw["rps_safe"],
        connections_safe=raw["connections_safe"],
        margin_applied=raw["margin_applied"],
        last_healthy_stage_id=raw["last_healthy_stage_id"],
        first_degraded_stage_id=raw["first_degraded_stage_id"],
        confidence=raw["confidence"],
    )

# <-- INFO DEV ---------------------------------------------------------
# Role :
# - Implementation concrete du port calibration_repository.py sur un
#   fichier JSON par empreinte machine.
# Pourquoi dans infrastructure/storage/files/ (charte) :
# - Meme raisonnement que json_settings_store.py : adaptateur remplacable,
#   distinct des repositories SQLite (le document produit isole
#   explicitement les calibrages dans var/calibrations/, jamais dans
#   app.db).
# Ce qu'il ne contient PAS :
# - Aucune ecriture atomique (pas de fichier temporaire + rename) : meme
#   simplification assumee que json_settings_store.py, un calibrage est
#   une operation rare et interactive, jamais concurrente sur ce projet
#   mono-utilisateur local.
# - Aucun calcul de fingerprint (voir infrastructure/calibration/
#   fingerprint.py::compute_fingerprint(), appele par l'appelant AVANT
#   de construire le CalibrationResult transmis a save()) — seul
#   compute_fingerprint_hash() est consomme ici, pour nommer le fichier.
# Points cles :
# - _serialize_*/_deserialize_* explicites (jamais dataclasses.asdict()
#   suivi d'une reconstruction directe) : meme discipline que
#   infrastructure/storage/sqlite/run_repository.py pour ses value
#   objects imbriques — un champ ajoute plus tard a un des dataclasses
#   de domain/calibration/models.py doit etre reporte ICI explicitement,
#   jamais suppose automatiquement serialise.
# - save() ECRASE tout resultat precedent pour la meme empreinte (meme
#   nom de fichier) : coherent avec ports/calibration_repository.py, un
#   seul resultat par empreinte, jamais un historique.
# - load() retourne None (jamais une erreur) si le fichier n'existe pas :
#   un poste jamais calibre est un cas normal, pas une erreur de stockage.
# Comment il sera utilise (apercu) :
# - app/dependency_container.py construit une instance avec
#   infrastructure/config/paths.py::calibrations_dir().
#---------------------------------------------------------------------->
