# Datos a pedir a Tigo (los que convierten el caso en definitivo)

Lista corta y priorizada. Los **cuatro primeros** se ingresan en **Pon tus números** de la app y el caso de negocio deja de ser un supuesto.

| # | Dato | Para qué | Quién lo tiene |
|---|---|---|---|
| 1 | **Visitas técnicas de Hogar al mes** (nacional y San Pedro Sula, últimos 6 meses), **con código de cierre** | Volumen y % de visitas evitables (WiFi, firmware, «sin falla encontrada») | Operaciones de campo |
| 2 | **Costo total por visita técnica** | Valor de cada visita evitada | Finanzas / operaciones |
| 3 | **Llamadas al mes por fallas masivas de red** | Volumen del frente Móvil | Call center / IVR (motivo de llamada) |
| 4 | **Costo total por llamada atendida** | Valor de cada llamada evitada | Finanzas / CX |
| 5 | **3 meses de telemetría diaria de módems** de San Pedro Sula: señal, errores, reinicios, latencia y WiFi | **Análisis retrospectivo:** ¿la IA le gana a la regla de umbrales con datos reales? | Ingeniería de acceso (ACS / gestor de OLT y CMTS) |
| 6 | Hogares por nodo/OLT y por ciudad | Saber a quién afecta cada problema; tamaño del piloto | Inventario de red |
| 7 | Acciones remotas permitidas hoy (reinicio, canal WiFi, firmware) y quién las ejecuta | Qué se puede corregir a distancia | Soporte nivel 2 / ingeniería |
| 8 | Fallas masivas por mes en San Pedro Sula, con sitios, duración y si hubo hora estimada | Tamaño de muestra del frente Móvil | NOC / OSS |
| 9 | % de clientes con WhatsApp y consentimiento para mensajes de servicio | Tasa de entrega real | Canales digitales / CRM |
| 10 | Aviso de privacidad y contrato de servicio vigentes (gestión remota del equipo) | Cumplimiento (ver `seguridad_y_privacidad.md`) | Legal / Privacidad |
| 11 | Churn mensual de afectados vs. no afectados | Potencial de retención (Fase 2) | BI / Finanzas |

**Formato sugerido para empezar:**
- Exportaciones CSV diarias, sin integraciones.
- **Antes de compartir se seudonimizan:** el identificador del cliente se reemplaza por un hash con sal, y no se incluyen nombres, teléfonos ni direcciones.
- El análisis retrospectivo (dato 5) no necesita ningún dato personal.
