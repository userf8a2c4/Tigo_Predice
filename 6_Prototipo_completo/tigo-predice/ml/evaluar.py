"""Genera reports/modelo.md a partir de reports/metricas_hogar.json, metricas_72h.json y metricas.json.

Uso:  python -m ml.evaluar
"""

from __future__ import annotations

import json

from ml.comun import REPORTES_DIR

NOMBRES = {
    "incidencia": "Fase 2 · Riesgo de incidencia general (llamará en 7 días)",
    "churn": "Fase 2 · Riesgo de churn (abandono en 30 días)",
}


def reporte_hogar(m: dict) -> str:
    """Sección principal (v03): el modelo del frente Hogar, medido contra la regla de umbrales."""
    mods = m["modelos"] | {"regla de umbrales": m["regla_umbrales"], "azar": m["azar"]}
    filas = [
        {
            "modelo": k,
            "auc": v["auc"],
            "brier": v["brier"],
            "prec": v["precision"],
            "cap": v["captura_eventos"],
            "cap_ev": v["captura_visitas_evitables"],
            "v100": v["visitas_por_100_marcados"],
        }
        for k, v in mods.items()
    ]
    ia = m["modelos"]["LightGBM calibrado"]
    L = [
        "# Reporte del modelo — Tigo Predice v03",
        "",
        "> ⚠️ **Datos simulados.** Las métricas muestran cómo se evaluará el modelo; con 3 meses de telemetría real",
        "> de Tigo se recalculan antes del piloto (análisis retrospectivo).",
        "",
        "## Frente Hogar · ¿llamará por un problema técnico o necesitará visita en los próximos 7 días?",
        "",
        f"**Validación:** {m['validacion']}",
        f"Presupuesto: cada semana se actúa sobre el **{m['presupuesto']:.0%}** de hogares con más riesgo. "
        f"En prueba: {m['tasa_base_prueba']:.1%} de hogares llama o necesita visita en 7 días · "
        f"{m['visitas_por_1000_prueba']:.0f} visitas por 1,000 hogares · {m['pct_visitas_evitables_prueba']:.0%} "
        "de las visitas son evitables.",
        "",
        "### IA vs. regla de umbrales vs. azar (mismo presupuesto semanal)",
        "",
    ]
    L += _tabla(
        filas,
        [
            ("modelo", "Estrategia"),
            ("auc", "AUC"),
            ("brier", "Brier (↓ mejor)"),
            ("prec", "Precisión"),
            ("cap", "Captura de eventos"),
            ("cap_ev", "Captura de visitas evitables"),
            ("v100", "Visitas por 100 marcados"),
        ],
    )
    L += [
        "",
        "Regla de umbrales: " + " · ".join(m["umbrales"].values()) + ".",
        "",
        "**Lectura honesta:**",
        f"- Con el mismo presupuesto, la IA anticipa **{ia['captura_visitas_evitables']:.0%}** de las visitas "
        f"evitables y la regla **{m['regla_umbrales']['captura_visitas_evitables']:.0%}**: "
        f"**{m['ia_vs_regla']:.1f}×**.",
        f"- **{m['deteccion_temprana']:.0%}** de las visitas que la IA anticipó todavía no tenían ninguna alarma de "
        "umbral: la IA ve tendencias (señal que baja, WiFi que empeora, vecinos con cortes).",
        "- Una regresión logística sencilla rinde cerca de LightGBM: se puede empezar simple y auditable.",
        "- Criterio del piloto: si con datos reales la IA no supera a la regla por 1.3×, se usa la regla.",
        "",
        "### Calibración (LightGBM calibrado, isotónica)",
        "",
    ]
    L += _tabla(
        m["calibracion"]["LightGBM calibrado"],
        [("prob_media", "Probabilidad media"), ("tasa_real", "Tasa real"), ("n", "n")],
    )
    L += ["", "### Sesgo: ¿se descuida a algún grupo?", ""]
    for dim, nombre in (("tecnologia", "Tecnología"), ("zona", "Zona")):
        L += _tabla(
            m["sesgo"][dim],
            [
                ("grupo", nombre),
                ("n", "n"),
                ("tasa_real", "Tasa real"),
                ("prob_media", "Prob. media"),
                ("pct_marcado", "% marcado"),
                ("captura_visitas_evitables", "Captura de evitables"),
                ("auc", "AUC"),
            ],
        )
        L.append("")
    L += ["### Variables más influyentes (ganancia LightGBM)", ""]
    L += _tabla(m["importancia"], [("nombre", "Variable"), ("valor", "Importancia")])
    L += ["", "---", ""]
    return "\n".join(L) + "\n"


def reporte_72h(m: dict) -> str:
    """Sección principal: el modelo del piloto de fallas masivas (72 h)."""
    mods = m["modelos"] | {"regla operativa": m["regla_operativa"]}
    filas = [
        {
            "modelo": k,
            "auc": v["auc"],
            "brier": v["brier"],
            "p10": v["precision_top10"],
            "r10": v["recall_top10"],
            "l100": v["llamadas_por_100_contactos_top20"],
        }
        for k, v in mods.items()
    ]
    filas.append({"modelo": "azar", "auc": 0.5, "l100": m["azar"]["llamadas_por_100_contactos_top20"]})
    L = [
        "## Frente Móvil · Fallas masivas: ¿llamará en las 72 h posteriores a la falla?",
        "",
        f"**Validación:** {m['validacion']}",
        f"Tasa base en prueba: **{m['tasa_base_prueba']:.0%}** de afectados llama · "
        f"**{m['llamadas_por_1000_prueba']:,} llamadas por cada 1,000 afectados**.",
        "",
        "### Modelo vs. regla operativa vs. azar (fallas de prueba)",
        "",
    ]
    L += _tabla(
        filas,
        [
            ("modelo", "Estrategia de orden"),
            ("auc", "AUC"),
            ("brier", "Brier (↓ mejor)"),
            ("p10", "Precisión top 10 %"),
            ("r10", "Recall top 10 %"),
            ("l100", f"Llamadas capturadas por 100 contactos (top {m['pct_prioridad']:.0%})"),
        ],
    )
    L += [
        "",
        "**Lectura honesta:**",
        "- El modelo ordena mejor que la regla operativa y mucho mejor que el azar, pero la mejora sobre una "
        "regresión logística simple es pequeña: un modelo sencillo es suficiente para empezar.",
        "- Para el **aviso por WhatsApp** (barato) la mejor estrategia es **avisar a todos los afectados**: no hace "
        "falta un modelo para eso.",
        "- El modelo aporta valor para **priorizar acciones caras** (compensaciones, llamadas salientes) cuando el "
        "presupuesto no alcanza para todos.",
        "",
        "### Costo-efectividad por estrategia (valores base de la configuración)",
        "",
    ]
    est = []
    for e in m["estrategias"]:
        est.append(
            {
                "e": e["estrategia"],
                "c": e["contactos"],
                "costo": e["costo"],
                "ev": e.get("llamadas_evitadas", e.get("llamadas_capturadas")),
                "l100": e.get("llamadas_por_100"),
                "cxl": e.get("costo_por_llamada_evitada", e.get("costo_por_llamada_capturada")),
            }
        )
    L += _tabla(
        est,
        [
            ("e", "Estrategia"),
            ("c", "Contactos"),
            ("costo", "Costo (L)"),
            ("ev", "Llamadas evitadas / capturadas"),
            ("l100", "Llamadas por 100 contactos"),
            ("cxl", "Costo por llamada (L)"),
        ],
    )
    L += ["", "### Calibración (LightGBM calibrado, isotónica)", ""]
    L += _tabla(
        m["calibracion"]["LightGBM calibrado"],
        [("prob_media", "Probabilidad media predicha"), ("tasa_real", "Tasa real"), ("n", "Afectados")],
    )
    L += ["", "### Sesgo: % priorizado vs. tasa real", ""]
    for dim in ("zona", "segmento"):
        L += [f"**Por {dim}:**", ""]
        L += _tabla(
            m["sesgo"][dim],
            [
                ("grupo", dim.capitalize()),
                ("n", "Afectados"),
                ("tasa_real", "Tasa real"),
                ("prob_media", "Prob. media"),
                ("pct_priorizado", "% priorizado"),
                ("auc", "AUC"),
            ],
        )
        L.append("")
    L += ["### Variables más influyentes (ganancia LightGBM)", ""]
    L += _tabla(m["importancia"], [("nombre", "Variable"), ("valor", "Peso relativo")])
    L += ["", "---", ""]
    return "\n".join(L)


def _tabla(filas: list[dict], columnas: list[tuple[str, str]]) -> list[str]:
    salida = ["| " + " | ".join(t for _, t in columnas) + " |", "|" + "---|" * len(columnas)]
    for f in filas:
        salida.append("| " + " | ".join(_fmt(f.get(c)) for c, _ in columnas) + " |")
    return salida


def _fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        a = abs(v)
        if a == 0:
            return "0"
        if a < 1:
            return f"{v:.3f}"
        if a < 10 and isinstance(v, float):
            return f"{v:.2f}"
        return f"{v:,.0f}"
    return str(v)


def generar_reporte(m: dict) -> str:
    L = [
        "## Fase 2 (visión, NO entra al caso base) · Modelos de 7 y 30 días",
        "",
        f"**Versión:** `{m['version']}` · **Fecha de corte:** {m['fecha_corte']} · "
        f"**Clientes:** {m['n_clientes']:,} · **Variables:** {len(m['variables'])}",
        "",
        "> Validación con partición aleatoria y predicciones fuera de muestra (5 particiones). En Fase 2 se",
        "> pasará a validación temporal como la del modelo de 72 h.",
        "",
        "### Resumen Fase 2",
        "",
    ]
    resumen = []
    for nombre, mod in m["modelos"].items():
        b, g = mod["baseline_regresion_logistica"], mod["lightgbm"]
        resumen.append(
            {
                "modelo": NOMBRES[nombre],
                "auc_base": b["auc"],
                "auc_lgbm": g["auc"],
                "prec": g["precision_top10"],
                "rec": g["recall_top10"],
                "lift": g["lift"][0]["lift"],
                "tasa": g["tasa_base"],
            }
        )
    L += _tabla(
        resumen,
        [
            ("modelo", "Modelo"),
            ("auc_base", "AUC baseline (reg. logística)"),
            ("auc_lgbm", "AUC LightGBM"),
            ("tasa", "Tasa base"),
            ("prec", "Precisión top 10 %"),
            ("rec", "Recall top 10 %"),
            ("lift", "Lift decil 1"),
        ],
    )
    L += [
        "",
        "**Cómo leerlo:** si contactamos solo al 10 % de clientes con mayor riesgo, "
        "encontramos varias veces más casos reales que contactando al azar (lift).",
        "",
    ]

    for nombre, mod in m["modelos"].items():
        g = mod["lightgbm"]
        cm = g["matriz_confusion"]
        L += [
            f"## {NOMBRES[nombre]}",
            "",
            f"_{mod['descripcion']}_",
            "",
            "### Matriz de confusión (LightGBM, umbral = top 10 % de riesgo)",
            "",
            "| | Predicho: no | Predicho: sí |",
            "|---|---|---|",
            f"| **Real: no** | {cm['vn']:,} | {cm['fp']:,} |",
            f"| **Real: sí** | {cm['fn']:,} | {cm['vp']:,} |",
            "",
            "### Curva de lift por decil",
            "",
        ]
        L += _tabla(
            g["lift"],
            [
                ("decil", "Decil"),
                ("tasa", "Tasa real"),
                ("lift", "Lift"),
                ("captura_acumulada", "% capturado acumulado"),
            ],
        )
        L += ["", "### Variables más influyentes (SHAP promedio)", ""]
        L += _tabla(mod["importancia_shap"], [("variable", "Variable"), ("grupo", "Grupo"), ("valor", "Impacto")])
        L += [
            "",
            "### Revisión de sesgo por zona y segmento",
            "",
            "Se compara el % de clientes marcados (top 10 %) con la tasa real del grupo. "
            "Un grupo marcado muy por encima de su riesgo real indicaría sesgo.",
            "",
        ]
        for dim in ("ciudad", "segmento"):
            L += [f"**Por {dim}:**", ""]
            L += _tabla(
                mod["sesgo"][dim],
                [
                    ("grupo", dim.capitalize()),
                    ("n", "Clientes (prueba)"),
                    ("tasa_real", "Tasa real"),
                    ("prob_media", "Prob. media"),
                    ("pct_marcado_top10", "% marcado"),
                    ("auc", "AUC"),
                ],
            )
            L.append("")
    L += [
        "### Metodología (Fase 2)",
        "",
        "- Partición estratificada 75 % entrenamiento / 25 % prueba (semilla fija).",
        "- Baseline: regresión logística con imputación y estandarización.",
        "- Modelo principal: LightGBM (árboles de gradiente) regularizado.",
        "- Puntajes del tablero: predicciones fuera de muestra con validación cruzada de 5 particiones "
        "(ningún cliente se califica con un modelo que lo vio).",
        "- Explicaciones: valores SHAP por cliente traducidos a lenguaje natural (3 factores principales).",
        "- Reproducible: `tareas.ps1 datos` → `tareas.ps1 entrenar` → `tareas.ps1 evaluar`.",
        "",
    ]
    return "\n".join(L)


def main() -> None:
    m = json.loads((REPORTES_DIR / "metricas.json").read_text(encoding="utf-8"))
    m72 = json.loads((REPORTES_DIR / "metricas_72h.json").read_text(encoding="utf-8"))
    mh = json.loads((REPORTES_DIR / "metricas_hogar.json").read_text(encoding="utf-8"))
    (REPORTES_DIR / "modelo.md").write_text(
        reporte_hogar(mh) + reporte_72h(m72) + generar_reporte(m), encoding="utf-8", newline="\n"
    )
    print(f"Reporte escrito en {REPORTES_DIR / 'modelo.md'}")


if __name__ == "__main__":
    main()
