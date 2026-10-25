"""Tests del diseño y análisis del experimento del piloto."""

import math

import numpy as np
import pytest

from experimento import analisis, asignacion, potencia
from ml.comun import cargar_config

CFG = cargar_config()


def test_asignacion_estable_y_reproducible():
    ids = [f"C{i:06d}" for i in range(2000)]
    a = asignacion.asignar(ids, "sal", 0.15)
    b = asignacion.asignar(ids, "sal", 0.15)
    assert (a == b).all(), "el mismo cliente cae siempre en el mismo grupo"
    assert asignacion.asignar(ids, "otra-sal", 0.15).tolist() != a.tolist(), "la sal cambia la asignación"


def test_asignacion_respeta_el_porcentaje_de_control():
    ids = [f"V{i}" for i in range(50_000)]
    assert asignacion.asignar(ids, "tigo", 0.15).mean() == pytest.approx(0.15, abs=0.01)


def test_comparar_medias_contra_calculo_a_mano():
    t = np.array([0] * 70 + [1] * 30, dtype=float)  # 0.30 llamadas por afectado
    c = np.array([0] * 60 + [1] * 40, dtype=float)  # 0.40
    r = analisis.comparar_medias(t, c)
    se = math.sqrt(t.var(ddof=1) / 100 + c.var(ddof=1) / 100)
    assert r["por_1000_tratamiento"] == 300 and r["por_1000_control"] == 400
    assert r["diferencia_por_1000"] == -100
    assert r["ic_diferencia_por_1000"][0] == pytest.approx((-0.1 - 1.959964 * se) * 1000, abs=0.2)
    assert r["reduccion_relativa"] == pytest.approx(0.25)
    assert r["valor_p"] == pytest.approx(2 * (1 - 0.5 * (1 + math.erf(abs(-0.1 / se) / math.sqrt(2)))), rel=1e-6)


def test_prueba_de_proporciones_caso_conocido():
    r = analisis.comparar_proporciones(300, 1000, 400, 1000)
    # z combinado = -0.1 / sqrt(0.35*0.65*0.002) = -4.688  => p ≈ 2.8e-6
    assert r["valor_p"] == pytest.approx(2.76e-6, rel=0.05)
    assert r["diferencia"] == pytest.approx(-0.1)


def test_tamano_de_muestra_referencia_asignacion_igual():
    # Fórmula clásica de dos proporciones: p0 = 0.33, reducción 10 %, α = 0.05, poder 80 % => ~3,101 por grupo
    n = potencia.tamano_muestra(0.33, 0.10, 0.05, 0.80, 0.5)
    assert 6190 <= n <= 6215
    assert potencia.poder_alcanzado(n, 0.33, 0.10, 0.05, 0.5) == pytest.approx(0.80, abs=0.01)


def test_control_pequeno_requiere_mas_muestra():
    assert potencia.tamano_muestra(0.33, 0.10, 0.05, 0.8, 0.15) > potencia.tamano_muestra(0.33, 0.10, 0.05, 0.8, 0.5)


def _efecto(red, p):
    return {"reduccion_relativa": red, "valor_p": p}


@pytest.mark.parametrize(
    "efecto,optout,esperado",
    [
        (_efecto(0.15, 0.001), 0.005, "GO"),
        (_efecto(0.15, 0.20), 0.005, "NO-GO"),  # no significativo
        (_efecto(0.05, 0.001), 0.005, "NO-GO"),  # efecto real pero menor al mínimo
        (_efecto(0.15, 0.001), 0.05, "NO-GO"),  # demasiados opt-out
    ],
)
def test_decision_go_no_go(efecto, optout, esperado):
    assert analisis.decidir(efecto, optout, CFG["piloto"])["decision"] == esperado
