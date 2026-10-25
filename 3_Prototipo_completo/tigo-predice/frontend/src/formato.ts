const num = new Intl.NumberFormat("es-HN", { maximumFractionDigits: 0 });

export const entero = (v: number) => num.format(Math.round(v));

export const lempiras = (v: number) => `L ${num.format(Math.round(v))}`;

/** L 22.2 M, L 850 mil, L 7,583 */
export const lempirasCorto = (v: number) => {
  const a = Math.abs(v);
  if (a >= 1_000_000) return `L ${(v / 1_000_000).toLocaleString("es-HN", { maximumFractionDigits: 1 })} M`;
  if (a >= 100_000) return `L ${num.format(Math.round(v / 1000))} mil`;
  return lempiras(v);
};

/** Redondea a N cifras significativas (evita la falsa precisión). */
export function sig(v: number, cifras = 2): number {
  if (v === 0 || !Number.isFinite(v)) return v;
  const e = Math.floor(Math.log10(Math.abs(v)));
  const f = Math.pow(10, cifras - 1 - e);
  return Math.round(v * f) / f;
}

/** Lempiras a 2 cifras significativas: "L 5.1 M", "L 520 mil", "−L 1.5 M". */
export function lempirasSig(v: number): string {
  const r = sig(v);
  const signo = r < 0 ? "−" : "";
  const a = Math.abs(r);
  if (a >= 1e6) return `${signo}L ${(a / 1e6).toLocaleString("es-HN", { maximumFractionDigits: 1 })} M`;
  if (a >= 1e4) return `${signo}L ${num.format(a / 1e3)} mil`;
  return `${signo}L ${num.format(a)}`;
}

export const rangoL = (a: number, b: number) => {
  const [lo, hi] = a <= b ? [a, b] : [b, a];
  return `${lempirasSig(lo)} a ${lempirasSig(hi)}`;
};

export const enteroSig = (v: number) => num.format(sig(v));

export const pct = (v: number, decimales = 0) =>
  `${(v * 100).toLocaleString("es-HN", { maximumFractionDigits: decimales, minimumFractionDigits: decimales })} %`;

/** Probabilidad para mostrar: nunca «100 %» ni «0 %» (un modelo no da certeza absoluta). */
export const pctRiesgo = (v: number) => (v >= 0.995 ? "> 99 %" : v > 0 && v < 0.005 ? "< 1 %" : pct(v));

export const SEGMENTOS: Record<string, string> = { prepago: "Prepago", pospago: "Pospago", hogar: "Hogar" };

/** Escala secuencial de un solo tono (rojo claro → rojo oscuro) para magnitud de riesgo. */
export const RAMPA_RIESGO = ["#fde7e5", "#f7b4ad", "#ec7468", "#d23a2f", "#9e1a14"];

export function colorRiesgo(p: number, max = 0.25): string {
  const t = Math.max(0, Math.min(1, p / max)) * (RAMPA_RIESGO.length - 1);
  const i = Math.min(Math.floor(t), RAMPA_RIESGO.length - 2);
  const a = hex(RAMPA_RIESGO[i]);
  const b = hex(RAMPA_RIESGO[i + 1]);
  const k = t - i;
  const c = a.map((v, j) => Math.round(v + (b[j] - v) * k));
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
}

const hex = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));

/** Paleta categórica validada (CVD y visión normal) para gráficos con varias series. */
export const SERIES = ["#1E5BBF", "#00A3CC", "#B0479B"];

export const EJES = { stroke: "#94a3b8", fontSize: 12 };
export const GRILLA = "#e8edf4";
