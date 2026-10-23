"""Asistente de autoservicio por WhatsApp (simulado).

Flujos: estado de la falla, autodiagnóstico guiado, aceptar oferta, pagar, pedir agente.
La intención se detecta con palabras clave; si hay LLM disponible, Claude clasifica el texto libre.
Si no se resuelve, se crea un ticket con el resumen YA escrito para el agente.
"""

from __future__ import annotations

import unicodedata

from backend.app.llm_client import ClienteLLM
from backend.app.privacidad import redactar

INTENCIONES = ("agente", "si", "no", "empezar", "funciona", "sigue_mal", "estado", "pagar", "plazo", "gracias")

_CLAVES = [
    ("agente", ["AGENTE", "PERSONA", "ASESOR", "HUMANO", "OPERADOR"]),
    ("pagar", ["PAGAR", "PAGO"]),
    ("plazo", ["PLAZO", "ARREGLO", "CUOTAS"]),
    ("estado", ["CUANDO", "HORA", "ESTADO", "VUELVE", "QUE PASO", "CUANTO FALTA"]),
    ("sigue_mal", ["SIGUE", "NO FUNCIONA", "IGUAL", "LENTO", "TODAVIA", "NADA"]),
    ("funciona", ["YA FUNCIONA", "FUNCIONA", "LISTO", "RESUELTO", "YA SIRVE", "YA ESTA"]),
    ("no", ["NO GRACIAS", "NO ME INTERESA"]),
    ("si", ["SI", "ACEPTO", "ME INTERESA", "DALE", "CLARO", "OK"]),
    ("gracias", ["GRACIAS", "MUY AMABLE"]),
]


def _normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto.upper())
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return " ".join("".join(ch if ch.isascii() and ch.isalnum() else " " for ch in t).split())


def detectar_intencion(texto: str, llm: ClienteLLM | None = None) -> str:
    t = _normalizar(texto)
    if t in ("1",):
        return "empezar_o_funciona"
    if t in ("2",):
        return "sigue_mal"
    if t == "NO":
        return "no"
    for intencion, claves in _CLAVES:
        if any(f" {c} " in f" {t} " for c in claves):
            return intencion
    if llm is not None and llm.activo:
        r = llm.completar(
            "Clasifica la intención del mensaje de un cliente de Tigo Honduras. Responde SOLO una palabra de "
            f"esta lista: {', '.join(INTENCIONES)}, otro.",
            redactar(texto),
            max_tokens=1000,
        )
        if r and r.strip().lower() in INTENCIONES:
            return r.strip().lower()
    return "otro"


def _pasos_autodiagnostico(segmento: str) -> list[str]:
    if segmento == "hogar":
        return [
            "Paso 1 de 2: desconecte su módem de la corriente, espere 30 segundos y vuelva a conectarlo. "
            "Cuando las luces estén fijas, pruebe su internet. Responda 1 si ya funciona o 2 si sigue igual.",
            "Paso 2 de 2: acabamos de reiniciar su módem de forma remota y actualizar su configuración. "
            "Espere 2 minutos y pruebe de nuevo. Responda 1 si ya funciona o 2 si sigue igual.",
        ]
    return [
        "Paso 1 de 2: active el modo avión 10 segundos y luego desactívelo. Pruebe navegar. "
        "Responda 1 si ya funciona o 2 si sigue igual.",
        "Paso 2 de 2: le enviamos la configuración de internet (APN) actualizada. Acéptela y reinicie su "
        "teléfono. Responda 1 si ya funciona o 2 si sigue igual.",
    ]


def responder(conv: dict, intencion: str, ctx: dict) -> dict:
    """Aplica la intención a la conversación.

    Devuelve {"respuestas": [...], "resultado": str|None, "ticket": bool, "paso": int, "estado": str}
    """
    nombre, accion, paso = ctx["nombre"], conv["accion"], conv.get("paso", 0)
    salida = {"respuestas": [], "resultado": None, "ticket": False, "paso": paso, "estado": conv["estado"]}

    def cerrar(texto: str, resultado: str, estado: str = "resuelta"):
        salida.update(respuestas=[texto], resultado=resultado, estado=estado)
        return salida

    if conv["estado"] != "abierta":
        salida["respuestas"] = [f"¡Con gusto, {nombre}! Si necesita algo más, aquí estamos. 💙"]
        return salida

    if intencion == "agente":
        salida.update(
            ticket=True,
            estado="escalada",
            resultado="ticket",
            respuestas=[
                "Le comunico con un asesor. Ya tiene todo su caso, no tendrá que repetir nada. En breve le atienden. 🙌"
            ],
        )
        return salida

    if accion == "hogar_visita":
        if intencion in ("empezar_o_funciona", "si", "empezar"):
            return cerrar(
                f"¡Listo, {nombre}! ✅ Un técnico le contactará para coordinar el día. Llegará con el diagnóstico "
                f"de su módem, así se resuelve en una sola visita.",
                "visita_agendada",
            )
        if intencion == "no":
            return cerrar(
                "Entendido. Seguiremos pendientes de su servicio; si nota fallas, escríbanos aquí.", "sin_accion"
            )

    if accion in ("aviso_falla", "cierre_falla", "hogar_remoto") and intencion == "empezar_o_funciona":
        # "1" = el cliente cree que su problema es otro: pasa a autodiagnóstico guiado
        conv["accion"] = "autodiagnostico"
        salida.update(paso=1, respuestas=[_pasos_autodiagnostico(ctx["segmento"])[0]])
        return salida

    if accion == "aviso_falla":
        if intencion in ("estado", "sigue_mal", "otro"):
            eta = (
                f"El equipo técnico estima restablecerlo en unas {int(ctx['eta_horas'])} horas."
                if ctx.get("eta_horas")
                else "El equipo técnico sigue trabajando."
            )
            salida["respuestas"] = [
                f"La falla en {ctx['ciudad']} sigue en reparación. {eta} Le escribiremos "
                f"apenas se restablezca, no necesita llamar. Si desea, responda AGENTE."
            ]
            return salida
        return cerrar(
            f"¡Gracias por su paciencia, {nombre}! Le avisaremos por aquí cuando el servicio vuelva. 💙",
            "llamada_evitada",
        )

    if accion == "autodiagnostico":
        pasos = _pasos_autodiagnostico(ctx["segmento"])
        if paso == 0:
            if intencion in ("empezar_o_funciona", "si", "empezar", "sigue_mal", "otro"):
                salida.update(paso=1, respuestas=[pasos[0]])
                return salida
        elif intencion in ("empezar_o_funciona", "funciona", "gracias", "si"):
            return cerrar(
                f"¡Excelente, {nombre}! 🎉 Su servicio quedó funcionando. Nos alegra haberle ayudado "
                f"sin que tuviera que llamar.",
                "llamada_evitada",
            )
        elif intencion in ("sigue_mal", "no", "otro"):
            if paso == 1:
                salida.update(paso=2, respuestas=[pasos[1]])
                return salida
            salida.update(
                ticket=True,
                estado="escalada",
                resultado="ticket",
                respuestas=[
                    "Lamentamos que siga fallando. Creamos su caso con todo lo que ya "
                    "probamos, así nadie le volverá a preguntar lo mismo. Un técnico le "
                    "contactará hoy."
                ],
            )
            return salida

    if accion in ("oferta_retencion", "retencion_agente"):
        if intencion in ("si", "empezar_o_funciona", "funciona", "gracias"):
            return cerrar(f"¡Listo, {nombre}! ✅ Activamos {ctx['oferta']}. Gracias por seguir con Tigo.", "retenido")
        if intencion == "no":
            salida["respuestas"] = [
                "Entendido. Si prefiere, un asesor puede llamarle para buscar la mejor "
                "opción para usted. Responda AGENTE cuando guste."
            ]
            return salida

    if accion == "recordatorio_pago":
        if intencion == "pagar":
            return cerrar(
                "Aquí tiene su enlace seguro de Tigo Money para pagar en segundos: "
                "tigomoney.hn/pagar (demo). ¡Gracias!",
                "pago",
            )
        if intencion == "plazo":
            return cerrar(
                f"Con gusto, {nombre}. Le ofrecemos dividir su saldo en 2 pagos sin recargo. Ya quedó registrado. ✅",
                "arreglo_pago",
            )

    salida["respuestas"] = [
        "Disculpe, no le entendí bien. Puede responder con una de las opciones del "
        "mensaje o escribir AGENTE para hablar con una persona."
    ]
    return salida


def resumen_ticket(c: dict, conv: dict, factores: list[dict]) -> str:
    """Resumen listo para el agente: no tiene que volver a preguntar nada."""
    lineas = [
        f"Cliente: {c['nombre']} · {c['segmento']} · {c['plan']} · {c['ciudad']} (celda {c['celda_id']})",
        f"Motivo del contacto proactivo: {conv['accion_nombre']}",
        "Factores detectados por la IA: " + ("; ".join(f["texto"] for f in factores) or "—"),
        f"Historial: {int(c['llamadas_30d'])} llamadas en 30 días, {int(c['llamadas_sin_resolver_30d'])} sin resolver.",
    ]
    pasos = [m["texto"] for m in conv["mensajes"] if m["de"] == "tigo" and m["texto"].startswith("Paso")]
    if pasos:
        lineas.append(f"Ya realizó {len(pasos)} paso(s) de autodiagnóstico sin éxito.")
    respuestas = [m["texto"] for m in conv["mensajes"] if m["de"] == "cliente"]
    if respuestas:
        lineas.append("Lo que dijo el cliente: " + " | ".join(f"«{r}»" for r in respuestas[-3:]))
    lineas.append(
        "Siguiente paso sugerido: "
        + {
            "autodiagnostico": "agendar visita técnica / cambio de equipo.",
            "hogar_remoto": "revisar la telemetría del módem antes de agendar visita.",
            "hogar_visita": "agendar visita con el diagnóstico de la IA (señal / conector).",
            "aviso_falla": "confirmar tiempo de solución con NOC y ofrecer compensación adicional.",
            "oferta_retencion": "escuchar motivo y ofrecer plan alternativo.",
            "retencion_agente": "llamada de retención con oferta de alto valor.",
            "recordatorio_pago": "ofrecer arreglo de pago.",
        }.get(conv["accion"], "atender la solicitud.")
    )
    return "\n".join(lineas)
