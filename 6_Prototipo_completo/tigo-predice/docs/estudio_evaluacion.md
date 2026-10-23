# Estudio de evaluación: ¿invertiría un Shark de Tigo en esto?

*Evaluación crítica de Tigo Predice v02, hecha desde la mirada de un comité que decide dónde poner dinero real. Octubre 2026.*

---

## Actualización 14/10/2026: la recomendación ya está implementada (v03)

**Lo que cambió.** El estudio recomendaba «Hogar primero». Ya está construido y probado:
- **Telemetría y modelo:** telemetría de módems y un modelo de 7 días medido contra la regla de umbrales.
  La IA anticipa el **52 %** de las visitas evitables, frente al **26 %** de la regla (**2.0×**).
- **Piloto Hogar con control:** −19 % de visitas y −56 % de llamadas técnicas (simulado).
- **Caso de negocio por frente** y una demo «Hogar en vivo» con explicación SHAP.
- **Seguridad de nivel internacional** con red team propio.

| Criterio | Peso | Antes (v02) | Ahora (v03) | Por qué cambió |
|---|---|---|---|---|
| Problema relevante | 15 % | 4.5 | 4.5 | — |
| Tamaño del impacto | 15 % | 2.5 | **3.5** | Neto año 1 de L 5.1 M a **L 10 M**; las visitas valen más que las llamadas |
| Credibilidad de la evidencia | 15 % | 4.5 | 4.5 | Sigue faltando un dato real de Tigo |
| Factibilidad | 10 % | 3.5 | **4.0** | El mapeo cliente ↔ nodo es exacto; se arranca con CSV del ACS |
| Protagonismo de la IA | 15 % | 2.5 | **4.5** | La IA predice qué hogar va a fallar y le gana a la regla con explicación |
| Escalabilidad | 10 % | 4.0 | 4.0 | — |
| Riesgo y cumplimiento | 5 % | 4.0 | **4.5** | GDPR como estándar, evaluación de impacto y red team con 12 ataques corregidos |
| Equipo | 10 % | 2.5 | 2.5 | **Depende de ti:** sumar a NOC/acceso y datos lo sube a 4 |
| Pitch y demo | 5 % | 4.5 | 4.5 | Dos demos en vivo |
| **Total ponderado** | | **≈ 3.6** | **≈ 4.1 / 5** | Con equipo de 3 y un dato real: **≈ 4.3** |

**Nota sobre el tamaño.** La sección 5 estimaba unos L 10 M solo en visitas, como indicativo. El caso implementado es más
conservador: **L 6.6 M de beneficio y L 5.4 M netos** en Hogar. La razón es que solo cuenta las visitas evitables en los
hogares que la IA marca **a tiempo** (30 % × 45 % × 45 % = 6 % del total de visitas). Preferimos un número que resista
preguntas.

---

## 1. Veredicto en una línea

**Hoy es una propuesta sólida y creíble, pero chica y poco "IA" para un concurso de IA.** Gana en rigor y ejecución; pierde en tamaño del premio y en protagonismo de la IA. Con tres cambios concretos (sección 6) puede pasar de "buena idea" a "la que hay que financiar".

---

## 2. Quién va a evaluar y qué le importa a cada uno

| Evaluador probable | Lo que pregunta en su cabeza | Cómo le va hoy a Tigo Predice |
|---|---|---|
| **Dirección de CX** | ¿Mejora la experiencia de forma visible? ¿Baja quejas y llamadas? | ✅ Muy bien: el relato del cliente que se entera por Tigo conecta. |
| **Finanzas (CFO)** | ¿Cuánto da y cuán seguro es? ¿Cuánto me pides? | ⚠️ Confía en los números, pero son chicos: L 5.1 M netos al año (≈ US$ 190 mil). |
| **Tecnología / NOC** | ¿Se puede hacer con nuestros sistemas? ¿Quién lo mantiene? | ⚠️ Pregunta difícil: ¿cómo saben qué clientes **móviles** estaban en el sitio caído? |
| **Comercial / Mercado** | ¿Nos diferencia frente a Claro? ¿Retiene clientes? | ⚠️ La retención está fuera del caso base. Es honesto, pero no lo emociona. |
| **Transformación digital / IA** | ¿Dónde está la IA? ¿Es innovación o un SMS con otro nombre? | ❌ **El punto más débil.** Nosotros mismos decimos que para avisar "basta la regla". |
| **Legal / Riesgo** | Consentimiento, privacidad, regulación. | ✅ Bien cubierto: guardrails, opt-out, bitácora, CONATEL como punto a validar. |

---

## 3. Calificación actual (escala 1 a 5, criterios típicos de un Shark Tank corporativo)

| Criterio | Peso | Nota | Por qué |
|---|---|---|---|
| Problema relevante y alineado a la estrategia | 15 % | **4.5** | La estrategia 2026 de Millicom gira en torno a la experiencia del cliente y la eficiencia. Encaja perfecto. |
| Tamaño del impacto | 15 % | **2.5** | Ahorro duro modesto. Comparado con el tamaño de la operación, "no mueve la aguja". |
| Credibilidad de la evidencia | 15 % | **4.5** | Grupo control, rangos, punto de equilibrio y honestidad: muy por encima de lo usual. Falta **un solo dato real de Tigo**. |
| Factibilidad y tiempo al valor | 10 % | **3.5** | Arrancar con CSV es inteligente. El mapeo cliente móvil ↔ sitio es el riesgo técnico. |
| Protagonismo de la IA | 15 % | **2.5** | La IA está en priorizar compensaciones y redactar mensajes. Un jurado puede verlo como algo accesorio. |
| Escalabilidad (país y Millicom) | 10 % | **4.0** | Replicable en todas las operaciones y tecnologías. |
| Riesgo y cumplimiento | 5 % | **4.0** | Bien tratado. |
| Equipo | 10 % | **2.5** | Hasta ahora es una propuesta individual. Los Sharks invierten en equipos, y faltan NOC y TI. |
| Pitch y demo | 5 % | **4.5** | Un prototipo funcionando y una demo de 90 s son raros en estos concursos. |
| **Total ponderado** | | **≈ 3.6 / 5** | Competitiva, pero vulnerable frente a ideas "más IA" con números más grandes, aunque sean menos creíbles. |

---

## 4. Lo que un jurado escéptico va a decir (y es justo)

1. **"Esto ya existe."** Es cierto en otros mercados: Comcast/Xfinity ya identifica a los clientes afectados y les envía mensajes de texto proactivos durante las fallas [(Comcast, 2024)](https://legislature.vermont.gov/Documents/2024/WorkGroups/Senate%20Government%20Operations/Bills/S.310/Witness%20Documents/S.310~Jim%20White~Comcast%20Practices%20on%20Notices%20and%20Information%20Provided%20to%20Customers~3-26-2024.pdf), y AT&T ofrece alertas de restablecimiento. → **Respuesta:** "Es una práctica probada que Tigo Honduras aún no tiene (a confirmar). Lo nuevo es medirla con grupo control y usar IA donde sí agrega valor." Que ya exista **baja el riesgo**: no es una apuesta, es una adopción.
2. **"¿Dónde está la IA?"** Si la respuesta es "para avisar basta una regla", el jurado de un concurso de IA baja la nota. → Hay que mover la IA al centro (ver la sección 6).
3. **"¿Cómo saben qué clientes móviles estaban en la celda caída?"** Un cliente móvil se mueve. Se necesita la última celda registrada (CDR/señalización) en las horas previas. En **hogar** (fibra/HFC) el mapeo cliente ↔ nodo es exacto. → Esto empuja a **empezar por hogar**.
4. **"L 5 M al año es poco."** Es el caso conservador **solo de llamadas móviles**. El costo total de una falla incluye llamadas, **visitas técnicas**, compensaciones y clientes que se van. Hoy no mostramos ese "tamaño del premio".
5. **"¿Quién más está en el equipo?"** Sin alguien del NOC y de TI, el jurado duda de la ejecución.
6. **"Todo es simulado."** La metodología es impecable, pero sin un dato real de Tigo el jurado no puede saber si el problema es grande.

---

## 5. ¿Hay ideas mejores? Comparación honesta

Evalué cinco alternativas con la misma vara. Una nota más alta es mejor; "reutiliza" indica cuánto del prototipo actual se aprovecha.

| Opción | Valor | IA central | Factibilidad | Diferenciación | Reutiliza | Lectura |
|---|---|---|---|---|---|---|
| **A. Actual:** aviso de fallas masivas móviles | 2.5 | 2.5 | 3.5 | 3.0 | 100 % | Creíble, pero chica y "poco IA". |
| **B. Atención proactiva Hogar:** fallas de nodo + degradación de módem, con arreglo remoto y menos visitas técnicas | **4.0** | **4.5** | 3.5 | **4.0** | ~75 % | **La mejor relación valor/riesgo.** La IA es el corazón: predice qué hogar va a fallar antes de que llame. |
| C. Agente de IA en WhatsApp/IVR ("sabemos de la falla") | 3.0 | 4.0 | 4.5 | 2.0 | ~60 % | Rápido y vistoso, pero habrá muchos chatbots en el concurso. Sirve como **complemento**, no como idea principal. |
| D. Churn de prepago y ofertas personalizadas | 3.5 | 4.0 | 3.0 | 2.0 | ~50 % | Millicom ya hace analítica de migración prepago → pospago: compite con lo que ya existe. |
| E. Fraude en Tigo Money | 4.0 | 4.5 | 2.0 | 3.5 | 0 % | Valor alto, pero exige datos financieros, regulación y otro prototipo. No llega al 23 de octubre. |

### Por qué B (Hogar) es la mejor apuesta

- **El dinero está en las visitas técnicas, no solo en las llamadas.** Una llamada cuesta unos L 85 (supuesto); una visita técnica cuesta mucho más (supuesto: L 800 a L 1,500). Los proveedores de "cuidado proactivo" reportan entre 20 % y 60 % menos visitas innecesarias con IA sobre la telemetría de los módems [(Ksolves, caso de operador de cable)](https://www.ksolves.com/case-studies/big-data/predictive-cable-network-analytics-platform-docsis) [(Beegol)](https://beegol.com). Son cifras de proveedores, así que conviene usar el extremo bajo.
- **El mapeo es exacto:** cada módem cuelga de un nodo u OLT conocido. Desaparece la pregunta difícil del NOC.
- **La IA es protagonista de verdad:** detectar módems que se degradan (caídas intermitentes, señal baja) y predecir "este hogar va a llamar o necesitará una visita en 72 h" **es** machine learning. No es una regla.
- **Es estratégico:** el hogar con fibra es donde Tigo crece (175 mil relaciones de hogar a fines de 2025, frente a 166 mil un año antes, según el [20-F de Millicom](https://www.sec.gov/Archives/edgar/data/912958/000162828026020831/tigo-20251231.htm)). Allí el churn por mala experiencia duele más (ARPU supuesto de L 950).
- **Reutiliza el 75 % de lo construido:** la detección de afectados, la asignación con grupo control, los mensajes con guardrails, el WhatsApp, la medición GO/NO-GO, el caso de negocio y la demo.

### Tamaño indicativo de la oportunidad en hogar

Son **hipótesis para validar con dos datos de Tigo**: visitas técnicas por mes y costo por visita.

| Supuesto | Bajo | Base | Alto |
|---|---|---|---|
| Visitas técnicas al mes (3 % a 6 % de 175 mil hogares) | 5,000 | 7,500 | 10,000 |
| % de visitas evitables (resolubles a distancia o sin falla) | 20 % | 30 % | 40 % |
| Reducción lograda sobre las evitables | 25 % | 35 % | 50 % |
| Costo por visita | L 800 | L 1,100 | L 1,500 |
| **Ahorro anual en visitas** | **≈ L 2.4 M** | **≈ L 10 M** | **≈ L 36 M** |

Sumado al caso móvil actual (L 5.1 M netos en el escenario base), el **escenario base combinado** pasa de unos L 5 M a unos **L 15 M al año, antes de restar el costo adicional de la extensión Hogar** (integrar la telemetría de módems; hay que estimarlo con TI). Todo sigue medido contra el grupo control. Es una estimación de orden de magnitud, no una promesa.

---

## 6. Recomendación: qué cambiar para ganar

### Cambio 1 · Reposicionar como "Atención proactiva: Hogar primero"
> *"Tigo Predice: la IA que detecta el problema antes que el cliente, y lo resuelve antes de que llame o de que haya que mandar un técnico."*
- **Piloto:** Tigo Hogar en San Pedro Sula, con fallas de nodo/OLT y degradación de módems, aviso por WhatsApp y arreglo remoto. Las fallas masivas móviles pasan a ser el segundo frente, con el mismo motor.
- **Métricas norte:** llamadas y **visitas técnicas** por cada 1,000 hogares afectados, tratados vs. control.
- Se mantiene todo el rigor: control del 15 %, IC 95 %, GO/NO-GO y un caso de negocio que solo cuenta beneficio duro.

### Cambio 2 · Poner la IA en el centro, sin exagerar
1. **IA predictiva:** un modelo sobre la telemetría del módem (caídas intermitentes, señal, reinicios) que predice qué hogar va a fallar o llamar en 72 h. Es el corazón del producto.
2. **IA generativa con guardrails:** redacta el aviso y **atiende las respuestas** del cliente en WhatsApp (autodiagnóstico, estado y agendar técnico solo si hace falta). Absorbe la ola de mensajes que llega después de cada falla.
3. **IA de priorización:** decide a quién compensar, a quién llamar y a quién mandar un técnico primero cuando el presupuesto no alcanza.

### Cambio 3 · Llevar un dato real y un equipo
- **Antes del pitch, un análisis retrospectivo con datos reales de Tigo:** tomar las fallas de los últimos 3 meses y contar cuántos afectados llamaron y cuántas visitas se generaron. Basta un CSV del NOC y otro del call center. **Este dato vale más que cualquier diapositiva**: convierte "1 de cada 3 según un benchmark" en "en Tigo, X de cada 100 llamaron".
- **Formar el equipo de 3 que permite el concurso:** tú (dueño de la propuesta), alguien del **NOC o ingeniería de acceso**, y alguien de **TI o datos**. Si además hay un gerente que diga "yo patrocino el piloto", la nota de ejecución sube mucho.
- **Hacer un pedido escalonado:** L 520 mil para el piloto y, si da GO, un compromiso de escalar. A los Sharks les gusta arriesgar poco con una opción de ganar mucho.

### Lo que NO hay que cambiar
- La honestidad (simulado, supuestos, rangos): es la mayor ventaja frente a propuestas infladas.
- El grupo control y el GO/NO-GO: ningún otro equipo va a traer eso.
- La demo en vivo y la frase de posicionamiento.

---

## 7. Plan para los próximos días (hasta el envío del 23 de octubre)

| Cuándo | Qué | Quién |
|---|---|---|
| Ya | Pedir los datos de `docs/datos_a_pedir_a_tigo.md` y, **si eliges Hogar**, dos más: visitas técnicas por mes y costo por visita | Tú |
| Ya | Invitar a 2 compañeros (NOC/acceso y TI/datos) y buscar un patrocinador | Tú |
| 1–2 días | Si eliges Hogar: agregar al prototipo la telemetría de módems, el modelo de degradación, las visitas técnicas en el caso de negocio y la demo "Falla en vivo Hogar" | Claude |
| Cuando lleguen los datos | Cargarlos en "Pon tus números" y regenerar todos los documentos con cifras reales | Claude |
| 2 días antes | Ensayar 3 veces y grabar el video de respaldo | Tú y el equipo |
| 21–22 oct | Enviar | Tú |

---

## 8. Conclusión

Tigo Predice ya tiene lo más difícil de conseguir: **credibilidad, un prototipo funcionando y un diseño para medir.** Lo que le falta es **tamaño y protagonismo de la IA**, y ambas cosas se resuelven con el mismo movimiento: llevarla primero al **hogar**, donde la IA predictiva tiene un rol natural y el ahorro en visitas técnicas es mucho mayor que el de llamadas. Además, un **dato real** y un **equipo de 3** quitan las dos dudas que más pesan en un comité de inversión.

*Fuentes: Comcast/Xfinity (2024), Ksolves y Beegol (proveedores; cifras autodeclaradas), Millicom 20-F 2025 y resultados del 2T 2026. Todos los valores de hogar son supuestos a validar con Tigo.*
