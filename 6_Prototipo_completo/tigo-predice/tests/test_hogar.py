"""Tests del frente Hogar: telemetría sin fuga de datos, regla de umbrales, datos plausibles y piloto."""

import numpy as np
import pandas as pd
import pytest

from experimento import analisis
from ml import telemetria
from ml.comun import DB_PATH, cargar_config

CFG = cargar_config()


def _hogares(n=6):
    return pd.DataFrame(
        {
            "hogar_id": [f"H{i}" for i in range(n)],
            "nodo_id": ["N1"] * (n // 2) + ["N2"] * (n - n // 2),
            "zona": ["urbana"] * n,
            "es_fibra": [1] * n,
            "modem_antiguo": [0] * n,
            "edad_modem_meses": [12] * n,
            "firmware_desactualizado": [0] * n,
            "solo_2_4ghz": [0] * n,
            "antiguedad_meses": [24] * n,
            "plan_mbps": [100] * n,
            "dispositivos_base": [7] * n,
            "uso_base": [8.0] * n,
        }
    )


def test_variables_no_miran_el_futuro():
    h = _hogares()
    rng = np.random.default_rng(1)
    s = telemetria.base(rng, h, 40)
    cero = np.zeros((len(h), 40), int)
    antes = telemetria.variables(s, h, cero, cero, 25)
    s2 = {k: v.copy() for k, v in s.items()}
    s2["margen"][:, 26:] -= 10  # el futuro cambia por completo
    s2["retrans"][:, 26:] += 50
    pd.testing.assert_frame_equal(antes, telemetria.variables(s2, h, cero, cero, 25))


def test_problema_de_senal_baja_el_margen_y_dispara_la_regla_tarde():
    h = _hogares(1)
    rng = np.random.default_rng(2)
    s = telemetria.base(rng, h, 60)
    telemetria.aplicar(s, 0, "senal", telemetria.severidad(60, 30, 14, 99), rng)
    cero = np.zeros((1, 60), int)
    temprano = telemetria.variables(s, h, cero, cero, 33)
    tarde = telemetria.variables(s, h, cero, cero, 50)
    assert temprano["pendiente_margen_14d"].iloc[0] < 0 < tarde["margen_ult"].iloc[0] + 10
    assert not telemetria.alarma_regla(temprano)[0], "al inicio la regla aún no ve nada"
    assert telemetria.alarma_regla(tarde)[0], "con la señal bajo el umbral, la regla sí alarma"


def test_vecinos_del_nodo():
    h = _hogares(4)
    s = telemetria.base(np.random.default_rng(3), h, 20)
    s["desconexiones"][:] = 0
    s["desconexiones"][1, 15] = 30  # un vecino del nodo N1 con muchos cortes
    cero = np.zeros((4, 20), int)
    X = telemetria.variables(s, h, cero, cero, 19)
    assert X["desconexiones_nodo_7d"].iloc[0] == 30  # su único vecino en N1
    assert X["desconexiones_nodo_7d"].iloc[2] == 0  # N2 no se entera


def test_top_k_respeta_el_presupuesto():
    m = telemetria.top_k(np.arange(1000), 0.02)
    assert m.sum() == 20 and m[-20:].all()


def _efecto(red, p):
    return {"reduccion_relativa": red, "valor_p": p}


def test_decision_hogar():
    ch, pc = CFG["hogar"], CFG["piloto"]
    go = analisis.decidir_hogar(_efecto(0.25, 0.001), 0.004, 2.0, ch, pc)
    assert go["decision"] == "GO" and "modelo" in go["motivo"]
    con_regla = analisis.decidir_hogar(_efecto(0.25, 0.001), 0.004, 1.1, ch, pc)
    assert con_regla["decision"] == "GO" and "regla" in con_regla["motivo"]
    assert analisis.decidir_hogar(_efecto(0.05, 0.001), 0.004, 2.0, ch, pc)["decision"] == "NO-GO"
    assert analisis.decidir_hogar(_efecto(0.25, 0.30), 0.004, 2.0, ch, pc)["decision"] == "NO-GO"


@pytest.mark.skipif(not DB_PATH.exists(), reason="Faltan datos: ejecute tareas.ps1 preparar")
def test_datos_sinteticos_plausibles():
    from sqlalchemy import create_engine

    from ml.comun import url_db

    eng = create_engine(url_db())
    h = pd.read_sql_table("hogares", eng)
    ct = pd.read_sql_table("contactos_hogar", eng)
    sn = pd.read_sql_table("snapshots_hogar", eng, columns=["evento_7d", "dia_corte"])
    eng.dispose()
    vis = ct[ct["tipo"] == "visita"]
    tasa_mes = len(vis) / len(h) / 3
    assert 0.03 <= tasa_mes <= 0.06, "visitas por hogar al mes dentro del rango de los supuestos"
    assert 0.20 <= vis["evitable"].mean() <= 0.45
    assert 0.005 < sn["evento_7d"].mean() < 0.05
    assert not {"propension", "calidad_nodo"} & set(h.columns), "las variables latentes no se guardan"


@pytest.mark.skipif(not DB_PATH.exists(), reason="Faltan datos: ejecute tareas.ps1 preparar")
def test_simulacion_hogar_determinista():
    from sqlalchemy import create_engine

    from experimento import simulacion_hogar
    from ml.comun import url_db

    eng = create_engine(url_db())
    pu = pd.read_sql_table("puntajes_hogar", eng)
    eng.dispose()
    a = simulacion_hogar.simular(CFG, pu, 2.0)
    b = simulacion_hogar.simular(CFG, pu, 2.0)
    assert a == b
    assert a["marcados_por_semana"] == round(
        CFG["supuestos"]["hogares_piloto"]["base"] * CFG["hogar"]["pct_marcados_semana"]
    )
    assert a["metrica_norte"]["por_1000_tratamiento"] < a["metrica_norte"]["por_1000_control"]
