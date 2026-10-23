"""Tamaño de muestra y poder estadístico del piloto (dos proporciones, asignación desigual).

Pregunta que responde: ¿cuántos clientes afectados necesitamos para detectar una reducción de X %
en el % de afectados que llama, con un grupo control del k %?
"""

from __future__ import annotations

import math

from scipy.stats import norm


def tamano_muestra(p0: float, reduccion_rel: float, alfa: float, poder: float, pct_control: float) -> int:
    """Total de afectados necesarios (tratamiento + control)."""
    p1 = p0 * (1 - reduccion_rel)
    k = pct_control
    za, zb = norm.ppf(1 - alfa / 2), norm.ppf(poder)
    pbar = k * p0 + (1 - k) * p1
    num = (
        za * math.sqrt(pbar * (1 - pbar) * (1 / k + 1 / (1 - k)))
        + zb * math.sqrt(p0 * (1 - p0) / k + p1 * (1 - p1) / (1 - k))
    ) ** 2
    return math.ceil(num / (p0 - p1) ** 2)


def poder_alcanzado(n_total: int, p0: float, reduccion_rel: float, alfa: float, pct_control: float) -> float:
    p1 = p0 * (1 - reduccion_rel)
    k = pct_control
    n_c, n_t = n_total * k, n_total * (1 - k)
    pbar = k * p0 + (1 - k) * p1
    se0 = math.sqrt(pbar * (1 - pbar) * (1 / n_c + 1 / n_t))
    se1 = math.sqrt(p0 * (1 - p0) / n_c + p1 * (1 - p1) / n_t)
    za = norm.ppf(1 - alfa / 2)
    return float(norm.cdf((abs(p0 - p1) - za * se0) / se1))


def plan(cfg: dict, p0: float, afectados_esperados: int, reduccion_rel: float | None = None) -> dict:
    """Resumen para la UI: muestra necesaria, esperada en el piloto y poder alcanzado."""
    pc = cfg["piloto"]
    red = pc["go_reduccion_min"] if reduccion_rel is None else reduccion_rel
    n = tamano_muestra(p0, red, pc["alfa"], pc["poder"], pc["pct_control"])
    return {
        "tasa_base": round(p0, 3),
        "reduccion_a_detectar": red,
        "alfa": pc["alfa"],
        "poder_objetivo": pc["poder"],
        "pct_control": pc["pct_control"],
        "afectados_necesarios": n,
        "control_necesario": math.ceil(n * pc["pct_control"]),
        "afectados_esperados_piloto": int(afectados_esperados),
        "poder_alcanzado": round(poder_alcanzado(afectados_esperados, p0, red, pc["alfa"], pc["pct_control"]), 3),
        "dias_necesarios": math.ceil(n / max(afectados_esperados, 1) * pc["dias"]),
        "nota": "Asume afectados independientes. Como los clientes de una misma falla se parecen, "
        "en el piloto se usarán errores agrupados por falla; si hay pocas fallas, conviene extender el plazo.",
    }
