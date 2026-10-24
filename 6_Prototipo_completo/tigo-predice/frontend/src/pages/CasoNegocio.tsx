import clsx from "clsx";
import { Calculator, RotateCcw } from "lucide-react";
import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ESTATICO, api, type Escenario } from "../api";
import { Cargando, ErrorCaja, Tarjeta, Titulo } from "../components/ui";
import { EJES, GRILLA, SERIES, enteroSig, lempirasSig, pct, rangoL } from "../formato";
import { useAncho, useConfig, useDatos } from "../hooks";

export const NOMBRES_SUPUESTOS: Record<string, string> = {
  fallas_mes_piloto: "Fallas masivas por mes (ciudad piloto)",
  afectados_por_falla: "Afectados por falla",
  afectados_mes_nacional: "Afectados por mes (nacional)",
  tasa_llamada_72h: "% de afectados que llama en 72 h",
  llamadas_por_cliente_que_llama: "Llamadas por cliente que llama",
  reduccion_con_aviso: "Reducción de llamadas con aviso",
  tasa_entrega: "% que recibe y lee el aviso",
  costo_por_llamada: "Costo por llamada",
  tipo_cambio: "Tipo de cambio",
  costo_whatsapp_mensaje: "Costo por mensaje de WhatsApp",
  desarrollo_piloto: "Desarrollo e integración del piloto",
  equipo_piloto: "Equipo del piloto (60 días)",
  infraestructura_mes: "Infraestructura por mes",
  desarrollo_nacional: "Integración nacional (una vez)",
  operacion_anual: "Operación y mantenimiento por año",
  pct_compensados: "% de afectados compensados",
  costo_compensacion: "Costo por compensación",
  hogares_piloto: "Hogares en la ciudad piloto",
  tasa_visitas_hogar_mes: "Visitas técnicas por hogar al mes",
  pct_visitas_evitables: "% de visitas evitables",
  llamadas_por_visita: "Llamadas por visita",
  captura_modelo_hogar: "% de visitas evitables que la IA anticipa",
  reduccion_visitas_marcados: "Reducción de visitas evitables en marcados",
  costo_por_visita: "Costo por visita técnica",
  desarrollo_hogar_piloto: "Hogar: integración del piloto (CSV)",
  equipo_hogar_piloto: "Hogar: equipo del piloto",
  desarrollo_hogar_nacional: "Hogar: integración nacional (una vez)",
  operacion_hogar_anual: "Hogar: operación incremental por año",
  margen_contribucion: "Margen de contribución",
  churn_incremental_evitado: "Churn evitado (avisados vs. control)",
  arpu_afectado: "ARPU de afectados",
};

const COLUMNAS = ["conservador", "base", "optimista"] as const;
const COSTOS: Record<string, string> = {
  desarrollo_integracion: "Móvil: desarrollo e integración (CSV)",
  equipo_piloto: "Móvil: equipo del piloto",
  infraestructura: "Infraestructura y LLM",
  whatsapp: "Móvil: mensajes de WhatsApp",
  compensaciones: "Móvil: compensaciones (con tope)",
  operacion_y_mantenimiento: "Operación y mantenimiento (plataforma)",
  desarrollo_hogar: "Hogar: telemetría por CSV y modelo",
  equipo_hogar: "Hogar: ingeniería de acceso y soporte N2",
  whatsapp_hogar: "Hogar: mensajes de WhatsApp",
  operacion_hogar: "Hogar: operación incremental",
};
const FUENTE: Record<string, string> = {
  "supuesto a validar": "bg-ambar/15 text-amber-800 ring-ambar/40",
  "benchmark público": "bg-sky-50 text-sky-700 ring-sky-200",
  "dato Tigo": "bg-exito/10 text-exito ring-exito/30",
};
const CAMPOS = [
  { k: "visitas_mes_hogar_nacional", t: "Visitas técnicas de Hogar al mes (todo el país)" },
  { k: "costo_por_visita", t: "Costo por visita técnica (L)" },
  { k: "llamadas_mes_fallas_nacional", t: "Llamadas al mes por fallas masivas de red (todo el país)" },
  { k: "costo_por_llamada", t: "Costo por llamada atendida (L)" },
] as const;
type Clave = (typeof CAMPOS)[number]["k"];

export default function CasoNegocio() {
  const config = useConfig();
  const ancho = useAncho();
  const vacio = { visitas_mes_hogar_nacional: "", costo_por_visita: "", llamadas_mes_fallas_nacional: "", costo_por_llamada: "" };
  const [entrada, setEntrada] = useState<Record<Clave, string>>(vacio);
  const [tus, setTus] = useState<Record<string, number | undefined>>({});
  const { datos, error } = useDatos(() => api.roi(tus), [JSON.stringify(tus)]);

  if (error) return <ErrorCaja error={error} />;
  if (!datos) return <Cargando />;
  const { base: b, conservador: c, optimista: o } = datos.escenarios;
  const usaTus = Object.keys(datos.tus_numeros).length > 0;
  const fila = (t: string, f: (e: Escenario) => string, estilo?: "fuerte" | "seccion") => (
    <tr className={clsx("border-t border-slate-100", estilo === "fuerte" && "font-bold", estilo === "seccion" && "bg-slate-50 text-xs uppercase tracking-wide text-slate-500")}>
      <td className="py-2 pr-3 text-slate-600">{t}</td>
      {COLUMNAS.map((k) => (
        <td key={k} className={clsx("py-2 text-right tabular-nums", k === "base" && "bg-celeste-50/60")}>{f(datos.escenarios[k])}</td>
      ))}
    </tr>
  );
  const tornado = datos.tornado.slice(0, 10).map((t) => ({
    nombre: NOMBRES_SUPUESTOS[t.supuesto] ?? t.supuesto,
    bajo: t.neto_con_bajo - t.neto_base,
    alto: t.neto_con_alto - t.neto_base,
  }));
  const placeholder: Record<Clave, string> = {
    visitas_mes_hogar_nacional: enteroSig(b.hogar.nacional.visitas_mes),
    costo_por_visita: String(b.supuestos.costo_por_visita),
    llamadas_mes_fallas_nacional: enteroSig(b.movil.nacional.llamadas_mes_por_fallas),
    costo_por_llamada: String(b.supuestos.costo_por_llamada),
  };

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 lg:text-3xl">Caso de negocio conservador: Hogar + Móvil</h1>
        <p className="text-slate-500">
          El caso base cuenta <b>solo beneficio duro</b>: visitas técnicas evitadas (Hogar) y llamadas evitadas (Móvil) por su
          costo. La retención y el NPS van aparte, como potencial no incluido. Cifras redondeadas a 2 cifras significativas.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.4fr_1fr]">
        <Tarjeta className="bg-gradient-to-br from-tigo to-tigo-700 p-6 text-white">
          <div className="text-sm text-white/70">Neto del año 1, con inversión (escenario base, ambos frentes)</div>
          <div className="mt-1 text-3xl font-extrabold leading-tight sm:text-4xl lg:text-5xl">{lempirasSig(b.nacional.neto_anio1)}</div>
          <ul className="mt-3 space-y-1.5 text-white/90">
            <li>
              <b>Hogar</b> se paga con solo <b>{pct(b.hogar.nacional.equilibrio_reduccion_anio1)}</b> menos visitas evitables en los hogares
              marcados (caso base {pct(b.supuestos.reduccion_visitas_marcados)}; proveedores 20 % a 60 %).
            </li>
            <li>
              <b>Móvil</b> se paga con solo <b>{pct(b.movil.nacional.equilibrio_reduccion_anio1)}</b> menos llamadas en los avisados (caso
              base {pct(b.supuestos.reduccion_con_aviso)}; el piloto exige ≥ {pct(Number(config?.piloto.go_reduccion_min ?? 0.1))}).
            </li>
          </ul>
          <div className="mt-5 grid grid-cols-2 gap-4 md:grid-cols-4">
            <Dato t="Rango (conservador a optimista)" v={rangoL(c.nacional.neto_anio1, o.nacional.neto_anio1)} />
            <Dato t="Hogar · neto año 1" v={lempirasSig(b.hogar.nacional.neto_anio1)} />
            <Dato t="Móvil · neto año 1" v={lempirasSig(b.movil.nacional.neto_anio1)} />
            <Dato t="Recupera la inversión" v={b.nacional.payback_meses ? `${Math.ceil(b.nacional.payback_meses)} meses` : "no"} />
          </div>
        </Tarjeta>

        <Tarjeta className="p-5">
          <Titulo extra={usaTus ? <span className={clsx("rounded-full px-2 py-0.5 text-xs ring-1", FUENTE["dato Tigo"])}>usando dato Tigo</span> : null}>
            <span className="flex items-center gap-2"><Calculator size={18} /> Pon tus números</span>
          </Titulo>
          <p className="mb-3 text-sm text-slate-500">Cuatro datos reales de Tigo convierten este caso en definitivo. Todo se recalcula al instante.</p>
          {ESTATICO ? (
            <p className="rounded-xl bg-celeste-50 p-3 text-sm text-slate-600">
              En esta versión sin servidor se muestra el caso base. Para recalcular con los datos de Tigo, abra la demo completa
              (<b>iniciar_demo.bat</b>).
            </p>
          ) : (
          <form className="grid grid-cols-1 gap-3 sm:grid-cols-2" onSubmit={(e) => {
            e.preventDefault();
            setTus(Object.fromEntries(CAMPOS.map(({ k }) => [k, entrada[k] ? Number(entrada[k]) : undefined])));
          }}>
            {CAMPOS.map(({ k, t }) => (
              <Campo key={k} id={k} t={t} ph={placeholder[k]} v={entrada[k]} on={(x) => setEntrada({ ...entrada, [k]: x })} />
            ))}
            <div className="flex gap-2 sm:col-span-2">
              <button type="submit" className="rounded-xl bg-tigo px-4 py-2 text-sm font-semibold text-white">Recalcular</button>
              <button type="button" onClick={() => { setEntrada(vacio); setTus({}); }} className="flex items-center gap-1 rounded-xl px-3 py-2 text-sm text-slate-500 hover:text-tigo">
                <RotateCcw size={14} /> Supuestos
              </button>
            </div>
          </form>
          )}
        </Tarjeta>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.2fr_1fr]">
        <Tarjeta className="p-5" desplazable="Escalamiento nacional (anual)">
          <Titulo>Escalamiento nacional (anual)</Titulo>
          <table className="w-full min-w-[520px] text-sm">
            <thead><tr className="text-right text-xs uppercase tracking-wide text-slate-500"><th className="text-left" />{COLUMNAS.map((k) => <th key={k} className="pb-2">{k}</th>)}</tr></thead>
            <tbody>
              {fila("Hogar", () => "", "seccion")}
              {fila("Visitas evitadas al año", (e) => enteroSig(e.hogar.nacional.visitas_evitadas_anio))}
              {fila("Reducción del total de visitas", (e) => pct(e.hogar.nacional.reduccion_total_visitas))}
              {fila("Beneficio duro", (e) => lempirasSig(e.hogar.nacional.beneficio_duro_anio))}
              {fila("Neto año 1", (e) => lempirasSig(e.hogar.nacional.neto_anio1))}
              {fila("Equilibrio (reducción mínima de evitables)", (e) => pct(e.hogar.nacional.equilibrio_reduccion_anio1))}
              {fila("Móvil", () => "", "seccion")}
              {fila("Llamadas evitadas al año", (e) => enteroSig(e.movil.nacional.llamadas_evitadas_anio))}
              {fila("Beneficio duro", (e) => lempirasSig(e.movil.nacional.beneficio_duro_anio))}
              {fila("Neto año 1", (e) => lempirasSig(e.movil.nacional.neto_anio1))}
              {fila("Equilibrio (reducción mínima de llamadas)", (e) => pct(e.movil.nacional.equilibrio_reduccion_anio1))}
              {fila("Total", () => "", "seccion")}
              {fila("Beneficio duro", (e) => lempirasSig(e.nacional.beneficio_duro_anio))}
              {fila("Costo recurrente", (e) => lempirasSig(e.nacional.costo_recurrente_anio))}
              {fila("Inversión única", (e) => lempirasSig(e.nacional.inversion_unica))}
              {fila("Neto año 1", (e) => lempirasSig(e.nacional.neto_anio1), "fuerte")}
              {fila("Neto en régimen (año 2+)", (e) => lempirasSig(e.nacional.neto_regimen_anio))}
            </tbody>
          </table>
          <p className="mt-3 text-xs text-slate-500">
            Los escenarios varían lo que el piloto medirá (efectos) y los costos. El volumen y los costos unitarios son datos de
            Tigo: ingréselos en «Pon tus números». Su incertidumbre se ve en el tornado. Hogar solo carga sus costos incrementales.
          </p>
        </Tarjeta>

        <Tarjeta className="p-5">
          <Titulo>Piloto de 60 días en {b.piloto.ciudad}</Titulo>
          <div className="grid grid-cols-2 gap-3">
            <Mini t="Costo total del piloto" v={lempirasSig(b.piloto.costo_total)} s={rangoL(o.piloto.costo_total, c.piloto.costo_total)} />
            <Mini t="Beneficio duro en 60 días" v={lempirasSig(b.piloto.beneficio_duro)}
              s={`${enteroSig(b.hogar.piloto.visitas_evitadas)} visitas y ${enteroSig(b.movil.piloto.llamadas_evitadas)} llamadas evitadas`} />
          </div>
          <ul className="mt-3 space-y-1 text-sm text-slate-600">
            {Object.entries(b.piloto.costos).map(([k, v]) => (
              <li key={k} className="flex justify-between gap-2"><span>{COSTOS[k] ?? k}</span><b className="tabular-nums">{lempirasSig(v)}</b></li>
            ))}
          </ul>
          <p className="mt-3 rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
            El piloto <b>no busca pagarse en 60 días</b>: busca <b>medir</b> con grupo control si el efecto supera el punto de
            equilibrio. Si da GO, la operación nacional se paga sola.
          </p>
        </Tarjeta>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.4fr_1fr]">
        <Tarjeta className="p-4">
          <Titulo>Sensibilidad: qué supuestos mueven más el neto del año 1</Titulo>
          <div className="h-[clamp(300px,46vh,500px)]">
            <ResponsiveContainer>
              <BarChart data={tornado} layout="vertical" stackOffset="sign" margin={{ left: 8, right: 16 }}>
                <CartesianGrid stroke={GRILLA} horizontal={false} />
                <XAxis type="number" {...EJES} tickFormatter={(v: number) => lempirasSig(v)} />
                <YAxis type="category" dataKey="nombre" width={ancho < 640 ? 120 : 230} {...EJES} tick={{ fontSize: ancho < 640 ? 10 : 12, fill: "#334155" }} />
                <Tooltip formatter={(v, n) => [lempirasSig(Number(v)), n]} />
                <Legend />
                <ReferenceLine x={0} stroke="#334155" />
                <Bar isAnimationActive={false} dataKey="bajo" name="Con su valor bajo" stackId="t" fill={SERIES[0]} />
                <Bar isAnimationActive={false} dataKey="alto" name="Con su valor alto" stackId="t" fill={SERIES[2]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500">Cambio en el neto del año 1 (vs. {lempirasSig(b.nacional.neto_anio1)} del caso base) al mover un supuesto a su extremo.</p>
        </Tarjeta>

        <div className="space-y-5">
          <Tarjeta className="p-5">
            <Titulo>Potencial NO incluido en el caso base</Titulo>
            <div className="text-2xl font-extrabold text-tigo">{lempirasSig(b.potencial_no_incluido.margen_retenido_anio)} al año</div>
            <p className="text-sm text-slate-600">
              Retención, medida con <b>margen de contribución</b> (no ingreso bruto) y solo si el piloto mide menos churn en
              avisados que en control. Tampoco se cuentan las visitas repetidas evitadas ni las llamadas que se evitan al avisar
              problemas físicos. Hasta medirlo, vale cero.
            </p>
          </Tarjeta>
          <Tarjeta className="p-5">
            <Titulo>Costos recurrentes (base, anual)</Titulo>
            <ul className="space-y-1 text-sm text-slate-600">
              {Object.entries(b.nacional.costos_recurrentes).map(([k, v]) => (
                <li key={k} className="flex justify-between gap-2"><span>{COSTOS[k] ?? k}</span><b className="tabular-nums">{lempirasSig(v)}</b></li>
              ))}
              <li className="flex justify-between gap-2 border-t border-slate-100 pt-1"><span>Inversión única de integración (ambos)</span><b className="tabular-nums">{lempirasSig(b.nacional.inversion_unica)}</b></li>
            </ul>
          </Tarjeta>
        </div>
      </div>

      {config && (
        <Tarjeta className="p-5" desplazable="Supuestos y su fuente">
          <Titulo>Supuestos (bajo · base · alto) y su fuente</Titulo>
          <table className="w-full min-w-[900px] text-sm">
            <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-500"><th className="pb-2">Supuesto</th><th>Bajo</th><th>Base</th><th>Alto</th><th>Fuente</th><th>Nota</th></tr></thead>
            <tbody>
              {Object.entries(config.supuestos).map(([k, s]) => {
                const fuente = datos.escenarios.base.fuentes[k] ?? s.fuente;
                return (
                  <tr key={k} className="border-t border-slate-100 align-top">
                    <td className="py-2 pr-3"><div className="font-medium text-slate-800">{NOMBRES_SUPUESTOS[k] ?? k}</div><div className="text-xs text-slate-400">{s.unidad}</div></td>
                    <td className="py-2 tabular-nums">{s.bajo}</td><td className="py-2 font-semibold tabular-nums">{s.base}</td><td className="py-2 tabular-nums">{s.alto}</td>
                    <td className="py-2"><span className={clsx("whitespace-nowrap rounded-full px-2 py-0.5 text-xs ring-1", FUENTE[fuente])}>{fuente}</span></td>
                    <td className="max-w-md py-2 text-xs text-slate-500">{s.nota}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Tarjeta>
      )}
    </div>
  );
}

function Dato({ t, v }: { t: string; v: string }) {
  return (
    <div>
      <div className="text-xs text-white/60">{t}</div>
      <div className="text-xl font-bold tabular-nums">{v}</div>
    </div>
  );
}

function Mini({ t, v, s }: { t: string; v: string; s: string }) {
  return (
    <div className="rounded-xl border border-slate-200 p-3">
      <div className="text-xs text-slate-500">{t}</div>
      <div className="text-2xl font-extrabold tabular-nums text-slate-900">{v}</div>
      <div className="text-xs text-slate-500">{s}</div>
    </div>
  );
}

function Campo({ id, t, ph, v, on }: { id: string; t: string; ph: string; v: string; on: (x: string) => void }) {
  return (
    <div>
      <label htmlFor={id} className="text-sm font-medium text-slate-700">{t}</label>
      <input id={id} type="number" min={0} inputMode="numeric" value={v} placeholder={`supuesto: ${ph}`} onChange={(e) => on(e.target.value)}
        className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-tigo" />
    </div>
  );
}
