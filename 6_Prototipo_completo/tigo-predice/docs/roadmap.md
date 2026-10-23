# Roadmap

## Fase 1 · Piloto Hogar + Móvil (12 semanas, San Pedro Sula)

| Semanas | Fase | Entregable |
|---|---|---|
| 0–2 | Preparación | CSV del ACS/OLT, NOC, CRM, call center y campo. **Análisis retrospectivo** (¿la IA le gana a la regla con 3 meses reales?). Mapeo cliente ↔ nodo/sitio. Plantillas aprobadas. Evaluación de impacto, SSO y pentest |
| 3–10 | Piloto en vivo | Hogar: la IA marca el 2 % semanal y soporte N2 corrige a distancia o agenda la visita con diagnóstico. Móvil: aviso y cierre en fallas masivas. 15 % de control en ambos; tablero diario |
| 11–12 | Análisis y decisión | Efecto con IC 95 %, costo real por visita y por llamada evitada, y **GO / NO-GO por frente** al comité |

**Criterios:**
- **Hogar:** GO si las visitas en hogares marcados bajan ≥ 15 %, de forma significativa (p < 0.05) y con opt-out < 2 %. Si la IA no supera a la regla de umbrales por 1.3×, se usa la regla.
- **Móvil:** GO si las llamadas en 72 h bajan ≥ 10 %, de forma significativa y con opt-out < 2 %.

**Inversión:** L 770 mil (rango L 480 mil a L 1.2 M). Ver [impacto.md](impacto.md).

## Fase 2 · Churn de prepago y retención (solo si la Fase 1 da GO)
- Los modelos de 7 y 30 días que ya existen en el prototipo, reentrenados con **validación temporal**.
- Ofertas de retención **medidas contra un grupo control**: solo se acredita el efecto incremental, con margen de contribución.
- Requiere su propia evaluación de impacto en privacidad (uso comercial de datos).

## Fase 3 · Escalamiento nacional
- Integración en tiempo real con el ACS, OSS, CRM y WhatsApp, con inversión única de unos L 1.7 M para ambos frentes.
- Acciones remotas automáticas dentro de la lista cerrada, con reversión.
- Holdout permanente del 5 % para seguir midiendo el efecto.
- Replicable en otras operaciones de Millicom/Tigo.
