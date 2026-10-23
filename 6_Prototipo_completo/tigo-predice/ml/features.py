"""Construcción de variables (features) por cliente a una fecha de corte.

Se usa igual para entrenar y para calificar, de modo que la lógica viva en un solo lugar.
También define cómo se explica cada variable en lenguaje natural (para SHAP).
"""

from __future__ import annotations

import math
from datetime import date, timedelta

import numpy as np
import pandas as pd

NUMERICAS = [
    # Red
    "caidas_7d",
    "caidas_30d",
    "min_sin_servicio_30d",
    "latencia_ms_7d",
    "velocidad_pct_plan_7d",
    "brecha_velocidad_celda",
    "falla_masiva_activa",
    # Uso
    "datos_gb_30d",
    "voz_min_30d",
    "tendencia_uso",
    "recargas_30d",
    "dias_sin_recarga",
    # Facturación
    "dias_atraso",
    "meses_con_atraso_90d",
    "bajo_plan_90d",
    "reclamos_cobro_90d",
    # Interacciones
    "llamadas_30d",
    "llamadas_sin_resolver_30d",
    "llamadas_red_30d",
    "llamadas_equipo_30d",
    "tickets_abiertos",
    "horas_resolucion_prom",
    "nps_ultimo",
    # Perfil
    "antiguedad_meses",
    "arpu",
    "gama_ord",
    "es_prepago",
    "es_pospago",
    "es_hogar",
]

GRUPO = {
    "caidas_7d": "Red",
    "caidas_30d": "Red",
    "min_sin_servicio_30d": "Red",
    "latencia_ms_7d": "Red",
    "velocidad_pct_plan_7d": "Red",
    "brecha_velocidad_celda": "Equipo",
    "falla_masiva_activa": "Red",
    "datos_gb_30d": "Uso",
    "voz_min_30d": "Uso",
    "tendencia_uso": "Uso",
    "recargas_30d": "Uso",
    "dias_sin_recarga": "Uso",
    "dias_atraso": "Facturación",
    "meses_con_atraso_90d": "Facturación",
    "bajo_plan_90d": "Facturación",
    "reclamos_cobro_90d": "Facturación",
    "llamadas_30d": "Atención",
    "llamadas_sin_resolver_30d": "Atención",
    "llamadas_red_30d": "Atención",
    "llamadas_equipo_30d": "Equipo",
    "tickets_abiertos": "Atención",
    "horas_resolucion_prom": "Atención",
    "nps_ultimo": "Satisfacción",
    "antiguedad_meses": "Perfil",
    "arpu": "Perfil",
    "gama_ord": "Perfil",
    "es_prepago": "Perfil",
    "es_pospago": "Perfil",
    "es_hogar": "Perfil",
}


def _pct(v: float) -> str:
    return f"{abs(v) * 100:.0f} %"


def _n(v: float, singular: str, plural: str) -> str:
    return f"{int(v)} {singular if int(v) == 1 else plural}"


# Texto en lenguaje natural para un no técnico. Devuelve None si el valor no amerita mención.
def explicar(variable: str, v: float) -> str | None:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    textos = {
        "caidas_7d": lambda: f"{int(v)} caídas de señal esta semana en su zona" if v >= 2 else None,
        "caidas_30d": lambda: f"{int(v)} caídas de señal en el último mes" if v >= 4 else None,
        "min_sin_servicio_30d": lambda: f"{v / 60:.1f} horas sin servicio en el último mes" if v >= 60 else None,
        "latencia_ms_7d": lambda: f"Conexión lenta para responder ({v:.0f} ms)" if v >= 90 else None,
        "velocidad_pct_plan_7d": lambda: f"Recibe solo el {_pct(v)} de la velocidad contratada" if v < 0.7 else None,
        "brecha_velocidad_celda": lambda: (
            "Su velocidad está muy por debajo de la de sus vecinos (posible falla de equipo)" if v <= -0.25 else None
        ),
        "falla_masiva_activa": lambda: "Falla masiva activa en su zona" if v >= 1 else None,
        "tendencia_uso": lambda: f"Su consumo bajó {_pct(v)} frente al mes anterior" if v <= -0.15 else None,
        "dias_sin_recarga": lambda: f"{int(v)} días sin recargar" if v >= 14 else None,
        "recargas_30d": lambda: "Casi no ha recargado este mes" if v <= 1 else None,
        "dias_atraso": lambda: f"Pago atrasado {int(v)} días" if v >= 5 else None,
        "meses_con_atraso_90d": lambda: f"Atrasos de pago en {int(v)} de los últimos 3 meses" if v >= 2 else None,
        "bajo_plan_90d": lambda: "Bajó de plan recientemente" if v >= 1 else None,
        "reclamos_cobro_90d": lambda: (
            _n(v, "reclamo de cobro reciente", "reclamos de cobro recientes") if v >= 1 else None
        ),
        "llamadas_30d": lambda: f"{int(v)} llamadas al call center este mes" if v >= 2 else None,
        "llamadas_sin_resolver_30d": lambda: (
            _n(v, "llamada reciente sin resolver", "llamadas recientes sin resolver") if v >= 1 else None
        ),
        "llamadas_red_30d": lambda: (
            _n(v, "llamada por problemas de señal", "llamadas por problemas de señal") if v >= 1 else None
        ),
        "llamadas_equipo_30d": lambda: (
            _n(v, "llamada por fallas de su equipo/módem", "llamadas por fallas de su equipo/módem") if v >= 1 else None
        ),
        "tickets_abiertos": lambda: (
            _n(v, "ticket abierto sin cerrar", "tickets abiertos sin cerrar") if v >= 1 else None
        ),
        "horas_resolucion_prom": lambda: f"Sus casos tardan {v:.0f} horas en resolverse" if v >= 36 else None,
        "nps_ultimo": lambda: f"Calificó a Tigo con {int(v)}/10 en la última encuesta" if v <= 6 else None,
        "antiguedad_meses": lambda: f"Cliente nuevo ({int(v)} meses con Tigo)" if v <= 6 else None,
    }
    f = textos.get(variable)
    return f() if f else None


def construir(tablas: dict[str, pd.DataFrame], corte: date) -> pd.DataFrame:
    """Devuelve un DataFrame indexado por cliente_id con las columnas de NUMERICAS."""
    cl = tablas["clientes"].set_index("cliente_id")
    idx = cl.index
    c7 = (corte - timedelta(days=6)).isoformat()
    c30 = (corte - timedelta(days=29)).isoformat()
    X = pd.DataFrame(index=idx)

    # ---------------- Red (por la celda del cliente) + telemetría individual
    hoy = corte.isoformat()  # todo se filtra a <= corte: sin fuga de información futura
    red = tablas["red_diaria"][tablas["red_diaria"]["fecha"] <= hoy]
    r7 = (
        red[red["fecha"] >= c7]
        .groupby("celda_id")
        .agg(caidas_7d=("caidas", "sum"), vel_celda=("velocidad_pct_plan", "mean"))
    )
    r30 = (
        red[red["fecha"] >= c30]
        .groupby("celda_id")
        .agg(caidas_30d=("caidas", "sum"), min_sin_servicio_30d=("minutos_sin_servicio", "sum"))
    )
    celda = cl["celda_id"]
    X["caidas_7d"] = r7["caidas_7d"].reindex(celda).to_numpy()
    X["caidas_30d"] = r30["caidas_30d"].reindex(celda).to_numpy()
    X["min_sin_servicio_30d"] = r30["min_sin_servicio_30d"].reindex(celda).to_numpy()
    tel = tablas["telemetria"].set_index("cliente_id").reindex(idx)
    X["latencia_ms_7d"] = tel["latencia_ms_7d"].to_numpy()
    X["velocidad_pct_plan_7d"] = tel["velocidad_pct_plan_7d"].to_numpy()
    X["brecha_velocidad_celda"] = X["velocidad_pct_plan_7d"] - r7["vel_celda"].reindex(celda).to_numpy()
    fm = tablas["fallas_masivas"]
    activas = set()
    for celdas_txt in fm.loc[fm["estado"] == "activa", "celdas"]:
        activas.update(celdas_txt.split(","))
    X["falla_masiva_activa"] = celda.isin(activas).astype(int).to_numpy()

    # ---------------- Uso
    uso = tablas["uso_semanal"]
    ult = uso["semana"].max()
    u_rec = uso[uso["semana"] > ult - 4].groupby("cliente_id")
    u_prev = uso[(uso["semana"] <= ult - 4) & (uso["semana"] > ult - 8)].groupby("cliente_id")
    gb_rec = u_rec["datos_gb"].sum().reindex(idx)
    gb_prev = u_prev["datos_gb"].sum().reindex(idx)
    X["datos_gb_30d"] = gb_rec.to_numpy()
    X["voz_min_30d"] = u_rec["voz_min"].sum().reindex(idx).to_numpy()
    X["tendencia_uso"] = np.clip((gb_rec / gb_prev.clip(lower=1e-3) - 1).to_numpy(), -1, 3)
    X["recargas_30d"] = u_rec["recargas"].sum().reindex(idx).to_numpy()
    con_rec = uso[uso["recargas"] > 0].groupby("cliente_id")["semana"].max().reindex(idx)
    dias_sin = ((ult - con_rec) * 7 + 3).fillna(90).to_numpy()
    X["dias_sin_recarga"] = np.where(cl["segmento"].to_numpy() == "prepago", dias_sin, 0)

    # ---------------- Facturación
    pg = tablas["pagos"]
    mes_ult = pg["mes"].max()
    X["dias_atraso"] = pg[pg["mes"] == mes_ult].set_index("cliente_id")["dias_atraso"].reindex(idx).fillna(0).to_numpy()
    X["meses_con_atraso_90d"] = pg[pg["dias_atraso"] > 0].groupby("cliente_id").size().reindex(idx).fillna(0).to_numpy()
    X["bajo_plan_90d"] = (
        pg[pg["cambio_plan"] == "baja"].groupby("cliente_id").size().reindex(idx).fillna(0).clip(upper=1).to_numpy()
    )

    # ---------------- Interacciones
    it = tablas["interacciones"][tablas["interacciones"]["fecha"] <= hoy]
    i30 = it[it["fecha"] >= c30]
    X["reclamos_cobro_90d"] = it[it["motivo"] == "cobro"].groupby("cliente_id").size().reindex(idx).fillna(0).to_numpy()
    X["llamadas_30d"] = i30.groupby("cliente_id").size().reindex(idx).fillna(0).to_numpy()
    X["llamadas_sin_resolver_30d"] = (
        i30[i30["resuelto"] == 0].groupby("cliente_id").size().reindex(idx).fillna(0).to_numpy()
    )
    X["llamadas_red_30d"] = i30[i30["motivo"] == "red"].groupby("cliente_id").size().reindex(idx).fillna(0).to_numpy()
    X["llamadas_equipo_30d"] = (
        i30[i30["motivo"] == "equipo"].groupby("cliente_id").size().reindex(idx).fillna(0).to_numpy()
    )
    X["tickets_abiertos"] = it.groupby("cliente_id")["ticket_abierto"].sum().reindex(idx).fillna(0).to_numpy()
    X["horas_resolucion_prom"] = it.groupby("cliente_id")["horas_resolucion"].mean().reindex(idx).fillna(0).to_numpy()
    enc = (
        tablas["encuestas"][tablas["encuestas"]["fecha"] <= hoy]
        .sort_values("fecha")
        .groupby("cliente_id")["nps"]
        .last()
    )
    X["nps_ultimo"] = enc.reindex(idx).astype(float).to_numpy()

    # ---------------- Perfil
    X["antiguedad_meses"] = cl["antiguedad_meses"].to_numpy()
    X["arpu"] = cl["arpu"].to_numpy()
    X["gama_ord"] = cl["gama_dispositivo"].map({"baja": 0, "media": 1, "alta": 2, "módem": 1}).to_numpy()
    seg = cl["segmento"].to_numpy()
    X["es_prepago"] = (seg == "prepago").astype(int)
    X["es_pospago"] = (seg == "pospago").astype(int)
    X["es_hogar"] = (seg == "hogar").astype(int)

    return X[NUMERICAS].astype(float)


def cargar_tablas(engine) -> dict[str, pd.DataFrame]:
    nombres = [
        "clientes",
        "celdas",
        "red_diaria",
        "fallas_masivas",
        "uso_semanal",
        "pagos",
        "interacciones",
        "encuestas",
        "telemetria",
    ]
    return {t: pd.read_sql_table(t, engine) for t in nombres}
