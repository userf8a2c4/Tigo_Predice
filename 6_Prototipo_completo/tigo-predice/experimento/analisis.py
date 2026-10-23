"""Análisis del piloto: efecto del aviso con intervalo de confianza, valor p y decisión GO / NO-GO.

Métrica norte: llamadas al call center por cada 1,000 afectados en las 72 h posteriores a la falla.
- Inferencia sobre la media de llamadas por afectado (diferencia de medias, aproximación normal;
  con miles de afectados por grupo el teorema central del límite aplica).
- Reducción relativa con IC 95 % por método delta sobre el log del cociente.
- Secundario: % de afectados que llama (prueba z de dos proporciones).
Análisis por intención de tratar: se compara a TODOS los asignados, aunque no hayan leído el aviso.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import norm


def _z(alfa: float) -> float:
    return float(norm.ppf(1 - alfa / 2))


def comparar_medias(llam_t: np.ndarray, llam_c: np.ndarray, alfa: float = 0.05) -> dict:
    """Llamadas por afectado: tratamiento vs. control."""
    llam_t, llam_c = np.asarray(llam_t, float), np.asarray(llam_c, float)
    n_t, n_c = len(llam_t), len(llam_c)
    m_t, m_c = float(llam_t.mean()), float(llam_c.mean())
    v_t, v_c = float(llam_t.var(ddof=1)), float(llam_c.var(ddof=1))
    z = _z(alfa)
    dif = m_t - m_c
    se = math.sqrt(v_t / n_t + v_c / n_c)
    estad = dif / se if se > 0 else 0.0
    p = float(2 * norm.sf(abs(estad)))
    rr = m_t / m_c if m_c > 0 else float("nan")
    se_log = math.sqrt(v_t / (n_t * m_t**2) + v_c / (n_c * m_c**2)) if m_t > 0 and m_c > 0 else float("nan")
    rr_lo, rr_hi = rr * math.exp(-z * se_log), rr * math.exp(z * se_log)
    return {
        "n_tratamiento": n_t,
        "n_control": n_c,
        "por_1000_tratamiento": round(m_t * 1000, 1),
        "por_1000_control": round(m_c * 1000, 1),
        "diferencia_por_1000": round(dif * 1000, 1),
        "ic_diferencia_por_1000": [round((dif - z * se) * 1000, 1), round((dif + z * se) * 1000, 1)],
        "reduccion_relativa": round(1 - rr, 4),
        "ic_reduccion_relativa": [round(1 - rr_hi, 4), round(1 - rr_lo, 4)],
        "estadistico_z": round(estad, 3),
        "valor_p": p,
        "significativo": bool(p < alfa),
        "alfa": alfa,
    }


def comparar_proporciones(x_t: int, n_t: int, x_c: int, n_c: int, alfa: float = 0.05) -> dict:
    """% de afectados que llama: prueba z de dos proporciones (varianza combinada)."""
    p_t, p_c = x_t / n_t, x_c / n_c
    p = (x_t + x_c) / (n_t + n_c)
    se0 = math.sqrt(p * (1 - p) * (1 / n_t + 1 / n_c))
    z_est = (p_t - p_c) / se0 if se0 > 0 else 0.0
    se = math.sqrt(p_t * (1 - p_t) / n_t + p_c * (1 - p_c) / n_c)
    z = _z(alfa)
    return {
        "tasa_tratamiento": round(p_t, 4),
        "tasa_control": round(p_c, 4),
        "diferencia": round(p_t - p_c, 4),
        "ic_diferencia": [round(p_t - p_c - z * se, 4), round(p_t - p_c + z * se, 4)],
        "valor_p": float(2 * norm.sf(abs(z_est))),
    }


def _pct(v: float, decimales: int = 0) -> str:
    return f"{v * 100:.{decimales}f} %"


def _p(v: float) -> str:
    return "p < 0.001" if v < 0.001 else f"p = {v:.3f}"


def decidir(efecto: dict, tasa_optout: float, cfg_piloto: dict) -> dict:
    """GO solo si: reducción >= mínimo, diferencia significativa y opt-out bajo el máximo."""
    minimo, opt_max, alfa = cfg_piloto["go_reduccion_min"], cfg_piloto["go_optout_max"], cfg_piloto["alfa"]
    criterios = [
        {
            "criterio": f"Reducción de llamadas ≥ {_pct(minimo)}",
            "valor": _pct(efecto["reduccion_relativa"]),
            "cumple": bool(efecto["reduccion_relativa"] >= minimo),
        },
        {
            "criterio": f"Diferencia significativa (p < {alfa})",
            "valor": _p(efecto["valor_p"]),
            "cumple": bool(efecto["valor_p"] < alfa),
        },
        {
            "criterio": f"Opt-out < {_pct(opt_max)}",
            "valor": _pct(tasa_optout, 1),
            "cumple": bool(tasa_optout < opt_max),
        },
    ]
    go = all(c["cumple"] for c in criterios)
    if go:
        motivo = "El aviso reduce las llamadas de forma significativa y sin rechazo de los clientes: escalar."
    elif not criterios[1]["cumple"]:
        motivo = "No hay diferencia significativa frente al control: no escalar (o ampliar la muestra)."
    elif not criterios[0]["cumple"]:
        motivo = "El efecto es real pero menor al mínimo que justifica la inversión: no escalar."
    else:
        motivo = "Demasiados clientes piden no recibir mensajes: revisar el mensaje antes de escalar."
    return {"decision": "GO" if go else "NO-GO", "criterios": criterios, "motivo": motivo}


def decidir_hogar(efecto: dict, tasa_optout: float, ia_vs_regla: float, cfg_hogar: dict, cfg_piloto: dict) -> dict:
    """Frente Hogar: GO si bajan las visitas (≥ mínimo y significativo), sin rechazo, y la IA le gana a la regla.

    Si la IA no supera a la regla de umbrales por el margen pedido, el piloto sigue con la regla (más simple):
    el producto funciona igual, con menos captura. Eso no es NO-GO del frente, es NO-GO del modelo.
    """
    minimo, alfa, opt_max = cfg_hogar["go_reduccion_visitas_min"], cfg_piloto["alfa"], cfg_piloto["go_optout_max"]
    ia_min = cfg_hogar["go_ia_vs_regla_min"]
    criterios = [
        {
            "criterio": f"Reducción de visitas en hogares marcados ≥ {_pct(minimo)}",
            "valor": _pct(efecto["reduccion_relativa"]),
            "cumple": bool(efecto["reduccion_relativa"] >= minimo),
        },
        {
            "criterio": f"Diferencia significativa (p < {alfa})",
            "valor": _p(efecto["valor_p"]),
            "cumple": bool(efecto["valor_p"] < alfa),
        },
        {
            "criterio": f"Opt-out < {_pct(opt_max)}",
            "valor": _pct(tasa_optout, 1),
            "cumple": bool(tasa_optout < opt_max),
        },
        {
            "criterio": f"La IA captura ≥ {ia_min:.1f}× lo que captura la regla de umbrales",
            "valor": f"{ia_vs_regla:.1f}×",
            "cumple": bool(ia_vs_regla >= ia_min),
        },
    ]
    go = all(c["cumple"] for c in criterios[:3])
    if go and criterios[3]["cumple"]:
        motivo = "Las visitas bajan de forma significativa y la IA supera a la regla: escalar con el modelo."
    elif go:
        motivo = "Las visitas bajan, pero la IA no supera a la regla por el margen pedido: escalar con la regla."
    elif not criterios[1]["cumple"]:
        motivo = "No hay diferencia significativa frente al control: no escalar (o ampliar la muestra)."
    elif not criterios[0]["cumple"]:
        motivo = "El efecto es real pero menor al mínimo que justifica la inversión: no escalar."
    else:
        motivo = "Demasiados clientes piden no recibir mensajes: revisar el mensaje antes de escalar."
    return {"decision": "GO" if go else "NO-GO", "criterios": criterios, "motivo": motivo}
