"""Exporta los números que usan los gráficos de la presentación (una sola fuente: config + modelos + simulación).

Uso:  python docs/entregables/datos_deck.py <salida.json>
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402

from backend.app.services import roi  # noqa: E402
from experimento import simulacion_hogar  # noqa: E402
from ml.comun import REPORTES_DIR, cargar_config, url_db  # noqa: E402

cfg = cargar_config()
es = roi.escenarios(cfg)
mh = json.loads((REPORTES_DIR / "metricas_hogar.json").read_text(encoding="utf-8"))
eng = create_engine(url_db())
piloto_h = simulacion_hogar.simular(cfg, pd.read_sql_table("puntajes_hogar", eng), mh["ia_vs_regla"])
eng.dispose()
m = lambda v: round(v / 1e6, 1)  # noqa: E731
n = piloto_h["metrica_norte"]
datos = {
    "cifras": roi.cifras(cfg),
    "neto_frente_millones": {
        k: {"Hogar": m(v["hogar"]["nacional"]["neto_anio1"]), "Móvil": m(v["movil"]["nacional"]["neto_anio1"])}
        for k, v in es.items()
    },
    "captura_visitas_evitables": {
        "Azar": round(mh["azar"]["captura_visitas_evitables"] * 100),
        "Regla de umbrales": round(mh["regla_umbrales"]["captura_visitas_evitables"] * 100),
        "Regresión logística": round(mh["modelos"]["regresión logística"]["captura_visitas_evitables"] * 100),
        "IA (LightGBM calibrado)": round(mh["modelos"]["LightGBM calibrado"]["captura_visitas_evitables"] * 100),
    },
    "piloto_hogar": {
        "control_por_1000": round(n["por_1000_control"]),
        "tratamiento_por_1000": round(n["por_1000_tratamiento"]),
        "reduccion": f"{n['reduccion_relativa'] * 100:.0f} %",
        "ic": f"{n['ic_reduccion_relativa'][0] * 100:.0f} % a {n['ic_reduccion_relativa'][1] * 100:.0f} %",
        "reduccion_llamadas": f"{piloto_h['llamadas']['reduccion_relativa'] * 100:.0f} %",
        "poder": f"{piloto_h['potencia']['poder_alcanzado'] * 100:.0f} %",
        "marcados": piloto_h["marcados"],
        "decision": piloto_h["decision"]["decision"],
    },
}
Path(sys.argv[1]).write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
print("OK", sys.argv[1])
