"""Contenido de "Listo para producción" (una sola fuente para la app y docs/listo_para_produccion.md).

No inventa artículos de ley: los puntos regulatorios se listan como temas a validar con Legal de Tigo.
Detalle completo de seguridad y privacidad: docs/seguridad_y_privacidad.md.
"""

from __future__ import annotations

CONSENTIMIENTO = [
    {
        "tema": "Canal",
        "detalle": "WhatsApp Business API (proveedor oficial de Meta) con plantillas de utilidad "
        "aprobadas por Meta, Marca y Legal. SMS como respaldo para quien no usa WhatsApp.",
    },
    {
        "tema": "Opt-in / opt-out",
        "detalle": "Solo clientes con consentimiento para mensajes de servicio. "
        'Cualquier respuesta "BAJA" o "NO" registra el opt-out al instante '
        "y se respeta para siempre.",
    },
    {
        "tema": "Frecuencia",
        "detalle": "Máximo 2 mensajes por falla (aviso + cierre) y 1 mensaje proactivo por semana fuera de fallas.",
    },
    {
        "tema": "Contenido",
        "detalle": "Guardrails automáticos: 300 caracteres, trato de usted, sin pedir datos "
        "sensibles, sin inventar horas de solución y siempre con opción de agente.",
    },
    {
        "tema": "Telemetría del hogar",
        "detalle": "Solo desempeño de la línea y del módem (señal, errores, reinicios, WiFi, nº de dispositivos). "
        "Nunca contenido, navegación, DNS ni datos de los dispositivos del cliente. Finalidad única: atender fallas.",
    },
    {
        "tema": "Acciones remotas",
        "detalle": "Lista cerrada (reinicio programado, canal WiFi, firmware certificado), de madrugada, "
        "por lotes y con reversión. Las ejecuta el ACS por reglas, nunca el modelo de lenguaje. "
        "Validar que el contrato lo permite.",
    },
    {
        "tema": "Regulación de telecomunicaciones",
        "detalle": "Validar con Legal de Tigo los requisitos de CONATEL "
        "sobre comunicación de interrupciones y compensaciones.",
    },
    {
        "tema": "Protección de datos",
        "detalle": "Honduras aún no tiene ley integral (proyecto pendiente desde 2018): se aplica el GDPR "
        "como estándar, más la Constitución (arts. 76, 100 y 182, habeas data) y la política de privacidad de "
        "Millicom. Datos mínimos, seudonimización, cifrado, acceso por rol, bitácoras y evaluación de "
        "impacto aprobada antes del piloto.",
    },
]

INTEGRACION = [
    {
        "fuente": "Alarmas del NOC / OSS",
        "dato": "Sitios caídos, inicio, causa, hora estimada de solución, restablecimiento",
        "frecuencia_piloto": "Exportación CSV cada 15 min (o correo del NOC)",
        "frecuencia_produccion": "Tiempo real (API / eventos)",
    },
    {
        "fuente": "ACS (TR-069) y gestores de OLT / CMTS",
        "dato": "Telemetría diaria por módem: señal, errores, reinicios, micro-cortes, latencia, WiFi",
        "frecuencia_piloto": "Exportación CSV diaria",
        "frecuencia_produccion": "Cada hora (API del ACS)",
    },
    {
        "fuente": "Órdenes de trabajo de campo",
        "dato": "Visitas técnicas con fecha, motivo y código de cierre (métrica norte de Hogar)",
        "frecuencia_piloto": "CSV diario",
        "frecuencia_produccion": "Diario",
    },
    {
        "fuente": "Inventario de red",
        "dato": "Qué clientes cuelgan de cada sitio/celda y de cada nodo/OLT (hogar)",
        "frecuencia_piloto": "CSV diario",
        "frecuencia_produccion": "Diario",
    },
    {
        "fuente": "CRM / BSS",
        "dato": "Segmento, plan, antigüedad, canal preferido, consentimiento, opt-out",
        "frecuencia_piloto": "CSV diario",
        "frecuencia_produccion": "Diario",
    },
    {
        "fuente": "Call center / IVR",
        "dato": "Llamadas por cliente con fecha, hora, motivo y resolución (métrica norte)",
        "frecuencia_piloto": "CSV diario",
        "frecuencia_produccion": "Diario o tiempo real",
    },
    {
        "fuente": "WhatsApp Business API",
        "dato": "Envío, entrega, lectura, respuestas, opt-outs",
        "frecuencia_piloto": "Webhook del proveedor",
        "frecuencia_produccion": "Tiempo real",
    },
    {
        "fuente": "Encuestas CSAT/NPS",
        "dato": "Satisfacción de afectados después de la falla",
        "frecuencia_piloto": "Encuesta corta post-falla",
        "frecuencia_produccion": "Semanal",
    },
]

RIESGOS = [
    {
        "riesgo": "Calidad de datos (cliente ↔ sitio mal mapeado)",
        "probabilidad": "Media",
        "impacto": "Alto",
        "mitigacion": "Semanas 0–2: auditar una muestra; usar zona/código postal como respaldo; medir % de avisos a "
        "no afectados.",
    },
    {
        "riesgo": "La IA no supera a la regla de umbrales con datos reales",
        "probabilidad": "Media",
        "impacto": "Medio",
        "mitigacion": "Análisis retrospectivo con 3 meses de telemetría en las semanas 0–2; si no llega a 1.3×, "
        "el piloto usa la regla (el producto funciona igual, con menos captura).",
    },
    {
        "riesgo": "Una acción remota deja al cliente sin servicio",
        "probabilidad": "Baja",
        "impacto": "Medio",
        "mitigacion": "Lista cerrada de acciones, firmware certificado, ventana de madrugada, lotes pequeños y "
        "reversión automática; se mide en el grupo tratado.",
    },
    {
        "riesgo": "Aviso con hora de solución equivocada",
        "probabilidad": "Media",
        "impacto": "Medio",
        "mitigacion": 'Solo se da hora si el NOC la tiene; si no, "le avisaremos al restablecer". Mensaje de '
        "actualización si la hora cambia.",
    },
    {
        "riesgo": "Fatiga de mensajes / opt-outs",
        "probabilidad": "Baja",
        "impacto": "Medio",
        "mitigacion": "Máximo 2 mensajes por falla; criterio NO-GO si el opt-out supera 2 %.",
    },
    {
        "riesgo": "Costo de compensaciones",
        "probabilidad": "Media",
        "impacto": "Medio",
        "mitigacion": "Tope mensual configurable; el modelo prioriza a quién compensar.",
    },
    {
        "riesgo": "Privacidad y cumplimiento",
        "probabilidad": "Baja",
        "impacto": "Alto",
        "mitigacion": "Evaluación de impacto aprobada antes del piloto; datos mínimos; al LLM solo llega el nombre de "
        "pila (texto libre redactado); bitácoras de mensajes y accesos; SSO con MFA y roles.",
    },
    {
        "riesgo": "Adopción interna (NOC y call center)",
        "probabilidad": "Media",
        "impacto": "Alto",
        "mitigacion": "Patrocinador de CX; enlace del NOC en el equipo; tablero diario compartido.",
    },
    {
        "riesgo": "El efecto real es menor al esperado",
        "probabilidad": "Media",
        "impacto": "Medio",
        "mitigacion": "Es para lo que existe el grupo control: si no supera el 10 % se detiene (NO-GO) con un costo "
        "acotado.",
    },
]

EQUIPO = [
    {
        "rol": "Patrocinador (Dirección de CX)",
        "dedicacion": "2 h/semana",
        "responsabilidad": "Decide GO/NO-GO, quita obstáculos",
    },
    {"rol": "Líder del piloto", "dedicacion": "50 %", "responsabilidad": "Coordina, mide y reporta"},
    {"rol": "Analista/científico de datos", "dedicacion": "50 %", "responsabilidad": "Datos, modelo, análisis A/B"},
    {"rol": "Enlace del NOC", "dedicacion": "10 %", "responsabilidad": "Alarmas, causas y horas estimadas"},
    {
        "rol": "Ingeniería de acceso (Hogar)",
        "dedicacion": "20 %",
        "responsabilidad": "Telemetría del ACS/OLT, acciones remotas permitidas",
    },
    {"rol": "Soporte remoto nivel 2", "dedicacion": "Turno", "responsabilidad": "Atiende la lista diaria de hogares"},
    {
        "rol": "Seguridad y Privacidad",
        "dedicacion": "Puntual",
        "responsabilidad": "Evaluación de impacto, SSO, pentest",
    },
    {"rol": "Canales digitales", "dedicacion": "10 %", "responsabilidad": "WhatsApp Business, plantillas"},
    {"rol": "Legal", "dedicacion": "Puntual", "responsabilidad": "Consentimiento, plantillas, compensaciones"},
    {"rol": "Finanzas", "dedicacion": "Puntual", "responsabilidad": "Valida costo por llamada y caso de negocio"},
]

PLAN = [
    {
        "semanas": "0–2",
        "fase": "Preparación",
        "actividades": "CSV del NOC, ACS/OLT, CRM, call center y campo; análisis retrospectivo (IA vs. regla con "
        "3 meses reales); mapeo cliente↔sitio/nodo; plantillas y evaluación de impacto aprobadas; SSO y pentest.",
    },
    {
        "semanas": "3–10",
        "fase": "Piloto en vivo",
        "actividades": "Hogar: la IA marca el 2 % semanal y soporte N2 corrige a distancia. Móvil: avisos y cierres. "
        "15 % de control en ambos; tablero diario.",
    },
    {
        "semanas": "11–12",
        "fase": "Análisis y decisión",
        "actividades": "Efecto con IC 95 % (visitas y llamadas), costo real por visita y llamada evitada, GO/NO-GO por "
        "frente al comité.",
    },
]


DIAGRAMA = """```mermaid
flowchart LR
    subgraph Tigo["Sistemas de Tigo (ya existen)"]
        NOC["Alarmas NOC / OSS<br/>sitios caídos, causa, ETA"]
        ACS["ACS TR-069 · OLT / CMTS<br/>telemetría de módems"]
        CAMPO["Órdenes de campo<br/>visitas técnicas"]
        INV["Inventario de red<br/>cliente ↔ sitio"]
        CRM["CRM / BSS<br/>segmento, consentimiento"]
        CC["Call center / IVR<br/>llamadas (métrica norte)"]
    end
    subgraph TP["Tigo Predice"]
        ING["Ingesta<br/>piloto: CSV diario / 15 min<br/>producción: tiempo real"]
        AFE["Detección de afectados<br/>+ asignación por hash<br/>tratamiento 85 % / control 15 %"]
        IAH["IA Hogar (7 días)<br/>marca el 2 % semanal<br/>+ explicación"]
        REM["Acción remota<br/>lista cerrada, de madrugada"]
        MOD["Modelo 72 h<br/>prioriza compensaciones"]
        MSG["Mensajes: plantillas + LLM<br/>con guardrails y bitácora"]
        MED["Medición A/B<br/>IC 95 %, GO/NO-GO"]
    end
    WA["WhatsApp Business API<br/>(SMS de respaldo)"]
    NOC --> ING
    ACS --> ING
    INV --> ING
    CRM --> ING
    ING --> AFE --> MOD --> MSG --> WA
    ING --> IAH --> REM --> ACS
    IAH --> MSG
    WA -- entregas, respuestas, opt-out --> MED
    CC -- llamadas --> MED
    CAMPO -- visitas en 7 días --> MED
```"""


SEGURIDAD = [
    {"control": "Cabeceras de seguridad, CSP y HSTS", "estado": "Implementado y probado", "produccion": "Igual + WAF"},
    {
        "control": "Autenticación y sesión",
        "estado": "Sesión firmada y revocable, tokens de 24+ caracteres, bloqueo por intentos; probado",
        "produccion": "SSO corporativo con MFA",
    },
    {
        "control": "Roles (mínimo privilegio)",
        "estado": "Lectura, operador y auditor (solo el auditor lee bitácoras); probado",
        "produccion": "Roles desde el SSO",
    },
    {
        "control": "CSRF, exposición y abuso",
        "estado": "Rechazo por origen; demo solo local; límite de peticiones; parámetros acotados; probado",
        "produccion": "API gateway",
    },
    {
        "control": "Minimización de datos personales",
        "estado": "Nombre corto, teléfono enmascarado, sin coordenadas; probado",
        "produccion": "Esquemas por rol",
    },
    {
        "control": "Seguridad del LLM",
        "estado": "Sin identificadores; entrada saneada; anti-phishing; sin herramientas; probado",
        "produccion": "DPA con retención cero o nube corporativa",
    },
    {
        "control": "Integridad de los modelos",
        "estado": "Huella SHA-256 verificada antes de cargar; probado",
        "produccion": "Manifiesto firmado con clave del gestor de secretos",
    },
    {
        "control": "Bitácoras y retención",
        "estado": "Mensajes 90 días; accesos con sesión seudonimizada y sin consulta",
        "produccion": "SIEM, 1 año",
    },
    {
        "control": "Cadena de suministro",
        "estado": "requirements.lock; pip-audit y npm audit sin hallazgos; reglas S en el lint",
        "produccion": "SBOM, escaneo de contenedores y pentest",
    },
    {
        "control": "Cifrado y red",
        "estado": "Servidor solo en 127.0.0.1 (demo)",
        "produccion": "TLS 1.3, cifrado con KMS, red privada",
    },
]


def markdown() -> str:
    def tabla(filas: list[dict], cols: list[tuple[str, str]]) -> list[str]:
        out = ["| " + " | ".join(t for _, t in cols) + " |", "|" + "---|" * len(cols)]
        out += ["| " + " | ".join(str(f[c]) for c, _ in cols) + " |" for f in filas]
        return out

    L = [
        "# Listo para producción",
        "",
        "> Generado con `python -m backend.app.services.produccion` (misma fuente que la pantalla de la app).",
        "> El piloto arranca con **exportaciones batch (CSV diarios)** antes de integrar en tiempo real: menos costo y "
        "menos riesgo. Lo regulatorio se lista como **puntos a validar con Legal de Tigo**; "
        "no se citan artículos de ley.",
        "",
        "## Integración",
        "",
        DIAGRAMA,
        "",
    ]
    L += tabla(
        INTEGRACION,
        [
            ("fuente", "Fuente"),
            ("dato", "Dato"),
            ("frecuencia_piloto", "Piloto"),
            ("frecuencia_produccion", "Producción"),
        ],
    )
    L += ["", "## Consentimiento, canal y cumplimiento", ""]
    L += [f"- **{c['tema']}:** {c['detalle']}" for c in CONSENTIMIENTO]
    L += ["", "## Seguridad y privacidad (detalle en docs/seguridad_y_privacidad.md)", ""]
    L += tabla(SEGURIDAD, [("control", "Control"), ("estado", "Prototipo"), ("produccion", "Producción")])
    L += ["", "## Matriz de riesgos", ""]
    L += tabla(
        RIESGOS,
        [("riesgo", "Riesgo"), ("probabilidad", "Probabilidad"), ("impacto", "Impacto"), ("mitigacion", "Mitigación")],
    )
    L += ["", "## Equipo del piloto", ""]
    L += tabla(EQUIPO, [("rol", "Rol"), ("dedicacion", "Dedicación"), ("responsabilidad", "Responsabilidad")])
    L += ["", "## Plan (12 semanas)", ""]
    L += tabla(PLAN, [("semanas", "Semanas"), ("fase", "Fase"), ("actividades", "Actividades")])
    return "\n".join(L) + "\n"


def contenido() -> dict:
    return {
        "consentimiento": CONSENTIMIENTO,
        "integracion": INTEGRACION,
        "riesgos": RIESGOS,
        "equipo": EQUIPO,
        "plan": PLAN,
        "seguridad": SEGURIDAD,
    }


if __name__ == "__main__":
    from ml.comun import RAIZ

    (RAIZ / "docs" / "listo_para_produccion.md").write_text(markdown(), encoding="utf-8", newline="\n")
    print("docs/listo_para_produccion.md actualizado")
