"""Guardrails de los mensajes al cliente (más de 20 casos).

Reglas: máx. 300 caracteres · trato de usted · no inventar horas de solución · no pedir datos sensibles ·
no revelar datos internos · siempre opción de hablar con una persona (AGENTE).
"""

import pytest

from backend.app.services import mensajes

CIUDADES_LARGAS = ["San Pedro Sula", "Santa Rosa de Copán", "Tegucigalpa"]
CAUSAS = [
    "Falla de energía comercial en sitios",
    "Corte de fibra óptica",
    "Lluvias intensas dañaron enlaces",
    "Robo de baterías en un sitio",
    "Falla de equipo de transmisión",
    "Causa no informada",
]


def _ctx(accion, segmento="hogar", ciudad="San Pedro Sula", eta=4, causa=CAUSAS[0], gb=0):
    c = {"nombre": "María López Paz", "ciudad": ciudad, "segmento": segmento, "plan": "Plan", "dias_atraso": 0}
    falla = {"eta_horas": eta, "causa_publica": causa}
    return mensajes.contexto_mensaje(c, accion, falla if accion in ("aviso_falla", "cierre_falla") else None, gb)


# ---------------------------------------------------------- plantillas: todas las combinaciones válidas
@pytest.mark.parametrize("accion", ["aviso_falla", "cierre_falla"])
@pytest.mark.parametrize("ciudad", CIUDADES_LARGAS)
@pytest.mark.parametrize("eta", [None, 2, 18])
@pytest.mark.parametrize("gb", [0, 2])
def test_plantillas_del_piloto_cumplen(accion, ciudad, eta, gb):
    ctx = _ctx(accion, ciudad=ciudad, eta=eta, gb=gb)
    texto = mensajes.plantilla(ctx)
    assert len(texto) <= mensajes.MAX_CARACTERES
    assert mensajes.validar(texto, ctx) == [], texto


@pytest.mark.parametrize("causa", CAUSAS)
def test_causa_en_lenguaje_simple(causa):
    simple = mensajes.causa_simple(causa)
    assert simple and "transmisión" not in simple and "sitios" not in simple


@pytest.mark.parametrize("accion", ["autodiagnostico", "oferta_retencion", "retencion_agente", "recordatorio_pago"])
@pytest.mark.parametrize("segmento", ["prepago", "pospago", "hogar"])
def test_plantillas_fase2_cumplen(accion, segmento):
    ctx = _ctx(accion, segmento=segmento)
    texto = mensajes.plantilla(ctx)
    assert len(texto) <= mensajes.MAX_CARACTERES
    assert mensajes.validar(texto, ctx) == [], texto


@pytest.mark.parametrize("accion", ["hogar_remoto", "hogar_visita"])
@pytest.mark.parametrize("ciudad", CIUDADES_LARGAS)
def test_plantillas_hogar_cumplen(accion, ciudad):
    ctx = _ctx(accion, ciudad=ciudad)
    texto = mensajes.plantilla(ctx)
    assert len(texto) <= mensajes.MAX_CARACTERES
    assert mensajes.validar(texto, ctx) == [], texto
    assert ctx["situacion"], "la IA recibe qué pasó en palabras simples, para no inventar"
    assert "riesgo" not in texto.lower() and "predic" not in texto.lower()


def test_aviso_sin_hora_del_noc_no_promete_tiempo():
    texto = mensajes.plantilla(_ctx("aviso_falla", eta=None))
    assert "horas" not in texto and "avisaremos" in texto


# ---------------------------------------------------------- textos adversos que debe rechazar
OK = (
    "Hola María, le escribe Tigo. Hay una falla por un corte de energía. Estimamos restablecerlo en unas 4 horas. "
    "Responda 1 para revisar su equipo o AGENTE para hablar con una persona."
)


@pytest.mark.parametrize(
    "texto,problema",
    [
        (OK.replace("4 horas", "2 horas"), "tiempo"),  # hora inventada
        (OK.replace("unas 4 horas", "30 minutos"), "tiempo"),  # minutos inventados
        ("Hola María, tu servicio vuelve pronto. Responde 1 o AGENTE.", "tutea"),  # tuteo
        ("Hola, ¿tienes problemas? Responda 1 o AGENTE.", "tutea"),
        ("Hola, contáctanos si sigue sin señal. Responda 1 o AGENTE.", "tutea"),
        ("Para compensarle, envíenos su PIN. Responda 1 o AGENTE.", "sensible"),  # datos sensibles
        ("Confirme su contraseña de Mi Tigo. Responda 1 o AGENTE.", "sensible"),
        ("Díganos el código que le llegó por SMS. Responda 1 o AGENTE.", "sensible"),
        ("Le reembolsamos: envíe su número de tarjeta. Responda 1 o AGENTE.", "sensible"),
        ("Su riesgo de churn es alto, por eso le escribimos. Responda 1 o AGENTE.", "interna"),  # datos internos
        ("Nuestro algoritmo detectó que podría irse. Responda 1 o AGENTE.", "interna"),
        ("Llame al 22809000 para más ayuda. Responda 1 o AGENTE.", "número largo"),
        ("Hola María, hay una falla en su zona y ya trabajamos en ella. Responda 1.", "persona"),  # sin humano
        (OK + " " + "x" * 120, "300 caracteres"),  # demasiado largo
        ("Hola María, hay una falla en su zona. Responda AGENTE para hablar con alguien.", "palabra clave 1"),
    ],
)
def test_guardrails_rechazan_textos_inseguros(texto, problema):
    problemas = mensajes.validar(texto, _ctx("aviso_falla"))
    assert any(problema in p for p in problemas), problemas


def test_texto_correcto_pasa():
    assert mensajes.validar(OK, _ctx("aviso_falla")) == []


class LLMFalso:
    activo = True

    def __init__(self, respuesta):
        self.respuesta = respuesta

    def completar(self, *_a, **_k):
        return self.respuesta


@pytest.mark.parametrize(
    "salida_llm",
    [
        "Hola María, tu internet vuelve en 1 hora. Responde AGENTE.",
        "Envíe su PIN para compensarle. Responda 1 o AGENTE.",
        "",
        None,
    ],
)
def test_salida_mala_del_llm_cae_a_plantilla(salida_llm):
    ctx = _ctx("aviso_falla")
    r = mensajes.generar(ctx, LLMFalso(salida_llm))
    assert r["fuente"] == "plantilla"
    assert r["texto"] == mensajes.plantilla(ctx)
    assert r["version_prompt"] == mensajes.PROMPT_VERSION


def test_salida_buena_del_llm_se_usa_y_registra_version():
    r = mensajes.generar(_ctx("aviso_falla"), LLMFalso(OK))
    assert r["fuente"] == "claude" and r["version_prompt"] == mensajes.PROMPT_VERSION
