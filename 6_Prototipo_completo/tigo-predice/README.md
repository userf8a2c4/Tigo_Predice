# Tigo Predice

> **Los chatbots y copilotos atienden la llamada. Tigo Predice evita que ocurra.**
> La IA que detecta el problema antes que el cliente, y lo resuelve antes de que llame o de que haya que mandar un técnico.

Atención proactiva con IA para Tigo Honduras, en dos frentes con el mismo motor:
- **Hogar (principal):**
  - Cada semana la IA lee la telemetría de los módems y marca al **2 %** de hogares que van a fallar, con su explicación.
  - Si es WiFi o firmware, se corrige **a distancia**.
  - Si es físico, el técnico va **una sola vez y con el diagnóstico**.
- **Móvil:** en fallas masivas de red, aviso por WhatsApp antes de que llamen.

En ambos, un **grupo control aleatorio del 15 %** mide el efecto real.

Propuesta para **Tigo CX Month · Sharks** (octubre 2026), de Sandra Jimenez (Asistente de Experiencia B2B, sandra.jimenez@tigo.com.hn). ⚠️ **Datos simulados — supuestos a validar con Tigo.**

## Arranque (Windows, 3 pasos)
1. Tener **Python 3.11+** y **Node 18+** (solo la primera vez).
2. Doble clic en **`iniciar_demo.bat`**. La primera vez instala las versiones fijadas (`requirements.lock`), genera los datos, entrena y firma los modelos y compila la interfaz. Toma unos 4 minutos; después arranca en unos 5 segundos.
3. Se abre **http://127.0.0.1:8000** → **Hogar en vivo ★** → **▶ Iniciar**.

**Sin servidor:** `2_Demo/Demo_Tigo_Predice.html` (en la carpeta del proyecto, junto a `1_Presentacion` … `5_Envio`, donde están todos los entregables) es la misma demo en un solo archivo que se abre con doble clic, por ejemplo para enviarla al jurado. Se genera con `docs/entregables/gen_demo_html.py`; «Pon tus números» solo funciona en la versión completa.

Funciona **sin internet y sin clave de API** («Modo plantillas»). Para que Claude redacte los mensajes («Modo IA»), copie `.env.ejemplo` como `.env` y agregue `ANTHROPIC_API_KEY`.

**Compartir la demo de forma segura:**
- Por defecto el servidor **solo atiende a la misma máquina**.
- Para mostrarla en red, defina `TIGO_TOKEN_LECTURA` (jurado: solo consulta), `TIGO_TOKEN` (operador) y `TIGO_TOKEN_AUDITOR` (bitácoras), con 24 caracteres o más. La app pedirá el token.
- En producción, `TIGO_PRODUCCION=1` apaga `/docs` y fuerza cookies seguras.

Tareas: `.\tareas.ps1 preparar | test | lint | seguridad | dev | front`.

## Qué muestra la app
| Pantalla | Para qué |
|---|---|
| **Inicio** | Posicionamiento, neto año 1, IA vs. regla, punto de equilibrio e inversión del piloto |
| **Hogar en vivo ★** | Demo de 80 s: un módem se degrada, la IA lo marca días antes que la regla y que la llamada, explica por qué y se corrige a distancia (o se agenda técnico con diagnóstico). Incluye la **lista de trabajo de hoy** para soporte. `?final` abre directo el resultado |
| **Falla masiva en vivo** | Demo de 90 s del frente Móvil: cae un sitio, se separan tratamiento y control, llegan los WhatsApp y se cuentan 72 h de llamadas |
| **Resultados del piloto** | Hogar y Móvil: tratados vs. control con IC 95 %, valor p, GO/NO-GO y poder estadístico |
| **Caso de negocio** | Solo beneficio duro por frente, escenarios, tornado, punto de equilibrio y **Pon tus números** (4 datos de Tigo) |
| **Modelo de IA** | Hogar: IA vs. regla de umbrales vs. azar, calibración, importancia y sesgo. Móvil: modelo 72 h |
| **Listo para producción** | Integración (CSV primero), consentimiento, seguridad y privacidad, riesgos, equipo y plan |
| Fase 2 (visión) | Churn y WhatsApp/tickets. **No entran al caso base** |

## Cifras clave (escenario base, `docs/cifras.json`)
- **Neto año 1 (Hogar + Móvil):** **L 4.3 M**, con un rango de −L 3 M a L 14 M. Solo beneficio duro, con costos hondureños (visita L 650, llamada L 65) y la base real de Tigo Honduras (191 mil hogares, 5.0 M móviles).
- **Equilibrio:**
  - Hogar se paga con **22 %** menos visitas evitables en los hogares marcados (el caso base evita un 5 % del total de visitas).
  - Móvil se paga con **12 %** menos llamadas.
- **IA vs. regla de umbrales (datos simulados):** anticipa **52 %** de las visitas evitables frente a 26 % (2.0×). Se valida con telemetría real antes del piloto.
- **Piloto de 60 días:** **L 770 mil** (≈ US$ 28 mil).
- **Simulación del piloto:** Hogar −19 % de visitas (IC 95 %: 12–25 %) y −56 % de llamadas técnicas; Móvil −16 % de llamadas. Son resultados **simulados**.

## Seguridad y privacidad
Diseñado con marcos internacionales de seguridad y privacidad. Detalle en [docs/seguridad_y_privacidad.md](docs/seguridad_y_privacidad.md):
- **Marcos:** GDPR como estándar (Honduras aún no tiene ley integral), ISO 27001/27701/42001, SOC 2, NIST CSF/AI RMF, OWASP ASVS/API/LLM y MITRE ATLAS.
- **Datos:** sin contenido de comunicaciones ni navegación; datos mínimos.
- **Controles de acceso:** sesión firmada y revocable, roles y CSRF.
- **Integridad:** huella SHA-256 de cada modelo verificada antes de cargarlo, y dependencias fijadas y auditadas.
- **Red team propio:** 12 ataques corregidos, cada uno con su prueba.

## Estructura
```
ml/            generar_datos · generar_hogar · telemetria · entrenar_hogar · entrenar_72h · entrenar (Fase 2) ·
               manifiesto (firmas SHA-256) · evaluar
experimento/   asignacion (hash) · analisis (IC, p, GO/NO-GO) · potencia · simulacion · simulacion_hogar
backend/app/   main (API) · estado · seguridad · privacidad · llm_client ·
               services/{roi, hogar_vivo, falla_vivo, mensajes, bitacora, produccion, ...}
frontend/      React + Vite + TS + Tailwind + Recharts + Leaflet (GeoJSON local)
config/        negocio.toml: cada supuesto con unidad, bajo/base/alto, fuente y nota
docs/          pitch · elevator_pitch · one_pager · preguntas_frecuentes_jurado · guia_demo · formato_concurso · datos_a_pedir_a_tigo · seguridad_y_privacidad ·
               revision_critica · estrategia_y_regulacion · impacto, cifras.json y listo_para_produccion (generados) · arquitectura · roadmap · fuentes
reports/       modelo.md (Hogar, Móvil y Fase 2)
tests/         hogar · seguridad (red team) · experimento · roi · guardrails · consistencia de cifras · API (214 en total)
```

## Limitaciones honestas
- **Datos simulados:** la telemetría, las tasas de visitas y llamadas, los efectos y los costos son supuestos. Antes del piloto, un análisis retrospectivo con 3 meses de telemetría real confirma (o no) que la IA le gana a la regla.
- **Demo guionada:** los dos hogares de «Hogar en vivo» tienen problemas guionados, pero el riesgo diario y la explicación los calcula el modelo real.
- **Agrupamiento:** la potencia asume unidades independientes. En el piloto se usan errores agrupados por nodo (Hogar) y por falla (Móvil).
- **Integraciones simuladas:** ACS, WhatsApp Business y SSO se conectan en las semanas 0–2.

Más detalle: [docs/revision_critica.md](docs/revision_critica.md) (datos reales y puntos débiles) · [docs/estrategia_y_regulacion.md](docs/estrategia_y_regulacion.md) (Millicom 2026 y CONATEL NR001/26) · [DECISIONES.md](DECISIONES.md)
