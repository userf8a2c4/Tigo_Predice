"""Motor de acciones (Next Best Action).

Decide automáticamente qué hacer con cada cliente según su riesgo y la causa,
respetando opt-out, la regla anti-fatiga (1 mensaje cada 7 días) y el tope de
presupuesto de compensaciones.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

CATALOGO = {
    "aviso_falla": {
        "nombre": "Aviso proactivo de falla + compensación",
        "descripcion": "Falla masiva en su zona: avisar con tiempo estimado y regalar GB.",
        "canal": "WhatsApp",
        "contacta": True,
        "humano": False,
    },
    "autodiagnostico": {
        "nombre": "Autodiagnóstico guiado",
        "descripcion": "Problema individual de equipo/configuración: guía paso a paso.",
        "canal": "WhatsApp",
        "contacta": True,
        "humano": False,
    },
    "retencion_agente": {
        "nombre": "Llamada de agente especializado + oferta",
        "descripcion": "Alto riesgo de abandono y alto valor: un humano decide la oferta.",
        "canal": "Llamada saliente",
        "contacta": True,
        "humano": True,
    },
    "oferta_retencion": {
        "nombre": "Oferta de retención personalizada",
        "descripcion": "Alto riesgo de abandono: beneficio por 3 meses.",
        "canal": "WhatsApp",
        "contacta": True,
        "humano": False,
    },
    "recordatorio_pago": {
        "nombre": "Recordatorio amable + Tigo Money",
        "descripcion": "Pago atrasado y bajo uso: facilidad de pago.",
        "canal": "WhatsApp",
        "contacta": True,
        "humano": False,
    },
    "monitorear": {
        "nombre": "Monitorear",
        "descripcion": "Riesgo medio sin causa accionable hoy.",
        "canal": "—",
        "contacta": False,
        "humano": False,
    },
    "no_molestar": {
        "nombre": "No molestar",
        "descripcion": "Riesgo bajo: evitar fatiga de mensajes.",
        "canal": "—",
        "contacta": False,
        "humano": False,
    },
    "esperar": {
        "nombre": "Esperar (anti-fatiga)",
        "descripcion": "Ya recibió un mensaje proactivo en los últimos 7 días.",
        "canal": "—",
        "contacta": False,
        "humano": False,
    },
    "no_contactar": {
        "nombre": "No contactar (opt-out)",
        "descripcion": "El cliente pidió no recibir mensajes.",
        "canal": "—",
        "contacta": False,
        "humano": False,
    },
}


def decidir(c: pd.Series | dict, cfg: dict, hoy: date) -> tuple[str, str]:
    """Devuelve (codigo_accion, motivo legible)."""
    r = cfg["reglas"]
    if c["opt_out"]:
        return "no_contactar", "El cliente pidió no recibir mensajes proactivos."
    ultimo = c.get("ultimo_contacto_proactivo")
    if isinstance(ultimo, str) and ultimo:  # puede venir None o NaN desde la base
        dias = (hoy - date.fromisoformat(ultimo[:10])).days
        if dias < r["dias_entre_mensajes"]:
            return (
                "esperar",
                f"Recibió un mensaje hace {dias} día(s); la regla es 1 cada {r['dias_entre_mensajes']} días.",
            )
    if c["falla_masiva_activa"] >= 1:
        return "aviso_falla", "Está en la zona de una falla masiva activa."
    if c["brecha_velocidad_celda"] <= -0.25 and c["prob_incidencia"] >= 0.15:
        return "autodiagnostico", "Su velocidad está muy por debajo de la de sus vecinos: probable falla de equipo."
    if c["prioridad"] == "Alta" and c["prob_churn"] >= 0.15:
        if c["clv"] >= r["valor_alto_clv"]:
            return "retencion_agente", "Alto riesgo de abandono y cliente de alto valor: atiende un humano."
        return "oferta_retencion", "Alto riesgo de abandono."
    if c["caidas_7d"] >= 6 and c["prob_incidencia"] >= 0.3:
        return "aviso_falla", "Intermitencias frecuentes en su zona esta semana."
    if c["dias_atraso"] >= 10 and c["tendencia_uso"] <= -0.2 and c["prioridad"] != "Baja":
        return "recordatorio_pago", "Pago atrasado y consumo a la baja."
    if c["prioridad"] == "Baja":
        return "no_molestar", "Riesgo bajo."
    return "monitorear", "Riesgo medio sin causa accionable hoy."


def asignar(df: pd.DataFrame, cfg: dict, hoy: date) -> pd.DataFrame:
    res = [decidir(row, cfg, hoy) for row in df.to_dict("records")]
    df["accion"] = [a for a, _ in res]
    df["motivo_accion"] = [m for _, m in res]
    return df
