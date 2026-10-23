# Auditoría v02 — estado real del prototipo (13-oct-2026)

Verificación hecha corriendo la app, los tests y la API desde la rama `v02`, creada desde `main` en `2e4c603`.

## Lo que funciona
| Componente | Estado verificado |
|---|---|
| Tests | 52 de pytest y 4 de vitest en verde; ruff y eslint limpios |
| Pipeline de IA | `tareas.ps1 preparar` desde cero en unos 31 s, con resultados idénticos (semilla fija) |
| Modelos (Fase 2) | Incidencia 7 d: AUC 0.864 (baseline 0.843). Churn 30 d: AUC 0.877 (baseline 0.865) |
| Lanzador | `iniciar_demo.bat` arranca en unos 5 s y sirve la API y la interfaz en `127.0.0.1:8000` |
| Sin internet | El mapa usa un GeoJSON local y los mensajes salen de plantillas si no hay clave |

## Problemas confirmados (críticas del documento v02)
| # | Crítica | ¿Es cierta? | Evidencia |
|---|---|---|---|
| 1 | El ROI usa **ingreso bruto** | **Sí** | `roi.py`: `retenidos × ARPU × meses`. En el escenario base, L 56.2 M de L 78.4 M de beneficio son ingresos retenidos brutos y no hay grupo de control |
| 2 | 35 % de llamadas evitadas sin fuente | **Sí** | Los benchmarks reales van de 18 % (KUBRA) a 88 % (MidSouth, n = 99). El 35 % se eligió sin justificarlo |
| 3 | Base de clientes y costo por llamada sin fuente | **En parte** | La base de 5.0 M sí tiene fuente (Millicom 20-F). Los L 85 por llamada son un supuesto derivado de tarifas por hora |
| 4 | **Estado sucio** después de la demo | **Sí** | Después de `/api/demo/stream`, `/api/kpis` queda en 331 mensajes, 89 llamadas evitadas y 1 retenido. `reiniciar()` solo se llama al iniciar la demo |
| 5 | NPS "1.8 → 4.0" poco creíble | **Sí** | La escala es correcta (−100 a +100), pero el "NPS proyectado" es un supuesto sin medición |
| 6 | Nombre de modelo LLM inválido (`claude-opus-5-5`) | **No** | `claude-opus-5-5` es un ID vigente en la lista oficial de modelos de Claude. Lo que falta es **verificarlo al arrancar** y reportar el estado real en `/api/salud`, que hoy solo devuelve `llm_activo` según exista la clave |
| 7 | Modelo apenas mejor que el baseline | **Sí** | +0.02 de AUC en incidencia. No se compara con la regla operativa ("avisar a todos los de la celda caída") |
| 8 | Horizontes mezclados | **Sí** | 7 días (incidencia) y 30 días (churn). No hay una métrica de 72 h posterior a la falla |
| 9 | Sin validación temporal ni calibración | **Sí** | Se usa un solo corte con partición aleatoria. `features.construir` no filtra uso, pagos ni interacciones por `<= corte` |
| 10 | Entregables con cifras viejas | **Sí** | `../entrega/*` dice L 64.9 M y ROI de 4.85×, y debe actualizarse |

## Fuentes nuevas para v02
- WhatsApp Business, plantilla de **utilidad**, Resto de Latinoamérica: unos **US$0.0113 por mensaje** (tarifa del 1-jul-2026 según Zernio; fuente secundaria, verificar con Meta).
- Avisos proactivos: MidSouth (−88 %, n = 99), Convey (−57 %, en una eléctrica con cortes programados) y KUBRA (−18 %). Las tres fuentes son de proveedores. → **Rango usado: 10 % / 20 % / 35 %**.
- No se encontró evidencia pública de que Tigo/Millicom ya avise proactivamente de fallas por WhatsApp. Hay que confirmarlo con Millicom.

## Conclusión
La base técnica es sólida. El relato económico no lo era: mezclaba ingreso bruto, no tenía grupo de control y usaba un supuesto sin fuente. v02 reenfoca el producto en un **piloto de fallas masivas** medible (tratados vs. control a 72 h) y en un **caso de negocio duro** (llamadas evitadas × costo) con rangos, sensibilidad y punto de equilibrio.
