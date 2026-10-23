"""Entrena los modelos de riesgo (incidencia 7 días y churn 30 días).

Uso:  python -m ml.entrenar

1. Baseline: regresión logística.
2. Modelo principal: LightGBM.
3. Evalúa en un conjunto de prueba (25 %) y guarda métricas en reports/metricas.json.
4. Califica a todos los clientes con predicciones fuera de muestra (5 particiones)
   y guarda probabilidades + explicaciones SHAP en la tabla `puntajes`.
5. Guarda los modelos versionados en ml/modelos/.
"""

from __future__ import annotations

import json
import warnings
from datetime import date

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
import shap
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, precision_score, recall_score, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine

from ml import features, manifiesto
from ml.comun import MODELOS_DIR, REPORTES_DIR, cargar_config, url_db

OBJETIVOS = {
    "incidencia": ("llamara_7d", "Probabilidad de que llame o reclame en los próximos 7 días"),
    "churn": ("churn_30d", "Probabilidad de abandono/portabilidad en 30 días"),
}
TOP_PCT = 0.10  # se contacta al 10 % de mayor riesgo

warnings.filterwarnings("ignore", message=".*TreeExplainer shap values output has changed.*")


def params_lgbm(semilla: int) -> dict:
    return dict(
        n_estimators=300,
        learning_rate=0.03,
        num_leaves=7,
        min_child_samples=60,
        subsample=0.8,
        subsample_freq=1,
        colsample_bytree=0.8,
        reg_lambda=3.0,
        random_state=semilla,
        verbose=-1,
    )


def baseline(semilla: int):
    return make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True),
        StandardScaler(),
        LogisticRegression(max_iter=3000, random_state=semilla),
    )


def lift_por_decil(y: np.ndarray, p: np.ndarray) -> list[dict]:
    orden = np.argsort(-p)
    y_ord = y[orden]
    base = y.mean()
    salida, acumulado = [], 0
    for d, bloque in enumerate(np.array_split(y_ord, 10), start=1):
        acumulado += bloque.sum()
        salida.append(
            {
                "decil": d,
                "tasa": round(float(bloque.mean()), 4),
                "lift": round(float(bloque.mean() / base), 2),
                "captura_acumulada": round(float(acumulado / y.sum()), 4),
            }
        )
    return salida


def metricas(y: np.ndarray, p: np.ndarray) -> dict:
    umbral = float(np.quantile(p, 1 - TOP_PCT))
    pred = (p >= umbral).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
    fpr, tpr, _ = roc_curve(y, p)
    pasos = np.linspace(0, len(fpr) - 1, 40).astype(int)
    return {
        "auc": round(float(roc_auc_score(y, p)), 4),
        "umbral_top10": round(umbral, 4),
        "precision_top10": round(float(precision_score(y, pred)), 4),
        "recall_top10": round(float(recall_score(y, pred)), 4),
        "tasa_base": round(float(y.mean()), 4),
        "matriz_confusion": {"vn": int(tn), "fp": int(fp), "fn": int(fn), "vp": int(tp)},
        "lift": lift_por_decil(y, p),
        "roc": [{"fpr": round(float(fpr[i]), 4), "tpr": round(float(tpr[i]), 4)} for i in pasos],
    }


def shap_matriz(modelo: lgb.LGBMClassifier, X: pd.DataFrame) -> np.ndarray:
    sv = shap.TreeExplainer(modelo).shap_values(X)
    if isinstance(sv, list):
        sv = sv[1]
    sv = np.asarray(sv)
    return sv[..., 1] if sv.ndim == 3 else sv


def top_factores(X: pd.DataFrame, sv: np.ndarray, k: int = 3) -> list[str]:
    cols = list(X.columns)
    valores = X.to_numpy()
    salida = []
    for i in range(len(X)):
        orden = np.argsort(-sv[i])
        factores = []
        for j in orden:
            if sv[i, j] <= 0:
                break
            texto = features.explicar(cols[j], float(valores[i, j]))
            if texto:
                factores.append(
                    {
                        "variable": cols[j],
                        "grupo": features.GRUPO[cols[j]],
                        "texto": texto,
                        "impacto": round(float(sv[i, j]), 3),
                    }
                )
            if len(factores) == k:
                break
        salida.append(json.dumps(factores, ensure_ascii=False))
    return salida


def main() -> None:
    cfg = cargar_config()
    semilla = cfg["general"]["semilla"]
    corte = date.fromisoformat(cfg["general"]["fecha_corte"])
    version = f"v{corte:%Y%m%d}"
    eng = create_engine(url_db())
    tablas = features.cargar_tablas(eng)
    X = features.construir(tablas, corte)
    etiquetas = pd.read_sql_table("etiquetas", eng).set_index("cliente_id").reindex(X.index)
    clientes = tablas["clientes"].set_index("cliente_id").reindex(X.index)

    MODELOS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTES_DIR.mkdir(parents=True, exist_ok=True)
    resultado = {
        "version": version,
        "fecha_corte": corte.isoformat(),
        "n_clientes": len(X),
        "variables": features.NUMERICAS,
        "modelos": {},
    }
    puntajes = pd.DataFrame(index=X.index)

    for nombre, (col, descripcion) in OBJETIVOS.items():
        y = etiquetas[col].to_numpy()
        X_tr, X_te, y_tr, y_te, _, idx_te = train_test_split(
            X, y, np.arange(len(X)), test_size=0.25, stratify=y, random_state=semilla
        )

        base = baseline(semilla).fit(X_tr, y_tr)
        p_base = base.predict_proba(X_te)[:, 1]
        modelo = lgb.LGBMClassifier(**params_lgbm(semilla)).fit(X_tr, y_tr)
        p_lgbm = modelo.predict_proba(X_te)[:, 1]

        # Sesgo: AUC y tasa marcada vs tasa real por ciudad y segmento (en prueba)
        prueba = clientes.iloc[idx_te][["ciudad", "segmento"]].assign(y=y_te, p=p_lgbm)
        corte_top = np.quantile(p_lgbm, 1 - TOP_PCT)
        sesgo = {}
        for dim in ("ciudad", "segmento"):
            filas = []
            for grupo, g in prueba.groupby(dim):
                filas.append(
                    {
                        "grupo": grupo,
                        "n": int(len(g)),
                        "tasa_real": round(float(g["y"].mean()), 4),
                        "prob_media": round(float(g["p"].mean()), 4),
                        "pct_marcado_top10": round(float((g["p"] >= corte_top).mean()), 4),
                        "auc": round(float(roc_auc_score(g["y"], g["p"])), 3) if g["y"].nunique() > 1 else None,
                    }
                )
            sesgo[dim] = filas

        importancia = pd.Series(np.abs(shap_matriz(modelo, X_te)).mean(0), index=X.columns)
        importancia = importancia.sort_values(ascending=False).head(12)

        resultado["modelos"][nombre] = {
            "objetivo": col,
            "descripcion": descripcion,
            "baseline_regresion_logistica": metricas(y_te, p_base),
            "lightgbm": metricas(y_te, p_lgbm),
            "importancia_shap": [
                {"variable": v, "grupo": features.GRUPO[v], "valor": round(float(s), 4)} for v, s in importancia.items()
            ],
            "sesgo": sesgo,
        }
        print(
            f"[{nombre}] AUC baseline={resultado['modelos'][nombre]['baseline_regresion_logistica']['auc']:.3f} "
            f"| AUC LightGBM={resultado['modelos'][nombre]['lightgbm']['auc']:.3f}"
        )

        # Puntaje fuera de muestra para todos los clientes (nadie se califica con un modelo que lo vio)
        oof = np.zeros(len(X))
        sv_oof = np.zeros(X.shape)
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=semilla)
        for tr, te in skf.split(X, y):
            m = lgb.LGBMClassifier(**params_lgbm(semilla)).fit(X.iloc[tr], y[tr])
            oof[te] = m.predict_proba(X.iloc[te])[:, 1]
            sv_oof[te] = shap_matriz(m, X.iloc[te])
        puntajes[f"prob_{nombre}"] = np.round(oof, 5)
        puntajes[f"factores_{nombre}"] = top_factores(X, sv_oof)

        # Modelo final (todos los datos) para recalcular en vivo durante la demo
        final = lgb.LGBMClassifier(**params_lgbm(semilla)).fit(X, y)
        joblib.dump(final, MODELOS_DIR / f"{nombre}_lgbm_{version}.joblib")
        joblib.dump(base, MODELOS_DIR / f"{nombre}_logreg_{version}.joblib")

    # Se combina con el registro existente: los otros entrenamientos (72 h, Hogar) guardan sus propias claves
    actual_path = MODELOS_DIR / "actual.json"
    actual = json.loads(actual_path.read_text(encoding="utf-8")) if actual_path.exists() else {}
    actual = {
        "version": version,
        "incidencia": f"incidencia_lgbm_{version}.joblib",
        "churn": f"churn_lgbm_{version}.joblib",
        "variables": features.NUMERICAS,
    } | {k: v for k, v in actual.items() if k not in ("version", "incidencia", "churn", "variables")}
    actual_path.write_text(json.dumps(actual, indent=2), encoding="utf-8", newline="\n")
    (REPORTES_DIR / "metricas.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n"
    )

    # Features actuales y puntajes a la base (los usa el backend)
    puntajes.reset_index().to_sql("puntajes", eng, if_exists="replace", index=False)
    X.reset_index().to_sql("features", eng, if_exists="replace", index=False)
    eng.dispose()
    print(f"Modelos guardados en {MODELOS_DIR} ({version}). Métricas en {REPORTES_DIR / 'metricas.json'}")


if __name__ == "__main__":
    main()
    manifiesto.firmar()
