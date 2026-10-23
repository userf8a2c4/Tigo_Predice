"""Modelo del frente Hogar: ¿este hogar llamará por un problema técnico o necesitará una visita
en los próximos 7 días? Se califica a todos los hogares cada semana y se actúa sobre el 2 % más alto.

Uso:  python -m ml.entrenar_hogar

- Validación TEMPORAL: entrena con las semanas de los días 19–54 y prueba con las de los días 61–82.
- Compara: regresión logística, LightGBM, LightGBM calibrado, la REGLA DE UMBRALES (lo que ya
  puede alarmar un ACS/NOC sin IA) y el azar, con el mismo presupuesto semanal.
- Métrica de negocio: % de las visitas evitables que ocurren en hogares marcados a tiempo
  (captura) y visitas por cada 100 hogares marcados.
"""

from __future__ import annotations

import json
import warnings
from datetime import date

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine

from ml import manifiesto
from ml.comun import MODELOS_DIR, REPORTES_DIR, cargar_config, url_db
from ml.entrenar_72h import calibracion, lgbm, lift_deciles
from ml.telemetria import NOMBRES_HOGAR, VARIABLES_HOGAR, alarma_regla, regla, top_k

warnings.filterwarnings("ignore", category=UserWarning)

DIA_CORTE_TEMPORAL = 58  # semanas con corte antes de este día = entrenamiento


def por_semana(df: pd.DataFrame, score: np.ndarray, pct: float) -> np.ndarray:
    """Marca el top `pct` de cada semana por separado (así opera el piloto: presupuesto semanal)."""
    marca = np.zeros(len(df), dtype=bool)
    for _, idx in df.groupby("dia_corte").indices.items():
        marca[idx] = top_k(score[idx], pct)
    return marca


def metricas(df: pd.DataFrame, p: np.ndarray, pct: float) -> dict:
    y = df["evento_7d"].to_numpy()
    m = por_semana(df, p, pct)
    tot = lambda c: float(df[c].sum())  # noqa: E731
    cap = lambda c: round(float(df.loc[m, c].sum() / max(tot(c), 1)), 3)  # noqa: E731
    return {
        "auc": round(float(roc_auc_score(y, p)), 3),
        "brier": round(float(brier_score_loss(y, np.clip(p, 0, 1))), 4) if p.max() <= 1 else None,
        "marcados_por_semana": int(m.sum() / df["dia_corte"].nunique()),
        "precision": round(float(y[m].mean()), 3),
        "captura_eventos": round(float(y[m].sum() / y.sum()), 3),
        "captura_visitas": cap("visitas_7d"),
        "captura_visitas_evitables": cap("visitas_evitables_7d"),
        "captura_visitas_prevenibles": cap("visitas_prevenibles_7d"),
        "visitas_por_100_marcados": round(float(df.loc[m, "visitas_7d"].sum() / m.sum() * 100), 1),
        "visitas_evitables_por_100_marcados": round(float(df.loc[m, "visitas_evitables_7d"].sum() / m.sum() * 100), 1),
        "lift": lift_deciles(y, p),
    }


def sesgo(df: pd.DataFrame, p: np.ndarray, pct: float) -> dict:
    m = por_semana(df, p, pct)
    d = df.assign(p=p, marcado=m)
    salida = {}
    for dim in ("tecnologia", "zona"):
        filas = []
        for g, s in d.groupby(dim):
            filas.append(
                {
                    "grupo": str(g),
                    "n": int(len(s)),
                    "tasa_real": round(float(s["evento_7d"].mean()), 4),
                    "prob_media": round(float(s["p"].mean()), 4),
                    "pct_marcado": round(float(s["marcado"].mean()), 4),
                    "captura_visitas_evitables": round(
                        float(
                            s.loc[s["marcado"], "visitas_evitables_7d"].sum() / max(s["visitas_evitables_7d"].sum(), 1)
                        ),
                        3,
                    ),
                    "auc": round(float(roc_auc_score(s["evento_7d"], s["p"])), 3)
                    if s["evento_7d"].nunique() > 1
                    else None,
                }
            )
        salida[dim] = filas
    return salida


def main() -> None:
    cfg = cargar_config()
    semilla = cfg["general"]["semilla"]
    pct = cfg["hogar"]["pct_marcados_semana"]
    version = f"v{date.fromisoformat(cfg['general']['fecha_corte']):%Y%m%d}"
    eng = create_engine(url_db())
    sn = pd.read_sql_table("snapshots_hogar", eng)
    hoy = pd.read_sql_table("variables_hogar_hoy", eng)

    tr = sn[sn["dia_corte"] < DIA_CORTE_TEMPORAL].reset_index(drop=True)
    te = sn[sn["dia_corte"] >= DIA_CORTE_TEMPORAL].reset_index(drop=True)
    Xtr, ytr, Xte = tr[VARIABLES_HOGAR], tr["evento_7d"].to_numpy(), te[VARIABLES_HOGAR]

    logit = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=3000)).fit(
        Xtr, ytr
    )
    gbm = lgbm(semilla).fit(Xtr, ytr)
    gbm_cal = CalibratedClassifierCV(lgbm(semilla), method="isotonic", cv=5).fit(Xtr, ytr)
    p = {
        "regresión logística": logit.predict_proba(Xte)[:, 1],
        "LightGBM": gbm.predict_proba(Xte)[:, 1],
        "LightGBM calibrado": gbm_cal.predict_proba(Xte)[:, 1],
    }
    r = regla(Xte)
    azar = np.random.default_rng(semilla).random(len(te))

    ia = metricas(te, p["LightGBM calibrado"], pct)
    reg = metricas(te, r / r.max(), pct) | {"brier": None}
    # ¿Cuántas de las visitas evitables que la IA anticipó aún no tenían NINGUNA alarma de umbral?
    m_ia = por_semana(te, p["LightGBM calibrado"], pct)
    sin_alarma = ~alarma_regla(Xte)
    ev = te["visitas_evitables_7d"].to_numpy()
    temprana = float(ev[m_ia & sin_alarma].sum() / max(ev[m_ia].sum(), 1))

    res = {
        "version": version,
        "pregunta": "¿Este hogar llamará por un problema técnico o necesitará una visita en los próximos 7 días?",
        "validacion": f"Temporal: entrena con {tr['dia_corte'].nunique()} semanas (días 19–{DIA_CORTE_TEMPORAL - 4}, "
        f"{len(tr):,} hogar-semana) y prueba con las {te['dia_corte'].nunique()} siguientes "
        f"(días {DIA_CORTE_TEMPORAL + 3}–82, {len(te):,} hogar-semana).",
        "presupuesto": pct,
        "tasa_base_prueba": round(float(te["evento_7d"].mean()), 4),
        "visitas_por_1000_prueba": round(float(te["visitas_7d"].mean() * 1000), 1),
        "pct_visitas_evitables_prueba": round(
            float(te["visitas_evitables_7d"].sum() / max(te["visitas_7d"].sum(), 1)), 3
        ),
        "modelos": {k: metricas(te, v, pct) for k, v in p.items()},
        "regla_umbrales": reg,
        "umbrales": {
            "margen_min_7d": "margen de señal < 3 dB",
            "reinicios_7d": "≥ 5 reinicios en 7 días",
            "desconexiones_7d": "≥ 15 micro-cortes en 7 días",
            "retrans_7d": "retransmisiones WiFi > 25 %",
        },
        "azar": metricas(te, azar, pct) | {"auc": 0.5, "brier": None},
        "ia_vs_regla": round(ia["captura_visitas_evitables"] / max(reg["captura_visitas_evitables"], 1e-9), 2),
        "deteccion_temprana": round(temprana, 3),
        "calibracion": {
            "LightGBM": calibracion(te["evento_7d"].to_numpy(), p["LightGBM"]),
            "LightGBM calibrado": calibracion(te["evento_7d"].to_numpy(), p["LightGBM calibrado"]),
        },
        "sesgo": sesgo(te, p["LightGBM calibrado"], pct),
        "importancia": [
            {"variable": v, "nombre": NOMBRES_HOGAR[v], "valor": round(float(i), 4)}
            for v, i in sorted(
                zip(
                    VARIABLES_HOGAR,
                    gbm.booster_.feature_importance("gain") / gbm.booster_.feature_importance("gain").sum(),
                    strict=True,
                ),
                key=lambda t: -t[1],
            )[:10]
        ],
    }

    # Modelo final (calibrado) + explicador (LightGBM sin calibrar, para contribuciones SHAP)
    final = CalibratedClassifierCV(lgbm(semilla), method="isotonic", cv=5).fit(sn[VARIABLES_HOGAR], sn["evento_7d"])
    explicador = lgbm(semilla).fit(sn[VARIABLES_HOGAR], sn["evento_7d"])
    MODELOS_DIR.mkdir(parents=True, exist_ok=True)
    nombres = {"hogar": f"hogar_lgbm_cal_{version}.joblib", "hogar_explicador": f"hogar_lgbm_{version}.joblib"}
    joblib.dump(final, MODELOS_DIR / nombres["hogar"])
    joblib.dump(explicador, MODELOS_DIR / nombres["hogar_explicador"])
    actual_path = MODELOS_DIR / "actual.json"
    actual = json.loads(actual_path.read_text(encoding="utf-8")) if actual_path.exists() else {}
    actual |= nombres | {"variables_hogar": VARIABLES_HOGAR}
    actual_path.write_text(json.dumps(actual, indent=2), encoding="utf-8", newline="\n")
    (REPORTES_DIR / "metricas_hogar.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n"
    )

    # Puntajes fuera de muestra (semanas de prueba) para simular el piloto, y puntajes de hoy
    cols = [
        "hogar_id",
        "dia_corte",
        "ciudad",
        "evento_7d",
        "llamadas_7d",
        "visitas_7d",
        "visitas_evitables_7d",
        "llamadas_prevenibles_7d",
        "visitas_prevenibles_7d",
        "llamadas_fisico_7d",
    ]
    punt = te[cols].assign(p=p["LightGBM calibrado"], regla=r)
    p_hoy = final.predict_proba(hoy[VARIABLES_HOGAR])[:, 1]
    punt_hoy = pd.DataFrame(
        {"hogar_id": hoy["hogar_id"], "p": p_hoy, "regla": regla(hoy[VARIABLES_HOGAR]), "marcado": top_k(p_hoy, pct)}
    )
    punt.to_sql("puntajes_hogar", eng, index=False, if_exists="replace")
    punt_hoy.to_sql("puntajes_hogar_hoy", eng, index=False, if_exists="replace")
    eng.dispose()

    for k, m in res["modelos"].items():
        print(
            f"[hogar] {k:20s} AUC={m['auc']:.3f} Brier={m['brier']} precisión={m['precision']:.2f} "
            f"captura visitas evitables={m['captura_visitas_evitables']:.0%} "
            f"visitas/100={m['visitas_por_100_marcados']}"
        )
    for k in ("regla_umbrales", "azar"):
        m = res[k]
        print(
            f"[hogar] {k:20s} AUC={m['auc']:.3f} precisión={m['precision']:.2f} "
            f"captura visitas evitables={m['captura_visitas_evitables']:.0%} "
            f"visitas/100={m['visitas_por_100_marcados']}"
        )
    print(f"[hogar] IA vs regla: {res['ia_vs_regla']}× · detección temprana: {res['deteccion_temprana']:.0%}")
    print(res["validacion"])


if __name__ == "__main__":
    main()
    manifiesto.firmar()
