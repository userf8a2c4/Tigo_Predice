"""Telemetría de módems del frente Hogar: simulación, variables para la IA y regla de umbrales.

Señales diarias por hogar (lo que reporta un ACS TR-069 o el gestor de OLT/CMTS):
  margen   margen de señal en dB sobre el umbral de servicio (fibra: potencia óptica Rx;
           HFC: SNR de bajada). Normal ≈ 8 dB; bajo 3 dB empiezan los cortes.
  fec      errores de transmisión no corregibles por hora
  reinicios, desconexiones (micro-cortes del enlace), latencia (ms),
  retrans  % de retransmisiones WiFi (interferencia / congestión), dispositivos WiFi, uso (GB/día)

Lo usan el generador de datos, el entrenamiento, la simulación del piloto y la demo «Hogar en vivo».
Solo usa información disponible al día de corte (sin fuga de datos).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SENALES = ("margen", "fec", "reinicios", "desconexiones", "latencia", "retrans", "dispositivos", "uso")

# Tipos de problema (episodios latentes). remoto = se corrige a distancia sin técnico.
TIPOS = {
    "wifi": {"nombre": "Interferencia o congestión WiFi", "remoto": True, "cierre": "Configuración WiFi"},
    "firmware": {"nombre": "Cuelgues del módem por firmware", "remoto": True, "cierre": "Firmware / reinicio"},
    "senal": {
        "nombre": "Degradación de señal (conector, acometida, cable)",
        "remoto": False,
        "cierre": "Conector / acometida",
    },
    "equipo": {"nombre": "Módem dañado", "remoto": False, "cierre": "Cambio de equipo"},
}

# Regla de umbrales: lo que ya puede alarmar hoy un ACS o el NOC, sin IA.
UMBRALES_REGLA = {"margen_min_7d": 3.0, "reinicios_7d": 5, "desconexiones_7d": 15, "retrans_7d": 25.0}

VARIABLES_HOGAR = [
    "margen_ult",
    "margen_min_7d",
    "pendiente_margen_14d",
    "fec_7d",
    "reinicios_7d",
    "cambio_reinicios",
    "desconexiones_7d",
    "desconexiones_nodo_7d",
    "latencia_7d",
    "pendiente_latencia_14d",
    "retrans_7d",
    "pendiente_retrans_14d",
    "dispositivos_7d",
    "uso_relativo",
    "es_fibra",
    "edad_modem_meses",
    "modem_antiguo",
    "firmware_desactualizado",
    "solo_2_4ghz",
    "antiguedad_meses",
    "plan_mbps",
    "zona_periurbana",
    "llamadas_tecnicas_30d",
    "visitas_90d",
]

NOMBRES_HOGAR = {
    "margen_ult": "Margen de señal hoy",
    "margen_min_7d": "Margen de señal mínimo (7 d)",
    "pendiente_margen_14d": "Tendencia de la señal (14 d)",
    "fec_7d": "Errores de transmisión (7 d)",
    "reinicios_7d": "Reinicios del módem (7 d)",
    "cambio_reinicios": "Aumento de reinicios vs. semana anterior",
    "desconexiones_7d": "Micro-cortes (7 d)",
    "desconexiones_nodo_7d": "Micro-cortes en el nodo (vecinos)",
    "latencia_7d": "Latencia (7 d)",
    "pendiente_latencia_14d": "Tendencia de la latencia (14 d)",
    "retrans_7d": "Retransmisiones WiFi (7 d)",
    "pendiente_retrans_14d": "Tendencia del WiFi (14 d)",
    "dispositivos_7d": "Dispositivos conectados",
    "uso_relativo": "Uso esta semana vs. su promedio",
    "es_fibra": "Tecnología fibra",
    "edad_modem_meses": "Edad del módem",
    "modem_antiguo": "Modelo de módem antiguo",
    "firmware_desactualizado": "Firmware desactualizado",
    "solo_2_4ghz": "WiFi solo 2.4 GHz",
    "antiguedad_meses": "Antigüedad del cliente",
    "plan_mbps": "Velocidad del plan",
    "zona_periurbana": "Zona periurbana",
    "llamadas_tecnicas_30d": "Llamadas técnicas (30 d)",
    "visitas_90d": "Visitas técnicas (90 d)",
}

# Frase para el diagnóstico (cuando la variable EMPUJA el riesgo hacia arriba)
EXPLICACIONES = {
    "margen_ult": "la señal está cerca del límite",
    "margen_min_7d": "la señal tocó niveles bajos esta semana",
    "pendiente_margen_14d": "la señal viene cayendo día a día",
    "fec_7d": "aumentan los errores de transmisión",
    "reinicios_7d": "el módem se reinicia solo",
    "cambio_reinicios": "los reinicios se aceleraron esta semana",
    "desconexiones_7d": "hay micro-cortes frecuentes",
    "desconexiones_nodo_7d": "los vecinos del nodo también tienen cortes",
    "latencia_7d": "la conexión está lenta",
    "pendiente_latencia_14d": "la lentitud va en aumento",
    "retrans_7d": "el WiFi tiene mucha interferencia",
    "pendiente_retrans_14d": "el WiFi empeora día a día",
    "dispositivos_7d": "hay muchos dispositivos conectados",
    "uso_relativo": "el cliente usa menos su internet de lo normal",
    "es_fibra": "tecnología del servicio",
    "edad_modem_meses": "el módem tiene varios años",
    "modem_antiguo": "es un modelo de módem antiguo",
    "firmware_desactualizado": "el firmware está desactualizado",
    "solo_2_4ghz": "el módem solo tiene WiFi 2.4 GHz",
    "antiguedad_meses": "antigüedad del cliente",
    "plan_mbps": "velocidad del plan",
    "zona_periurbana": "zona periurbana",
    "llamadas_tecnicas_30d": "ya llamó por problemas técnicos este mes",
    "visitas_90d": "tuvo visitas técnicas recientes",
}


# ---------------------------------------------------------------------------- simulación
def base(rng: np.random.Generator, hogares: pd.DataFrame, dias: int) -> dict[str, np.ndarray]:
    """Señales "sanas" de cada hogar (n × días) antes de agregar problemas."""
    n = len(hogares)
    fibra = hogares["es_fibra"].to_numpy()[:, None]
    disp_base = hogares["dispositivos_base"].to_numpy()[:, None].astype(float)
    margen0 = rng.normal(8.0, 1.0, (n, 1))
    return {
        "margen": margen0 + rng.normal(0, 0.35, (n, dias)),
        "fec": rng.lognormal(np.log(2.0), 0.5, (n, dias)),
        "reinicios": rng.poisson(0.03 + 0.04 * hogares["modem_antiguo"].to_numpy()[:, None], (n, dias)).astype(float),
        "desconexiones": rng.poisson(0.25, (n, dias)).astype(float),
        "latencia": np.where(fibra == 1, 18.0, 30.0) + rng.normal(0, 4, (n, dias)).clip(-8, None),
        "retrans": (3.0 + 2.5 * disp_base / 8 + 3.0 * hogares["solo_2_4ghz"].to_numpy()[:, None])
        + rng.normal(0, 1.6, (n, dias)),
        "dispositivos": rng.poisson(np.broadcast_to(disp_base, (n, dias))).astype(float),
        "uso": hogares["uso_base"].to_numpy()[:, None] * rng.lognormal(0, 0.25, (n, dias)),
    }


def severidad(dias: int, inicio: int, rampa: int, fin: int) -> np.ndarray:
    """0 antes del inicio, sube linealmente durante la rampa hasta 1 y vuelve a 0 al terminar."""
    t = np.arange(dias)
    s = np.clip((t - inicio + 1) / max(rampa, 1), 0, 1)
    s[(t < inicio) | (t >= fin)] = 0.0
    return s


def aplicar(senales: dict[str, np.ndarray], i: int, tipo: str, sev: np.ndarray, rng: np.random.Generator) -> None:
    """Agrega a la fila i el efecto de un problema de tipo `tipo` con severidad diaria `sev`."""
    d = len(sev)
    if tipo == "wifi":
        senales["retrans"][i] += 26 * sev + rng.normal(0, 2.5, d) * (sev > 0)
        senales["latencia"][i] += 32 * sev
        senales["desconexiones"][i] += rng.poisson(0.6 * sev)
        senales["uso"][i] *= 1 - 0.35 * sev
    elif tipo == "firmware":
        senales["reinicios"][i] += rng.poisson(2.2 * sev**1.3)
        senales["desconexiones"][i] += rng.poisson(1.2 * sev)
        senales["latencia"][i] += 10 * sev
        senales["uso"][i] *= 1 - 0.25 * sev
    elif tipo == "senal":
        senales["margen"][i] -= 7.2 * sev
        senales["fec"][i] += 45 * sev**2 * rng.lognormal(0, 0.3, d)
        senales["desconexiones"][i] += rng.poisson(5.5 * sev**2)
        senales["latencia"][i] += 8 * sev**2
        senales["uso"][i] *= 1 - 0.3 * sev**2
    elif tipo == "equipo":
        senales["reinicios"][i] += rng.poisson(1.0 * sev)
        senales["latencia"][i] += 22 * sev
        senales["retrans"][i] += 9 * sev
        senales["desconexiones"][i] += rng.poisson(1.8 * sev)
        senales["uso"][i] *= 1 - 0.3 * sev
    else:
        raise ValueError(tipo)


def falla_nodo(senales: dict[str, np.ndarray], filas: np.ndarray, dia: int, horas: float, rng) -> None:
    """Falla masiva del nodo / OLT: todos los hogares del nodo se cortan el mismo día."""
    senales["desconexiones"][filas, dia] += rng.poisson(4 + horas, len(filas))
    senales["latencia"][filas, dia] *= 1.8
    senales["uso"][filas, dia] *= max(0.1, 1 - horas / 24)


# ---------------------------------------------------------------------------- variables
def _pendiente(m: np.ndarray) -> np.ndarray:
    """Pendiente por fila (unidades por día) de una ventana n × w."""
    x = np.arange(m.shape[1], dtype=float)
    x -= x.mean()
    return ((m - m.mean(axis=1, keepdims=True)) * x).sum(axis=1) / (x**2).sum()


def variables(
    senales: dict[str, np.ndarray],
    hogares: pd.DataFrame,
    llamadas: np.ndarray,
    visitas: np.ndarray,
    dia: int,
    vecinos_fijo: float | None = None,
) -> pd.DataFrame:
    """Variables de todos los hogares al cierre del día `dia` (incluido). Sin mirar el futuro.

    `vecinos_fijo` reemplaza los micro-cortes promedio del nodo (para calificar un hogar suelto en la demo).
    """
    a = max(0, dia - 6)
    a14 = max(0, dia - 13)
    a28 = max(0, dia - 27)
    s = {k: v[:, : dia + 1] for k, v in senales.items()}
    nodo = pd.factorize(hogares["nodo_id"])[0]
    desc7 = s["desconexiones"][:, a:].sum(axis=1)
    suma_nodo = np.bincount(nodo, weights=desc7)
    cuenta_nodo = np.bincount(nodo)
    vecinos = (suma_nodo[nodo] - desc7) / np.maximum(cuenta_nodo[nodo] - 1, 1)
    if vecinos_fijo is not None:
        vecinos = np.full(len(desc7), float(vecinos_fijo))
    reinicios_prev = s["reinicios"][:, max(0, dia - 13) : a].sum(axis=1)
    reinicios7 = s["reinicios"][:, a:].sum(axis=1)
    X = pd.DataFrame(
        {
            "margen_ult": s["margen"][:, max(0, dia - 1) :].mean(axis=1),
            "margen_min_7d": s["margen"][:, a:].min(axis=1),
            "pendiente_margen_14d": _pendiente(s["margen"][:, a14:]),
            "fec_7d": s["fec"][:, a:].mean(axis=1),
            "reinicios_7d": reinicios7,
            "cambio_reinicios": reinicios7 - reinicios_prev,
            "desconexiones_7d": desc7,
            "desconexiones_nodo_7d": vecinos,
            "latencia_7d": s["latencia"][:, a:].mean(axis=1),
            "pendiente_latencia_14d": _pendiente(s["latencia"][:, a14:]),
            "retrans_7d": s["retrans"][:, a:].mean(axis=1),
            "pendiente_retrans_14d": _pendiente(s["retrans"][:, a14:]),
            "dispositivos_7d": s["dispositivos"][:, a:].mean(axis=1),
            "uso_relativo": s["uso"][:, a:].mean(axis=1) / np.maximum(s["uso"][:, a28:].mean(axis=1), 0.01),
            "es_fibra": hogares["es_fibra"].to_numpy(),
            "edad_modem_meses": hogares["edad_modem_meses"].to_numpy(),
            "modem_antiguo": hogares["modem_antiguo"].to_numpy(),
            "firmware_desactualizado": hogares["firmware_desactualizado"].to_numpy(),
            "solo_2_4ghz": hogares["solo_2_4ghz"].to_numpy(),
            "antiguedad_meses": hogares["antiguedad_meses"].to_numpy(),
            "plan_mbps": hogares["plan_mbps"].to_numpy(),
            "zona_periurbana": (hogares["zona"] == "periurbana").astype(int).to_numpy(),
            "llamadas_tecnicas_30d": llamadas[:, max(0, dia - 29) : dia + 1].sum(axis=1),
            "visitas_90d": visitas[:, max(0, dia - 89) : dia + 1].sum(axis=1),
        },
        index=hogares["hogar_id"].to_numpy(),
    )
    return X[VARIABLES_HOGAR]


def regla(X: pd.DataFrame) -> np.ndarray:
    """Puntaje de la regla de umbrales: nº de alarmas encendidas + cuánto se pasó de cada umbral."""
    u = UMBRALES_REGLA
    alarmas = np.column_stack(
        [
            np.clip((u["margen_min_7d"] - X["margen_min_7d"]) / 3, 0, None),
            np.clip(X["reinicios_7d"] / u["reinicios_7d"] - 1, 0, None),
            np.clip(X["desconexiones_7d"] / u["desconexiones_7d"] - 1, 0, None),
            np.clip(X["retrans_7d"] / u["retrans_7d"] - 1, 0, None),
        ]
    )
    encendidas = np.column_stack(
        [
            X["margen_min_7d"] < u["margen_min_7d"],
            X["reinicios_7d"] >= u["reinicios_7d"],
            X["desconexiones_7d"] >= u["desconexiones_7d"],
            X["retrans_7d"] > u["retrans_7d"],
        ]
    )
    return encendidas.sum(axis=1) + np.minimum(alarmas.sum(axis=1), 0.99)


def alarma_regla(X: pd.DataFrame) -> np.ndarray:
    """True si la regla de umbrales dispara al menos una alarma."""
    return regla(X) >= 1


def top_k(score: np.ndarray, pct: float) -> np.ndarray:
    k = max(1, int(round(len(score) * pct)))
    marca = np.zeros(len(score), dtype=bool)
    marca[np.argsort(-np.asarray(score), kind="stable")[:k]] = True
    return marca
