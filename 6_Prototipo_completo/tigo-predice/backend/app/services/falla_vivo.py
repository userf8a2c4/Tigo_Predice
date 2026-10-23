"""Escenario "Falla en vivo" para la demo (~90 s).

Devuelve TODO el escenario de una vez (el frontend lo anima): sitio caído, afectados con su grupo
(tratamiento/control por hash), mensajes de ejemplo, línea de tiempo de llamadas por 1,000 afectados
y KPIs con rangos. Es determinista y NO modifica ningún estado: correrlo N veces da lo mismo.
"""

from __future__ import annotations

import math
from datetime import date, timedelta

import numpy as np

from backend.app.privacidad import nombre_corto
from backend.app.services import bitacora, mensajes
from backend.app.services.roi import L, rango, sig
from experimento import asignacion
from ml import eventos
from ml.comun import supuesto

HORA_INICIO = 19  # 7 p. m.: la historia de la clienta que trabaja desde casa
ETA_HORAS = 4
CAUSA = "Falla de energía comercial en 3 sitios"
HORAS = [0, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 18, 24, 36, 48, 60, 72]
MEDIA_HORAS_LLAMADA = 5.0  # las llamadas se concentran en las primeras horas


def _sitio(estado) -> list[str]:
    """Celda urbana con más clientes de la ciudad piloto + sus 2 vecinas más cercanas."""
    cel = estado.celdas[estado.celdas["ciudad"] == estado.cfg["piloto"]["ciudad"]].copy()
    n = estado.tablas["clientes"].groupby("celda_id").size()
    cel["clientes"] = cel["celda_id"].map(n).fillna(0)
    centro = cel[cel["zona"] == "urbana"].sort_values(["clientes", "celda_id"], ascending=[False, True]).iloc[0]
    cel["dist"] = np.hypot(cel["lat"] - centro["lat"], cel["lon"] - centro["lon"])
    return list(cel.sort_values(["dist", "celda_id"])["celda_id"].iloc[:3])


def _cdf(h: float) -> float:
    return (1 - math.exp(-h / MEDIA_HORAS_LLAMADA)) / (1 - math.exp(-72 / MEDIA_HORAS_LLAMADA))


def escenario(estado) -> dict:
    cfg, pc = estado.cfg, estado.cfg["piloto"]
    celdas_ids = _sitio(estado)
    cl = estado.tablas["clientes"]
    afect = cl[cl["celda_id"].isin(celdas_ids)].sort_values("cliente_id")
    fm = estado.fallas
    previas = [(set(c.split(",")), date.fromisoformat(i)) for c, i in zip(fm["celdas"], fm["inicio"], strict=True)]
    X = eventos.construir(
        afect,
        estado.celdas.set_index("celda_id")["zona"],
        estado.tablas["interacciones"],
        estado.tablas["encuestas"],
        estado.tablas["red_diaria"],
        previas,
        estado.hoy + timedelta(days=1),
        estado.hoy,
        ETA_HORAS,
        len(celdas_ids),
        HORA_INICIO,
    )
    p = estado.modelo72.predict_proba(X[eventos.VARIABLES_EVENTO])[:, 1]
    control = asignacion.asignar(afect["cliente_id"], pc["sal_asignacion"], pc["pct_control"])

    llpc = supuesto(cfg, "llamadas_por_cliente_que_llama")
    entrega = supuesto(cfg, "tasa_entrega")
    red = {n: supuesto(cfg, "reduccion_con_aviso", n) for n in ("bajo", "base", "alto")}
    por_1000_sin = float(p.mean() * llpc * 1000)
    por_1000_con = por_1000_sin * (1 - red["base"] * entrega)
    linea = [
        {"hora": h, "control": round(por_1000_sin * _cdf(h), 1), "tratados": round(por_1000_con * _cdf(h), 1)}
        for h in HORAS
    ]

    # Escala real: una falla típica de la ciudad piloto (supuesto), no solo la muestra sintética
    n_real = supuesto(cfg, "afectados_por_falla")
    trat_real = n_real * (1 - pc["pct_control"])
    costo_llamada = supuesto(cfg, "costo_por_llamada")
    evitadas = {k: trat_real * por_1000_sin / 1000 * v * entrega for k, v in red.items()}
    costo_accion = trat_real * pc["mensajes_por_afectado"] * supuesto(cfg, "costo_whatsapp_mensaje")
    n_comp = int(round(n_real * supuesto(cfg, "pct_compensados")))
    costo_comp = n_comp * supuesto(cfg, "costo_compensacion")
    costo_total = costo_accion + costo_comp
    ahorro = {k: v * costo_llamada for k, v in evitadas.items()}
    fallas_mes = supuesto(cfg, "fallas_mes_piloto")

    # Prioridad para compensación (acción cara): el modelo elige al 5 % con más probabilidad de llamar
    orden = np.argsort(-p, kind="stable")
    k = max(1, int(round(len(p) * supuesto(cfg, "pct_compensados"))))
    prioridad_ids = set(afect["cliente_id"].to_numpy()[orden[:k]])

    # Mensajes de ejemplo (plantilla o IA con guardrails) a dos clientes tratados con WhatsApp
    tratados = afect[~control & (afect["canal_preferido"] == "WhatsApp")]
    c1, c2 = tratados.iloc[0].to_dict(), tratados.iloc[1].to_dict()
    falla = {"eta_horas": ETA_HORAS, "causa_publica": CAUSA}
    ejemplos = []
    for etiqueta, cli, accion, f in (
        ("Aviso (el NOC tiene hora estimada)", c1, "aviso_falla", falla),
        ("Aviso (el NOC aún no tiene hora)", c2, "aviso_falla", {"eta_horas": None, "causa_publica": CAUSA}),
        ("Cierre al restablecer el servicio", c1, "cierre_falla", falla),
    ):
        ctx = mensajes.contexto_mensaje(cli, accion, f)
        msg = mensajes.generar(ctx, estado.llm)
        bitacora.registrar(cli["cliente_id"], accion, msg)
        ejemplos.append(
            {
                "etiqueta": etiqueta,
                "cliente": nombre_corto(cli["nombre"]),
                "telefono": cli["telefono"],
                "texto": msg["texto"],
                "fuente": msg["fuente"],
                "guardrails": msg["guardrails"],
                "version_prompt": msg["version_prompt"],
            }
        )

    lat_c = float(estado.celdas.set_index("celda_id").loc[celdas_ids, "lat"].mean())
    lon_c = float(estado.celdas.set_index("celda_id").loc[celdas_ids, "lon"].mean())
    radio_km = max(1.5, float(np.hypot(afect["lat"] - lat_c, afect["lon"] - lon_c).max() * 111))
    return {
        "ciudad": pc["ciudad"],
        "sitio": {
            "celdas": celdas_ids,
            "lat": lat_c,
            "lon": lon_c,
            "radio_km": round(radio_km, 1),
            "causa": CAUSA,
            "causa_cliente": mensajes.causa_simple(CAUSA),
            "hora_inicio": HORA_INICIO,
            "eta_horas": ETA_HORAS,
        },
        "muestra": {
            "afectados": int(len(afect)),
            "tratamiento": int((~control).sum()),
            "control": int(control.sum()),
            "pct_control": pc["pct_control"],
            "puntos": [
                {
                    "lat": round(float(a), 5),
                    "lon": round(float(b), 5),
                    "grupo": "control" if c else "tratamiento",
                    "prioridad": i in prioridad_ids,
                }
                for a, b, c, i in zip(afect["lat"], afect["lon"], control, afect["cliente_id"], strict=True)
            ],
        },
        "mensajes": ejemplos,
        "linea_tiempo": linea,
        "por_1000": {"sin_aviso": round(por_1000_sin), "con_aviso": round(por_1000_con)},
        "kpis": {
            "afectados_reales": int(n_real),
            "llamadas_sin_aviso": int(sig(n_real * por_1000_sin / 1000)),
            "llamadas_evitadas": {k: int(round(v)) for k, v in evitadas.items()},
            "llamadas_evitadas_texto": f"{sig(evitadas['bajo']):,.0f} a {sig(evitadas['alto']):,.0f}",
            "ahorro": {k: round(v) for k, v in ahorro.items()},
            "ahorro_texto": rango(ahorro["bajo"], ahorro["alto"]),
            "costo_accion": round(costo_total),
            "costo_accion_texto": L(costo_total),
            "compensados_por_modelo": n_comp,
            "neto": {k: round(v - costo_total) for k, v in ahorro.items()},
            "neto_texto": rango(ahorro["bajo"] - costo_total, ahorro["alto"] - costo_total),
            "supuestos": f"Escala de una falla típica ({n_real:,.0f} afectados, supuesto), reducción "
            f"{red['bajo']:.0%}–{red['alto']:.0%}, entrega {entrega:.0%}, {L(costo_llamada)} por llamada.",
        },
        "frase_final": f"Esto fue una falla. {pc['ciudad']} tiene ~{fallas_mes:.0f} al mes (supuesto): "
        f"≈ {sig(evitadas['base'] * fallas_mes):,.0f} llamadas evitadas al mes.",
        "aviso": "Datos simulados — supuestos a validar con Tigo.",
    }
