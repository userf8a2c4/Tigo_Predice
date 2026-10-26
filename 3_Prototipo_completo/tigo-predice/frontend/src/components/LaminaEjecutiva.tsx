import clsx from "clsx";
import { BrainCircuit, MessageCircle, Wrench } from "lucide-react";
import type { ReactNode } from "react";
import { api, type Config, type EscenarioFalla, type EscenarioHogar, type Inicio, type Produccion } from "../api";
import type { Escena } from "../escenas";
import { enteroSig, pct } from "../formato";
import { useDatos } from "../hooks";

// Capturas reales del sistema (docs/entregables/gen_capturas.mjs), incrustadas en el código: funcionan sin servidor
const ARCHIVOS = import.meta.glob("../assets/capturas/*.webp", { query: "?inline", import: "default", eager: true }) as Record<string, string>;
export const CAPTURAS: Record<string, string> = Object.fromEntries(
  Object.entries(ARCHIVOS).map(([ruta, url]) => [ruta.split("/").pop()!.replace(".webp", ""), url]),
);

const DESCRIPCION: Record<string, string> = {
  inicio: "Pantalla de inicio de Tigo Predice",
  "hogar-casa": "Hogar en vivo: la señal del módem de Karla, sin y con Tigo Predice",
  "hogar-diagnostico": "Por qué la IA marcó el hogar y qué se corrigió a distancia",
  "hogar-telefono": "WhatsApp que recibe la clienta",
  "modelo-captura": "Visitas evitables que anticipa la IA frente a las alarmas de hoy",
  "falla-resultado": "Resultado de una falla masiva con aviso por WhatsApp",
  "negocio-escenarios": "Caso de negocio por escenario: conservador, base y optimista",
  "produccion-seguridad": "Controles de seguridad y privacidad, del prototipo a producción",
  "piloto-decision": "Decisión GO / NO-GO del piloto con sus criterios",
};

interface Datos {
  inicio: Inicio;
  config: Config;
  hogar: EscenarioHogar;
  falla: EscenarioFalla;
  produccion: Produccion;
}

interface Kpi {
  v: string;
  t: string;
  fuente: string;
}

interface Contenido {
  kicker: string;
  titular: string;
  bajada?: string;
  kpis?: Kpi[];
  pasos?: [typeof BrainCircuit, string, string][];
  visual?: ReactNode;
  nota?: string;
}

/** Modo resumen de la presentación: cada escena como una lámina para directivos, con datos del sistema y su captura. */
export default function LaminaEjecutiva({ escena }: { escena: Escena }) {
  const inicio = useDatos(api.inicio);
  const config = useDatos(api.config);
  const hogar = useDatos(() => api.hogar("remoto"));
  const falla = useDatos(api.falla);
  const produccion = useDatos(api.produccion);
  if (!inicio.datos || !config.datos || !hogar.datos || !falla.datos || !produccion.datos)
    return <div className="flex h-full items-center justify-center text-slate-500">Preparando…</div>;
  const d: Datos = { inicio: inicio.datos, config: config.datos, hogar: hogar.datos, falla: falla.datos, produccion: produccion.datos };

  if (escena.id === "portada" || escena.id === "cierre") return <Portada d={d} cierre={escena.id === "cierre"} />;
  const c = contenido(escena, d);
  return (
    <section key={escena.id} aria-label={c.titular}
      className="aparecer mx-auto grid min-h-[calc(100vh-10rem)] max-w-[1600px] grid-cols-1 items-center gap-8 lg:grid-cols-[minmax(0,0.42fr)_minmax(0,0.58fr)]">
      <div>
        <div className="text-sm font-bold uppercase tracking-wider text-tigo-700">{c.kicker}</div>
        <h2 className="mt-2 text-3xl font-extrabold leading-tight text-slate-900 xl:text-4xl">{c.titular}</h2>
        {c.bajada && <p className="mt-3 text-lg text-slate-600">{c.bajada}</p>}
        {c.kpis && (
          <div className="mt-6 grid grid-cols-3 gap-3">
            {c.kpis.map((k) => (
              <div key={k.t} className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
                <div className="whitespace-nowrap text-2xl font-extrabold leading-tight tabular-nums text-tigo 2xl:text-3xl">{k.v}</div>
                <div className="mt-1 text-sm font-medium leading-snug text-slate-700">{k.t}</div>
                <div className="mt-1 text-[11px] leading-snug text-slate-500">{k.fuente}</div>
              </div>
            ))}
          </div>
        )}
        {c.pasos && (
          <ol className="mt-6 space-y-3">
            {c.pasos.map(([Icono, t, s], k) => (
              <li key={t} className="flex gap-3 rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-celeste-50 text-tigo"><Icono size={20} /></span>
                <div><div className="font-bold text-slate-900">{k + 1}. {t}</div><div className="text-sm text-slate-600">{s}</div></div>
              </li>
            ))}
          </ol>
        )}
        {c.nota && <p className="mt-4 text-sm text-slate-500">{c.nota}</p>}
      </div>
      <div className="min-w-0">
        {c.visual}
        {escena.capturas && <Capturas nombres={escena.capturas} />}
      </div>
    </section>
  );
}

function contenido(escena: Escena, d: Datos): Contenido {
  const c = d.inicio.cifras;
  const sup = d.config.supuestos;
  const k = d.hogar.kpis;
  const nombre = d.hogar.hogar.nombre.split(" ")[0];
  const evitables = sup.pct_visitas_evitables?.base ?? 0.25;
  const visitasMes = Number(c.hogar_visitas_mes.replace(/,/g, ""));
  switch (escena.id) {
    case "karla":
      return {
        kicker: "El problema",
        titular: `Una visita evitable le cuesta a Tigo ${k.ahorro} y la paciencia del cliente`,
        bajada: `${nombre} llamó dos veces y recibió un técnico que no encontró nada roto. La señal del módem avisaba días antes.`,
        kpis: [
          { v: c.costo_por_visita, t: "por visita técnica", fuente: "Costo hondureño estimado" },
          { v: `${Math.round(k.llamadas_evitadas)} × ${c.costo_por_llamada}`, t: "llamadas al call center", fuente: "Costo estimado por llamada" },
          { v: `${d.hogar.eventos.dias_antes_llamada ?? "—"} días`, t: "de aviso que hoy no se aprovecha", fuente: "La IA la marcó antes de que llamara (datos de ejemplo)" },
        ],
      };
    case "escala":
      return {
        kicker: "La escala",
        titular: `Cerca de ${enteroSig(visitasMes * evitables)} visitas al mes se podrían resolver a distancia`,
        bajada: "No es un caso aislado: es parte de la operación de cada mes.",
        kpis: [
          { v: c.hogares_nacional, t: "hogares con internet de Tigo", fuente: "Millicom, Form 20-F 2025" },
          { v: `≈ ${c.hogar_visitas_mes}`, t: "visitas técnicas al mes", fuente: `Estimado: ${pct(sup.tasa_visitas_hogar_mes?.base ?? 0.03)} de los hogares al mes` },
          { v: `1 de ${Math.round(1 / evitables)}`, t: "se podía resolver sin ir", fuente: "Supuesto; la industria reporta 17–20 % sin falla" },
        ],
        visual: <BarraEscala total={visitasMes} evitables={visitasMes * evitables} />,
        nota: "Cálculos a confirmar con los datos de operaciones de campo de Tigo.",
      };
    case "idea":
      return {
        kicker: "La solución",
        titular: "Detecta, resuelve y avisa antes de que el cliente llame",
        pasos: [
          [BrainCircuit, "Detecta", `La IA revisa cada semana las señales del módem y marca al ${pct(Number(d.config.hogar.pct_marcados_semana ?? 0.02))} de hogares con más riesgo, con el porqué.`],
          [Wrench, "Resuelve", "Se corrige a distancia (firmware, canal del WiFi). Si es físico, el técnico va una sola vez."],
          [MessageCircle, "Avisa", "El cliente recibe un WhatsApp con plantilla aprobada: no tiene que llamar."],
        ],
      };
    case "ia":
      return {
        kicker: "Inteligencia artificial",
        titular: "La IA anticipa el doble de visitas evitables que las alarmas de hoy",
        bajada: "Con el mismo número de casas revisadas por semana.",
        kpis: [
          { v: c.hogar_ia_captura, t: "anticipa la IA", fuente: "Datos de ejemplo, validación temporal" },
          { v: c.hogar_regla_captura, t: "anticipan las alarmas de hoy", fuente: "Regla de umbrales" },
          { v: c.hogar_deteccion_temprana, t: "de lo que ve la IA aún no tenía alarma", fuente: "Datos de ejemplo" },
        ],
        nota: `Si con datos reales la IA no supera a las alarmas por ${String(d.config.hogar.go_ia_vs_regla_min ?? 1.3)}×, se usan las alarmas.`,
      };
    case "movil":
      return {
        kicker: "Celulares",
        titular: "Avisar a tiempo baja las llamadas cuando se cae una antena",
        bajada: "El cliente se entera por WhatsApp de la causa y de la hora estimada, antes de llamar.",
        kpis: [
          { v: `−${pct(d.inicio.piloto.reduccion)}`, t: "llamadas en fallas masivas", fuente: "Simulación con grupo de comparación" },
          { v: `${d.falla.por_1000.sin_aviso} → ${d.falla.por_1000.con_aviso}`, t: "llamadas por 1,000 afectados", fuente: "Sin aviso → con aviso (datos de ejemplo)" },
          { v: "NR001/26", t: "CONATEL ya exige avisar de las averías", fuente: "Art. 39, núm. 15 · La Gaceta, 28-feb-2026" },
        ],
      };
    case "negocio":
      return {
        kicker: "Caso de negocio",
        titular: `${c.neto_anio1_base} netos en el año 1, contando solo lo que se puede medir`,
        bajada: `Visitas y llamadas que ya no hacen falta, con costos hondureños. En celulares se paga con ${c.equilibrio_anio1} menos llamadas.`,
        kpis: [
          { v: c.neto_anio1_base, t: "ahorro neto en el año 1", fuente: `Cálculo base · rango ${c.neto_anio1_rango}` },
          { v: c.payback_base, t: "para recuperar la inversión", fuente: "Cálculo base" },
          { v: c.hogar_equilibrio_anio1, t: "menos visitas evitables y en casas ya se paga", fuente: "Punto de equilibrio, año 1" },
        ],
        nota: "La retención de clientes no se suma hasta medirla en el piloto.",
      };
    case "confianza":
      return {
        kicker: "Confianza",
        titular: "Privacidad y medición desde el diseño",
        bajada: "No se lee lo que el cliente hace en internet: solo cómo funciona su módem.",
        kpis: [
          { v: "0", t: "contenido o navegación del cliente que se lee", fuente: "Solo señales del módem: señal, reinicios, WiFi" },
          { v: pct(Number(d.config.piloto.pct_control ?? 0.15)), t: "de clientes en el grupo de comparación", fuente: "Así se mide el efecto real" },
          { v: "3", t: "marcos de referencia: GDPR, ISO 27001 y OWASP", fuente: "Revisión con Seguridad, Privacidad y Legal de Tigo" },
        ],
      };
    case "pedido":
      return {
        kicker: "Lo que pedimos",
        titular: "Un piloto de 12 semanas para decidir con datos reales",
        kpis: [
          { v: c.piloto_costo_base, t: `≈ ${c.piloto_costo_usd}`, fuente: `Rango ${c.piloto_costo_rango}` },
          { v: "12", t: `semanas en ${d.hogar.ciudad}, casas y celulares`, fuente: "Con grupo de comparación" },
          { v: `≥ ${pct(Number(d.config.hogar.go_reduccion_visitas_min ?? 0.15))}`, t: "menos visitas para seguir (GO)", fuente: `Y la IA ≥ ${String(d.config.hogar.go_ia_vs_regla_min ?? 1.3)}× las alarmas` },
        ],
        visual: <Fases plan={d.produccion.plan} />,
      };
    default:
      return { kicker: "", titular: "" };
  }
}

function Capturas({ nombres }: { nombres: string[] }) {
  return (
    <figure className="m-0">
      <div className={clsx("grid gap-4", nombres.length > 1 && "grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)] items-start")}>
        {nombres.map((n) => (
          <img key={n} src={CAPTURAS[n]} alt={DESCRIPCION[n] ?? n}
            className="mx-auto h-auto max-h-[calc(100vh-15rem)] w-auto max-w-full rounded-2xl shadow-xl ring-1 ring-slate-200" />
        ))}
      </div>
      <figcaption className="mt-2 text-center text-xs text-slate-500">Captura del sistema · datos simulados</figcaption>
    </figure>
  );
}

function BarraEscala({ total, evitables }: { total: number; evitables: number }) {
  const parte = evitables / total;
  return (
    <div className="rounded-2xl bg-white p-6 shadow-xl ring-1 ring-slate-200">
      <div className="text-sm font-semibold text-slate-600">Visitas técnicas a hogares, cada mes</div>
      <div className="mt-4 flex h-16 overflow-hidden rounded-xl">
        <div className="flex items-center justify-center bg-celeste text-sm font-bold text-tigo-900" style={{ width: `${parte * 100}%` }}>
          ≈ {enteroSig(evitables)}
        </div>
        <div className="flex flex-1 items-center justify-center bg-slate-200 text-sm font-semibold text-slate-700">≈ {enteroSig(total - evitables)}</div>
      </div>
      <div className="mt-3 flex justify-between gap-4 text-sm">
        <span className="font-semibold text-tigo">Se podían resolver a distancia ({pct(parte)})</span>
        <span className="text-slate-600">Necesitan técnico</span>
      </div>
      <div className="mt-1 text-xs text-slate-500">Estimado sobre ≈ {enteroSig(total)} visitas al mes</div>
    </div>
  );
}

function Fases({ plan }: { plan: Produccion["plan"] }) {
  return (
    <ol className="mb-4 grid grid-cols-3 gap-3">
      {plan.map((f) => (
        <li key={f.semanas} className="rounded-2xl bg-tigo p-4 text-white shadow-sm">
          <div className="text-xs font-semibold text-celeste">Semanas {f.semanas}</div>
          <div className="text-lg font-bold">{f.fase}</div>
        </li>
      ))}
    </ol>
  );
}

function Portada({ d, cierre }: { d: Datos; cierre: boolean }) {
  const c = d.inicio.cifras;
  const kpis: Kpi[] = [
    { v: c.neto_anio1_base, t: "ahorro neto en el año 1", fuente: `Cálculo base · rango ${c.neto_anio1_rango}` },
    { v: c.hogar_ia_vs_regla, t: "la IA frente a las alarmas de hoy", fuente: "Datos de ejemplo" },
    { v: c.piloto_costo_base, t: "piloto de 12 semanas", fuente: `≈ ${c.piloto_costo_usd}` },
  ];
  return (
    <section aria-label={cierre ? "Cierre" : "Portada"}
      className="aparecer mx-auto grid min-h-[calc(100vh-10rem)] max-w-[1600px] grid-cols-1 items-center gap-8 lg:grid-cols-[minmax(0,0.48fr)_minmax(0,0.52fr)]">
      <div>
        <div className="text-sm font-bold uppercase tracking-wider text-tigo-700">AI Shark Tank · Tigo CX Month 2026</div>
        <h2 className="mt-2 text-3xl font-extrabold leading-tight text-slate-900 xl:text-5xl">{d.inicio.posicionamiento}</h2>
        {cierre ? (
          <>
            <div className="mt-6 text-4xl font-extrabold text-tigo">Gracias</div>
            <p className="mt-3 text-lg text-slate-700">Sandra Michel Jimenez Zelaya · Asistente de Experiencia B2B</p>
            <p className="text-slate-500">sandra.jimenez@tigo.com.hn</p>
          </>
        ) : (
          <p className="mt-4 text-xl text-slate-600">{d.inicio.lema}</p>
        )}
        <div className="mt-6 grid grid-cols-3 gap-3">
          {kpis.map((k) => (
            <div key={k.t} className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
              <div className="whitespace-nowrap text-2xl font-extrabold tabular-nums text-tigo 2xl:text-3xl">{k.v}</div>
              <div className="mt-1 text-sm font-medium text-slate-700">{k.t}</div>
              <div className="mt-1 text-[11px] text-slate-500">{k.fuente}</div>
            </div>
          ))}
        </div>
      </div>
      <Capturas nombres={["hogar-casa"]} />
    </section>
  );
}
