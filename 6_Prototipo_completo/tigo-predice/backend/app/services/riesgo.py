"""Motor de riesgo: valor del cliente, valor en riesgo (L) y prioridad Alta/Media/Baja.

Prioridad = riesgo × valor, expresado en Lempiras en riesgo:
    valor_en_riesgo = P(churn) × CLV + P(incidencia) × costo de atender la llamada
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ml.comun import supuesto


def calcular_valor(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    vida = df["segmento"].map(cfg["vida_util_meses"]).astype(float)
    df["valor_mensual"] = df["arpu"].round(2)
    df["clv"] = (df["arpu"] * vida).round(0)
    df["valor_en_riesgo"] = (
        df["prob_churn"] * df["clv"] + df["prob_incidencia"] * supuesto(cfg, "costo_por_llamada")
    ).round(2)
    df["riesgo_dominante"] = np.where(
        df["prob_churn"] * df["clv"] >= df["prob_incidencia"] * supuesto(cfg, "costo_por_llamada"),
        "churn",
        "incidencia",
    )
    return df


def umbrales(df: pd.DataFrame, cfg: dict) -> tuple[float, float]:
    """Se fijan una vez con la foto del día; la demo reutiliza los mismos umbrales."""
    r = cfg["reglas"]
    alta = float(df["valor_en_riesgo"].quantile(1 - r["porcentaje_alta"]))
    media = float(df["valor_en_riesgo"].quantile(1 - r["porcentaje_alta"] - r["porcentaje_media"]))
    return alta, media


def asignar_prioridad(df: pd.DataFrame, u: tuple[float, float]) -> pd.DataFrame:
    alta, media = u
    df["prioridad"] = np.select(
        [df["valor_en_riesgo"] >= alta, df["valor_en_riesgo"] >= media], ["Alta", "Media"], "Baja"
    )
    return df
