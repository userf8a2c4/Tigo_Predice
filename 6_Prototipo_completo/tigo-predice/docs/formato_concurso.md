# Texto listo para el formato del concurso (Tigo CX Month · Sharks)

> Copie cada bloque en el campo que corresponda del formato oficial. Las cifras son simuladas o supuestas a validar con Tigo.

**Nombre de la idea:**
Tigo Predice: la IA que resuelve antes de que el cliente llame

**Participante(s):**
[Nombre completo] · [Área] · [Correo] · [Extensión]

**Categoría principal:**
Experiencia del Cliente / CX

**Otras categorías:**
Red y Operaciones · Eficiencia / Reducción de Costos · Self-Service y Canales Digitales · Analítica y toma de decisiones

**Problema:**
Los problemas de internet del hogar avisan en la telemetría del módem días antes de que el cliente los sufra, pero hoy solo se miran cuando cruzan un umbral. El cliente llama, espera y se agenda un técnico, aunque 1 de cada 4 visitas es evitable (supuesto a validar; la industria reporta 17–20 % de visitas «sin falla encontrada»). En móvil, cuando cae un sitio, 1 de cada 3 afectados llama si no recibe aviso (benchmark público). Llamadas y visitas que cuestan, saturan y deterioran la experiencia.

**Solución:**
- **Frente Hogar (principal).** Cada semana un modelo de IA califica la telemetría de todos los módems y marca al 2 % con más riesgo de llamar o necesitar visita en 7 días, con la explicación de por qué. Si el problema es de WiFi o firmware, se corrige a distancia y el cliente recibe un WhatsApp. Si es físico, se agenda la visita antes del corte y el técnico llega con el diagnóstico.
- **Frente Móvil.** En fallas masivas de red, aviso por WhatsApp en minutos con la causa en palabras simples y la hora del NOC (solo si la tiene), más un mensaje de cierre.
- **Medición.** En ambos frentes, un grupo control aleatorio del 15 % mide el efecto real.

*"Los chatbots y copilotos atienden la llamada. Tigo Predice evita que ocurra."*

**¿Cómo usa la IA?**
- **IA predictiva (corazón del producto):**
  - Modelo de machine learning sobre la telemetría de módems, con validación temporal.
  - Comparado con la regla de umbrales: anticipa el 52 % de las visitas evitables, contra 26 % de la regla (2.0×, en datos simulados; se valida con telemetría real en las semanas 0–2).
  - Explica cada caso por variables (SHAP).
- **IA generativa (Claude):**
  - Redacta los avisos con guardrails (usted, sin datos sensibles, sin horas inventadas, siempre opción de hablar con una persona).
  - Si falla, se usa una plantilla aprobada.
- **Diseño experimental:** tratados vs. control, con intervalo de confianza y criterios GO/NO-GO.

**Beneficios:**
- **Cliente:** no sufre la falla o se entera por Tigo, no tiene que llamar ni esperar, y el técnico llega una sola vez.
- **Tigo:** menos visitas técnicas evitables y menos llamadas; técnicos dedicados a lo que de verdad necesita ir a campo.
- **Colaboradores:**
  - Soporte recibe cada día una lista de trabajo priorizada y explicada.
  - El call center recibe menos llamadas repetitivas.

**Inversión estimada:**
- **Piloto de 60 días en San Pedro Sula (Hogar + Móvil):** **L 770 mil** (≈ US$ 28 mil), con un rango de L 480 mil a L 1.2 M.
- **Si da GO:** integración nacional única de L 1.7 M para ambos frentes y un costo recurrente de unos L 3.6 M al año.

**Impacto esperado (caso conservador, solo beneficio duro):**
- **Hogar** se paga en el primer año con 22 % menos visitas evitables en los hogares marcados. En el caso base se evitan unas 3,300 visitas al año, apenas un 5 % del total.
- **Móvil:** con 12 % menos llamadas en los avisados, la plataforma se paga en el primer año, con unas 110,000 llamadas evitadas al año.
- **Juntos:** **L 4.3 M netos en el año 1** (rango −L 3 M a L 14 M), con costos hondureños (visita L 650, llamada L 65). La retención es potencial adicional y no se incluye hasta medirla.

**KPIs:**
- **Métricas norte:**
  - visitas técnicas por cada 1,000 hogares marcados (7 días);
  - llamadas por cada 1,000 afectados en fallas masivas (72 h).

  En ambos casos, tratados vs. control.
- **Secundarios:** llamadas técnicas, visitas repetidas, CSAT, opt-outs, captura de la IA vs. la regla y sesgo por zona y tecnología.
- **Criterios GO:**
  - **Hogar:** visitas −15 % o más, significativo, opt-out < 2 % e IA ≥ 1.3× la regla (si no, se usa la regla).
  - **Móvil:** llamadas −10 % o más, significativo y opt-out < 2 %.

**Seguridad y privacidad:**
- **Datos:** sin contenido de comunicaciones ni navegación; datos mínimos.
- **Estándar:** GDPR como referencia (Honduras aún no tiene ley integral), con ISO 27001/27701/42001, SOC 2 y OWASP.
- **Controles:** sesión segura y bitácoras; evaluación de impacto antes del piloto.

**Estado:**
Prototipo funcional con dos demos en vivo («Hogar en vivo», 80 s, y «Falla masiva en vivo», 90 s). Funciona sin internet, usa datos simulados y tiene más de 200 pruebas automáticas, incluido un ejercicio de red team con 12 ataques corregidos.
