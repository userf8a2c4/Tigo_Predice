import { describe, expect, it } from "vitest";
import { casoNegocio, LIMITES, type ConfigNegocio } from "../roi";
import paridad from "./roi_paridad.json";

// Compara dos resultados número por número (tolerancia de redondeo de punto flotante)
function igual(ts: unknown, py: unknown, ruta = "respuesta"): string | null {
  if (typeof py === "number" && typeof ts === "number") {
    const tolerancia = 1e-9 * Math.max(1, Math.abs(py));
    return Math.abs(ts - py) <= tolerancia ? null : `${ruta}: ${ts} ≠ ${py}`;
  }
  if (py === null || typeof py !== "object") return ts === py ? null : `${ruta}: ${String(ts)} ≠ ${String(py)}`;
  if (typeof ts !== "object" || ts === null) return `${ruta}: falta`;
  if (Array.isArray(py)) {
    if (!Array.isArray(ts) || ts.length !== py.length) return `${ruta}: largo distinto`;
    for (let i = 0; i < py.length; i++) {
      const e = igual(ts[i], py[i], `${ruta}[${i}]`);
      if (e) return e;
    }
    return null;
  }
  const a = ts as Record<string, unknown>, b = py as Record<string, unknown>;
  const claves = new Set([...Object.keys(a), ...Object.keys(b)]);
  for (const k of claves) {
    const e = igual(a[k], b[k], `${ruta}.${k}`);
    if (e) return e;
  }
  return null;
}

describe("calculadora del caso de negocio en el navegador (demo sin servidor)", () => {
  const cfg = paridad.config as unknown as ConfigNegocio;

  it.each(paridad.casos.map((c) => [JSON.stringify(c.tus), c] as const))("da lo mismo que Python con %s", (_, caso) => {
    expect(igual(casoNegocio(cfg, caso.tus), caso.respuesta)).toBeNull();
  });

  it("sin datos de Tigo reproduce el caso base publicado (L 4.3 M netos en el año 1)", () => {
    const neto = casoNegocio(cfg).escenarios.base.nacional.neto_anio1;
    expect(neto / 1e6).toBeCloseTo(4.28, 2);
  });

  it("acepta los mismos límites que la API", () => {
    expect(LIMITES).toEqual({
      llamadas_mes_fallas_nacional: 10_000_000,
      costo_por_llamada: 100_000,
      visitas_mes_hogar_nacional: 1_000_000,
      costo_por_visita: 1_000_000,
    });
  });
});
