"""Bitácora de mensajes (auditoría): cada mensaje generado queda registrado.

Guarda: fecha y hora, cliente, acción, fuente (plantilla / IA), versión del prompt, resultado de los
guardrails y el texto enviado. Es solo de anexar (append-only) en la base SQLite del proyecto.
Retención: los registros de más de `RETENCION_DIAS` se borran al arrancar (minimización de datos).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

from ml.comun import DB_PATH

RETENCION_DIAS = 90

_SQL = """CREATE TABLE IF NOT EXISTS bitacora_mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, fecha_hora TEXT, cliente_id TEXT, accion TEXT,
    fuente TEXT, version_prompt TEXT, guardrails TEXT, caracteres INTEGER, texto TEXT)"""


def registrar(cliente_id: str, accion: str, msg: dict) -> None:
    try:
        with sqlite3.connect(DB_PATH) as con:
            con.execute(_SQL)
            con.execute(
                "INSERT INTO bitacora_mensajes (fecha_hora, cliente_id, accion, fuente, version_prompt, guardrails,"
                " caracteres, texto) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    datetime.now().isoformat(timespec="seconds"),
                    cliente_id,
                    accion,
                    msg["fuente"],
                    msg.get("version_prompt", ""),
                    msg["guardrails"],
                    len(msg["texto"]),
                    msg["texto"],
                ),
            )
    except sqlite3.Error:
        pass  # la bitácora nunca debe tumbar la demo


def purgar(dias: int = RETENCION_DIAS) -> int:
    """Borra los registros más antiguos que `dias`. Devuelve cuántos borró."""
    limite = (datetime.now() - timedelta(days=dias)).isoformat(timespec="seconds")
    try:
        with sqlite3.connect(DB_PATH) as con:
            con.execute(_SQL)
            return con.execute("DELETE FROM bitacora_mensajes WHERE fecha_hora < ?", (limite,)).rowcount
    except sqlite3.Error:
        return 0


def ultimos(limite: int = 100) -> list[dict]:
    try:
        with sqlite3.connect(DB_PATH) as con:
            con.execute(_SQL)
            con.row_factory = sqlite3.Row
            filas = con.execute("SELECT * FROM bitacora_mensajes ORDER BY id DESC LIMIT ?", (limite,)).fetchall()
            return [dict(f) for f in filas]
    except sqlite3.Error:
        return []
