# Guion del pitch v03 — 5 minutos frente a los Sharks

**Tigo Predice** · *"Los chatbots y copilotos atienden la llamada. Tigo Predice evita que ocurra."*
*La IA que detecta el problema antes que el cliente, y lo resuelve antes de que llame o de que haya que mandar un técnico.*

> **Antes de empezar:**
> - Abra la app (`iniciar_demo.bat`) en **Hogar en vivo ★**, caso **A distancia**, velocidad 1×, y presione ↺.
> - Tenga a mano el video de respaldo y las URL `…/hogar?final` y `…/falla?final`, que abren directo el resultado.
> - Todas las cifras son **simuladas o supuestas a validar con Tigo**, y así hay que decirlo.

---

## 0:00 – 0:40 · El dolor
> "Karla trabaja desde su casa en San Pedro Sula, con internet de fibra. Desde hace una semana su WiFi empeora y el módem se reinicia solo. Un día no aguanta más: llama, espera, le agendan un técnico. El técnico va, no encuentra nada físico, cambia el canal del WiFi y se va.
> Esa visita costó, en nuestro supuesto, **L 1,100**, más **dos llamadas**. Y se podía resolver a distancia, **una semana antes**, sin que Karla sufriera nada.
> Suponemos que **3 de cada 10 visitas técnicas son evitables** (dato a validar con los códigos de cierre de Tigo). Tigo hace unas **7,500 visitas al mes** en sus 175 mil hogares (supuesto)."

## 0:40 – 1:10 · Qué es y por qué ahora
- Los módems **ya reportan su telemetría**: señal, errores, reinicios, WiFi. Hoy solo se mira cuando cruza un umbral, y casi siempre es tarde.
- **IA predictiva:** cada semana califica a todos los hogares y marca al **2 %** que va a fallar, días antes.
- **Acción remota + WhatsApp:** se corrige a distancia; si es físico, el técnico va **una sola vez y con el diagnóstico**.
- **El mismo motor sirve en móvil:** en una falla masiva, aviso por WhatsApp antes de que llamen.

## 1:10 – 2:30 · Demo "Hogar en vivo" (80 s)
Presione **▶ Iniciar** y lea la franja azul. Los momentos clave:
1. **26/09:** empieza el problema. La telemetría cambia, pero Karla todavía no nota nada.
2. **28/09: la IA lo marca** (riesgo 13 %, dentro del 2 % más alto de la ciudad). **La regla de umbrales todavía no ve nada.** A la derecha aparece **por qué**: el WiFi empeora día a día y la lentitud va en aumento.
3. **Corrección remota:** firmware y canal WiFi, de madrugada. Le llega un WhatsApp: *"ya la corregimos a distancia, sin que tuviera que llamar"*.
4. **Dos mundos:** en rojo, sin Tigo Predice, el **02/10 Karla habría llamado**, el **03/10** recién la regla habría alarmado y el **04/10** se habría enviado un técnico. En verde, el WiFi ya está sano.
5. **Resultado:** visita evitada y 2 llamadas evitadas, **L 1,270** de ahorro por **L 0.31** (un WhatsApp).

*Si sobra tiempo:* en el caso **Con técnico**, la IA marca la señal de fibra **10 días antes** de la llamada y el técnico llega una sola vez.
*Abajo está la **lista de trabajo de hoy** para soporte: 100 hogares marcados en la ciudad. **57 no tienen ninguna alarma de umbral**: solo la IA los ve.*

## 2:30 – 3:10 · La IA, medida contra la regla (no contra nada)
Pestaña **Modelo de IA → Hogar**:
> "Con el mismo presupuesto, la IA anticipa el **52 %** de las visitas evitables y la regla de umbrales el **26 %**: **2.0×**. La mitad de lo que la IA anticipa **todavía no tenía ninguna alarma**.
> Y somos honestos: una regresión logística simple llega al 46 %. Si con datos reales la IA no le gana a la regla por 1.3×, **usamos la regla**. Ese es un criterio del GO."

Pestaña **Resultados del piloto → Hogar**:
> "Simulamos 60 días con grupo control: **−19 % de visitas** (IC 95 % 12 % a 25 %) y **−56 % de llamadas técnicas** en los hogares marcados, con 97 % de poder estadístico. **Es simulado:** muestra cómo se va a medir."

## 3:10 – 3:40 · Móvil: el mismo motor
> "Cuando cae un sitio, el mismo motor avisa por WhatsApp a los afectados. En la simulación, **−15 % de llamadas** (IC 12 % a 19 %)."
*(Opcional: abra **Falla masiva en vivo** con `?final`.)*

## 3:40 – 4:20 · Caso de negocio conservador
Pestaña **Caso de negocio**:
> "Solo contamos **beneficio duro**: visitas y llamadas evitadas por su costo. La retención vale cero hasta medirla.
> - **Hogar** se paga con solo **9 %** menos visitas evitables; el caso base supone 45 % y los proveedores reportan de 20 % a 60 %. Eso equivale a solo un 6 % menos del total de visitas.
> - **Móvil** se paga con solo **9 %** menos llamadas en los avisados.
> - **Juntos: L 10 M netos en el año 1** (rango −L 23 mil a L 25 M). En el peor escenario quedamos en equilibrio, y para eso existe el GO/NO-GO."

Si hay tiempo, use **Pon tus números**: *"Denme visitas por mes y costo por visita, y el caso queda definitivo en vivo."*

## 4:20 – 4:40 · Seguridad y privacidad, a nivel de hiperescalador
> "No leemos contenido, ni navegación, ni los dispositivos del cliente: solo el desempeño del módem. Honduras todavía no tiene ley integral de datos, así que usamos el GDPR como vara, además de ISO 27001/27701/42001, SOC 2 y OWASP. Sesión segura, datos mínimos, bitácoras y **más de 200 pruebas automáticas**, incluido un red team propio."

## 4:40 – 5:00 · El pedido a los Sharks
> "Les pido, por **12 semanas** en San Pedro Sula:
> 1. **Datos:** CSV diarios del NOC, del ACS/OLT, del CRM, del call center y de las órdenes de campo.
> 2. **Equipo:** un patrocinador, un enlace del NOC, uno de ingeniería de acceso, soporte nivel 2 y un analista de datos al 50 %.
> 3. **Canal y cumplimiento:** plantillas de WhatsApp, evaluación de impacto y visto bueno de Legal.
> 4. **Inversión:** **L 770 mil** (≈ US$ 28 mil), con un rango de L 470 mil a L 1.2 M.
> En la semana 12, con números reales, ustedes deciden GO o NO-GO por frente."

**Cierre:** *"Los chatbots atienden la llamada. Tigo Predice evita que ocurra, y evita la visita. Gracias."*

---

## Consejos
- Diga **"simulado"** y **"supuesto"** sin miedo: es lo que da credibilidad frente a un comité.
- Si dicen "esto ya existe" (Xfinity, AT&T): *"Sí, es una práctica probada que Tigo Honduras aún no tiene. Lo nuevo es medirla con grupo control y que la IA le gane a la regla."*
- Si preguntan "¿por qué no basta una regla?": *"La regla anticipa la mitad. Y si con datos reales no le ganamos, usamos la regla."*
- Para preguntas difíciles, vea [preguntas_frecuentes_jurado.md](preguntas_frecuentes_jurado.md).
- Versión corta: [elevator_pitch.md](elevator_pitch.md) (2 minutos). Cómo usar la app en vivo: [guia_demo.md](guia_demo.md).
