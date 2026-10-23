# Reporte del modelo — Tigo Predice v03

> ⚠️ **Datos simulados.** Las métricas muestran cómo se evaluará el modelo; con 3 meses de telemetría real
> de Tigo se recalculan antes del piloto (análisis retrospectivo).

## Frente Hogar · ¿llamará por un problema técnico o necesitará visita en los próximos 7 días?

**Validación:** Temporal: entrena con 6 semanas (días 19–54, 72,000 hogar-semana) y prueba con las 4 siguientes (días 61–82, 48,000 hogar-semana).
Presupuesto: cada semana se actúa sobre el **2%** de hogares con más riesgo. En prueba: 1.5% de hogares llama o necesita visita en 7 días · 9 visitas por 1,000 hogares · 34% de las visitas son evitables.

### IA vs. regla de umbrales vs. azar (mismo presupuesto semanal)

| Estrategia | AUC | Brier (↓ mejor) | Precisión | Captura de eventos | Captura de visitas evitables | Visitas por 100 marcados |
|---|---|---|---|---|---|---|
| regresión logística | 0.800 | 0.010 | 0.425 | 0.556 | 0.457 | 35 |
| LightGBM | 0.810 | 0.009 | 0.454 | 0.594 | 0.503 | 36 |
| LightGBM calibrado | 0.813 | 0.009 | 0.457 | 0.598 | 0.517 | 37 |
| regla de umbrales | 0.669 | — | 0.267 | 0.349 | 0.258 | 24 |
| azar | 0.500 | — | 0.020 | 0.026 | 0.033 | 1.40 |

Regla de umbrales: margen de señal < 3 dB · ≥ 5 reinicios en 7 días · ≥ 15 micro-cortes en 7 días · retransmisiones WiFi > 25 %.

**Lectura honesta:**
- Con el mismo presupuesto, la IA anticipa **52%** de las visitas evitables y la regla **26%**: **2.0×**.
- **51%** de las visitas que la IA anticipó todavía no tenían ninguna alarma de umbral: la IA ve tendencias (señal que baja, WiFi que empeora, vecinos con cortes).
- Una regresión logística sencilla rinde cerca de LightGBM: se puede empezar simple y auditable.
- Criterio del piloto: si con datos reales la IA no supera a la regla por 1.3×, se usa la regla.

### Calibración (LightGBM calibrado, isotónica)

| Probabilidad media | Tasa real | n |
|---|---|---|
| 0.004 | 0.007 | 4,800 |
| 0.005 | 0.006 | 4,800 |
| 0.005 | 0.004 | 4,800 |
| 0.005 | 0.005 | 4,800 |
| 0.006 | 0.005 | 4,800 |
| 0.006 | 0.007 | 4,800 |
| 0.007 | 0.006 | 4,800 |
| 0.008 | 0.006 | 4,800 |
| 0.010 | 0.006 | 4,800 |
| 0.102 | 0.101 | 4,800 |

### Sesgo: ¿se descuida a algún grupo?

| Tecnología | n | Tasa real | Prob. media | % marcado | Captura de evitables | AUC |
|---|---|---|---|---|---|---|
| HFC | 18,992 | 0.017 | 0.017 | 0.024 | 0.533 | 0.814 |
| fibra | 29,008 | 0.014 | 0.015 | 0.018 | 0.505 | 0.811 |

| Zona | n | Tasa real | Prob. media | % marcado | Captura de evitables | AUC |
|---|---|---|---|---|---|---|
| periurbana | 16,356 | 0.016 | 0.018 | 0.022 | 0.511 | 0.850 |
| urbana | 31,644 | 0.015 | 0.015 | 0.019 | 0.519 | 0.794 |

### Variables más influyentes (ganancia LightGBM)

| Variable | Importancia |
|---|---|
| Tendencia de la señal (14 d) | 0.215 |
| Micro-cortes (7 d) | 0.178 |
| Tendencia de la latencia (14 d) | 0.169 |
| Errores de transmisión (7 d) | 0.102 |
| Tendencia del WiFi (14 d) | 0.085 |
| Margen de señal hoy | 0.056 |
| Reinicios del módem (7 d) | 0.052 |
| Visitas técnicas (90 d) | 0.033 |
| Micro-cortes en el nodo (vecinos) | 0.031 |
| Latencia (7 d) | 0.018 |

---

## Frente Móvil · Fallas masivas: ¿llamará en las 72 h posteriores a la falla?

**Validación:** Temporal: entrena con fallas de los días 0–59 (16 fallas, 5,619 afectados) y prueba con las de los días 60–89 (5 fallas, 1,784 afectados).
Tasa base en prueba: **37%** de afectados llama · **522 llamadas por cada 1,000 afectados**.

### Modelo vs. regla operativa vs. azar (fallas de prueba)

| Estrategia de orden | AUC | Brier (↓ mejor) | Precisión top 10 % | Recall top 10 % | Llamadas capturadas por 100 contactos (top 20%) |
|---|---|---|---|---|---|
| regresión logística | 0.705 | 0.223 | 0.680 | 0.183 | 93 |
| LightGBM | 0.712 | 0.213 | 0.770 | 0.207 | 92 |
| LightGBM calibrado | 0.703 | 0.208 | 0.753 | 0.202 | 92 |
| regla operativa | 0.608 | — | 0.624 | 0.167 | 75 |
| azar | 0.500 | — | — | — | 50 |

**Lectura honesta:**
- El modelo ordena mejor que la regla operativa y mucho mejor que el azar, pero la mejora sobre una regresión logística simple es pequeña: un modelo sencillo es suficiente para empezar.
- Para el **aviso por WhatsApp** (barato) la mejor estrategia es **avisar a todos los afectados**: no hace falta un modelo para eso.
- El modelo aporta valor para **priorizar acciones caras** (compensaciones, llamadas salientes) cuando el presupuesto no alcanza para todos.

### Costo-efectividad por estrategia (valores base de la configuración)

| Estrategia | Contactos | Costo (L) | Llamadas evitadas / capturadas | Llamadas por 100 contactos | Costo por llamada (L) |
|---|---|---|---|---|---|
| Hoy: no avisar | 0 | 0 | 0 | — | — |
| Avisar por WhatsApp a TODOS los afectados (regla simple) | 1,784 | 940 | 158 | 52 | 5.93 |
| Compensar al 20 % elegido por azar | 357 | 5,712 | 179 | 50 | 32 |
| Compensar al 20 % elegido por la regla (hogar primero) | 357 | 5,712 | 269 | 75 | 21 |
| Compensar al 20 % elegido por el modelo | 357 | 5,712 | 328 | 92 | 17 |

### Calibración (LightGBM calibrado, isotónica)

| Probabilidad media predicha | Tasa real | Afectados |
|---|---|---|
| 0.267 | 0.196 | 179 |
| 0.298 | 0.201 | 179 |
| 0.315 | 0.268 | 179 |
| 0.333 | 0.218 | 179 |
| 0.352 | 0.264 | 178 |
| 0.367 | 0.360 | 178 |
| 0.396 | 0.365 | 178 |
| 0.444 | 0.539 | 178 |
| 0.503 | 0.562 | 178 |
| 0.655 | 0.747 | 178 |

### Sesgo: % priorizado vs. tasa real

**Por zona:**

| Zona | Afectados | Tasa real | Prob. media | % priorizado | AUC |
|---|---|---|---|---|---|
| periurbana | 881 | 0.373 | 0.387 | 0.166 | 0.686 |
| rural | 256 | 0.426 | 0.418 | 0.246 | 0.662 |
| urbana | 647 | 0.348 | 0.391 | 0.229 | 0.737 |

**Por segmento:**

| Segmento | Afectados | Tasa real | Prob. media | % priorizado | AUC |
|---|---|---|---|---|---|
| hogar | 190 | 0.632 | 0.554 | 0.668 | 0.734 |
| pospago | 526 | 0.399 | 0.409 | 0.224 | 0.689 |
| prepago | 1,068 | 0.312 | 0.356 | 0.105 | 0.655 |

### Variables más influyentes (ganancia LightGBM)

| Variable | Peso relativo |
|---|---|
| Llamadas por red (90 d) | 0.148 |
| ARPU | 0.130 |
| Es cliente hogar | 0.121 |
| Antigüedad | 0.111 |
| Hora de inicio | 0.086 |
| Llamadas sin resolver (30 d) | 0.079 |
| Es prepago | 0.044 |
| Hora estimada de solución | 0.043 |
| Caídas en su celda (30 d) | 0.041 |
| Última calificación | 0.041 |

---
## Fase 2 (visión, NO entra al caso base) · Modelos de 7 y 30 días

**Versión:** `v20261012` · **Fecha de corte:** 2026-10-12 · **Clientes:** 20,000 · **Variables:** 29

> Validación con partición aleatoria y predicciones fuera de muestra (5 particiones). En Fase 2 se
> pasará a validación temporal como la del modelo de 72 h.

### Resumen Fase 2

| Modelo | AUC baseline (reg. logística) | AUC LightGBM | Tasa base | Precisión top 10 % | Recall top 10 % | Lift decil 1 |
|---|---|---|---|---|---|---|
| Fase 2 · Riesgo de incidencia general (llamará en 7 días) | 0.800 | 0.829 | 0.092 | 0.500 | 0.541 | 5.41 |
| Fase 2 · Riesgo de churn (abandono en 30 días) | 0.844 | 0.866 | 0.039 | 0.220 | 0.561 | 5.61 |

**Cómo leerlo:** si contactamos solo al 10 % de clientes con mayor riesgo, encontramos varias veces más casos reales que contactando al azar (lift).

## Fase 2 · Riesgo de incidencia general (llamará en 7 días)

_Probabilidad de que llame o reclame en los próximos 7 días_

### Matriz de confusión (LightGBM, umbral = top 10 % de riesgo)

| | Predicho: no | Predicho: sí |
|---|---|---|
| **Real: no** | 4,288 | 250 |
| **Real: sí** | 212 | 250 |

### Curva de lift por decil

| Decil | Tasa real | Lift | % capturado acumulado |
|---|---|---|---|
| 1 | 0.500 | 5.41 | 0.541 |
| 2 | 0.126 | 1.36 | 0.677 |
| 3 | 0.072 | 0.780 | 0.755 |
| 4 | 0.044 | 0.480 | 0.803 |
| 5 | 0.048 | 0.520 | 0.855 |
| 6 | 0.040 | 0.430 | 0.898 |
| 7 | 0.034 | 0.370 | 0.935 |
| 8 | 0.026 | 0.280 | 0.963 |
| 9 | 0.012 | 0.130 | 0.976 |
| 10 | 0.022 | 0.240 | 1.00 |

### Variables más influyentes (SHAP promedio)

| Variable | Grupo | Impacto |
|---|---|---|
| caidas_7d | Red | 0.293 |
| velocidad_pct_plan_7d | Red | 0.290 |
| llamadas_sin_resolver_30d | Atención | 0.206 |
| reclamos_cobro_90d | Facturación | 0.107 |
| horas_resolucion_prom | Atención | 0.068 |
| caidas_30d | Red | 0.058 |
| nps_ultimo | Satisfacción | 0.055 |
| llamadas_30d | Atención | 0.054 |
| tickets_abiertos | Atención | 0.053 |
| datos_gb_30d | Uso | 0.052 |
| latencia_ms_7d | Red | 0.051 |
| brecha_velocidad_celda | Equipo | 0.044 |

### Revisión de sesgo por zona y segmento

Se compara el % de clientes marcados (top 10 %) con la tasa real del grupo. Un grupo marcado muy por encima de su riesgo real indicaría sesgo.

**Por ciudad:**

| Ciudad | Clientes (prueba) | Tasa real | Prob. media | % marcado | AUC |
|---|---|---|---|---|---|
| Choluteca | 242 | 0.087 | 0.083 | 0.070 | 0.787 |
| Comayagua | 230 | 0.096 | 0.080 | 0.078 | 0.776 |
| Danlí | 324 | 0.096 | 0.091 | 0.108 | 0.870 |
| El Progreso | 311 | 0.035 | 0.058 | 0.035 | 0.708 |
| Juticalpa | 220 | 0.054 | 0.056 | 0.050 | 0.691 |
| La Ceiba | 256 | 0.332 | 0.319 | 0.492 | 0.902 |
| San Pedro Sula | 1,189 | 0.091 | 0.097 | 0.112 | 0.821 |
| Santa Rosa de Copán | 101 | 0.129 | 0.144 | 0.208 | 0.908 |
| Siguatepeque | 158 | 0.076 | 0.091 | 0.089 | 0.737 |
| Tegucigalpa | 1,969 | 0.075 | 0.070 | 0.058 | 0.777 |

**Por segmento:**

| Segmento | Clientes (prueba) | Tasa real | Prob. media | % marcado | AUC |
|---|---|---|---|---|---|
| hogar | 509 | 0.120 | 0.111 | 0.124 | 0.853 |
| pospago | 1,504 | 0.098 | 0.098 | 0.100 | 0.816 |
| prepago | 2,987 | 0.085 | 0.086 | 0.096 | 0.829 |

## Fase 2 · Riesgo de churn (abandono en 30 días)

_Probabilidad de abandono/portabilidad en 30 días_

### Matriz de confusión (LightGBM, umbral = top 10 % de riesgo)

| | Predicho: no | Predicho: sí |
|---|---|---|
| **Real: no** | 4,414 | 390 |
| **Real: sí** | 86 | 110 |

### Curva de lift por decil

| Decil | Tasa real | Lift | % capturado acumulado |
|---|---|---|---|
| 1 | 0.220 | 5.61 | 0.561 |
| 2 | 0.074 | 1.89 | 0.750 |
| 3 | 0.036 | 0.920 | 0.842 |
| 4 | 0.026 | 0.660 | 0.908 |
| 5 | 0.008 | 0.200 | 0.929 |
| 6 | 0.010 | 0.260 | 0.954 |
| 7 | 0.010 | 0.260 | 0.980 |
| 8 | 0.006 | 0.150 | 0.995 |
| 9 | 0.002 | 0.050 | 1.00 |
| 10 | 0 | 0 | 1.00 |

### Variables más influyentes (SHAP promedio)

| Variable | Grupo | Impacto |
|---|---|---|
| llamadas_sin_resolver_30d | Atención | 0.328 |
| tendencia_uso | Uso | 0.262 |
| caidas_30d | Red | 0.203 |
| antiguedad_meses | Perfil | 0.191 |
| dias_atraso | Facturación | 0.158 |
| arpu | Perfil | 0.155 |
| nps_ultimo | Satisfacción | 0.148 |
| datos_gb_30d | Uso | 0.139 |
| dias_sin_recarga | Uso | 0.138 |
| min_sin_servicio_30d | Red | 0.134 |
| llamadas_red_30d | Atención | 0.065 |
| recargas_30d | Uso | 0.059 |

### Revisión de sesgo por zona y segmento

Se compara el % de clientes marcados (top 10 %) con la tasa real del grupo. Un grupo marcado muy por encima de su riesgo real indicaría sesgo.

**Por ciudad:**

| Ciudad | Clientes (prueba) | Tasa real | Prob. media | % marcado | AUC |
|---|---|---|---|---|---|
| Choluteca | 230 | 0.035 | 0.037 | 0.100 | 0.794 |
| Comayagua | 234 | 0.021 | 0.034 | 0.073 | 0.911 |
| Danlí | 296 | 0.041 | 0.035 | 0.078 | 0.849 |
| El Progreso | 320 | 0.019 | 0.025 | 0.056 | 0.884 |
| Juticalpa | 189 | 0.026 | 0.016 | 0.016 | 0.761 |
| La Ceiba | 277 | 0.087 | 0.080 | 0.256 | 0.893 |
| San Pedro Sula | 1,263 | 0.048 | 0.054 | 0.150 | 0.854 |
| Santa Rosa de Copán | 105 | 0.057 | 0.050 | 0.143 | 0.901 |
| Siguatepeque | 164 | 0.049 | 0.037 | 0.079 | 0.878 |
| Tegucigalpa | 1,922 | 0.032 | 0.031 | 0.067 | 0.867 |

**Por segmento:**

| Segmento | Clientes (prueba) | Tasa real | Prob. media | % marcado | AUC |
|---|---|---|---|---|---|
| hogar | 536 | 0.028 | 0.023 | 0.060 | 0.917 |
| pospago | 1,511 | 0.017 | 0.025 | 0.058 | 0.875 |
| prepago | 2,953 | 0.052 | 0.051 | 0.129 | 0.843 |

### Metodología (Fase 2)

- Partición estratificada 75 % entrenamiento / 25 % prueba (semilla fija).
- Baseline: regresión logística con imputación y estandarización.
- Modelo principal: LightGBM (árboles de gradiente) regularizado.
- Puntajes del tablero: predicciones fuera de muestra con validación cruzada de 5 particiones (ningún cliente se califica con un modelo que lo vio).
- Explicaciones: valores SHAP por cliente traducidos a lenguaje natural (3 factores principales).
- Reproducible: `tareas.ps1 datos` → `tareas.ps1 entrenar` → `tareas.ps1 evaluar`.
