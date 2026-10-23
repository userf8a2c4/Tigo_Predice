# Preguntas frecuentes del jurado — y cómo responderlas

**Tigo Predice** · Guía para la ronda de preguntas de los Sharks.

## Cómo usar este documento
Cada pregunta tiene tres partes:
- **Respuesta corta:** lo que se dice primero, en unos 10 segundos.
- **Si piden más:** el detalle, solo si el jurado insiste.
- **Muéstrelo:** la pantalla de la app que lo prueba.

**Reglas de oro**
1. **Corto, honesto y con número.** Primero la respuesta, después el detalle.
2. Si no lo sabe: *«No lo sé todavía; el piloto está diseñado para medirlo.»* Nunca invente una cifra.
3. Diga **«supuesto»** y **«simulado»** sin pedir disculpas: es su ventaja frente a propuestas infladas.
4. Si la pregunta es una crítica justa, **dé la razón primero** («Es un buen punto…») y luego responda.
5. **Nunca diga** «garantizado», «seguro», «sin riesgo» ni «100 %».

**Cifras para tener a mano**

| Tema | Cifra |
|---|---|
| Tigo Honduras (datos públicos) | **5.0 M** clientes móviles · **191 mil** hogares · ~US$600 M de ingresos por servicios al año (Millicom 2025–2026) |
| Neto año 1 (Hogar + Móvil, base) | **L 4.3 M** · rango −L 3 M a L 14 M |
| Punto de equilibrio | Hogar **22 %** de las visitas evitables · Móvil **12 %** de las llamadas |
| IA vs. regla de umbrales | **52 % vs. 26 %** de las visitas evitables (2.0×, en datos simulados); el 51 % sin ninguna alarma previa |
| Piloto Hogar simulado | **−19 %** visitas (IC 95 % 12–25 %) · −56 % llamadas técnicas |
| Piloto Móvil simulado | **−16 %** llamadas (IC 95 % 12–19 %) |
| Inversión del piloto | **L 770 mil** (≈ US$ 28 mil) · 12 semanas · San Pedro Sula |
| Supuestos clave | visita **L 650** · llamada **L 65** · ~5,700 visitas al mes · 25 % evitables |

---

## A. La idea

**1. ¿Qué es Tigo Predice, en una frase?**
- **Respuesta corta:** Una IA que detecta en la telemetría del módem que un hogar va a fallar y lo corrige a distancia antes de que el cliente llame o haya que mandar un técnico.
- **Si piden más:** Cada semana marca al 2 % de hogares con más riesgo y explica por qué. El mismo motor avisa en fallas masivas móviles.
- **Muéstrelo:** Hogar en vivo.

**2. ¿Por qué no un chatbot?**
- **Respuesta corta:** El chatbot atiende al cliente cuando ya está molesto; Tigo Predice evita que llegue a estarlo.
- **Si piden más:** Se complementan: si el cliente responde el WhatsApp, el asistente lo atiende y, si hace falta, pasa el caso a un agente con el resumen.

**3. Esto ya existe (Xfinity, AT&T). ¿Qué tiene de nuevo?**
- **Respuesta corta:** Es cierto, y eso baja el riesgo: es una práctica probada que Tigo Honduras aún no tiene (a confirmar internamente).
- **Si piden más:** Lo nuevo es medirla desde el día 1 con grupo control y exigir que la IA le gane a la regla actual. No traemos una promesa, traemos un experimento.

**4. ¿Por qué Hogar primero y no Móvil?**
- **Respuesta corta:** Una visita técnica vale mucho más que una llamada, y en hogar sabemos exactamente de qué nodo cuelga cada módem.
- **Si piden más:** Además, predecir qué hogar va a fallar es machine learning de verdad. Y el hogar con fibra es donde Tigo crece.

**5. ¿Qué gana el cliente?**
- **Respuesta corta:** No sufre la falla, no tiene que llamar y, si hace falta un técnico, va una sola vez.
- **Si piden más:** El CSAT y las visitas repetidas se miden en el piloto como métricas secundarias.

## B. La inteligencia artificial

**6. ¿Por qué no bastan las alarmas por umbral que ya tiene el ACS?**
- **Respuesta corta:** En nuestra simulación, con el mismo presupuesto, la regla anticipa el 26 % de las visitas evitables y la IA el 52 %.
- **Si piden más:** El 51 % de lo que anticipa la IA todavía no tenía ninguna alarma: la IA ve tendencias, el umbral solo ve cuando ya es tarde. Ojo: los datos son sintéticos, así que es una hipótesis. La validamos en las semanas 0–2 con 3 meses de telemetría real, y si la IA no le gana a la regla por 1.3×, usamos la regla.
- **Muéstrelo:** Modelo de IA → Hogar.

**7. ¿Qué datos usa la IA?**
- **Respuesta corta:** Solo el desempeño del módem y de la línea: señal, errores, reinicios, micro-cortes, latencia y WiFi. Más el historial de llamadas y visitas.
- **Si piden más:** Nunca contenido, navegación ni los dispositivos del cliente.

**8. ¿Cómo explica la IA sus decisiones?**
- **Respuesta corta:** Cada hogar marcado trae sus motivos en lenguaje simple, por ejemplo «la señal viene cayendo 0.45 dB por día».
- **Si piden más:** Usamos contribuciones SHAP del modelo LightGBM, y soporte ve los motivos en la lista de trabajo de hoy.
- **Muéstrelo:** Hogar en vivo → «Por qué la IA lo marcó» y la lista de trabajo.

**9. ¿Qué tan bueno es el modelo? ¿No está sobreajustado?**
- **Respuesta corta:** AUC de 0.81 con validación temporal: entrena con semanas pasadas y se prueba con semanas futuras que nunca vio.
- **Si piden más:** Está calibrado (el riesgo predicho coincide con la tasa real) y se revisa el sesgo por tecnología y zona. Un AUC de 0.99 sería sospechoso; 0.81 es creíble.

**10. ¿Y si el modelo se equivoca?**
- **Respuesta corta:** Un falso positivo cuesta una revisión remota y, como mucho, un WhatsApp. Un falso negativo deja al cliente como está hoy.
- **Si piden más:** La IA nunca corta, cobra ni cambia condiciones, y todo se mide contra el grupo control.

**11. ¿Por qué LightGBM y no algo más simple?**
- **Respuesta corta:** Una regresión logística simple logra casi lo mismo (46 % contra 52 %), y podemos empezar con ella.
- **Si piden más:** Elegimos por desempeño medido, no por moda. Simple y auditable es un valor.

**12. ¿Dónde está la IA generativa?**
- **Respuesta corta:** Redacta los WhatsApp en español hondureño con guardrails. Si un texto no los pasa, se envía la plantilla aprobada.
- **Si piden más:** Los guardrails cubren:
  - 300 caracteres como máximo y trato de usted;
  - sin datos sensibles, sin horas inventadas y sin enlaces no oficiales;
  - siempre la opción AGENTE.

  Hay 82 pruebas automáticas.

## C. Los números

**13. Los datos son simulados. ¿Cómo sabemos que funciona?**
- **Respuesta corta:** No lo sabemos todavía, y por eso pedimos un piloto con grupo control.
- **Si piden más:** Antes del piloto hacemos un análisis retrospectivo con 3 meses de telemetría real: si la IA no le gana a la regla, lo sabremos en dos semanas y gastando poco.

**14. ¿De dónde salen los L 4.3 millones?**
- **Respuesta corta:** Son visitas y llamadas evitadas por su costo, menos todos los costos e inversión. Hogar aporta L 1.3 M y Móvil L 3 M.
- **Si piden más:** Usamos la base real de Tigo Honduras (191 mil hogares y 5.0 M de clientes móviles, según el 20-F 2025 de Millicom) y costos hondureños. Solo cuenta beneficio duro: la retención (L 3.4 M al año en margen) no está incluida hasta medirla.
- **Muéstrelo:** Caso de negocio.

**15. ¿No es optimista el 45 % de reducción de visitas evitables?**
- **Respuesta corta:** Equivale a solo un 5 % menos del total de visitas, y los proveedores reportan hasta 20 %. Hogar se paga con 22 %.
- **Si piden más:** Beegol declara hasta −20 % de todas las visitas y Ksolves −60 % de las innecesarias. Son cifras de proveedores, por eso usamos un valor intermedio y el piloto lo mide.

**16. ¿De dónde salen L 650 por visita y L 65 por llamada?**
- **Respuesta corta:** De costos hondureños, no de otros países. La visita: técnico con cargas sociales, vehículo, combustible y despacho, a unas 4.5 visitas por día. La llamada: US$11–16 por hora de agente en Honduras, con 5–7 llamadas por hora.
- **Si piden más:** Si Finanzas nos da los reales, los ingresamos en la app y el caso se recalcula en vivo.
- **Muéstrelo:** Caso de negocio → «Pon tus números».

**17. El escenario conservador da −L 3 M. ¿Eso no es perder?**
- **Respuesta corta:** Sí: si todos los supuestos salen mal a la vez, escalar perdería hasta L 3 M. Por eso no pedimos escalar, pedimos un piloto de L 770 mil que lo averigua con datos.
- **Si piden más:** El GO exige al menos el punto de equilibrio (12 % menos llamadas en Móvil) con significancia estadística. Si el efecto real es bajo, se detiene y la pérdida queda acotada al piloto.

**18. ¿En cuánto tiempo se recupera la inversión?**
- **Respuesta corta:** En el escenario base, en unos 4 meses de operación nacional.
- **Si piden más:** El piloto no busca pagarse en 60 días; busca medir si el efecto supera el punto de equilibrio.

**19. L 4.3 M al año, ¿no es poco para Tigo Honduras?**
- **Respuesta corta:** Es poco frente a unos L 16 mil millones de ingresos por servicios al año, y lo decimos. El ahorro alcanza para que el proyecto se pague solo; el valor de fondo es la experiencia: clientes que no sufren la falla, no llaman y no esperan al técnico.
- **Si piden más:** El caso no incluye retención ni NPS hasta medirlos, y la misma plataforma sirve después para otros usos (churn, priorización de red). Preferimos un número chico y defendible a uno grande e inflado.

**20. ¿Estos números son reales o inventados?**
- **Respuesta corta:** La base de clientes es real: 191 mil hogares y 5.0 M de clientes móviles, según el 20-F 2025 de Millicom. Los costos están calculados con datos hondureños, y el tipo de cambio es el del BCH.
- **Si piden más:** Lo que no es público (visitas al mes, códigos de cierre, costo real por llamada) está marcado como supuesto, y es justo lo que pedimos en las semanas 0–2. Todo está en docs/revision_critica.md, con sus fuentes.

## D. El piloto y la operación

**21. ¿Qué piden exactamente?**
- **Respuesta corta:** 12 semanas en San Pedro Sula y L 770 mil, más:
  - datos en CSV del ACS/OLT, NOC, CRM, call center y campo;
  - un equipo pequeño;
  - plantillas de WhatsApp aprobadas.
- **Muéstrelo:** última diapositiva o el one-pager.

**22. ¿Cómo deciden si funcionó?**
- **Respuesta corta:**
  - **Hogar:** GO si las visitas en los hogares marcados bajan 15 % o más, de forma significativa, y con opt-out bajo el 2 %.
  - **Móvil:** GO si las llamadas bajan 10 % o más.
  - Si no se cumplen los criterios, NO-GO.
- **Muéstrelo:** Resultados del piloto.

**23. ¿Alcanza la muestra para medir?**
- **Respuesta corta:** Sí. Con unos 7,200 hogares marcados en 60 días, el poder estadístico es del 97 % para detectar −15 %.
- **Si piden más:** Usaremos errores agrupados por nodo, porque los hogares vecinos se parecen.

**24. ¿Por qué el grupo control no recibe atención? ¿No es injusto?**
- **Respuesta corta:** Es temporal, es pequeño (15 %) y esos clientes reciben el mismo servicio que hoy.
- **Si piden más:** Sin control no hay forma honesta de medir. Al escalar, el control baja a 5 %.

**25. ¿Qué pasa si una acción remota deja al cliente sin servicio?**
- **Respuesta corta:** Hay una lista cerrada de acciones (reinicio programado, canal WiFi, firmware certificado) que se aplican de madrugada, por lotes y con reversión.
- **Si piden más:** Las ejecuta el ACS por reglas, nunca la IA generativa, y cualquier daño se vería en el grupo tratado.

**26. ¿No vamos a molestar a los clientes con mensajes?**
- **Respuesta corta:**
  - **Hogar:** un mensaje como máximo y solo si hubo acción.
  - **Móvil:** dos por falla.
  - El opt-out se respeta al instante, y si supera el 2 % la decisión es NO-GO.

**27. ¿Quién lo opera y mantiene?**
- **Respuesta corta:** Un analista de datos, soporte nivel 2 e ingeniería de acceso.
- **Si piden más:** La operación está incluida en el caso de negocio. No hace falta comprar una plataforma nueva.

**28. ¿Cuánto tarda en estar listo el piloto?**
- **Respuesta corta:** Dos semanas de preparación con exportaciones CSV, sin integraciones grandes. Ocho semanas en vivo y dos de análisis.

## E. Privacidad, seguridad y regulación

**29. ¿Están espiando el internet de los clientes?**
- **Respuesta corta:** No. Solo leemos el desempeño del módem; nunca contenido, navegación, DNS ni los dispositivos del cliente.
- **Si piden más:** Eso protege el secreto de las comunicaciones del artículo 100 de la Constitución.

**30. ¿Qué ley de datos cumplen, si Honduras no tiene una?**
- **Respuesta corta:** Usamos el GDPR como estándar, que es la vara más exigente, más la Constitución (artículos 76, 100 y 182, habeas data) y la política de privacidad de Millicom.
- **Si piden más:** Cuando se apruebe la ley hondureña (pendiente desde 2018), ya la cumpliremos. Legal aprueba una evaluación de impacto antes del primer mensaje.
- **Muéstrelo:** Listo para producción → Seguridad y privacidad.

**31. ¿Qué tan seguro es el sistema?**
- **Respuesta corta:** Hicimos un red team propio: atacamos la API, encontramos 12 debilidades y las corregimos todas, cada una con su prueba automática.
- **Si piden más:** El diseño sigue ISO 27001/27701/42001, SOC 2, NIST y OWASP. En producción: SSO con MFA, cifrado con KMS, WAF y una prueba de penetración independiente.

**32. ¿Qué datos van a la IA generativa?**
- **Respuesta corta:** Solo el nombre de pila y el tipo de situación. Nunca el ID, el teléfono ni la ubicación.
- **Si piden más:** El texto que escribe el cliente se redacta antes de enviarse. En producción se usa un acuerdo de retención cero o la nube corporativa de Tigo.

**33. ¿Y CONATEL?**
- **Respuesta corta:** Los requisitos de aviso de interrupciones y de compensaciones los valida Legal antes del piloto.
- **Si piden más:** El sistema no toca el contenido de las comunicaciones ni la intervención legal de comunicaciones.

## F. El equipo y la ejecución

**34. ¿Quién lo va a hacer?**
- **Respuesta corta:** *[Nombre del equipo]*. Proponemos sumar un enlace del NOC o de ingeniería de acceso y alguien de datos.
- **Si piden más:** El prototipo ya funciona: dos demos en vivo, más de 200 pruebas automáticas y un pipeline reproducible desde cero.

**35. ¿Qué necesitan de nosotros, además del dinero?**
- **Respuesta corta:** Un patrocinador que quite obstáculos, acceso a los datos en CSV y el visto bueno de Legal.

## G. Preguntas curvas

**36. Si funciona tan bien, ¿por qué no lo hizo ya Tigo?**
- **Respuesta corta:** Porque la telemetría existe, pero nadie la había convertido en una lista de trabajo semanal medida con grupo control. Es exactamente lo que proponemos probar.
- **Si piden más:** Si ya existe algo parecido internamente, mejor: lo usamos como punto de partida y aportamos la medición y la IA.

---

*Datos simulados — supuestos a validar con Tigo. Detalle técnico en `seguridad_y_privacidad.md`, `impacto.md` y `reports/modelo.md`.*
