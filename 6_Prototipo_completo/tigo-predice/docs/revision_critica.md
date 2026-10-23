# Revisión crítica y datos reales (22 de octubre de 2026)

Esta revisión contrasta cada supuesto del sistema con datos públicos de Tigo Honduras, de Millicom y del mercado hondureño, y lista los puntos débiles que encontramos. Hay supuestos que no tienen fuente pública; esos siguen marcados como **«supuesto a validar»** y encabezan la lista de datos a pedir a Tigo.

## 1. Qué cambió en los números

| Supuesto | Antes | Ahora | Por qué |
|---|---|---|---|
| Hogares de Tigo Honduras | 175 mil | **191 mil** | El 20-F 2025 de Millicom dice 191,000 relaciones de clientes de hogar (184,000 en 2024). El dato anterior era un error nuestro. |
| Visitas técnicas por hogar al mes | 4.3 % (7,500/mes) | **3 % (≈ 5,700/mes)** | No hay un benchmark público confiable; bajamos al centro de un rango prudente y lo marcamos como el primer dato a pedir. |
| Visitas evitables | 30 % | **25 %** (17 % a 35 %) | La industria estima que el 17–20 % de las visitas termina «sin falla encontrada»; se suman los problemas de WiFi y firmware que se resuelven a distancia. |
| Costo por visita evitable | L 1,100 | **L 650** (L 450 a L 1,000) | Cálculo con costos hondureños: técnico, cargas sociales, vehículo, combustible y despacho, a unas 4.5 visitas por día. |
| Costo por llamada atendida | L 85 | **L 65** (L 40 a L 95) | Un centro de contacto en Honduras cuesta US$11–16 por hora de agente, todo incluido; con 5–7 llamadas técnicas por hora sale ≈ US$2.4. |
| WhatsApp por mensaje | L 0.25 a L 0.40 | **L 0.30 a L 0.36** | Tarifa de utilidad de octubre de 2026: US$0.0113–0.0130. Desde ese mes Meta también cobra los mensajes de servicio. |
| Tipo de cambio | L 27.0 | **L 27.0** (L 26.8 a L 27.3) | BCH: L 26.87 compra y L 27.01 venta (7 de septiembre de 2026). |
| ARPU de hogar (Fase 2) | L 950 | **L 800** | Planes publicados en tigo.com.hn: L 599 (100 Mbps) a L 1,399 (400 Mbps), con ISV. |
| Criterio GO de Móvil | −10 % de llamadas | **−12 %** | Con costos reales, Móvil se paga con 11.5 %; el GO no puede exigir menos que el punto de equilibrio. |

**Resultado:**
- **Neto del año 1 (escenario base):** pasa de L 10 M a **L 4.3 M**. El rango va de −L 3 M a L 14 M.
- **Punto de equilibrio:** Hogar ahora se paga con 22 % menos visitas evitables en los hogares marcados (antes 9 %), y Móvil con 12 % menos llamadas (antes 9 %).
- **Piloto:** sigue costando L 770 mil.

El caso es más chico, pero cada cifra se puede defender frente a un comité.

## 2. Tigo Honduras en datos públicos

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

**Escala:** los ingresos por servicios de Tigo Honduras rondan US$600 M al año, unos L 16 mil millones. El neto base de Tigo Predice (L 4.3 M) es cerca del **0.03 %** de esos ingresos. Hay que decirlo con naturalidad: el valor principal es la experiencia del cliente, con menos fallas sufridas, llamadas y visitas, y el ahorro alcanza para que el proyecto se pague solo.

## 3. Puntos débiles y qué hicimos

| # | Punto débil | Riesgo | Estado |
|---|---|---|---|
| 1 | Base de hogares mal citada (175 mil en lugar de 191 mil) | Pierde credibilidad si el jurado conoce el dato | **Corregido** |
| 2 | Costos de visita y llamada con niveles de otros países | Infla el ahorro un 40–70 % | **Corregido** con cálculo hondureño y rangos |
| 3 | 30 % de visitas evitables, por encima del benchmark (17–20 % sin falla) | Infla el ahorro de Hogar | **Corregido** a 25 % |
| 4 | Frecuencia de visitas (4.3 % al mes) sin respaldo | Es una de las variables más sensibles | **Mitigado:** baja a 3 % y es el primer dato a pedir |
| 5 | El GO de Móvil (10 %) quedaba por debajo del nuevo equilibrio (11.5 %) | Se podría «aprobar» algo que pierde plata | **Corregido** a 12 % |
| 6 | «En el peor escenario queda en equilibrio» ya no es cierto: el conservador da −L 3 M | Afirmación falsa frente al jurado | **Corregido:** el mensaje ahora es que un piloto de L 770 mil evita apostar L 1.7 M a ciegas |
| 7 | La ventaja de la IA sobre la regla (2.0×) sale de datos sintéticos donde nosotros pusimos la señal | No es evidencia; un jurado técnico lo detecta | **Mitigado:** se presenta como hipótesis y se valida en las semanas 0–2 con 3 meses de telemetría real; si no gana por 1.3×, se usa la regla |
| 8 | Los efectos de referencia son de proveedores (avisos −18 % a −88 %; visitas −20 % a −60 %) y algunos con muestras chicas (MidSouth, n = 99) | Pueden estar sesgados al alza | **Mitigado:** el caso base usa el extremo bajo y el piloto lo mide con grupo control |
| 9 | No sabemos qué parte de los módems reporta telemetría (TR-069 en GPON, CMTS en HFC) | Si la cobertura es baja, el beneficio de Hogar baja en proporción | **Pendiente:** pregunta para ingeniería de acceso |
| 10 | Capacidad operativa: el 2 % semanal son ~3,800 hogares por semana en el país y ~800 en San Pedro Sula | Hecho a mano no escala | **Mitigado:** en el piloto, ~160 acciones por día hábil (2–3 agentes de soporte nivel 2 o lotes del ACS); a nivel nacional, solo con acciones automáticas |
| 11 | El costo por llamada depende de si el call center es propio o tercerizado y de cuánto resuelve el IVR | Puede cambiar el caso de Móvil | **Pendiente:** dato de Finanzas/CX; el tornado ya lo muestra entre las tres variables que más pesan |
| 12 | Desde octubre de 2026 Meta cobra también los mensajes de servicio | Sube un poco el costo de mensajería | **Incluido** en el rango (L 0.30 a L 0.36) |

## 4. Lo que más mueve el resultado (tornado, escenario base)

| Supuesto | Neto año 1 con valor bajo | con valor alto |
|---|---|---|
| Reducción de llamadas con aviso (10 % a 35 %) | L 0.8 M | L 9.5 M |
| Afectados por fallas masivas al mes (60 mil a 200 mil) | L 1.4 M | L 8.4 M |
| Costo por llamada (L 40 a L 95) | L 1.4 M | L 7.7 M |
| Tasa de llamadas en 72 h sin aviso (25 % a 40 %) | L 2.6 M | L 5.8 M |
| Visitas técnicas por hogar al mes (2 % a 4.5 %) | L 3.4 M | L 5.6 M |

**Conclusión:** los cinco datos que más importan son el efecto real del aviso (lo mide el piloto), el volumen de afectados por fallas masivas (NOC), el costo por llamada (Finanzas), la tasa de llamadas sin aviso (call center) y la frecuencia de visitas (campo). Están al principio de [datos_a_pedir_a_tigo.md](datos_a_pedir_a_tigo.md).

## Fuentes de esta revisión
- Millicom, Form 20-F 2025 (SEC): https://www.sec.gov/Archives/edgar/data/912958/000162828026020831/tigo-20251231.htm (191,000 relaciones de hogar; 5.0 M móviles; empresa conjunta del 66.67 %). Verificado con la búsqueda de texto completo de EDGAR.
- Millicom, 6-K del 1T-2026 (SEC): https://www.sec.gov/Archives/edgar/data/912958/000095010326007169/dp246578_6k.htm (ingresos de Honduras de US$158 M; EBITDA del 51.6 %).
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
