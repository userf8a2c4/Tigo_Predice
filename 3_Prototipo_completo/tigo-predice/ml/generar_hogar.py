"""Genera datos sintéticos del frente Hogar (semilla fija): nodos, hogares, telemetría diaria de
módems, llamadas técnicas y visitas, y las variables semanales con su etiqueta.

Uso:  python -m ml.generar_hogar      (después de ml.generar_datos: agrega tablas a la misma base)

Cómo se generan (relaciones causales + variables latentes + ruido):
- Cada hogar puede sufrir problemas latentes: WiFi, firmware, señal o módem dañado. Cada problema
  empeora durante unos días (rampa) y se nota en la telemetría ANTES de que el cliente lo sufra.
- El cliente llama cuando el problema ya le afecta (según su propensión, también latente).
  Los problemas de WiFi y firmware terminan en visitas EVITABLES (se resolvían a distancia);
  los de señal y equipo, en visitas necesarias.
- Además: fallas masivas de nodo (cortes para todos los vecinos) y llamadas/visitas de fondo
  sin causa visible en la telemetría («sin falla encontrada»): ruido que ningún modelo predice.

Tablas: nodos_hogar, hogares, contactos_hogar, episodios_hogar, telemetria_hogar (últimos 28 días),
        snapshots_hogar (variables por semana + lo que pasó en los 7 días siguientes),
        variables_hogar_hoy (variables al día de corte, para calificar "hoy").
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from ml import telemetria
from ml.comun import CIUDADES, DATA_DIR, cargar_config, url_db
from ml.generar_datos import APELLIDOS, NOMBRES

DIAS = 90
HISTORIA_PREVIA = 25  # problemas que ya venían de antes de la ventana (estado estable)
CORTES = list(range(19, DIAS - 7, 7))  # 19, 26, ..., 82: la etiqueta mira los 7 días siguientes
DIAS_TELEMETRIA = 28
CIUDADES_HOGAR = {"Tegucigalpa": 0.40, "San Pedro Sula": 0.40, "La Ceiba": 0.08, "El Progreso": 0.06, "Choluteca": 0.06}
HOGARES_POR_NODO = 80
ABREV = {"Tegucigalpa": "TGU", "San Pedro Sula": "SPS", "La Ceiba": "LCE", "El Progreso": "EPR", "Choluteca": "CHO"}
MODEMS = {
    (1, 0): "ONT Huawei HG8145V5",
    (1, 1): "ONT ZTE F660 (antiguo)",
    (0, 0): "Cablemódem Technicolor CGA4233",
    (0, 1): "Cablemódem Cisco DPC3848 (antiguo)",
}
PLANES = {50: "Internet Hogar 50 Mbps", 100: "Internet Hogar 100 Mbps", 200: "Hogar Full 200 Mbps + TV"}

# Tasa diaria base de inicio de cada problema (se multiplica por factores del hogar)
TASA = {"wifi": 0.00024, "firmware": 0.00013, "senal": 0.00042, "equipo": 0.00012}
RAMPA = {"wifi": (2, 8), "firmware": (4, 14), "senal": (6, 20), "equipo": (3, 10)}
# Llamada: el cliente empieza a notar el problema cuando la severidad pasa este umbral
UMBRAL_NOTA = {"wifi": 0.35, "firmware": 0.35, "senal": 0.55, "equipo": 0.30}
PROB_LLAMADA = {"wifi": 0.22, "firmware": 0.22, "senal": 0.28, "equipo": 0.30}
RESUELVE_POR_TELEFONO = 0.30  # en WiFi/firmware, el agente lo resuelve sin visita
TASA_FONDO = 0.00025  # llamadas técnicas sin causa visible en la telemetría
VISITA_FONDO = 0.35  # de esas, cuántas terminan en visita «sin falla encontrada»
FALLAS_NODO = 14


def _hogares(rng: np.random.Generator, n: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    centros = {c[0]: (c[2], c[3]) for c in CIUDADES}
    filas_nodos = []
    for ciudad, w in CIUDADES_HOGAR.items():
        for k in range(max(2, int(round(n * w / HOGARES_POR_NODO)))):
            lat, lon = centros[ciudad]
            zona = "urbana" if rng.random() < 0.7 else "periurbana"
            disp = 0.025 if zona == "urbana" else 0.05
            filas_nodos.append(
                {
                    "nodo_id": f"{ABREV[ciudad]}-N{k + 1:03d}",
                    "ciudad": ciudad,
                    "tecnologia": "fibra" if rng.random() < 0.55 else "HFC",
                    "zona": zona,
                    "lat": lat + rng.normal(0, disp),
                    "lon": lon + rng.normal(0, disp),
                    "calidad": float(rng.lognormal(0, 0.4)),
                }
            )
    nodos = pd.DataFrame(filas_nodos)
    por_ciudad = nodos["ciudad"].map(nodos["ciudad"].value_counts())
    pesos = (nodos["ciudad"].map(CIUDADES_HOGAR) / por_ciudad).to_numpy()
    pesos = pesos / pesos.sum()
    idx = rng.choice(len(nodos), size=n, p=pesos)
    nd = nodos.iloc[idx].reset_index(drop=True)
    fibra = (nd["tecnologia"] == "fibra").astype(int).to_numpy()
    antiguo = (rng.random(n) < np.where(fibra == 1, 0.25, 0.35)).astype(int)
    plan = rng.choice([50, 100, 200], size=n, p=[0.45, 0.40, 0.15])
    hogares = pd.DataFrame(
        {
            "hogar_id": [f"HG-{i + 1:05d}" for i in range(n)],
            "nombre": [f"{rng.choice(NOMBRES)} {rng.choice(APELLIDOS)}" for _ in range(n)],
            "telefono": [f"+504 {rng.choice(['9', '8', '3'])}***-{rng.integers(1000, 9999)}" for _ in range(n)],
            "ciudad": nd["ciudad"],
            "nodo_id": nd["nodo_id"],
            "tecnologia": nd["tecnologia"],
            "zona": nd["zona"],
            "lat": nd["lat"] + rng.normal(0, 0.004, n),
            "lon": nd["lon"] + rng.normal(0, 0.004, n),
            "es_fibra": fibra,
            "modem": [MODEMS[(f, a)] for f, a in zip(fibra, antiguo, strict=True)],
            "modem_antiguo": antiguo,
            "edad_modem_meses": np.where(antiguo == 1, rng.integers(36, 85, n), rng.integers(0, 41, n)),
            "firmware_desactualizado": (rng.random(n) < np.where(antiguo == 1, 0.35, 0.12)).astype(int),
            "solo_2_4ghz": (rng.random(n) < np.where(antiguo == 1, 0.7, 0.05)).astype(int),
            "plan_mbps": plan,
            "plan": [PLANES[p] for p in plan],
            "antiguedad_meses": rng.integers(1, 121, n),
            "dispositivos_base": rng.poisson(4 + plan / 40) + 1,
            "uso_base": rng.lognormal(np.log(6 + plan / 25), 0.45, n),
            "canal_preferido": rng.choice(["WhatsApp", "SMS"], size=n, p=[0.85, 0.15]),
            "propension": rng.lognormal(0, 0.45, n),  # latente: qué tan rápido llama este cliente
            "calidad_nodo": nd["calidad"].to_numpy(),
        }
    )
    # Consentimiento para mensajes de servicio (generador aparte: no altera el resto de los datos)
    hogares["acepta_mensajes"] = (np.random.default_rng(len(hogares)).random(n) < 0.96).astype(int)
    return nodos, hogares


def _tasas(h: pd.DataFrame) -> dict[str, np.ndarray]:
    disp = np.clip(1 + 0.15 * (h["dispositivos_base"].to_numpy() - 7), 0.5, 3)
    return {
        "wifi": TASA["wifi"] * disp * np.where(h["solo_2_4ghz"] == 1, 2.2, 1.0),
        "firmware": TASA["firmware"]
        * np.where(h["firmware_desactualizado"] == 1, 3.0, 1.0)
        * np.where(h["modem_antiguo"] == 1, 1.5, 1.0),
        "senal": TASA["senal"]
        * np.where(h["es_fibra"] == 1, 1.0, 1.5)
        * np.where(h["zona"] == "periurbana", 1.4, 1.0)
        * h["calidad_nodo"].to_numpy(),
        "equipo": TASA["equipo"] * (1 + h["edad_modem_meses"].to_numpy() / 30),
    }


def generar(semilla: int | None = None) -> dict[str, pd.DataFrame]:
    cfg = cargar_config()
    semilla = (cfg["general"]["semilla"] if semilla is None else semilla) + 303
    rng = np.random.default_rng(semilla)
    n = int(cfg["hogar"]["hogares_simulados"])
    corte = date.fromisoformat(cfg["general"]["fecha_corte"])
    fechas = [corte - timedelta(days=DIAS - 1 - d) for d in range(DIAS)]

    nodos, hogares = _hogares(rng, n)
    senales = telemetria.base(rng, hogares, DIAS)
    llamadas = np.zeros((n, DIAS), dtype=int)
    visitas = np.zeros((n, DIAS), dtype=int)
    contactos: list[dict] = []
    episodios: list[dict] = []
    prop = hogares["propension"].to_numpy()

    def contacto(i: int, dia: int, tipo: str, causa: str, evitable: int, ep: int | None, origen: str, ini: int):
        if 0 <= dia < DIAS:
            (llamadas if tipo == "llamada" else visitas)[i, dia] += 1
            contactos.append(
                {
                    "i": i,
                    "dia": dia,
                    "tipo": tipo,
                    "causa": causa,
                    "evitable": evitable,
                    "episodio": ep,
                    "origen": origen,
                    "ep_inicio": ini,
                }
            )

    # ------------------------------------------------------------ problemas latentes por hogar
    tasas = _tasas(hogares)
    span = DIAS + HISTORIA_PREVIA
    for tipo, tasa in tasas.items():
        cuantos = rng.poisson(tasa * span)
        for i in np.flatnonzero(cuantos):
            for _ in range(cuantos[i]):
                ini = int(rng.integers(-HISTORIA_PREVIA, DIAS))
                rampa = int(rng.integers(*RAMPA[tipo]))
                fin_natural = ini + rampa + int(rng.lognormal(np.log(8), 0.5)) if tipo == "wifi" else ini + 70
                sev = telemetria.severidad(DIAS + 30, ini + 30, rampa, fin_natural + 30)  # índice +30: días previos
                u = UMBRAL_NOTA[tipo]
                p_dia = PROB_LLAMADA[tipo] * np.clip((sev - u) / (1 - u), 0, None) ** 1.2 * min(prop[i], 2.5)
                llama = np.flatnonzero(rng.random(len(p_dia)) < p_dia)
                ep = len(episodios)
                fin = fin_natural
                if len(llama):
                    t1 = int(llama[0]) - 30
                    contacto(i, t1, "llamada", telemetria.TIPOS[tipo]["nombre"], 0, ep, tipo, ini)
                    if telemetria.TIPOS[tipo]["remoto"] and rng.random() < RESUELVE_POR_TELEFONO:
                        fin = t1 + 1
                    else:
                        tv = t1 + int(rng.integers(1, 4 if tipo != "senal" else 5))
                        if rng.random() < (0.5 if telemetria.TIPOS[tipo]["remoto"] else 0.6):
                            contacto(i, int(rng.integers(t1, tv + 1)), "llamada", "Seguimiento", 0, ep, tipo, ini)
                        evitable = int(telemetria.TIPOS[tipo]["remoto"])
                        contacto(i, tv, "visita", telemetria.TIPOS[tipo]["cierre"], evitable, ep, tipo, ini)
                        fin = tv
                        if tipo == "senal" and rng.random() < 0.12:  # repetición: no se resolvió a la primera
                            tr = tv + int(rng.integers(3, 11))
                            contacto(i, tr - 1, "llamada", "Reclamo repetido", 0, ep, tipo, ini)
                            contacto(i, tr, "visita", "Visita repetida", 0, ep, tipo, ini)
                            fin = tr
                fin = min(fin, fin_natural) if tipo == "wifi" else fin
                episodios.append({"episodio": ep, "i": i, "tipo": tipo, "inicio": ini, "rampa": rampa, "fin": fin})
                telemetria.aplicar(senales, i, tipo, telemetria.severidad(DIAS, ini, rampa, fin), rng)

    # ------------------------------------------------------------ fallas masivas de nodo
    nodo_de = hogares["nodo_id"].to_numpy()
    for _ in range(FALLAS_NODO):
        nodo = str(rng.choice(nodos["nodo_id"]))
        dia, horas = int(rng.integers(0, DIAS)), float(rng.uniform(2, 14))
        filas = np.flatnonzero(nodo_de == nodo)
        telemetria.falla_nodo(senales, filas, dia, horas, rng)
        for i in filas:
            if rng.random() < min(0.6, 0.2 * prop[i]):
                contacto(i, dia, "llamada", "Falla masiva de nodo", 0, None, "nodo", dia)
                if rng.random() < 0.2:  # visita innecesaria: la falla era del nodo, no del hogar
                    contacto(i, dia + int(rng.integers(1, 4)), "visita", "Falla masiva de nodo", 1, None, "nodo", dia)

    # ------------------------------------------------------------ llamadas de fondo (sin señal)
    fondo = rng.random((n, DIAS)) < TASA_FONDO * np.clip(prop, 0.3, 2.5)[:, None]
    for i, dia in zip(*np.nonzero(fondo), strict=True):
        contacto(int(i), int(dia), "llamada", "Consulta técnica", 0, None, "fondo", int(dia))
        if rng.random() < VISITA_FONDO:
            contacto(
                int(i), int(dia) + int(rng.integers(1, 4)), "visita", "Sin falla encontrada", 1, None, "fondo", int(dia)
            )

    for k in senales:
        senales[k] = np.clip(senales[k], 0 if k != "margen" else -5, None)

    # ------------------------------------------------------------ variables semanales + etiquetas
    ct = pd.DataFrame(contactos)
    ct["hogar_id"] = hogares["hogar_id"].to_numpy()[ct["i"]]
    remoto = ct["origen"].isin([t for t, v in telemetria.TIPOS.items() if v["remoto"]])
    fisico = ct["origen"].isin([t for t, v in telemetria.TIPOS.items() if not v["remoto"]])
    snaps = []
    for d in CORTES:
        X = telemetria.variables(senales, hogares, llamadas, visitas, d).reset_index(names="hogar_id")
        v = ct[(ct["dia"] > d) & (ct["dia"] <= d + 7)]
        activo = v["ep_inicio"] <= d  # el problema ya existía al momento de calificar
        llam, vis = v["tipo"] == "llamada", v["tipo"] == "visita"
        prev, fis = remoto.loc[v.index] & activo, fisico.loc[v.index] & activo
        et = (
            pd.DataFrame(
                {
                    "hogar_id": v["hogar_id"],
                    "llamadas_7d": llam,
                    "visitas_7d": vis,
                    "visitas_evitables_7d": vis & (v["evitable"] == 1),
                    "llamadas_prevenibles_7d": llam & prev,
                    "visitas_prevenibles_7d": vis & prev,
                    "llamadas_fisico_7d": llam & fis,
                }
            )
            .groupby("hogar_id")
            .sum()
        )
        X = X.merge(et, left_on="hogar_id", right_index=True, how="left").fillna({c: 0 for c in et.columns})
        X["evento_7d"] = ((X["llamadas_7d"] + X["visitas_7d"]) > 0).astype(int)
        X.insert(1, "dia_corte", d)
        X.insert(2, "fecha_corte", fechas[d].isoformat())
        snaps.append(X)
    snapshots = pd.concat(snaps, ignore_index=True)
    snapshots = snapshots.merge(hogares[["hogar_id", "ciudad", "nodo_id", "tecnologia", "zona"]], on="hogar_id")
    for c in (
        "llamadas_7d",
        "visitas_7d",
        "visitas_evitables_7d",
        "llamadas_prevenibles_7d",
        "visitas_prevenibles_7d",
        "llamadas_fisico_7d",
    ):
        snapshots[c] = snapshots[c].astype(int)

    hoy = telemetria.variables(senales, hogares, llamadas, visitas, DIAS - 1).reset_index(names="hogar_id")

    d0 = DIAS - DIAS_TELEMETRIA
    tele = pd.DataFrame(
        {
            "hogar_id": np.repeat(hogares["hogar_id"].to_numpy(), DIAS_TELEMETRIA),
            "dia": np.tile(np.arange(d0, DIAS), n),
            **{k: np.round(v[:, d0:].ravel(), 2) for k, v in senales.items()},
        }
    )
    tele["fecha"] = [fechas[d].isoformat() for d in tele["dia"]]

    ct["fecha"] = [fechas[d].isoformat() for d in ct["dia"]]
    ep = pd.DataFrame(episodios)
    ep["hogar_id"] = hogares["hogar_id"].to_numpy()[ep["i"]]
    return {
        "nodos_hogar": nodos,
        "hogares": hogares.drop(columns=["propension", "calidad_nodo"]),
        "contactos_hogar": ct.drop(columns=["i"]),
        "episodios_hogar": ep.drop(columns=["i"]),
        "telemetria_hogar": tele,
        "snapshots_hogar": snapshots,
        "variables_hogar_hoy": hoy,
    }


def guardar(tablas: dict[str, pd.DataFrame]) -> None:
    eng = create_engine(url_db())
    for nombre, df in tablas.items():
        df.to_sql(nombre, eng, index=False, if_exists="replace", chunksize=20000)
    eng.dispose()


def validar(tablas: dict[str, pd.DataFrame]) -> str:
    h, ct, s = tablas["hogares"], tablas["contactos_hogar"], tablas["snapshots_hogar"]
    meses = DIAS / 30
    vis = ct[ct["tipo"] == "visita"]
    lin = ["# Validación de datos sintéticos · Hogar", ""]
    lin.append(
        f"- Hogares: {len(h):,} | Nodos: {len(tablas['nodos_hogar'])} | "
        f"Ciudades: {h['ciudad'].value_counts().to_dict()}"
    )
    lin.append(f"- Fibra: {h['es_fibra'].mean():.0%} | Módem antiguo: {h['modem_antiguo'].mean():.0%}")
    lin.append(
        "- Problemas latentes en 90 días: "
        f"{tablas['episodios_hogar'].query('inicio >= 0')['tipo'].value_counts().to_dict()}"
    )
    lin.append(f"- Visitas por hogar al mes: {len(vis) / len(h) / meses:.2%} (supuesto nacional base: 4.3 %)")
    lin.append(f"- Visitas evitables: {vis['evitable'].mean():.0%} (supuesto nacional base: 30 %)")
    lin.append(f"- Llamadas técnicas por visita: {(ct['tipo'] == 'llamada').sum() / max(len(vis), 1):.2f}")
    lin.append(f"- Causas de visita: {vis['causa'].value_counts().to_dict()}")
    lin.append(f"- Hogares con llamada o visita en 7 días (por semana): {s['evento_7d'].mean():.2%}")
    lin.append(f"- Visitas por 1,000 hogares en 7 días: {s['visitas_7d'].mean() * 1000:.1f}")
    return "\n".join(lin)


def main() -> None:
    tablas = generar()
    guardar(tablas)
    resumen = validar(tablas)
    (DATA_DIR / "validacion_hogar.md").write_text(resumen, encoding="utf-8", newline="\n")
    print(resumen)


if __name__ == "__main__":
    main()
