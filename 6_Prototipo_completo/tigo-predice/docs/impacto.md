# Impacto esperado — Tigo Predice v03 (caso conservador)

> Generado con `python -m backend.app.services.roi` desde `config/negocio.toml` (mismas fórmulas que la app).
> **Todos los supuestos son a validar con Tigo.** Cifras redondeadas a 2 cifras significativas.

## Las frases para el comité

- **Hogar:** con solo 9 % menos visitas evitables en los hogares que marca la IA, el frente Hogar se paga en el primer año (incluida su inversión). El caso base supone 45 % (proveedores reportan de 20 % a 60 %).
- **Móvil:** con solo 9 % menos llamadas en los clientes avisados, la plataforma se paga en el primer año. Los benchmarks públicos están entre 18 % y 88 %; el caso base usa 20 %.
- **Total:** neto del año 1 de L 10 M en el escenario base (rango −L 23 mil a L 25 M).

## Caso base = solo beneficio duro

| | Conservador | Base | Optimista |
|---|---|---|---|
| **Hogar** · visitas evitadas al año | 2,700 | 5,200 | 8,500 |
| Hogar · reducción del total de visitas | 3 % | 6 % | 10 % |
| Hogar · beneficio duro anual | L 3.4 M | L 6.6 M | L 11 M |
| Hogar · neto año 1 | L 1.5 M | L 5.4 M | L 10 M |
| **Móvil** · llamadas evitadas al año | 47,000 | 110,000 | 200,000 |
| Móvil · beneficio duro anual | L 4 M | L 9.1 M | L 17 M |
| Móvil · neto año 1 | −L 1.5 M | L 5.1 M | L 15 M |
| Beneficio duro anual (total) | L 7.5 M | L 16 M | L 28 M |
| Costo recurrente anual (total) | L 4.7 M | L 3.6 M | L 2 M |
| Inversión única (integración) | L 2.8 M | L 1.7 M | L 1.1 M |
| **Neto año 1 (total)** | **−L 23 mil** | **L 10 M** | **L 25 M** |
| Neto anual en régimen (año 2+) | L 2.8 M | L 12 M | L 26 M |
| Recuperación de la inversión | 12 meses | 2 meses | 1 meses |
| Equilibrio Hogar: reducción mínima de visitas evitables (año 1) | 17 % | 9 % | 4 % |
| Equilibrio Móvil: reducción mínima de llamadas (año 1) | 14 % | 9 % | 5 % |

Hogar cuenta solo visitas evitables (WiFi, firmware, «sin falla encontrada») en hogares que la IA marcó a tiempo, más las llamadas asociadas a esas visitas. No cuenta las visitas repetidas evitadas ni las llamadas que se evitan al avisar problemas físicos.

## Piloto de 60 días en San Pedro Sula

| | Conservador | Base | Optimista |
|---|---|---|---|
| Hogar · hogares marcados (acciones) | 6,900 | 6,900 | 6,900 |
| Hogar · visitas evitadas | 92 | 180 | 290 |
| Móvil · afectados en 60 días | 48,000 | 48,000 | 48,000 |
| Móvil · llamadas evitadas | 1,400 | 3,200 | 6,100 |
| Beneficio duro | L 240 mil | L 500 mil | L 880 mil |
| Costo total del piloto | L 1.2 M | L 770 mil | L 470 mil |

El piloto **no busca pagarse en 60 días**: busca **medir** con grupo de control si el efecto supera el punto de equilibrio. Si da GO, la escala nacional se paga sola.

## Potencial NO incluido en el caso base

- Retención: L 3.4 M al año de **margen** (no ingreso bruto) si el piloto mide 0.2 puntos menos de churn mensual en avisados vs. control. Hasta medirlo, vale cero.
- Hogar: visitas repetidas evitadas (el técnico llega con el diagnóstico) y llamadas evitadas al avisar problemas físicos. Se miden en el piloto, no se cuentan.
- NPS/CSAT de afectados: se mide en el piloto, no se monetiza.

## Sensibilidad (tornado): qué supuestos mueven más el neto total del año 1

| Supuesto | Bajo → neto | Alto → neto | Fuente |
|---|---|---|---|
| reduccion_con_aviso (0.1 / 0.35) | L 5.9 M | L 17 M | benchmark público |
| afectados_mes_nacional (60000 / 200000) | L 6.5 M | L 16 M | supuesto a validar |
| costo_por_llamada (55 / 120) | L 6.9 M | L 15 M | supuesto a validar |
| tasa_visitas_hogar_mes (0.03 / 0.06) | L 8.5 M | L 13 M | supuesto a validar |
| pct_visitas_evitables (0.2 / 0.4) | L 8.3 M | L 13 M | supuesto a validar |
| reduccion_visitas_marcados (0.3 / 0.6) | L 8.3 M | L 13 M | benchmark público |
| tasa_llamada_72h (0.25 / 0.4) | L 8.3 M | L 12 M | benchmark público |
| costo_por_visita (800 / 1500) | L 8.9 M | L 13 M | supuesto a validar |
| captura_modelo_hogar (0.35 / 0.55) | L 9 M | L 12 M | supuesto a validar |
| llamadas_por_cliente_que_llama (1.2 / 1.6) | L 9.2 M | L 12 M | supuesto a validar |

## Supuestos

| Supuesto | Unidad | Bajo | Base | Alto | Fuente | Nota |
|---|---|---|---|---|---|---|
| fallas_mes_piloto | fallas masivas por mes en la ciudad piloto | 4 | 8 | 12 | supuesto a validar | Caídas o degradación de sitios que afectan a muchos clientes (energía, fibra, clima). Dato del NOC. |
| afectados_por_falla | clientes afectados por falla | 1500 | 3000 | 5000 | supuesto a validar | Depende de cuántos sitios caen y cuánto dura. Dato del NOC/OSS. |
| afectados_mes_nacional | clientes afectados por fallas masivas al mes (todo el país) | 60000 | 120000 | 200000 | supuesto a validar | ~1–4 % de 5.2 M clientes afectados por alguna falla masiva al mes. |
| tasa_llamada_72h | % de afectados que llama en 72 h si NO recibe aviso | 0.25 | 0.33 | 0.4 | benchmark público | MidSouth Fiber: 33 % de suscriptores sin alerta llamó durante la falla (Calix, 2024; n = 99). |
| llamadas_por_cliente_que_llama | llamadas por cliente que llama (incluye reintentos) | 1.2 | 1.4 | 1.6 | supuesto a validar | Los clientes afectados suelen llamar más de una vez. Dato del call center/IVR. |
| reduccion_con_aviso | reducción relativa de llamadas en quienes reciben el aviso | 0.1 | 0.2 | 0.35 | benchmark público | Rango conservador: KUBRA −18 %, Convey −57 % (eléctrica), MidSouth −88 % (n = 99). Todos de proveedores; el piloto lo mide. |
| tasa_entrega | % de tratados que efectivamente recibe y lee el aviso | 0.75 | 0.85 | 0.92 | supuesto a validar | Clientes con WhatsApp activo y sin opt-out. Dato de canales digitales. |
| costo_por_llamada | L por llamada atendida (costo total) | 55 | 85 | 120 | supuesto a validar | Hora de agente LATAM US$12–24 todo incluido ÷ ~8 llamadas efectivas/h ≈ US$3.15 (FusionCX, Retell AI 2026). Dato de Finanzas/CX. |
| tipo_cambio | L por US$ | 26.5 | 27.0 | 27.5 | benchmark público | BCH, octubre 2026. |
| costo_whatsapp_mensaje | L por mensaje (plantilla de utilidad) | 0.25 | 0.31 | 0.4 | benchmark público | ≈ US$0.0113 por plantilla de utilidad, Resto de Latinoamérica, tarifa jul-2026 (Zernio; verificar con Meta). |
| desarrollo_piloto | L, una vez (integración batch CSV + configuración) | 150000 | 250000 | 400000 | supuesto a validar | El piloto arranca con exportaciones CSV diarias, sin integraciones en tiempo real. |
| equipo_piloto | L por 60 días (horas internas NOC, CX, Data, Legal) | 100000 | 150000 | 250000 | supuesto a validar | Analista de datos a medio tiempo + enlaces del NOC y CX. |
| infraestructura_mes | L por mes (nube, LLM, monitoreo) | 20000 | 30000 | 50000 | supuesto a validar | Servidor pequeño + base de datos + llamadas al LLM (centavos por mensaje). |
| desarrollo_nacional | L, una vez (integración en tiempo real OSS/CRM/WhatsApp) | 600000 | 900000 | 1500000 | supuesto a validar | Solo si el piloto da GO. |
| operacion_anual | L por año (operación y mantenimiento) | 800000 | 1200000 | 1600000 | supuesto a validar | 1 analista/científico de datos + soporte + reentrenamiento mensual. |
| pct_compensados | % de afectados que recibe compensación (GB) | 0.0 | 0.05 | 0.1 | supuesto a validar | Solo fallas largas o clientes priorizados por el modelo; siempre con tope. |
| costo_compensacion | L por cliente compensado (costo interno de 2 GB) | 8 | 16 | 25 | supuesto a validar | Costo marginal interno, no precio de venta. |
| hogares_piloto | hogares (fibra/HFC) en la ciudad piloto | 25000 | 40000 | 50000 | supuesto a validar | Tigo Hogar tiene ~175 mil hogares (Millicom 20-F 2025); se asume ~1 de cada 4 en San Pedro Sula. Dato de Tigo Hogar. |
| tasa_visitas_hogar_mes | visitas técnicas por hogar al mes | 0.03 | 0.043 | 0.06 | supuesto a validar | ≈ 7,500 visitas/mes sobre 175 mil hogares (3 % a 6 %). Dato de operaciones de campo. |
| pct_visitas_evitables | % de visitas evitables (resolubles a distancia o sin falla encontrada) | 0.2 | 0.3 | 0.4 | supuesto a validar | Códigos de cierre: WiFi/configuración, firmware, reinicio, «sin falla encontrada». Dato de cierres de visitas. |
| llamadas_por_visita | llamadas del cliente por cada visita (reporte + seguimiento) | 1.5 | 2.0 | 2.5 | supuesto a validar | Dato del call center de Hogar. |
| captura_modelo_hogar | % de visitas evitables que ocurren en hogares que la IA marcó a tiempo | 0.35 | 0.45 | 0.55 | supuesto a validar | Con presupuesto del 2 % de hogares por semana. Se valida con 3 meses de telemetría real (análisis retrospectivo). |
| reduccion_visitas_marcados | reducción de visitas evitables en hogares marcados y corregidos a distancia | 0.3 | 0.45 | 0.6 | benchmark público | Proveedores reportan −20 % (Beegol, todas las visitas) a −60 % (Ksolves, visitas innecesarias); cifras autodeclaradas. El piloto lo mide. |
| costo_por_visita | L por visita técnica (técnico, vehículo, tiempo) | 800 | 1100 | 1500 | supuesto a validar | Dato de Finanzas / operaciones de campo. |
| desarrollo_hogar_piloto | L, una vez (CSV diario de telemetría del ACS / gestor de OLT y CMTS + modelo) | 100000 | 150000 | 250000 | supuesto a validar | Sin integración en tiempo real: exportación diaria y acciones remotas que ejecuta soporte nivel 2. |
| equipo_hogar_piloto | L por 60 días (enlace de ingeniería de acceso + soporte remoto nivel 2) | 60000 | 100000 | 150000 | supuesto a validar | Horas internas adicionales al equipo del piloto móvil. |
| desarrollo_hogar_nacional | L, una vez (integración con ACS TR-069, OLT/CMTS y acciones remotas automáticas) | 500000 | 800000 | 1300000 | supuesto a validar | Solo si el piloto Hogar da GO. |
| operacion_hogar_anual | L por año (incremental: reentrenamiento y soporte de la integración) | 250000 | 400000 | 600000 | supuesto a validar | Se suma a la operación de la plataforma (que ya carga el frente móvil). |
| margen_contribucion | % del ARPU que es margen de contribución | 0.45 | 0.55 | 0.65 | supuesto a validar | Para estimar retención con margen, no con ingreso bruto. Dato de Finanzas. |
| churn_incremental_evitado | reducción absoluta de churn mensual en afectados avisados vs. control | 0.0 | 0.002 | 0.005 | supuesto a validar | Solo se acredita si el piloto lo mide frente al control. |
| arpu_afectado | L por mes | 160 | 220 | 300 | supuesto a validar | ARPU grupo Millicom ~US$6.2 ≈ L 167 (20-F 2025); afectados incluyen hogar. |
