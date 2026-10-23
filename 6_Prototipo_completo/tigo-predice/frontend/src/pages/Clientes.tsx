import { Search, Send, UserRound, X } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, type ClienteDetalle } from "../api";
import { BarraProb, Cargando, ErrorCaja, Factores, Fase2Aviso, PrioridadBadge, Tarjeta } from "../components/ui";
import { SEGMENTOS, entero, lempiras, pct } from "../formato";
import { useDatos } from "../hooks";

const CIUDADES = [
  "Tegucigalpa", "San Pedro Sula", "La Ceiba", "Choluteca", "Comayagua",
  "El Progreso", "Danlí", "Juticalpa", "Santa Rosa de Copán", "Siguatepeque",
];
const ACCIONES: Record<string, string> = {
  aviso_falla: "Aviso de falla",
  autodiagnostico: "Autodiagnóstico",
  retencion_agente: "Agente de retención",
  oferta_retencion: "Oferta de retención",
  recordatorio_pago: "Recordatorio de pago",
  monitorear: "Monitorear",
  no_molestar: "No molestar",
  esperar: "Esperar (anti-fatiga)",
  no_contactar: "No contactar (opt-out)",
};
const POR_PAGINA = 25;

export default function Clientes() {
  const [f, setF] = useState({ prioridad: "Alta", ciudad: "", segmento: "", accion: "", q: "" });
  const [pagina, setPagina] = useState(0);
  const [detalle, setDetalle] = useState<ClienteDetalle | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const navegar = useNavigate();
  const lista = useDatos(() => api.clientes({ ...f, limite: POR_PAGINA, offset: pagina * POR_PAGINA }), [
    JSON.stringify(f),
    pagina,
  ]);

  const cambiar = (k: keyof typeof f, v: string) => {
    setF({ ...f, [k]: v });
    setPagina(0);
  };

  const ejecutar = async (id: string) => {
    try {
      await api.ejecutar(id);
      navegar("/whatsapp", { state: { cliente: id } });
    } catch (e) {
      setMensaje((e as Error).message);
    }
  };

  const selector = (k: keyof typeof f, opciones: Record<string, string> | string[], todos: string) => (
    <select
      aria-label={todos}
      value={f[k]}
      onChange={(e) => cambiar(k, e.target.value)}
      className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
    >
      <option value="">{todos}</option>
      {(Array.isArray(opciones) ? opciones.map((o) => [o, o]) : Object.entries(opciones)).map(([v, t]) => (
        <option key={v} value={v}>
          {t}
        </option>
      ))}
    </select>
  );

  return (
    <div className="space-y-4">
      <Fase2Aviso />
      <div>
        <h1 className="text-2xl font-bold text-slate-900 lg:text-3xl">Clientes en riesgo</h1>
        <p className="text-slate-500">
          Ordenados por <b>valor en riesgo</b> = probabilidad × valor del cliente (en Lempiras). Cada uno con su
          explicación y la mejor acción.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {selector("prioridad", { Alta: "Prioridad alta", Media: "Prioridad media", Baja: "Prioridad baja" }, "Todas las prioridades")}
        {selector("ciudad", CIUDADES, "Todas las ciudades")}
        {selector("segmento", SEGMENTOS, "Todos los segmentos")}
        {selector("accion", ACCIONES, "Todas las acciones")}
        <label className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm">
          <Search size={16} className="text-slate-400" />
          <input
            value={f.q}
            onChange={(e) => cambiar("q", e.target.value)}
            placeholder="Nombre o código"
            className="w-40 outline-none"
          />
        </label>
        <span className="ml-auto text-sm text-slate-500">{lista.datos ? `${entero(lista.datos.total)} clientes` : ""}</span>
      </div>

      {mensaje && (
        <div className="rounded-xl bg-ambar/10 px-4 py-2 text-sm text-amber-900">
          {mensaje}{" "}
          <button className="ml-2 underline" onClick={() => setMensaje(null)}>
            cerrar
          </button>
        </div>
      )}
      {lista.error && <ErrorCaja error={lista.error} />}

      <Tarjeta className="overflow-x-auto">
        <table className="w-full min-w-[960px] text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">Cliente</th>
              <th className="px-3 py-3">Llamará (7 d)</th>
              <th className="px-3 py-3">Abandono (30 d)</th>
              <th className="px-3 py-3 text-right">L en riesgo</th>
              <th className="px-3 py-3">Prioridad</th>
              <th className="px-3 py-3">¿Por qué? (IA explicable)</th>
              <th className="px-3 py-3">Acción recomendada</th>
              <th className="px-3 py-3" />
            </tr>
          </thead>
          <tbody>
            {lista.cargando && !lista.datos && (
              <tr>
                <td colSpan={8}>
                  <Cargando />
                </td>
              </tr>
            )}
            {lista.datos?.clientes.map((c) => (
              <tr
                key={c.cliente_id}
                onClick={() => api.cliente(c.cliente_id).then(setDetalle)}
                className="cursor-pointer border-t border-slate-100 hover:bg-celeste-50/60"
              >
                <td className="px-4 py-3">
                  <div className="font-semibold text-slate-800">{c.nombre}</div>
                  <div className="text-xs text-slate-500">
                    {c.cliente_id} · {SEGMENTOS[c.segmento]} · {c.ciudad}
                  </div>
                </td>
                <td className="px-3 py-3">
                  <BarraProb p={c.prob_incidencia} />
                </td>
                <td className="px-3 py-3">
                  <BarraProb p={c.prob_churn} />
                </td>
                <td className="whitespace-nowrap px-3 py-3 text-right font-semibold tabular-nums">{lempiras(c.valor_en_riesgo)}</td>
                <td className="px-3 py-3">
                  <PrioridadBadge p={c.prioridad} />
                </td>
                <td className="px-3 py-3">
                  <Factores factores={c.factores} compacto />
                </td>
                <td className="px-3 py-3">
                  <div className="font-medium text-tigo">{c.accion_nombre}</div>
                  <div className="max-w-[190px] text-xs text-slate-500">{c.motivo_accion}</div>
                </td>
                <td className="px-3 py-3">
                  {c.contactable && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        ejecutar(c.cliente_id);
                      }}
                      className="flex items-center gap-1 whitespace-nowrap rounded-lg bg-tigo px-3 py-1.5 text-xs font-semibold text-white hover:bg-tigo-700"
                    >
                      <Send size={13} /> Ejecutar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Tarjeta>

      <div className="flex items-center justify-end gap-2 text-sm">
        <button
          disabled={pagina === 0}
          onClick={() => setPagina(pagina - 1)}
          className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 disabled:opacity-40"
        >
          ← Anterior
        </button>
        <span className="text-slate-500">Página {pagina + 1}</span>
        <button
          disabled={!lista.datos || (pagina + 1) * POR_PAGINA >= lista.datos.total}
          onClick={() => setPagina(pagina + 1)}
          className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 disabled:opacity-40"
        >
          Siguiente →
        </button>
      </div>

      {detalle && <Detalle c={detalle} cerrar={() => setDetalle(null)} ejecutar={ejecutar} />}
    </div>
  );
}

const VARIABLES_CLAVE: [string, string, (v: number) => string][] = [
  ["caidas_7d", "Caídas de señal (7 días)", (v) => entero(v)],
  ["velocidad_pct_plan_7d", "Velocidad vs. contratada", (v) => pct(v)],
  ["tendencia_uso", "Tendencia de consumo", (v) => `${v > 0 ? "+" : ""}${pct(v)}`],
  ["dias_atraso", "Días de atraso en pago", (v) => entero(v)],
  ["llamadas_30d", "Llamadas al call center (30 d)", (v) => entero(v)],
  ["llamadas_sin_resolver_30d", "Llamadas sin resolver (30 d)", (v) => entero(v)],
  ["nps_ultimo", "Última calificación NPS", (v) => `${v}/10`],
];

function Detalle({ c, cerrar, ejecutar }: { c: ClienteDetalle; cerrar: () => void; ejecutar: (id: string) => void }) {
  return (
    <div className="fixed inset-0 z-[1000] flex justify-end bg-slate-900/30" onClick={cerrar}>
      <div className="aparecer h-full w-full max-w-lg overflow-y-auto bg-white p-6 shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-tigo/10 p-3 text-tigo">
              <UserRound />
            </div>
            <div>
              <div className="text-xl font-bold">{c.nombre}</div>
              <div className="text-sm text-slate-500">
                {c.cliente_id} · {c.telefono} · {c.plan}
              </div>
              <div className="text-sm text-slate-500">
                {c.ciudad} (celda {c.celda_id}) · {c.antiguedad_meses} meses con Tigo
              </div>
            </div>
          </div>
          <button onClick={cerrar} aria-label="Cerrar" className="rounded-lg p-1 hover:bg-slate-100">
            <X />
          </button>
        </div>

        <div className="mt-5 grid grid-cols-3 gap-3 text-center">
          <div className="rounded-xl bg-slate-50 p-3">
            <div className="text-xs text-slate-500">Llamará (7 d)</div>
            <div className="text-xl font-bold">{pct(c.prob_incidencia)}</div>
          </div>
          <div className="rounded-xl bg-slate-50 p-3">
            <div className="text-xs text-slate-500">Abandono (30 d)</div>
            <div className="text-xl font-bold">{pct(c.prob_churn)}</div>
          </div>
          <div className="rounded-xl bg-slate-50 p-3">
            <div className="text-xs text-slate-500">Valor de vida</div>
            <div className="text-xl font-bold">{lempiras(c.clv)}</div>
          </div>
        </div>

        <h3 className="mt-6 font-semibold text-tigo">¿Por qué podría llamar?</h3>
        <div className="mt-2">
          <Factores factores={c.factores_incidencia} />
        </div>
        <h3 className="mt-4 font-semibold text-tigo">¿Por qué podría irse?</h3>
        <div className="mt-2">
          <Factores factores={c.factores_churn} />
        </div>

        <h3 className="mt-6 font-semibold text-tigo">Datos clave</h3>
        <dl className="mt-2 divide-y divide-slate-100 text-sm">
          {VARIABLES_CLAVE.map(([k, t, fmt]) => (
            <div key={k} className="flex justify-between py-1.5">
              <dt className="text-slate-500">{t}</dt>
              <dd className="font-medium">{c.variables[k] === null ? "Sin encuesta" : fmt(c.variables[k] as number)}</dd>
            </div>
          ))}
        </dl>

        <div className="mt-6 rounded-xl border border-tigo/20 bg-tigo/5 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Mejor acción</div>
          <div className="text-lg font-bold text-tigo">{c.accion_nombre}</div>
          <div className="text-sm text-slate-600">{c.motivo_accion}</div>
          {c.humano && <div className="mt-1 text-xs text-slate-500">👤 Humano en el circuito: un agente decide la oferta.</div>}
          {c.contactable && (
            <button
              onClick={() => ejecutar(c.cliente_id)}
              className="mt-3 flex items-center gap-2 rounded-xl bg-tigo px-4 py-2 text-sm font-semibold text-white"
            >
              <Send size={16} /> Ejecutar acción
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
