# PLAN — Tigo Predice (Tigo CX Month · Sharks)

**Fecha límite de envío:** antes del 23-oct-2026 · **Envío objetivo:** miércoles 21-oct

| Fase | Estado |
|---|---|
| 1. Estructura del repo, entorno, `PLAN.md` y `DECISIONES.md` | ✅ 13-oct |
| 2. Datos sintéticos + validación estadística | ✅ 13-oct |
| 3. Variables y modelo (baseline → LightGBM) + SHAP + reporte | ✅ 13-oct |
| 4. Backend: riesgo, acciones, mensajes, chat, API, demo SSE | ✅ 13-oct |
| 5. Frontend: dashboard, mapa, clientes, WhatsApp, ROI, modelo | ✅ 13-oct |
| 6. Modo demo guionizado (determinista, 3 corridas iguales) | ✅ 13-oct |
| 7. Tests (52 pytest + 4 vitest), lint, lanzador `iniciar_demo.bat`, README | ✅ 13-oct |
| 8. Documentos del pitch y carpeta `../entrega/` (Word, PDF, PowerPoint, correo) | ✅ 13-oct |
| 9. Rellenar nombres, ensayar, grabar el video de respaldo y ENVIAR (lo hace el usuario) | ⏳ hasta el 21-oct |

## Pendiente (solo el usuario puede hacerlo)
- [ ] Verificar la dirección de correo exacta en el afiche original.
- [ ] Rellenar `[Nombre] · [Área] · [Correo]` en la propuesta, el resumen y la presentación (marcados en amarillo).
- [ ] Si aparece el formato oficial, pasarle el texto de la propuesta.
- [ ] Opcional: conversar con 2 o 3 personas del call center o del NOC para conseguir cifras y frases reales.
- [ ] Ensayar el pitch 3 veces con cronómetro (`docs/pitch.md`).
- [ ] Grabar el video de respaldo de la demo (Win + Alt + R).
- [ ] Enviar el correo (`../entrega/correo.txt`).

## Métricas actuales del modelo (`reports/modelo.md`)
- Incidencia a 7 días: AUC 0.864 (baseline 0.843), precisión 53 % en el top 10 % y lift de 5.9.
- Churn a 30 días: AUC 0.877 (baseline 0.865) y lift de 6.0.
