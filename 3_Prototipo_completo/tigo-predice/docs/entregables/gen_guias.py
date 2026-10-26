"""Genera la guía visual de la demo, el elevator pitch y las preguntas frecuentes en PDF (y la guía en Markdown).

Uso:  python docs/entregables/gen_guias.py <carpeta_salida>

- Guía visual: capturas de docs/capturas con marcas numeradas (coordenadas en píxeles de la captura de 1600 de
  ancho) y su leyenda. Escribe también docs/guia_demo.md con el mismo contenido (una sola fuente).
- Elevator pitch y preguntas frecuentes: se convierten desde docs/*.md (markdown-it) a HTML con estilo.
- Los PDF los imprime Microsoft Edge en modo headless (sin encabezados ni pies del navegador).
"""

from __future__ import annotations

import html
import shutil
import subprocess  # noqa: S404 - solo para imprimir con Edge, con rutas fijas y sin shell
import sys
import tempfile
from pathlib import Path

from markdown_it import MarkdownIt

DOCS = Path(__file__).resolve().parents[1]
CAPT = DOCS / "capturas"
EDGE = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]
AZUL, CELESTE, ROJO = "#00377b", "#00c8ff", "#e0303a"

# ------------------------------------------------------------------ guía visual (una sola fuente)
# Cada marca: (x, y, título, explicación). x, y en píxeles de la captura (1600 de ancho).
PAGINAS = [
    {
        "titulo": "Inicio: el mapa de la app",
        "imagen": "inicio.png",
        "intro": "La primera pantalla resume la propuesta. Desde aquí, el botón Presentar abre el modo presentación.",
        "marcas": [
            (
                118,
                117,
                "Menú",
                "Todas las pantallas. Fase 1 es el piloto (Hogar + Móvil); Fase 2 es visión y no entra al caso.",
            ),
            (1380, 26, "Botón «Hogar en vivo»", "Atajo a la demo principal desde cualquier pantalla."),
            (405, 26, "Datos simulados", "Recordatorio permanente: todo es simulado o supuesto a validar con Tigo."),
            (
                615,
                26,
                "Modo plantillas / Modo IA",
                "Sin clave de API usa plantillas aprobadas; con clave, Claude redacta los mensajes.",
            ),
            (414, 400, "Ver Hogar en vivo", "Abre la demo de 80 segundos."),
            (425, 530, "Cifras clave", "Neto año 1, IA vs. regla, punto de equilibrio e inversión del piloto."),
        ],
    },
    {
        "titulo": "Hogar en vivo ★: antes de iniciar",
        "imagen": "hogar_inicio.png",
        "intro": "Deje esta pantalla lista antes de presentar: caso «A distancia», velocidad 1× y la demo reiniciada (↺).",
        "marcas": [
            (
                1100,
                98,
                "Caso",
                "«A distancia»: WiFi y firmware, se corrige sin técnico (recomendado). «Con técnico»: la señal de fibra baja y el técnico va una sola vez.",
            ),
            (1300, 98, "Velocidad", "1× dura unos 80 s. Use 2× si tiene poco tiempo."),
            (1404, 98, "Iniciar ▶", "Arranca la historia; la franja azul narra cada paso."),
            (1522, 98, "Reiniciar ↺", "Deja todo limpio para volver a empezar."),
            (
                272,
                92,
                "Pasos",
                "Se encienden a medida que avanza: hogar sano → la IA lo marca → diagnóstico → acción → sin vs. con → resultado.",
            ),
            (952, 130, "Narración", "Léala en voz alta o parafrasee: es el guion de la demo."),
            (
                737,
                245,
                "Indicadores",
                "Día, riesgo que calcula la IA, si la regla de umbrales alarma y la señal principal.",
            ),
            (1395, 210, "Diagnóstico", "Aquí aparece por qué la IA marcó el hogar y qué acción se tomó."),
            (1395, 470, "WhatsApp", "El mensaje que recibe el cliente (plantilla aprobada o IA con guardrails)."),
        ],
    },
    {
        "titulo": "Hogar en vivo ★: el resultado",
        "imagen": "hogar.png",
        "intro": "Así termina la demo. Si algo falla en vivo, abra #/hogar?final al final de la dirección (en el prototipo completo, /hogar?final) y explique esta pantalla.",
        "marcas": [
            (
                560,
                325,
                "IA lo marca (28/09)",
                "La IA detecta el problema con 13 % de riesgo, dentro del 2 % más alto de la ciudad.",
            ),
            (712, 315, "Llamaría (02/10)", "Sin Tigo Predice, el cliente habría llamado 4 días después."),
            (775, 343, "Regla (03/10)", "Recién aquí la regla de umbrales habría alarmado: después de la llamada."),
            (640, 505, "Riesgo de la IA", "Línea azul punteada: sube antes de que el cliente note nada."),
            (
                880,
                522,
                "Con Tigo Predice",
                "Línea verde: el WiFi queda sano tras la corrección remota. Rojo: sin Tigo Predice.",
            ),
            (1395, 220, "Por qué lo marcó", "Motivos en lenguaje simple (contribuciones SHAP del modelo)."),
            (1395, 490, "Acciones remotas", "Firmware de madrugada, cambio de canal WiFi y verificación a los 3 días."),
            (1395, 760, "WhatsApp", "«Ya la corregimos a distancia, sin que tuviera que llamar», con opción AGENTE."),
            (278, 710, "Resultado", "4 días antes de la llamada, visita evitada, L 780 de ahorro por L 0.31."),
        ],
    },
    {
        "titulo": "Hogar en vivo ★: la lista de trabajo de hoy",
        "imagen": "hogar_lista.png",
        "recorte": (1130, 1650, 1650),
        "intro": "Debajo de la demo: lo que soporte nivel 2 recibiría cada día. Muestra que es un producto operable, no solo una animación.",
        "marcas": [
            (
                1035,
                1200,
                "Resumen",
                "Hogares marcados hoy en San Pedro Sula y cuántos no tienen ninguna alarma de umbral (solo la IA los ve).",
            ),
            (404, 1226, "Riesgo", "Probabilidad de llamada o visita en 7 días. Nunca se muestra «100 %»."),
            (522, 1226, "Regla", "Si la regla de umbrales ya alarmaba o no."),
            (600, 1226, "Por qué", "Los tres motivos principales, con su valor."),
            (
                1300,
                1226,
                "Acción sugerida",
                "Corrección remota, visita con diagnóstico o revisar el nodo (posible falla masiva).",
            ),
            (1432, 1226, "Contacto", "Respeta el opt-out: sin mensajes, solo corrección remota."),
        ],
    },
    {
        "titulo": "Falla masiva en vivo (frente Móvil)",
        "imagen": "falla.png",
        "intro": "El mismo motor en fallas masivas de red. En el modo presentación se muestra su resultado; fuera de él, agregue #/falla?final a la dirección (en el prototipo completo, /falla?final).",
        "marcas": [
            (1300, 98, "Velocidad", "1× dura unos 90 s."),
            (1404, 98, "Iniciar ▶", "Cae un sitio en San Pedro Sula y se dibujan los afectados."),
            (735, 383, "Sitio caído", "Círculo con los clientes afectados (azul: reciben aviso; gris: control)."),
            (1000, 213, "Grupos", "Afectados, quiénes reciben aviso y el 15 % de control."),
            (1395, 330, "Aviso", "Causa en palabras simples y hora del NOC solo si la tiene."),
            (1395, 560, "Cierre", "Mensaje cuando vuelve el servicio."),
            (420, 655, "Llamadas por 1,000", "Rojo sin aviso vs. verde con aviso, durante 72 horas."),
            (700, 555, "Escala real", "Llamadas evitadas y ahorro de una falla típica (supuestos)."),
        ],
    },
    {
        "titulo": "Resultados del piloto",
        "imagen": "piloto.png",
        "intro": "Cómo se medirá: tratados vs. control con intervalo de confianza. Es una simulación: dígalo.",
        "marcas": [
            (375, 97, "Pestañas", "Hogar (por defecto) y Móvil."),
            (292, 360, "Control", "Visitas por 1,000 hogares marcados sin acción."),
            (574, 360, "Tratados", "Visitas por 1,000 con atención proactiva."),
            (855, 360, "Reducción", "−19 % con IC 95 % y valor p."),
            (1365, 372, "Decisión", "GO/NO-GO con sus criterios, incluido que la IA le gane a la regla."),
            (1240, 760, "Poder estadístico", "Muestra necesaria y poder con el piloto (97 %)."),
        ],
    },
    {
        "titulo": "Caso de negocio y «Pon tus números»",
        "imagen": "negocio.png",
        "intro": "Solo beneficio duro. Si el jurado da un dato real, ingréselo en vivo: es el momento más convincente.",
        "marcas": [
            (278, 232, "Neto año 1", "Ambos frentes, escenario base, con inversión."),
            (
                620,
                325,
                "Equilibrio por frente",
                "Móvil se paga con 12 % menos llamadas; Hogar, con 22 % menos visitas evitables.",
            ),
            (1060, 326, "Visitas al mes", "Escriba el dato real (solo números, sin comas)."),
            (1316, 306, "Costo por visita", "En lempiras. Lo mismo con llamadas y costo por llamada."),
            (1046, 476, "Recalcular", "Todo se recalcula al instante y aparece «usando dato Tigo»."),
            (1262, 476, "Supuestos", "Vuelve a los valores supuestos."),
            (
                620,
                700,
                "Escenarios",
                "Conservador, base y optimista por frente; más abajo, el tornado de sensibilidad.",
            ),
            (1280, 650, "Piloto", "Costo total del piloto (L 770 mil) y su desglose."),
        ],
    },
    {
        "titulo": "Modelo de IA: medido contra la regla",
        "imagen": "modelo.png",
        "intro": "La respuesta a «¿por qué no bastan las alarmas?». Señale las dos barras: regla de umbrales vs. IA.",
        "marcas": [
            (375, 97, "Pestañas", "Hogar (modelo de 7 días) y Móvil (modelo de 72 h)."),
            (500, 385, "Regla de umbrales", "Anticipa el 26 % de las visitas evitables."),
            (560, 532, "IA", "Anticipa el 52 %: 2.0× con el mismo presupuesto."),
            (
                1280,
                300,
                "Lectura honesta",
                "Incluye que una regresión simple casi iguala y que, si no gana, se usa la regla.",
            ),
            (
                700,
                830,
                "Comparación",
                "AUC, precisión y captura de cada estrategia. Más abajo: calibración, importancia y sesgo.",
            ),
        ],
    },
    {
        "titulo": "Listo para producción",
        "imagen": "produccion.png",
        "intro": "Para la pregunta «¿y esto cómo se implementa y es seguro?».",
        "marcas": [
            (
                480,
                186,
                "Integración",
                "Qué dato, de qué sistema y cada cuánto: CSV en el piloto y tiempo real en producción.",
            ),
            (1470, 250, "Producción", "Frecuencia objetivo al escalar."),
            (490, 585, "Seguridad y privacidad", "Cada control: estado en el prototipo (probado) y en producción."),
        ],
    },
    {
        "titulo": "Modo compartido (acceso con token)",
        "imagen": "acceso.png",
        "recorte": (250, 650, 900),
        "intro": "Por seguridad, la demo solo atiende a la misma computadora. Para mostrarla en red, defina tokens y la app pide acceso.",
        "marcas": [
            (800, 462, "Token", "Rol lectura (jurado), operador o auditor, con 24 caracteres o más."),
            (800, 516, "Entrar", "Sesión segura de 8 horas; 5 intentos fallidos bloquean por 15 minutos."),
        ],
        "extra": (
            "<div><h3>Atajos útiles</h3><table class='t'>"
            "<tr><td><code>/hogar?final</code></td><td>Resultado de la demo Hogar (respaldo)</td></tr>"
            "<tr><td><code>/falla?final</code></td><td>Resultado de la demo Falla masiva</td></tr>"
            "<tr><td><code>/negocio</code></td><td>Caso de negocio y «Pon tus números»</td></tr>"
            "<tr><td><code>/modelo</code></td><td>IA vs. regla de umbrales</td></tr></table></div>"
            "<div><h3>Si algo falla</h3><ul>"
            "<li><b>No se abre el navegador:</b> entre a http://127.0.0.1:8000.</li>"
            "<li><b>La demo quedó a medias:</b> presione ↺.</li>"
            "<li><b>No hay internet:</b> no importa; usa plantillas aprobadas.</li>"
            "<li><b>Otra computadora no entra:</b> es intencional; use tokens.</li>"
            "<li><b>Error 429:</b> demasiadas peticiones; espere un minuto.</li></ul></div>"
        ),
    },
]

CRONOLOGIA = [
    ("0", "Día normal: el módem reporta su telemetría", "~30", "«Dos mundos»: rojo sin, verde con Tigo Predice"),
    ("~9", "Empieza el problema (el cliente no nota nada)", "~38", "Sin Tigo Predice, el cliente habría llamado"),
    ("~14", "<b>La IA lo marca</b> y aparecen los motivos", "~43", "Recién ahí alarma la regla de umbrales"),
    ("~19", "Diagnóstico en la franja azul", "~48", "…y se habría enviado un técnico innecesario"),
    ("~23", "Corrección remota y WhatsApp", "~70 · ~77", "Resultado del hogar y frase final"),
]
ANTES = [
    "Abra <b>1_Demo/index.html</b> con doble clic: no necesita internet ni instalar nada. "
    "(Con el prototipo completo, <b>iniciar_demo.bat</b> abre la misma app en http://127.0.0.1:8000.)",
    "Presione <b>Presentar</b>, arriba a la derecha. El modo presentación queda en pausa en la primera escena.",
    "Presione <b>F</b> para pantalla completa. En Teams, comparta la pantalla o la ventana del navegador.",
    "Apague las notificaciones y tenga a mano el guion de la presentación (PDF aparte).",
    "Cuando le den la palabra, presione <b>Espacio</b>: la presentación avanza sola y dura 4:32.",
]
# Mismo orden y duración que frontend/src/escenas.ts
RECORRIDO = [
    ("0:00", "Inicio", "Frase de Tigo Predice", "Saludo breve"),
    ("0:10", "Karla", "Su historia y lo que cuesta", "«Llama, espera, llega un técnico… y no era necesario»"),
    ("0:36", "No es un caso aislado", "Hogares, visitas y cuántas se evitan", "«Estimaciones a validar con Tigo»"),
    ("0:56", "Nuestra idea", "Detecta, resuelve y avisa", "«Escuchar al módem a tiempo»"),
    ("1:16", "Demo en vivo", "Hogar en vivo corre sola (80 s)", "Acompañe la franja azul"),
    (
        "2:36",
        "IA frente a las alarmas",
        "52 % contra 26 % (datos de ejemplo)",
        "«Si no gana con datos reales, usamos las alarmas»",
    ),
    ("2:56", "Celulares", "WhatsApp cuando se cae una antena, y CONATEL", "«Cumplimos la norma y ahorramos»"),
    ("3:18", "Cuánto se ahorra", "L 4.3 M; se paga con 22 % y 12 %", "«Solo lo que se puede medir»"),
    ("3:44", "Confianza", "Privacidad y comparación con otros clientes", "«Solo vemos si el aparato funciona»"),
    ("3:58", "Lo que pedimos", "12 semanas, L 770 mil", "«Ustedes deciden con resultados reales»"),
    ("4:24", "Cierre", "Gracias y contacto", "«Tigo Predice evita que ocurra»"),
]

CSS_BASE = f"""
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: Calibri, "Segoe UI", Arial, sans-serif; color: #0f1b2d;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
h1, h2, h3 {{ color: {AZUL}; }}
code {{ background: #eef3f9; padding: 0 4px; border-radius: 4px; font-size: 0.92em; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border-bottom: 1px solid #d5dce6; padding: 4px 6px; text-align: left; vertical-align: top; }}
th {{ background: {AZUL}; color: #fff; }}
"""


def _marcas_html(marcas, ancho_px: float, y0: float, alto_px: float) -> str:
    return "".join(
        f"<span class='marca' style='left:{x / ancho_px * 100:.2f}%;top:{(y - y0) / alto_px * 100:.2f}%'>{i}</span>"
        for i, (x, y, _, _) in enumerate(marcas, start=1)
    )


def guia_html() -> str:
    css = (
        CSS_BASE
        + f"""
@page {{ size: Letter landscape; margin: 0; }}
.pagina {{ width: 11in; height: 8.5in; padding: 0.35in 0.45in; page-break-after: always; display: flex; flex-direction: column; }}
.pagina:last-child {{ page-break-after: auto; }}
.cab {{ display: flex; justify-content: space-between; align-items: baseline; border-bottom: 3px solid {CELESTE}; margin-bottom: 8px; }}
.cab h2 {{ margin: 0 0 4px; font-size: 24px; }}
.cab span {{ color: #5b6575; font-size: 11px; }}
.intro {{ font-size: 13px; margin: 0 0 8px; color: #334155; }}
.cuerpo {{ display: block; }}
.lienzo {{ position: relative; border: 1px solid #d5dce6; border-radius: 8px; overflow: hidden; }}
.lienzo img {{ display: block; width: 100%; }}
.recorte {{ width: 100%; background-repeat: no-repeat; background-size: 100% auto; background-position: 0 100%; }}
.marca {{ position: absolute; transform: translate(-50%, -50%); width: 24px; height: 24px; border-radius: 50%;
  background: {ROJO}; color: #fff; font-weight: 800; font-size: 13px; display: flex; align-items: center;
  justify-content: center; border: 2px solid #fff; box-shadow: 0 1px 4px rgba(0,0,0,.45); }}
ol.ley {{ margin: 10px 0 0; padding: 0; list-style: none; font-size: 11.5px; line-height: 1.32; columns: 3; column-gap: 22px; }}
ol.ley li {{ display: flex; gap: 7px; margin-bottom: 6px; break-inside: avoid; }}
.extra {{ display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }}
.lienzo.corto {{ width: 8.2in; margin: 0 auto; }}
ol.ley b.n {{ flex: 0 0 20px; height: 20px; border-radius: 50%; background: {ROJO}; color: #fff; font-size: 11px;
  display: flex; align-items: center; justify-content: center; }}
h3 {{ font-size: 13px; margin: 8px 0 4px; }}
table.t {{ font-size: 10.5px; }}
.extra ul {{ font-size: 11px; padding-left: 16px; margin: 4px 0; }}
.portada {{ background: {AZUL}; color: #fff; }}
.portada h1 {{ color: #fff; font-size: 44px; margin: 0.6in 0 6px; }}
.portada .lema {{ color: {CELESTE}; font-size: 20px; font-style: italic; }}
.caja {{ background: #fff; color: #0f1b2d; border-radius: 12px; padding: 14px 18px; margin-top: 18px; }}
.caja ol {{ margin: 6px 0 0; padding-left: 20px; font-size: 13.5px; line-height: 1.5; }}
.dos {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
.recorrido td, .recorrido th {{ font-size: 12px; padding: 6px 8px; }}
"""
    )
    paginas = [
        "<section class='pagina portada'><div style='font-size:12px;letter-spacing:2px;color:#00c8ff;font-weight:700'>"
        "TIGO CX MONTH · CONCURSO SHARKS DE IA</div><h1>Guía visual de la demo</h1>"
        "<div class='lema'>Tigo Predice · cómo usar el prototipo en la presentación</div>"
        "<div class='dos'><div class='caja'><h3>Antes de presentar</h3><ol>"
        + "".join(f"<li>{x}</li>" for x in ANTES)
        + "</ol></div><div class='caja'><h3>Plan B</h3><ol>"
        "<li>Si el modo presentación falla: abra <b>Hogar en vivo</b>, presione Iniciar y siga el mismo orden.</li>"
        "<li>Si la demo se traba: presione ↺ o agregue <b>#/hogar?final</b> a la dirección y explique el resultado.</li>"
        "<li>Si la computadora falla: el elevator pitch de 2 minutos, sin pantalla.</li>"
        "<li>Si se cae internet: no pasa nada; el prototipo funciona sin internet.</li>"
        "<li>Si la pantalla es chica: zoom del navegador al 80–90 %.</li></ol>"
        "<p style='font-size:12px;color:#5b6575'>Los números rojos de cada captura corresponden a la leyenda de la "
        "derecha. Todo usa datos simulados.</p></div></div></section>",
        "<section class='pagina'><div class='cab'><h2>Modo presentación (4:32)</h2><span>Tigo Predice</span></div>"
        "<p class='intro'>Botón <b>Presentar</b>: cada escena abre una pantalla real del sistema y, a la izquierda, una tarjeta con la idea y las cifras. Espacio pausa; ← y → (o un control remoto) cambian de escena; S muestra u oculta los subtítulos; V activa la vista simple; Esc vuelve a la demo para las preguntas. El guion va en un "
        "documento aparte.</p>"
        "<table class='recorrido'><tr><th>Min.</th><th>Escena</th><th>En pantalla</th><th>Idea</th></tr>"
        + "".join(
            f"<tr><td>{a}</td><td><b>{b}</b></td><td>{c}</td><td><i>{d}</i></td></tr>" for a, b, c, d in RECORRIDO
        )
        + "</table><h3 style='margin-top:18px'>Qué pasa y cuándo en «Hogar en vivo» (velocidad 1×)</h3>"
        "<table class='recorrido'><tr><th>Seg.</th><th>En pantalla</th><th>Seg.</th><th>En pantalla</th></tr>"
        + "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in CRONOLOGIA)
        + "</table></section>",
    ]
    for pg in PAGINAS:
        if "recorte" in pg:
            y0, y1, alto = pg["recorte"]
            pos = y0 / (alto - (y1 - y0)) * 100
            lienzo = (
                f"<div class='lienzo'><div class='recorte' style=\"aspect-ratio:1600/{y1 - y0};"
                f"background-image:url('{pg['imagen']}');background-position:0 {pos:.1f}%\"></div>"
                f"{_marcas_html(pg['marcas'], 1600, y0, y1 - y0)}</div>"
            )
        else:
            lienzo = (
                f"<div class='lienzo corto'><img src='{pg['imagen']}' alt=''>"
                f"{_marcas_html(pg['marcas'], 1600, 0, 900)}</div>"
            )
        leyenda = "".join(
            f"<li><b class='n'>{i}</b><span><b>{html.escape(t)}.</b> {html.escape(d)}</span></li>"
            for i, (_, _, t, d) in enumerate(pg["marcas"], start=1)
        )
        paginas.append(
            f"<section class='pagina'><div class='cab'><h2>{html.escape(pg['titulo'])}</h2><span>Tigo Predice · guía de la demo</span></div>"
            f"<p class='intro'>{html.escape(pg['intro'])}</p><div class='cuerpo'>{lienzo}"
            f"<ol class='ley'>{leyenda}</ol><div class='extra'>{pg.get('extra', '')}</div></div></section>"
        )
    return f"<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Guía visual de la demo</title><style>{css}</style></head><body>{''.join(paginas)}</body></html>"


def guia_markdown() -> str:
    L = [
        "# Guía visual de la demo — Tigo Predice",
        "",
        "> Generado con `python docs/entregables/gen_guias.py` (misma fuente que el PDF con capturas anotadas).",
        "",
        "## Antes de presentar",
        "",
    ]
    L += [f"{i}. {x.replace('<b>', '**').replace('</b>', '**')}" for i, x in enumerate(ANTES, start=1)]
    L += [
        "",
        "## Modo presentación (4:32)",
        "",
        "Botón **Presentar**: cada escena abre una pantalla real del sistema y, a la izquierda, una tarjeta con la idea y las "
        "cifras. Espacio pausa; ← y → (o un control remoto) cambian de "
        "escena; S muestra u oculta los subtítulos; V activa la vista simple; Esc vuelve a la demo para las preguntas. El guion va en un documento aparte ([pitch.md](pitch.md)).",
        "",
        "| Min. | Escena | En pantalla | Idea |",
        "|---|---|---|---|",
    ]
    L += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in RECORRIDO]
    for pg in PAGINAS:
        L += ["", f"## {pg['titulo']}", "", pg["intro"], "", f"![{pg['titulo']}](capturas/{pg['imagen']})", ""]
        L += [f"{i}. **{t}.** {d}" for i, (_, _, t, d) in enumerate(pg["marcas"], start=1)]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ documentos desde Markdown
def doc_html(md_path: Path, titulo: str, grande: bool) -> str:
    cuerpo = MarkdownIt("commonmark", {"html": False}).enable("table").render(md_path.read_text(encoding="utf-8"))
    base = 15 if grande else 12
    css = (
        CSS_BASE
        + f"""
@page {{ size: Letter; margin: 0.6in 0.65in; }}
body {{ font-size: {base}px; line-height: 1.45; }}
h1 {{ font-size: {base + 15}px; margin: 0 0 4px; border-bottom: 3px solid {CELESTE}; padding-bottom: 4px; }}
h2 {{ font-size: {base + 5}px; margin: 16px 0 6px; page-break-after: avoid; }}
blockquote {{ margin: 6px 0; padding: 8px 12px; background: #eef3f9; border-left: 4px solid {AZUL}; border-radius: 6px; }}
blockquote p {{ margin: 4px 0; }}
p {{ margin: 6px 0; page-break-inside: avoid; }}
li {{ margin: 2px 0; }}
table {{ font-size: {base - 1}px; margin: 6px 0; page-break-inside: avoid; }}
em {{ color: #5b6575; }}
hr {{ border: 0; border-top: 1px solid #d5dce6; margin: 12px 0; }}
"""
    )
    return f"<!doctype html><html lang='es'><head><meta charset='utf-8'><title>{titulo}</title><style>{css}</style></head><body>{cuerpo}</body></html>"


def imprimir(html_path: Path, pdf_path: Path) -> None:
    edge = next((e for e in EDGE if e.exists()), None)
    if edge is None:
        print("Edge no encontrado: quedó el HTML", html_path)
        return
    # Perfil temporal con ruta corta: con rutas largas Edge no puede crear su caché y no imprime
    perfil = Path(tempfile.gettempdir()) / "tigo_edge"
    subprocess.run(  # noqa: S603 - ejecutable fijo, argumentos sin shell
        [
            str(edge),
            "--headless=new",
            "--disable-gpu",
            f"--user-data-dir={perfil}",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ],
        check=False,
        capture_output=True,
        timeout=120,
    )
    print("PDF", pdf_path, "OK" if pdf_path.exists() else "FALLÓ")


def main() -> None:
    salida = Path(sys.argv[1])
    salida.mkdir(parents=True, exist_ok=True)
    for pg in PAGINAS:
        shutil.copy(CAPT / pg["imagen"], salida / pg["imagen"])
    (salida / "guia.html").write_text(guia_html(), encoding="utf-8", newline="\n")
    (DOCS / "guia_demo.md").write_text(guia_markdown(), encoding="utf-8", newline="\n")
    (salida / "pitch.html").write_text(
        doc_html(DOCS / "elevator_pitch.md", "Elevator pitch", True), encoding="utf-8", newline="\n"
    )
    (salida / "guion.html").write_text(
        doc_html(DOCS / "pitch.md", "Guion de la presentación", True), encoding="utf-8", newline="\n"
    )
    (salida / "faq.html").write_text(
        doc_html(DOCS / "preguntas_frecuentes_jurado.md", "Preguntas frecuentes", False), encoding="utf-8", newline="\n"
    )
    imprimir(salida / "guia.html", salida / "Guia_Visual_Demo.pdf")
    imprimir(salida / "pitch.html", salida / "Elevator_Pitch_2_min.pdf")
    imprimir(salida / "faq.html", salida / "Preguntas_Frecuentes_Jurado.pdf")
    imprimir(salida / "guion.html", salida / "Guion_de_la_presentacion.pdf")


if __name__ == "__main__":
    main()
