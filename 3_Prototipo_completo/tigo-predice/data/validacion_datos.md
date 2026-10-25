# Validación de datos sintéticos

- Clientes: 20,000 | Celdas: 202 | Registros de red: 18,180 | Llamadas: 36,971
- Mezcla de segmentos: {'prepago': 0.598, 'pospago': 0.299, 'hogar': 0.103}
- Tasa de llamada en 7 días: 9.2%
- Churn 30 días por segmento: {'hogar': 0.023, 'pospago': 0.022, 'prepago': 0.05}
- Clientes por ciudad: {'Tegucigalpa': 7836, 'San Pedro Sula': 4923, 'Danlí': 1221, 'El Progreso': 1220, 'La Ceiba': 1110, 'Choluteca': 966, 'Comayagua': 957, 'Juticalpa': 777, 'Siguatepeque': 613, 'Santa Rosa de Copán': 377}
- Fallas masivas: 22 (activas: 1)
- Eventos cliente × falla: 7,403 | llamó en 72 h: 33.6% | llamadas por 1,000 afectados: 475
- Tasa 72 h por segmento: {'hogar': 0.596, 'pospago': 0.367, 'prepago': 0.278}
- Tasa 72 h por zona: {np.str_('periurbana'): 0.328, np.str_('rural'): 0.335, np.str_('urbana'): 0.341}
- Correlación caidas_30d vs churn: +0.195
- Correlación llamadas_sin_resolver_30d vs churn: +0.223
- Correlación dias_atraso vs churn: +0.063
- Correlación tendencia_uso vs churn: -0.081