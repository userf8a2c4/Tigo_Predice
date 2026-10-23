# Seguridad, privacidad y cumplimiento — Tigo Predice v03

> **Alcance y honestidad.** Este documento describe cómo Tigo Predice se diseñó y se probó para cumplir con el
> marcos internacionales de seguridad y privacidad. **No es asesoría legal ni una certificación**: la
> validación legal la hace Legal y Privacidad de Tigo/Millicom, y una certificación (ISO, SOC 2) solo la otorga
> una auditoría independiente. Cada control indica si **ya está implementado y probado en el prototipo** o si
> **es un requisito para producción** con dueño y semana del plan.
> Revisión: 14 de octubre de 2026.

---

## 1. Resumen para el comité

- **Marcos de referencia:** ISO/IEC 27001, 27017, 27018, 27701 y 42001,
  SOC 2, NIST CSF 2.0, NIST AI RMF, OWASP (API y LLM), el pilar de seguridad de AWS Well-Architected y el
  **GDPR como estándar de referencia**.
- **Honduras no tiene todavía una ley integral de protección de datos** para el sector privado: el proyecto está
  pendiente en el Congreso desde 2018. Por eso aplicamos el estándar más exigente (GDPR) como base. Cuando la ley
  hondureña se apruebe, el sistema ya cumplirá sus principios.
- **Privacidad desde el diseño:**
  - **Sin contenido:** no lee el contenido de las comunicaciones ni el historial de navegación; tampoco los dispositivos del hogar.
  - **Lo mínimo al modelo de lenguaje:** solo recibe el nombre de pila y el tipo de situación.
  - **Sin efectos sobre el cliente:** la IA solo decide a quién atender primero; no niega servicio, no cobra, no cambia condiciones.
- **Ejercicio de red team:** se atacó la propia API y se confirmaron **8 debilidades reales** y 4 riesgos de diseño.
  **Todos están corregidos** y cada uno tiene su prueba de regresión (sección 7b).
- **Ya implementado y con tests automáticos (sección 12):**
  - cabeceras de seguridad, CSP y HSTS;
  - sesión firmada y **revocable**, con roles (lectura, operador y auditor);
  - bloqueo por intentos y tokens de 24 caracteres como mínimo;
  - defensa CSRF por origen;
  - en modo demo, solo acceso local;
  - límite de peticiones y parámetros acotados;
  - búsqueda sin regex;
  - guardrail anti-phishing y nombres saneados antes del LLM;
  - **huella SHA-256 de cada modelo verificada** antes de cargarlo;
  - dependencias fijadas y auditadas;
  - bitácoras de mensajes (90 días) y de accesos (solo el auditor las lee);
  - logs sin datos de consulta, minimización en pantallas, consentimiento y opt-out.
- **Para producción:**
  - SSO corporativo con MFA y roles;
  - cifrado con claves gestionadas;
  - red privada y WAF;
  - acuerdos de tratamiento de datos (DPA) con proveedores;
  - evaluación de impacto aprobada;
  - prueba de penetración.

  Todo está en el plan de las semanas 0–2 (sección 11).

---

## 2. Marco legal y normativo

### Honduras

| Norma | Qué exige | Cómo lo cumple Tigo Predice |
|---|---|---|
| Constitución, art. 76 | Protección del honor, la intimidad personal y familiar y la propia imagen | Minimización: solo datos necesarios para atender; nada de contenido ni hábitos de navegación |
| Constitución, art. 100 | Inviolabilidad y secreto de las comunicaciones (salvo resolución judicial) | **No accede a contenido** de llamadas, mensajes ni tráfico. La telemetría es de desempeño del equipo y la línea |
| Constitución, art. 182 (habeas data, reforma Decreto 10-2013) | Toda persona puede acceder, rectificar, actualizar y exigir confidencialidad de sus datos en registros públicos o privados | Derechos atendidos por los canales de Tigo (sección 5); trazabilidad de cada mensaje en la bitácora |
| Ley de Transparencia y Acceso a la Información Pública | Protege datos personales en entes públicos (IAIP) | No aplica directamente a Tigo; se toma como referencia de buenas prácticas |
| Proyecto de Ley de Protección de Datos Personales (pendiente desde 2018) y la nueva iniciativa presentada en el Congreso | Principios de finalidad, consentimiento y seguridad, con supervisión del IAIP | Diseñado para cumplirla: finalidad única, consentimiento para mensajes, seguridad y retención |
| Regulación de telecomunicaciones (CONATEL) y Ley Especial para la Intervención de las Comunicaciones Privadas | Derechos de los usuarios, secreto de las comunicaciones, comunicación de interrupciones | Validar con Legal los requisitos de aviso y compensación; la intervención de comunicaciones queda **fuera** del sistema |
| Código Penal (delitos contra la intimidad) | Sanciona el acceso y la revelación indebidos de datos y comunicaciones | Controles de acceso, bitácora y mínimo privilegio. Legal valida los artículos aplicables |

### Internacional y de grupo

| Marco | Uso en el proyecto |
|---|---|
| Política Global de Privacidad de Millicom | Política del grupo (con sede en Luxemburgo y que cotiza en Nasdaq): marco interno obligatorio |
| GDPR (Reglamento UE 2016/679) | **Estándar de referencia**. Se usan sus principios (art. 5), bases legales (art. 6), transparencia (art. 13), decisiones automatizadas (art. 22), privacidad desde el diseño (art. 25), seguridad (art. 32) y evaluación de impacto (art. 35). Su aplicación directa a los datos de Honduras no es automática; aquí se adopta como referencia |
| Estándares de Protección de Datos Personales para los Estados Iberoamericanos (RIPD, 2017) | Referencia regional: principios y derechos alineados con el GDPR |
| Directrices de privacidad de la OCDE y Convenio 108+ | Referencia de principios |
| ISO/IEC 27001:2022 · 27017 · 27018 · 27701 | Sistema de gestión de seguridad y de privacidad, y controles para la nube y para datos personales en la nube |
| ISO/IEC 42001:2023 y NIST AI RMF 1.0 | Gobierno de la IA: riesgos, sesgo, supervisión humana, monitoreo y documentación del modelo |
| SOC 2 (Trust Services Criteria) | Seguridad, disponibilidad, integridad del procesamiento, confidencialidad y privacidad |
| NIST CSF 2.0 | Funciones: Gobernar, Identificar, Proteger, Detectar, Responder y Recuperar |
| OWASP API Security Top 10 (2023) y OWASP Top 10 para aplicaciones con LLM (2025) | Revisión de cada endpoint y del uso del modelo de lenguaje (secciones 6 y 7) |
| OWASP ASVS 4.0, nivel 2 | Nivel objetivo para aplicaciones que manejan datos personales: autenticación, sesión, control de acceso, validación y registro |
| NIST SP 800-63B | Autenticación: secretos largos, limitación de intentos y sesiones con vencimiento y revocación |
| CWE Top 25 y MITRE ATLAS | Clasificación de las debilidades encontradas (CWE) y de las amenazas propias de sistemas de IA (ATLAS) |
| SLSA y SBOM (CycloneDX) | Cadena de suministro: dependencias fijadas y auditadas, artefactos (modelos) con huella verificada |
| AWS Well-Architected, pilar de seguridad | Identidad, detección, protección de infraestructura y de datos, respuesta a incidentes |
| Política de WhatsApp Business (Meta) | Opt-in previo, plantillas aprobadas y opt-out inmediato |
| Ley de IA de la UE (referencia) | No aplica en Honduras. Por su función (atención al cliente, sin efectos jurídicos) no encaja en los casos de alto riesgo; se aplican igual la transparencia y la supervisión humana |

---

## 3. Qué datos usa (inventario y minimización)

| Dato | Fuente | Para qué | Base legal (referencia GDPR) | Retención propuesta | Quién lo ve |
|---|---|---|---|---|---|
| Telemetría del módem: margen de señal, errores, reinicios, micro-cortes, latencia, retransmisiones WiFi, **número** de dispositivos, GB/día agregados | ACS (TR-069) y gestores de OLT/CMTS | Detectar degradación y corregirla | Ejecución del contrato e interés legítimo (calidad del servicio) | 90 días el detalle diario; luego agregados seudonimizados para reentrenar | El sistema; soporte N2 ve el resumen y los motivos |
| Cliente ↔ nodo / sitio | Inventario de red | Saber a quién afecta una falla | Ejecución del contrato | Mientras dure el servicio | El sistema |
| Móvil: afectado sí/no en una falla masiva | NOC + última celda registrada | Avisar a los afectados | Interés legítimo / contrato | Solo la marca de «afectado», **sin historial de ubicación**; 12 semanas para medir, luego agregado | El sistema |
| Nombre de pila, teléfono, canal, consentimiento, opt-out | CRM | Enviar el aviso | **Consentimiento** para mensajes; el opt-out se respeta siempre | Según la política de Tigo | El sistema; el agente cuando escala |
| Llamadas y visitas técnicas | Call center y operaciones de campo | Medir el efecto contra el control | Interés legítimo (mejora del servicio) | 12 semanas de detalle; luego agregado | Analista del piloto (seudonimizado) |
| Mensajes enviados (bitácora) | Tigo Predice | Auditoría y calidad | Responsabilidad proactiva | **90 días (implementado)** | Auditor / líder del piloto |
| Accesos a la API (bitácora) | Tigo Predice | Trazabilidad de quién consultó qué | Seguridad (art. 32) | 1 año en producción | Seguridad / auditoría |

**No se usa nunca:**
- contenido de llamadas, mensajes o tráfico;
- historial de navegación ni DNS;
- direcciones MAC ni nombres de los dispositivos del hogar;
- ubicación GPS;
- datos de menores;
- datos sensibles (salud, religión, etc.).

**Lo que recibe el modelo de lenguaje:** nombre de pila, ciudad, plan y el tipo de situación («corregimos la inestabilidad a distancia»). **Nunca** recibe el ID de cliente, el teléfono, la ubicación ni el historial; está probado con tests. El texto libre que escribe un cliente se **redacta** antes de enviarse: los números largos, como la identidad o una tarjeta, y los correos se reemplazan.

---

## 4. Principios de protección de datos → cómo se cumplen

| Principio (GDPR art. 5 / RIPD) | Implementación | Evidencia |
|---|---|---|
| Licitud, lealtad y transparencia | El aviso de privacidad de Tigo informa del uso de telemetría para atención proactiva; los mensajes dicen quién escribe y por qué | `listo_para_produccion.md`; plantillas |
| Limitación de la finalidad | La telemetría solo se usa para atender fallas. **Prohibido por diseño** usarla para publicidad o perfiles comerciales; churn y retención (Fase 2) requieren su propia evaluación | Este documento, sección 6 |
| Minimización | Solo variables de desempeño; nombre corto y teléfono enmascarado en pantallas; sin coordenadas del hogar en la API | `test_vistas_operativas_minimizan_datos_personales` |
| Exactitud | Auditoría del mapeo cliente ↔ nodo en las semanas 0–2; se mide el % de avisos a no afectados | Plan del piloto |
| Limitación del plazo de conservación | Bitácora de mensajes: 90 días con borrado automático; resto según la tabla de la sección 3 | `bitacora.purgar` |
| Integridad y confidencialidad | Sesión firmada, cabeceras, límites, logs sin consulta, cifrado en producción | `test_seguridad.py` |
| Responsabilidad proactiva | Bitácoras de mensajes y accesos, versión del prompt, documentación del modelo, tests automáticos | `reports/modelo.md`; bitácoras |

---

## 5. Derechos de los clientes (habeas data y derechos ARCO+)

| Derecho | Cómo se ejerce |
|---|---|
| Acceso, rectificación y supresión | Por los canales oficiales de Tigo. La bitácora permite responder qué mensajes recibió una persona y por qué |
| Oposición a los mensajes | Responder **BAJA** o **NO** registra el opt-out al instante y para siempre. El hogar sigue recibiendo la corrección remota (que es parte del servicio), pero sin mensajes |
| Portabilidad | Exportación de sus datos por los canales de Tigo |
| No ser objeto de decisiones automatizadas con efectos significativos | La IA **solo prioriza atención**: no niega servicio, no cobra, no cambia precios ni condiciones. Siempre hay una persona disponible (AGENTE) |

Plazo de respuesta propuesto: 15 días hábiles, a confirmar con Legal.

---

## 6. IA responsable (ISO/IEC 42001 · NIST AI RMF · OWASP LLM Top 10 2025)

- **Qué decide la IA:** a qué hogares atender primero cada semana y por qué (con explicación por variables, SHAP).
- **Qué no decide:** precios, cortes, cobros, crédito, ofertas comerciales ni sanciones.
- **Supervisión humana y criterio objetivo:** si con datos reales la IA no supera a la regla de umbrales por 1.3×, se usa
  la regla. Ese es un criterio del GO/NO-GO.
- **Sesgo:** se monitorea por tecnología (fibra/HFC) y zona (urbana/periurbana). Se exige que el % marcado sea
  proporcional a la tasa real y que ningún grupo quede sin captura.
- **Monitoreo:** calibración y deriva mensual, reentrenamiento con validación temporal y documentación del modelo
  (`reports/modelo.md`).
- **Acciones remotas sobre el módem:**
  - Lista cerrada de acciones: reinicio programado, cambio de canal WiFi y firmware certificado.
  - Nunca cambia contraseñas ni entra a la red interna del cliente.
  - Se ejecutan en ventana de madrugada, por lotes y con reversión.
  - Las ejecuta el ACS por reglas, **nunca el modelo de lenguaje**.

| Riesgo OWASP LLM (2025) | Control |
|---|---|
| LLM01 Inyección de prompt | El texto del cliente solo se usa para clasificar la intención entre opciones cerradas; la salida fuera de lista se descarta |
| LLM02 Revelación de información sensible | El LLM no recibe identificadores; el texto libre se redacta antes del envío (probado) |
| LLM05 Manejo inseguro de la salida | Guardrails (300 caracteres, usted, sin datos sensibles, sin horas inventadas, AGENTE). Si fallan, se usa la plantilla aprobada. Se muestra como texto plano (React escapa; no se usa HTML) |
| LLM06 Agencia excesiva | El LLM no tiene herramientas ni puede ejecutar acciones: solo redacta texto |
| LLM09 Desinformación | Solo usa datos del NOC; si no hay hora estimada, no la menciona (guardrail probado) |
| LLM10 Consumo sin límite | `max_tokens` fijo, límite de peticiones por IP y plantilla de respaldo |

---

## 7. Revisión de endpoints (OWASP API Security Top 10, 2023)

| Riesgo | Estado en el prototipo | Control en producción |
|---|---|---|
| API1 Autorización a nivel de objeto (BOLA) | Endpoints por ID solo en la Fase 2 (visión); en modo demo, solo acceso local (probado) | Autorización por rol y ámbito (por ejemplo, soporte N2 solo ve su ciudad y sus casos) |
| API2 Autenticación rota | ✅ En modo protegido: sesión firmada HMAC-SHA256 y **revocable en el servidor**, HttpOnly, SameSite=Strict, Secure con HTTPS o en producción, 8 h, renovada al entrar (evita fijación), bloqueo tras 5 intentos, tokens de 24 caracteres como mínimo (probado) | SSO corporativo (OIDC) con MFA |
| API3 Exposición excesiva de propiedades | ✅ Nombre corto, teléfono enmascarado, sin coordenadas del hogar (probado) | Esquemas de respuesta por rol |
| API4 Consumo de recursos sin límite | ✅ 600 peticiones por minuto por IP y parámetros acotados (probado) | API gateway con cuotas y WAF |
| API5 Autorización a nivel de función | ✅ Roles: **lectura** solo consulta, **operador** ejecuta acciones y **auditor** además lee las bitácoras (probado) | Mismos roles desde el SSO corporativo |
| API6 Flujos de negocio sensibles | ✅ Tope de mensajes (2 por falla, 1 proactivo por semana) y opt-out | Monitoreo de envíos anómalos |
| API7 SSRF | ✅ La API no consulta URLs que provengan del usuario (el LLM tiene URL fija) | Salida a internet solo por proxy con lista blanca |
| API8 Configuración insegura | ✅ CSP, nosniff, X-Frame-Options DENY, no-referrer, `no-store` en la API, CORS restringido, documentación interactiva apagada con `TIGO_PRODUCCION=1` (probado) | Endurecimiento del contenedor y escaneo |
| API9 Inventario deficiente | OpenAPI generado y versionado (v3.0) | Inventario en el API gateway |
| API10 Consumo inseguro de APIs | ✅ La respuesta del LLM pasa por guardrails antes de usarse | Igual + monitoreo |

**Otros controles revisados:**
- **Inyección SQL:** consultas parametrizadas (sqlite3/SQLAlchemy), sin concatenar texto.
- **XSS:** React escapa todo; no hay `innerHTML` ni `eval`.
- **Path traversal:** el frontend solo sirve archivos dentro de `frontend/dist` (probado).
- **Secretos:** `.env` y la base de datos están fuera de git, y se revisó el historial sin hallazgos.
- **Exposición del servidor:** escucha solo en 127.0.0.1.
- **Dependencias** (14/10/2026): `pip-audit` y `npm audit` sin vulnerabilidades conocidas.
- **Análisis estático:** reglas de seguridad de ruff (equivalentes a Bandit, `S`) activas en el lint.

---

## 7b. Ejercicio de red team: ataques probados contra la propia API

Se atacó el prototipo como lo haría un adversario. Cada ataque se ejecutó contra la API real **antes** de corregirlo,
para confirmar que funcionaba. Después se corrigió y quedó una prueba automática que impide que vuelva a aparecer.

| # | Ataque probado | Clasificación | Severidad | Antes | Corrección | Prueba de regresión |
|---|---|---|---|---|---|---|
| 1 | Búsqueda con `q=(` o `(a+)+$` (inyección de regex / ReDoS) | CWE-1333 · OWASP API4 | Media | Error 500 | La búsqueda es literal (`regex=False`), con largo máximo | `test_busqueda_no_interpreta_regex` |
| 2 | El LLM devuelve un mensaje con un enlace fraudulento («ganó un premio: ingrese a…») | OWASP LLM05 · CWE-601 | **Alta** | Pasaba los guardrails | Guardrail anti-phishing: ningún enlace salvo los dominios oficiales de Tigo; si falla, se usa la plantilla aprobada | `test_guardrail_anti_phishing` |
| 3 | Nombre del CRM con instrucciones («Ignora las reglas…», `<script>`) que llega al prompt | OWASP LLM01 · CWE-74 | Media | Llegaba tal cual | Solo letras, máximo 20 caracteres | `test_nombre_del_crm_no_inyecta_instrucciones` |
| 4 | Reusar una cookie robada después de que el usuario cerró sesión | OWASP API2 · CWE-613 · NIST 800-63B | **Alta** | Seguía válida (200) | Sesiones registradas en el servidor: cerrar sesión las revoca; nueva sesión al entrar | `test_cookie_robada_no_sirve_despues_de_cerrar_sesion` |
| 5 | Un usuario de consulta ejecuta acciones (enviar mensajes, reiniciar) | OWASP API5 · CWE-285 | **Alta** | Permitido | Roles: lectura, operador y auditor | `test_rol_lectura_no_ejecuta_acciones_ni_lee_bitacoras` |
| 6 | Cualquier sesión lee la bitácora con los textos enviados a clientes | OWASP API3 · CWE-200 | **Alta** | Permitido | Solo el rol auditor lee las bitácoras | `test_solo_el_auditor_lee_las_bitacoras` |
| 7 | Petición que cambia estado desde otro sitio (CSRF) | CWE-352 | Media | Aceptada | Rechazo por origen (403), además de SameSite=Strict | `test_peticion_desde_otro_origen_se_rechaza` |
| 8 | Token de acceso de 3 caracteres | CWE-521 · NIST 800-63B | Media | Aceptado | Mínimo de 24 caracteres; si no se cumple, la API no opera (503) | `test_token_debil_falla_en_modo_seguro` |
| 9 | Archivo de modelo alterado (joblib/pickle ejecuta código al cargarse) | CWE-502 · MITRE ATLAS (cadena de suministro de ML) | **Alta** | Se cargaba sin verificar | Firma SHA-256 en un manifiesto; el servidor se niega a cargar un modelo alterado o no firmado | `test_modelo_alterado_no_se_carga` |
| 10 | Exponer el servidor en la red sin configurar acceso | OWASP API8 · CWE-306 | **Alta** | Abierto a la red | En modo demo, solo responde a la misma máquina (403 a cualquier otra) | `test_modo_demo_rechaza_acceso_que_no_es_local` |
| 11 | Dependencias sin versión fija (cadena de suministro) | SLSA · CWE-1104 | Media | Versiones abiertas | `requirements.lock` con versiones exactas, auditado con pip-audit (sin hallazgos) | `tareas.ps1 seguridad` |
| 12 | Abuso del LLM: cada petición a la demo generaba mensajes nuevos (costo, DoS) | OWASP LLM10 | Baja | Una llamada por petición | Las demos son deterministas y se calculan una sola vez; además hay límite de peticiones | `test_limite_de_peticiones` |

**Cómo se ataca un sistema de IA y cómo se cubre (MITRE ATLAS):**

| Táctica | Cobertura |
|---|---|
| Envenenamiento de datos de entrenamiento | La telemetría viene de sistemas de red, no de los clientes; validación temporal y monitoreo de deriva; el modelo solo prioriza atención |
| Evasión del modelo | No hay incentivo, porque el «castigo» es recibir mejor servicio; la regla de umbrales sigue de respaldo |
| Inferencia de pertenencia o extracción del modelo | Los puntajes solo los ven roles internos; la API pública no expone puntajes por cliente |
| Inyección de prompt | El LLM no tiene herramientas, la entrada se sanea, la salida se valida y la plantilla queda de respaldo |
| Cadena de suministro de ML | Modelos con huella SHA-256 verificada; dependencias fijadas y auditadas |

**Riesgos residuales que solo se cierran en producción:**
- autenticación corporativa con MFA;
- TLS de extremo a extremo;
- cifrado con KMS;
- WAF;
- prueba de penetración independiente;
- firma del manifiesto con una clave del gestor de secretos.

El prototipo **falla en modo seguro** mientras tanto: sin configuración, solo atiende a la misma máquina.

---

## 8. Arquitectura de seguridad para producción (marcos internacionales)

| Dominio | Control |
|---|---|
| Identidad y acceso | SSO corporativo (Entra ID / Okta) con MFA; roles (analista, soporte N2, NOC, auditor, administrador); mínimo privilegio; revisión trimestral de accesos; cuentas de servicio con credenciales rotadas |
| Red | Red privada (VPC) sin exposición pública; API detrás de gateway y WAF; TLS 1.2 o superior (preferible 1.3); mTLS entre servicios |
| Datos | Cifrado en reposo AES-256 con claves gestionadas (KMS) y rotación; seudonimización con la tabla de equivalencias en una bóveda separada; backups cifrados; ambientes separados; en desarrollo solo datos sintéticos o anonimizados |
| Registro y detección | Logs centralizados e inmutables (bitácora de accesos por 1 año), SIEM con alertas y detección de anomalías |
| Secretos | Gestor de secretos; nunca en código ni en variables visibles |
| Ciclo de desarrollo seguro | Revisión de código, SAST, SCA (pip-audit, npm audit), SBOM (CycloneDX), escaneo de contenedores, modelado de amenazas por cambio relevante, prueba de penetración antes de salir a producción y luego cada año |
| Proveedores | DPA con el proveedor del LLM: retención cero y sin entrenamiento con datos de Tigo, o Claude en la nube corporativa de Tigo con región definida. DPA con el proveedor de WhatsApp Business. Cláusulas para transferencias internacionales |
| Continuidad | Si Tigo Predice falla, Tigo opera como hoy: no es un punto único de falla. RPO de 24 h y RTO de 4 h para el piloto |
| Incidentes | Plan con roles y tiempos; notificación a los afectados y a la autoridad cuando la ley lo exija (referencia: 72 h del GDPR); simulacro antes del piloto |

---

## 9. Modelo de amenazas (STRIDE, resumido)

| Amenaza | Ejemplo | Mitigación |
|---|---|---|
| Suplantación | Alguien usa la API sin permiso | Sesión firmada o SSO, bloqueo por intentos, bitácora de accesos |
| Manipulación | Alterar puntajes o mensajes | Escritura solo por roles; bitácora de solo anexar; versión del modelo y del prompt registradas |
| Repudio | «Yo no envié ese mensaje» | Bitácora con fecha, acción, fuente (plantilla o IA), versión del prompt y guardrails |
| Revelación de información | Fuga de datos de clientes | Minimización, seudonimización, cifrado, sin PII en logs ni en el LLM |
| Denegación de servicio | Saturar la API o el LLM | Límite de peticiones, `max_tokens` y plantilla de respaldo |
| Elevación de privilegios | Un usuario de consulta ejecuta acciones | Roles y separación de funciones; las acciones remotas solo desde el ACS con lista cerrada |

---

## 10. Evaluación de impacto en la privacidad (EIPD, resumida)

| Riesgo para el cliente | Probabilidad | Impacto | Mitigación | Riesgo residual |
|---|---|---|---|---|
| Mensaje a la persona equivocada (número reasignado o mapeo erróneo) | Media | Medio | El mensaje no contiene datos sensibles; validación del número en CRM; auditoría del mapeo en las semanas 0–2 | Bajo |
| Uso de la telemetría para otros fines (marketing) | Baja | Alto | Finalidad única por diseño, aprobación de Privacidad para cualquier uso nuevo y bitácora | Bajo |
| Fuga de datos | Baja | Alto | Controles de las secciones 7 y 8 y datos mínimos | Bajo |
| Sesgo: zonas atendidas peor | Media | Medio | Monitoreo por zona y tecnología; criterio de captura por grupo | Bajo |
| Acción remota que deja al cliente sin servicio | Baja | Medio | Lista cerrada, firmware certificado, madrugada, lotes y reversión | Bajo |
| Molestia por mensajes | Baja | Bajo | Tope de frecuencia, opt-out y criterio NO-GO si el opt-out supera el 2 % | Muy bajo |

---

## 11. Lista de verificación antes del primer mensaje del piloto

| # | Acción | Dueño | Semana |
|---|---|---|---|
| 1 | EIPD completa aprobada por Privacidad y Legal | Legal / Privacidad | 0–1 |
| 2 | Aviso de privacidad actualizado (telemetría para atención proactiva) | Legal | 1 |
| 3 | Confirmar que el contrato permite la gestión remota del equipo | Legal | 0 |
| 4 | Plantillas de WhatsApp aprobadas (Meta, Marca, Legal) | Canales digitales | 1 |
| 5 | DPA con el proveedor del LLM y del canal de WhatsApp | Compras / Legal | 1 |
| 6 | Registro de actividades de tratamiento | Privacidad | 1 |
| 7 | SSO con MFA y roles; `TIGO_PRODUCCION=1` | TI / Seguridad | 2 |
| 8 | Cifrado con claves gestionadas, red privada y WAF | TI / Seguridad | 2 |
| 9 | Prueba de penetración de la integración | Seguridad | 2 |
| 10 | Retención y borrado configurados; simulacro de incidente | Datos / Seguridad | 2 |

---

## 12. Evidencias en el prototipo (tests automáticos)

`tests/test_seguridad.py` (36 pruebas):
- **Los 12 ataques del red team**, uno por uno (sección 7b).
- `test_cabeceras_de_seguridad`: CSP, nosniff, DENY, no-referrer y `no-store`.
- `test_con_tokens_toda_la_api_exige_sesion`: cookie HttpOnly y SameSite=Strict; el token nunca viaja en la cookie.
- `test_sesion_firmada_revocable_y_con_vencimiento` y `test_roles`.
- `test_bloqueo_por_intentos_fallidos` y `test_limite_de_peticiones`.
- `test_parametros_fuera_de_rango_se_rechazan` (7 casos) y `test_no_se_sirven_archivos_fuera_del_frontend`.
- `test_vistas_operativas_minimizan_datos_personales`, `test_contexto_del_llm_no_lleva_identificadores`, `test_redaccion_antes_del_llm` y `test_logs_sin_parametros_de_consulta`.
- `test_modelos_actuales_coinciden_con_su_firma`.

`tests/test_guardrails.py`: 82 casos de mensajes (usted, sin datos sensibles, sin horas inventadas, AGENTE).

`tareas.ps1 seguridad` corre todo junto:
- análisis estático (reglas S, equivalentes a Bandit);
- `pip-audit` sobre `requirements.lock`;
- `npm audit`;
- las pruebas de seguridad y guardrails.

Resultado al 14/10/2026: **sin hallazgos**.

---

## Fuentes

- [DLA Piper: Data Protection in Honduras](https://www.dlapiperdataprotection.com/index.html?c=HN&t=law)
- [El Heraldo: IAIP y la Ley de Protección de Datos Personales](https://www.elheraldo.hn/honduras/iaip-destaca-beneficios-honduras-ley-proteccion-datos-personales-BP26294115)
- [El País (Honduras): nueva iniciativa de ley de datos personales](https://www.elpais.hn/diputada-kritza-perez-presenta-ley-para-proteger-datos-personales-en-honduras/)
- [Decreto 10-2013 (reforma del art. 182, habeas data)](https://oncae.gob.hn/wp-content/uploads/2024/05/Decreto-10-2013.pdf)
- [Consortium Legal: Protección de datos y privacidad en Honduras](https://consortiumlegal.com/2022/09/06/proteccion-de-datos-y-privacidad-de-la-informacion-en-honduras/)
- [GSMA: Ley para la Protección de los Usuarios de las Telecomunicaciones](https://www.gsma.com/latinamerica/es/honduras-ley-para-la-proteccion-de-los-usuarios-de-las-telecomunicaciones-perjudica-privacidad-e-inclusion-digital/)
- Reglamento (UE) 2016/679 (GDPR); ISO/IEC 27001:2022, 27701:2019 y 42001:2023; NIST CSF 2.0; NIST AI RMF 1.0;
  OWASP API Security Top 10 (2023); OWASP Top 10 for LLM Applications (2025); AWS Well-Architected, pilar de seguridad.
