import clsx from "clsx";
import { Radio, Router, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import type { Factor, Prioridad } from "../api";
import { colorRiesgo, pct } from "../formato";

/**
 * `desplazable`: nombre de la región cuando el contenido se desplaza a lo ancho; así se puede recorrer con el teclado.
 * `foco`: nombre con el que la vista simple del modo presentación resalta esta tarjeta (ver `resaltar` en escenas.ts).
 */
export function Tarjeta({ children, className, desplazable, foco }: { children: ReactNode; className?: string; desplazable?: string; foco?: string }) {
  if (!desplazable) return <div data-foco={foco} className={clsx("tarjeta", className)}>{children}</div>;
  return (
    <div role="region" aria-label={desplazable} tabIndex={0} data-foco={foco}
      className={clsx("tarjeta overflow-x-auto focus:outline-none focus-visible:ring-2 focus-visible:ring-celeste", className)}>
      {children}
    </div>
  );
}

export function Titulo({ children, extra }: { children: ReactNode; extra?: ReactNode }) {
  return (
    <div className="mb-3 flex items-center justify-between gap-3">
      <h2 className="text-lg font-semibold text-tigo">{children}</h2>
      {extra}
    </div>
  );
}

export function Kpi({
  icono: Icono,
  titulo,
  valor,
  detalle,
  acento = "tigo",
  destacar,
}: {
  icono: LucideIcon;
  titulo: string;
  valor: string;
  detalle?: ReactNode;
  acento?: "tigo" | "alerta" | "exito" | "celeste";
  destacar?: boolean;
}) {
  const colores = {
    tigo: "bg-tigo/10 text-tigo",
    alerta: "bg-alerta/10 text-alerta",
    exito: "bg-exito/10 text-exito",
    celeste: "bg-celeste/15 text-tigo-700",
  };
  return (
    <Tarjeta className={clsx("p-4", destacar && "destello")}>
      <div className="flex items-center gap-2">
        <div className={clsx("rounded-lg p-1.5", colores[acento])}>
          <Icono size={18} />
        </div>
        <div className="text-sm font-medium leading-tight text-slate-500">{titulo}</div>
      </div>
      <div className="mt-2 whitespace-nowrap text-[1.7rem] font-bold leading-none tracking-tight text-slate-900 tabular-nums 2xl:text-3xl">
        {valor}
      </div>
      {detalle && <div className="mt-1.5 text-xs text-slate-500">{detalle}</div>}
    </Tarjeta>
  );
}

export function PrioridadBadge({ p }: { p: Prioridad }) {
  const estilos = {
    Alta: "bg-alerta text-white",
    Media: "bg-ambar/20 text-amber-800",
    Baja: "bg-slate-100 text-slate-600",
  };
  return <span className={clsx("rounded-full px-2.5 py-0.5 text-xs font-semibold", estilos[p])}>{p}</span>;
}

const COLOR_GRUPO: Record<string, string> = {
  Red: "bg-red-50 text-red-700 ring-red-200",
  Equipo: "bg-orange-50 text-orange-700 ring-orange-200",
  Uso: "bg-violet-50 text-violet-700 ring-violet-200",
  Facturación: "bg-amber-50 text-amber-800 ring-amber-200",
  Atención: "bg-sky-50 text-sky-700 ring-sky-200",
  Satisfacción: "bg-pink-50 text-pink-700 ring-pink-200",
  Perfil: "bg-slate-50 text-slate-700 ring-slate-200",
};

export function Factores({ factores, compacto }: { factores: Factor[]; compacto?: boolean }) {
  if (!factores.length) return <span className="text-xs text-slate-400">Sin factores relevantes</span>;
  return (
    <div className={clsx("flex flex-wrap gap-1.5", compacto && "max-w-md")}>
      {factores.map((f) => (
        <span
          key={f.variable}
          title={`${f.grupo} · impacto ${f.impacto.toFixed(2)}`}
          className={clsx("rounded-md px-2 py-0.5 text-xs ring-1", COLOR_GRUPO[f.grupo] ?? COLOR_GRUPO.Perfil)}
        >
          {f.texto}
        </span>
      ))}
    </div>
  );
}

export function BarraProb({ p, max = 1, etiqueta }: { p: number; max?: number; etiqueta?: string }) {
  return (
    <div className="flex items-center gap-2" title={etiqueta}>
      <div className="h-2 w-12 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full rounded-full" style={{ width: `${Math.min(100, (p / max) * 100)}%`, background: colorRiesgo(p, max * 0.6) }} />
      </div>
      <span className="w-10 text-right text-sm tabular-nums text-slate-700">{pct(p)}</span>
    </div>
  );
}

export function Fase2Aviso() {
  return (
    <div className="rounded-xl border border-slate-300 bg-slate-50 px-4 py-2.5 text-sm text-slate-600">
      <b>Fase 2 · visión.</b> Churn, retención y cobros: no entran al piloto ni al caso de negocio hasta que se midan con
      grupo control. Se muestra para enseñar hacia dónde puede crecer la plataforma.
    </div>
  );
}

export type Frente = "hogar" | "movil";
const PESTANAS = [
  { k: "hogar", t: "Hogar (atención proactiva)", I: Router },
  { k: "movil", t: "Móvil (fallas masivas)", I: Radio },
] as const;

export function Pestanas({ valor, onCambio }: { valor: Frente; onCambio: (v: Frente) => void }) {
  return (
    <div className="inline-flex flex-wrap rounded-xl bg-slate-100 p-1" role="tablist">
      {PESTANAS.map(({ k, t, I }) => (
        <button key={k} role="tab" aria-selected={valor === k} onClick={() => onCambio(k)}
          className={clsx("flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold", valor === k ? "bg-white text-tigo shadow" : "text-slate-500 hover:text-tigo")}>
          <I size={16} /> {t}
        </button>
      ))}
    </div>
  );
}

export function Cargando({ texto = "Cargando…" }: { texto?: string }) {
  return <div className="p-8 text-center text-slate-400">{texto}</div>;
}

export function ErrorCaja({ error }: { error: string }) {
  return (
    <div className="rounded-xl border border-alerta/30 bg-alerta/5 p-4 text-sm text-alerta">
      No se pudo cargar la información: {error}. ¿Está corriendo el servidor? (iniciar_demo.bat)
    </div>
  );
}
