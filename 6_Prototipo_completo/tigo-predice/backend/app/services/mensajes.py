"""Generador de mensajes proactivos (WhatsApp/SMS) con LLM + plantillas + guardrails.

Reglas para todo mensaje:
  - máximo 300 caracteres, trato de usted, español hondureño cercano
  - nunca prometer lo que no se puede cumplir ni inventar tiempos de reparación
  - nunca revelar datos internos (riesgo, probabilidades, modelos) ni pedir datos sensibles
  - siempre con opción de hablar con una persona (palabra clave AGENTE)
"""

from __future__ import annotations

import json
import re

from backend.app.llm_client import ClienteLLM

MAX_CARACTERES = 300
PROMPT_VERSION = "v03-2026-10-14"

# Causas técnicas del NOC → lenguaje simple para el cliente
CAUSAS_SIMPLES = [
    ("energía", "un corte de energía"),
    ("fibra", "un daño en la fibra óptica"),
    ("lluvia", "las lluvias"),
    ("tormenta", "el mal tiempo"),
    ("robo", "un daño en una antena"),
    ("equipo", "una falla en un equipo de la red"),
]


def causa_simple(causa: str | None) -> str:
    texto = (causa or "").lower()
    for clave, simple in CAUSAS_SIMPLES:
        if clave in texto:
            return simple
    return "una falla en la red"


OFERTAS = {
    "prepago": "10 GB extra cada mes por 3 meses",
    "pospago": "20 % de descuento en su plan por 3 meses",
    "hogar": "el doble de velocidad por 3 meses",
}

PALABRAS_CLAVE = {
    "aviso_falla": ["1", "AGENTE"],
    "cierre_falla": ["1", "AGENTE"],
    "autodiagnostico": ["1", "AGENTE"],
    "hogar_remoto": ["1", "AGENTE"],
    "hogar_visita": ["1", "AGENTE"],
    "oferta_retencion": ["SÍ", "AGENTE"],
    "retencion_agente": ["AGENTE"],
    "recordatorio_pago": ["PAGAR", "PLAZO", "AGENTE"],
}

PROHIBIDAS = re.compile(
    r"riesgo|probab|churn|puntaje|score|modelo predictivo|algoritmo|contraseña|\bpin\b|"
    r"abandon|portabilidad",
    re.IGNORECASE,
)
TIEMPO = re.compile(r"(\d+)\s*(h\b|hr|hrs|hora|horas|min|minuto|minutos)", re.IGNORECASE)
NUMERO_LARGO = re.compile(r"\d{7,}")
# Trato de "tú" (prohibido: siempre "usted")
TUTEO = re.compile(
    # solo formas inequívocas de "tú" ("escribe"/"llama" también son de tercera persona: "le escribe Tigo")
    r"\b(tú|tu|tus|ti|te|contigo|tienes|puedes|quieres|necesitas|estás|eres|contáctanos|escríbenos|"
    r"llámanos|avísanos|respóndenos|recibiste|tuviste|reinícialo|revísalo)\b",
    re.IGNORECASE,
)
# Pedir datos sensibles (prohibido)
DATO_SENSIBLE = re.compile(
    r"contraseña|\bclave\b|\bpin\b|tarjeta|\bcvv\b|número de identidad|\bdni\b|cuenta bancaria|"
    r"código de verificación|código que le llegó",
    re.IGNORECASE,
)
UNO = re.compile(r"(?<!\d)1(?!\d)")
# Enlaces: un mensaje proactivo nunca lleva links (vector clásico de phishing), salvo dominios oficiales
ENLACE = re.compile(
    r"https?://\S+|www\.\S+|\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|info|xyz|io|ly|co|me|biz|top|hn|app|link)\b\S*",
    re.IGNORECASE,
)
DOMINIOS_OFICIALES = ("tigo.com.hn", "tigomoney.hn")
NOMBRE_SEGURO = re.compile(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]")


def nombre_seguro(nombre: str) -> str:
    """Solo letras y máximo 20: un nombre del CRM no puede colar instrucciones al LLM ni al mensaje."""
    primero = str(nombre).split()[0] if str(nombre).split() else ""
    return NOMBRE_SEGURO.sub("", primero)[:20] or "cliente"


SISTEMA = """Eres el asistente de mensajería de Tigo Honduras. Escribes UN solo mensaje de WhatsApp para un cliente.
Reglas obligatorias:
- Máximo 280 caracteres. Trato de usted. Español hondureño cercano, cálido y respetuoso. Sin jerga técnica.
- Usa SOLO los datos que se te dan. No inventes tiempos de reparación, montos, beneficios ni fechas.
- Si no se te da un tiempo estimado, no menciones horas ni minutos.
- Nunca menciones riesgo, probabilidades, modelos, análisis internos ni que el cliente podría irse.
- Nunca pidas contraseñas, PIN, códigos, tarjetas ni datos personales.
- Nunca uses "tú": siempre "usted" (le, su, responda).
- Incluye exactamente las palabras clave de respuesta indicadas, en MAYÚSCULAS.
- Siempre ofrece hablar con una persona respondiendo AGENTE.
- Puedes usar como máximo un emoji.
Devuelve solo el texto del mensaje, sin comillas ni explicaciones."""


# Qué pasó, en palabras simples, para que la IA redacte sin inventar (frente Hogar)
SITUACIONES = {
    "hogar_remoto": "Detectamos inestabilidad en el internet de hogar del cliente y ya la corregimos a distancia, "
    "antes de que tuviera que llamar.",
    "hogar_visita": "La señal del internet de hogar del cliente se está debilitando; queremos que un técnico la "
    "revise antes de que le afecte. El cliente decide si agenda la visita.",
}


def contexto_mensaje(c: dict, accion: str, falla: dict | None = None, gb: int = 0) -> dict:
    return {
        "situacion": SITUACIONES.get(accion),
        "nombre": nombre_seguro(c["nombre"]),
        "ciudad": c["ciudad"],
        "segmento": c["segmento"],
        "plan": c["plan"],
        "accion": accion,
        "eta_horas": (falla or {}).get("eta_horas"),
        "causa_falla": causa_simple((falla or {}).get("causa_publica")) if falla else None,
        "gb_regalo": gb,
        "oferta": OFERTAS.get(c["segmento"]),
        "dias_atraso": int(c.get("dias_atraso") or 0),
    }


def plantilla(ctx: dict) -> str:
    n, a = ctx["nombre"], ctx["accion"]
    if a == "aviso_falla":
        causa = ctx.get("causa_falla") or "una falla en la red"
        eta = (
            f"Estimamos restablecerlo en unas {int(ctx['eta_horas'])} horas; no necesita llamar."
            if ctx.get("eta_horas")
            else "Ya trabajamos en ello y le avisaremos al restablecerse."
        )
        regalo = f" Le acreditamos {ctx['gb_regalo']} GB de regalo." if ctx.get("gb_regalo") else ""
        return (
            f"Hola {n}, le escribe Tigo. Su servicio en {ctx['ciudad']} tiene una falla por {causa}. "
            f"{eta}{regalo} Si es otro problema, responda 1 para revisar su equipo o AGENTE para hablar "
            f"con una persona."
        )
    if a == "cierre_falla":
        return (
            f"Hola {n}, su servicio de Tigo en {ctx['ciudad']} ya se restableció. Gracias por su paciencia. "
            f"Si algo no funciona, responda 1 para revisar su equipo o AGENTE para hablar con una persona."
        )
    if a == "hogar_remoto":
        return (
            f"Hola {n}, le escribe Tigo. Detectamos inestabilidad en su internet de hogar y ya la corregimos "
            f"a distancia, sin que tuviera que llamar. Si aún nota fallas, responda 1 para revisarlo juntos o "
            f"AGENTE para hablar con una persona."
        )
    if a == "hogar_visita":
        return (
            f"Hola {n}, le escribe Tigo. Detectamos que la señal de su internet de hogar se está debilitando y "
            f"queremos resolverlo antes de que le afecte. Responda 1 para agendar la visita de un técnico o "
            f"AGENTE para hablar con una persona."
        )
    if a == "autodiagnostico":
        return (
            f"Hola {n}, le escribe Tigo. Notamos que su conexión está más lenta de lo normal y queremos "
            f"ayudarle a resolverlo ahora mismo, sin llamar. Responda 1 para empezar o AGENTE para "
            f"hablar con una persona."
        )
    if a == "oferta_retencion":
        return (
            f"Hola {n}, gracias por confiar en Tigo 💙. Queremos agradecer su preferencia con "
            f"{ctx['oferta']}, sin costo adicional. Responda SÍ para activarlo o AGENTE para hablar "
            f"con una persona."
        )
    if a == "retencion_agente":
        return (
            f"Hola {n}, le escribe Tigo. Un asesor especializado le llamará hoy para conversar sobre "
            f"su servicio y un beneficio exclusivo para usted. Si prefiere hablar ya con una persona, "
            f"responda AGENTE."
        )
    if a == "recordatorio_pago":
        return (
            f"Hola {n}, le escribe Tigo 😊. Le recordamos que su factura tiene un saldo pendiente. "
            f"Puede pagar en segundos con Tigo Money o pedir un arreglo de pago. Responda PAGAR, "
            f"PLAZO o AGENTE para hablar con una persona."
        )
    raise ValueError(f"La acción {a} no envía mensajes")


def validar(texto: str, ctx: dict) -> list[str]:
    """Devuelve la lista de problemas (vacía = el mensaje es seguro de enviar)."""
    problemas = []
    if len(texto) > MAX_CARACTERES:
        problemas.append(f"supera {MAX_CARACTERES} caracteres")
    if PROHIBIDAS.search(texto):
        problemas.append("menciona información interna o sensible")
    if DATO_SENSIBLE.search(texto):
        problemas.append("pide datos sensibles")
    if TUTEO.search(texto):
        problemas.append("tutea al cliente (debe usar usted)")
    if NUMERO_LARGO.search(texto):
        problemas.append("contiene un número largo (posible dato sensible)")
    if any(not any(d in m.group(0).lower() for d in DOMINIOS_OFICIALES) for m in ENLACE.finditer(texto)):
        problemas.append("contiene un enlace no oficial (posible phishing)")
    for m in TIEMPO.finditer(texto):
        if not ctx.get("eta_horas") or int(m.group(1)) != int(ctx["eta_horas"]):
            problemas.append("promete un tiempo que no viene del NOC")
            break
    for clave in PALABRAS_CLAVE.get(ctx["accion"], []):
        if clave == "1":
            ok = bool(UNO.search(texto))
        else:
            ok = any(v in texto for v in (clave, clave.replace("Í", "I")))
        if not ok:
            problemas.append(f"falta la palabra clave {clave}")
    if "AGENTE" not in texto:
        problemas.append("no ofrece hablar con una persona")
    return problemas


def generar(ctx: dict, llm: ClienteLLM | None = None) -> dict:
    """Genera el mensaje con Claude si está disponible; si no, o si falla un guardrail, usa plantilla."""
    base = plantilla(ctx)
    if llm is not None and llm.activo:
        datos = {k: v for k, v in ctx.items() if v not in (None, 0, "")}
        pedido = (
            f"Datos del caso (JSON): {json.dumps(datos, ensure_ascii=False)}\n"
            f"Palabras clave obligatorias: {', '.join(PALABRAS_CLAVE[ctx['accion']])}\n"
            f"Ejemplo de tono (no lo copies literal): {base}"
        )
        texto = llm.completar(SISTEMA, pedido)
        if texto:
            texto = texto.strip().strip('"')
            problemas = validar(texto, ctx)
            if not problemas:
                return {"texto": texto, "fuente": "claude", "guardrails": "aprobado", "version_prompt": PROMPT_VERSION}
            return {
                "texto": base,
                "fuente": "plantilla",
                "guardrails": f"texto de IA descartado: {', '.join(problemas)}",
                "version_prompt": PROMPT_VERSION,
            }
    return {"texto": base, "fuente": "plantilla", "guardrails": "aprobado", "version_prompt": PROMPT_VERSION}
