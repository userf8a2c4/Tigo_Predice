"""Casos para verificar que la calculadora de la interfaz («Pon tus números» sin servidor) dé lo mismo que Python.

Escribe frontend/src/test/roi_paridad.json con la configuración de negocio y la respuesta de GET /api/roi para varios
datos de Tigo. La prueba de la interfaz recalcula cada caso con frontend/src/roi.ts y exige el mismo resultado.

Uso: python docs/entregables/gen_paridad_roi.py   (después de cambiar config/negocio.toml o roi.py)
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from backend.app.services import roi  # noqa: E402
from ml.comun import cargar_config  # noqa: E402

SALIDA = RAIZ / "frontend" / "src" / "test" / "roi_paridad.json"

# Sin datos, cada dato por separado, los cuatro juntos y valores extremos permitidos por la API
CASOS = [
    {},
    {"visitas_mes_hogar_nacional": 4200},
    {"costo_por_visita": 900},
    {"llamadas_mes_fallas_nacional": 25000},
    {"costo_por_llamada": 48},
    {
        "visitas_mes_hogar_nacional": 7000,
        "costo_por_visita": 520,
        "llamadas_mes_fallas_nacional": 60000,
        "costo_por_llamada": 80,
    },
    {
        "visitas_mes_hogar_nacional": 50,
        "costo_por_visita": 1,
        "llamadas_mes_fallas_nacional": 10,
        "costo_por_llamada": 1,
    },
    {
        "visitas_mes_hogar_nacional": 1_000_000,
        "costo_por_visita": 1_000_000,
        "llamadas_mes_fallas_nacional": 10_000_000,
        "costo_por_llamada": 100_000,
    },
]


def main() -> None:
    cfg = cargar_config()
    casos = [
        {
            "tus": tus,
            "respuesta": {"escenarios": roi.escenarios(cfg, tus), "tornado": roi.tornado(cfg, tus), "tus_numeros": tus},
        }
        for tus in CASOS
    ]
    datos = {"config": roi.config_para_navegador(cfg), "casos": casos}
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("OK", SALIDA, len(casos), "casos")


if __name__ == "__main__":
    main()
