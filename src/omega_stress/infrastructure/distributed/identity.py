# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Identite TLS du coordinateur et contextes du canal de controle (Phase 2, 2026-11-21).

Le coordinateur a un certificat auto-signe (openssl, cree une fois, cle en 0600) ; le worker
EPINGLE son empreinte SHA-256 (donnee a l'appairage) et verifie chaque connexion contre elle :
pas d'autorite de certification, pas de confiance au premier contact. Le worker, lui, se
presente par un secret propre remis a l'appairage, transmis seulement dans le canal chiffre."""

from __future__ import annotations

import hashlib
import os
import ssl
import subprocess
from pathlib import Path

CERT_NAME = "coordinateur.crt"
KEY_NAME = "coordinateur.key"


class IdentityError(RuntimeError):
    pass


def ensure_coordinator_identity(directory: Path) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    cert, key = directory / CERT_NAME, directory / KEY_NAME
    if cert.is_file() and key.is_file():
        return cert, key
    try:
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "ec",
                "-pkeyopt",
                "ec_paramgen_curve:prime256v1",
                "-nodes",
                "-days",
                "3650",
                "-subj",
                "/CN=omega-stress-coordinateur",
                "-keyout",
                str(key),
                "-out",
                str(cert),
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise IdentityError(f"openssl: {error}") from error
    os.chmod(key, 0o600)
    return cert, key


def fingerprint_of_der(der: bytes) -> str:
    return hashlib.sha256(der).hexdigest()


def fingerprint_of(cert: Path) -> str:
    return fingerprint_of_der(ssl.PEM_cert_to_DER_cert(cert.read_text(encoding="ascii")))


def server_context(cert: Path, key: Path) -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(cert, key)
    return context


def client_context() -> ssl.SSLContext:
    """Aucune verification par autorite : l'empreinte est controlee juste apres la poignee de main
    (verify_pinned), seule preuve d'identite du coordinateur."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def peer_fingerprint(ssl_object: ssl.SSLObject | ssl.SSLSocket | None) -> str:
    der = ssl_object.getpeercert(binary_form=True) if ssl_object is not None else None
    if not der:
        raise IdentityError("no certificate presented by the coordinator")
    return fingerprint_of_der(der)
