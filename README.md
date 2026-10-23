# Tigo Predice

> **Los chatbots y copilotos atienden la llamada. Tigo Predice evita que ocurra.**

Propuesta para **AI Shark Tank · Tigo CX Month 2026**. Tigo Predice es atención proactiva con IA para Tigo Honduras:
- **Hogar:** cada semana la IA lee la telemetría de los módems, marca al 2 % de hogares con más riesgo de fallar y explica por qué. Si es WiFi o firmware, se corrige a distancia; si es físico, el técnico va una sola vez y con el diagnóstico.
- **Móvil:** en fallas masivas de red, aviso por WhatsApp antes de que el cliente llame.

En ambos frentes, un grupo control aleatorio del 15 % mide el efecto real.

**Autoría:** Sandra Jimenez · Asistente de Experiencia B2B · sandra.jimenez@tigo.com.hn

**Categoría:** Experiencia del cliente / CX (también Red y operaciones, y Eficiencia / reducción de costos).

## Contenido

| Carpeta | Qué tiene |
|---|---|
| [`1_Presentacion`](1_Presentacion) | Presentación para el concurso (12 diapositivas, con guion en las notas), en PowerPoint y PDF |
| [`2_Demo`](2_Demo) | `Demo_Tigo_Predice.html`: la demo en un solo archivo, sin servidor ni internet. `Abrir_Demo.exe` la abre en Windows |
| [`3_Para_el_jurado`](3_Para_el_jurado) | Resumen de una página, propuesta completa y datos reales con sus fuentes |
| [`4_Preparacion_del_pitch`](4_Preparacion_del_pitch) | Elevator pitch de 2 minutos, 36 preguntas probables del jurado, guía visual de la demo y presentación extendida de respaldo |
| [`5_Envio`](5_Envio) | Texto del correo de postulación |
| [`6_Prototipo_completo/tigo-predice`](6_Prototipo_completo/tigo-predice) | Código del prototipo: modelos de IA, API, interfaz, experimento del piloto, caso de negocio y pruebas |
| [`_referencias`](_referencias) | Afiche del concurso |

## Ver la demo
- **Sin instalar nada:** abrir `2_Demo/Demo_Tigo_Predice.html` con doble clic, entrar a **Hogar en vivo ★** y presionar **▶ Iniciar** (unos 80 segundos).
- **Prototipo completo (Windows):** con Python 3.11+ y Node 18+, doble clic en `6_Prototipo_completo/tigo-predice/iniciar_demo.bat` y abrir http://127.0.0.1:8000. La primera vez tarda unos 4 minutos. Detalles en el [README del prototipo](6_Prototipo_completo/tigo-predice/README.md).

## Cifras clave (escenario base)
- **Base real de Tigo Honduras:** 191 mil hogares y 5.0 M de clientes móviles (Millicom, Form 20-F 2025).
- **Neto del año 1:** L 4.3 M, con un rango de −L 3 M a L 14 M. Solo cuenta ahorro duro (visitas y llamadas evitadas), con costos hondureños.
- **Punto de equilibrio:** Móvil se paga con 12 % menos llamadas; Hogar, con 22 % menos visitas evitables en los hogares marcados.
- **Piloto:** 12 semanas en San Pedro Sula por L 770 mil (≈ US$ 28 mil), con criterios GO / NO-GO por frente.

## Qué es real y qué es supuesto
- **Real (público):** base de clientes, precios de los planes, tipo de cambio del BCH, tarifas de WhatsApp Business y costos de centros de contacto en Honduras. Fuentes en `3_Para_el_jurado/Datos_Reales_y_Revision.pdf`.
- **Supuesto, a validar con Tigo:** visitas técnicas al mes, porcentaje de visitas evitables, costo real por visita y por llamada, y el efecto de los avisos.
- **Simulado:** la telemetría, los clientes y los resultados del modelo y del piloto. Muestran cómo se medirá, no un resultado real.

## Antes de enviar
- Confirmar la dirección de correo con el afiche original.
- Si el correo rechaza el `.exe` o el `.html`, compartir el paquete por OneDrive.
