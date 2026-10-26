// Capturas del sistema para el modo resumen de la presentación (láminas con conclusión, indicadores y captura).
// Abre la demo de un solo archivo con Edge sin ventana, busca cada tarjeta por su atributo data-foco y la recorta.
//
// Uso (desde 3_Prototipo_completo/tigo-predice):
//   1. cd frontend && VITE_ESTATICO=1 npx vite build --base ./ --outDir dist-estatico && cd ..
//   2. python docs/entregables/gen_demo_html.py ../../1_Demo/index.html --datos-de ../../1_Demo/index.html
//   3. node docs/entregables/gen_capturas.mjs ../../1_Demo/index.html frontend/src/assets/capturas
//   4. Repetir 1 y 2 para que la demo incluya las capturas nuevas.
// Las capturas muestran las pantallas del sistema, no las láminas, así que el orden no crea una dependencia circular.

import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const [demo, salida] = process.argv.slice(2);
if (!demo || !salida) {
  console.error("Uso: node gen_capturas.mjs <demo.html> <carpeta_salida>");
  process.exit(1);
}

// pantalla (ruta de la demo) → tarjetas que se recortan
const CAPTURAS = [
  ["/hogar?final", ["hogar-casa", "hogar-diagnostico", "hogar-telefono"]],
  ["/modelo", ["modelo-captura"]],
  ["/falla?final", ["falla-resultado"]],
  ["/negocio", ["negocio-escenarios"]],
  ["/produccion", ["produccion-seguridad"]],
  ["/piloto", ["piloto-decision"]],
];

const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const PUERTO = 9351;
const espera = (ms) => new Promise((r) => setTimeout(r, ms));
mkdirSync(salida, { recursive: true });

const edge = spawn(EDGE, ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1600,900",
  `--remote-debugging-port=${PUERTO}`, `--user-data-dir=${join(tmpdir(), "tigo_capturas")}`, "about:blank"], { stdio: "ignore" });

let ws;
for (let i = 0; i < 40 && !ws; i++) {
  try {
    const pag = (await (await fetch(`http://127.0.0.1:${PUERTO}/json`)).json()).find((p) => p.type === "page");
    if (pag) ws = new WebSocket(pag.webSocketDebuggerUrl);
  } catch {
    // Edge todavía está arrancando
  }
  if (!ws) await espera(500);
}
await new Promise((r) => ws.addEventListener("open", r, { once: true }));
let id = 0;
const pendientes = new Map();
ws.addEventListener("message", (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pendientes.has(m.id)) {
    pendientes.get(m.id)(m.result);
    pendientes.delete(m.id);
  }
});
const cdp = (method, params = {}) => new Promise((r) => { id += 1; pendientes.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const js = async (expr) => (await cdp("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }))?.result?.value;

await cdp("Emulation.setDeviceMetricsOverride", { width: 1600, height: 900, deviceScaleFactor: 1.5, mobile: false });
// Sin animaciones: cada captura sale con su estado final
await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
const base = pathToFileURL(resolve(demo)).href;

let total = 0;
for (const [ruta, focos] of CAPTURAS) {
  // Carga limpia de cada pantalla (la demo abre la ruta que va después del #)
  await cdp("Page.navigate", { url: "about:blank" });
  await espera(300);
  await cdp("Page.navigate", { url: `${base}#${ruta}` });
  await espera(3500);
  for (const foco of focos) {
    const caja = await js(`(() => {
      const el = document.querySelector('[data-foco="${foco}"]');
      if (!el) return null;
      el.scrollIntoView({ block: "center" });
      const r = el.getBoundingClientRect();
      return { x: r.left, y: r.top, width: r.width, height: r.height };
    })()`);
    if (!caja) {
      console.error(`FALTA ${foco} en ${ruta}`);
      process.exitCode = 1;
      continue;
    }
    await espera(400);
    const r = await cdp("Page.captureScreenshot", { format: "webp", quality: 82, clip: { ...caja, scale: 1 } });
    writeFileSync(join(salida, `${foco}.webp`), Buffer.from(r.data, "base64"));
    console.log("OK", foco, `${Math.round(caja.width)}×${Math.round(caja.height)}`);
    total += 1;
  }
}
console.log(total, "capturas en", salida);
ws.close();
edge.kill();
