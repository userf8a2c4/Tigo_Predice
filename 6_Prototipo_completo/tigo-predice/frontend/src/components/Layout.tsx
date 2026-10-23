import clsx from "clsx";
import { BrainCircuit, Calculator, FlaskConical, Home, MessageCircle, Radio, Router, ShieldCheck, Sparkles, Users } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { api } from "../api";
import { ConfigContext, useDatos } from "../hooks";

const NAV_PILOTO = [
  { a: "/", texto: "Inicio", icono: Home },
  { a: "/hogar", texto: "Hogar en vivo ★", icono: Router },
  { a: "/falla", texto: "Falla masiva en vivo", icono: Radio },
  { a: "/piloto", texto: "Resultados del piloto", icono: FlaskConical },
  { a: "/negocio", texto: "Caso de negocio", icono: Calculator },
  { a: "/modelo", texto: "Modelo de IA", icono: BrainCircuit },
  { a: "/produccion", texto: "Listo para producción", icono: ShieldCheck },
];
const NAV_FASE2 = [
  { a: "/clientes", texto: "Clientes en riesgo", icono: Users },
  { a: "/whatsapp", texto: "WhatsApp y tickets", icono: MessageCircle },
];

export function Logo({ claro = true }: { claro?: boolean }) {
  return (
    <div className="flex items-center gap-2.5">
      <svg viewBox="0 0 64 64" className="h-9 w-9 shrink-0">
        <rect width="64" height="64" rx="14" fill={claro ? "#ffffff" : "#00377B"} />
        <path d="M14 40c6-14 12-20 18-20s12 6 18 20" fill="none" stroke="#00C8FF" strokeWidth="6" strokeLinecap="round" />
        <circle cx="32" cy="44" r="5" fill={claro ? "#00377B" : "#fff"} />
      </svg>
      <div className="leading-tight">
        <div className={clsx("text-xl font-extrabold tracking-tight", claro ? "text-white" : "text-tigo")}>
          Tigo <span className="text-celeste">Predice</span>
        </div>
        <div className={clsx("text-[11px]", claro ? "text-white/60" : "text-slate-500")}>Evita la llamada y la visita</div>
      </div>
    </div>
  );
}

function Enlace({ a, texto, icono: Icono }: { a: string; texto: string; icono: typeof Home }) {
  return (
    <NavLink
      to={a}
      end={a === "/"}
      className={({ isActive }) =>
        clsx(
          "flex items-center gap-3 rounded-xl px-3 py-2 text-[15px] font-medium transition",
          isActive ? "bg-white text-tigo shadow" : "text-white/80 hover:bg-white/10 hover:text-white",
        )
      }
    >
      <Icono size={18} />
      {texto}
    </NavLink>
  );
}

export default function Layout() {
  const { datos: config } = useDatos(api.config);
  const navegar = useNavigate();
  const modoIA = config?.llm_modo === "IA";

  return (
    <ConfigContext.Provider value={config}>
      <div className="flex h-full">
        <aside className="hidden w-64 shrink-0 flex-col bg-tigo p-4 text-white lg:flex">
          <Logo />
          <div className="mt-6 px-3 text-[11px] font-semibold uppercase tracking-wider text-celeste">Fase 1 · Piloto Hogar + Móvil</div>
          <nav className="mt-1 space-y-0.5">{NAV_PILOTO.map((n) => <Enlace key={n.a} {...n} />)}</nav>
          <div className="mt-5 px-3 text-[11px] font-semibold uppercase tracking-wider text-white/50">Fase 2 · Visión</div>
          <nav className="mt-1 space-y-0.5 opacity-80">{NAV_FASE2.map((n) => <Enlace key={n.a} {...n} />)}</nav>
          <div className="mt-auto space-y-1.5 rounded-xl bg-tigo-900/60 p-3 text-xs text-white/70">
            <div>Modelo: <span className="font-semibold text-white">{config?.modelo ?? "…"}</span></div>
            <div title={config?.llm_estado}>Mensajes: <span className="font-semibold text-white">{config?.llm_estado ?? "…"}</span></div>
            <div>Concurso Tigo CX Month · Sharks</div>
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="flex flex-wrap items-center gap-2 border-b border-slate-200 bg-white px-4 py-2.5 lg:px-6">
            <div className="lg:hidden"><Logo claro={false} /></div>
            <span className="rounded-full bg-ambar/15 px-3 py-1 text-xs font-semibold text-amber-800 ring-1 ring-ambar/40">
              ⚠ Datos simulados<span className="hidden sm:inline"> — supuestos a validar con Tigo</span>
            </span>
            <span
              title={config?.llm_estado}
              className={clsx("flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold ring-1",
                modoIA ? "bg-exito/10 text-exito ring-exito/30" : "bg-slate-100 text-slate-600 ring-slate-200")}
            >
              <Sparkles size={12} /> {config ? (modoIA ? "Modo IA" : "Modo plantillas") : "…"}
            </span>
            <button onClick={() => navegar("/hogar")}
              className="ml-auto flex items-center gap-2 rounded-xl bg-celeste px-4 py-2 text-sm font-bold text-tigo-900 shadow hover:brightness-105">
              <Router size={16} /> <span className="hidden sm:inline">Hogar en vivo</span>
            </button>
            <button onClick={() => navegar("/falla")}
              className="flex items-center gap-2 rounded-xl bg-tigo/10 px-3 py-2 text-sm font-semibold text-tigo hover:bg-tigo/15" title="Falla masiva en vivo">
              <Radio size={16} /> <span className="hidden xl:inline">Falla masiva</span>
            </button>
          </header>
          <nav className="flex gap-1 overflow-x-auto border-b border-slate-200 bg-white px-2 py-1.5 lg:hidden">
            {[...NAV_PILOTO, ...NAV_FASE2].map(({ a, texto }) => (
              <NavLink key={a} to={a} end={a === "/"}
                className={({ isActive }) => clsx("whitespace-nowrap rounded-lg px-3 py-1.5 text-sm", isActive ? "bg-tigo text-white" : "text-slate-600")}>
                {texto}
              </NavLink>
            ))}
          </nav>
          <main className="flex-1 overflow-y-auto p-3 sm:p-4 lg:p-6">
            <div className="mx-auto w-full max-w-[1800px]">
              <Outlet />
              <FuenteDatos />
            </div>
          </main>
        </div>
      </div>
    </ConfigContext.Provider>
  );
}

/** Fuente de los datos de muestra, visible al pie de cada pantalla. */
function FuenteDatos() {
  return (
    <footer className="mt-6 border-t border-slate-200 pt-3 text-[11px] leading-relaxed text-slate-500">
      <b>Fuente de los datos de muestra:</b> los clientes, hogares, la telemetría de los módems y las fallas son sintéticos,
      generados por el prototipo con semilla fija (<code>ml/generar_datos.py</code> y <code>ml/generar_hogar.py</code>) y
      parámetros de <code>config/negocio.toml</code>. La escala y los costos se calibran con datos públicos: Millicom, Form 20-F
      2025 (191 mil hogares y 5.0 M de clientes móviles de Tigo Honduras); CONATEL (mercado de internet fijo y líneas
      móviles); BCH (tipo de cambio); tigo.com.hn (precios de planes); tarifas de WhatsApp Business y costos de centros de
      contacto en Honduras. Detalle y enlaces en <code>docs/revision_critica.md</code> y <code>docs/fuentes.md</code>.
    </footer>
  );
}
