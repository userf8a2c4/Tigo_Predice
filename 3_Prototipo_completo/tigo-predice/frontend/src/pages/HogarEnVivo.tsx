import clsx from "clsx";
import { BrainCircuit, CheckCircle2, Play, RotateCcw, Wrench } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { CartesianGrid, ComposedChart, Legend, Line, ReferenceLine, ResponsiveContainer, Tooltip as TT, XAxis, YAxis } from "recharts";
import { api, type Conversacion } from "../api";
import Telefono from "../components/Telefono";
import { Cargando, ErrorCaja, Tarjeta, Titulo } from "../components/ui";
import { EJES, GRILLA, SERIES, entero, pct, pctRiesgo } from "../formato";
import { useDatos, usePideFinal, usePresentacion } from "../hooks";

const ROJO = "#c0262f"; // 6:1 sobre blanco (WCAG 2.2 AA)
const VERDE = "#0f7a43"; // 5.4:1 sobre blanco (WCAG 2.2 AA)
const PASOS = ["Hogar sano", "La IA lo marca", "Diagnóstico", "Acción", "Sin vs. con", "Resultado"];
const SEG_POR_DIA = 2.1;
type Caso = "remoto" | "tecnico";

interface Hito {
  t: number;
  fn: () => void;
}

export default function HogarEnVivo() {
  // En el modo presentación se ocultan los controles y la demo arranca sola en su escena
  const { escena } = usePresentacion();
  const presentando = escena !== null;
  const auto = escena === "demo";
  const [caso, setCaso] = useState<Caso>("remoto");
  const { datos: esc, error } = useDatos(() => api.hogar(caso), [caso]);
  const quiereFinal = usePideFinal();
  const [velocidad, setVelocidad] = useState(1);
  const [corriendo, setCorriendo] = useState(false);
  const [idx, setIdx] = useState(-1); // último día visible (índice en la ventana)
  const [paso, setPaso] = useState(-1);
  const [narracion, setNarracion] = useState("Presione ▶ para ver cómo la IA cuida un hogar antes de que el cliente llame.");
  const [diagnostico, setDiagnostico] = useState(false);
  const [acciones, setAcciones] = useState(0);
  const [mensaje, setMensaje] = useState(false);
  const [final, setFinal] = useState(0);
  const timers = useRef<number[]>([]);
  const tarjetaDiag = useRef<HTMLDivElement>(null);

  const limpiar = useCallback(() => {
    timers.current.forEach((t) => window.clearTimeout(t));
    timers.current = [];
    setCorriendo(false);
    setIdx(-1);
    setPaso(-1);
    setDiagnostico(false);
    setAcciones(0);
    setMensaje(false);
    setFinal(0);
    setNarracion("Presione ▶ para ver cómo la IA cuida un hogar antes de que el cliente llame.");
  }, []);
  useEffect(() => limpiar, [limpiar]);
  useEffect(() => limpiar(), [caso, limpiar]);

  // ?final abre directo el resultado (respaldo del presentador y revisión visual)
  useEffect(() => {
    if (!esc || !quiereFinal) return;
    setIdx(esc.sin.length - 1);
    setPaso(5);
    setDiagnostico(true);
    setAcciones(esc.acciones.length);
    setMensaje(true);
    setFinal(2);
    setNarracion(esc.frase_final);
  }, [esc, quiereFinal]);

  const iniciar = () => {
    if (!esc) return;
    limpiar();
    setCorriendo(true);
    const ev = esc.eventos;
    const nombre = esc.hogar.nombre.split(" ")[0];
    const hitos: Hito[] = [];
    let t = 0;
    const decir = (p: number, texto: string) => () => {
      setPaso(p);
      setNarracion(texto);
    };
    hitos.push({ t, fn: decir(0, `${esc.sin[0].fecha}: el internet de ${nombre} (${esc.hogar.tecnologia}, ${esc.ciudad}) funciona normal. El módem reporta su telemetría cada día.`) });
    esc.sin.forEach((dia, i) => {
      t += i === 0 ? 1 : SEG_POR_DIA;
      hitos.push({ t, fn: () => setIdx(i) });
      if (dia.dia === ev.inicio)
        hitos.push({ t: t + 0.1, fn: decir(0, esc.caso === "remoto"
          ? "Algo empieza a cambiar: el WiFi se satura y el módem se cuelga de vez en cuando. El cliente todavía no nota nada."
          : "Algo empieza a cambiar: la señal de la fibra baja un poco cada día. El cliente todavía no nota nada.") });
      if (dia.dia === ev.ia) {
        hitos.push({ t: t + 0.1, fn: () => {
          setDiagnostico(true);
          decir(1, `🧠 La IA lo marca: ${pct(esc.riesgo_al_marcar)} de riesgo de llamada o visita en 7 días. Entra al ${pct(esc.presupuesto)} de hogares con más riesgo de la ciudad. La regla de umbrales todavía no ve nada.`)();
        } });
        t += 5;
        hitos.push({ t, fn: decir(2, `Diagnóstico: ${esc.diagnostico}`) });
        t += 4;
      }
      if (dia.dia === ev.correccion) {
        esc.acciones.forEach((_, k) => hitos.push({ t: t + 0.6 + k * 1.3, fn: () => setAcciones(k + 1) }));
        hitos.push({ t: t + 0.2, fn: decir(3, esc.caso === "remoto"
          ? "🔧 Se corrige a distancia: firmware y canal WiFi. Al cliente le llega un WhatsApp."
          : "📲 WhatsApp para agendar la visita: el técnico llega una sola vez, con el diagnóstico y el repuesto.") });
        hitos.push({ t: t + 2.2, fn: () => setMensaje(true) });
        t += esc.acciones.length * 1.3 + 2;
        hitos.push({ t, fn: decir(4, "Desde aquí, dos mundos: en rojo, sin Tigo Predice; en verde, con Tigo Predice.") });
      }
      // Cada evento clave deja unos segundos para leer la narración antes de seguir con los días
      if (dia.dia === ev.llamada) {
        hitos.push({ t: t + 0.1, fn: decir(4, `📞 Sin Tigo Predice, hoy ${nombre} habría tenido que llamar al call center (${ev.dias_antes_llamada} días después de que la IA lo marcó).`) });
        t += 3;
      }
      if (dia.dia === ev.regla) {
        hitos.push({ t: t + 0.1, fn: decir(4, `⏰ Recién hoy la regla de umbrales habría encendido una alarma: ${ev.dias_antes_regla} días después que la IA.`) });
        t += 3;
      }
      if (dia.dia === ev.visita && esc.caso === "remoto") {
        hitos.push({ t: t + 0.1, fn: decir(4, "🚚 …y se habría enviado un técnico para algo que se arreglaba a distancia.") });
        t += 3;
      }
    });
    t += 1.5;
    hitos.push({ t, fn: () => { setFinal(1); decir(5, `Resultado: visita ${esc.kpis.visita.charAt(0).toLowerCase()}${esc.kpis.visita.slice(1)} · ${esc.kpis.llamadas_evitadas} llamadas evitadas · ahorro ${esc.kpis.ahorro}.`)(); } });
    hitos.push({ t: t + 7, fn: () => { setFinal(2); decir(5, esc.frase_final)(); setCorriendo(false); } });
    hitos.forEach((h) => timers.current.push(window.setTimeout(h.fn, (h.t * 1000) / velocidad)));
  };

  // Las acciones nuevas quedan a la vista aunque la tarjeta tenga alto fijo
  useEffect(() => {
    tarjetaDiag.current?.scrollTo({ top: tarjetaDiag.current.scrollHeight, behavior: "smooth" });
  }, [acciones]);

  // En el modo presentación la demo arranca sola, un instante después de cargar
  const iniciarRef = useRef(iniciar);
  useEffect(() => {
    iniciarRef.current = iniciar;
  });
  useEffect(() => {
    if (!auto || !esc) return;
    const id = window.setTimeout(() => iniciarRef.current(), 600);
    return () => {
      window.clearTimeout(id);
      limpiar();
    };
  }, [auto, esc, limpiar]);

  const datos = useMemo(() => {
    if (!esc) return [];
    const remoto = esc.caso === "remoto";
    return esc.sin.slice(0, idx + 1).map((s, i) => {
      const c = esc.con[i];
      const corregido = s.dia >= esc.eventos.correccion;
      return {
        dia: s.dia,
        fecha: s.fecha,
        sin: remoto ? s.retrans : s.senal,
        con: corregido && acciones > 0 ? (remoto ? c.retrans : c.senal) : null,
        riesgo: Math.round((corregido && acciones > 0 ? c.riesgo : s.riesgo) * 1000) / 10,
      };
    });
  }, [esc, idx, acciones]);

  const conv = useMemo<Conversacion | null>(() => {
    if (!esc || !mensaje) return null;
    return {
      cliente_id: esc.hogar.hogar_id, nombre: esc.hogar.nombre, telefono: esc.hogar.telefono, segmento: "hogar", ciudad: esc.ciudad,
      accion: esc.caso === "remoto" ? "hogar_remoto" : "hogar_visita", accion_nombre: "Atención proactiva", estado: "abierta",
      resultado: final >= 1 ? (esc.caso === "remoto" ? "visita_evitada" : "visita_agendada") : null,
      fuente: esc.mensaje.fuente as "claude" | "plantilla", guardrails: esc.mensaje.guardrails,
      mensajes: [{ de: "tigo", texto: esc.mensaje.texto, hora: "8:05 a. m." }],
    };
  }, [esc, mensaje, final]);

  if (error) return <ErrorCaja error={error} />;
  if (!esc) return <Cargando texto="Preparando el hogar…" />;
  const remoto = esc.caso === "remoto";
  const ev = esc.eventos;
  const actual = idx >= 0 ? esc.sin[idx] : null;
  const corregidoYa = actual && actual.dia >= ev.correccion && acciones > 0;
  const riesgoHoy = actual ? (corregidoYa ? esc.con[idx].riesgo : actual.riesgo) : 0;
  const marcado = actual && ev.ia !== null && actual.dia >= ev.ia;
  const reglaHoy = actual ? (corregidoYa ? esc.con[idx].regla : actual.regla) : false;
  const visible = (d: number | null) => d !== null && actual !== null && actual.dia >= d;
  const fechaDe = (d: number | null) => (d === null ? "—" : esc.sin.find((x) => x.dia === d)?.fecha ?? "—");
  const senales = esc.sin.map((x) => x.senal).concat(esc.hogar.senal_umbral);
  const rangoSenal = [Math.floor(Math.min(...senales)) - 1, Math.ceil(Math.max(...senales)) + 1];
  // En el modo presentación todo cabe en una pantalla de 1366×768, teléfono incluido
  const altoDiag = presentando ? "lg:h-[26vh]" : "lg:h-[410px]";

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-3 rounded-2xl bg-gradient-to-r from-tigo-900 via-tigo to-tigo-700 p-4 text-white shadow-lg lg:flex-row lg:items-center">
        <div className="min-w-0 flex-1">
          <div className="mb-1.5 flex flex-wrap gap-1.5">
            {PASOS.map((t, i) => (
              <span key={t} className={clsx("rounded-full px-2.5 py-0.5 text-xs font-semibold",
                i < paso ? "bg-celeste/30 text-white" : i === paso ? "bg-celeste text-tigo-900" : "bg-white/10 text-white/75")}>
                {i + 1}. {t}
              </span>
            ))}
          </div>
          <div key={narracion} className="aparecer min-h-[2lh] text-base font-semibold leading-snug sm:text-lg xl:text-xl">
            {presentando && paso < 0 && !corriendo ? `Así ve el sistema el hogar de ${esc.hogar.nombre}: ${esc.hogar.tecnologia}, ${esc.ciudad}.` : narracion}
          </div>
        </div>
        {!presentando && <div className="flex shrink-0 flex-wrap items-center gap-2">
          <div className="flex rounded-xl bg-white/10 p-1" role="group" aria-label="Caso">
            {(["remoto", "tecnico"] as const).map((c) => (
              <button key={c} disabled={corriendo} onClick={() => setCaso(c)}
                className={clsx("rounded-lg px-3 py-1.5 text-sm font-semibold", caso === c ? "bg-white text-tigo" : "text-white/80 hover:text-white")}>
                {c === "remoto" ? "A distancia" : "Con técnico"}
              </button>
            ))}
          </div>
          <select value={velocidad} disabled={corriendo} onChange={(e) => setVelocidad(Number(e.target.value))}
            className="rounded-lg bg-white/15 px-2 py-2 text-sm text-white" aria-label="Velocidad">
            <option value={1} className="text-slate-900">1× (~80 s)</option>
            <option value={2} className="text-slate-900">2×</option>
            <option value={4} className="text-slate-900">4×</option>
          </select>
          <button onClick={iniciar} disabled={corriendo} className="flex w-40 items-center justify-center gap-2 rounded-xl bg-celeste px-5 py-3 font-bold text-tigo-900 shadow disabled:opacity-60">
            <Play size={20} /> {corriendo ? "En curso…" : "Iniciar"}
          </button>
          <button onClick={limpiar} className="rounded-xl bg-white/15 p-3 hover:bg-white/25" aria-label="Reiniciar" title="Reiniciar">
            <RotateCcw size={20} />
          </button>
        </div>}
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-3">
          <Tarjeta className="relative p-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <div className="font-semibold text-tigo">
                {esc.hogar.nombre} · {esc.hogar.tecnologia} · {esc.hogar.modem}
              </div>
              <div className="text-xs text-slate-500">{esc.hogar.plan} · nodo {esc.hogar.nodo_id}</div>
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2 md:grid-cols-4">
              <Indicador t="Día" v={actual ? actual.fecha : "—"} />
              <Indicador t="Riesgo de la IA (7 días)" v={actual ? pctRiesgo(riesgoHoy) : "—"}
                color={marcado && !corregidoYa ? SERIES[0] : undefined} s={`marca desde ${pct(esc.umbral_riesgo, 1)} (top ${pct(esc.presupuesto)})`} />
              <Indicador t="Regla de umbrales" v={actual ? (reglaHoy ? "ALARMA" : "sin alarma") : "—"} color={reglaHoy ? ROJO : undefined} s="lo que alarma hoy un ACS" />
              <Indicador t={remoto ? "Retransmisiones WiFi" : esc.hogar.senal_unidad}
                v={actual ? (remoto ? `${(corregidoYa ? esc.con[idx].retrans : actual.retrans).toFixed(0)} %` : `${(corregidoYa ? esc.con[idx].senal : actual.senal).toFixed(1)}`) : "—"} />
            </div>
            <div className="mt-2 h-[clamp(220px,38vh,500px)]">
              <ResponsiveContainer>
                <ComposedChart data={datos} margin={{ top: 18, right: 8, left: 0, bottom: 0 }}>
                  <CartesianGrid stroke={GRILLA} vertical={false} />
                  <XAxis dataKey="dia" type="number" domain={[esc.sin[0].dia, esc.sin[esc.sin.length - 1].dia]} ticks={esc.sin.filter((_, i) => i % 4 === 0).map((d) => d.dia)}
                    tickFormatter={(d: number) => fechaDe(d)} {...EJES} />
                  <YAxis yAxisId="s" {...EJES} width={44} domain={remoto ? [0, 40] : rangoSenal}
                    tickFormatter={(v: number) => (remoto ? `${v} %` : `${v}`)} />
                  <YAxis yAxisId="r" orientation="right" {...EJES} width={44} domain={[0, 100]} tickFormatter={(v: number) => `${v} %`} />
                  <TT labelFormatter={(d) => fechaDe(Number(d))}
                    formatter={(v, n) => [n === "Riesgo de la IA" ? `${Number(v).toFixed(1)} %` : Number(v).toFixed(1), n]} />
                  <Legend />
                  <ReferenceLine yAxisId="s" y={remoto ? 25 : esc.hogar.senal_umbral} stroke="#94a3b8" strokeDasharray="4 4"
                    label={{ value: "umbral de la regla", position: "insideTopLeft", fontSize: 11, fill: "#64748b" }} />
                  {visible(ev.ia) && <ReferenceLine yAxisId="s" x={ev.ia!} stroke={SERIES[0]} strokeWidth={2} label={{ value: "IA lo marca", position: "top", fontSize: 11, fill: SERIES[0] }} />}
                  {visible(ev.llamada) && <ReferenceLine yAxisId="s" x={ev.llamada} stroke={ROJO} strokeDasharray="3 3" label={{ value: "llamaría", position: "top", fontSize: 11, fill: ROJO }} />}
                  {visible(ev.regla) && <ReferenceLine yAxisId="s" x={ev.regla!} stroke="#64748b" strokeDasharray="3 3" label={{ value: "regla", position: "insideTopRight", fontSize: 11, fill: "#64748b" }} />}
                  <Line yAxisId="s" isAnimationActive={false} dataKey="sin" name={remoto ? "Sin Tigo Predice: WiFi (%)" : "Sin Tigo Predice: señal (dBm)"} stroke={ROJO} strokeWidth={2.5} dot={false} />
                  <Line yAxisId="s" isAnimationActive={false} dataKey="con" name="Con Tigo Predice" stroke={VERDE} strokeWidth={2.5} dot={false} connectNulls={false} />
                  <Line yAxisId="r" isAnimationActive={false} dataKey="riesgo" name="Riesgo de la IA" stroke={SERIES[0]} strokeWidth={2} strokeDasharray="5 3" dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
            {final >= 1 && (
              <div className="aparecer mt-3 rounded-xl bg-slate-50 p-4 ring-1 ring-slate-200">
                <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Este hogar · {esc.titulo}</div>
                <div className="mt-1 grid grid-cols-2 gap-3 md:grid-cols-4">
                  <Final t="La IA lo detectó" v={`${ev.dias_antes_llamada} días antes de la llamada`} acento />
                  <Final t="Visita técnica" v={esc.kpis.visita} />
                  <Final t="Ahorro (supuestos)" v={esc.kpis.ahorro} />
                  <Final t="Costo de la acción" v={esc.kpis.costo_accion} />
                </div>
                <div className="mt-1 text-[11px] text-slate-500">{esc.kpis.detalle} La regla de umbrales habría alarmado {ev.dias_antes_regla} días después que la IA.</div>
                {final >= 2 && <div className="aparecer mt-2 text-lg font-bold text-tigo">{esc.frase_final}</div>}
              </div>
            )}
          </Tarjeta>
        </div>

        <div className="min-w-0 space-y-3">
          {/* Alto fijo: las acciones que van apareciendo no empujan el teléfono */}
          {diagnostico ? (
            <div ref={tarjetaDiag} className={clsx("tarjeta aparecer p-4 lg:overflow-y-auto", altoDiag)}>
              <div className="flex items-center gap-2 text-sm font-bold text-tigo"><BrainCircuit size={18} /> Por qué la IA lo marcó ({fechaDe(ev.ia)})</div>
              <ul className="mt-2 space-y-1.5 text-sm">
                {esc.explicacion.map((m) => (
                  <li key={m.variable} className="flex items-start justify-between gap-2">
                    <span className="text-slate-700">{m.texto}</span>
                    <b className="whitespace-nowrap text-slate-900">{m.valor}</b>
                  </li>
                ))}
              </ul>
              <div className="mt-2 rounded-lg bg-celeste-50 px-3 py-2 text-sm font-semibold text-tigo-900">{esc.diagnostico}</div>
              {acciones > 0 && (
                <ul className="mt-3 space-y-1.5 border-t border-slate-100 pt-2 text-sm">
                  {esc.acciones.slice(0, acciones).map((a) => (
                    <li key={a} className="aparecer flex items-start gap-2">
                      {remoto ? <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-exito" /> : <Wrench size={16} className="mt-0.5 shrink-0 text-tigo" />}
                      <span className="text-slate-700">{a}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ) : (
            <Tarjeta className={clsx("p-4 text-sm text-slate-500", altoDiag)}>
              La IA califica cada semana a todos los hogares con la telemetría del módem y marca al {pct(esc.presupuesto)} con más
              riesgo. Aquí aparecerá su diagnóstico.
            </Tarjeta>
          )}
          <Telefono conv={conv} alto={presentando ? "clamp(260px, 38vh, 520px)" : "clamp(300px, 44vh, 520px)"} />
        </div>
      </div>
      {!presentando && <ListaHoy />}
      <div className="text-xs text-slate-400">{esc.aviso}</div>
    </div>
  );
}

function ListaHoy() {
  const { datos: l } = useDatos(api.hogarHoy);
  if (!l) return null;
  return (
    <Tarjeta className="p-4" desplazable="Lista de trabajo de hoy">
      <Titulo extra={<span className="text-xs text-slate-500">datos simulados al {l.fecha}</span>}>
        Lista de trabajo de hoy · soporte nivel 2 · {l.ciudad}
      </Titulo>
      <p className="mb-2 text-sm text-slate-600">
        La IA marcó <b>{entero(l.marcados)}</b> de {entero(l.hogares_ciudad)} hogares simulados. <b>{entero(l.marcados - l.con_alarma_regla)}</b> de
        ellos ({pct((l.marcados - l.con_alarma_regla) / Math.max(l.marcados, 1))}) todavía no tienen ninguna alarma de umbral: solo la IA los ve.
      </p>
      <table className="w-full min-w-[760px] text-sm">
        <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-500"><th className="pb-1 pr-3">Hogar</th><th className="pr-3">Riesgo</th><th className="pr-3">Regla</th><th className="pr-3">Por qué</th><th className="pr-3">Acción sugerida</th><th>Contacto</th></tr></thead>
        <tbody>
          {l.hogares.map((h) => (
            <tr key={h.hogar_id} className="border-t border-slate-100 align-top">
              <td className="py-1.5 pr-2"><div className="font-medium text-slate-800">{h.nombre}</div><div className="text-xs text-slate-400">{h.hogar_id} · {h.tecnologia} · {h.nodo_id}</div></td>
              <td className="whitespace-nowrap py-1.5 pr-3 font-semibold tabular-nums">{pctRiesgo(h.riesgo)}</td>
              <td className="py-1.5 pr-3">{h.alarma_regla ? <span className="text-xs font-semibold text-alerta">alarma</span> : <span className="text-xs text-slate-400">sin alarma</span>}</td>
              <td className="py-1.5 pr-3 text-xs text-slate-600">{h.motivos.map((m) => `${m.texto} (${m.valor})`).join(" · ")}</td>
              <td className="py-1.5 pr-3 text-xs font-semibold text-tigo">{h.accion}</td>
              <td className="py-1.5 text-xs text-slate-500">{h.contacto}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Tarjeta>
  );
}

function Indicador({ t, v, s, color }: { t: string; v: string; s?: string; color?: string }) {
  return (
    <div className="rounded-lg border border-slate-200 px-3 py-1.5">
      <div className="text-[11px] font-medium text-slate-500">{t}</div>
      <div className="text-lg font-extrabold tabular-nums" style={{ color: color ?? "#0f172a" }}>{v}</div>
      {s && <div className="text-[10px] text-slate-400">{s}</div>}
    </div>
  );
}

function Final({ t, v, acento }: { t: string; v: string; acento?: boolean }) {
  return (
    <div>
      <div className="text-xs text-slate-500">{t}</div>
      <div className={clsx("text-base font-extrabold leading-tight", acento ? "text-exito" : "text-slate-900")}>{v}</div>
    </div>
  );
}

