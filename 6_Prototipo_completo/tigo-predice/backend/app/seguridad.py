"""Controles de seguridad de la API: autenticación, roles, límites y bitácora de accesos.

Modo demo local (sin tokens): solo atiende peticiones desde la misma máquina (127.0.0.1). Si alguien
expone el servidor en la red sin configurar tokens, la API responde 403: falla en modo seguro.

Modo protegido (al definir al menos un token de 24+ caracteres):
  TIGO_TOKEN_LECTURA → rol «lectura»: solo consulta (por ejemplo, el jurado en una demo compartida)
  TIGO_TOKEN         → rol «operador»: además ejecuta acciones (enviar mensajes, reiniciar la Fase 2)
  TIGO_TOKEN_AUDITOR → rol «auditor»: además lee las bitácoras de mensajes y accesos
  - POST /api/sesion con el token → cookie de sesión firmada (HMAC-SHA256), HttpOnly, SameSite=Strict, Secure
    con HTTPS o en producción, vence en 8 horas. La sesión vive también en el servidor: cerrar sesión la revoca.
  - 5 intentos fallidos por IP en 15 minutos → bloqueo temporal (429). Tokens cortos → la API no arranca (503).
  - Peticiones que cambian estado desde otro origen → 403 (defensa CSRF además de SameSite).
  - Cada acceso queda en la bitácora de accesos (sesión seudonimizada, rol, método, ruta SIN consulta, estado).
En producción esto se reemplaza por SSO corporativo (OIDC) con MFA; los roles y el contrato de la API no cambian.
Límite de peticiones (TIGO_LIMITE_MIN, por defecto 600 por minuto por IP) para evitar abuso de recursos.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
import threading
import time
from collections import defaultdict, deque
from datetime import datetime

from ml.comun import DB_PATH

COOKIE = "tigo_sesion"
DURACION_SESION = 8 * 3600
MAX_FALLIDOS, VENTANA_FALLIDOS = 5, 15 * 60
LARGO_MINIMO_TOKEN = 24
ROLES = {"TIGO_TOKEN_LECTURA": "lectura", "TIGO_TOKEN": "operador", "TIGO_TOKEN_AUDITOR": "auditor"}
NIVEL = {"lectura": 1, "operador": 2, "auditor": 3}
RUTAS_PUBLICAS = {("POST", "/api/sesion"), ("GET", "/api/sesion"), ("DELETE", "/api/sesion")}
CLIENTES_LOCALES = {"127.0.0.1", "::1", "localhost", "testclient"}
METODOS_ESCRITURA = {"POST", "PUT", "PATCH", "DELETE"}

_CLAVE = secrets.token_bytes(32)  # se renueva al reiniciar: las sesiones viejas dejan de valer
_lock = threading.Lock()
_sesiones: dict[str, tuple[str, int]] = {}  # id de sesión → (rol, vencimiento)
_peticiones: dict[str, deque] = defaultdict(deque)
_fallidos: dict[str, deque] = defaultdict(deque)

_SQL = """CREATE TABLE IF NOT EXISTS bitacora_accesos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, fecha_hora TEXT, sesion TEXT, rol TEXT, metodo TEXT, ruta TEXT,
    estado INTEGER)"""


# ------------------------------------------------------------------ configuración
def tokens() -> dict[str, str]:
    """Rol por token configurado (vacío = modo demo local)."""
    return {v: ROLES[k] for k in ROLES if (v := os.getenv(k))}


def modo_protegido() -> bool:
    return bool(tokens())


def configuracion_debil() -> bool:
    """Algún token es demasiado corto: la API se niega a operar (falla en modo seguro)."""
    return any(len(t) < LARGO_MINIMO_TOKEN for t in tokens())


def limite_por_minuto() -> int:
    return int(os.getenv("TIGO_LIMITE_MIN", "600"))


# ------------------------------------------------------------------ sesiones
def _firma(valor: str) -> str:
    return hmac.new(_CLAVE, valor.encode(), hashlib.sha256).hexdigest()


def crear_sesion(rol: str) -> str:
    sid = secrets.token_urlsafe(24)
    vence = int(time.time()) + DURACION_SESION
    with _lock:
        _sesiones[sid] = (rol, vence)
    return f"{sid}.{vence}.{_firma(f'{sid}.{vence}')}"


def rol_de_sesion(cookie: str | None) -> str | None:
    """Rol de una cookie válida (firma correcta, no vencida y no revocada); si no, None."""
    if not cookie or cookie.count(".") != 2:
        return None
    sid, vence, firma = cookie.split(".")
    if not hmac.compare_digest(firma, _firma(f"{sid}.{vence}")):
        return None
    with _lock:
        guardada = _sesiones.get(sid)
    if not guardada or guardada[1] < time.time() or str(guardada[1]) != vence:
        return None
    return guardada[0]


def sesion_valida(cookie: str | None) -> bool:
    return rol_de_sesion(cookie) is not None


def revocar(cookie: str | None) -> None:
    if cookie and cookie.count(".") == 2:
        with _lock:
            _sesiones.pop(cookie.split(".")[0], None)


def rol_de_token(intento: str) -> str | None:
    """Compara en tiempo constante contra cada token configurado."""
    rol = None
    for token, r in tokens().items():
        if hmac.compare_digest(intento.encode(), token.encode()):
            rol = r
    return rol


def autorizado(rol: str, metodo: str, ruta: str) -> bool:
    if ruta.startswith("/api/bitacora"):
        return NIVEL[rol] >= NIVEL["auditor"]
    if metodo in METODOS_ESCRITURA:
        return NIVEL[rol] >= NIVEL["operador"]
    return True


def seudonimo(cookie: str | None) -> str:
    """Identificador estable de la sesión para la bitácora, sin poder reconstruir la cookie."""
    return hashlib.sha256((cookie or "anonima").encode()).hexdigest()[:12]


def origen_ajeno(origen: str | None, host: str | None) -> bool:
    """True si una petición que cambia estado viene de otro sitio (defensa CSRF)."""
    if not origen:
        return False
    destino = origen.split("://", 1)[-1].rstrip("/")
    return destino not in {host, "localhost:5173", "127.0.0.1:5173"}


# ------------------------------------------------------------------ límites
def _ventana(cola: deque, segundos: int, ahora: float) -> None:
    while cola and cola[0] < ahora - segundos:
        cola.popleft()


def permitir_peticion(ip: str) -> bool:
    ahora = time.time()
    with _lock:
        if len(_peticiones) > 10_000:  # evita que la tabla crezca sin límite
            for k in [k for k, v in _peticiones.items() if not v or v[-1] < ahora - 60]:
                del _peticiones[k]
        cola = _peticiones[ip]
        _ventana(cola, 60, ahora)
        if len(cola) >= limite_por_minuto():
            return False
        cola.append(ahora)
        return True


def bloqueado(ip: str) -> bool:
    with _lock:
        cola = _fallidos[ip]
        _ventana(cola, VENTANA_FALLIDOS, time.time())
        return len(cola) >= MAX_FALLIDOS


def registrar_fallido(ip: str) -> None:
    with _lock:
        _fallidos[ip].append(time.time())


def reiniciar_limites() -> None:
    with _lock:
        _peticiones.clear()
        _fallidos.clear()
        _sesiones.clear()


# ------------------------------------------------------------------ bitácora de accesos
def _preparar(con: sqlite3.Connection) -> None:
    con.execute(_SQL)
    columnas = {c[1] for c in con.execute("PRAGMA table_info(bitacora_accesos)")}
    if "rol" not in columnas:  # tabla creada por una versión anterior
        con.execute("ALTER TABLE bitacora_accesos ADD COLUMN rol TEXT")


def registrar_acceso(cookie: str | None, rol: str | None, metodo: str, ruta: str, estado: int) -> None:
    try:
        with sqlite3.connect(DB_PATH) as con:
            _preparar(con)
            con.execute(
                "INSERT INTO bitacora_accesos (fecha_hora, sesion, rol, metodo, ruta, estado) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (datetime.now().isoformat(timespec="seconds"), seudonimo(cookie), rol or "-", metodo, ruta, estado),
            )
    except sqlite3.Error:
        pass


def ultimos_accesos(limite: int = 100) -> list[dict]:
    try:
        with sqlite3.connect(DB_PATH) as con:
            _preparar(con)
            con.row_factory = sqlite3.Row
            filas = con.execute("SELECT * FROM bitacora_accesos ORDER BY id DESC LIMIT ?", (limite,)).fetchall()
            return [dict(f) for f in filas]
    except sqlite3.Error:
        return []
