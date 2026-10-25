"""Integridad de los modelos: huella SHA-256 de cada archivo y verificación antes de cargarlo.

Los modelos se guardan con joblib (pickle): cargar un archivo alterado podría ejecutar código (CWE-502).
Por eso cada entrenamiento firma los archivos en ml/modelos/manifiesto.json y el servidor se niega a
cargar un modelo cuya huella no coincida o que no esté en el manifiesto (falla en modo seguro).
En producción, el manifiesto se firma además con una clave del gestor de secretos y los modelos
viven en un repositorio de artefactos con control de acceso.

Uso:  python -m ml.manifiesto      (vuelve a firmar los modelos actuales)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib

from ml.comun import MODELOS_DIR

MANIFIESTO = MODELOS_DIR / "manifiesto.json"


class ModeloAlterado(RuntimeError):
    """El archivo del modelo no coincide con su huella firmada."""


def huella(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def firmar() -> dict[str, str]:
    huellas = {p.name: huella(p) for p in sorted(MODELOS_DIR.glob("*.joblib"))}
    MANIFIESTO.write_text(json.dumps(huellas, indent=2) + "\n", encoding="utf-8", newline="\n")
    return huellas


def cargar(nombre: str):
    """Carga un modelo solo si su huella coincide con la del manifiesto."""
    ruta = MODELOS_DIR / nombre
    if ruta.parent.resolve() != MODELOS_DIR.resolve():
        raise ModeloAlterado(f"Ruta de modelo no permitida: {nombre}")
    huellas = json.loads(MANIFIESTO.read_text(encoding="utf-8")) if MANIFIESTO.exists() else {}
    if nombre not in huellas:
        raise ModeloAlterado(f"{nombre} no está firmado en {MANIFIESTO.name}: ejecute el entrenamiento")
    if huella(ruta) != huellas[nombre]:
        raise ModeloAlterado(f"{nombre} fue modificado después de entrenarse: no se carga")
    return joblib.load(ruta)


if __name__ == "__main__":
    for k, v in firmar().items():
        print(f"{v[:16]}…  {k}")
