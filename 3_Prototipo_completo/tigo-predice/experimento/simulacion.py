"""Simulación del piloto de 60 días (datos sintéticos) para mostrar CÓMO se medirá.

- Fallas masivas en la ciudad piloto: Poisson con la tasa base de la configuración.
- Afectados: clientes "virtuales" muestreados del perfil sintético de la ciudad (con reemplazo).
- Probabilidad de llamar en 72 h sin aviso: modelo 72 h calibrado.
- Control: llama con prob. p. Tratamiento: si recibe el aviso (tasa de entrega), p·(1 − efecto).
- El efecto es un SUPUESTO de la simulación (`piloto.efecto_simulado`): esto no es un resultado real.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from experimento import analisis, asignacion, potencia
from ml import eventos
from ml.comun import supuesto


def perfil_ciudad(tablas: dict[str, pd.DataFrame], cfg: dict, ciudad: str) -> pd.DataFrame:
    """Variables de evento de todos los clientes de la ciudad, como si la falla empezara mañana."""
    corte = date.fromisoformat(cfg["general"]["fecha_corte"])
    fm = tablas["fallas_masivas"]
    previas = [(set(c.split(",")), date.fromisoformat(i)) for c, i in zip(fm["celdas"], fm["inicio"], strict=True)]
    cl = tablas["clientes"]
    return eventos.construir(
        cl[cl["ciudad"] == ciudad],
        tablas["celdas"].set_index("celda_id")["zona"],
        tablas["interacciones"],
        tablas["encuestas"],
        tablas["red_diaria"],
        previas,
        corte + timedelta(days=1),
        corte,
        None,
        1,
        12,
    )


def _resultado_falla(rng, n_sitios: int, eta: float | None, hora: int) -> dict:
    return {
        "n_sitios_afectados": n_sitios,
        "eta_conocida": int(eta is not None),
        "eta_horas": np.nan if eta is None else eta,
        "hora_inicio": hora,
        "es_nocturna": int(hora >= 22 or hora < 6),
    }


def simular(cfg: dict, modelo72, perfil: pd.DataFrame, semilla: int | None = None) -> dict:
    pc = cfg["piloto"]
    rng = np.random.default_rng(cfg["general"]["semilla"] + 7 if semilla is None else semilla)
    meses = pc["dias"] / 30
    n_fallas = max(1, int(rng.poisson(supuesto(cfg, "fallas_mes_piloto") * meses)))
    llamadas_por_cliente = supuesto(cfg, "llamadas_por_cliente_que_llama")
    entrega, efecto = supuesto(cfg, "tasa_entrega"), pc["efecto_simulado"]

    bloques, por_falla, contador = [], [], 0
    for f in range(n_fallas):
        n_af = max(200, int(rng.poisson(supuesto(cfg, "afectados_por_falla"))))
        eta = float(max(1, round(rng.lognormal(np.log(6), 0.6)))) if rng.random() < pc["pct_fallas_con_eta"] else None
        X = perfil.sample(n=n_af, replace=True, random_state=int(rng.integers(1_000_000_000))).copy()
        for k, v in _resultado_falla(rng, int(rng.integers(1, 6)), eta, int(rng.integers(0, 24))).items():
            X[k] = v
        ids = [f"{cid}#{contador + i}" for i, cid in enumerate(X.index)]
        contador += n_af
        p = modelo72.predict_proba(X[eventos.VARIABLES_EVENTO])[:, 1]
        control = asignacion.asignar(ids, pc["sal_asignacion"], pc["pct_control"])
        recibio = ~control & (rng.random(n_af) < entrega)
        p_final = np.where(recibio, p * (1 - efecto), p)
        llamo = rng.random(n_af) < p_final
        n_llam = np.where(llamo, 1 + rng.poisson(llamadas_por_cliente - 1, n_af), 0)
        optout = recibio & (rng.random(n_af) < pc["optout_simulado"])
        bloques.append(
            pd.DataFrame(
                {
                    "falla": f + 1,
                    "control": control,
                    "recibio": recibio,
                    "p": p,
                    "llamo": llamo,
                    "n_llamadas": n_llam,
                    "optout": optout,
                    "es_hogar": X["es_hogar"].to_numpy(),
                }
            )
        )
        por_falla.append(
            {
                "falla": f + 1,
                "afectados": n_af,
                "eta_conocida": eta is not None,
                "control_por_1000": round(float(n_llam[control].mean() * 1000), 0),
                "tratamiento_por_1000": round(float(n_llam[~control].mean() * 1000), 0),
            }
        )
    d = pd.concat(bloques, ignore_index=True)
    t, c = d[~d["control"]], d[d["control"]]

    efecto_est = analisis.comparar_medias(t["n_llamadas"].to_numpy(), c["n_llamadas"].to_numpy(), pc["alfa"])
    prop = analisis.comparar_proporciones(int(t["llamo"].sum()), len(t), int(c["llamo"].sum()), len(c), pc["alfa"])
    tasa_optout = float(t["optout"].sum() / max(t["recibio"].sum(), 1))
    decision = analisis.decidir(efecto_est, tasa_optout, pc)

    # Métricas secundarias (simuladas con supuestos explícitos)
    n_enc_t, n_enc_c = int(len(t) * 0.2), int(len(c) * 0.2)
    csat_t = float(np.clip(rng.normal(3.4, 1.1, n_enc_t), 1, 5).mean())
    csat_c = float(np.clip(rng.normal(2.9, 1.1, n_enc_c), 1, 5).mean())
    afectados = len(d)
    comp = min(
        afectados * supuesto(cfg, "pct_compensados") * supuesto(cfg, "costo_compensacion"),
        cfg["topes"]["compensaciones_mes_piloto"] * meses,
    )
    evitadas = (c["n_llamadas"].mean() - t["n_llamadas"].mean()) * len(t)

    return {
        "aviso": f"Resultado SIMULADO con un efecto supuesto de {efecto * 100:.0f} %: muestra cómo se medirá, "
        "no es un resultado real.",
        "ciudad": pc["ciudad"],
        "dias": pc["dias"],
        "fallas": n_fallas,
        "afectados": afectados,
        "efecto_supuesto": efecto,
        "metrica_norte": efecto_est,
        "pct_que_llama": prop,
        "decision": decision,
        "llamadas_evitadas_estimadas": round(float(evitadas)),
        "secundarias": {
            "csat_tratamiento": round(csat_t, 2),
            "csat_control": round(csat_c, 2),
            "csat_escala": "1 a 5 (encuesta post-falla, 20 % responde)",
            "reclamos_repetidos_tratamiento": round(float((t["n_llamadas"] >= 2).mean()), 4),
            "reclamos_repetidos_control": round(float((c["n_llamadas"] >= 2).mean()), 4),
            "minutos_al_primer_contacto_tratamiento": 15,
            "minutos_al_primer_contacto_control": "cuando el cliente llama (mediana ~3 h)",
            "tasa_optout": round(tasa_optout, 4),
            "costo_compensaciones": round(comp, -2),
            "quejas_por_mensaje": "se registran en la bitácora; meta 0",
        },
        "por_falla": por_falla,
        "potencia": potencia.plan(cfg, float(c["llamo"].mean()), afectados),
    }
