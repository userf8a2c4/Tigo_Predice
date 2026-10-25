"""API de Tigo Predice v03 (FastAPI). Documentación interactiva en /docs.

Ejecutar desde la raíz del proyecto:
    python -m uvicorn backend.app.main:app --port 8000
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.app import seguridad
from backend.app.llm_client import cargar_env
from backend.app.privacidad import CABECERAS, CSP, SinConsultaEnLogs
from ml.comun import RAIZ

cargar_env(RAIZ / ".env")

from backend.app.estado import Estado  # noqa: E402  (después de cargar .env)
from backend.app.services import acciones, bitacora, falla_vivo, hogar_vivo, produccion, roi  # noqa: E402
from experimento import potencia  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logging.getLogger("uvicorn.access").addFilter(SinConsultaEnLogs())
PRODUCCION = os.getenv("TIGO_PRODUCCION") == "1"  # en producción no se publica la documentación interactiva
FRONT = RAIZ / "frontend" / "dist"
POSICIONAMIENTO = "Los chatbots y copilotos atienden la llamada. Tigo Predice evita que ocurra."
LEMA = (
    "La IA que detecta el problema antes que el cliente, y lo resuelve antes de que llame "
    "o de que haya que mandar un técnico."
)
estado: Estado | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global estado
    estado = Estado()
    estado.llm.verificar()
    bitacora.purgar()
    logging.getLogger("tigo").info("Listo: %s clientes · %s", len(estado.df), estado.llm.estado)
    yield


app = FastAPI(
    title="Tigo Predice API",
    version="3.0",
    description=f"{POSICIONAMIENTO} Datos simulados — supuestos a validar con Tigo.",
    lifespan=lifespan,
    docs_url=None if PRODUCCION else "/docs",
    redoc_url=None,
    openapi_url=None if PRODUCCION else "/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def _negar(estado_http: int, detalle: str) -> JSONResponse:
    return JSONResponse({"detail": detalle}, status_code=estado_http)


@app.middleware("http")
async def control_de_acceso(request: Request, call_next):
    """Límite de peticiones, origen, sesión y rol; bitácora de accesos (sin consulta). Falla en modo seguro."""
    ruta, metodo = request.url.path, request.method
    if not ruta.startswith("/api/"):
        return await call_next(request)
    ip = request.client.host if request.client else "desconocida"
    if not seguridad.permitir_peticion(ip):
        return _negar(429, "Demasiadas peticiones. Intente en un minuto.")
    if metodo in seguridad.METODOS_ESCRITURA and seguridad.origen_ajeno(
        request.headers.get("origin"), request.headers.get("host")
    ):
        return _negar(403, "Origen no permitido")
    if not seguridad.modo_protegido():
        if ip not in seguridad.CLIENTES_LOCALES:
            return _negar(403, "Modo demo: solo acceso local. Configure TIGO_TOKEN para compartir.")
        return await call_next(request)
    if seguridad.configuracion_debil():
        return _negar(503, f"Token demasiado corto (mínimo {seguridad.LARGO_MINIMO_TOKEN} caracteres).")
    cookie = request.cookies.get(seguridad.COOKIE)
    rol = seguridad.rol_de_sesion(cookie)
    if (metodo, ruta) not in seguridad.RUTAS_PUBLICAS:
        if rol is None:
            seguridad.registrar_acceso(cookie, None, metodo, ruta, 401)
            return _negar(401, "Sesión requerida")
        if not seguridad.autorizado(rol, metodo, ruta):
            seguridad.registrar_acceso(cookie, rol, metodo, ruta, 403)
            return _negar(403, "Su rol no permite esta acción")
    respuesta = await call_next(request)
    seguridad.registrar_acceso(cookie, rol, metodo, ruta, respuesta.status_code)
    return respuesta


@app.middleware("http")
async def cabeceras_de_seguridad(request: Request, call_next):
    respuesta = await call_next(request)
    respuesta.headers.update(CABECERAS)
    if not request.url.path.startswith("/docs"):  # la documentación interactiva carga su propio JS
        respuesta.headers["Content-Security-Policy"] = CSP
    if request.url.path.startswith("/api/"):
        respuesta.headers["Cache-Control"] = "no-store"
    if request.url.scheme == "https" or PRODUCCION:
        respuesta.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return respuesta


def _e() -> Estado:
    if estado is None:
        raise HTTPException(503, "El estado aún se está cargando")
    return estado


def _conv_publica(conv: dict) -> dict:
    return {k: v for k, v in conv.items() if k != "ctx"}


class Respuesta(BaseModel):
    texto: str


class Acceso(BaseModel):
    token: str


# ------------------------------------------------------------------ sesión (solo en modo protegido)
@app.get("/api/sesion")
def sesion_estado(request: Request):
    requiere = seguridad.modo_protegido()
    rol = seguridad.rol_de_sesion(request.cookies.get(seguridad.COOKIE)) if requiere else "local"
    return {"requiere": requiere, "activa": rol is not None, "rol": rol}


@app.post("/api/sesion")
def sesion_abrir(a: Acceso, request: Request, response: Response):
    ip = request.client.host if request.client else "desconocida"
    if seguridad.bloqueado(ip):
        raise HTTPException(429, "Demasiados intentos fallidos. Espere 15 minutos.")
    rol = seguridad.rol_de_token(a.token[:200])
    if rol is None:
        seguridad.registrar_fallido(ip)
        seguridad.registrar_acceso(None, None, "POST", "/api/sesion", 401)
        raise HTTPException(401, "Token incorrecto")
    seguridad.revocar(request.cookies.get(seguridad.COOKIE))  # nueva sesión: evita fijación de sesión
    cookie = seguridad.crear_sesion(rol)
    response.set_cookie(
        seguridad.COOKIE,
        cookie,
        max_age=seguridad.DURACION_SESION,
        httponly=True,
        samesite="strict",
        secure=request.url.scheme == "https" or PRODUCCION,
        path="/",
    )
    seguridad.registrar_acceso(cookie, rol, "POST", "/api/sesion", 200)
    return {"ok": True, "rol": rol}


@app.delete("/api/sesion")
def sesion_cerrar(request: Request, response: Response):
    seguridad.revocar(request.cookies.get(seguridad.COOKIE))  # la cookie deja de valer también en el servidor
    response.delete_cookie(seguridad.COOKIE, path="/")
    return {"ok": True}


# ------------------------------------------------------------------ general
@app.get("/api/salud")
def salud():
    e = _e()
    return {
        "ok": True,
        "clientes": len(e.df),
        "hogares": len(e.hogares),
        "modelo": e.version_modelo,
        "llm_modo": e.llm.modo,
        "llm_estado": e.llm.estado,
        "llm_modelo": e.llm.modelo,
    }


@app.get("/api/config")
def config():
    e = _e()
    return {
        "posicionamiento": POSICIONAMIENTO,
        "lema": LEMA,
        "fecha_corte": e.cfg["general"]["fecha_corte"],
        "piloto": e.cfg["piloto"],
        "hogar": e.cfg["hogar"],
        "supuestos": e.cfg["supuestos"],
        "topes": e.cfg["topes"],
        "modelo": e.version_modelo,
        "llm_modo": e.llm.modo,
        "llm_estado": e.llm.estado,
    }


@app.get("/api/inicio")
def inicio():
    e = _e()
    p, ph = e.piloto, e.piloto_hogar
    return {
        "posicionamiento": POSICIONAMIENTO,
        "lema": LEMA,
        "cifras": roi.cifras(e.cfg),
        "hogar": {
            "reduccion_visitas": ph["metrica_norte"]["reduccion_relativa"],
            "ic": ph["metrica_norte"]["ic_reduccion_relativa"],
            "reduccion_llamadas": ph["llamadas"]["reduccion_relativa"],
            "decision": ph["decision"]["decision"],
            "ia_vs_regla": e.metricas_hogar["ia_vs_regla"],
            "captura_ia": e.metricas_hogar["modelos"]["LightGBM calibrado"]["captura_visitas_evitables"],
            "captura_regla": e.metricas_hogar["regla_umbrales"]["captura_visitas_evitables"],
            "marcados_hoy": int((e.hoy_hogar["ciudad"].eq(e.cfg["piloto"]["ciudad"]) & e.hoy_hogar["marcado"]).sum()),
            "aviso": ph["aviso"],
        },
        "piloto": {
            "reduccion": p["metrica_norte"]["reduccion_relativa"],
            "ic": p["metrica_norte"]["ic_reduccion_relativa"],
            "decision": p["decision"]["decision"],
            "por_1000_control": p["metrica_norte"]["por_1000_control"],
            "por_1000_tratamiento": p["metrica_norte"]["por_1000_tratamiento"],
            "aviso": p["aviso"],
        },
        "criterios": {k: e.cfg["piloto"][k] for k in ("go_reduccion_min", "go_optout_max", "alfa")},
    }


@app.get("/api/mapa")
def mapa():
    return _e().mapa()


# ------------------------------------------------------------------ frente Hogar
@app.get("/api/hogar/simular")
def hogar_simular(caso: str = Query("remoto", pattern="^(remoto|tecnico)$")):
    return _e().demo(("hogar", caso), lambda: hogar_vivo.escenario(_e(), caso))


@app.get("/api/hogar/hoy")
def hogar_hoy(limite: int = Query(12, ge=1, le=50)):
    return hogar_vivo.lista_hoy(_e(), limite)


@app.get("/api/hogar/piloto")
def hogar_piloto():
    return _e().piloto_hogar


# ------------------------------------------------------------------ frente Móvil: piloto
@app.get("/api/falla/simular")
def falla_simular():
    return _e().demo(("falla",), lambda: falla_vivo.escenario(_e()))


@app.get("/api/piloto/resultados")
def piloto_resultados():
    return _e().piloto


@app.get("/api/piloto/potencia")
def piloto_potencia(
    tasa_base: float = Query(0.33, gt=0, lt=1),
    reduccion: float = Query(0.10, gt=0, lt=1),
    pct_control: float = Query(0.15, gt=0, lt=0.5),
    afectados: int = Query(48000, gt=0, le=10_000_000),
):
    e = _e()
    cfg = {**e.cfg, "piloto": {**e.cfg["piloto"], "pct_control": pct_control}}
    return potencia.plan(cfg, tasa_base, afectados, reduccion)


@app.get("/api/roi")
def calcular_roi(
    llamadas_mes_fallas_nacional: float | None = Query(None, gt=0, le=10_000_000),
    costo_por_llamada: float | None = Query(None, gt=0, le=100_000),
    visitas_mes_hogar_nacional: float | None = Query(None, gt=0, le=1_000_000),
    costo_por_visita: float | None = Query(None, gt=0, le=1_000_000),
):
    e = _e()
    tus = {
        k: v
        for k, v in {
            "llamadas_mes_fallas_nacional": llamadas_mes_fallas_nacional,
            "costo_por_llamada": costo_por_llamada,
            "visitas_mes_hogar_nacional": visitas_mes_hogar_nacional,
            "costo_por_visita": costo_por_visita,
        }.items()
        if v is not None
    }
    return {"escenarios": roi.escenarios(e.cfg, tus), "tornado": roi.tornado(e.cfg, tus), "tus_numeros": tus}


@app.get("/api/modelo")
def modelo():
    e = _e()
    f2 = e.metricas_fase2["modelos"]
    return {
        "hogar": e.metricas_hogar,
        "fase1": e.metricas_72h,
        "fase2": {
            k: {
                "descripcion": v["descripcion"],
                "auc": v["lightgbm"]["auc"],
                "auc_baseline": v["baseline_regresion_logistica"]["auc"],
            }
            for k, v in f2.items()
        },
    }


@app.get("/api/produccion")
def listo_produccion():
    return produccion.contenido()


@app.get("/api/bitacora/mensajes")
def bitacora_mensajes(limite: int = Query(50, ge=1, le=500)):
    return bitacora.ultimos(limite)


@app.get("/api/bitacora/accesos")
def bitacora_accesos(limite: int = Query(50, ge=1, le=500)):
    return seguridad.ultimos_accesos(limite)


# ------------------------------------------------------------------ Fase 2 (visión)
@app.get("/api/clientes")
def clientes(
    prioridad: str | None = None,
    ciudad: str | None = None,
    segmento: str | None = None,
    accion: str | None = None,
    q: str | None = Query(None, max_length=60),
    limite: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return _e().listar(prioridad, ciudad, segmento, accion, q, limite, offset)


@app.get("/api/clientes/{cliente_id}")
def cliente(cliente_id: str):
    e = _e()
    if cliente_id not in e.df.index:
        raise HTTPException(404, "Cliente no encontrado")
    return e.detalle(cliente_id)


@app.post("/api/clientes/{cliente_id}/ejecutar")
def ejecutar(cliente_id: str):
    e = _e()
    if cliente_id not in e.df.index:
        raise HTTPException(404, "Cliente no encontrado")
    try:
        return _conv_publica(e.ejecutar(cliente_id))
    except ValueError as err:
        raise HTTPException(409, str(err)) from err


@app.get("/api/conversaciones")
def conversaciones():
    return [_conv_publica(c) for c in reversed(list(_e().conversaciones.values()))]


@app.post("/api/conversaciones/{cliente_id}/responder")
def responder(cliente_id: str, r: Respuesta):
    e = _e()
    if cliente_id not in e.conversaciones:
        raise HTTPException(404, "No hay conversación con este cliente")
    return _conv_publica(e.responder(cliente_id, r.texto.strip()[:500]))


@app.get("/api/tickets")
def tickets():
    return list(reversed(_e().tickets))


@app.post("/api/fase2/reiniciar")
def fase2_reiniciar():
    _e().reiniciar()
    return {"ok": True}


@app.get("/api/acciones")
def catalogo_acciones():
    return acciones.CATALOGO


# ------------------------------------------------------------------ frontend compilado
if FRONT.exists():
    app.mount("/assets", StaticFiles(directory=FRONT / "assets"), name="assets")

    @app.get("/{ruta:path}", include_in_schema=False)
    def spa(ruta: str):
        archivo = FRONT / ruta
        if ruta and archivo.is_file() and FRONT in archivo.resolve().parents:
            return FileResponse(archivo)
        return FileResponse(FRONT / "index.html")
