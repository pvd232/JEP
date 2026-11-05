"""Configure verified Codex TLS trust for each child process."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import ssl
from typing import Mapping

CA_SETTINGS = ("CODEX_CA_CERTIFICATE", "SSL_CERT_FILE")


def codex_environment(environ: Mapping[str, str] | None = None):
    """Preserve explicit trust settings; otherwise use certifi or OS defaults.

    CODEX_CA_CERTIFICATE supplies a missing SSL_CERT_FILE, and vice versa.
    Distinct explicit settings remain distinct and both must validate. No
    process-wide environment or TLS verification switch is changed.
    """
    environment = dict(os.environ if environ is None else environ)
    explicit = {name: environment[name] for name in CA_SETTINGS if name in environment}
    if any(not value.strip() for value in explicit.values()):
        raise ValueError("Explicit Codex CA settings must name a nonempty CA file")
    source = "explicit"
    if explicit:
        selected = explicit.get("CODEX_CA_CERTIFICATE", explicit.get("SSL_CERT_FILE"))
    else:
        try:
            import certifi
        except ModuleNotFoundError:
            ssl.create_default_context()
            return environment, {"tls_verification": "enabled", "trust_source": "os_default", "bundles": []}
        selected = certifi.where()
        source = "certifi"
    for name in CA_SETTINGS:
        environment.setdefault(name, selected)
    bundles = []
    checked = {}
    for name in CA_SETTINGS:
        path = Path(environment[name]).expanduser().resolve()
        if path not in checked:
            try:
                raw = path.read_bytes()
                ssl.create_default_context(cafile=str(path))
            except (OSError, ssl.SSLError) as error:
                raise ValueError(f"Invalid CA file for {name}: {path}") from error
            checked[path] = hashlib.sha256(raw).hexdigest()
        environment[name] = str(path)
        bundles.append({"setting": name, "path": str(path), "sha256": checked[path]})
    return environment, {"tls_verification": "enabled", "trust_source": source, "bundles": bundles}
