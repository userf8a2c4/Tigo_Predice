# PLAN v02 — de demo a caso de inversión

> *"Los chatbots y copilotos atienden la llamada. Tigo Predice evita que ocurra."*

Rama: `v02` · Auditoría: [AUDITORIA_v02.md](AUDITORIA_v02.md)

| Fase | Contenido | Estado |
|---|---|---|
| A | Configuración como única fuente de verdad: cada supuesto con valor, unidad, fuente y rango | ✅ |
| B | Experimento: asignación por hash, análisis con IC 95 % y valor p, potencia, simulación del piloto y GO/NO-GO | ✅ |
| C | Modelo 72 h tras la falla: validación temporal, calibración, estrategias frente a la regla y sesgo | ✅ |
| D | ROI duro (llamadas × costo), costos completos, escenarios, tornado, equilibrio y "Pon tus números" | ✅ |
| E | Backend: estado limpio, `/api/falla/simular`, endpoints del piloto, verificación del LLM y bitácora | ✅ |
| F | Frontend: Inicio, Falla en vivo ★, Resultados del piloto, Caso de negocio, Modelo, Producción y Fase 2 | ✅ |
| G | Documentos y entregables actualizados | ✅ |
| H | Tests, 3 corridas de la demo sin internet, consistencia de cifras y resumen | ✅ |

## v03 (14/10/2026) · todo completado

| Fase | Contenido | Estado |
|---|---|---|
| I | Frente Hogar: telemetría de módems, modelo de 7 días vs. regla de umbrales, simulación del piloto con control | ✅ |
| J | Caso de negocio por frente (Hogar + Móvil), «Pon tus números» con 4 datos de Tigo | ✅ |
| K | Demo «Hogar en vivo» con explicación SHAP y lista de trabajo diaria | ✅ |
| L | Seguridad y privacidad: red team propio (12 ataques corregidos), roles, firma de modelos, GDPR como estándar | ✅ |
| M | Entregables v03: Word, PowerPoint, one-pager, correo, elevator pitch, preguntas frecuentes y guía visual | ✅ |
| N | Pipeline reproducible desde cero (mismas huellas SHA-256) y más de 200 pruebas automáticas | ✅ |
