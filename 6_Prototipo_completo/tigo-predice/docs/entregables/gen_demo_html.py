"""Arma la demo en un solo archivo HTML que se abre con doble clic, sin servidor, sin internet y sin instalar nada.

Toma las respuestas de la API que corre en esta máquina y las incrusta en la página junto con el JavaScript y el CSS
de la versión sin servidor del frontend.

Uso:
  1. cd frontend && VITE_ESTATICO=1 npx vite build --base ./ --outDir dist-estatico
  2. Con la API corriendo en http://127.0.0.1:8000:
     python docs/entregables/gen_demo_html.py <salida.html>
"""

import base64
import json
import re
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DIST = RAIZ / "frontend" / "dist-estatico"
API = "http://127.0.0.1:8000"


def pedir(ruta: str):
    with urllib.request.urlopen(API + ruta, timeout=60) as r:  # noqa: S310 (solo la API local)
        return json.loads(r.read().decode("utf-8"))


def texto_js(v) -> str:
    """Igual que String(v) en JavaScript para los números de los parámetros."""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v)


def main(salida: Path) -> None:
    datos = {"/api/sesion": {"requiere": False, "activa": True}}
    for ruta in [
        "/api/salud",
        "/api/config",
        "/api/inicio",
        "/api/mapa",
        "/api/falla/simular",
        "/api/hogar/simular?caso=remoto",
        "/api/hogar/simular?caso=tecnico",
        "/api/hogar/hoy",
        "/api/hogar/piloto",
        "/api/piloto/resultados",
        "/api/roi",
        "/api/modelo",
        "/api/produccion",
        "/api/conversaciones",
        "/api/tickets",
    ]:
        datos[ruta] = pedir(ruta)

    # La calculadora de poder pide primero sus valores iniciales
    p = datos["/api/piloto/resultados"]["potencia"]
    qs = "&".join(
        f"{k}={texto_js(v)}"
        for k, v in [
            ("tasa_base", p["tasa_base"]),
            ("reduccion", p["reduccion_a_detectar"]),
            ("pct_control", p["pct_control"]),
            ("afectados", p["afectados_esperados_piloto"]),
        ]
    )
    datos[f"/api/piloto/potencia?{qs}"] = pedir(f"/api/piloto/potencia?{qs}")

    # Fase 2: primera página de clientes (filtro inicial) y su detalle
    ruta = "/api/clientes?prioridad=Alta&limite=25&offset=0"
    datos[ruta] = pedir(ruta)
    for c in datos[ruta]["clientes"]:
        datos[f"/api/clientes/{c['cliente_id']}"] = pedir(f"/api/clientes/{c['cliente_id']}")

    datos["/honduras.geojson"] = json.loads((DIST / "honduras.geojson").read_text(encoding="utf-8"))

    html = (DIST / "index.html").read_text(encoding="utf-8")
    js = (DIST / re.search(r'src="\./(assets/[^"]+\.js)"', html).group(1)).read_text(encoding="utf-8")
    css = (DIST / re.search(r'href="\./(assets/[^"]+\.css)"', html).group(1)).read_text(encoding="utf-8")
    icono = base64.b64encode((DIST / "icono.svg").read_bytes()).decode("ascii")
    js_seguro = js.replace("</script", "<\\/script")
    carga = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    html = re.sub(r'<script type="module" crossorigin src="[^"]+"></script>', "", html)
    html = re.sub(r'<link rel="stylesheet" crossorigin href="[^"]+">', lambda _: f"<style>{css}</style>", html)
    html = html.replace('href="./icono.svg"', f'href="data:image/svg+xml;base64,{icono}"')
    html = html.replace("<title>Tigo Predice</title>", "<title>Tigo Predice · Demo</title>")
    html = html.replace(
        "</head>",
        f'<script>window.__DATOS__={carga};</script>\n<script type="module">{js_seguro}</script>\n</head>',
    )
    salida.write_text(html, encoding="utf-8", newline="\n")
    print("OK", salida, f"{len(html.encode('utf-8')) / 1e6:.1f} MB", f"{len(datos)} respuestas")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
