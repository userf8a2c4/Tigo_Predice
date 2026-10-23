"""Modelo del piloto (Fase 1): ¿llamará el afectado al call center en las 72 h posteriores a la falla?

Uso:  python -m ml.entrenar_72h

- Validación TEMPORAL: entrena con fallas de los días 0–59 y prueba con las de los días 60–89.
- Compara: regresión logística, LightGBM, LightGBM calibrado y la REGLA OPERATIVA.
- Reporta lo que importa al negocio: llamadas capturadas por cada 100 contactos,
  costo por llamada evitada por estrategia, calibración y sesgo por zona y segmento.
"""

from __future__ import annotations

import json
import warnings
from datetime import date

import joblib
import lightgbm as lgb
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
from ml.comun import MODELOS_DIR, REPORTES_DIR, cargar_config, supuesto, url_db
from ml.eventos import NOMBRES_VARIABLES, VARIABLES_EVENTO

warnings.filterwarnings("ignore", category=UserWarning)

DIA_CORTE_TEMPORAL = 60  # entrena con fallas antes de este día; prueba con las posteriores
PCT_PRIORIDAD = 0.20  # presupuesto de acciones caras (compensación / llamada saliente)


def lgbm(semilla: int) -> lgb.LGBMClassifier:
    return lgb.LGBMClassifier(
        n_estimators=250,
        learning_rate=0.03,
        num_leaves=7,
        min_child_samples=40,
        subsample=0.8,
        subsample_freq=1,
        colsample_bytree=0.8,
        reg_lambda=3.0,
        random_state=semilla,
        verbose=-1,
    )


def regla_operativa(X: pd.DataFrame) -> np.ndarray:
    """Lo que haría un supervisor sin modelo: primero hogar, luego pospago; más si no hay ETA."""
    return 2.0 * X["es_hogar"] + 1.0 * X["es_pospago"] + 0.5 * (1 - X["eta_conocida"]) + 0.01 * X["arpu"] / 100


def top_k(score: np.ndarray, pct: float) -> np.ndarray:
    k = max(1, int(round(len(score) * pct)))
    marca = np.zeros(len(score), dtype=bool)
    marca[np.argsort(-score, kind="stable")[:k]] = True
    return marca


def lift_deciles(y: np.ndarray, p: np.ndarray) -> list[dict]:
    orden = np.argsort(-p, kind="stable")
    base, salida, acum = y.mean(), [], 0
    for d, bloque in enumerate(np.array_split(y[orden], 10), start=1):
        acum += bloque.sum()
        salida.append(
            {
                "decil": d,
                "tasa": round(float(bloque.mean()), 4),
                "lift": round(float(bloque.mean() / base), 2),
                "captura_acumulada": round(float(acum / y.sum()), 4),
            }
        )
    return salida


def calibracion(y: np.ndarray, p: np.ndarray, bins: int = 10) -> list[dict]:
    orden = np.argsort(p)
    return [
        {"prob_media": round(float(p[b].mean()), 4), "tasa_real": round(float(y[b].mean()), 4), "n": int(len(b))}
        for b in np.array_split(orden, bins)
    ]


def metricas(y: np.ndarray, p: np.ndarray, n_llam: np.ndarray) -> dict:
    top10 = top_k(p, 0.10)
    prio = top_k(p, PCT_PRIORIDAD)
    return {
        "auc": round(float(roc_auc_score(y, p)), 3),
        "brier": round(float(brier_score_loss(y, np.clip(p, 0, 1))), 4) if p.max() <= 1 else None,
        "precision_top10": round(float(y[top10].mean()), 3),
        "recall_top10": round(float(y[top10].sum() / y.sum()), 3),
        "llamadas_por_100_contactos_top20": round(float(n_llam[prio].sum() / prio.sum() * 100), 1),
        "recall_llamadas_top20": round(float(n_llam[prio].sum() / n_llam.sum()), 3),
        "lift": lift_deciles(y, p),
    }


def estrategias(cfg: dict, n_llam: np.ndarray, scores: dict[str, np.ndarray]) -> list[dict]:
    """Costo-efectividad por estrategia sobre las fallas de prueba (valores base de la configuración)."""
    red, ent = supuesto(cfg, "reduccion_con_aviso"), supuesto(cfg, "tasa_entrega")
    c_wa, c_comp = supuesto(cfg, "costo_whatsapp_mensaje"), supuesto(cfg, "costo_compensacion")
    msgs = cfg["piloto"]["mensajes_por_afectado"]
    n = len(n_llam)
    evitadas_todos = float(n_llam.sum() * red * ent)
    salida = [
        {
            "estrategia": "Hoy: no avisar",
            "tipo": "base",
            "contactos": 0,
            "costo": 0.0,
            "llamadas_evitadas": 0.0,
            "llamadas_por_100": None,
            "costo_por_llamada_evitada": None,
        },
        {
            "estrategia": "Avisar por WhatsApp a TODOS los afectados (regla simple)",
            "tipo": "whatsapp",
            "contactos": n,
            "costo": round(n * msgs * c_wa * ent, 0),
            "llamadas_evitadas": round(evitadas_todos, 1),
            "llamadas_por_100": round(float(n_llam.sum() / n * 100), 1),
            "costo_por_llamada_evitada": round(n * msgs * c_wa * ent / evitadas_todos, 2),
        },
    ]
    # Acción cara (compensación) con presupuesto para el 20 % de los afectados
    for nombre, s in scores.items():
        m = top_k(s, PCT_PRIORIDAD)
        capt = float(n_llam[m].sum())
        costo = m.sum() * c_comp
        salida.append(
            {
                "estrategia": f"Compensar al 20 % elegido por {nombre}",
                "tipo": "prioridad",
                "contactos": int(m.sum()),
                "costo": round(costo, 0),
                "llamadas_capturadas": round(capt, 0),
                "llamadas_por_100": round(capt / m.sum() * 100, 1),
                "costo_por_llamada_capturada": round(costo / capt, 2) if capt else None,
            }
        )
    return salida


def sesgo(df: pd.DataFrame, p: np.ndarray) -> dict:
    marcado = top_k(p, PCT_PRIORIDAD)
    d = df.assign(p=p, marcado=marcado)
    salida = {}
    for dim in ("zona", "segmento"):
        filas = []
        for g, s in d.groupby(dim):
            filas.append(
                {
                    "grupo": str(g),
                    "n": int(len(s)),
                    "tasa_real": round(float(s["llamo_72h"].mean()), 3),
                    "prob_media": round(float(s["p"].mean()), 3),
                    "pct_priorizado": round(float(s["marcado"].mean()), 3),
                    "auc": round(float(roc_auc_score(s["llamo_72h"], s["p"])), 3)
                    if s["llamo_72h"].nunique() > 1
                    else None,
                }
            )
        salida[dim] = filas
    return salida


def main() -> None:
    cfg = cargar_config()
    semilla = cfg["general"]["semilla"]
    version = f"v{date.fromisoformat(cfg['general']['fecha_corte']):%Y%m%d}"
    eng = create_engine(url_db())
    ev = pd.read_sql_table("eventos_falla", eng)
    eng.dispose()

    tr, te = ev[ev["dia_inicio"] < DIA_CORTE_TEMPORAL], ev[ev["dia_inicio"] >= DIA_CORTE_TEMPORAL]
    Xtr, ytr = tr[VARIABLES_EVENTO], tr["llamo_72h"].to_numpy()
    Xte, yte, nte = te[VARIABLES_EVENTO], te["llamo_72h"].to_numpy(), te["n_llamadas_72h"].to_numpy()

    logit = make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True), StandardScaler(), LogisticRegression(max_iter=3000)
    ).fit(Xtr, ytr)
    gbm = lgbm(semilla).fit(Xtr, ytr)
    gbm_cal = CalibratedClassifierCV(lgbm(semilla), method="isotonic", cv=5).fit(Xtr, ytr)

    p = {
        "regresión logística": logit.predict_proba(Xte)[:, 1],
        "LightGBM": gbm.predict_proba(Xte)[:, 1],
        "LightGBM calibrado": gbm_cal.predict_proba(Xte)[:, 1],
    }
    regla = regla_operativa(Xte).to_numpy()
    rng = np.random.default_rng(semilla)
    azar = rng.random(len(Xte))

    res = {
        "version": version,
        "pregunta": "¿Llamará al call center en las 72 h posteriores a la falla si NO recibe aviso?",
        "validacion": f"Temporal: entrena con fallas de los días 0–{DIA_CORTE_TEMPORAL - 1} "
        f"({tr['falla_id'].nunique()} fallas, {len(tr):,} afectados) y prueba con las de los días "
        f"{DIA_CORTE_TEMPORAL}–89 ({te['falla_id'].nunique()} fallas, {len(te):,} afectados).",
        "tasa_base_prueba": round(float(yte.mean()), 3),
        "llamadas_por_1000_prueba": round(float(nte.mean() * 1000)),
        "modelos": {k: metricas(yte, v, nte) for k, v in p.items()},
        "regla_operativa": metricas(yte, regla / regla.max(), nte) | {"brier": None},
        "azar": {
            "llamadas_por_100_contactos_top20": round(
                float(nte[top_k(azar, PCT_PRIORIDAD)].sum() / top_k(azar, PCT_PRIORIDAD).sum() * 100), 1
            )
        },
        "calibracion": {
            "LightGBM": calibracion(yte, p["LightGBM"]),
            "LightGBM calibrado": calibracion(yte, p["LightGBM calibrado"]),
        },
        "estrategias": estrategias(
            cfg, nte, {"azar": azar, "la regla (hogar primero)": regla, "el modelo": p["LightGBM calibrado"]}
        ),
        "sesgo": sesgo(te.reset_index(drop=True), p["LightGBM calibrado"]),
        "importancia": [
            {"variable": v, "nombre": NOMBRES_VARIABLES[v], "valor": round(float(i), 4)}
            for v, i in sorted(
                zip(
                    VARIABLES_EVENTO,
                    gbm.booster_.feature_importance("gain") / gbm.booster_.feature_importance("gain").sum(),
                    strict=True,
                ),
                key=lambda t: -t[1],
            )[:10]
        ],
        "pct_prioridad": PCT_PRIORIDAD,
    }

    # Modelo final para producción/demo: calibrado, entrenado con TODAS las fallas resueltas
    final = CalibratedClassifierCV(lgbm(semilla), method="isotonic", cv=5).fit(ev[VARIABLES_EVENTO], ev["llamo_72h"])
    MODELOS_DIR.mkdir(parents=True, exist_ok=True)
    nombre = f"llamada72h_lgbm_cal_{version}.joblib"
    joblib.dump(final, MODELOS_DIR / nombre)
    actual_path = MODELOS_DIR / "actual.json"
    actual = json.loads(actual_path.read_text(encoding="utf-8")) if actual_path.exists() else {}
    actual["llamada_72h"] = nombre
    actual["variables_72h"] = VARIABLES_EVENTO
    actual_path.write_text(json.dumps(actual, indent=2), encoding="utf-8", newline="\n")
    (REPORTES_DIR / "metricas_72h.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n"
    )

    for k, m in res["modelos"].items():
        print(
            f"[72h] {k:22s} AUC={m['auc']:.3f} Brier={m['brier']} "
            f"llamadas/100 (top20%)={m['llamadas_por_100_contactos_top20']}"
        )
    print(
        f"[72h] regla operativa        AUC={res['regla_operativa']['auc']:.3f} "
        f"llamadas/100 (top20%)={res['regla_operativa']['llamadas_por_100_contactos_top20']}"
    )
    print(f"[72h] azar                   llamadas/100 (top20%)={res['azar']['llamadas_por_100_contactos_top20']}")
    print(res["validacion"])


if __name__ == "__main__":
    main()
    manifiesto.firmar()
