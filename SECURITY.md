# Política de seguridad

## Alcance
Este repositorio contiene un **prototipo** con datos simulados. No procesa datos reales de clientes de Tigo y no está desplegado en producción.

## Cómo reportar una vulnerabilidad
Escriba a **sandra.jimenez@tigo.com.hn** con:
- la descripción del problema y su impacto;
- los pasos para reproducirlo;
- la versión o commit afectado.

No publique el detalle en issues públicos hasta que esté corregido.

## Qué esperar
- Confirmación de recibido en un máximo de 3 días hábiles.
- Evaluación inicial en un máximo de 10 días hábiles.
- Aviso cuando la corrección esté disponible y crédito a quien reportó, si lo desea.

## Prácticas del proyecto
- Dependencias con versiones fijadas (`requirements.lock` y `package-lock.json`) y auditadas con `pip-audit` y `npm audit`.
- Inventario de componentes (SBOM) en formato CycloneDX en `6_Prototipo_completo/tigo-predice/sbom/`.
- Análisis estático con reglas de seguridad (ruff, reglas S y BLE) y pruebas automáticas de ataque.
- Detalle en `6_Prototipo_completo/tigo-predice/docs/seguridad_y_privacidad.md` y `docs/estandares_y_calidad.md`.
