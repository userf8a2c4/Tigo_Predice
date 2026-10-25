"""Tests del caso de negocio conservador (v03: Hogar + Móvil)."""

import copy

import pytest

from backend.app.services import roi
from ml.comun import cargar_config

CFG = cargar_config()


def test_escenarios_ordenados():
    e = roi.escenarios(CFG)
    assert (
        e["conservador"]["nacional"]["neto_anio1"]
        < e["base"]["nacional"]["neto_anio1"]
        < e["optimista"]["nacional"]["neto_anio1"]
    )


def test_caso_base_usa_solo_beneficio_duro():
    """Cambiar la retención (potencial no incluido) NO debe mover el neto del caso base."""
    cfg = copy.deepcopy(CFG)
    base = roi.calcular(cfg)["nacional"]["neto_anio1"]
    cfg["supuestos"]["churn_incremental_evitado"]["base"] = 0.05
    otro = roi.calcular(cfg)
    assert otro["nacional"]["neto_anio1"] == pytest.approx(base)
    assert otro["potencial_no_incluido"]["margen_retenido_anio"] > 0


def test_beneficio_duro_es_llamadas_por_costo():
    r = roi.calcular(CFG)["movil"]["nacional"]
    assert r["beneficio_duro_anio"] == pytest.approx(
        r["llamadas_evitadas_anio"] * CFG["supuestos"]["costo_por_llamada"]["base"]
    )


def test_beneficio_hogar_es_visitas_por_valor_de_visita():
    s = {k: v["base"] for k, v in CFG["supuestos"].items()}
    h = roi.calcular(CFG)["hogar"]["nacional"]
    valor = s["costo_por_visita"] + s["llamadas_por_visita"] * s["costo_por_llamada"]
    assert h["valor_por_visita"] == pytest.approx(valor)
    assert h["beneficio_duro_anio"] == pytest.approx(h["visitas_evitadas_anio"] * valor)
    efecto = s["pct_visitas_evitables"] * s["captura_modelo_hogar"] * s["reduccion_visitas_marcados"]
    assert h["reduccion_total_visitas"] == pytest.approx(efecto)
    assert efecto < 0.20, "conservador: menos que el 20 % que declaran los proveedores sobre TODAS las visitas"


def test_total_es_la_suma_de_los_frentes():
    r = roi.calcular(CFG)
    for k in ("beneficio_duro_anio", "costo_recurrente_anio", "inversion_unica", "neto_anio1"):
        assert r["nacional"][k] == pytest.approx(r["movil"]["nacional"][k] + r["hogar"]["nacional"][k])
    assert r["piloto"]["costo_total"] == pytest.approx(
        r["movil"]["piloto"]["costo_total"] + r["hogar"]["piloto"]["costo_total"]
    )


def test_punto_de_equilibrio_da_neto_cero():
    r = roi.calcular(CFG)
    eq = r["movil"]["nacional"]["equilibrio_reduccion_anio1"]
    vals = dict(r["supuestos"])
    vals["reduccion_con_aviso"] = eq
    assert roi.calcular(CFG, valores=vals)["movil"]["nacional"]["neto_anio1"] == pytest.approx(0, abs=1)
    assert eq < CFG["piloto"]["go_reduccion_min"], "el criterio GO debe exigir más que el equilibrio"


def test_punto_de_equilibrio_hogar_da_neto_cero():
    r = roi.calcular(CFG)
    eq = r["hogar"]["nacional"]["equilibrio_reduccion_anio1"]
    vals = dict(r["supuestos"])
    vals["reduccion_visitas_marcados"] = eq
    assert roi.calcular(CFG, valores=vals)["hogar"]["nacional"]["neto_anio1"] == pytest.approx(0, abs=1)
    assert eq < CFG["supuestos"]["reduccion_visitas_marcados"]["bajo"], "Hogar se paga aun con el efecto bajo"


def test_tornado_ordenado_por_amplitud():
    t = roi.tornado(CFG)
    amplitudes = [x["amplitud"] for x in t]
    assert amplitudes == sorted(amplitudes, reverse=True)
    assert t[0]["supuesto"] == "reduccion_con_aviso"
    nombres = {x["supuesto"] for x in t}
    assert {"reduccion_visitas_marcados", "costo_por_visita"} <= nombres
    assert not nombres & roi.SOLO_PILOTO


def test_pon_tus_numeros_recalcula_y_marca_dato_tigo():
    base = roi.calcular(CFG)
    r = roi.calcular(CFG, tus_numeros={"costo_por_llamada": 170, "llamadas_mes_fallas_nacional": 30000})
    assert r["fuentes"]["costo_por_llamada"] == "dato Tigo"
    assert r["movil"]["nacional"]["llamadas_mes_por_fallas"] == 30000
    assert r["nacional"]["beneficio_duro_anio"] != base["nacional"]["beneficio_duro_anio"]
    h = roi.calcular(CFG, tus_numeros={"visitas_mes_hogar_nacional": 9000, "costo_por_visita": 1300})
    assert h["fuentes"]["costo_por_visita"] == "dato Tigo" and h["fuentes"]["visitas_mes_hogar_nacional"] == "dato Tigo"
    assert h["hogar"]["nacional"]["visitas_mes"] == 9000
    assert h["movil"]["nacional"]["neto_anio1"] == pytest.approx(base["movil"]["nacional"]["neto_anio1"])
    ignorado = roi.calcular(CFG, tus_numeros={"parametro_inventado": 99})
    assert ignorado["nacional"]["neto_anio1"] == pytest.approx(base["nacional"]["neto_anio1"])


def test_costos_completos_incluidos():
    r = roi.calcular(CFG)
    assert set(r["piloto"]["costos"]) == {
        "desarrollo_integracion",
        "equipo_piloto",
        "infraestructura",
        "whatsapp",
        "compensaciones",
        "desarrollo_hogar",
        "equipo_hogar",
        "whatsapp_hogar",
    }
    assert set(r["nacional"]["costos_recurrentes"]) == {
        "operacion_y_mantenimiento",
        "infraestructura",
        "whatsapp",
        "compensaciones",
        "operacion_hogar",
        "whatsapp_hogar",
    }
    assert r["nacional"]["inversion_unica"] > 0


def test_compensaciones_con_tope():
    cfg = copy.deepcopy(CFG)
    cfg["supuestos"]["pct_compensados"]["base"] = 1.0
    r = roi.calcular(cfg)
    assert r["movil"]["nacional"]["costos_recurrentes"]["compensaciones"] == pytest.approx(
        cfg["topes"]["compensaciones_mes_nacional"] * 12
    )


@pytest.mark.parametrize(
    "v,texto",
    [(5_123_456, "L 5.1 M"), (-1_480_000, "−L 1.5 M"), (523_000, "L 520 mil"), (85, "L 85"), (1_100, "L 1,100")],
)
def test_redondeo_sin_falsa_precision(v, texto):
    assert roi.L(v) == texto
