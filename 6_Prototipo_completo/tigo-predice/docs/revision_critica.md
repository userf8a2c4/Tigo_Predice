# Datos reales, supuestos y riesgos

Este documento reúne los datos públicos de Tigo Honduras y del mercado hondureño que usa el caso de negocio, los supuestos que todavía hay que validar con Tigo y los riesgos identificados con su mitigación. Los supuestos sin fuente pública están marcados como **«supuesto a validar»** y encabezan la lista de datos a solicitar.

## 1. Tigo Honduras en datos públicos

| Dato | Valor | Fuente |
|---|---|---|
| Clientes móviles | 5.0 millones (el mayor operador móvil del país) | Millicom, Form 20-F 2025 |
| Relaciones de clientes de hogar | 191 mil (184 mil en 2024: +3.8 %); el mayor proveedor de banda ancha | Millicom, Form 20-F 2025 y 2024 |
| Estructura | Empresa conjunta (Celtel); Millicom tiene el 66.67 % | Millicom, Form 20-F 2025 |
| Ingresos | US$158 M en el 1T-2026 (US$150 M de servicios); margen EBITDA del 51.6 % | Millicom, 6-K del 1T-2026 |
| Inversión anunciada | US$1,000 M en cinco años, sobre todo en red | DCD, BNamericas |
| Mercado de internet fijo | ~505 mil suscriptores (1T-2025, +14 % anual) | CONATEL, vía DPL News |
| Líneas móviles del país | 6.9 millones (3T-2025) | CONATEL, vía DPL News |
| Planes de internet hogar | L 599 (100 Mbps) a L 1,399 (400 Mbps) al mes | tigo.com.hn |
| Salario mínimo promedio 2026 | L 14,917.20 | Secretaría de Trabajo, La Gaceta |
| Ley de datos personales | Sigue sin aprobarse (proyecto pendiente desde 2018) | IAIP, El Heraldo |

**Escala:** los ingresos por servicios de Tigo Honduras rondan US$600 M al año, unos L 16 mil millones. El beneficio neto base de Tigo Predice (L 4.3 M en el año 1) cubre su propio costo; su valor principal es la experiencia del cliente: menos fallas sufridas, menos llamadas y menos visitas.

## 2. Supuestos del caso de negocio (escenario base)

| Supuesto | Valor usado | Rango | Fuente o cálculo |
|---|---|---|---|
| Hogares de Tigo Honduras | 191 mil | — | Millicom, Form 20-F 2025 |
| Visitas técnicas por hogar al mes | 3 % (≈ 5,700 al mes) | 2 % a 4.5 % | Supuesto a validar con operaciones de campo; no hay un referente público confiable |
| Visitas evitables | 25 % | 17 % a 35 % | La industria estima que el 17–20 % de las visitas termina «sin falla encontrada», más los problemas de WiFi y firmware que se resuelven a distancia |
| Costo por visita evitable | L 650 | L 450 a L 1,000 | Cálculo con costos hondureños: técnico, cargas sociales, vehículo, combustible y despacho, a unas 4.5 visitas por día |
| Costo por llamada atendida | L 65 | L 40 a L 95 | Centro de contacto en Honduras: US$11–16 por hora de agente, todo incluido, con 5–7 llamadas técnicas por hora |
| WhatsApp por mensaje | L 0.31 | L 0.30 a L 0.36 | Tarifa de utilidad de octubre de 2026: US$0.0113–0.0130 |
| Tipo de cambio | L 27.0 por US$ | L 26.8 a L 27.3 | BCH: L 26.87 compra y L 27.01 venta (7 de septiembre de 2026) |
| ARPU de hogar | L 800 | — | Planes publicados en tigo.com.hn |
| Criterio GO de Móvil | −12 % de llamadas | — | Al menos el punto de equilibrio (11.5 %) |

**Resultado:** el escenario base deja **L 4.3 M netos en el año 1**, con un rango de −L 3 M a L 14 M. Hogar se paga con 22 % menos visitas evitables en los hogares marcados y Móvil con 12 % menos llamadas. El piloto cuesta L 770 mil.

## 3. Riesgos identificados y mitigación

| # | Riesgo | Mitigación |
|---|---|---|
| 1 | La frecuencia real de visitas técnicas puede diferir del supuesto | Es el primer dato a solicitar a operaciones de campo; el caso se recalcula con él |
| 2 | La ventaja de la IA sobre la regla de umbrales (2.0×) proviene de datos simulados | Se valida en las semanas 0–2 con 3 meses de telemetría real; si la IA no supera a la regla por 1.3×, se usa la regla |
| 3 | Los efectos de referencia (avisos de −18 % a −88 %; visitas de −20 % a −60 %) son de proveedores y algunos con muestras pequeñas | El caso base usa valores conservadores y el piloto mide el efecto real con grupo control |
| 4 | Se desconoce qué parte de los módems reporta telemetría (TR-069 en GPON, CMTS en HFC) | Pregunta para ingeniería de acceso; si la cobertura es menor, el beneficio de Hogar se ajusta en proporción |
| 5 | Capacidad operativa: el 2 % semanal equivale a ~3,800 hogares por semana en el país y ~800 en San Pedro Sula | En el piloto, ~160 acciones por día hábil (2–3 agentes de soporte nivel 2 o lotes del ACS); a nivel nacional, con acciones automáticas |
| 6 | El costo por llamada depende de si el centro de contacto es propio o tercerizado y de cuánto resuelve el IVR | Dato a solicitar a Finanzas/CX; el análisis de sensibilidad lo muestra entre las tres variables que más pesan |
| 7 | Desde octubre de 2026 Meta cobra también los mensajes de servicio | Incluido en el rango de costo de mensajería |
| 8 | En el escenario conservador, escalar sin validar podría perder hasta L 3 M | Por eso se propone primero un piloto acotado de L 770 mil con criterios GO / NO-GO |

## 4. Lo que más mueve el resultado (análisis de sensibilidad, escenario base)

| Supuesto | Neto año 1 con valor bajo | con valor alto |
|---|---|---|
| Reducción de llamadas con aviso (10 % a 35 %) | L 0.8 M | L 9.5 M |
| Afectados por fallas masivas al mes (60 mil a 200 mil) | L 1.4 M | L 8.4 M |
| Costo por llamada (L 40 a L 95) | L 1.4 M | L 7.7 M |
| Tasa de llamadas en 72 h sin aviso (25 % a 40 %) | L 2.6 M | L 5.8 M |
| Visitas técnicas por hogar al mes (2 % a 4.5 %) | L 3.4 M | L 5.6 M |

**Conclusión:** los cinco datos que más importan son el efecto real del aviso (lo mide el piloto), el volumen de afectados por fallas masivas (NOC), el costo por llamada (Finanzas), la tasa de llamadas sin aviso (centro de contacto) y la frecuencia de visitas (campo). Están al principio de [datos_a_pedir_a_tigo.md](datos_a_pedir_a_tigo.md).

## Fuentes
- Millicom, Form 20-F 2025 (SEC): https://www.sec.gov/Archives/edgar/data/912958/000162828026020831/tigo-20251231.htm
- Millicom, 6-K del 1T-2026 (SEC): https://www.sec.gov/Archives/edgar/data/912958/000095010326007169/dp246578_6k.htm
- CONATEL vía DPL News: https://dplnews.com/honduras-alcanza-record-de-suscriptores-internet-fijo/ y https://dplnews.com/suscriptores-telefonia-movil-siguen-a-la-baja-honduras/
- Planes de Tigo Honduras: https://www.tigo.com.hn/internet
- BCH vía El Heraldo: https://www.elheraldo.hn/economia/precio-dolar-hoy-lunes-7-septiembre-honduras-FI31934818
- Salario mínimo 2026: https://www.elheraldo.hn/economia/salario-minimo-promedio-2026-honduras-reporte-trabajadores-HD30554388
- Costos de centros de contacto en Honduras: https://globalify.com/countries/honduras y https://www.tdsgs.com/call-center-outsourcing/honduras
- Visitas «sin falla encontrada»: https://www.firstsource.com/insights/glossary/truck-roll-reduction y https://techsee.com/blog/reduce-truck-rolls/
- Costo de una visita (EE. UU.): https://aexinc.com/blog/truck-roll-cost-benchmarks-fiber
- Tarifas de WhatsApp Business: https://zernio.com/blog/whatsapp-business-api-pricing y https://help.sleekflow.io/en_US/whatsapp/pricing
- Inversión de Tigo en Honduras: https://www.datacenterdynamics.com/en/news/honduras-boosts-its-digital-infrastructure-with-a-1-billion-investment-from-tigo/
- Ley de datos personales: https://www.elheraldo.hn/honduras/iaip-destaca-beneficios-honduras-ley-proteccion-datos-personales-BP26294115
