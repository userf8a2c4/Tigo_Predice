# Estándares internacionales y calidad del código

Revisión del 23 de octubre de 2026. Cada fila dice qué se cumple, con qué evidencia y qué falta. Lo que no está verificado se marca como pendiente.

## 1. OWASP Top 10:2025

| Riesgo | Control en el prototipo | Evidencia |
|---|---|---|
| A01 Control de acceso roto | Roles separados (consulta, operador, auditor); sin token, el servidor solo atiende a la misma máquina | `backend/app/seguridad.py`, `tests/test_seguridad.py` |
| A02 Configuración insegura | Cabeceras de seguridad (CSP, HSTS, nosniff, X-Frame-Options), `no-store` en la API y `/docs` apagado en producción | `backend/app/main.py`, pruebas de cabeceras |
| A03 Fallas en la cadena de suministro | Versiones fijadas, auditoría de dependencias sin vulnerabilidades conocidas y SBOM CycloneDX. Ese día se corrigió certifi (PYSEC-2026-4320) | `requirements.lock`, `frontend/package-lock.json`, `sbom/` |
| A04 Fallas criptográficas | Sesión firmada con HMAC, cookies HttpOnly, SameSite=Strict y Secure con HTTPS; tokens de 24 caracteres o más | `backend/app/seguridad.py` |
| A05 Inyección | Consultas parametrizadas, búsqueda literal (sin expresiones regulares del usuario), nombres saneados y texto libre redactado antes del LLM | `backend/app/estado.py`, `services/mensajes.py`, `privacidad.py` |
| A06 Diseño inseguro | Red team propio con 12 ataques probados y corregidos; privacidad desde el diseño | `docs/seguridad_y_privacidad.md` |
| A07 Fallas de autenticación | Sesiones revocables, límite de peticiones y verificación de origen (CSRF) | `tests/test_seguridad.py` |
| A08 Fallas de integridad | Huella SHA-256 de cada modelo verificada antes de cargarlo | `ml/manifiesto.py` |
| A09 Fallas de registro y alerta | Bitácora de accesos con sesión seudonimizada y sin parámetros de consulta; purga a 90 días | `backend/app/services/bitacora.py` |
| A10 Mal manejo de condiciones excepcionales | Sin excepciones capturadas a ciegas (regla BLE de ruff, obligatoria); si el LLM falla, se usan plantillas aprobadas | `pyproject.toml`, `backend/app/llm_client.py` |

## 2. Accesibilidad: WCAG 2.2 nivel AA

- **Herramienta:** axe-core 4.10.2 con las reglas de WCAG 2.0, 2.1 y 2.2 niveles A y AA.
- **Alcance:** las 11 pantallas de la demo, incluidas las dos demos en vivo con su resultado final, y las 11 escenas del modo presentación (22 vistas).
- **Resultado:** 0 infracciones automáticas.
- **Correcciones hechas:**
  - contraste de los textos secundarios y de los colores de éxito y alerta, ahora de 4.5:1 o más;
  - nombre accesible en los marcadores del mapa;
  - objetivos táctiles de 24 px o más;
  - etiquetas en los filtros;
  - zonas con desplazamiento alcanzables con el teclado.
- **Pendiente:** prueba manual con lector de pantalla (NVDA) y recorrido completo solo con teclado. Las herramientas automáticas detectan solo una parte de los problemas.

## 3. Cadena de suministro y prácticas de OpenSSF Scorecard

| Práctica | Estado |
|---|---|
| Política de seguridad (`SECURITY.md`) | Cumplido |
| Dependencias fijadas | Cumplido: `requirements.lock` y `package-lock.json` |
| Sin binarios en el repositorio | Cumplido: se retiró el lanzador `.exe` sin firma |
| SBOM | Cumplido: CycloneDX para Python y para el frontend |
| Análisis estático | Cumplido: ruff (E, F, W, I, B, UP, S, BLE), ESLint y TypeScript estricto |
| Integración continua, protección de rama y versiones firmadas | **Pendiente:** decisión de quien administra el repositorio |

## 4. Pruebas

- **Python:** 230 pruebas (unitarias, API, seguridad y consistencia de cifras). Pasaron completas el 22 de octubre de 2026.
- **Interfaz:** 11 pruebas; pasan el 23 de octubre de 2026.
- **Limitación honesta:** el 23 de octubre, el Control inteligente de aplicaciones de Windows bloqueó una librería de scikit-learn en la computadora de desarrollo. Por eso las pruebas de Python no se pudieron repetir ese día. Los cambios de ese día en Python fueron de configuración (regla BLE, certifi) y de texto, y no tocaron la lógica.

## 5. Pendientes para llegar al máximo nivel
1. Volver a mapear los controles al **OWASP ASVS 5.0** (publicado en 2025); el mapeo actual usa la versión 4.0.
2. Prueba manual de accesibilidad con lector de pantalla.
3. Integración continua con pruebas y auditoría en cada cambio, más protección de la rama principal.
4. Firmar digitalmente cualquier ejecutable que se distribuya.

## Fuentes
- OWASP Top 10:2025: https://owasp.org/Top10/2025/
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- OpenSSF Scorecard: https://github.com/ossf/scorecard
- CycloneDX: https://cyclonedx.org/
