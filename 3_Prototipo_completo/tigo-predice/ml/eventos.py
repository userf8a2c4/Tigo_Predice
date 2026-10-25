"""Variables de un cliente al INICIO de una falla masiva (para el piloto de 72 h).

Solo usa información disponible en ese momento (sin fuga de datos):
historial anterior a la falla + lo que el NOC sabe de la falla (ETA, nº de sitios, hora).
Lo usan el generador de datos, el entrenamiento del modelo 72 h, la simulación
del piloto y la demo "Falla en vivo".
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

VARIABLES_EVENTO = [
    "es_prepago",
    "es_pospago",
    "es_hogar",
    "antiguedad_meses",
    "arpu",
    "gama_ord",
    "zona_urbana",
    "zona_rural",
    "llamadas_30d_previas",
    "llamadas_red_90d_previas",
    "sin_resolver_30d_previas",
    "nps_previo",
    "fallas_previas_90d",
    "caidas_30d_previas",
    "eta_conocida",
    "eta_horas",
    "n_sitios_afectados",
    "hora_inicio",
    "es_nocturna",
    "usa_whatsapp",
]

NOMBRES_VARIABLES = {
    "es_prepago": "Es prepago",
    "es_pospago": "Es pospago",
    "es_hogar": "Es cliente hogar",
    "antiguedad_meses": "Antigüedad",
    "arpu": "ARPU",
    "gama_ord": "Gama del equipo",
    "zona_urbana": "Zona urbana",
    "zona_rural": "Zona rural",
    "llamadas_30d_previas": "Llamadas previas (30 d)",
    "llamadas_red_90d_previas": "Llamadas por red (90 d)",
    "sin_resolver_30d_previas": "Llamadas sin resolver (30 d)",
    "nps_previo": "Última calificación",
    "fallas_previas_90d": "Fallas que ya le tocaron (90 d)",
    "caidas_30d_previas": "Caídas en su celda (30 d)",
    "eta_conocida": "El NOC tiene hora estimada",
    "eta_horas": "Hora estimada de solución",
    "n_sitios_afectados": "Sitios afectados",
    "hora_inicio": "Hora de inicio",
    "es_nocturna": "Falla nocturna",
    "usa_whatsapp": "Usa WhatsApp",
}


def construir(
    afectados: pd.DataFrame,
    zona_celda: pd.Series,
    interacciones: pd.DataFrame,
    encuestas: pd.DataFrame,
    red: pd.DataFrame,
    fallas_previas: list[tuple[set, date]],
    inicio: date,
    corte_datos: date,
    eta_horas: float | None,
    n_sitios: int,
    hora_inicio: int,
) -> pd.DataFrame:
    """Devuelve un DataFrame indexado por cliente_id con VARIABLES_EVENTO.

    `afectados`: filas de la tabla clientes (con cliente_id, segmento, antiguedad_meses, arpu,
    gama_dispositivo, canal_preferido, celda_id). `corte_datos`: fecha a la que corresponde
    la antigüedad guardada en la tabla clientes.
    """
    cl = afectados.set_index("cliente_id")
    idx = cl.index
    ini = inicio.isoformat()
    d30 = (inicio - timedelta(days=30)).isoformat()
    d90 = (inicio - timedelta(days=90)).isoformat()
    X = pd.DataFrame(index=idx)
    seg = cl["segmento"].to_numpy()
    X["es_prepago"] = (seg == "prepago").astype(int)
    X["es_pospago"] = (seg == "pospago").astype(int)
    X["es_hogar"] = (seg == "hogar").astype(int)
    meses_atras = max((corte_datos - inicio).days, 0) / 30.4
    X["antiguedad_meses"] = np.clip(cl["antiguedad_meses"].to_numpy() - meses_atras, 0, None).round(1)
    X["arpu"] = cl["arpu"].to_numpy()
    X["gama_ord"] = cl["gama_dispositivo"].map({"baja": 0, "media": 1, "alta": 2, "módem": 1}).to_numpy()
    zona = cl["celda_id"].map(zona_celda).to_numpy()
    X["zona_urbana"] = (zona == "urbana").astype(int)
    X["zona_rural"] = (zona == "rural").astype(int)

    it = interacciones[(interacciones["fecha"] < ini) & interacciones["cliente_id"].isin(idx)]
    i30 = it[it["fecha"] >= d30]
    X["llamadas_30d_previas"] = i30.groupby("cliente_id").size().reindex(idx).fillna(0).to_numpy()
    X["llamadas_red_90d_previas"] = (
        it[(it["fecha"] >= d90) & (it["motivo"] == "red")]
        .groupby("cliente_id")
        .size()
        .reindex(idx)
        .fillna(0)
        .to_numpy()
    )
    X["sin_resolver_30d_previas"] = (
        i30[i30["resuelto"] == 0].groupby("cliente_id").size().reindex(idx).fillna(0).to_numpy()
    )
    enc = encuestas[encuestas["fecha"] < ini].sort_values("fecha").groupby("cliente_id")["nps"].last()
    X["nps_previo"] = enc.reindex(idx).astype(float).to_numpy()

    celdas_cli = cl["celda_id"].to_numpy()
    previas = np.zeros(len(idx))
    for celdas_f, fecha_f in fallas_previas:
        if fecha_f.isoformat() >= d90 and fecha_f < inicio:
            previas += np.isin(celdas_cli, list(celdas_f))
    X["fallas_previas_90d"] = previas
    r30 = red[(red["fecha"] >= d30) & (red["fecha"] < ini)].groupby("celda_id")["caidas"].sum()
    X["caidas_30d_previas"] = pd.Series(celdas_cli).map(r30).fillna(0).to_numpy()

    X["eta_conocida"] = int(eta_horas is not None)
    X["eta_horas"] = np.nan if eta_horas is None else float(eta_horas)
    X["n_sitios_afectados"] = n_sitios
    X["hora_inicio"] = hora_inicio
    X["es_nocturna"] = int(hora_inicio >= 22 or hora_inicio < 6)
    X["usa_whatsapp"] = (cl["canal_preferido"] == "WhatsApp").astype(int).to_numpy()
    return X[VARIABLES_EVENTO].astype(float)


def logit_llamada(X: pd.DataFrame, duracion_horas: float, lealtad: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Propensión (logit sin intercepto) a llamar en 72 h si NO recibe aviso.

    Relaciones causales plausibles + variable latente (lealtad, que el modelo no ve) + ruido.
    La duración real de la falla solo es observable a través de la ETA del NOC.
    """
    nps = X["nps_previo"].to_numpy()
    nps_malo = np.where(np.isnan(nps), 0, nps <= 6)
    return (
        1.1 * X["es_hogar"].to_numpy()
        + 0.45 * X["es_pospago"].to_numpy()
        + 1.1 * np.tanh(duracion_horas / 10)
        + 0.45 * np.minimum(X["sin_resolver_30d_previas"].to_numpy(), 3)
        + 0.25 * np.minimum(X["llamadas_red_90d_previas"].to_numpy(), 3)
        + 0.35 * np.minimum(X["fallas_previas_90d"].to_numpy(), 3)
        + 0.4 * nps_malo
        - 0.005 * np.minimum(X["antiguedad_meses"].to_numpy(), 120)
        - 0.5 * X["es_nocturna"].to_numpy()
        + 0.25 * X["zona_urbana"].to_numpy()
        + 0.3 * (1 - X["eta_conocida"].to_numpy())
        - 0.25 * lealtad
        + rng.normal(0, 0.5, len(X))
    )
