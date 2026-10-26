import clsx from "clsx";
import { CheckCircle2, FlaskConical, XCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, type Criterio, type Potencia } from "../api";
import { Cargando, ErrorCaja, Pestanas, Tarjeta, Titulo, type Frente } from "../components/ui";
import { EJES, GRILLA, entero, pct } from "../formato";
import { useDatos } from "../hooks";

const ROJO = "#c0262f"; // 6:1 sobre blanco (WCAG 2.2 AA)
const VERDE = "#0f7a43"; // 5.4:1 sobre blanco (WCAG 2.2 AA)

export default function Piloto() {
  const [frente, setFrente] = useState<Frente>("hogar");
  return (
    <div className="space-y-4">
      <Pestanas valor={frente} onCambio={setFrente} />
      {frente === "hogar" ? <PilotoHogar /> : <PilotoMovil />}
    </div>
  );
}

function Decision({ decision, motivo, criterios, titulo }: { decision: "GO" | "NO-GO"; motivo: string; criterios: Criterio[]; titulo: string }) {
  const go = decision === "GO";
  return (
    <Tarjeta foco="piloto-decision" className={clsx("p-5", go ? "ring-2 ring-exito" : "ring-2 ring-alerta")}>
      <Titulo>{titulo}</Titulo>
      <div className={clsx("text-4xl font-extrabold sm:text-5xl", go ? "text-exito" : "text-alerta")}>{decision}</div>
      <p className="mt-1 text-sm text-slate-600">{motivo}</p>
      <ul className="mt-3 space-y-2 text-sm">
        {criterios.map((c) => (
          <li key={c.criterio} className="flex items-start gap-2">
            {c.cumple ? <CheckCircle2 size={18} className="shrink-0 text-exito" /> : <XCircle size={18} className="shrink-0 text-alerta" />}
            <span>{c.criterio} <b className="text-slate-800">({c.valor})</b></span>
          </li>
        ))}
      </ul>
    </Tarjeta>
  );
}

function PilotoHogar() {
  const { datos: r, error } = useDatos(api.pilotoHogar);
  if (error) return <ErrorCaja error={error} />;
  if (!r) return <Cargando />;
  const n = r.metrica_norte;
  const ll = r.llamadas;
  const pot = r.potencia;
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 lg:text-3xl">Piloto Hogar: hogares marcados, tratados vs. control</h1>
        <p className="text-slate-500">
          {r.ciudad} · {r.dias} días · {entero(r.hogares_piloto)} hogares (supuesto) · la IA marca {entero(r.marcados_por_semana)} por semana ·{" "}
          {entero(r.marcados)} marcados en total · métrica norte: visitas técnicas por cada 1,000 hogares marcados en los 7 días siguientes.
        </p>
      </div>
      <div className="flex items-start gap-3 rounded-xl border border-ambar/40 bg-ambar/10 p-3 text-sm text-amber-900">
        <FlaskConical size={18} className="mt-0.5 shrink-0" />
        <span><b>{r.aviso}</b> Los hogares, la telemetría y el riesgo de la IA salen de los datos sintéticos fuera de muestra.</span>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Tarjeta className="p-5 xl:col-span-2">
          <Titulo>Métrica norte: visitas técnicas</Titulo>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <Grupo t="Sin acción (control)" v={n.por_1000_control} n={n.n_control} color={ROJO} unidad="visitas por 1,000 marcados" />
            <Grupo t="Con atención proactiva" v={n.por_1000_tratamiento} n={n.n_tratamiento} color={VERDE} unidad="visitas por 1,000 marcados" />
            <div className="rounded-xl bg-tigo p-4 text-white">
              <div className="text-sm text-white/70">Reducción de visitas</div>
              <div className="text-3xl font-extrabold tabular-nums sm:text-4xl">{pct(n.reduccion_relativa)}</div>
              <div className="text-sm text-white/80">IC 95 %: {pct(n.ic_reduccion_relativa[0])} a {pct(n.ic_reduccion_relativa[1])}</div>
              <div className="text-xs text-white/60">valor p {n.valor_p < 0.001 ? "< 0.001" : n.valor_p.toFixed(3)}</div>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
            <Grupo t="Llamadas técnicas · control" v={ll.por_1000_control} n={ll.n_control} color={ROJO} unidad="llamadas por 1,000 marcados" />
            <Grupo t="Llamadas técnicas · tratados" v={ll.por_1000_tratamiento} n={ll.n_tratamiento} color={VERDE} unidad="llamadas por 1,000 marcados" />
            <div className="rounded-xl border border-slate-200 p-4">
              <div className="text-sm text-slate-500">Reducción de llamadas</div>
              <div className="text-3xl font-extrabold tabular-nums text-exito">{pct(ll.reduccion_relativa)}</div>
              <div className="text-xs text-slate-500">IC 95 %: {pct(ll.ic_reduccion_relativa[0])} a {pct(ll.ic_reduccion_relativa[1])}</div>
            </div>
          </div>
          <p className="mt-3 text-sm text-slate-600">
            En el piloto simulado: ≈ <b>{entero(r.visitas_evitadas_estimadas)}</b> visitas y <b>{entero(r.llamadas_evitadas_estimadas)}</b> llamadas
            evitadas en 60 días. Las visitas por problemas físicos se siguen haciendo (antes del corte y con diagnóstico): por eso la
            reducción de visitas es menor que la de llamadas.
          </p>
        </Tarjeta>
        <Decision titulo="Decisión al día 60" {...r.decision} />
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <Tarjeta className="p-4">
          <Titulo>Visitas por 1,000 hogares marcados, semana a semana</Titulo>
          <div className="h-[clamp(220px,34vh,380px)]">
            <ResponsiveContainer>
              <BarChart data={r.por_semana} margin={{ left: 0, right: 8, top: 8 }} barGap={2}>
                <CartesianGrid stroke={GRILLA} vertical={false} />
                <XAxis dataKey="semana" {...EJES} tickFormatter={(s) => `S${s}`} />
                <YAxis {...EJES} width={40} />
                <Tooltip formatter={(v, nombre) => [entero(Number(v)), nombre]} labelFormatter={(s) => `Semana ${s}`} />
                <Legend />
                <Bar isAnimationActive={false} dataKey="control_por_1000" name="Sin acción (control)" fill={ROJO} radius={[4, 4, 0, 0]} />
                <Bar isAnimationActive={false} dataKey="tratamiento_por_1000" name="Con atención proactiva" fill={VERDE} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500">Cada semana la IA marca a otros hogares; el grupo de cada hogar se decide por hash (siempre el mismo).</p>
        </Tarjeta>
        <Tarjeta className="p-5">
          <Titulo>Tamaño de muestra y poder estadístico</Titulo>
          <div className="grid grid-cols-2 gap-3">
            <Dato t="Hogares marcados necesarios" v={entero(pot.afectados_necesarios)} s={`para detectar −${pct(pot.reduccion_a_detectar)} · ${entero(pot.control_necesario)} en control`} />
            <Dato t="Días necesarios" v={String(pot.dias_necesarios)} s={`al ritmo de ${entero(r.marcados_por_semana)} marcados por semana`} />
            <Dato t="Poder con el piloto" v={pct(pot.poder_alcanzado)} s={`objetivo ${pct(pot.poder_objetivo)}`} ok={pot.poder_alcanzado >= pot.poder_objetivo} />
            <Dato t="Opt-out de mensajes" v={pct(r.secundarias.tasa_optout, 2)} s="meta < 2 %" />
          </div>
          <p className="mt-3 text-xs text-slate-500">{pot.nota}</p>
        </Tarjeta>
      </div>
    </div>
  );
}

function PilotoMovil() {
  const { datos: r, error } = useDatos(api.piloto);
  if (error) return <ErrorCaja error={error} />;
  if (!r) return <Cargando />;
  const n = r.metrica_norte;
  const s = r.secundarias;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 lg:text-3xl">Piloto Móvil: tratados vs. control</h1>
        <p className="text-slate-500">
          {r.ciudad} · {r.dias} días · {r.fallas} fallas masivas · {entero(r.afectados)} afectados · métrica norte: llamadas al
          call center por cada 1,000 afectados en las 72 h posteriores a la falla.
        </p>
      </div>
      <div className="flex items-start gap-3 rounded-xl border border-ambar/40 bg-ambar/10 p-3 text-sm text-amber-900">
        <FlaskConical size={18} className="mt-0.5 shrink-0" />
        <span><b>{r.aviso}</b> El piloto real reemplaza estos números por los medidos.</span>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Tarjeta className="p-5 xl:col-span-2">
          <Titulo>Métrica norte</Titulo>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <Grupo t="Sin aviso (control)" v={n.por_1000_control} n={n.n_control} color={ROJO} />
            <Grupo t="Con aviso (tratamiento)" v={n.por_1000_tratamiento} n={n.n_tratamiento} color={VERDE} />
            <div className="rounded-xl bg-tigo p-4 text-white">
              <div className="text-sm text-white/70">Reducción de llamadas</div>
              <div className="text-3xl font-extrabold tabular-nums sm:text-4xl">{pct(n.reduccion_relativa)}</div>
              <div className="text-sm text-white/80">IC 95 %: {pct(n.ic_reduccion_relativa[0])} a {pct(n.ic_reduccion_relativa[1])}</div>
              <div className="text-xs text-white/60">valor p {n.valor_p < 0.001 ? "< 0.001" : n.valor_p.toFixed(3)}</div>
            </div>
          </div>
          <p className="mt-3 text-sm text-slate-600">
            Diferencia: <b>{entero(n.diferencia_por_1000)}</b> llamadas por 1,000 afectados (IC 95 %{" "}
            {entero(n.ic_diferencia_por_1000[0])} a {entero(n.ic_diferencia_por_1000[1])}). Análisis por intención de tratar:
            se compara a todos los asignados, aunque no hayan leído el aviso. Secundario: llama el{" "}
            {pct(r.pct_que_llama.tasa_tratamiento)} de los avisados vs. {pct(r.pct_que_llama.tasa_control)} del control.
          </p>
        </Tarjeta>

        <Decision titulo="Decisión al día 60" {...r.decision} />
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <Tarjeta className="p-4">
          <Titulo>Llamadas por 1,000 afectados en cada falla</Titulo>
          <div className="h-[clamp(220px,34vh,380px)]">
            <ResponsiveContainer>
              <BarChart data={r.por_falla} margin={{ left: 0, right: 8, top: 8 }} barGap={2}>
                <CartesianGrid stroke={GRILLA} vertical={false} />
                <XAxis dataKey="falla" {...EJES} tickFormatter={(f) => `F${f}`} />
                <YAxis {...EJES} width={40} />
                <Tooltip formatter={(v, nombre) => [entero(Number(v)), nombre]} labelFormatter={(f) => `Falla ${f}`} />
                <Legend />
                <Bar isAnimationActive={false} dataKey="control_por_1000" name="Sin aviso (control)" fill={ROJO} radius={[4, 4, 0, 0]} />
                <Bar isAnimationActive={false} dataKey="tratamiento_por_1000" name="Con aviso" fill={VERDE} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500">Cada falla es distinta (duración, hora, si el NOC tiene hora estimada); por eso se mide con muchas fallas y grupo control.</p>
        </Tarjeta>

        <Tarjeta className="p-4">
          <Titulo>Métricas secundarias</Titulo>
          <table className="w-full text-sm">
            <thead><tr className="text-left text-xs text-slate-500"><th className="pb-1" /><th className="pb-1">Con aviso</th><th className="pb-1">Control</th></tr></thead>
            <tbody className="divide-y divide-slate-100">
              <Fila t="CSAT de afectados (1 a 5)" a={String(s.csat_tratamiento)} b={String(s.csat_control)} />
              <Fila t="Reclamos repetidos (2+ llamadas)" a={pct(Number(s.reclamos_repetidos_tratamiento), 1)} b={pct(Number(s.reclamos_repetidos_control), 1)} />
              <Fila t="Tiempo al primer contacto de Tigo" a={`${s.minutos_al_primer_contacto_tratamiento} min`} b={String(s.minutos_al_primer_contacto_control)} />
              <tr><td className="py-2 text-slate-600">Opt-out de mensajes</td><td colSpan={2} className="py-2 font-semibold">{pct(Number(s.tasa_optout), 2)}</td></tr>
              <tr><td className="py-2 text-slate-600">Costo de compensaciones</td><td colSpan={2} className="py-2 font-semibold">L {entero(Number(s.costo_compensaciones))} (con tope)</td></tr>
              <tr><td className="py-2 text-slate-600">Quejas por mensajes</td><td colSpan={2} className="py-2 font-semibold">{String(s.quejas_por_mensaje)}</td></tr>
            </tbody>
          </table>
        </Tarjeta>
      </div>

      <Calculadora inicial={r.potencia} />
    </div>
  );
}

function Grupo({ t, v, n, color, unidad }: { t: string; v: number; n: number; color: string; unidad?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 p-4">
      <div className="text-sm font-semibold" style={{ color }}>{t}</div>
      <div className="text-3xl font-extrabold tabular-nums sm:text-4xl" style={{ color }}>{entero(v)}</div>
      <div className="text-xs text-slate-500">{unidad ?? "llamadas por 1,000 afectados"} · {entero(n)} {unidad ? "hogares" : "afectados"}</div>
    </div>
  );
}

function Fila({ t, a, b }: { t: string; a: string; b: string }) {
  return (
    <tr>
      <td className="py-2 text-slate-600">{t}</td>
      <td className="py-2 font-semibold text-exito">{a}</td>
      <td className="py-2 font-semibold text-slate-700">{b}</td>
    </tr>
  );
}

function Calculadora({ inicial }: { inicial: Potencia }) {
  const [v, setV] = useState({ tasa_base: inicial.tasa_base, reduccion: inicial.reduccion_a_detectar,
    pct_control: inicial.pct_control, afectados: inicial.afectados_esperados_piloto });
  const [res, setRes] = useState<Potencia>(inicial);
  useEffect(() => {
    const t = setTimeout(() => api.potencia(v).then(setRes).catch(() => undefined), 150);
    return () => clearTimeout(t);
  }, [v]);
  const campos: [keyof typeof v, string, number, number, number, (x: number) => string][] = [
    ["tasa_base", "% de afectados que llama sin aviso", 0.1, 0.6, 0.01, (x) => pct(x)],
    ["reduccion", "Reducción mínima a detectar", 0.05, 0.4, 0.01, (x) => pct(x)],
    ["pct_control", "Tamaño del grupo control", 0.05, 0.3, 0.01, (x) => pct(x)],
    ["afectados", "Afectados esperados en 60 días", 5000, 100000, 1000, (x) => entero(x)],
  ];
  return (
    <Tarjeta className="p-5">
      <Titulo>Calculadora de tamaño de muestra y poder estadístico</Titulo>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_1fr]">
        <div className="space-y-4">
          {campos.map(([k, t, min, max, paso, fmt]) => (
            <div key={k}>
              <div className="flex justify-between text-sm"><label htmlFor={k} className="font-medium text-slate-700">{t}</label><b className="text-tigo">{fmt(v[k])}</b></div>
              <input id={k} type="range" min={min} max={max} step={paso} value={v[k]} onChange={(e) => setV({ ...v, [k]: Number(e.target.value) })} className="w-full accent-tigo" />
            </div>
          ))}
        </div>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Dato t="Afectados necesarios" v={entero(res.afectados_necesarios)} s={`${entero(res.control_necesario)} en control`} />
            <Dato t="Días necesarios" v={String(res.dias_necesarios)} s="al ritmo esperado de fallas" />
            <Dato t="Poder con los afectados esperados" v={pct(res.poder_alcanzado)} s={`objetivo ${pct(res.poder_objetivo)}`} ok={res.poder_alcanzado >= res.poder_objetivo} />
            <Dato t="Nivel de significancia" v={`α = ${res.alfa}`} s="prueba bilateral" />
          </div>
          <p className="text-xs text-slate-500">{res.nota}</p>
        </div>
      </div>
    </Tarjeta>
  );
}

function Dato({ t, v, s, ok }: { t: string; v: string; s: string; ok?: boolean }) {
  return (
    <div className={clsx("rounded-xl border p-3", ok === false ? "border-alerta/40 bg-alerta/5" : "border-slate-200")}>
      <div className="text-xs text-slate-500">{t}</div>
      <div className="text-2xl font-extrabold tabular-nums text-slate-900">{v}</div>
      <div className="text-xs text-slate-500">{s}</div>
    </div>
  );
}
