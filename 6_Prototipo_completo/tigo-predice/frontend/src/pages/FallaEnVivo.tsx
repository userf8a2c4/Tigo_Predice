import clsx from "clsx";
import { Play, RotateCcw } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Circle, CircleMarker, Marker, Tooltip } from "react-leaflet";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip as TT, XAxis, YAxis } from "recharts";
import { api, type Conversacion } from "../api";
import { MapaBase, iconoPulso } from "../components/MapaHonduras";
import Telefono from "../components/Telefono";
import { Cargando, ErrorCaja, Tarjeta } from "../components/ui";
import { EJES, GRILLA, entero, pct } from "../formato";
import { useDatos } from "../hooks";

const ROJO = "#e0303a";
const VERDE = "#16a35a";
const PASOS = ["Falla", "Afectados", "Control", "Aviso", "72 horas", "Resultado"];
const SEG_POR_HORA = 2.2; // cada punto de la línea de tiempo (18 puntos ≈ 40 s)

type Fase = { paso: number; narracion: string };

export default function FallaEnVivo() {
  const { datos: esc, error } = useDatos(api.falla);
  const [fase, setFase] = useState<Fase>({ paso: -1, narracion: "Presione ▶ para simular una falla masiva de red." });
  const [velocidad, setVelocidad] = useState(1);
  const [corriendo, setCorriendo] = useState(false);
  const [vuelo, setVuelo] = useState(false);
  const [caido, setCaido] = useState(false);
  const [mostrarGrupos, setMostrarGrupos] = useState(false);
  const [afectadosVisibles, setAfectadosVisibles] = useState(0);
  const [mensajes, setMensajes] = useState(0); // 0..3
  const [restablecido, setRestablecido] = useState(false);
  const [hora, setHora] = useState(-1);
  const [final, setFinal] = useState(0); // 0 nada, 1 KPIs, 2 frase
  const timers = useRef<number[]>([]);
  const restablecidoRef = useRef(false);

  const limpiar = useCallback(() => {
    timers.current.forEach((t) => window.clearTimeout(t));
    timers.current = [];
    setCorriendo(false);
    setVuelo(false);
    setCaido(false);
    setMostrarGrupos(false);
    setAfectadosVisibles(0);
    setMensajes(0);
    setRestablecido(false);
    setHora(-1);
    setFinal(0);
    setFase({ paso: -1, narracion: "Presione ▶ para simular una falla masiva de red." });
  }, []);

  useEffect(() => limpiar, [limpiar]);

  // ?final abre directo el resultado (respaldo del presentador y revisión visual)
  useEffect(() => {
    if (!esc || !new URLSearchParams(window.location.search).has("final")) return;
    setVuelo(true);
    setCaido(true);
    setMostrarGrupos(true);
    setAfectadosVisibles(esc.muestra.afectados);
    setMensajes(3);
    setRestablecido(true);
    setHora(esc.linea_tiempo.length - 1);
    setFinal(2);
    setFase({ paso: 5, narracion: esc.frase_final });
  }, [esc]);

  const iniciar = () => {
    if (!esc) return;
    limpiar();
    restablecidoRef.current = false;
    setCorriendo(true);
    const v = velocidad;
    const en = (seg: number, fn: () => void) => timers.current.push(window.setTimeout(fn, (seg * 1000) / v));
    const k = esc.kpis;
    en(0, () => setFase({ paso: 0, narracion: `${esc.sitio.hora_inicio - 12}:00 p. m. Un día normal en ${esc.ciudad}. El NOC monitorea los sitios de la red.` }));
    en(2.5, () => setVuelo(true));
    en(6.5, () => {
      setCaido(true);
      setFase({ paso: 0, narracion: `⚡ ${esc.sitio.causa}. Los clientes se quedan sin servicio… y todavía no saben por qué.` });
    });
    for (let i = 1; i <= 10; i++) en(7 + i * 0.25, () => setAfectadosVisibles(Math.round((esc.muestra.afectados * i) / 10)));
    en(10, () => setFase({ paso: 1, narracion: `${esc.muestra.afectados} clientes de la muestra afectados (≈ ${entero(k.afectados_reales)} en una falla típica real).` }));
    en(14, () => {
      setMostrarGrupos(true);
      setFase({ paso: 2, narracion: `El sistema separa al azar un ${pct(esc.muestra.pct_control)} de control que NO recibe aviso: así medimos el efecto real, no lo suponemos.` });
    });
    en(19, () => {
      setMensajes(1);
      setFase({ paso: 3, narracion: "📲 En minutos, los afectados reciben un WhatsApp con la causa en palabras simples y la hora estimada del NOC. No necesitan llamar." });
    });
    en(24, () => {
      setMensajes(2);
      setFase({ paso: 3, narracion: "Si el NOC aún no tiene hora, el mensaje no la inventa: «le avisaremos al restablecer». Guardrails automáticos." });
    });
    const t0 = 29;
    en(t0, () => setFase({ paso: 4, narracion: "📞 Las siguientes 72 horas: en el grupo control entran llamadas (rojo); en los avisados, muchas menos (verde)." }));
    esc.linea_tiempo.forEach((p, i) => {
      en(t0 + i * SEG_POR_HORA, () => {
        setHora(i);
        if (p.hora >= esc.sitio.eta_horas && !restablecidoRef.current) {
          restablecidoRef.current = true;
          setRestablecido(true);
          setMensajes(3);
          setFase({ paso: 4, narracion: `✅ Hora ${esc.sitio.eta_horas}: el servicio se restablece y llega el mensaje de cierre. Las llamadas del control siguen entrando.` });
        }
      });
    });
    const tFin = t0 + esc.linea_tiempo.length * SEG_POR_HORA + 1;
    en(tFin, () => {
      setFinal(1);
      setFase({ paso: 5, narracion: `Resultado de esta falla a escala real: ${k.llamadas_evitadas_texto} llamadas evitadas, ${k.neto_texto} de ahorro neto.` });
    });
    en(tFin + 8, () => {
      setFinal(2);
      setFase({ paso: 5, narracion: esc.frase_final });
      setCorriendo(false);
    });
  };
  const reiniciar = () => {
    restablecidoRef.current = false;
    limpiar();
  };

  const centroCiudad = useMemo<[number, number] | undefined>(
    () => (esc && vuelo ? [esc.sitio.lat, esc.sitio.lon] : undefined),
    [esc, vuelo],
  );
  const conv = useMemo<Conversacion | null>(() => {
    if (!esc || mensajes === 0) return null;
    const m = esc.mensajes;
    const lista = [{ de: "tigo" as const, texto: m[0].texto, hora: "7:12 p. m." }];
    if (mensajes >= 3) lista.push({ de: "tigo" as const, texto: m[2].texto, hora: "11:05 p. m." });
    return {
      cliente_id: "demo", nombre: m[0].cliente, telefono: m[0].telefono, segmento: "", ciudad: esc.ciudad,
      accion: "aviso_falla", accion_nombre: "Aviso de falla", estado: "abierta", resultado: null,
      fuente: m[0].fuente as "claude" | "plantilla", guardrails: m[0].guardrails, mensajes: lista,
    };
  }, [esc, mensajes]);

  if (error) return <ErrorCaja error={error} />;
  if (!esc) return <Cargando texto="Preparando la falla…" />;
  const p = hora >= 0 ? esc.linea_tiempo[hora] : { hora: 0, control: 0, tratados: 0 };
  const serie = hora >= 0 ? esc.linea_tiempo.slice(0, hora + 1) : [];

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-3 rounded-2xl bg-gradient-to-r from-tigo-900 via-tigo to-tigo-700 p-4 text-white shadow-lg lg:flex-row lg:items-center">
        <div className="min-w-0 flex-1">
          <div className="mb-1.5 flex flex-wrap gap-1.5">
            {PASOS.map((t, i) => (
              <span key={t} className={clsx("rounded-full px-2.5 py-0.5 text-xs font-semibold",
                i < fase.paso ? "bg-celeste/30 text-white" : i === fase.paso ? "bg-celeste text-tigo-900" : "bg-white/10 text-white/50")}>
                {i + 1}. {t}
              </span>
            ))}
          </div>
          <div key={fase.narracion} className="aparecer text-base font-semibold leading-snug sm:text-lg xl:text-xl">{fase.narracion}</div>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <select value={velocidad} disabled={corriendo} onChange={(e) => setVelocidad(Number(e.target.value))}
            className="rounded-lg bg-white/15 px-2 py-2 text-sm text-white" aria-label="Velocidad">
            <option value={1} className="text-slate-900">1× (~90 s)</option>
            <option value={2} className="text-slate-900">2×</option>
            <option value={4} className="text-slate-900">4×</option>
          </select>
          <button onClick={iniciar} disabled={corriendo} className="flex items-center gap-2 rounded-xl bg-celeste px-5 py-3 font-bold text-tigo-900 shadow disabled:opacity-60">
            <Play size={20} /> {corriendo ? "En curso…" : "Iniciar"}
          </button>
          <button onClick={reiniciar} className="rounded-xl bg-white/15 p-3 hover:bg-white/25" aria-label="Reiniciar" title="Reiniciar">
            <RotateCcw size={20} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(290px,360px)]">
        <div className="space-y-3">
          <Tarjeta className="relative p-2">
            <MapaBase altura="clamp(240px, 46vh, 600px)" centro={centroCiudad} zoom={11.75}>
              {caido && (
                <>
                  <Circle center={[esc.sitio.lat, esc.sitio.lon]} radius={esc.sitio.radio_km * 1000}
                    pathOptions={{ color: restablecido ? VERDE : ROJO, weight: 2, dashArray: "6 6", fillOpacity: 0.06 }} />
                  <Marker position={[esc.sitio.lat, esc.sitio.lon]} icon={iconoPulso(restablecido ? "verde" : "rojo")}>
                    <Tooltip>Sitios {esc.sitio.celdas.join(", ")}</Tooltip>
                  </Marker>
                </>
              )}
              {caido &&
                esc.muestra.puntos.slice(0, afectadosVisibles).map((pt, i) => (
                  <CircleMarker key={i} center={[pt.lat, pt.lon]} radius={3.5}
                    pathOptions={{ weight: 0, fillOpacity: 0.85, fillColor: !mostrarGrupos ? ROJO : pt.grupo === "control" ? "#475569" : "#00A3CC" }} />
                ))}
            </MapaBase>
            {caido && (
              <div className="z-[500] mt-2 grid grid-cols-3 gap-2 sm:pointer-events-none sm:absolute sm:right-4 sm:top-4 sm:mt-0">
                <Caja titulo="Afectados (muestra)" valor={entero(afectadosVisibles)} />
                <Caja titulo="Reciben aviso" valor={mostrarGrupos ? entero(esc.muestra.tratamiento) : "—"} color="#00A3CC" />
                <Caja titulo={`Control (${pct(esc.muestra.pct_control)})`} valor={mostrarGrupos ? entero(esc.muestra.control) : "—"} color="#475569" />
              </div>
            )}
            {final >= 1 && (
              <div className="aparecer relative z-[500] mt-2 rounded-xl bg-white/95 p-4 shadow-lg sm:absolute sm:inset-x-4 sm:bottom-4 sm:mt-0">
                <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Esta falla, a escala real (~{entero(esc.kpis.afectados_reales)} afectados)</div>
                <div className="mt-1 grid grid-cols-2 gap-3 md:grid-cols-4">
                  <Final t="Llamadas evitadas" v={esc.kpis.llamadas_evitadas_texto} />
                  <Final t="Ahorro en call center" v={esc.kpis.ahorro_texto} />
                  <Final t="Costo de la acción" v={esc.kpis.costo_accion_texto} />
                  <Final t="Ahorro neto" v={esc.kpis.neto_texto} acento />
                </div>
                <div className="mt-1 text-[11px] text-slate-500">{esc.kpis.supuestos} · {esc.kpis.compensados_por_modelo} compensaciones priorizadas por el modelo.</div>
                {final >= 2 && <div className="aparecer mt-2 text-lg font-bold text-tigo">{esc.frase_final}</div>}
              </div>
            )}
          </Tarjeta>

          <Tarjeta className="p-3">
            <div className="flex flex-wrap items-end gap-6">
              <Contador t="Sin aviso (control)" v={p.control} color={ROJO} />
              <Contador t="Con aviso" v={p.tratados} color={VERDE} />
              <div className="text-sm text-slate-600">
                llamadas por cada 1,000 afectados · hora <b>{p.hora}</b> de 72
                <div className="text-xs text-slate-400">Esperadas según el modelo 72 h y una reducción supuesta del 20 % en avisados</div>
              </div>
            </div>
            <div className="mt-2 h-[clamp(120px,20vh,240px)]">
              <ResponsiveContainer>
                <LineChart data={serie} margin={{ top: 6, right: 16, left: 0, bottom: 0 }}>
                  <CartesianGrid stroke={GRILLA} vertical={false} />
                  <XAxis dataKey="hora" type="number" domain={[0, 72]} ticks={[0, 4, 12, 24, 48, 72]} {...EJES} tickFormatter={(h) => `${h} h`} />
                  <YAxis {...EJES} width={40} domain={[0, Math.ceil(esc.por_1000.sin_aviso / 100) * 100]} />
                  <TT formatter={(v, n) => [entero(Number(v)), n]} labelFormatter={(h) => `Hora ${h}`} />
                  <Legend />
                  <Line isAnimationActive={false} dataKey="control" name="Sin aviso (control)" stroke={ROJO} strokeWidth={2.5} dot={false} />
                  <Line isAnimationActive={false} dataKey="tratados" name="Con aviso" stroke={VERDE} strokeWidth={2.5} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Tarjeta>
        </div>

        <div className="space-y-3">
          <Telefono conv={conv} alto="clamp(380px, 56vh, 640px)" />
          {mensajes >= 2 && (
            <Tarjeta className="aparecer p-3 text-sm">
              <div className="text-xs font-semibold text-slate-500">{esc.mensajes[1].etiqueta}</div>
              <div className="mt-1 text-slate-700">{esc.mensajes[1].texto}</div>
            </Tarjeta>
          )}
        </div>
      </div>
      <div className="text-xs text-slate-400">{esc.aviso} Muestra sintética de {esc.muestra.afectados} clientes; la escala real es un supuesto de configuración.</div>
    </div>
  );
}

function Caja({ titulo, valor, color }: { titulo: string; valor: string; color?: string }) {
  return (
    <div className="rounded-lg bg-white/95 px-3 py-2 shadow">
      <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-500">
        {color && <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: color }} />}
        {titulo}
      </div>
      <div className="text-xl font-extrabold tabular-nums">{valor}</div>
    </div>
  );
}

function Contador({ t, v, color }: { t: string; v: number; color: string }) {
  return (
    <div>
      <div className="text-xs font-semibold" style={{ color }}>{t}</div>
      <div className="text-3xl font-extrabold tabular-nums sm:text-4xl" style={{ color }}>{entero(v)}</div>
    </div>
  );
}

function Final({ t, v, acento }: { t: string; v: string; acento?: boolean }) {
  return (
    <div>
      <div className="text-xs text-slate-500">{t}</div>
      <div className={clsx("text-lg font-extrabold", acento ? "text-exito" : "text-slate-900")}>{v}</div>
    </div>
  );
}
