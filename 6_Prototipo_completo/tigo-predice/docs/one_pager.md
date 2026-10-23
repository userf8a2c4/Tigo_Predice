# Tigo Predice — resumen ejecutivo para el comité

**Los chatbots y copilotos atienden la llamada. Tigo Predice evita que ocurra.**
*La IA que detecta el problema antes que el cliente, y lo resuelve antes de que llame o de que haya que mandar un técnico.*

**Problema.**
- **Hogar:** los módems avisan días antes de fallar (señal que baja, WiFi saturado, reinicios), pero hoy solo se mira cuando cruza un umbral. El cliente llama y se manda un técnico, aunque 1 de cada 4 visitas es evitable (supuesto; la industria reporta 17–20 % «sin falla encontrada»).
- **Móvil:** cuando cae un sitio, 1 de cada 3 afectados llama si no recibe aviso (benchmark público).

**Solución (piloto Fase 1, San Pedro Sula, 60 días).**
- **Hogar (frente principal).** Cada semana la IA califica la telemetría de todos los módems y marca al **2 %** con más riesgo, con su porqué. Si es WiFi o firmware, se **corrige a distancia** y el cliente recibe un WhatsApp. Si es físico, la visita se agenda antes del corte y con el diagnóstico.
- **Móvil.** En fallas masivas, WhatsApp en minutos con la causa y la hora del NOC (solo si la tiene) y un mensaje de cierre.
- **Medición.** En ambos frentes, un **15 % de control** aleatorio mide el efecto real.

**Métricas norte.** Visitas técnicas por cada 1,000 hogares marcados (7 días) y llamadas por cada 1,000 afectados (72 h), tratados vs. control.

| | Valor | Nota |
|---|---|---|
| Neto año 1 (Hogar + Móvil, base) | **L 4.3 M** | Rango −L 3 M a L 14 M · solo beneficio duro, costos hondureños |
| Neto anual en régimen | **L 6 M** | Año 2 en adelante |
| Punto de equilibrio | Hogar **22 %** · Móvil **12 %** | Reducción mínima para que cada frente se pague en el año 1 |
| IA vs. regla de umbrales | **2.0×** | Anticipa 52 % de las visitas evitables vs. 26 % (datos simulados; se valida en las semanas 0–2) |
| Visitas evitadas al año (Hogar) | **3,300** | Rango 1,700 a 5,400 · solo 5 % del total de visitas |
| Llamadas evitadas al año (Móvil) | **110,000** | Rango 47,000 a 200,000 |
| Inversión del piloto (60 días) | **L 770 mil** (≈ US$ 28 mil) | Rango L 480 mil a L 1.2 M |
| Simulación del piloto | Hogar **−19 %** visitas · Móvil **−16 %** llamadas | Efectos supuestos; **resultado simulado** |
| Potencial no incluido | L 3.4 M al año en retención (margen) | Vale cero hasta medirlo contra el control |

**Criterios de decisión (semana 12, por frente).**
- **Hogar:** GO si las visitas bajan ≥ 15 %, de forma significativa y con opt-out < 2 %. Si la IA no supera a la regla por 1.3×, se usa la regla.
- **Móvil:** GO si las llamadas bajan ≥ 12 % (su punto de equilibrio), de forma significativa y con opt-out < 2 %.

**Seguridad y privacidad (vara de hiperescalador).**
- No se lee contenido, navegación ni los dispositivos del cliente.
- GDPR como estándar, porque Honduras aún no tiene ley integral, más ISO 27001/27701/42001, SOC 2 y OWASP.
- Datos mínimos, sesión segura y bitácoras.
- Evaluación de impacto aprobada antes del primer mensaje.

**Pedido.** 12 semanas, más:
- CSV diarios del NOC, ACS/OLT, CRM, call center y órdenes de campo;
- un patrocinador, enlaces del NOC y de ingeniería de acceso, soporte nivel 2 y un analista de datos al 50 %;
- plantillas de WhatsApp Business y visto bueno de Legal;
- L 770 mil.

**Fase 2 (visión).** Churn, retención y cobros, solo después de medir la Fase 1.

*Datos simulados — supuestos a validar con Tigo. Fuentes: docs/fuentes.md.*
