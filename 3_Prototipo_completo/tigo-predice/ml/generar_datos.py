"""Genera datos sintéticos realistas de clientes de Tigo Honduras (semilla fija).

Uso:  python -m ml.generar_datos

Tablas que escribe en data/tigo_predice.db:
  clientes, celdas, red_diaria, fallas_masivas, uso_semanal, pagos,
  interacciones, encuestas, etiquetas

Las etiquetas (llamará en 7 días / abandonará en 30 días) se generan con
relaciones causales plausibles + variables latentes no observables (lealtad)
+ ruido, para que el modelo aprenda patrones creíbles sin llegar a AUC 0.99.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from ml import eventos, features
from ml.comun import CIUDADES, DATA_DIR, DB_PATH, cargar_config, url_db

DIAS = 90
SEMANAS = 13
N_CELDAS_OBJETIVO = 200
# Qué tan fuerte es la señal causal frente al azar. Calibrado para AUC ~0.83-0.87
# (creíble: un AUC de 0.99 se vería falso ante los jueces).
FUERZA_SENAL = 1.2

NOMBRES = [
    "José",
    "María",
    "Juan",
    "Ana",
    "Carlos",
    "Rosa",
    "Luis",
    "Karla",
    "Jorge",
    "Gabriela",
    "Marvin",
    "Dania",
    "Wilmer",
    "Iris",
    "Óscar",
    "Sonia",
    "Kevin",
    "Yessenia",
    "Elvin",
    "Lesly",
    "Denis",
    "Marlen",
    "Edwin",
    "Suyapa",
    "Nelson",
    "Glenda",
    "Fredy",
    "Xiomara",
    "Mario",
    "Cindy",
    "Héctor",
    "Lourdes",
    "Allan",
    "Fátima",
    "Bayron",
    "Nohemí",
    "Josué",
    "Daysi",
    "Wendy",
    "Elmer",
]
APELLIDOS = [
    "Hernández",
    "López",
    "Martínez",
    "Rodríguez",
    "García",
    "Mejía",
    "Flores",
    "Reyes",
    "Castillo",
    "Zelaya",
    "Ramírez",
    "Cruz",
    "Sánchez",
    "Pineda",
    "Discua",
    "Bonilla",
    "Banegas",
    "Maradiaga",
    "Ordóñez",
    "Fúnez",
    "Matute",
    "Turcios",
    "Rivera",
    "Sierra",
    "Paz",
    "Alvarado",
    "Andino",
    "Ponce",
    "Murillo",
    "Velásquez",
    "Aguilar",
    "Midence",
]
PLANES = {
    "prepago": ["Prepago Tigo", "Prepago Tigo + Paquetes"],
    "pospago": ["Plan Ilimitado 10 GB", "Plan Ilimitado 20 GB", "Plan Ilimitado 40 GB"],
    "hogar": ["Internet Hogar 50 Mbps", "Internet Hogar 100 Mbps", "Hogar Full 200 Mbps + TV"],
}
ABREV = {
    "Tegucigalpa": "TGU",
    "San Pedro Sula": "SPS",
    "La Ceiba": "LCE",
    "Choluteca": "CHO",
    "Comayagua": "CMY",
    "El Progreso": "EPR",
    "Danlí": "DAN",
    "Juticalpa": "JUT",
    "Santa Rosa de Copán": "SRC",
    "Siguatepeque": "SIG",
}

# Fallas masivas fijas (día de inicio 0..89, horas de duración, ciudad, nº de sitios, causa).
# Se completan con FALLAS_ALEATORIAS más. La de La Ceiba sigue ACTIVA en la fecha de corte.
FALLAS_FIJAS = [
    (18, 40, "Tegucigalpa", 6, "Lluvias intensas dañaron enlaces de transmisión"),
    (41, 20, "Choluteca", 4, "Corte de fibra óptica por obra vial"),
    (63, 30, "San Pedro Sula", 5, "Falla de energía comercial en sitios"),
    (87, 96, "La Ceiba", 5, "Tormenta tropical: sitios sin energía"),
]
FALLAS_ALEATORIAS = 18
CAUSAS = [
    "Falla de energía comercial en sitios",
    "Corte de fibra óptica",
    "Lluvias intensas dañaron enlaces",
    "Robo de baterías en un sitio",
    "Falla de equipo de transmisión",
]
# Tasa base de llamada en 72 h sin aviso (MidSouth: 33 %) y fuerza de la señal causal.
TASA_LLAMADA_72H = 0.33
FUERZA_72H = 1.3


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def _calibrar_intercepto(z_sin_intercepto: np.ndarray, tasa_objetivo: float) -> float:
    """Busca el intercepto que hace que la probabilidad promedio = tasa objetivo."""
    lo, hi = -15.0, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _sigmoid(z_sin_intercepto + mid).mean() > tasa_objetivo:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def _eventos_falla(rng, fallas, clientes, celdas, interacciones, encuestas, red, fechas, corte, lealtad):
    """Por cada falla resuelta y cliente afectado: variables al inicio + si llamó en 72 h.

    Se procesa en orden cronológico: las llamadas de una falla entran al historial y
    cuentan como "llamadas previas" en las fallas siguientes. Devuelve (eventos, interacciones).
    """
    zona_celda = celdas.set_index("celda_id")["zona"]
    pos = pd.Series(np.arange(len(clientes)), index=clientes["cliente_id"])
    resueltas = fallas[fallas["estado"] == "resuelta"].sort_values(["dia_inicio", "hora_inicio"])

    def variables(f, inter, previas):
        celdas_f = set(f["celdas"].split(","))
        afect = clientes[clientes["celda_id"].isin(celdas_f)]
        X = eventos.construir(
            afect,
            zona_celda,
            inter,
            encuestas,
            red,
            previas,
            date.fromisoformat(f["inicio"]),
            corte,
            None if pd.isna(f["eta_horas"]) else float(f["eta_horas"]),
            len(celdas_f),
            int(f["hora_inicio"]),
        )
        return X, celdas_f

    # 1ª pasada (sin retroalimentación) solo para fijar el intercepto => tasa base ~33 %
    zs, previas = [], []
    for _, f in resueltas.iterrows():
        X, celdas_f = variables(f, interacciones, previas)
        zs.append(FUERZA_72H * eventos.logit_llamada(X, f["duracion_horas"], lealtad[pos[X.index]], rng))
        previas.append((celdas_f, date.fromisoformat(f["inicio"])))
    intercepto = _calibrar_intercepto(np.concatenate(zs), TASA_LLAMADA_72H)

    # 2ª pasada cronológica con retroalimentación al historial
    filas, nuevas_llamadas, previas = [], [], []
    inter = interacciones
    for _, f in resueltas.iterrows():
        X, celdas_f = variables(f, inter, previas)
        z = FUERZA_72H * eventos.logit_llamada(X, f["duracion_horas"], lealtad[pos[X.index]], rng)
        llamo = rng.random(len(X)) < _sigmoid(z + intercepto)
        n_llam = np.where(llamo, 1 + rng.poisson(0.4, len(X)), 0)
        horas = np.where(llamo, np.minimum(rng.exponential(5.0, len(X)), 71.9), np.nan)
        cl = clientes.set_index("cliente_id").loc[X.index]
        ev = X.copy()
        ev.insert(0, "cliente_id", X.index)
        ev.insert(0, "dia_inicio", int(f["dia_inicio"]))
        ev.insert(0, "falla_id", f["falla_id"])
        ev["ciudad"] = f["ciudad"]
        ev["zona"] = cl["celda_id"].map(zona_celda).to_numpy()
        ev["segmento"] = cl["segmento"].to_numpy()
        ev["duracion_horas"] = f["duracion_horas"]
        ev["llamo_72h"] = llamo.astype(int)
        ev["n_llamadas_72h"] = n_llam
        ev["horas_a_primera_llamada"] = np.round(horas, 2)
        filas.append(ev.reset_index(drop=True))
        # las llamadas quedan en el historial del call center
        base_h = f["dia_inicio"] * 24 + f["hora_inicio"]
        for cid, k, h in zip(X.index[llamo], n_llam[llamo], horas[llamo], strict=True):
            for j in range(int(k)):
                dia = min(int((base_h + h + j * 6) // 24), len(fechas) - 1)
                nuevas_llamadas.append(
                    {
                        "cliente_id": cid,
                        "fecha": fechas[dia].isoformat(),
                        "motivo": "red",
                        "resuelto": int(rng.random() < 0.45),
                        "ticket_abierto": 0,
                        "horas_resolucion": round(float(rng.gamma(2, 20)), 1),
                    }
                )
        inter = pd.concat([interacciones, pd.DataFrame(nuevas_llamadas)], ignore_index=True)
        previas.append((celdas_f, date.fromisoformat(f["inicio"])))
    return pd.concat(filas, ignore_index=True), inter


def generar(semilla: int | None = None) -> dict[str, pd.DataFrame]:
    cfg = cargar_config()
    semilla = cfg["general"]["semilla"] if semilla is None else semilla
    rng = np.random.default_rng(semilla)
    n = int(cfg["general"]["clientes_simulados"])
    corte = date.fromisoformat(cfg["general"]["fecha_corte"])
    fechas = [corte - timedelta(days=DIAS - 1 - d) for d in range(DIAS)]

    # ------------------------------------------------------------------ celdas
    pesos = np.array([c[4] for c in CIUDADES], dtype=float)
    pesos /= pesos.sum()
    filas_celdas = []
    for (ciudad, depto, lat, lon, _), w in zip(CIUDADES, pesos, strict=False):
        k = max(6, int(round(N_CELDAS_OBJETIVO * w)))
        for i in range(k):
            problema = rng.random() < 0.12
            zona = rng.choice(["urbana", "periurbana", "rural"], p=[0.6, 0.25, 0.15])
            disp = {"urbana": 0.02, "periurbana": 0.05, "rural": 0.09}[zona]
            filas_celdas.append(
                {
                    "celda_id": f"{ABREV[ciudad]}-{i + 1:03d}",
                    "ciudad": ciudad,
                    "departamento": depto,
                    "zona": zona,
                    "lat": lat + rng.normal(0, disp),
                    "lon": lon + rng.normal(0, disp),
                    "tecnologia": "4G" if rng.random() < 0.85 else "3G",
                    "celda_problematica": int(problema),
                }
            )
    celdas = pd.DataFrame(filas_celdas)
    nc = len(celdas)
    prob = celdas["celda_problematica"].to_numpy()
    es3g = (celdas["tecnologia"] == "3G").to_numpy()

    # ------------------------------------------------------- red diaria por celda
    tasa = rng.lognormal(np.log(0.25), 0.5, nc) * np.where(prob == 1, 4.0, 1.0)
    caidas = rng.poisson(tasa[:, None], (nc, DIAS)).astype(float)
    min_sin = caidas * rng.exponential(12, (nc, DIAS))
    lat_base = np.where(es3g, 90.0, 45.0) * np.where(prob == 1, 1.35, 1.0)
    latencia = lat_base[:, None] + rng.normal(0, 6, (nc, DIAS)) + caidas * 4
    vel = np.clip(rng.normal((0.86 - 0.22 * prob)[:, None], 0.07, (nc, DIAS)), 0.15, 1.0)

    lista_fallas = list(FALLAS_FIJAS)
    for _ in range(FALLAS_ALEATORIAS):
        lista_fallas.append(
            (
                int(rng.integers(3, 85)),
                float(np.clip(rng.lognormal(np.log(7), 0.7), 1.5, 48)),
                str(rng.choice([c[0] for c in CIUDADES], p=pesos)),
                int(rng.integers(2, 6)),
                str(rng.choice(CAUSAS)),
            )
        )
    lista_fallas.sort(key=lambda f: f[0])

    filas_fallas = []
    for idx, (ini, horas, ciudad, k, causa) in enumerate(lista_fallas):
        cand = np.flatnonzero((celdas["ciudad"] == ciudad).to_numpy())
        elegidas = rng.choice(cand, size=min(k, len(cand)), replace=False)
        hora_inicio = int(rng.integers(0, 24))
        dias_afectados = int(np.ceil((hora_inicio + horas) / 24))
        fin = min(ini + dias_afectados, DIAS)
        for d in range(ini, fin):
            caidas[elegidas, d] += rng.poisson(3 + horas / 4, len(elegidas))
            min_sin[elegidas, d] += min(horas, 24) * 60 * rng.uniform(0.6, 1.0, len(elegidas))
            latencia[elegidas, d] *= 3.0
            vel[elegidas, d] = rng.uniform(0.05, 0.3, len(elegidas))
        activa = (ini * 24 + hora_inicio + horas) > DIAS * 24
        if activa:
            eta = 18.0
        elif rng.random() < cfg["piloto"]["pct_fallas_con_eta"]:
            eta = float(max(1, round(horas * rng.normal(1, 0.25))))
        else:
            eta = None
        filas_fallas.append(
            {
                "falla_id": f"FM-{idx + 1:03d}",
                "ciudad": ciudad,
                "celdas": ",".join(celdas.loc[elegidas, "celda_id"]),
                "inicio": fechas[ini].isoformat(),
                "dia_inicio": ini,
                "hora_inicio": hora_inicio,
                "duracion_horas": round(horas, 1),
                "fin": None if activa else fechas[fin - 1].isoformat(),
                "estado": "activa" if activa else "resuelta",
                "causa": causa,
                "eta_horas": eta,
            }
        )
    fallas = pd.DataFrame(filas_fallas)

    red = pd.DataFrame(
        {
            "celda_id": np.repeat(celdas["celda_id"].to_numpy(), DIAS),
            "fecha": np.tile([f.isoformat() for f in fechas], nc),
            "caidas": caidas.ravel().astype(int),
            "minutos_sin_servicio": np.round(min_sin.ravel(), 1),
            "latencia_ms": np.round(latencia.ravel(), 1),
            "velocidad_pct_plan": np.round(vel.ravel(), 3),
        }
    )

    # ---------------------------------------------------------------- clientes
    segmento = rng.choice(["prepago", "pospago", "hogar"], size=n, p=[0.6, 0.3, 0.1])
    ciudad_idx = rng.choice(len(CIUDADES), size=n, p=pesos)
    celda_idx = np.empty(n, dtype=int)
    for ci, (ciudad, *_rest) in enumerate(CIUDADES):
        miembros = np.flatnonzero(ciudad_idx == ci)
        cand = np.flatnonzero((celdas["ciudad"] == ciudad).to_numpy())
        celda_idx[miembros] = rng.choice(cand, size=len(miembros))

    forma = {"prepago": 1.6, "pospago": 2.6, "hogar": 2.2}
    antig = np.array([rng.gamma(forma[s], 14) for s in segmento])
    antig = np.clip(np.round(antig), 1, 180).astype(int)
    arpu_seg = np.array([cfg["arpu"][s] for s in segmento])
    arpu = np.round(arpu_seg * rng.lognormal(-0.06, 0.35, n), 2)
    gama = np.where(segmento == "hogar", "módem", rng.choice(["baja", "media", "alta"], size=n, p=[0.45, 0.4, 0.15]))
    gama = np.where((segmento == "pospago") & (rng.random(n) < 0.5), "alta", gama)

    # variables latentes (NO se guardan: el modelo no las ve)
    lealtad = rng.normal(0, 1, n)
    sensib_precio = rng.normal(0, 1, n)
    problema_indiv = rng.random(n) < 0.045  # módem/APN/equipo con falla individual

    nombres = [f"{rng.choice(NOMBRES)} {rng.choice(APELLIDOS)} {rng.choice(APELLIDOS)}" for _ in range(n)]
    telefonos = [f"+504 {rng.choice(['9', '8', '3'])}***-{rng.integers(1000, 9999)}" for _ in range(n)]
    planes = [rng.choice(PLANES[s]) for s in segmento]
    ultimo_contacto = np.where(
        rng.random(n) < 0.05,
        [(corte - timedelta(days=int(d))).isoformat() for d in rng.integers(1, 6, n)],
        None,
    )

    clientes = pd.DataFrame(
        {
            "cliente_id": [f"C{i + 1:06d}" for i in range(n)],
            "nombre": nombres,
            "telefono": telefonos,
            "segmento": segmento,
            "plan": planes,
            "ciudad": [CIUDADES[i][0] for i in ciudad_idx],
            "departamento": [CIUDADES[i][1] for i in ciudad_idx],
            "celda_id": celdas["celda_id"].to_numpy()[celda_idx],
            "lat": celdas["lat"].to_numpy()[celda_idx] + rng.normal(0, 0.01, n),
            "lon": celdas["lon"].to_numpy()[celda_idx] + rng.normal(0, 0.01, n),
            "antiguedad_meses": antig,
            "gama_dispositivo": gama,
            "arpu": arpu,
            "opt_out": (rng.random(n) < 0.03).astype(int),
            "canal_preferido": rng.choice(["WhatsApp", "SMS"], size=n, p=[0.82, 0.18]),
            "ultimo_contacto_proactivo": ultimo_contacto,
        }
    )

    # --------------------------------------------------------- uso semanal
    base_gb = np.select([segmento == "prepago", segmento == "pospago"], [1.6, 4.5], 55.0)
    base_voz = np.select([segmento == "prepago", segmento == "pospago"], [45.0, 95.0], 0.0)
    actividad = rng.lognormal(0, 0.45, n)
    intencion = _sigmoid(-1.2 * lealtad + 0.5 * sensib_precio - 2.2) > rng.random(n)
    declive = np.where(intencion, np.clip(rng.normal(0.45, 0.15, n), 0.1, 0.9), 0.0)
    # 90 días + 1 día de relleno al inicio = 13 semanas exactas
    caidas_semana = np.pad(caidas[celda_idx], ((0, 0), (SEMANAS * 7 - DIAS, 0))).reshape(n, SEMANAS, 7).sum(2)

    # ------------------------------------------- telemetría individual (equipo / módem)
    vel_celda_7d = vel[:, -7:].mean(1)[celda_idx]
    lat_celda_7d = latencia[:, -7:].mean(1)[celda_idx]
    factor_equipo = np.where(gama == "baja", 0.92, 1.0)
    telemetria = pd.DataFrame(
        {
            "cliente_id": [f"C{i + 1:06d}" for i in range(n)],
            "velocidad_pct_plan_7d": np.round(
                np.clip(
                    vel_celda_7d
                    * factor_equipo
                    * rng.normal(1, 0.06, n)
                    * np.where(problema_indiv, rng.uniform(0.25, 0.5, n), 1.0),
                    0.03,
                    1.0,
                ),
                3,
            ),
            "latencia_ms_7d": np.round(
                lat_celda_7d + rng.normal(0, 8, n) + np.where(problema_indiv, rng.uniform(40, 120, n), 0), 1
            ),
        }
    )

    filas_uso = {k: [] for k in ("cliente_id", "semana", "datos_gb", "voz_min", "recargas", "monto_recargas")}
    for w in range(SEMANAS):
        semanas_al_final = SEMANAS - w  # 13..1
        factor = np.where(semanas_al_final <= 4, 1 - declive * (5 - semanas_al_final) / 4, 1.0)
        factor = factor * (1 - np.minimum(caidas_semana[:, w], 20) * 0.01)
        ruido = rng.gamma(8, 1 / 8, n)
        gb = np.round(base_gb * actividad * factor * ruido, 3)
        voz = np.round(base_voz * actividad * factor * rng.gamma(8, 1 / 8, n), 1)
        rec = np.where(segmento == "prepago", rng.poisson(np.clip(1.3 * actividad * factor, 0.05, None)), 0)
        monto = rec * rng.choice([20, 30, 50, 100], size=n, p=[0.35, 0.3, 0.25, 0.1])
        filas_uso["cliente_id"].append(clientes["cliente_id"].to_numpy())
        filas_uso["semana"].append(np.full(n, w + 1))
        filas_uso["datos_gb"].append(gb)
        filas_uso["voz_min"].append(voz)
        filas_uso["recargas"].append(rec)
        filas_uso["monto_recargas"].append(monto)
    uso = pd.DataFrame({k: np.concatenate(v) for k, v in filas_uso.items()})

    # ----------------------------------------------------------- pagos (pospago/hogar)
    con_factura = segmento != "prepago"
    idx_fact = np.flatnonzero(con_factura)
    filas_pagos = []
    p_atraso = _sigmoid(0.9 * sensib_precio - 0.6 * lealtad - 1.6)
    for m in range(3):
        mes = (corte.replace(day=1) - timedelta(days=30 * (2 - m))).strftime("%Y-%m")
        atrasa = rng.random(len(idx_fact)) < p_atraso[idx_fact]
        dias = np.where(atrasa, rng.integers(3, 45, len(idx_fact)), 0)
        filas_pagos.append(
            pd.DataFrame(
                {
                    "cliente_id": clientes["cliente_id"].to_numpy()[idx_fact],
                    "mes": mes,
                    "monto": arpu[idx_fact],
                    "dias_atraso": dias,
                    "cambio_plan": np.where(
                        rng.random(len(idx_fact)) < 0.02 + 0.05 * (lealtad[idx_fact] < -1), "baja", ""
                    ),
                }
            )
        )
    pagos = pd.concat(filas_pagos, ignore_index=True)
    atraso_ultimo = np.zeros(n)
    ultimo_mes = pagos["mes"].max()
    ult = pagos[pagos["mes"] == ultimo_mes].set_index("cliente_id")["dias_atraso"]
    atraso_ultimo[idx_fact] = ult.reindex(clientes["cliente_id"].to_numpy()[idx_fact]).to_numpy()

    # ----------------------------------------------------- interacciones (call center)
    filas_int = []
    caidas_cli = caidas[celda_idx]  # (n, DIAS)
    for v in range(3):  # ventanas de 30 días
        d0, d1 = v * 30, (v + 1) * 30
        cw = caidas_cli[:, d0:d1].sum(1)
        lam = (
            0.07
            + 0.045 * np.power(cw, 0.85)
            + 0.9 * problema_indiv
            + 0.35 * (atraso_ultimo > 15)
            + 0.15 * (segmento == "hogar")
        )
        k = rng.poisson(lam)
        for i in np.flatnonzero(k):
            pesos_mot = np.array(
                [0.045 * cw[i] ** 0.85, 0.9 * problema_indiv[i], 0.35 * (atraso_ultimo[i] > 15) + 0.03, 0.07]
            )
            pesos_mot /= pesos_mot.sum()
            for _ in range(k[i]):
                motivo = rng.choice(["red", "equipo", "cobro", "otros"], p=pesos_mot)
                p_res = {"red": 0.45, "equipo": 0.6, "cobro": 0.7, "otros": 0.85}[motivo]
                dia = int(rng.integers(d0, d1))
                resuelto = rng.random() < p_res
                filas_int.append(
                    {
                        "cliente_id": clientes["cliente_id"].iat[i],
                        "fecha": fechas[dia].isoformat(),
                        "motivo": motivo,
                        "resuelto": int(resuelto),
                        "ticket_abierto": int((not resuelto) and dia >= DIAS - 14 and rng.random() < 0.6),
                        "horas_resolucion": round(float(rng.gamma(2, 8 if resuelto else 30)), 1),
                    }
                )
    interacciones = pd.DataFrame(filas_int)

    # ------------------------------------------------------------- encuestas NPS
    sin_resolver_cli = np.zeros(n)
    if len(interacciones):
        sr = interacciones[interacciones["resuelto"] == 0].groupby("cliente_id").size()
        sin_resolver_cli = sr.reindex(clientes["cliente_id"]).fillna(0).to_numpy()
    responde = rng.random(n) < 0.3
    c30 = caidas_cli[:, -30:].sum(1)
    nps = np.clip(
        np.round(
            9.3
            - 0.18 * np.power(c30, 0.75)
            - 0.9 * sin_resolver_cli
            - 1.5 * problema_indiv
            + 0.9 * lealtad
            + rng.normal(0, 1.3, n)
        ),
        0,
        10,
    )
    encuestas = pd.DataFrame(
        {
            "cliente_id": clientes["cliente_id"].to_numpy()[responde],
            "fecha": [(corte - timedelta(days=int(d))).isoformat() for d in rng.integers(1, 90, responde.sum())],
            "nps": nps[responde].astype(int),
        }
    )

    # ------------------------------- eventos de falla: ¿llamó en 72 h? (sin aviso, histórico)
    tabla_eventos, interacciones = _eventos_falla(
        rng, fallas, clientes, celdas, interacciones, encuestas, red, fechas, corte, lealtad
    )

    tablas = {
        "clientes": clientes,
        "celdas": celdas,
        "red_diaria": red,
        "fallas_masivas": fallas,
        "eventos_falla": tabla_eventos,
        "uso_semanal": uso,
        "pagos": pagos,
        "interacciones": interacciones,
        "encuestas": encuestas,
        "telemetria": telemetria,
    }

    # ---------------------------------------------- etiquetas (causales + latentes + ruido)
    X = features.construir(tablas, corte)
    X = X.reindex(clientes["cliente_id"])
    seg = clientes["segmento"].to_numpy()
    nps_conocido = X["nps_ultimo"].to_numpy()
    nps_malo = np.where(np.isnan(nps_conocido), 0, nps_conocido <= 6)

    # Efectos de umbral, saturación e interacciones (así se comporta la realidad)
    caidas7 = X["caidas_7d"].to_numpy()
    sin_res = X["llamadas_sin_resolver_30d"].to_numpy()
    falla = X["falla_masiva_activa"].to_numpy()
    vel7 = X["velocidad_pct_plan_7d"].to_numpy()
    z_inc = (
        1.4 * np.tanh(caidas7 / 6)
        + 1.6 * falla
        + 0.6 * falla * (seg == "hogar")
        + 1.3 * problema_indiv
        + 1.3 * (vel7 < 0.5)
        + 0.5 * (vel7 < 0.3)
        + 0.55 * np.minimum(sin_res, 3)
        + 0.4 * X["tickets_abiertos"].to_numpy()
        + 0.45 * (X["reclamos_cobro_90d"].to_numpy() > 0)
        + 0.3 * (seg == "hogar")
        + 0.4 * (X["dias_atraso"].to_numpy() > 20)
        - 0.12 * lealtad
        + rng.normal(0, 0.5, n)
    )
    z_inc = FUERZA_SENAL * z_inc
    p_inc = _sigmoid(z_inc + _calibrar_intercepto(z_inc, 0.09))

    tend = X["tendencia_uso"].to_numpy()
    caidas30 = X["caidas_30d"].to_numpy()
    antig_x = X["antiguedad_meses"].to_numpy()
    atraso = X["dias_atraso"].to_numpy()
    sin_recarga = np.where(seg == "prepago", X["dias_sin_recarga"].to_numpy(), 0)
    z_ch = (
        1.0 * np.tanh(caidas30 / 15)
        + 1.0 * (tend < -0.3)
        + 0.6 * (tend < -0.55)
        + 0.9 * (atraso > 15)
        + 0.5 * (atraso > 30)
        + 0.5 * np.minimum(sin_res, 3)
        + 0.8 * (sin_res >= 1) * (caidas30 > 12)  # frustración acumulada
        + 0.6 * nps_malo
        + 0.7 * X["bajo_plan_90d"].to_numpy()
        + 1.0 * (sin_recarga > 21)
        + 0.5 * (sin_recarga > 35)
        + 0.7 * (antig_x <= 6)
        - 0.006 * np.minimum(antig_x, 120)
        + 0.4 * problema_indiv
        + 0.35 * (X["reclamos_cobro_90d"].to_numpy() > 0)
        + 0.6 * falla
        - 0.30 * lealtad
        + 0.15 * sensib_precio
        + rng.normal(0, 0.45, n)
    )
    z_ch = FUERZA_SENAL * z_ch
    p_ch = np.zeros(n)
    for s in ("prepago", "pospago", "hogar"):
        m = seg == s
        objetivo = cfg["churn_base_mensual"][s] * 1.15  # el corte incluye una falla activa
        p_ch[m] = _sigmoid(z_ch[m] + _calibrar_intercepto(z_ch[m], objetivo))

    tablas["etiquetas"] = pd.DataFrame(
        {
            "cliente_id": clientes["cliente_id"],
            "llamara_7d": (rng.random(n) < p_inc).astype(int),
            "churn_30d": (rng.random(n) < p_ch).astype(int),
        }
    )
    return tablas


def guardar(tablas: dict[str, pd.DataFrame]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    eng = create_engine(url_db())
    for nombre, df in tablas.items():
        df.to_sql(nombre, eng, index=False, chunksize=20000)
    eng.dispose()


def validar(tablas: dict[str, pd.DataFrame]) -> str:
    """Resumen estadístico para comprobar que los datos son plausibles."""
    cl, et = tablas["clientes"], tablas["etiquetas"]
    df = cl.merge(et, on="cliente_id")
    lineas = ["# Validación de datos sintéticos", ""]
    lineas.append(
        f"- Clientes: {len(cl):,} | Celdas: {len(tablas['celdas'])} | "
        f"Registros de red: {len(tablas['red_diaria']):,} | Llamadas: {len(tablas['interacciones']):,}"
    )
    lineas.append(f"- Mezcla de segmentos: {cl['segmento'].value_counts(normalize=True).round(3).to_dict()}")
    lineas.append(f"- Tasa de llamada en 7 días: {et['llamara_7d'].mean():.1%}")
    lineas.append(f"- Churn 30 días por segmento: {df.groupby('segmento')['churn_30d'].mean().round(3).to_dict()}")
    lineas.append(f"- Clientes por ciudad: {cl['ciudad'].value_counts().to_dict()}")
    lineas.append(
        f"- Fallas masivas: {len(tablas['fallas_masivas'])} "
        f"(activas: {(tablas['fallas_masivas']['estado'] == 'activa').sum()})"
    )
    ev = tablas["eventos_falla"]
    lineas.append(
        f"- Eventos cliente × falla: {len(ev):,} | llamó en 72 h: {ev['llamo_72h'].mean():.1%} | "
        f"llamadas por 1,000 afectados: {ev['n_llamadas_72h'].mean() * 1000:,.0f}"
    )
    lineas.append(f"- Tasa 72 h por segmento: {ev.groupby('segmento')['llamo_72h'].mean().round(3).to_dict()}")
    lineas.append(f"- Tasa 72 h por zona: {ev.groupby('zona')['llamo_72h'].mean().round(3).to_dict()}")
    X = features.construir(tablas, date.fromisoformat(cargar_config()["general"]["fecha_corte"]))
    m = X.join(et.set_index("cliente_id"))
    for col in ["caidas_30d", "llamadas_sin_resolver_30d", "dias_atraso", "tendencia_uso"]:
        corr = m[col].corr(m["churn_30d"])
        lineas.append(f"- Correlación {col} vs churn: {corr:+.3f}")
    return "\n".join(lineas)


def main() -> None:
    tablas = generar()
    guardar(tablas)
    resumen = validar(tablas)
    (DATA_DIR / "validacion_datos.md").write_text(resumen, encoding="utf-8", newline="\n")
    print(resumen)
    print(f"\nBase de datos: {DB_PATH}")


if __name__ == "__main__":
    main()
