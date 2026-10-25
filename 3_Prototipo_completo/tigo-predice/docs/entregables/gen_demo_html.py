"""Arma la demo en un solo archivo HTML que se abre con doble clic, sin servidor, sin internet y sin instalar nada.

Toma las respuestas de la API que corre en esta máquina y las incrusta en la página junto con el JavaScript y el CSS
de la versión sin servidor del frontend. Junto al HTML escribe lo necesario para publicar la carpeta tal cual en un
hosting estático (se sube completa a la raíz del dominio):
  - política de seguridad de contenido (CSP) con el hash de cada script, dentro del mismo HTML;
  - _headers (Netlify, Cloudflare Pages) y .htaccess (Apache) con las cabeceras de seguridad;
  - robots.txt y .well-known/security.txt (RFC 9116).

Uso:
  1. cd frontend && VITE_ESTATICO=1 npx vite build --base ./ --outDir dist-estatico
  2. Con la API corriendo en http://127.0.0.1:8000:
     python docs/entregables/gen_demo_html.py <carpeta>/index.html
     O, si solo cambió la interfaz, reutilizando los datos de una demo ya generada (sin API):
     python docs/entregables/gen_demo_html.py <carpeta>/index.html --datos-de <carpeta>/index.html
"""

import base64
import hashlib
import json
import re
import sys
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DIST = RAIZ / "frontend" / "dist-estatico"
API = "http://127.0.0.1:8000"
CONTACTO = "sandra.jimenez@tigo.com.hn"
DESCRIPCION = (
    "Prototipo presentado en el concurso interno AI Shark Tank · Tigo CX Month 2026. "
    "Datos simulados; no es un canal oficial de atención de Tigo."
)


def pedir(ruta: str):
    with urllib.request.urlopen(API + ruta, timeout=60) as r:  # noqa: S310 (solo la API local)
        return json.loads(r.read().decode("utf-8"))


def texto_js(v) -> str:
    """Igual que String(v) en JavaScript para los números de los parámetros."""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v)


def datos_de_demo(html: Path) -> dict:
    """Recupera las respuestas incrustadas en una demo ya generada."""
    texto = html.read_text(encoding="utf-8")
    inicio = texto.index("window.__DATOS__=") + len("window.__DATOS__=")
    fin = texto.index(";</script>", inicio)
    return json.loads(texto[inicio:fin])  # «<\/» es un escape válido en JSON


def main(salida: Path, reutilizar: Path | None = None) -> None:
    datos = datos_de_demo(reutilizar) if reutilizar else recolectar()
    # «Pon tus números» se calcula en el navegador (frontend/src/roi.ts) con los supuestos de config/negocio.toml
    sys.path.insert(0, str(RAIZ))
    from backend.app.services import produccion, roi
    from ml.comun import cargar_config

    datos["/config/negocio"] = roi.config_para_navegador(cargar_config())
    # «Listo para producción» no depende de los modelos: se toma siempre de su fuente vigente
    datos["/api/produccion"] = produccion.contenido()
    escribir(salida, datos)


def recolectar() -> dict:
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
    return datos


def escribir(salida: Path, datos: dict) -> None:
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
    datos_js = f"window.__DATOS__={carga};"
    csp = politica(datos_js, js_seguro)
    meta = (
        f'<meta http-equiv="Content-Security-Policy" content="{csp}" />\n'
        '<meta name="referrer" content="no-referrer" />\n'
        '<meta name="robots" content="noindex, nofollow" />\n'
        f'<meta name="description" content="{DESCRIPCION}" />\n'
    )
    # La CSP va antes que cualquier script para que los cubra a todos
    html = html.replace("<title>", meta + "<title>", 1)
    html = html.replace(
        "</head>",
        f'<script>{datos_js}</script>\n<script type="module">{js_seguro}</script>\n</head>',
    )
    salida.write_text(html, encoding="utf-8", newline="\n")
    escribir_hosting(salida.parent, csp)
    print("OK", salida, f"{len(html.encode('utf-8')) / 1e6:.1f} MB", f"{len(datos)} respuestas")


def politica(*scripts: str) -> str:
    """CSP estricta: solo corren los scripts incrustados (por su hash); sin conexiones ni recursos externos."""
    hashes = " ".join(
        f"'sha256-{base64.b64encode(hashlib.sha256(s.encode('utf-8')).digest()).decode()}'" for s in scripts
    )
    return (
        f"default-src 'none'; script-src {hashes}; style-src 'unsafe-inline'; img-src data:; "
        "connect-src 'none'; base-uri 'none'; form-action 'none'"
    )


def escribir_hosting(carpeta: Path, csp: str) -> None:
    """Cabeceras de seguridad del hosting estático. frame-ancestors solo funciona como cabecera, no en <meta>."""
    cabeceras = {
        "Content-Security-Policy": f"{csp}; frame-ancestors 'none'",
        "Strict-Transport-Security": "max-age=31536000",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
        "Cross-Origin-Opener-Policy": "same-origin",
        "X-Robots-Tag": "noindex, nofollow",
        "Cache-Control": "no-cache",
    }
    (carpeta / "_headers").write_text(
        "/*\n" + "".join(f"  {k}: {v}\n" for k, v in cabeceras.items()), encoding="utf-8", newline="\n"
    )
    (carpeta / ".htaccess").write_text(
        "DirectoryIndex index.html\nOptions -Indexes\n\n"
        # Si el hosting despliega desde un repositorio (p. ej. Hostinger con GitHub), .git queda en la carpeta pública:
        # ningún archivo oculto se sirve, salvo .well-known
        "RedirectMatch 404 ^/\\.(?!well-known/)\n\n"
        "<IfModule mod_rewrite.c>\n  RewriteEngine On\n  RewriteCond %{HTTPS} off\n"
        "  RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]\n</IfModule>\n\n"
        "<IfModule mod_headers.c>\n"
        + "".join(f'  Header always set {k} "{v}"\n' for k, v in cabeceras.items())
        + "</IfModule>\n",
        encoding="utf-8",
        newline="\n",
    )
    (carpeta / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8", newline="\n")
    vence = (datetime.now(UTC) + timedelta(days=365)).strftime("%Y-%m-%dT00:00:00Z")
    (carpeta / ".well-known").mkdir(exist_ok=True)
    (carpeta / ".well-known" / "security.txt").write_text(
        f"Contact: mailto:{CONTACTO}\nExpires: {vence}\nPreferred-Languages: es, en\n", encoding="utf-8", newline="\n"
    )
    # Si la carpeta de la demo está en la raíz del repositorio (<repo>/1_Demo), también se escribe el .htaccess del repo
    if (carpeta.parent / ".git").exists():
        escribir_raiz_repositorio(carpeta.parent, carpeta.name, cabeceras)


RAIZ_REPOSITORIO = r"""# Generado por gen_demo_html.py.
# El hosting publica el repositorio completo (Hostinger conectado a GitHub):
# la raíz del dominio muestra la demo de {demo}/ y nada más del repositorio se sirve.
DirectoryIndex index.html
Options -Indexes

RewriteEngine On

RewriteCond %{HTTPS} off
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# La dirección es solo el dominio: sin www, sin /index.html y sin carpetas
# (2_Demo era la carpeta de la demo en una versión anterior: sus enlaces viejos también llegan a la raíz)
RewriteCond %{HTTP_HOST} ^www\.(.+)$ [NC]
RewriteRule ^ https://%1/ [L,R=301]
RewriteCond %{THE_REQUEST} \s/+(({demo}|2_Demo)(/|\s|\?)|index\.html)
RewriteRule ^ / [L,R=301]

# Lo único público: la demo y sus archivos de sitio
RewriteRule ^(index\.html)?$ {demo}/index.html [L]
RewriteRule ^robots\.txt$ {demo}/robots.txt [L]
RewriteRule ^\.well-known/security\.txt$ {demo}/.well-known/security.txt [L]

# Todo lo demás del repositorio (código, documentos, PDF, .git) no se sirve
RewriteCond %{THE_REQUEST} !\s/+(index\.html|robots\.txt|\.well-known/security\.txt)?(\s|\?)
RewriteRule ^ - [F]
"""


def escribir_raiz_repositorio(raiz: Path, demo: str, cabeceras: dict[str, str]) -> None:
    """.htaccess de la raíz del repo: dirección limpia (sin la carpeta de la demo) y el resto del repo, cerrado."""
    (raiz / ".htaccess").write_text(
        RAIZ_REPOSITORIO.replace("{demo}", demo)
        + "\n<IfModule mod_headers.c>\n"
        + "".join(f'  Header always set {k} "{v}"\n' for k, v in cabeceras.items())
        + "</IfModule>\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    reutilizar = Path(args[args.index("--datos-de") + 1]) if "--datos-de" in args else None
    main(Path(args[0]), reutilizar)
