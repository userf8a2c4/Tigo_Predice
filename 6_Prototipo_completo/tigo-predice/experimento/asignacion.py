"""Asignación reproducible a tratamiento o control por hash del ID del cliente.

El mismo cliente cae siempre en el mismo grupo (aunque le toquen varias fallas), sin tablas
que mantener y auditable: cualquiera puede recalcularlo con la sal y el ID.
"""

from __future__ import annotations

import hashlib

import numpy as np


def fraccion(cliente_id: str, sal: str) -> float:
    """Número en [0, 1) determinado por sha256(sal:cliente_id)."""
    h = hashlib.sha256(f"{sal}:{cliente_id}".encode()).digest()
    return int.from_bytes(h[:8], "big") / 2**64


def es_control(cliente_id: str, sal: str, pct_control: float) -> bool:
    return fraccion(cliente_id, sal) < pct_control


def asignar(ids, sal: str, pct_control: float) -> np.ndarray:
    """Vector booleano: True = control (NO recibe aviso)."""
    return np.array([es_control(str(i), sal, pct_control) for i in ids], dtype=bool)
