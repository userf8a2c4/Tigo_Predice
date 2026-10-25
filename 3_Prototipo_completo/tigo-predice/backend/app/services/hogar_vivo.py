"""Escenario «Hogar en vivo» para la demo (~90 s).

Dos casos guionados con datos sintéticos y deterministas, calificados con el MODELO REAL día a día:
- remoto:  el WiFi se satura y el módem se cuelga (firmware). La IA lo marca días antes de la regla de
           umbrales y de que el cliente llame; se corrige a distancia: visita evitada.
- tecnico: la señal de fibra se degrada (conector). No se arregla a distancia, pero la IA lo detecta
           antes de que el cliente lo sufra: el técnico llega una sola vez y con el diagnóstico.

Para cada uno de los últimos 21 días devuelve la telemetría, el riesgo de la IA y la alarma de la regla,
en dos mundos: «sin Tigo Predice» (el problema sigue, el cliente llama y se manda un técnico) y
«con Tigo Predice» (se actúa el día que la IA lo marca). No modifica ningún estado.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from backend.app.privacidad import nombre_corto
from backend.app.services import bitacora, mensajes
from backend.app.services.roi import L, sig
from ml import telemetria
from ml.comun import supuesto
from ml.generar_hogar import UMBRAL_NOTA

DIAS = 90
VENTANA = 21  # días que muestra la demo
VECINOS_NORMAL = 1.9  # micro-cortes promedio del nodo en 7 días (mediana de los datos)
SEMILLA = 2026

CASOS = {
    "remoto": {
        "titulo": "Se corrige a distancia",
        "filtro": {"es_fibra": 1, "solo_2_4ghz": 1, "firmware_desactualizado": 1},
        "episodios": [("wifi", 73, 9), ("firmware", 75, 9)],
        "accion": "hogar_remoto",
        "dias_para_corregir": 0,
    },
    "tecnico": {
        "titulo": "Necesita técnico (llega con el diagnóstico)",
        "filtro": {"es_fibra": 1, "solo_2_4ghz": 0, "zona": "periurbana"},
        "episodios": [("senal", 71, 14)],
        "accion": "hogar_visita",
        "dias_para_corregir": 2,
    },
}


def _hogar(estado, caso: str) -> pd.Series:
    h = estado.hogares
    m = (
        (h["ciudad"] == estado.cfg["piloto"]["ciudad"])
        & (h["canal_preferido"] == "WhatsApp")
        & (h["acepta_mensajes"] == 1)
    )
    for k, v in CASOS[caso]["filtro"].items():
        m &= h[k] == v
    return h[m].sort_values("hogar_id").iloc[0]


def _mundo(hogar: pd.DataFrame, episodios: list[tuple[str, int, int]], fin: int | None) -> dict[str, np.ndarray]:
    """Telemetría de 90 días del hogar. `fin` = día en que se corrige el problema (None = nunca)."""
    rng = np.random.default_rng(SEMILLA)
    senales = telemetria.base(rng, hogar, DIAS)
    for tipo, inicio, rampa in episodios:
        sev = telemetria.severidad(DIAS, inicio, rampa, DIAS + 99 if fin is None else fin)
        telemetria.aplicar(senales, 0, tipo, sev, np.random.default_rng(SEMILLA + inicio))
    for k in senales:
        senales[k] = np.clip(senales[k], 0 if k != "margen" else -5, None)
    return senales


def _contrafactual(episodios: list[tuple[str, int, int]]) -> tuple[int, int]:
    """Sin aviso: el cliente llama cuando ya lo sufre y el técnico va 2 días después."""
    llamada = min(inicio + int(np.ceil(rampa * (UMBRAL_NOTA[tipo] + 0.3))) for tipo, inicio, rampa in episodios)
    return llamada, llamada + 2


def _calificar(estado, hogar: pd.DataFrame, senales: dict, llamadas: np.ndarray, visitas: np.ndarray) -> pd.DataFrame:
    filas = [
        telemetria.variables(senales, hogar, llamadas, visitas, d, vecinos_fijo=VECINOS_NORMAL)
        for d in range(DIAS - VENTANA, DIAS)
    ]
    X = pd.concat(filas, ignore_index=True)
    X["p"] = estado.modelo_hogar.predict_proba(X[telemetria.VARIABLES_HOGAR])[:, 1]
    X["regla"] = telemetria.alarma_regla(X)
    return X


def _legible(var: str, v: float, es_fibra: bool) -> str:
    if var in ("margen_ult", "margen_min_7d"):
        return f"{-27 + v:.1f} dBm" if es_fibra else f"SNR {30 + v:.1f} dB"
    if var == "pendiente_margen_14d":
        return f"{v:+.2f} dB por día"
    if var in ("retrans_7d",):
        return f"{v:.0f} %"
    if var == "pendiente_retrans_14d":
        return f"{v:+.1f} puntos por día"
    if var in ("reinicios_7d", "desconexiones_7d", "llamadas_tecnicas_30d", "visitas_90d", "cambio_reinicios"):
        return f"{v:.0f}"
    if var in ("latencia_7d",):
        return f"{v:.0f} ms"
    if var == "pendiente_latencia_14d":
        return f"{v:+.1f} ms por día"
    if var == "fec_7d":
        return f"{v:.0f} por hora"
    if var == "uso_relativo":
        return f"{v * 100:.0f} % de lo normal"
    if var == "edad_modem_meses":
        return f"{v / 12:.0f} años"
    if var in ("firmware_desactualizado", "solo_2_4ghz", "modem_antiguo", "es_fibra", "zona_periurbana"):
        return "sí" if v else "no"
    return f"{v:.1f}"


# Variables que solo explican si su valor apunta al problema (evita «tuvo visitas recientes: 0»)
_SOLO_SI_POSITIVO = {
    "reinicios_7d",
    "cambio_reinicios",
    "desconexiones_7d",
    "llamadas_tecnicas_30d",
    "visitas_90d",
    "firmware_desactualizado",
    "solo_2_4ghz",
    "modem_antiguo",
    "zona_periurbana",
    "pendiente_retrans_14d",
    "pendiente_latencia_14d",
}
_NO_EXPLICAN = {"es_fibra", "plan_mbps", "antiguedad_meses", "dispositivos_7d", "uso_relativo", "edad_modem_meses"}
REMOTAS = {
    "retrans_7d",
    "pendiente_retrans_14d",
    "reinicios_7d",
    "cambio_reinicios",
    "latencia_7d",
    "pendiente_latencia_14d",
    "firmware_desactualizado",
    "solo_2_4ghz",
}


def _tiene_sentido(var: str, v: float) -> bool:
    if var in _NO_EXPLICAN:
        return False
    if var in _SOLO_SI_POSITIVO:
        return v > 0
    if var == "pendiente_margen_14d":
        return v < 0
    return True


def explicar(explicador, X: pd.DataFrame, es_fibra: np.ndarray, n: int = 3) -> list[list[dict]]:
    """Contribuciones SHAP del modelo (LightGBM) al riesgo: por qué marcó a cada hogar."""
    valores = X[telemetria.VARIABLES_HOGAR].to_numpy(float)
    contrib = explicador.booster_.predict(valores, pred_contrib=True)[:, :-1]
    salida = []
    for fila, c, fib in zip(valores, contrib, es_fibra, strict=True):
        items = []
        for i in np.argsort(-c):
            var = telemetria.VARIABLES_HOGAR[i]
            if c[i] <= 0 or len(items) == n:
                break
            if _tiene_sentido(var, fila[i]):
                items.append(
                    {
                        "variable": var,
                        "texto": telemetria.EXPLICACIONES[var],
                        "valor": _legible(var, float(fila[i]), bool(fib)),
                        "contribucion": round(float(c[i]), 3),
                    }
                )
        salida.append(items)
    return salida


def accion_sugerida(explicacion: list[dict]) -> str:
    variables = [e["variable"] for e in explicacion]
    if variables and variables[0] == "desconexiones_nodo_7d":
        return "Revisar el nodo (posible falla masiva)"
    if variables and variables[0] in REMOTAS:
        return "Corrección remota (WiFi / firmware)"
    return "Visita con diagnóstico (señal)"


def lista_hoy(estado, n: int = 12) -> dict:
    """Lista de trabajo de hoy para soporte nivel 2: hogares de la ciudad piloto que la IA marcó."""
    h = estado.hoy_hogar
    ciudad = estado.cfg["piloto"]["ciudad"]
    sel = h[(h["ciudad"] == ciudad) & h["marcado"]].sort_values("p", ascending=False)
    top = sel.head(n)
    exp = explicar(estado.explicador_hogar, top, top["es_fibra"].to_numpy())
    return {
        "ciudad": ciudad,
        "fecha": estado.hoy.isoformat(),
        "hogares_ciudad": int((h["ciudad"] == ciudad).sum()),
        "marcados": int(len(sel)),
        "con_alarma_regla": int((sel["regla"] >= 1).sum()),
        "umbral_riesgo": round(float(estado.umbral_hogar), 4),
        "hogares": [
            {
                "hogar_id": r.hogar_id,
                "nombre": nombre_corto(r.nombre),
                "nodo_id": r.nodo_id,
                "tecnologia": "Fibra" if r.es_fibra else "HFC",
                "riesgo": round(float(r.p), 3),
                "alarma_regla": bool(r.regla >= 1),
                "motivos": e,
                "accion": accion_sugerida(e),
                "contacto": r.canal_preferido
                if r.acepta_mensajes
                else "Sin mensajes (opt-out): solo corrección remota",
            }
            for r, e in zip(top.itertuples(), exp, strict=True)
        ],
    }


def escenario(estado, caso: str = "remoto") -> dict:
    if caso not in CASOS:
        raise ValueError(f"Caso desconocido: {caso}")
    cfg, conf = estado.cfg, CASOS[caso]
    fila_h = _hogar(estado, caso)
    hogar = fila_h.to_frame().T.reset_index(drop=True)
    for c in (
        "es_fibra",
        "solo_2_4ghz",
        "firmware_desactualizado",
        "modem_antiguo",
        "edad_modem_meses",
        "antiguedad_meses",
        "plan_mbps",
        "dispositivos_base",
    ):
        hogar[c] = hogar[c].astype(int)
    hogar["uso_base"] = hogar["uso_base"].astype(float)
    es_fibra = bool(fila_h["es_fibra"])
    eps = conf["episodios"]
    umbral = estado.umbral_hogar
    d0 = DIAS - VENTANA

    # ---- mundo SIN Tigo Predice: el problema sigue, el cliente llama y se manda un técnico
    t_llamada, t_visita = _contrafactual(eps)
    sin = _mundo(hogar, eps, fin=t_visita)
    llam_sin, vis_sin = np.zeros((1, DIAS), int), np.zeros((1, DIAS), int)
    if t_llamada < DIAS:
        llam_sin[0, t_llamada] = 1
    if t_visita < DIAS:
        vis_sin[0, t_visita] = 1
    X_sin = _calificar(estado, hogar, sin, llam_sin, vis_sin)

    # ---- la IA lo marca: primer día que entra al presupuesto semanal (umbral del top de la ciudad)
    marcado = np.flatnonzero(X_sin["p"].to_numpy() >= umbral)
    t_ia = d0 + int(marcado[0]) if len(marcado) else None
    alarma = np.flatnonzero(X_sin["regla"].to_numpy())
    t_regla = d0 + int(alarma[0]) if len(alarma) else None

    # ---- mundo CON Tigo Predice: se actúa el día que la IA lo marca
    t_fix = (t_ia + conf["dias_para_corregir"]) if t_ia is not None else t_visita
    con = _mundo(hogar, eps, fin=t_fix + 1)
    X_con = _calificar(estado, hogar, con, np.zeros((1, DIAS), int), np.zeros((1, DIAS), int))
    fila_ia = X_sin.iloc[(t_ia if t_ia is not None else t_llamada) - d0]
    fila_fix = X_sin.iloc[min(t_fix, DIAS - 1) - d0]

    def serie(s: dict, X: pd.DataFrame) -> list[dict]:
        return [
            {
                "dia": d,
                "fecha": (pd.Timestamp(estado.hoy) - pd.Timedelta(days=DIAS - 1 - d)).strftime("%d/%m"),
                "senal": round(float((-27 if es_fibra else 30) + s["margen"][0, d]), 1),
                "retrans": round(float(s["retrans"][0, d]), 1),
                "reinicios": int(s["reinicios"][0, d]),
                "desconexiones": int(s["desconexiones"][0, d]),
                "latencia": round(float(s["latencia"][0, d])),
                "riesgo": round(float(X["p"].iloc[d - d0]), 4),
                "regla": bool(X["regla"].iloc[d - d0]),
            }
            for d in range(d0, DIAS)
        ]

    # ---- mensaje real (IA con guardrails o plantilla) y acciones
    cliente = fila_h.to_dict() | {"segmento": "hogar"}
    msg = mensajes.generar(mensajes.contexto_mensaje(cliente, conf["accion"]), estado.llm)
    bitacora.registrar(str(fila_h["hogar_id"]), conf["accion"], msg)
    if caso == "remoto":
        d_ver = min(t_fix + 3, DIAS - 1)
        acciones = [
            "Diagnóstico remoto del módem (ACS TR-069): WiFi saturado y firmware con cuelgues conocidos.",
            "Actualización de firmware a la versión estable, programada a las 3:00 a. m.",
            "Cambio automático del WiFi al canal menos congestionado del vecindario.",
            f"Verificación a los 3 días: retransmisiones WiFi en {con['retrans'][0, d_ver]:.0f} % "
            f"(sin la corrección: {sin['retrans'][0, d_ver]:.0f} %) y sin reinicios.",
        ]
        diagnostico = "Interferencia WiFi + firmware desactualizado: se corrige a distancia, sin técnico."
    else:
        acciones = [
            f"Diagnóstico remoto: potencia óptica {-27 + float(fila_fix['margen_ult']):.1f} dBm y bajando "
            f"{abs(float(fila_fix['pendiente_margen_14d'])):.2f} dB por día; los errores de transmisión aumentan.",
            "No se corrige a distancia: patrón típico de conector sucio o acometida doblada.",
            "WhatsApp al cliente para agendar la visita antes de que se quede sin servicio.",
            "La orden de trabajo lleva el diagnóstico y el repuesto: se resuelve en una sola visita.",
        ]
        diagnostico = "Degradación física de la señal de fibra: visita preventiva con diagnóstico."

    costo_llamada = supuesto(cfg, "costo_por_llamada")
    costo_visita = supuesto(cfg, "costo_por_visita")
    llamadas_visita = supuesto(cfg, "llamadas_por_visita")
    costo_wa = supuesto(cfg, "costo_whatsapp_mensaje")
    if caso == "remoto":
        ahorro = costo_visita + llamadas_visita * costo_llamada
        kpis = {
            "visita": "Evitada",
            "llamadas_evitadas": llamadas_visita,
            "ahorro": f"L {ahorro:,.0f}",
            "costo_accion": f"L {costo_wa:.2f}",
            "detalle": f"Visita {L(costo_visita)} + {llamadas_visita:.0f} llamadas × {L(costo_llamada)} (supuestos). "
            "Costo: 1 WhatsApp; la corrección remota es automática.",
        }
    else:
        ahorro = llamadas_visita * costo_llamada
        kpis = {
            "visita": "Se hace igual, pero una sola vez y antes del corte",
            "llamadas_evitadas": llamadas_visita,
            "ahorro": f"L {ahorro:,.0f}",
            "costo_accion": f"L {costo_wa:.2f}",
            "detalle": f"{llamadas_visita:.0f} llamadas × {L(costo_llamada)}. Las visitas repetidas evitadas no se "
            "cuentan en el caso de negocio.",
        }
    hp = estado.roi_base["hogar"]["piloto"]
    por_semana = supuesto(cfg, "hogares_piloto") * cfg["hogar"]["pct_marcados_semana"]
    return {
        "caso": caso,
        "titulo": conf["titulo"],
        "ciudad": cfg["piloto"]["ciudad"],
        "hogar": {
            "hogar_id": fila_h["hogar_id"],
            "nombre": nombre_corto(fila_h["nombre"]),
            "telefono": fila_h["telefono"],
            "nodo_id": fila_h["nodo_id"],
            "tecnologia": "Fibra (GPON)" if es_fibra else "HFC (cable)",
            "modem": fila_h["modem"],
            "plan": fila_h["plan"],
            "senal_unidad": "Potencia óptica (dBm)" if es_fibra else "SNR (dB)",
            "senal_umbral": -24.0 if es_fibra else 33.0,
        },
        "umbral_riesgo": round(float(umbral), 4),
        "presupuesto": cfg["hogar"]["pct_marcados_semana"],
        "eventos": {
            "inicio": min(i for _, i, _ in eps),
            "ia": t_ia,
            "regla": t_regla,
            "llamada": t_llamada,
            "visita": t_visita,
            "correccion": t_fix,
            "dias_antes_llamada": (t_llamada - t_ia) if t_ia is not None else None,
            "dias_antes_regla": (t_regla - t_ia) if (t_ia is not None and t_regla is not None) else None,
        },
        "riesgo_al_marcar": round(float(fila_ia["p"]), 3),
        "explicacion": explicar(estado.explicador_hogar, fila_ia.to_frame().T, np.array([es_fibra]), n=4)[0],
        "diagnostico": diagnostico,
        "acciones": acciones,
        "mensaje": {k: msg[k] for k in ("texto", "fuente", "guardrails", "version_prompt")},
        "sin": serie(sin, X_sin),
        "con": serie(con, X_con),
        "kpis": kpis,
        "frase_final": f"Esto fue un hogar. En {cfg['piloto']['ciudad']} la IA marcaría "
        f"~{sig(por_semana):,.0f} hogares "
        f"por semana (supuesto): ≈ {sig(hp['visitas_evitadas'] / (cfg['piloto']['dias'] / 30)):,.0f} visitas "
        "evitadas al mes en el escenario base.",
        "aviso": "Datos simulados — supuestos a validar con Tigo. El riesgo diario lo calcula el modelo real.",
    }
