"""Rellena onepager.html con docs/cifras.json (una sola fuente de verdad).

Uso:  python docs/entregables/gen_onepager.py <carpeta_salida>
Deja <carpeta_salida>/onepager.html + hogar.png listos para imprimir a PDF con Edge.
"""

import json
import re
import shutil
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1]
salida = Path(sys.argv[1])
salida.mkdir(parents=True, exist_ok=True)
cifras = json.loads((DOCS / "cifras.json").read_text(encoding="utf-8"))
plantilla = (DOCS / "entregables" / "onepager.html").read_text(encoding="utf-8")
html = re.sub(r"\{\{(\w+)\}\}", lambda m: cifras[m.group(1)], plantilla)
faltan = re.findall(r"\{\{\w+\}\}", html)
if faltan:
    raise SystemExit(f"Cifras sin valor: {faltan}")
(salida / "onepager.html").write_text(html, encoding="utf-8", newline="\n")
shutil.copy(DOCS / "capturas" / "hogar.png", salida / "hogar.png")
print("OK", salida / "onepager.html")
