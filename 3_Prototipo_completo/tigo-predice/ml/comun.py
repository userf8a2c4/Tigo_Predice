"""Utilidades compartidas: rutas, configuración de negocio y catálogo de ciudades."""

from __future__ import annotations

import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATA_DIR = RAIZ / "data"
MODELOS_DIR = RAIZ / "ml" / "modelos"
REPORTES_DIR = RAIZ / "reports"
CONFIG_PATH = RAIZ / "config" / "negocio.toml"
DB_PATH = DATA_DIR / "tigo_predice.db"

# Ciudad, departamento, latitud, longitud, peso poblacional aproximado (miles)
CIUDADES = [
    ("Tegucigalpa", "Francisco Morazán", 14.0818, -87.2068, 1300),
    ("San Pedro Sula", "Cortés", 15.5042, -88.0250, 800),
    ("La Ceiba", "Atlántida", 15.7597, -86.7822, 200),
    ("Choluteca", "Choluteca", 13.3007, -87.1908, 160),
    ("Comayagua", "Comayagua", 14.4513, -87.6376, 160),
    ("El Progreso", "Yoro", 15.4000, -87.8000, 200),
    ("Danlí", "El Paraíso", 14.0333, -86.5833, 200),
    ("Juticalpa", "Olancho", 14.6667, -86.2167, 130),
    ("Santa Rosa de Copán", "Copán", 14.7667, -88.7833, 70),
    ("Siguatepeque", "Comayagua", 14.6000, -87.8333, 100),
]

SEGMENTOS = ("prepago", "pospago", "hogar")


NIVELES = ("bajo", "base", "alto")


def cargar_config() -> dict:
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def supuesto(cfg: dict, nombre: str, nivel: str = "base") -> float:
    """Valor de un supuesto de negocio en el nivel pedido (bajo / base / alto)."""
    return float(cfg["supuestos"][nombre][nivel])


def supuestos_nivel(cfg: dict, nivel: str = "base") -> dict[str, float]:
    """Todos los supuestos en un mismo nivel, como diccionario plano."""
    return {k: float(v[nivel]) for k, v in cfg["supuestos"].items()}


def url_db() -> str:
    return f"sqlite:///{DB_PATH.as_posix()}"
