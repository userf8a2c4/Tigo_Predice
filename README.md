<div align="center">

<img src="assets/readme/portada.png" alt="Tigo Predice: la IA que resuelve la falla antes de que el cliente llame" width="100%">

<br>

![Concurso](https://img.shields.io/badge/AI%20Shark%20Tank-Tigo%20CX%20Month%202026-0A22B8)
![Categoría](https://img.shields.io/badge/categor%C3%ADa-Experiencia%20del%20cliente-4CC9F0)
![Pruebas](https://img.shields.io/badge/pruebas%20autom%C3%A1ticas-258-2BB673)
![Regulación](https://img.shields.io/badge/alineado%20con-CONATEL%20NR001%2F26-FFC629)
![Accesibilidad](https://img.shields.io/badge/WCAG%202.2%20AA-0%20infracciones%20(axe--core)-2BB673)
![Marcos de referencia](https://img.shields.io/badge/marcos%20de%20referencia-OWASP%20Top%2010%3A2025%20%C2%B7%20GDPR%20%C2%B7%20ISO%2027001-00377B)

**[Cómo ver la demo](#cómo-ver-la-demo)** · **[Presentación](2_Documentos/1_Presentacion/AI_Shark_Tank_Tigo_Predice.pdf)** · **[Resumen de una página](2_Documentos/2_Para_el_jurado/OnePager_Tigo_Predice.pdf)** · **[Datos y fuentes](2_Documentos/2_Para_el_jurado/Datos_Reales_y_Revision.pdf)** · **[Estrategia y regulación](2_Documentos/2_Para_el_jurado/Estrategia_y_Regulacion.pdf)**

</div>

> [!IMPORTANT]
> **Datos simulados, base real.** La telemetría, los clientes y los resultados del modelo y del piloto son simulados: muestran cómo se medirá, no un resultado real. La base de clientes (191 mil hogares y 5.0 M de clientes móviles), los precios, el tipo de cambio y los costos de referencia son datos públicos con fuente.

## ¿Qué es Tigo Predice?

**Los chatbots y copilotos atienden la llamada. Tigo Predice evita que ocurra.**

Atención proactiva con IA para Tigo Honduras, en dos frentes con el mismo motor:
- **Hogar:** cada semana la IA lee la telemetría de los módems, marca al 2 % de hogares con más riesgo de fallar y explica por qué. Si es WiFi o firmware, se corrige a distancia; si es físico, el técnico va una sola vez y con el diagnóstico.
- **Móvil:** cuando cae un sitio, aviso en minutos, antes de que el cliente llame. El prototipo simula el canal WhatsApp; en el piloto, el SMS cubre a quien no tenga WhatsApp.

En ambos frentes, un **grupo control aleatorio del 15 %** mide el efecto real.

<div align="center">
<img src="assets/readme/demo_hogar.gif" alt="Demo Hogar en vivo: la IA marca el hogar días antes de la llamada y se corrige a distancia" width="100%">
<br><sub>Demo «Hogar en vivo»: la IA marca el hogar 4 días antes de la llamada, explica por qué y se corrige a distancia.</sub>
</div>

## Lo que hace

<table>
<tr>
<td width="50%" valign="top">

### Hogar en vivo
La IA detecta la degradación del módem días antes de que el cliente la note y propone la acción: corrección remota o visita con diagnóstico.

<img src="assets/readme/hogar.png" alt="Pantalla Hogar en vivo" width="100%">
</td>
<td width="50%" valign="top">

### Falla masiva en vivo
Cae un sitio: el aviso llega en minutos y un grupo control mide cuántas llamadas se evitan en 72 horas.

<img src="assets/readme/falla.png" alt="Pantalla Falla masiva en vivo" width="100%">
</td>
</tr>
<tr>
<td width="50%" valign="top">

### La IA, medida contra la regla
Con el mismo presupuesto, se compara contra las alarmas por umbral que Tigo ya tiene. Si no gana por 1.3×, se usa la regla.

<img src="assets/readme/modelo.png" alt="Pantalla Modelo de IA" width="100%">
</td>
<td width="50%" valign="top">

### Caso de negocio conservador
Solo ahorro duro, con costos hondureños, escenarios y punto de equilibrio. «Pon tus números» recalcula todo con cuatro datos reales de Tigo, también en la demo web, sin servidor.

<img src="assets/readme/negocio.png" alt="Pantalla Caso de negocio" width="100%">
</td>
</tr>
</table>

## Cómo ver la demo

> [!NOTE]
> GitHub no ejecuta archivos HTML: si abre `index.html` aquí, verá su código. La demo se abre en su computadora o se publica en un hosting estático.

1. **Descargue el archivo.** Abra [`1_Demo/index.html`](1_Demo/index.html) y use el botón **Download raw file**, o descargue todo el repositorio con **Code → Download ZIP** y descomprímalo.
2. **Ábralo con doble clic.** Se abre en el navegador, sin internet y sin instalar nada. Probado en Windows 11 con Microsoft Edge, incluso sin conexión a la red.
3. Entre a **Hogar en vivo ★** y presione **▶ Iniciar**. La historia dura unos 80 segundos. Explore también **Falla masiva en vivo**, **Resultados del piloto** y **Caso de negocio**.

### Modo presentación

El botón **Presentar** (arriba a la derecha) recorre el sistema en **4:32**, dentro de los 5 minutos del concurso. Cada escena abre una pantalla real y, a la izquierda, una tarjeta muestra la idea y las cifras, para que quien presenta cuente la historia sin memorizar números. Espacio pausa; ← y → (o un control remoto de presentaciones) cambian de escena; **S** muestra u oculta los subtítulos, que dicen lo mismo que el guion; **V** cambia entre **Resumen** (láminas para directivos: conclusión, 3 indicadores y una captura real del sistema) y **Completo** (el sistema entero); Esc vuelve a la demo para las preguntas. El guion va aparte: [`Guion_de_la_presentacion.pdf`](2_Documentos/1_Presentacion/Guion_de_la_presentacion.pdf).

<img src="assets/readme/presentacion.png" alt="Modo presentación: tarjeta con la idea a la izquierda y la demo Hogar en vivo a la derecha" width="100%">

### Publicarla en un dominio

Todo lo de la demo está en la carpeta [`1_Demo`](1_Demo). Hay dos formas de publicarla:

- **Este repositorio conectado al hosting** (por ejemplo, Hostinger con GitHub). El [`.htaccess`](.htaccess) de la raíz hace que el dominio muestre la demo directamente: la dirección queda solo como el dominio, sin carpetas, sin `www` y sin `index.html`. Todo lo demás del repositorio (documentos, código, PDF y `.git`) no se sirve: responde 403.
- **Cualquier otro hosting estático:** suba el contenido de `1_Demo`, incluidos `.htaccess` y `.well-known`, a la raíz del dominio.

En los dos casos no hace falta servidor de aplicaciones, base de datos ni internet adicional: los datos van dentro de `index.html`. Dentro de la demo, la dirección del navegador no cambia al pasar de una pantalla a otra.

| Archivo | Para qué sirve |
|---|---|
| `index.html` | La demo completa, con su política de seguridad de contenido: solo corren sus propios scripts (verificados por hash) y no se conecta a ningún servidor externo |
| `.htaccess` | Cabeceras de seguridad, redirección a HTTPS y bloqueo de archivos ocultos en hostings con Apache o LiteSpeed (Hostinger, cPanel y similares) |
| `_headers` | Las mismas cabeceras en Netlify y Cloudflare Pages |
| `robots.txt` | Pide a los buscadores no indexarla; la página también lleva `noindex` |
| `.well-known/security.txt` | Contacto para reportar problemas de seguridad (RFC 9116) |

Probada abriéndola con doble clic y desde un servidor web local: sin errores y sin violaciones de la política de seguridad. Que el hosting aplique `.htaccess` o `_headers` depende del proveedor.

## Cifras clave (escenario base)

| Indicador | Valor |
|---|---|
| **Neto del año 1** | **L 4.3 M**, rango −L 3 M a L 14 M · solo ahorro duro |
| **Punto de equilibrio** | Móvil se paga con 12 % menos llamadas · Hogar, con 22 % menos visitas evitables |
| **IA vs. regla de umbrales** | 52 % vs. 26 % de las visitas evitables anticipadas (2.0×, datos simulados) |
| **Piloto** | 12 semanas en San Pedro Sula · **L 770 mil** (≈ US$ 28 mil) · GO / NO-GO por frente |
| **Costos de referencia** | Visita L 650 · llamada L 65 · WhatsApp L 0.31 por mensaje |

## Por qué ahora

- **Lo prioriza Millicom en 2026:** mejor servicio, eficiencia, flujo de caja y crecer en valor protegiendo el hogar y a los clientes convergentes.
- **Lo exige CONATEL:** el Reglamento de Protección al Usuario NR001/26 (La Gaceta, 28-feb-2026) obliga a avisar a tiempo de averías e interrupciones y a compensar automáticamente las horas sin servicio, con un registro de la duración y las zonas de cada falla. El prototipo ya genera el aviso; el registro para la compensación se construye en el piloto con los datos del NOC.

## Contenido

| Carpeta | Qué tiene |
|---|---|
| [`1_Demo`](1_Demo) | La demo (sitio web): se abre con doble clic o se publica en el dominio |
| [`2_Documentos/1_Presentacion`](2_Documentos/1_Presentacion) | Guion del modo presentación, elevator pitch de 2 minutos y presentación de respaldo (13 diapositivas, PowerPoint y PDF) |
| [`2_Documentos/2_Para_el_jurado`](2_Documentos/2_Para_el_jurado) | Resumen de una página, propuesta completa, datos reales con fuentes, y estrategia y regulación |
| [`2_Documentos/3_Preguntas_y_respaldo`](2_Documentos/3_Preguntas_y_respaldo) | 38 preguntas probables del jurado, guía visual de la demo y presentación extendida |
| [`2_Documentos/4_Envio`](2_Documentos/4_Envio) | Texto del correo de postulación |
| [`2_Documentos/5_Referencias`](2_Documentos/5_Referencias) | Afiche del concurso |
| [`3_Prototipo_completo/tigo-predice`](3_Prototipo_completo/tigo-predice) | Código del prototipo: modelos de IA, API, interfaz, experimento del piloto, caso de negocio y pruebas |

<details>
<summary><b>Prototipo completo: cómo ejecutarlo</b></summary>

<br>

Probado en Windows 11 con Python 3.15 y Node 24: doble clic en `3_Prototipo_completo/tigo-predice/iniciar_demo.bat` y abrir http://127.0.0.1:8000. La primera vez instala las versiones fijadas, genera los datos, entrena los modelos, registra su huella SHA-256 y compila la interfaz (unos 4 minutos); después arranca en segundos.

Si el **Control inteligente de aplicaciones** de Windows está activo, puede bloquear librerías científicas sin firma (como scikit-learn) y el prototipo completo no arrancará. La demo de `1_Demo` no tiene ese problema.

- **Stack:** Python (FastAPI, LightGBM con calibración isotónica y explicaciones SHAP, SQLite) y React con Vite, TypeScript, Tailwind y Recharts.
- **Pruebas:** 230 de Python (última ejecución completa: 22-oct-2026) y 28 de la interfaz, más análisis estático con reglas de seguridad y auditoría de dependencias sin vulnerabilidades conocidas.
- **Reproducible:** el pipeline completo regenera los mismos datos, modelos y cifras desde cero.

Detalles en el [README del prototipo](3_Prototipo_completo/tigo-predice/README.md).
</details>

<details>
<summary><b>Seguridad y privacidad</b></summary>

<br>

- **Marcos de referencia:** GDPR (Honduras aún no tiene ley integral de datos personales), ISO 27001/27701/42001, SOC 2, NIST CSF y AI RMF, OWASP ASVS, API y LLM, y MITRE ATLAS.
- **Datos mínimos:** solo el desempeño del módem y de la línea; nunca contenido, navegación ni los dispositivos del cliente.
- **Controles:** sesión firmada (HMAC) y revocable, roles, protección CSRF, cabeceras de seguridad, bitácoras seudonimizadas y huella SHA-256 de cada modelo verificada antes de cargarlo.
- **Estándares:** mapeo al OWASP Top 10:2025, accesibilidad WCAG 2.2 AA sin infracciones automáticas (axe-core), SBOM CycloneDX y política de seguridad ([`SECURITY.md`](SECURITY.md)). Detalle y pendientes en [`docs/estandares_y_calidad.md`](3_Prototipo_completo/tigo-predice/docs/estandares_y_calidad.md).
- **Red team propio:** 12 ataques probados y corregidos, cada uno con su prueba automática.

Detalle en [`docs/seguridad_y_privacidad.md`](3_Prototipo_completo/tigo-predice/docs/seguridad_y_privacidad.md).
</details>

<details>
<summary><b>Qué es real y qué es supuesto</b></summary>

<br>

- **Real (público):** base de clientes de Tigo Honduras (Millicom, Form 20-F 2025), precios de los planes, tipo de cambio del BCH, tarifas de WhatsApp Business, costos de centros de contacto en Honduras y el reglamento NR001/26 de CONATEL.
- **Supuesto, a validar con Tigo:** visitas técnicas al mes, porcentaje de visitas evitables, costo real por visita y por llamada, y el efecto de los avisos.
- **Simulado:** la telemetría, los clientes y los resultados del modelo y del piloto.

Fuentes completas en [`2_Documentos/2_Para_el_jurado/Datos_Reales_y_Revision.pdf`](2_Documentos/2_Para_el_jurado/Datos_Reales_y_Revision.pdf).
</details>

## Autoría

**Sandra Michel Jimenez Zelaya** · Asistente de Experiencia B2B · Tigo Honduras · [sandra.jimenez@tigo.com.hn](mailto:sandra.jimenez@tigo.com.hn)
