"""Tests de los servicios (sin base de datos)."""

import math
from datetime import date

import pytest

from backend.app.services import acciones, chat, mensajes
from ml import features
from ml.comun import cargar_config

CFG = cargar_config()
HOY = date(2026, 10, 12)


# ----------------------------------------------------------------- Mensajes (más casos en test_guardrails.py)
CLIENTE = {
    "nombre": "María López Paz",
    "ciudad": "San Pedro Sula",
    "segmento": "hogar",
    "plan": "Internet Hogar 50 Mbps",
    "dias_atraso": 0,
}


class LLMFalso:
    activo = True

    def __init__(self, respuesta):
        self.respuesta = respuesta

    def completar(self, *_a, **_k):
        return self.respuesta


def test_llm_con_texto_inseguro_cae_a_plantilla():
    ctx = mensajes.contexto_mensaje(CLIENTE, "oferta_retencion")
    r = mensajes.generar(ctx, LLMFalso("Vemos que su probabilidad de irse es alta. Responda SÍ o AGENTE"))
    assert r["fuente"] == "plantilla" and "descartado" in r["guardrails"]


def test_llm_con_texto_valido_se_usa():
    ctx = mensajes.contexto_mensaje(CLIENTE, "oferta_retencion")
    r = mensajes.generar(
        ctx,
        LLMFalso(
            "Hola María 💙, tiene el doble de velocidad por 3 meses de regalo. "
            "Responda SÍ para activarlo o AGENTE para hablar con alguien."
        ),
    )
    assert r["fuente"] == "claude"


def test_sin_llm_usa_plantilla():
    ctx = mensajes.contexto_mensaje(CLIENTE, "autodiagnostico")
    assert mensajes.generar(ctx, None)["fuente"] == "plantilla"


# ----------------------------------------------------------------- Next Best Action
def _c(**kw):
    base = {
        "opt_out": 0,
        "ultimo_contacto_proactivo": None,
        "falla_masiva_activa": 0,
        "brecha_velocidad_celda": 0.0,
        "prob_incidencia": 0.05,
        "prob_churn": 0.02,
        "prioridad": "Baja",
        "clv": 3000,
        "dias_atraso": 0,
        "tendencia_uso": 0.0,
        "caidas_7d": 0,
    }
    return {**base, **kw}


@pytest.mark.parametrize(
    "cliente,esperado",
    [
        (_c(opt_out=1, falla_masiva_activa=1), "no_contactar"),
        (_c(ultimo_contacto_proactivo="2026-10-10", falla_masiva_activa=1), "esperar"),
        (_c(ultimo_contacto_proactivo=float("nan"), falla_masiva_activa=1), "aviso_falla"),
        (_c(brecha_velocidad_celda=-0.4, prob_incidencia=0.5), "autodiagnostico"),
        (_c(prioridad="Alta", prob_churn=0.4, clv=20000), "retencion_agente"),
        (_c(prioridad="Alta", prob_churn=0.4, clv=2000), "oferta_retencion"),
        (_c(prioridad="Media", dias_atraso=20, tendencia_uso=-0.4), "recordatorio_pago"),
        (_c(), "no_molestar"),
        (_c(prioridad="Media"), "monitorear"),
    ],
)
def test_decidir_accion(cliente, esperado):
    assert acciones.decidir(cliente, CFG, HOY)[0] == esperado


def test_regla_antifatiga_vence_a_los_7_dias():
    assert (
        acciones.decidir(_c(ultimo_contacto_proactivo="2026-10-04", falla_masiva_activa=1), CFG, HOY)[0]
        == "aviso_falla"
    )


# ----------------------------------------------------------------- Chat
@pytest.mark.parametrize(
    "texto,intencion",
    [
        ("¿Y a qué hora vuelve el servicio?", "estado"),
        ("¡Listo! Ya funciona 🙌", "funciona"),
        ("No funciona todavía", "sigue_mal"),
        ("quiero hablar con un agente", "agente"),
        ("SÍ, me interesa", "si"),
        ("2", "sigue_mal"),
        ("PAGAR", "pagar"),
    ],
)
def test_detectar_intencion(texto, intencion):
    assert chat.detectar_intencion(texto) == intencion


def test_autodiagnostico_escala_a_ticket_si_no_se_resuelve():
    ctx = mensajes.contexto_mensaje(CLIENTE, "autodiagnostico")
    conv = {"accion": "autodiagnostico", "estado": "abierta", "paso": 0}
    for texto in ("1", "Sigue igual", "Sigue igual"):
        r = chat.responder(conv, chat.detectar_intencion(texto), ctx)
        conv.update(paso=r["paso"], estado=r["estado"])
    assert r["ticket"] and r["estado"] == "escalada"


# ----------------------------------------------------------------- Explicaciones
def test_explicaciones_en_lenguaje_natural():
    assert features.explicar("dias_atraso", 12) == "Pago atrasado 12 días"
    assert features.explicar("llamadas_sin_resolver_30d", 1) == "1 llamada reciente sin resolver"
    assert features.explicar("llamadas_sin_resolver_30d", 3) == "3 llamadas recientes sin resolver"
    assert features.explicar("dias_atraso", 0) is None
    assert features.explicar("nps_ultimo", math.nan) is None
