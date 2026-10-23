"""Privacidad desde el diseño: minimización, seudonimización y redacción de datos personales.

- `nombre_corto`: en pantallas operativas basta el nombre de pila y la inicial del apellido.
- `redactar`: antes de mandar texto libre de un cliente al LLM se ocultan números largos (identidad,
  tarjetas, teléfonos) y correos. El LLM nunca recibe IDs de cliente, teléfonos ni ubicaciones.
- `SinConsultaEnLogs`: los registros de acceso no guardan parámetros de consulta (pueden traer nombres).
"""

from __future__ import annotations

import logging
import re

NUMERO = re.compile(r"\d[\d\s-]{5,}\d")
CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def nombre_corto(nombre: str) -> str:
    partes = str(nombre).split()
    if len(partes) < 2:
        return partes[0] if partes else ""
    return f"{partes[0]} {partes[1][0]}."


def redactar(texto: str) -> str:
    return CORREO.sub("[correo]", NUMERO.sub("[número]", texto))


class SinConsultaEnLogs(logging.Filter):
    """Quita la consulta (?q=...) de la ruta en los registros de acceso de uvicorn."""

    def filter(self, record: logging.LogRecord) -> bool:
        args = record.args
        if isinstance(args, tuple) and len(args) >= 3 and isinstance(args[2], str) and "?" in args[2]:
            record.args = (*args[:2], args[2].split("?", 1)[0] + "?…", *args[3:])
        return True


CABECERAS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
    "Cross-Origin-Opener-Policy": "same-origin",
}
CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
    "connect-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
)
