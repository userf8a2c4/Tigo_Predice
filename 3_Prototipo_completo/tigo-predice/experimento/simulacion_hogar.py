"""Simulación del piloto Hogar de 60 días (datos sintéticos) para mostrar CÓMO se medirá.

- Cada semana la IA califica a todos los hogares de la ciudad piloto y marca al 2 % más alto
  (presupuesto de la configuración).
- Los marcados se asignan por hash: 85 % tratamiento (acción remota + WhatsApp), 15 % control (nada).
- Resultados por hogar marcado en los 7 días siguientes: SALEN de los datos sintéticos fuera de
  muestra (semanas de prueba del modelo), con el riesgo que la IA predijo para cada hogar.
- Tratamiento: los problemas resolubles a distancia que ya existían se corrigen con probabilidad
  `exito_remoto_simulado` (desaparecen sus llamadas y visitas); en problemas físicos, el aviso evita
  la llamada del cliente con probabilidad `evita_llamada_fisico_simulado`, pero la visita sigue.
- Esos dos efectos son SUPUESTOS de la simulación: esto no es un resultado real.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from experimento import analisis, asignacion, potencia
from ml.comun import supuesto
from ml.telemetria import top_k


def marcados_ciudad(puntajes: pd.DataFrame, ciudad: str, pct: float) -> pd.DataFrame:
    """Hogares que la IA marcó cada semana de prueba en la ciudad (top `pct` por semana)."""
    sel = []
    for _, s in puntajes[puntajes["ciudad"] == ciudad].groupby("dia_corte"):
        sel.append(s[top_k(s["p"].to_numpy(), pct)])
    return pd.concat(sel, ignore_index=True)


def simular(cfg: dict, puntajes: pd.DataFrame, ia_vs_regla: float, semilla: int | None = None) -> dict:
    ch, pc = cfg["hogar"], cfg["piloto"]
    rng = np.random.default_rng(cfg["general"]["semilla"] + 11 if semilla is None else semilla)
    pct = ch["pct_marcados_semana"]
    semanas = math.ceil(pc["dias"] / 7)
    n_semana = int(round(supuesto(cfg, "hogares_piloto") * pct))
    marcados = marcados_ciudad(puntajes, pc["ciudad"], pct)
    dias_corte = sorted(marcados["dia_corte"].unique())

    bloques, por_semana, contador = [], [], 0
    for w in range(semanas):
        fuente = marcados[marcados["dia_corte"] == dias_corte[w % len(dias_corte)]]
        X = fuente.sample(n=n_semana, replace=True, random_state=int(rng.integers(1_000_000_000))).reset_index(
            drop=True
        )
        ids = [f"{h}#{contador + i}" for i, h in enumerate(X["hogar_id"])]
        contador += n_semana
        control = asignacion.asignar(ids, ch["sal_asignacion"], pc["pct_control"])
        corregido = ~control & (rng.random(n_semana) < ch["exito_remoto_simulado"])
        vis = X["visitas_7d"].to_numpy() - np.where(corregido, X["visitas_prevenibles_7d"].to_numpy(), 0)
        llam_fis = rng.binomial(X["llamadas_fisico_7d"].to_numpy(), ch["evita_llamada_fisico_simulado"])
        llam = (
            X["llamadas_7d"].to_numpy()
            - np.where(corregido, X["llamadas_prevenibles_7d"].to_numpy(), 0)
            - np.where(~control, llam_fis, 0)
        )
        optout = ~control & (rng.random(n_semana) < ch["optout_simulado"])
        bloques.append(
            pd.DataFrame(
                {"semana": w + 1, "control": control, "p": X["p"], "visitas": vis, "llamadas": llam, "optout": optout}
            )
        )
        por_semana.append(
            {
                "semana": w + 1,
                "marcados": n_semana,
                "control_por_1000": round(float(vis[control].mean() * 1000)),
                "tratamiento_por_1000": round(float(vis[~control].mean() * 1000)),
            }
        )
    d = pd.concat(bloques, ignore_index=True)
    t, c = d[~d["control"]], d[d["control"]]
    efecto = analisis.comparar_medias(t["visitas"].to_numpy(), c["visitas"].to_numpy(), pc["alfa"])
    llamadas = analisis.comparar_medias(t["llamadas"].to_numpy(), c["llamadas"].to_numpy(), pc["alfa"])
    prop = analisis.comparar_proporciones(
        int((t["visitas"] > 0).sum()), len(t), int((c["visitas"] > 0).sum()), len(c), pc["alfa"]
    )
    tasa_optout = float(t["optout"].mean())
    decision = analisis.decidir_hogar(efecto, tasa_optout, ia_vs_regla, ch, pc)
    evitadas = (c["visitas"].mean() - t["visitas"].mean()) * len(t)
    llam_evitadas = (c["llamadas"].mean() - t["llamadas"].mean()) * len(t)
    valor = evitadas * supuesto(cfg, "costo_por_visita") + llam_evitadas * supuesto(cfg, "costo_por_llamada")
    return {
        "aviso": f"Resultado SIMULADO: supone que el {ch['exito_remoto_simulado']:.0%} de los problemas resolubles a "
        "distancia se corrigen. Muestra cómo se medirá, no es un resultado real.",
        "ciudad": pc["ciudad"],
        "dias": pc["dias"],
        "semanas": semanas,
        "hogares_piloto": int(supuesto(cfg, "hogares_piloto")),
        "marcados_por_semana": n_semana,
        "marcados": len(d),
        "metrica_norte": efecto,
        "llamadas": llamadas,
        "pct_con_visita": prop,
        "decision": decision,
        "ia_vs_regla": ia_vs_regla,
        "visitas_evitadas_estimadas": round(float(evitadas)),
        "llamadas_evitadas_estimadas": round(float(llam_evitadas)),
        "valor_estimado": round(float(valor), -3),
        "secundarias": {
            "tasa_optout": round(tasa_optout, 4),
            "acciones_remotas": int((~d["control"]).sum()),
            "riesgo_medio_marcados": round(float(d["p"].mean()), 3),
        },
        "por_semana": por_semana,
        "potencia": potencia.plan(cfg, float((c["visitas"] > 0).mean()), len(d), ch["go_reduccion_visitas_min"])
        | {
            "nota": "Asume hogares marcados independientes. Como los hogares de un mismo nodo se parecen, en el piloto "
            "se usarán errores agrupados por nodo; si el poder no alcanza, se amplía el presupuesto semanal o el plazo."
        },
    }
