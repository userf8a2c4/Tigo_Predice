"""Caso de negocio conservador y defendible (v03: frente Hogar + frente Móvil).

- Caso base = SOLO beneficio duro:
    Móvil: llamadas evitadas × costo por llamada (fallas masivas de red).
    Hogar: visitas técnicas evitadas × (costo por visita + llamadas asociadas × costo por llamada).
- El frente Móvil carga los costos de la plataforma; el frente Hogar suma solo sus costos incrementales.
- Retención = "potencial no incluido", con margen de contribución y solo el efecto incremental vs. control.
- Escenarios: conservador = efectos bajos y costos altos; optimista = lo contrario. El volumen y los costos
  unitarios (datos que Tigo ya tiene) quedan en su valor base; su incertidumbre se ve en el tornado.
- Sensibilidad (tornado) y punto de equilibrio por frente.
Una sola fuente de verdad: config/negocio.toml. La usan la API, los tests y docs/impacto.md.
"""

from __future__ import annotations

import json
import math

from ml.comun import NIVELES, REPORTES_DIR, supuestos_nivel

# Supuestos que, al subir, AUMENTAN el beneficio neto (el resto lo reduce)
A_FAVOR = {
    "fallas_mes_piloto",
    "afectados_por_falla",
    "afectados_mes_nacional",
    "tasa_llamada_72h",
    "llamadas_por_cliente_que_llama",
    "reduccion_con_aviso",
    "tasa_entrega",
    "costo_por_llamada",
    "hogares_piloto",
    "tasa_visitas_hogar_mes",
    "pct_visitas_evitables",
    "llamadas_por_visita",
    "captura_modelo_hogar",
    "reduccion_visitas_marcados",
    "costo_por_visita",
}
NEUTROS = {"tipo_cambio", "margen_contribucion", "churn_incremental_evitado", "arpu_afectado"}
# Datos que Tigo ya tiene ("Pon tus números"): en los escenarios quedan en su valor base.
VOLUMEN = {
    "fallas_mes_piloto",
    "afectados_por_falla",
    "afectados_mes_nacional",
    "tasa_llamada_72h",
    "llamadas_por_cliente_que_llama",
    "costo_por_llamada",
    "hogares_piloto",
    "tasa_visitas_hogar_mes",
    "pct_visitas_evitables",
    "llamadas_por_visita",
    "costo_por_visita",
}
# Solo afectan al piloto (no entran al tornado del neto nacional)
SOLO_PILOTO = {
    "fallas_mes_piloto",
    "afectados_por_falla",
    "desarrollo_piloto",
    "equipo_piloto",
    "hogares_piloto",
    "desarrollo_hogar_piloto",
    "equipo_hogar_piloto",
}
ESCENARIOS = {"conservador": ("bajo", "alto"), "base": ("base", "base"), "optimista": ("alto", "bajo")}
TUS_NUMEROS = ("llamadas_mes_fallas_nacional", "costo_por_llamada", "visitas_mes_hogar_nacional", "costo_por_visita")
# Qué supuesto reemplaza cada dato de Tigo (para no moverlo en el tornado)
REEMPLAZA = {
    "costo_por_llamada": "costo_por_llamada",
    "llamadas_mes_fallas_nacional": "afectados_mes_nacional",
    "costo_por_visita": "costo_por_visita",
    "visitas_mes_hogar_nacional": "tasa_visitas_hogar_mes",
}


def _valores(cfg: dict, escenario: str) -> dict[str, float]:
    nivel_favor, nivel_contra = ESCENARIOS[escenario]
    favor, contra, base = supuestos_nivel(cfg, nivel_favor), supuestos_nivel(cfg, nivel_contra), supuestos_nivel(cfg)
    return {k: (base[k] if k in NEUTROS | VOLUMEN else favor[k] if k in A_FAVOR else contra[k]) for k in base}


def sig(v: float, cifras: int = 2) -> float:
    """Redondea a N cifras significativas (evita la falsa precisión)."""
    if v == 0 or not math.isfinite(v):
        return v
    return round(v, cifras - 1 - int(math.floor(math.log10(abs(v)))))


def _movil(cfg: dict, s: dict, tus: dict, fuentes: dict) -> dict:
    """Frente Móvil: aviso proactivo en fallas masivas de red (carga los costos de la plataforma)."""
    pc = cfg["piloto"]
    llamadas_por_afectado = s["tasa_llamada_72h"] * s["llamadas_por_cliente_que_llama"]
    msgs, c_wa = pc["mensajes_por_afectado"], s["costo_whatsapp_mensaje"]
    efecto_tratado = s["tasa_entrega"] * s["reduccion_con_aviso"]

    meses_p, trat_p = pc["dias"] / 30, 1 - pc["pct_control"]
    afectados_p = s["fallas_mes_piloto"] * s["afectados_por_falla"] * meses_p
    llamadas_p = afectados_p * llamadas_por_afectado
    evitadas_p = llamadas_p * trat_p * efecto_tratado
    costos_p = {
        "desarrollo_integracion": s["desarrollo_piloto"],
        "equipo_piloto": s["equipo_piloto"],
        "infraestructura": s["infraestructura_mes"] * meses_p,
        "whatsapp": afectados_p * trat_p * msgs * c_wa,
        "compensaciones": min(
            afectados_p * trat_p * s["pct_compensados"] * s["costo_compensacion"],
            cfg["topes"]["compensaciones_mes_piloto"] * meses_p,
        ),
    }
    costo_p = sum(costos_p.values())
    beneficio_p = evitadas_p * s["costo_por_llamada"]

    trat_n = 1 - pc["holdout_escala"]
    if "llamadas_mes_fallas_nacional" in tus:
        llamadas_mes_n = tus["llamadas_mes_fallas_nacional"]
        afectados_mes_n = llamadas_mes_n / llamadas_por_afectado
        fuentes["llamadas_mes_fallas_nacional"] = "dato Tigo"
    else:
        afectados_mes_n = s["afectados_mes_nacional"]
        llamadas_mes_n = afectados_mes_n * llamadas_por_afectado
    evitadas_n = llamadas_mes_n * 12 * trat_n * efecto_tratado
    beneficio_n = evitadas_n * s["costo_por_llamada"]
    recurrentes = {
        "operacion_y_mantenimiento": s["operacion_anual"],
        "infraestructura": s["infraestructura_mes"] * 12,
        "whatsapp": afectados_mes_n * 12 * trat_n * msgs * c_wa,
        "compensaciones": min(
            afectados_mes_n * 12 * trat_n * s["pct_compensados"] * s["costo_compensacion"],
            cfg["topes"]["compensaciones_mes_nacional"] * 12,
        ),
    }
    costo_rec = sum(recurrentes.values())
    inversion = s["desarrollo_nacional"]
    valor_por_punto = llamadas_mes_n * 12 * trat_n * s["tasa_entrega"] * s["costo_por_llamada"]
    return {
        "piloto": {
            "afectados": afectados_p,
            "llamadas_sin_aviso": llamadas_p,
            "llamadas_evitadas": evitadas_p,
            "beneficio_duro": beneficio_p,
            "costos": costos_p,
            "costo_total": costo_p,
            "neto": beneficio_p - costo_p,
            "equilibrio_reduccion": costo_p / (llamadas_p * trat_p * s["tasa_entrega"] * s["costo_por_llamada"]),
        },
        "nacional": {
            "afectados_mes": afectados_mes_n,
            "llamadas_mes_por_fallas": llamadas_mes_n,
            "llamadas_evitadas_anio": evitadas_n,
            "beneficio_duro_anio": beneficio_n,
            "costos_recurrentes": recurrentes,
            "costo_recurrente_anio": costo_rec,
            "inversion_unica": inversion,
            "neto_anio1": beneficio_n - costo_rec - inversion,
            "neto_regimen_anio": beneficio_n - costo_rec,
            "equilibrio_reduccion_anio1": (costo_rec + inversion) / valor_por_punto if valor_por_punto else None,
            "equilibrio_reduccion_regimen": costo_rec / valor_por_punto if valor_por_punto else None,
        },
    }


def _hogar(cfg: dict, s: dict, tus: dict, fuentes: dict) -> dict:
    """Frente Hogar: la IA marca hogares que van a fallar y se corrigen a distancia (costos incrementales)."""
    ch, pc = cfg["hogar"], cfg["piloto"]
    c_wa, msgs = s["costo_whatsapp_mensaje"], ch["mensajes_por_marcado"]
    valor_visita = s["costo_por_visita"] + s["llamadas_por_visita"] * s["costo_por_llamada"]
    alcance = s["pct_visitas_evitables"] * s["captura_modelo_hogar"]  # visitas que la IA puede tocar
    efecto = alcance * s["reduccion_visitas_marcados"]  # reducción sobre el TOTAL de visitas

    meses_p, semanas_p, trat_p = pc["dias"] / 30, pc["dias"] / 7, 1 - pc["pct_control"]
    visitas_p = s["hogares_piloto"] * s["tasa_visitas_hogar_mes"] * meses_p
    evitadas_p = visitas_p * trat_p * efecto
    marcados_p = s["hogares_piloto"] * ch["pct_marcados_semana"] * semanas_p
    costos_p = {
        "desarrollo_hogar": s["desarrollo_hogar_piloto"],
        "equipo_hogar": s["equipo_hogar_piloto"],
        "whatsapp_hogar": marcados_p * trat_p * msgs * c_wa,
    }
    costo_p = sum(costos_p.values())
    beneficio_p = evitadas_p * valor_visita

    trat_n = 1 - pc["holdout_escala"]
    hogares_n = float(cfg["base_real"]["clientes_hogar"])
    if "visitas_mes_hogar_nacional" in tus:
        visitas_mes_n = tus["visitas_mes_hogar_nacional"]
        fuentes["visitas_mes_hogar_nacional"] = "dato Tigo"
    else:
        visitas_mes_n = hogares_n * s["tasa_visitas_hogar_mes"]
    evitadas_n = visitas_mes_n * 12 * trat_n * efecto
    beneficio_n = evitadas_n * valor_visita
    marcados_n = hogares_n * ch["pct_marcados_semana"] * 52
    recurrentes = {
        "operacion_hogar": s["operacion_hogar_anual"],
        "whatsapp_hogar": marcados_n * trat_n * msgs * c_wa,
    }
    costo_rec = sum(recurrentes.values())
    inversion = s["desarrollo_hogar_nacional"]
    valor_por_punto = visitas_mes_n * 12 * trat_n * alcance * valor_visita
    return {
        "piloto": {
            "hogares": s["hogares_piloto"],
            "marcados": marcados_p,
            "visitas": visitas_p,
            "visitas_evitadas": evitadas_p,
            "llamadas_evitadas": evitadas_p * s["llamadas_por_visita"],
            "beneficio_duro": beneficio_p,
            "costos": costos_p,
            "costo_total": costo_p,
            "neto": beneficio_p - costo_p,
            "equilibrio_reduccion": costo_p / (visitas_p * trat_p * alcance * valor_visita),
        },
        "nacional": {
            "hogares": hogares_n,
            "visitas_mes": visitas_mes_n,
            "marcados_anio": marcados_n,
            "valor_por_visita": valor_visita,
            "reduccion_total_visitas": efecto,
            "visitas_evitadas_anio": evitadas_n,
            "llamadas_evitadas_anio": evitadas_n * s["llamadas_por_visita"],
            "beneficio_duro_anio": beneficio_n,
            "costos_recurrentes": recurrentes,
            "costo_recurrente_anio": costo_rec,
            "inversion_unica": inversion,
            "neto_anio1": beneficio_n - costo_rec - inversion,
            "neto_regimen_anio": beneficio_n - costo_rec,
            "equilibrio_reduccion_anio1": (costo_rec + inversion) / valor_por_punto if valor_por_punto else None,
            "equilibrio_reduccion_regimen": costo_rec / valor_por_punto if valor_por_punto else None,
        },
    }


def calcular(cfg: dict, escenario: str = "base", tus_numeros: dict | None = None, valores: dict | None = None) -> dict:
    s = dict(valores) if valores is not None else _valores(cfg, escenario)
    pc = cfg["piloto"]
    fuentes = {k: v["fuente"] for k, v in cfg["supuestos"].items()}
    tus = {k: float(v) for k, v in (tus_numeros or {}).items() if k in TUS_NUMEROS and v not in (None, "")}
    for k in ("costo_por_llamada", "costo_por_visita"):
        if k in tus:
            s[k] = tus[k]
            fuentes[k] = "dato Tigo"
    mov, hog = _movil(cfg, s, tus, fuentes), _hogar(cfg, s, tus, fuentes)

    # ------------------------------------------------------------------ totales (ambos frentes)
    mp, hp, mn, hn = mov["piloto"], hog["piloto"], mov["nacional"], hog["nacional"]
    costo_p = mp["costo_total"] + hp["costo_total"]
    beneficio_p = mp["beneficio_duro"] + hp["beneficio_duro"]
    beneficio_n = mn["beneficio_duro_anio"] + hn["beneficio_duro_anio"]
    costo_rec = mn["costo_recurrente_anio"] + hn["costo_recurrente_anio"]
    inversion = mn["inversion_unica"] + hn["inversion_unica"]
    neto_regimen = beneficio_n - costo_rec

    # -------------------------------- potencial NO incluido en el caso base (retención, frente móvil)
    trat_n = 1 - pc["holdout_escala"]
    retenidos = mn["afectados_mes"] * 12 * trat_n * s["tasa_entrega"] * s["churn_incremental_evitado"]
    potencial_retencion = retenidos * s["arpu_afectado"] * s["margen_contribucion"] * 12

    return {
        "escenario": escenario,
        "supuestos": s,
        "fuentes": fuentes,
        "tus_numeros": tus,
        "movil": mov,
        "hogar": hog,
        "piloto": {
            "ciudad": pc["ciudad"],
            "dias": pc["dias"],
            "costos": mp["costos"] | hp["costos"],
            "costo_total": costo_p,
            "beneficio_duro": beneficio_p,
            "neto": beneficio_p - costo_p,
        },
        "nacional": {
            "beneficio_duro_anio": beneficio_n,
            "costos_recurrentes": mn["costos_recurrentes"] | hn["costos_recurrentes"],
            "costo_recurrente_anio": costo_rec,
            "inversion_unica": inversion,
            "neto_anio1": neto_regimen - inversion,
            "neto_regimen_anio": neto_regimen,
            "roi_anio1": (neto_regimen - inversion) / (costo_rec + inversion),
            "payback_meses": inversion / (neto_regimen / 12) if neto_regimen > 0 else None,
        },
        "potencial_no_incluido": {
            "clientes_retenidos_anio": retenidos,
            "margen_retenido_anio": potencial_retencion,
            "nota": "Solo se acredita si el piloto mide menos churn en tratados que en control; "
            "se calcula con margen de contribución, no con ingreso bruto.",
        },
        "tipo_cambio": s["tipo_cambio"],
    }


def config_para_navegador(cfg: dict) -> dict:
    """Lo que necesita la copia de este cálculo en el navegador (frontend/src/roi.ts), para la demo sin servidor."""
    return {k: cfg[k] for k in ("piloto", "hogar", "topes", "base_real", "supuestos")}


def escenarios(cfg: dict, tus_numeros: dict | None = None) -> dict:
    return {e: calcular(cfg, e, tus_numeros) for e in ESCENARIOS}


def tornado(cfg: dict, tus_numeros: dict | None = None, metrica: str = "neto_anio1") -> list[dict]:
    """Cuánto se mueve el neto nacional del año 1 al llevar cada supuesto a su valor bajo y alto."""
    base_vals = _valores(cfg, "base")
    base = calcular(cfg, valores=base_vals, tus_numeros=tus_numeros)["nacional"][metrica]
    fijados = {REEMPLAZA[k] for k in (tus_numeros or {}) if k in REEMPLAZA}
    salida = []
    for k, sup in cfg["supuestos"].items():
        if k in NEUTROS or k in SOLO_PILOTO or k in fijados:
            continue
        r = {}
        for nivel in ("bajo", "alto"):
            v = dict(base_vals)
            v[k] = float(sup[nivel])
            r[nivel] = calcular(cfg, valores=v, tus_numeros=tus_numeros)["nacional"][metrica]
        salida.append(
            {
                "supuesto": k,
                "unidad": sup["unidad"],
                "fuente": sup["fuente"],
                "valor_bajo": sup["bajo"],
                "valor_base": sup["base"],
                "valor_alto": sup["alto"],
                "neto_con_bajo": r["bajo"],
                "neto_con_alto": r["alto"],
                "neto_base": base,
                "amplitud": abs(r["alto"] - r["bajo"]),
            }
        )
    return sorted(salida, key=lambda x: -x["amplitud"])


# ------------------------------------------------------------------ cifras y reporte
def L(v: float) -> str:
    """Lempiras redondeados a 2 cifras significativas: L 1,100, L 850 mil, L 3.4 M."""
    v = sig(v)
    signo, a = ("−" if v < 0 else ""), abs(v)
    if a >= 1e6:
        return f"{signo}L {a / 1e6:,.1f} M".replace(".0 M", " M")
    if a >= 1e4:
        return f"{signo}L {a / 1e3:,.0f} mil"
    return f"{signo}L {a:,.0f}"


def rango(a: float, b: float) -> str:
    lo, hi = sorted((a, b))
    return f"{L(lo)} a {L(hi)}"


def _entero(v: float) -> str:
    return f"{sig(v):,.0f}"


def _modelo_hogar() -> dict:
    ruta = REPORTES_DIR / "metricas_hogar.json"
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}


def cifras(cfg: dict) -> dict:
    """Números clave redondeados que usan la UI, los documentos y el pitch (una sola fuente)."""
    es = escenarios(cfg)
    b, c, o = es["base"], es["conservador"], es["optimista"]
    tc = b["tipo_cambio"]
    pct = lambda v: f"{v * 100:.0f} %"  # noqa: E731
    mb, mc, mo = b["movil"], c["movil"], o["movil"]
    hb, hc, ho = b["hogar"], c["hogar"], o["hogar"]
    mh = _modelo_hogar()
    ia = mh.get("modelos", {}).get("LightGBM calibrado", {})
    regla = mh.get("regla_umbrales", {})
    return {
        # ---------------------------------------------------------------- total (ambos frentes)
        "neto_anio1_base": L(b["nacional"]["neto_anio1"]),
        "neto_anio1_rango": rango(c["nacional"]["neto_anio1"], o["nacional"]["neto_anio1"]),
        "neto_regimen_base": L(b["nacional"]["neto_regimen_anio"]),
        "beneficio_duro_anio_base": L(b["nacional"]["beneficio_duro_anio"]),
        "costo_recurrente_anio_base": L(b["nacional"]["costo_recurrente_anio"]),
        "inversion_unica_base": L(b["nacional"]["inversion_unica"]),
        "roi_anio1_base": f"{b['nacional']['roi_anio1']:.1f}×",
        "payback_base": f"{math.ceil(b['nacional']['payback_meses'])} meses" if b["nacional"]["payback_meses"] else "—",
        "piloto_costo_base": L(b["piloto"]["costo_total"]),
        "piloto_costo_usd": f"US$ {sig(b['piloto']['costo_total'] / tc) / 1000:,.0f} mil",
        "piloto_costo_rango": rango(o["piloto"]["costo_total"], c["piloto"]["costo_total"]),
        "piloto_beneficio_base": L(b["piloto"]["beneficio_duro"]),
        "conservador_neto_anio1": L(c["nacional"]["neto_anio1"]),
        "optimista_neto_anio1": L(o["nacional"]["neto_anio1"]),
        "potencial_retencion_base": L(b["potencial_no_incluido"]["margen_retenido_anio"]),
        # ---------------------------------------------------------------- frente Hogar
        "hogar_neto_anio1_base": L(hb["nacional"]["neto_anio1"]),
        "hogar_neto_anio1_rango": rango(hc["nacional"]["neto_anio1"], ho["nacional"]["neto_anio1"]),
        "hogar_beneficio_anio_base": L(hb["nacional"]["beneficio_duro_anio"]),
        "hogar_equilibrio_anio1": pct(hb["nacional"]["equilibrio_reduccion_anio1"]),
        "hogar_visitas_evitadas_anio_base": _entero(hb["nacional"]["visitas_evitadas_anio"]),
        "hogar_visitas_evitadas_anio_rango": f"{_entero(hc['nacional']['visitas_evitadas_anio'])} a "
        f"{_entero(ho['nacional']['visitas_evitadas_anio'])}",
        "hogar_llamadas_evitadas_anio_base": _entero(hb["nacional"]["llamadas_evitadas_anio"]),
        "hogar_reduccion_total_visitas": pct(hb["nacional"]["reduccion_total_visitas"]),
        "hogar_reduccion_supuesta": pct(b["supuestos"]["reduccion_visitas_marcados"]),
        "hogar_inversion_base": L(hb["nacional"]["inversion_unica"]),
        "hogar_piloto_costo_base": L(hb["piloto"]["costo_total"]),
        "hogar_visitas_mes": _entero(hb["nacional"]["visitas_mes"]),
        "hogares_nacional": f"{hb['nacional']['hogares']:,.0f}",
        "costo_por_visita": L(b["supuestos"]["costo_por_visita"]),
        "hogar_ia_captura": pct(ia["captura_visitas_evitables"]) if ia else "—",
        "hogar_regla_captura": pct(regla["captura_visitas_evitables"]) if regla else "—",
        "hogar_ia_vs_regla": f"{mh['ia_vs_regla']:.1f}×" if mh else "—",
        "hogar_ia_auc": f"{ia['auc']:.2f}" if ia else "—",
        "hogar_deteccion_temprana": pct(mh["deteccion_temprana"]) if mh else "—",
        # ---------------------------------------------------------------- frente Móvil
        "movil_neto_anio1_base": L(mb["nacional"]["neto_anio1"]),
        "movil_neto_anio1_rango": rango(mc["nacional"]["neto_anio1"], mo["nacional"]["neto_anio1"]),
        "movil_piloto_costo_base": L(mb["piloto"]["costo_total"]),
        "equilibrio_anio1": pct(mb["nacional"]["equilibrio_reduccion_anio1"]),
        "equilibrio_regimen": pct(mb["nacional"]["equilibrio_reduccion_regimen"]),
        "reduccion_supuesta_base": pct(b["supuestos"]["reduccion_con_aviso"]),
        "reduccion_rango": f"{pct(c['supuestos']['reduccion_con_aviso'])} a "
        f"{pct(o['supuestos']['reduccion_con_aviso'])}",
        "llamadas_evitadas_anio_base": _entero(mb["nacional"]["llamadas_evitadas_anio"]),
        "llamadas_evitadas_anio_rango": f"{_entero(mc['nacional']['llamadas_evitadas_anio'])} a "
        f"{_entero(mo['nacional']['llamadas_evitadas_anio'])}",
        "piloto_afectados_base": _entero(mb["piloto"]["afectados"]),
        "piloto_llamadas_evitadas_base": _entero(mb["piloto"]["llamadas_evitadas"]),
        "fallas_mes_piloto": f"{cfg['supuestos']['fallas_mes_piloto']['base']:.0f}",
        "costo_por_llamada": L(b["supuestos"]["costo_por_llamada"]),
    }


def reporte_markdown(cfg: dict) -> str:
    es = escenarios(cfg)
    cf = cifras(cfg)
    orden = ("conservador", "base", "optimista")

    def fila(nombre, f):
        return f"| {nombre} | " + " | ".join(f(es[e]) for e in orden) + " |"

    pct = lambda v: f"{v * 100:.0f} %"  # noqa: E731
    pago = lambda n: f"{math.ceil(n['payback_meses'])} meses" if n["payback_meses"] else "no se recupera"  # noqa: E731
    out = [
        "# Impacto esperado — Tigo Predice v03 (caso conservador)",
        "",
        "> Generado con `python -m backend.app.services.roi` desde `config/negocio.toml` (mismas fórmulas que la app).",
        "> **Todos los supuestos son a validar con Tigo.** Cifras redondeadas a 2 cifras significativas.",
        "",
        "## Las frases para el comité",
        "",
        f"- **Hogar:** con solo {cf['hogar_equilibrio_anio1']} menos visitas evitables en los hogares que marca la IA, "
        f"el frente Hogar se paga en el primer año (incluida su inversión). El caso base supone "
        f"{cf['hogar_reduccion_supuesta']} (proveedores reportan de 20 % a 60 %).",
        f"- **Móvil:** con solo {cf['equilibrio_anio1']} menos llamadas en los clientes avisados, "
        "la plataforma se paga "
        f"en el primer año. Los benchmarks públicos están entre 18 % y 88 %; el caso base usa "
        f"{cf['reduccion_supuesta_base']}.",
        f"- **Total:** neto del año 1 de {cf['neto_anio1_base']} en el escenario base "
        f"(rango {cf['neto_anio1_rango']}).",
        "",
        "## Caso base = solo beneficio duro",
        "",
        "| | Conservador | Base | Optimista |",
        "|---|---|---|---|",
        fila("**Hogar** · visitas evitadas al año", lambda r: _entero(r["hogar"]["nacional"]["visitas_evitadas_anio"])),
        fila(
            "Hogar · reducción del total de visitas", lambda r: pct(r["hogar"]["nacional"]["reduccion_total_visitas"])
        ),
        fila("Hogar · beneficio duro anual", lambda r: L(r["hogar"]["nacional"]["beneficio_duro_anio"])),
        fila("Hogar · neto año 1", lambda r: L(r["hogar"]["nacional"]["neto_anio1"])),
        fila(
            "**Móvil** · llamadas evitadas al año", lambda r: _entero(r["movil"]["nacional"]["llamadas_evitadas_anio"])
        ),
        fila("Móvil · beneficio duro anual", lambda r: L(r["movil"]["nacional"]["beneficio_duro_anio"])),
        fila("Móvil · neto año 1", lambda r: L(r["movil"]["nacional"]["neto_anio1"])),
        fila("Beneficio duro anual (total)", lambda r: L(r["nacional"]["beneficio_duro_anio"])),
        fila("Costo recurrente anual (total)", lambda r: L(r["nacional"]["costo_recurrente_anio"])),
        fila("Inversión única (integración)", lambda r: L(r["nacional"]["inversion_unica"])),
        fila("**Neto año 1 (total)**", lambda r: f"**{L(r['nacional']['neto_anio1'])}**"),
        fila("Neto anual en régimen (año 2+)", lambda r: L(r["nacional"]["neto_regimen_anio"])),
        fila("Recuperación de la inversión", lambda r: pago(r["nacional"])),
        fila(
            "Equilibrio Hogar: reducción mínima de visitas evitables (año 1)",
            lambda r: pct(r["hogar"]["nacional"]["equilibrio_reduccion_anio1"]),
        ),
        fila(
            "Equilibrio Móvil: reducción mínima de llamadas (año 1)",
            lambda r: pct(r["movil"]["nacional"]["equilibrio_reduccion_anio1"]),
        ),
        "",
        "Hogar cuenta solo visitas evitables (WiFi, firmware, «sin falla encontrada») en hogares que la IA marcó a "
        "tiempo, más las llamadas asociadas a esas visitas. No cuenta las visitas repetidas evitadas ni las llamadas "
        "que se evitan al avisar problemas físicos.",
        "",
        "## Piloto de 60 días en San Pedro Sula",
        "",
        "| | Conservador | Base | Optimista |",
        "|---|---|---|---|",
        fila("Hogar · hogares marcados (acciones)", lambda r: _entero(r["hogar"]["piloto"]["marcados"])),
        fila("Hogar · visitas evitadas", lambda r: _entero(r["hogar"]["piloto"]["visitas_evitadas"])),
        fila("Móvil · afectados en 60 días", lambda r: _entero(r["movil"]["piloto"]["afectados"])),
        fila("Móvil · llamadas evitadas", lambda r: _entero(r["movil"]["piloto"]["llamadas_evitadas"])),
        fila("Beneficio duro", lambda r: L(r["piloto"]["beneficio_duro"])),
        fila("Costo total del piloto", lambda r: L(r["piloto"]["costo_total"])),
        "",
        "El piloto **no busca pagarse en 60 días**: busca **medir** con grupo de control si el efecto supera el "
        "punto de equilibrio. Si da GO, la escala nacional se paga sola.",
        "",
        "## Potencial NO incluido en el caso base",
        "",
        f"- Retención: {L(es['base']['potencial_no_incluido']['margen_retenido_anio'])} al año de **margen** "
        f"(no ingreso bruto) si el piloto mide {cfg['supuestos']['churn_incremental_evitado']['base'] * 100:.1f} "
        "puntos menos de churn mensual en avisados vs. control. Hasta medirlo, vale cero.",
        "- Hogar: visitas repetidas evitadas (el técnico llega con el diagnóstico) y llamadas evitadas al avisar "
        "problemas físicos. Se miden en el piloto, no se cuentan.",
        "- NPS/CSAT de afectados: se mide en el piloto, no se monetiza.",
        "",
        "## Sensibilidad (tornado): qué supuestos mueven más el neto total del año 1",
        "",
        "| Supuesto | Bajo → neto | Alto → neto | Fuente |",
        "|---|---|---|---|",
    ]
    for t in tornado(cfg)[:10]:
        out.append(
            f"| {t['supuesto']} ({t['valor_bajo']} / {t['valor_alto']}) | {L(t['neto_con_bajo'])} | "
            f"{L(t['neto_con_alto'])} | {t['fuente']} |"
        )
    out += [
        "",
        "## Supuestos",
        "",
        "| Supuesto | Unidad | Bajo | Base | Alto | Fuente | Nota |",
        "|---|---|---|---|---|---|---|",
    ]
    for k, v in cfg["supuestos"].items():
        out.append(f"| {k} | {v['unidad']} | {v['bajo']} | {v['base']} | {v['alto']} | {v['fuente']} | {v['nota']} |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    from ml.comun import RAIZ, cargar_config

    cfg = cargar_config()
    (RAIZ / "docs" / "impacto.md").write_text(reporte_markdown(cfg), encoding="utf-8", newline="\n")
    (RAIZ / "docs" / "cifras.json").write_text(
        json.dumps(cifras(cfg), indent=2, ensure_ascii=False), encoding="utf-8", newline="\n"
    )
    print(json.dumps(cifras(cfg), indent=2, ensure_ascii=False))
    _ = NIVELES
