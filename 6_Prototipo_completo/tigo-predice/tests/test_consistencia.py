"""Una sola fuente de verdad: las cifras de los documentos deben coincidir con las del cálculo."""

import json

import pytest

from backend.app.services import produccion, roi
from ml.comun import RAIZ, cargar_config

CFG = cargar_config()
CIFRAS = roi.cifras(CFG)
DOCS = RAIZ / "docs"

HOGAR = ["hogar_equilibrio_anio1", "hogar_ia_vs_regla", "hogar_ia_captura", "hogar_regla_captura"]
REQUERIDAS = {
    "pitch.md": [
        *HOGAR,
        "equilibrio_anio1",
        "neto_anio1_base",
        "neto_anio1_rango",
        "piloto_costo_base",
        "piloto_costo_usd",
        "piloto_costo_rango",
    ],
    "one_pager.md": [
        *HOGAR,
        "hogar_visitas_evitadas_anio_base",
        "hogar_visitas_evitadas_anio_rango",
        "hogar_reduccion_total_visitas",
        "equilibrio_anio1",
        "neto_anio1_base",
        "neto_anio1_rango",
        "neto_regimen_base",
        "llamadas_evitadas_anio_base",
        "llamadas_evitadas_anio_rango",
        "piloto_costo_base",
        "piloto_costo_rango",
        "potencial_retencion_base",
    ],
    "formato_concurso.md": [
        *HOGAR,
        "hogar_visitas_evitadas_anio_base",
        "equilibrio_anio1",
        "neto_anio1_base",
        "neto_anio1_rango",
        "piloto_costo_base",
        "piloto_costo_rango",
        "inversion_unica_base",
        "costo_recurrente_anio_base",
        "llamadas_evitadas_anio_base",
    ],
}


@pytest.mark.parametrize("doc,clave", [(d, c) for d, cs in REQUERIDAS.items() for c in cs])
def test_cifras_del_documento_coinciden_con_el_calculo(doc, clave):
    texto = (DOCS / doc).read_text(encoding="utf-8")
    assert CIFRAS[clave] in texto, f"{doc} no contiene {clave} = «{CIFRAS[clave]}» (¿cambió la configuración?)"


def test_documentos_generados_estan_al_dia():
    assert (DOCS / "impacto.md").read_text(encoding="utf-8") == roi.reporte_markdown(CFG)
    assert json.loads((DOCS / "cifras.json").read_text(encoding="utf-8")) == CIFRAS
    assert (DOCS / "listo_para_produccion.md").read_text(encoding="utf-8") == produccion.markdown()


def test_criterio_go_supera_el_equilibrio():
    eq = roi.calcular(CFG)["movil"]["nacional"]["equilibrio_reduccion_anio1"]
    assert CFG["piloto"]["go_reduccion_min"] > eq
    eq_h = roi.calcular(CFG)["hogar"]["nacional"]["equilibrio_reduccion_anio1"]
    assert CFG["hogar"]["go_reduccion_visitas_min"] > eq_h * CFG["supuestos"]["pct_visitas_evitables"]["base"]
