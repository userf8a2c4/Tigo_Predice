import clsx from "clsx";
import { ArrowRight, Database, LockKeyhole, ShieldCheck, TriangleAlert, Users } from "lucide-react";
import { api } from "../api";
import { Cargando, ErrorCaja, Tarjeta, Titulo } from "../components/ui";
import { useDatos } from "../hooks";

const NIVEL: Record<string, string> = {
  Alta: "bg-alerta/15 text-alerta",
  Alto: "bg-alerta/15 text-alerta",
  Media: "bg-ambar/20 text-amber-800",
  Medio: "bg-ambar/20 text-amber-800",
  Baja: "bg-slate-100 text-slate-600",
  Bajo: "bg-slate-100 text-slate-600",
};

export default function Produccion() {
  const { datos: p, error } = useDatos(api.produccion);
  if (error) return <ErrorCaja error={error} />;
  if (!p) return <Cargando />;
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 lg:text-3xl">Listo para producción</h1>
        <p className="text-slate-500">
          El piloto arranca con <b>exportaciones CSV diarias</b>, sin integraciones en tiempo real: menos costo y menos riesgo.
          Lo regulatorio se valida con Legal de Tigo antes de enviar el primer mensaje.
        </p>
      </div>

      <Tarjeta className="p-5">
        <Titulo><span className="flex items-center gap-2"><Database size={18} /> Integración: qué dato, de dónde y cada cuánto</span></Titulo>
        <div role="region" aria-label="Integración de datos" tabIndex={0} className="overflow-x-auto focus:outline-none focus-visible:ring-2 focus-visible:ring-celeste">
          <table className="w-full min-w-[820px] text-sm">
            <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-500"><th className="pb-2">Fuente</th><th>Dato</th><th>Piloto</th><th /><th>Producción</th></tr></thead>
            <tbody>
              {p.integracion.map((i) => (
                <tr key={i.fuente} className="border-t border-slate-100 align-top">
                  <td className="py-2 pr-3 font-semibold text-tigo">{i.fuente}</td>
                  <td className="py-2 pr-3 text-slate-600">{i.dato}</td>
                  <td className="py-2 pr-2"><span className="rounded-md bg-celeste-50 px-2 py-0.5 text-xs text-tigo">{i.frecuencia_piloto}</span></td>
                  <td className="py-2 text-slate-300"><ArrowRight size={14} /></td>
                  <td className="py-2"><span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs text-slate-600">{i.frecuencia_produccion}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Tarjeta>

      <Tarjeta className="p-5">
        <Titulo><span className="flex items-center gap-2"><LockKeyhole size={18} /> Seguridad y privacidad: prototipo y producción</span></Titulo>
        <p className="mb-3 text-sm text-slate-600">
          Marcos internacionales: ISO 27001/27701/42001, SOC 2, NIST, OWASP (API y LLM) y GDPR como estándar de referencia.
          Detalle, marco legal de Honduras y evaluación de impacto en <b>docs/seguridad_y_privacidad.md</b>.
        </p>
        <div role="region" aria-label="Controles de seguridad" tabIndex={0} className="overflow-x-auto focus:outline-none focus-visible:ring-2 focus-visible:ring-celeste">
          <table className="w-full min-w-[720px] text-sm">
            <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-500"><th className="pb-2">Control</th><th>Prototipo</th><th>Producción</th></tr></thead>
            <tbody>
              {p.seguridad.map((s) => (
                <tr key={s.control} className="border-t border-slate-100 align-top">
                  <td className="py-2 pr-3 font-semibold text-tigo">{s.control}</td>
                  <td className="py-2 pr-3 text-slate-700">{s.estado}</td>
                  <td className="py-2 text-slate-500">{s.produccion}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Tarjeta>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <Tarjeta className="p-5">
          <Titulo><span className="flex items-center gap-2"><ShieldCheck size={18} /> Consentimiento, canal y cumplimiento</span></Titulo>
          <dl className="space-y-2 text-sm">
            {p.consentimiento.map((c) => (
              <div key={c.tema}><dt className="font-semibold text-slate-800">{c.tema}</dt><dd className="text-slate-600">{c.detalle}</dd></div>
            ))}
          </dl>
        </Tarjeta>

        <Tarjeta className="p-5">
          <Titulo><span className="flex items-center gap-2"><Users size={18} /> Equipo y plan del piloto</span></Titulo>
          <div className="mb-4 grid grid-cols-1 gap-2 sm:grid-cols-3">
            {p.plan.map((f) => (
              <div key={f.semanas} className="rounded-xl bg-tigo/5 p-3">
                <div className="text-xs font-semibold text-tigo">Semanas {f.semanas}</div>
                <div className="font-bold text-slate-800">{f.fase}</div>
                <div className="text-xs text-slate-600">{f.actividades}</div>
              </div>
            ))}
          </div>
          <table className="w-full text-sm">
            <tbody>
              {p.equipo.map((e) => (
                <tr key={e.rol} className="border-t border-slate-100">
                  <td className="py-1.5 pr-2 font-medium text-slate-800">{e.rol}</td>
                  <td className="py-1.5 pr-2 text-xs text-slate-500">{e.dedicacion}</td>
                  <td className="py-1.5 text-slate-600">{e.responsabilidad}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Tarjeta>
      </div>

      <Tarjeta className="p-5">
        <Titulo><span className="flex items-center gap-2"><TriangleAlert size={18} /> Matriz de riesgos</span></Titulo>
        <div role="region" aria-label="Matriz de riesgos" tabIndex={0} className="overflow-x-auto focus:outline-none focus-visible:ring-2 focus-visible:ring-celeste">
          <table className="w-full min-w-[820px] text-sm">
            <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-500"><th className="pb-2">Riesgo</th><th>Probabilidad</th><th>Impacto</th><th>Mitigación</th></tr></thead>
            <tbody>
              {p.riesgos.map((r) => (
                <tr key={r.riesgo} className="border-t border-slate-100 align-top">
                  <td className="py-2 pr-3 font-medium text-slate-800">{r.riesgo}</td>
                  <td className="py-2 pr-2"><span className={clsx("rounded-full px-2 py-0.5 text-xs font-semibold", NIVEL[r.probabilidad])}>{r.probabilidad}</span></td>
                  <td className="py-2 pr-2"><span className={clsx("rounded-full px-2 py-0.5 text-xs font-semibold", NIVEL[r.impacto])}>{r.impacto}</span></td>
                  <td className="py-2 text-slate-600">{r.mitigacion}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Tarjeta>
    </div>
  );
}
