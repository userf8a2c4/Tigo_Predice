# Decisiones tomadas

| # | Fecha | Decisión | Motivo |
|---|---|---|---|
| 1 | 13-oct | No se cuenta con el formato oficial del concurso: se prepara una **propuesta genérica en Word** con los campos típicos. | El formato no está disponible; el texto es fácil de adaptar. |
| 2 | 13-oct | Participación **individual**. Si se suma equipo, solo se agregan los nombres. | Sin información de equipo. |
| 3 | 13-oct | ROI con **datos públicos + supuestos conservadores**, editables en vivo. | No hay acceso a cifras internas. Ver `docs/fuentes.md`. |
| 4 | 13-oct | Stack completo **sin Docker**: Python 3.15 + FastAPI + LightGBM y React + Vite. | Docker no está instalado y no hace falta para la demo. |
| 5 | 13-oct | Configuración en **TOML** (`config/negocio.toml`) en vez de YAML. | PyYAML no tiene versión para Python 3.15; `tomllib` viene con Python. |
| 6 | 13-oct | `tareas.ps1` en lugar de `Makefile`. | Windows no trae `make`. |
| 7 | 13-oct | Entorno virtual en `%USERPROFILE%\.venvs\tigo-predice`, **fuera de OneDrive**. | Evita que OneDrive sincronice miles de archivos. |
| 8 | 13-oct | `uvicorn` simple, sin `[standard]`. | Los extras (`httptools`, `websockets`) no tienen versión para Python 3.15. La demo usa SSE, que no necesita WebSockets. |
| 9 | 13-oct | Teléfonos guardados **enmascarados** (`+504 9***-1234`). | Evita generar por azar números reales. Es la práctica recomendada de privacidad. |
| 10 | 13-oct | Señal causal de los datos sintéticos calibrada (`FUERZA_SENAL = 1.5`) para un **AUC de ~0.87**. | Con 1.0 el techo teórico era 0.81; con 1.8 subía a 0.91, que se vería falso. |
| 11 | 13-oct | Se agregó la tabla `telemetria` con la velocidad y latencia **por cliente**. | Sin ella no se distingue una falla individual de equipo de una falla de la celda (acción: autodiagnóstico). |
| 12 | 13-oct | Puntajes del tablero con **predicciones fuera de muestra** (validación cruzada de 5 particiones). | Ningún cliente se califica con un modelo que lo vio: los números son honestos. |
| 13 | 13-oct | Durante la demo, el modelo final **recalcula en vivo** el riesgo de los clientes afectados por la falla simulada. | Demuestra que es IA real y no una animación. |
| 14 | 13-oct | La base SQLite no se versiona en git. | Se regenera igual en unos 30 segundos con la misma semilla. |
| 15 | 13-oct | Prioridad = **Lempiras en riesgo** = P(churn) × CLV + P(llamada) × costo por llamada. Alta = top 5 %, Media = siguiente 15 %. | Es más fácil de explicar a ejecutivos que un puntaje abstracto. |
| 16 | 13-oct | LLM por defecto: `claude-opus-5-5` con esfuerzo bajo, timeout de 8 s, sin reintentos y con *fallback* del servidor. Se puede cambiar con `TIGO_LLM_MODEL`. | Si tarda o falla, la demo sigue con plantillas. |
| 17 | 13-oct | El escenario optimista se moderó: 25 000 clientes, 12 % de retención y 10 meses. | Con los valores iniciales daba L 194 M, una cifra difícil de defender. |
| 18 | 13-oct | El riesgo en mapas y barras usa una escala de un solo tono (rojos). Las series categóricas usan una paleta validada para daltonismo. | Es la guía de visualización: una magnitud no se pinta con semáforo. |
| 19 | 13-oct | Gráficos sin animación y animaciones CSS que nunca parten de opacidad 0. | Si el navegador o el proyector congelan las animaciones, todo sigue legible. |
| 20 | 13-oct | El lanzador abre `http://127.0.0.1:8000` y no `localhost`. | En algunos equipos `localhost` resuelve primero a IPv6 y la carga se demora. |
| 21 | 13-oct | Los entregables con marca Tigo se manejan como **archivos internos** y no se publican en línea. | Usan la identidad de una empresa real: se comparten solo por canales internos. |
| 22 | 13-oct | Sin el formato oficial, la propuesta usa campos estándar y los datos del participante quedan resaltados en amarillo. | Es fácil de adaptar cuando llegue el formato. |

## v02 (rama `v02`)
| # | Decisión | Motivo |
|---|---|---|
| 23 | Se reenfoca en un **piloto de fallas masivas** con grupo control del 15 %. Churn, retención y cobros pasan a **Fase 2**. | Un comité aprueba un piloto concreto y medible, no una plataforma gigante. |
| 24 | Se mantiene `claude-opus-5-5`, porque **es un ID válido**, y se verifica al arrancar con `models.retrieve`. | Corregir sobre una premisa falsa habría roto la integración. La verificación da el estado real. |
| 25 | TOML en vez de YAML, con la misma estructura (valor, unidad, fuente, bajo/base/alto). | PyYAML no tiene versión para Python 3.15. |
| 26 | Caso base = **solo beneficio duro**. La retención aparece aparte, con margen de contribución, y vale cero hasta medirla. | El ROI de v01 usaba ingreso bruto y sin control. |
| 27 | Los escenarios varían el **efecto y los costos**; el volumen y el costo por llamada quedan en su valor base ("Pon tus números"). | Combinar todos los extremos daba un rango absurdo (−L 4 M a L 54 M). |
| 28 | Criterio GO: reducción ≥ 10 %, por encima del equilibrio del 9 %. *(Actualizado en la decisión 44: ahora 12 %.)* | El GO debe exigir más que el punto de equilibrio. |
| 29 | Métrica norte en **llamadas por 1,000 afectados a 72 h**, con inferencia sobre la media. Secundaria: % que llama (prueba de proporciones). | Cuenta también los reintentos, que son costo real. |
| 30 | Modelo 72 h con **validación temporal** (días 0–59 / 60–89) y calibración isotónica. Se compara contra la regla operativa y el azar. | Es lo que exigiría un comité técnico, y así se ve el valor real del modelo. |
| 31 | La Falla en vivo es un escenario **determinista y sin estado**. Se eliminó la demo SSE vieja. | La demo anterior dejaba el dashboard sucio (331 mensajes, 89 llamadas). |
| 32 | Los guardrails detectan tuteo solo con formas inequívocas ("tú", "tienes", "puedes"…), no "escribe" ni "llama". | "Le escribe Tigo" usa tercera persona; marcarlo daba falsos positivos. |
| 33 | `docs/impacto.md`, `cifras.json` y `listo_para_produccion.md` se generan desde el código, y un test verifica que el pitch, el resumen y el formato usan esas cifras. | Una sola fuente de verdad. |
| 34 | **v03: Hogar primero.** Se agrega el frente Hogar (telemetría de módems → IA de 7 días → corrección remota o visita con diagnóstico); el frente Móvil sigue con el mismo motor. | El análisis de la versión anterior mostró que el caso móvil era chico y la IA poco central. Las visitas técnicas valen mucho más que las llamadas y el mapeo cliente ↔ nodo es exacto. |
| 35 | Se compara la IA contra una **regla de umbrales** realista (señal < 3 dB, ≥ 5 reinicios, ≥ 15 micro-cortes, WiFi > 25 %), no solo contra el azar. Criterio: si con datos reales no le gana por 1.3×, se usa la regla. | Un jurado técnico preguntará por qué no bastan las alarmas del ACS. |
| 36 | Presupuesto del **2 %** de hogares por semana (no 3 %). | Con 2 % la IA captura lo mismo (52 % de las visitas evitables) con mucha más precisión (46 % vs. 31 %): menos mensajes a hogares sin problema. |
| 37 | Hogar solo cuenta en el caso base las visitas **evitables** en hogares marcados a tiempo (30 % × 45 % × 45 % = 6 % del total; con datos reales, 25 % × 45 % × 45 % = 5 %). No cuenta visitas repetidas ni llamadas por problemas físicos. | Conservador: los proveedores declaran hasta 20 % sobre todas las visitas. |
| 38 | Los costos de la plataforma los carga el frente Móvil; Hogar solo suma los incrementales. | Así el frente Móvil queda idéntico a v02 y Hogar se juzga por su aporte marginal. |
| 39 | La demo Hogar usa dos casos **guionados**, pero calificados día a día con el **modelo real** (riesgo, alarma de la regla y explicación SHAP). | Narrativa clara sin inventar resultados del modelo. |
| 40 | **GDPR como estándar de referencia**, además de la Constitución hondureña (arts. 76, 100 y 182) y la política de Millicom. | Honduras no tiene ley integral de datos (proyecto pendiente desde 2018); se adopta el marco más exigente. |
| 41 | Red team propio: 12 ataques confirmados y corregidos, cada uno con prueba de regresión. Roles, sesión revocable, CSRF, anti-phishing, huella SHA-256 de los modelos verificada antes de cargarlos, dependencias fijadas. Sin tokens, el servidor solo atiende a la misma máquina. | La seguridad se demuestra con evidencia y pruebas automáticas, no con promesas. |
| 42 | **Datos reales de Tigo Honduras** como base: 191 mil hogares y 5.0 M de clientes móviles (Millicom 20-F 2025, verificado en EDGAR). | Usar la cifra pública más reciente y verificable. |
| 43 | **Costos hondureños**, no internacionales: visita L 650 (cálculo con salarios, cargas, vehículo y despacho) y llamada L 65 (US$11–16 por hora de agente en Honduras). Visitas evitables 25 % (la industria reporta 17–20 % «sin falla encontrada») y 3 % de visitas por hogar al mes. | Los costos deben reflejar la realidad hondureña; el neto base queda en L 4.3 M con fuentes verificables. |
| 44 | El GO de Móvil sube de 10 % a **12 %**, porque el nuevo punto de equilibrio es 11.5 %. | El GO nunca puede aprobar un efecto que no paga sus costos. |
| 45 | La ventaja de la IA sobre la regla (2.0×) se presenta siempre como **resultado en datos simulados** e hipótesis a validar en las semanas 0–2. | Los datos sintéticos no son evidencia del desempeño real; la validación con datos de Tigo es la que decide. |
