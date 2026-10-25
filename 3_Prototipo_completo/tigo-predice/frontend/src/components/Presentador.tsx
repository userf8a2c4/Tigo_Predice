import clsx from "clsx";
import {
  BrainCircuit, Captions, CaptionsOff, ChevronLeft, ChevronRight, FlaskConical, Lock, Maximize, MessageCircle, Pause,
  PhoneCall, Play, RotateCcw, ShieldCheck, Truck, Wifi, Wrench, X,
} from "lucide-react";
import { useCallback, useEffect, useState, type ReactNode, type RefObject } from "react";
import { useNavigate } from "react-router-dom";
import { api, type Config, type EscenarioHogar, type Inicio } from "../api";
import { DURACION_TOTAL, ESCENAS, reloj, subtituloEn, type Escena } from "../escenas";
import { pct } from "../formato";
import { useDatos } from "../hooks";

const PASO = 0.25; // segundos por tic del reloj
const ULTIMA = ESCENAS.length - 1;
const CLAVE_SUBTITULOS = "tigo-predice:subtitulos";

// Preferencia de quien presenta en este navegador; si el almacenamiento no está disponible, arrancan apagados
function leerSubtitulos() {
  try {
    return window.localStorage.getItem(CLAVE_SUBTITULOS) === "1";
  } catch {
    return false;
  }
}
function guardarSubtitulos(v: boolean) {
  try {
    window.localStorage.setItem(CLAVE_SUBTITULOS, v ? "1" : "0");
  } catch {
    // sin almacenamiento: la elección dura mientras la página esté abierta
  }
}

export interface Reproductor {
  pos: { i: number; t: number };
  corriendo: boolean;
  iniciado: boolean;
  subtitulos: boolean;
  alternar: () => void;
  alternarSubtitulos: () => void;
  ir: (i: number) => void;
  reiniciar: () => void;
}

/**
 * Reloj del modo presentación: avanza solo de escena en escena, abre la pantalla de cada una y responde al teclado
 * (Espacio pausa; ←/→ o un control remoto con Re Pág/Av Pág cambian de escena; S subtítulos; F pantalla completa;
 * Esc sale).
 */
export function useReproductor(activo: boolean, principal: RefObject<HTMLElement | null>, salir: () => void): Reproductor {
  const navegar = useNavigate();
  const [pos, setPos] = useState({ i: 0, t: 0 });
  const [corriendo, setCorriendo] = useState(false);
  const [iniciado, setIniciado] = useState(false);
  const [subtitulos, setSubtitulos] = useState(leerSubtitulos);

  const alternarSubtitulos = useCallback(() => {
    setSubtitulos((v) => {
      guardarSubtitulos(!v);
      return !v;
    });
  }, []);
  const ir = useCallback((i: number) => setPos({ i: Math.min(Math.max(i, 0), ULTIMA), t: 0 }), []);
  const alternar = useCallback(() => {
    setIniciado(true);
    setCorriendo((c) => !c);
  }, []);
  const reiniciar = useCallback(() => {
    setPos({ i: 0, t: 0 });
    setCorriendo(false);
    setIniciado(false);
  }, []);

  // Al salir, la próxima vez empieza desde la portada y en pausa
  useEffect(() => {
    if (!activo) reiniciar();
  }, [activo, reiniciar]);

  useEffect(() => {
    if (!activo || !corriendo) return;
    const id = window.setInterval(() => {
      setPos((p) => {
        const t = p.t + PASO;
        if (t < ESCENAS[p.i].seg) return { i: p.i, t };
        return p.i < ULTIMA ? { i: p.i + 1, t: 0 } : { i: p.i, t: ESCENAS[p.i].seg };
      });
    }, PASO * 1000);
    return () => window.clearInterval(id);
  }, [activo, corriendo]);

  // Cada escena abre su pantalla del sistema y la muestra desde arriba (o desde su sección)
  useEffect(() => {
    if (!activo) return;
    const escena = ESCENAS[pos.i];
    navegar(escena.ruta, { replace: true });
    const id = window.setTimeout(() => {
      const foco = escena.foco ? document.getElementById(escena.foco) : null;
      if (foco) foco.scrollIntoView({ block: "start", behavior: "smooth" });
      else principal.current?.scrollTo({ top: 0 });
    }, 350);
    return () => window.clearTimeout(id);
  }, [activo, pos.i, navegar, principal]);

  useEffect(() => {
    if (!activo) return;
    const tecla = (e: KeyboardEvent) => {
      if (e.target instanceof Element && e.target.closest("input, select, textarea")) return;
      const k = e.key;
      if (k === " " || k === "k" || k === "K") alternar();
      else if (k === "ArrowRight" || k === "PageDown") { setIniciado(true); setPos((p) => ({ i: Math.min(p.i + 1, ULTIMA), t: 0 })); }
      else if (k === "ArrowLeft" || k === "PageUp") setPos((p) => ({ i: Math.max(p.i - 1, 0), t: 0 }));
      else if (k === "f" || k === "F") pantallaCompleta();
      else if (k === "s" || k === "S") alternarSubtitulos();
      else if (k === "Home") reiniciar();
      else if (k === "Escape" && !document.fullscreenElement) salir();
      else return;
      e.preventDefault();
    };
    window.addEventListener("keydown", tecla);
    return () => window.removeEventListener("keydown", tecla);
  }, [activo, alternar, alternarSubtitulos, reiniciar, salir]);

  const fin = pos.i === ULTIMA && pos.t >= ESCENAS[ULTIMA].seg;
  return { pos, corriendo: corriendo && !fin, iniciado, subtitulos, alternar, alternarSubtitulos, ir, reiniciar };
}

function pantallaCompleta() {
  if (document.fullscreenElement) document.exitFullscreen().catch(() => undefined);
  else document.documentElement.requestFullscreen().catch(() => undefined);
}

// ------------------------------------------------------------------ barra de control

export function BarraPresentacion({ r, salir }: { r: Reproductor; salir: () => void }) {
  const { pos } = r;
  const escena = ESCENAS[pos.i];
  const previo = ESCENAS.slice(0, pos.i).reduce((s, e) => s + e.seg, 0);
  const boton = "rounded-lg p-2 text-white/80 hover:bg-white/10 hover:text-white";
  return (
    <div className="flex items-center gap-3 bg-tigo-900 px-3 py-2 text-sm text-white">
      <button onClick={() => r.ir(pos.i - 1)} className={boton} aria-label="Escena anterior" title="Anterior (←)"><ChevronLeft size={18} /></button>
      <button onClick={r.alternar} className="flex items-center gap-1.5 rounded-lg bg-celeste px-3 py-1.5 font-bold text-tigo-900"
        aria-label={r.corriendo ? "Pausar" : "Reproducir"} title="Reproducir o pausar (Espacio)">
        {r.corriendo ? <Pause size={16} /> : <Play size={16} />} {r.corriendo ? "Pausa" : "Play"}
      </button>
      <button onClick={() => r.ir(pos.i + 1)} className={boton} aria-label="Escena siguiente" title="Siguiente (→)"><ChevronRight size={18} /></button>

      <div className="flex min-w-0 flex-1 gap-0.5" aria-hidden="true">
        {ESCENAS.map((e, k) => (
          <button key={e.id} onClick={() => r.ir(k)} title={e.titulo} tabIndex={-1}
            className="h-2 overflow-hidden rounded-full bg-white/15" style={{ flexGrow: e.seg, flexBasis: 0 }}>
            <div className="h-full bg-celeste" style={{ width: k < pos.i ? "100%" : k > pos.i ? "0%" : `${(pos.t / e.seg) * 100}%` }} />
          </button>
        ))}
      </div>

      <div className="hidden whitespace-nowrap text-white/80 md:block">
        <b className="text-white">{pos.i + 1}/{ESCENAS.length} · {escena.titulo}</b>
        <span className="ml-2 tabular-nums">{reloj(previo + pos.t)} / {reloj(DURACION_TOTAL)}</span>
      </div>
      <button onClick={r.alternarSubtitulos} aria-pressed={r.subtitulos} title="Subtítulos (S)"
        className={clsx("flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 font-semibold", r.subtitulos ? "bg-white text-tigo-900" : "text-white/80 hover:bg-white/10 hover:text-white")}>
        {r.subtitulos ? <Captions size={18} /> : <CaptionsOff size={18} />} <span className="hidden lg:inline">Subtítulos</span>
      </button>
      <button onClick={pantallaCompleta} className={boton} aria-label="Pantalla completa" title="Pantalla completa (F)"><Maximize size={18} /></button>
      <button onClick={r.reiniciar} className={boton} aria-label="Volver a la primera escena" title="Volver al inicio (Inicio)"><RotateCcw size={18} /></button>
      <button onClick={salir} className={boton} aria-label="Salir del modo presentación" title="Salir (Esc)"><X size={18} /></button>
    </div>
  );
}

// ------------------------------------------------------------------ subtítulos

/** Franja de subtítulos sobre la pantalla del sistema (a la derecha de la tarjeta), con el texto del guion. */
export function SubtitulosPresentacion({ r }: { r: Reproductor }) {
  if (!r.subtitulos || !r.iniciado) return null;
  const texto = subtituloEn(ESCENAS[r.pos.i], r.pos.t);
  if (!texto) return null;
  return (
    <div className="pointer-events-none fixed bottom-16 left-[22rem] right-0 z-[1100] flex justify-center px-8">
      <p key={texto}
        className="subtitulo max-w-3xl rounded-2xl border-l-4 border-celeste bg-tigo-900/85 px-6 py-3 text-center text-lg font-medium leading-snug tracking-wide text-white shadow-2xl backdrop-blur-md lg:text-xl">
        {texto}
      </p>
    </div>
  );
}

// ------------------------------------------------------------------ tarjeta de cada escena

/** Columna izquierda durante la presentación: la idea de la escena y sus cifras, junto a la pantalla real. */
export function PanelEscena({ r }: { r: Reproductor }) {
  const inicio = useDatos(api.inicio);
  const config = useDatos(api.config);
  const hogar = useDatos(() => api.hogar("remoto"));
  const escena = ESCENAS[r.pos.i];
  const datos = inicio.datos && config.datos && hogar.datos ? { inicio: inicio.datos, config: config.datos, hogar: hogar.datos } : null;
  return (
    <aside className="flex w-[22rem] shrink-0 flex-col overflow-y-auto bg-gradient-to-b from-tigo-900 via-tigo to-tigo-700 p-5 text-white" aria-live="polite">
      <div className="text-[11px] font-semibold uppercase tracking-wider text-white/70">Tigo Predice · {r.pos.i + 1} de {ESCENAS.length}</div>
      {datos ? (
        <div key={escena.id} className="aparecer mt-4 flex flex-1 flex-col">
          <Tarjeta escena={escena} d={datos} />
          {escena.id === "portada" && !r.iniciado && (
            <div className="mt-6 rounded-xl bg-white/10 px-3 py-2 text-sm text-white/85">
              Presione <b>Espacio</b> o <b>Play</b> para comenzar. <b>S</b>: subtítulos. <b>F</b>: pantalla completa.
              <b> Esc</b>: salir.
            </div>
          )}
        </div>
      ) : (
        <div className="mt-6 text-white/70">Preparando…</div>
      )}
      <div className="mt-4 text-[11px] text-white/60">⚠ Datos simulados · supuestos a validar con Tigo</div>
    </aside>
  );
}

interface Datos {
  inicio: Inicio;
  config: Config;
  hogar: EscenarioHogar;
}

function Tarjeta({ escena, d }: { escena: Escena; d: Datos }) {
  const c = d.inicio.cifras;
  const sup = d.config.supuestos;
  const nombre = d.hogar.hogar.nombre.split(" ")[0];
  switch (escena.id) {
    case "portada":
      return (
        <Bloque kicker="AI Shark Tank · Tigo CX Month 2026" titulo={d.inicio.posicionamiento}>
          <p className="text-lg text-white/85">{d.inicio.lema}</p>
          <p className="mt-6 text-sm text-white/70">Sandra Michel Jimenez Zelaya · Experiencia B2B · Tigo Honduras</p>
        </Bloque>
      );

    case "karla": {
      const llamadas = Math.round(d.hogar.kpis.llamadas_evitadas);
      return (
        <Bloque kicker="Una historia que se repite" titulo={`${nombre} trabaja desde su casa en ${d.hogar.ciudad}`}>
          <Lista items={[
            [Wifi, "Su WiFi empieza a fallar", "El módem se reinicia solo. Ella aguanta unos días."],
            [PhoneCall, `Llama al call center ${llamadas === 2 ? "dos veces" : `${llamadas} veces`}`, "Espera, explica, le agendan un técnico."],
            [Truck, "Llega un técnico", "No encuentra falla física: cambia el canal del WiFi y se va."],
          ]} />
          <Cifra v={d.hogar.kpis.ahorro} t="le cuesta esa experiencia a Tigo"
            fuente={`Visita ${c.costo_por_visita} + ${llamadas} llamadas × ${c.costo_por_llamada}: costos hondureños estimados`} />
        </Bloque>
      );
    }

    case "escala": {
      const evitables = sup.pct_visitas_evitables?.base ?? 0.25;
      return (
        <Bloque kicker="No es un caso aislado" titulo={`${nombre} no es la única`}>
          <Cifra v={c.hogares_nacional} t="hogares con internet de Tigo en Honduras" fuente="Millicom, Form 20-F 2025" />
          <Cifra v={`≈ ${c.hogar_visitas_mes}`} t="visitas de técnicos al mes" fuente={`Estimado: ${pct(sup.tasa_visitas_hogar_mes?.base ?? 0.03)} de los hogares al mes, a validar`} />
          <Cifra v={`1 de cada ${Math.round(1 / evitables)}`} t="se podía resolver sin ir" fuente="Cálculo a confirmar; en la industria, 17–20 % de las visitas no encuentran nada roto" />
        </Bloque>
      );
    }

    case "idea":
      return (
        <Bloque kicker="Nuestra idea" titulo="Escuchar al módem antes de que el cliente tenga que llamar">
          <Lista items={[
            [BrainCircuit, "Detecta", `La inteligencia artificial revisa las señales que el módem ya envía y cada semana marca al ${pct(Number(d.config.hogar.pct_marcados_semana ?? 0.02))} con más riesgo.`],
            [Wrench, "Resuelve", "Se arregla a distancia. Si algo está roto, el técnico va una sola vez y sabiendo qué arreglar."],
            [MessageCircle, "Avisa", "El cliente recibe un WhatsApp: no tiene que llamar ni esperar."],
          ]} />
          <p className="mt-4 text-white/85">Y en <b className="text-celeste">celulares</b>, el mismo sistema avisa cuando se cae una antena.</p>
        </Bloque>
      );

    case "demo":
      return (
        <Bloque kicker="Demo en vivo · prototipo funcionando" titulo={`Lo que habría pasado con ${nombre}`}>
          <Lista items={[
            [BrainCircuit, "La inteligencia artificial lo detecta", "Antes de que ella llame, y antes que la alarma de siempre."],
            [Wrench, "Se arregla de madrugada", "Se actualiza el módem y se ajusta el WiFi, a distancia."],
            [MessageCircle, "Le llega un WhatsApp", "No tuvo que llamar."],
            [Truck, "Dos caminos", "Rojo: sin Tigo Predice. Verde: con Tigo Predice."],
          ]} />
          <Cifra v={d.hogar.kpis.costo_accion} t={`cuesta la acción, frente a ${d.hogar.kpis.ahorro} de la visita y las llamadas`} fuente="Un mensaje de WhatsApp; el arreglo a distancia es automático" />
        </Bloque>
      );

    case "ia": {
      const h = d.inicio.hogar;
      return (
        <Bloque kicker="Inteligencia artificial frente a las alarmas de hoy" titulo="Ve lo que las alarmas todavía no ven">
          <Cifra v={c.hogar_ia_vs_regla} t="más visitas evitables anticipadas" fuente="Con datos de ejemplo y la misma cantidad de casas revisadas" />
          <div className="mt-4 space-y-3">
            <Barra t="Inteligencia artificial" v={h.captura_ia} color="bg-celeste" />
            <Barra t="Alarmas de hoy" v={h.captura_regla} color="bg-white/50" />
          </div>
          <p className="mt-4 text-sm text-white/75">Si con datos reales la inteligencia artificial no supera a las alarmas por {String(d.config.hogar.go_ia_vs_regla_min ?? 1.3)}×, se usan las alarmas de siempre.</p>
        </Bloque>
      );
    }

    case "movil":
      return (
        <Bloque kicker="Lo mismo, en celulares" titulo="Cuando se cae una antena, el cliente se entera por Tigo">
          <Cifra v={`−${pct(d.inicio.piloto.reduccion)}`} t="llamadas cuando se cae una antena" fuente="Con datos de ejemplo, comparando con clientes sin aviso" />
          <div className="mt-4 rounded-xl bg-white/10 p-3 ring-1 ring-white/15">
            <div className="font-bold">CONATEL, el ente regulador, ya lo exige</div>
            <div className="text-sm text-white/85">Avisar a tiempo de las fallas y de cuándo se arreglan.</div>
            <div className="mt-1 text-[11px] text-white/60">Reglamento NR001/26, Art. 39, núm. 15 · La Gaceta, 28-feb-2026</div>
          </div>
        </Bloque>
      );

    case "negocio":
      return (
        <Bloque kicker="Cuánto se ahorra (cálculo prudente)" titulo="Se paga con poco">
          <Cifra v={c.neto_anio1_base} t="de ahorro neto en el primer año (casas + celulares)" fuente={`Cálculo base · de lo peor a lo mejor: ${c.neto_anio1_rango}`} />
          <Cifra v={c.hogar_equilibrio_anio1} t="menos visitas evitables y en casas ya se paga" fuente="Lo mínimo para pagarse en el primer año" />
          <Cifra v={c.equilibrio_anio1} t="menos llamadas y en celulares ya se paga" fuente="Lo mínimo para pagarse en el primer año" />
          <p className="mt-4 text-sm text-white/75">Solo cuenta lo que se puede medir: visitas y llamadas que no hacen falta.</p>
        </Bloque>
      );

    case "confianza":
      return (
        <Bloque kicker="Confianza" titulo="Seguro y medible">
          <Lista items={[
            [Lock, "Solo cómo funciona el módem", "No vemos lo que el cliente hace en internet."],
            [FlaskConical, "Se mide de verdad", `Un ${pct(Number(d.config.piloto.pct_control ?? 0.15))} de los clientes no recibe el servicio, para comparar.`],
            [ShieldCheck, "Normas internacionales", "Seguimos las normas de privacidad y seguridad más exigentes (GDPR, ISO 27001, OWASP)."],
          ]} />
        </Bloque>
      );

    case "pedido":
      return (
        <Bloque kicker="Lo que pedimos" titulo="Una prueba pequeña, con fecha de fin">
          <Cifra v="12 semanas" t={`en ${d.hogar.ciudad}, casas y celulares`} fuente="Comparando con clientes sin el servicio" />
          <Cifra v={c.piloto_costo_base} t={`≈ ${c.piloto_costo_usd}`} fuente={`Rango ${c.piloto_costo_rango}`} />
          <Cifra v="Datos + equipo" t="datos que Tigo ya tiene, de su red y su call center" fuente="y un equipo pequeño de Tigo" />
          <p className="mt-4 text-lg font-bold">En la semana 12, con resultados reales, ustedes deciden <span className="text-celeste">si sigue o no</span>.</p>
        </Bloque>
      );

    case "cierre":
      return (
        <Bloque kicker="Tigo Predice" titulo={d.inicio.posicionamiento}>
          <div className="mt-2 text-3xl font-bold text-celeste">Gracias</div>
          <div className="mt-4 text-white/85">Sandra Michel Jimenez Zelaya · Asistente de Experiencia B2B</div>
          <div className="text-sm text-white/70">sandra.jimenez@tigo.com.hn</div>
        </Bloque>
      );
  }
}

function Bloque({ kicker, titulo, children }: { kicker: string; titulo: string; children: ReactNode }) {
  return (
    <div>
      <div className="text-xs font-bold uppercase tracking-wider text-celeste">{kicker}</div>
      <h2 className="mt-1 mb-4 text-2xl font-extrabold leading-tight">{titulo}</h2>
      {children}
    </div>
  );
}

function Cifra({ v, t, fuente }: { v: string; t: string; fuente: string }) {
  return (
    <div className="mt-3 rounded-xl bg-white/10 p-3 ring-1 ring-white/15">
      <div className="text-3xl font-extrabold tabular-nums text-celeste">{v}</div>
      <div className="font-semibold leading-snug">{t}</div>
      <div className="mt-1 text-[11px] text-white/65">{fuente}</div>
    </div>
  );
}

function Lista({ items }: { items: [typeof Wifi, string, string][] }) {
  return (
    <ul className="space-y-3">
      {items.map(([Icono, t, s]) => (
        <li key={t} className="flex gap-3">
          <Icono size={22} className="mt-0.5 shrink-0 text-celeste" />
          <div><div className="font-bold">{t}</div><div className="text-sm text-white/80">{s}</div></div>
        </li>
      ))}
    </ul>
  );
}

function Barra({ t, v, color }: { t: string; v: number; color: string }) {
  return (
    <div>
      <div className="flex justify-between text-sm"><span>{t}</span><b className="tabular-nums">{pct(v)}</b></div>
      <div className="mt-1 h-3 overflow-hidden rounded-full bg-white/10">
        <div className={clsx("h-full rounded-full", color)} style={{ width: `${v * 100}%` }} />
      </div>
    </div>
  );
}
