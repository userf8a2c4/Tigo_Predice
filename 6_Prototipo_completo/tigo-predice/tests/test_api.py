"""Tests de la API completa (requieren datos y modelos: tareas.ps1 preparar)."""

import pytest

from ml.comun import DB_PATH, MODELOS_DIR

pytestmark = pytest.mark.skipif(
    not DB_PATH.exists() or not (MODELOS_DIR / "actual.json").exists(),
    reason="Faltan datos/modelos: ejecute tareas.ps1 preparar",
)


@pytest.fixture(scope="module")
def client():
    import os

    os.environ["TIGO_LLM_DESACTIVADO"] = "1"  # sin internet y sin clave: modo plantillas
    from fastapi.testclient import TestClient

    from backend.app.main import app

    with TestClient(app) as c:
        yield c


def test_salud_reporta_estado_real_del_llm(client):
    r = client.get("/api/salud").json()
    assert r["ok"] and r["clientes"] == 20000 and r["hogares"] == 12000
    assert r["llm_modo"] == "plantillas" and "plantillas" in r["llm_estado"].lower()


def test_falla_en_vivo_determinista_tres_veces(client):
    corridas = [client.get("/api/falla/simular").json() for _ in range(3)]
    assert corridas[0] == corridas[1] == corridas[2], "la demo debe dar exactamente lo mismo cada vez"
    f = corridas[0]
    m = f["muestra"]
    assert m["tratamiento"] + m["control"] == m["afectados"] > 100
    assert 0.08 < m["control"] / m["afectados"] < 0.25
    assert f["por_1000"]["con_aviso"] < f["por_1000"]["sin_aviso"]
    assert len(f["mensajes"]) == 3 and all(len(x["texto"]) <= 300 for x in f["mensajes"])
    k = f["kpis"]
    assert k["llamadas_evitadas"]["bajo"] < k["llamadas_evitadas"]["base"] < k["llamadas_evitadas"]["alto"]
    assert "supuesto" in f["frase_final"]


def test_falla_en_vivo_no_ensucia_el_estado(client):
    antes = client.get("/api/clientes?prioridad=Alta&limite=5").json()
    client.get("/api/falla/simular")
    assert client.get("/api/clientes?prioridad=Alta&limite=5").json() == antes
    assert client.get("/api/conversaciones").json() == []


def test_piloto_resultados_con_incertidumbre(client):
    r = client.get("/api/piloto/resultados").json()
    n = r["metrica_norte"]
    lo, hi = n["ic_reduccion_relativa"]
    assert lo <= n["reduccion_relativa"] <= hi
    assert r["decision"]["decision"] in ("GO", "NO-GO") and len(r["decision"]["criterios"]) == 3
    assert "SIMULADO" in r["aviso"]
    assert r["potencia"]["afectados_necesarios"] > 0


def test_potencia(client):
    a = client.get("/api/piloto/potencia?reduccion=0.10").json()["afectados_necesarios"]
    b = client.get("/api/piloto/potencia?reduccion=0.20").json()["afectados_necesarios"]
    assert a > b, "detectar un efecto más pequeño requiere más muestra"


def test_roi_y_tus_numeros(client):
    base = client.get("/api/roi").json()
    assert set(base["escenarios"]) == {"conservador", "base", "optimista"} and base["tornado"]
    tus = client.get("/api/roi?costo_por_llamada=170").json()
    assert tus["escenarios"]["base"]["fuentes"]["costo_por_llamada"] == "dato Tigo"
    assert tus["escenarios"]["base"]["movil"]["nacional"]["beneficio_duro_anio"] == pytest.approx(
        base["escenarios"]["base"]["movil"]["nacional"]["beneficio_duro_anio"] * 2, rel=0.01
    )
    h = client.get("/api/roi?costo_por_visita=2200").json()["escenarios"]["base"]
    assert h["fuentes"]["costo_por_visita"] == "dato Tigo"
    assert (
        h["hogar"]["nacional"]["beneficio_duro_anio"]
        > base["escenarios"]["base"]["hogar"]["nacional"]["beneficio_duro_anio"]
    )


def test_modelo_compara_contra_regla(client):
    m = client.get("/api/modelo").json()["fase1"]
    assert (
        m["modelos"]["LightGBM calibrado"]["llamadas_por_100_contactos_top20"]
        > m["regla_operativa"]["llamadas_por_100_contactos_top20"]
        > m["azar"]["llamadas_por_100_contactos_top20"]
    )
    assert "Temporal" in m["validacion"]


def test_produccion_y_bitacora(client):
    p = client.get("/api/produccion").json()
    assert {"consentimiento", "integracion", "riesgos", "equipo", "plan"} <= set(p)
    client.get("/api/falla/simular")
    b = client.get("/api/bitacora/mensajes?limite=3").json()
    assert b and {"fuente", "version_prompt", "guardrails"} <= set(b[0])


# ---------------------------------------------------------------- frente Hogar
@pytest.mark.parametrize("caso", ["remoto", "tecnico"])
def test_hogar_en_vivo_determinista_y_coherente(client, caso):
    corridas = [client.get(f"/api/hogar/simular?caso={caso}").json() for _ in range(3)]
    assert corridas[0] == corridas[1] == corridas[2], "la demo debe dar exactamente lo mismo cada vez"
    h = corridas[0]
    ev = h["eventos"]
    assert ev["inicio"] <= ev["ia"] < ev["llamada"], "la IA lo marca antes de que el cliente llame"
    assert ev["regla"] is None or ev["ia"] < ev["regla"], "y antes que la regla de umbrales"
    assert h["riesgo_al_marcar"] >= h["umbral_riesgo"]
    assert h["explicacion"] and all(m["contribucion"] > 0 for m in h["explicacion"])
    assert len(h["sin"]) == len(h["con"]) == 21
    assert len(h["mensaje"]["texto"]) <= 300 and "AGENTE" in h["mensaje"]["texto"]
    riesgo_final_con = h["con"][-1]["riesgo"]
    assert riesgo_final_con < h["umbral_riesgo"], "después de actuar, el hogar vuelve a estar sano"


def test_hogar_caso_invalido(client):
    assert client.get("/api/hogar/simular?caso=otro").status_code == 422


def test_hogar_lista_de_hoy(client):
    hoy = client.get("/api/hogar/hoy?limite=5").json()
    assert 0 < hoy["marcados"] < hoy["hogares_ciudad"] * 0.05
    assert len(hoy["hogares"]) == 5
    riesgos = [x["riesgo"] for x in hoy["hogares"]]
    assert riesgos == sorted(riesgos, reverse=True)
    assert all(x["accion"] and x["motivos"] for x in hoy["hogares"])


def test_hogar_piloto_con_control_y_criterio_ia(client):
    r = client.get("/api/hogar/piloto").json()
    n = r["metrica_norte"]
    lo, hi = n["ic_reduccion_relativa"]
    assert lo <= n["reduccion_relativa"] <= hi
    assert 0.10 < n["n_control"] / (n["n_control"] + n["n_tratamiento"]) < 0.20
    assert len(r["decision"]["criterios"]) == 4 and "regla" in r["decision"]["criterios"][3]["criterio"]
    assert "SIMULADO" in r["aviso"]


def test_modelo_hogar_le_gana_a_la_regla(client):
    m = client.get("/api/modelo").json()["hogar"]
    ia = m["modelos"]["LightGBM calibrado"]["captura_visitas_evitables"]
    assert ia > m["regla_umbrales"]["captura_visitas_evitables"] > m["azar"]["captura_visitas_evitables"]
    assert 0.7 < m["modelos"]["LightGBM calibrado"]["auc"] < 0.95, "AUC creíble, ni malo ni sospechosamente alto"
    assert "Temporal" in m["validacion"]


# ---------------------------------------------------------------- Fase 2
def test_fase2_flujo_whatsapp_y_ticket(client):
    client.post("/api/fase2/reiniciar")
    c = client.get("/api/clientes?accion=autodiagnostico&limite=1").json()["clientes"][0]
    conv = client.post(f"/api/clientes/{c['cliente_id']}/ejecutar").json()
    assert conv["mensajes"][0]["de"] == "tigo"
    conv = client.post(f"/api/conversaciones/{c['cliente_id']}/responder", json={"texto": "AGENTE"}).json()
    assert conv["estado"] == "escalada"
    assert client.get("/api/tickets").json()[0]["cliente_id"] == c["cliente_id"]
    assert client.post(f"/api/clientes/{c['cliente_id']}/ejecutar").status_code == 409  # anti-fatiga
    client.post("/api/fase2/reiniciar")
    assert client.get("/api/conversaciones").json() == []


def test_fase2_opt_out(client):
    c = client.get("/api/clientes?accion=no_contactar&limite=1").json()["clientes"][0]
    assert client.post(f"/api/clientes/{c['cliente_id']}/ejecutar").status_code == 409
