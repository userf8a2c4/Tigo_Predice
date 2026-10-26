import { BrainCircuit, FlaskConical, MonitorPlay, PlayCircle, Radio, Router, Scale, Wallet } from "lucide-react";
import { DURACION_TOTAL, reloj } from "../escenas";
import { Link } from "react-router-dom";
import { api } from "../api";
import MapaHonduras from "../components/MapaHonduras";
import { Cargando, ErrorCaja, Tarjeta, Titulo } from "../components/ui";
import { pct } from "../formato";
import { useConfig, useDatos, usePresentacion } from "../hooks";

export default function Inicio() {
  const { datos: d, error } = useDatos(api.inicio);
  const mapa = useDatos(api.mapa);
  const config = useConfig();
  const { abrir } = usePresentacion();
  const pctMarcados = Number(config?.hogar?.pct_marcados_semana ?? 0.02);
  const pctControl = Number(config?.piloto?.pct_control ?? 0.15);
  if (error) return <ErrorCaja error={error} />;
  if (!d) return <Cargando />;
  const c = d.cifras;
  const h = d.hogar;

  return (
    <div className="space-y-5">
      <Tarjeta foco="inicio" className="bg-gradient-to-br from-tigo-900 via-tigo to-tigo-700 p-6 text-white lg:p-8">
        <div className="text-sm font-semibold tracking-wide text-celeste">ATENCIÓN PROACTIVA CON IA · PILOTO HOGAR + MÓVIL · 60 DÍAS · SAN PEDRO SULA</div>
        <h1 className="mt-2 max-w-4xl text-2xl font-extrabold leading-tight sm:text-3xl lg:text-4xl">{d.posicionamiento}</h1>
        <p className="mt-3 max-w-3xl text-lg text-white/90">{d.lema}</p>
        <p className="mt-2 max-w-3xl text-white/75">
          <b>Hogar:</b> la IA lee la telemetría de los módems, marca los hogares que van a fallar y se corrigen a distancia.{" "}
          <b>Móvil:</b> en fallas masivas, aviso por WhatsApp antes de que llamen. En los dos, un grupo control mide el efecto real.
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          <button onClick={abrir} className="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 font-bold text-tigo shadow hover:brightness-95">
            <MonitorPlay size={20} /> Modo presentación ({reloj(DURACION_TOTAL)} min)
          </button>
          <Link to="/hogar" className="inline-flex items-center gap-2 rounded-xl bg-celeste px-5 py-3 font-bold text-tigo-900 shadow hover:brightness-105">
            <PlayCircle size={20} /> Ver Hogar en vivo (80 s)
          </Link>
          <Link to="/falla" className="inline-flex items-center gap-2 rounded-xl bg-white/15 px-5 py-3 font-semibold text-white hover:bg-white/25">
            <Radio size={18} /> Falla masiva en vivo
          </Link>
        </div>
      </Tarjeta>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Cifra icono={Wallet} t="Neto año 1 (Hogar + Móvil, base)" v={c.neto_anio1_base} s={`rango ${c.neto_anio1_rango} · solo beneficio duro`} />
        <Cifra icono={BrainCircuit} t="IA vs. regla de umbrales" v={c.hogar_ia_vs_regla}
          s={`la IA anticipa ${c.hogar_ia_captura} de las visitas evitables; la regla, ${c.hogar_regla_captura} (simulado)`} />
        <Cifra icono={Scale} t="Punto de equilibrio" v={`${c.hogar_equilibrio_anio1} · ${c.equilibrio_anio1}`}
          s="menos visitas evitables (Hogar) · menos llamadas (Móvil): cada frente se paga en el año 1" />
        <Cifra icono={FlaskConical} t="Inversión del piloto" v={c.piloto_costo_base} s={`≈ ${c.piloto_costo_usd} · rango ${c.piloto_costo_rango}`} />
      </div>

      <div id="como-funciona" className="grid scroll-mt-4 grid-cols-1 gap-5 xl:grid-cols-[1fr_1fr]">
        <Tarjeta foco="como-funciona" className="p-5">
          <Titulo extra={<span className="flex items-center gap-1 text-xs font-semibold text-tigo"><Router size={14} /> Frente principal</span>}>
            Hogar: cómo funciona
          </Titulo>
          <ol className="space-y-4">
            {[
              ["1", "Detecta", `Cada semana la IA califica a todos los hogares con la telemetría del módem (señal, errores, reinicios, WiFi) y marca al ${pct(pctMarcados)} con más riesgo de llamar o necesitar visita en 7 días.`],
              ["2", "Resuelve", "Si es WiFi o firmware, se corrige a distancia y el cliente recibe un WhatsApp. Si es físico, se agenda la visita antes del corte y el técnico llega con el diagnóstico."],
              ["3", "Mide", `Un ${pct(pctControl)} de los hogares marcados queda como control. GO solo si las visitas bajan ≥ 15 %, de forma significativa, y la IA le gana a la regla de umbrales.`],
            ].map(([n, t, s]) => (
              <li key={n} className="flex gap-3">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-celeste font-bold text-tigo">{n}</span>
                <div><div className="font-bold text-slate-800">{t}</div><div className="text-sm text-slate-600">{s}</div></div>
              </li>
            ))}
          </ol>
          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Simulado t="Hogar · visitas en hogares marcados" v={`−${pct(h.reduccion_visitas)}`} s={`IC 95 % ${pct(h.ic[0])} a ${pct(h.ic[1])} · llamadas −${pct(h.reduccion_llamadas)} · ${h.decision}`} />
            <Simulado t="Móvil · llamadas en fallas masivas" v={`−${pct(d.piloto.reduccion)}`} s={`IC 95 % ${pct(d.piloto.ic[0])} a ${pct(d.piloto.ic[1])} · ${d.piloto.decision}`} />
          </div>
          <div className="mt-2 text-xs text-slate-500">Resultados simulados con efectos supuestos: muestran cómo se medirá, no son resultados reales.</div>
        </Tarjeta>

        <Tarjeta className="p-4">
          <Titulo extra={<span className="text-xs text-slate-500">Puntos rojos = sitios con falla masiva en 90 días</span>}>Móvil: fallas masivas de red</Titulo>
          {mapa.datos ? <MapaHonduras mapa={mapa.datos} altura="clamp(240px, 36vh, 480px)" /> : <Cargando />}
          <p className="mt-2 text-sm text-slate-600">
            Cuando cae un sitio, los afectados reciben un WhatsApp con la causa en palabras simples y la hora del NOC
            (solo si la tiene). Mismo motor, mismos guardrails, mismo grupo control.
          </p>
        </Tarjeta>
      </div>
      <div className="rounded-xl bg-slate-50 p-3 text-xs text-slate-500">
        Churn, retención y cobros quedan para la <b>Fase 2</b>: no entran al caso de negocio hasta que el piloto mida su efecto.
      </div>
    </div>
  );
}

function Cifra({ icono: Icono, t, v, s }: { icono: typeof Scale; t: string; v: string; s: string }) {
  return (
    <Tarjeta className="p-4">
      <div className="flex items-center gap-2 text-sm font-medium text-slate-500"><Icono size={16} className="text-tigo" /> {t}</div>
      <div className="mt-1 text-2xl font-extrabold tabular-nums text-slate-900 sm:whitespace-nowrap sm:text-3xl">{v}</div>
      <div className="mt-1 text-xs text-slate-500">{s}</div>
    </Tarjeta>
  );
}

function Simulado({ t, v, s }: { t: string; v: string; s: string }) {
  return (
    <div className="rounded-xl border border-slate-200 p-3">
      <div className="text-xs text-slate-500">{t}</div>
      <div className="text-2xl font-extrabold tabular-nums text-exito">{v}</div>
      <div className="text-xs text-slate-500">{s}</div>
    </div>
  );
}
