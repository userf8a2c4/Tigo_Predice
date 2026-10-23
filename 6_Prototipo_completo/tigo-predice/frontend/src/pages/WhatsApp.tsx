import clsx from "clsx";
import { Ticket as IconoTicket } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { api, type Conversacion } from "../api";
import Telefono from "../components/Telefono";
import { Fase2Aviso, PrioridadBadge, Tarjeta, Titulo } from "../components/ui";
import { useDatos } from "../hooks";

export const SUGERENCIAS: Record<string, string[]> = {
  aviso_falla: ["¿A qué hora vuelve el servicio?", "Gracias por avisar", "AGENTE"],
  autodiagnostico: ["1", "Sigue igual", "Ya funciona", "AGENTE"],
  oferta_retencion: ["SÍ", "No gracias", "AGENTE"],
  retencion_agente: ["SÍ", "AGENTE"],
  recordatorio_pago: ["PAGAR", "PLAZO", "AGENTE"],
};

const ESTADO: Record<string, string> = {
  abierta: "bg-celeste/20 text-tigo",
  resuelta: "bg-exito/15 text-exito",
  escalada: "bg-ambar/20 text-amber-800",
};

export default function WhatsApp() {
  const ubicacion = useLocation();
  const convs = useDatos(api.conversaciones);
  const tickets = useDatos(api.tickets);
  const [activa, setActiva] = useState<string | null>((ubicacion.state as { cliente?: string } | null)?.cliente ?? null);

  useEffect(() => {
    if (!activa && convs.datos?.length) setActiva(convs.datos[0].cliente_id);
  }, [convs.datos, activa]);

  const conv = convs.datos?.find((c) => c.cliente_id === activa) ?? null;

  const enviar = async (texto: string) => {
    if (!conv) return;
    const nueva = await api.responder(conv.cliente_id, texto);
    convs.setDatos((lista) => (lista ?? []).map((c: Conversacion) => (c.cliente_id === nueva.cliente_id ? nueva : c)));
    tickets.recargar();
  };

  return (
    <div className="space-y-4">
      <Fase2Aviso />
      <div>
        <h1 className="text-2xl font-bold text-slate-900 lg:text-3xl">WhatsApp y tickets</h1>
        <p className="text-slate-500">
          Simulador del canal: responda como si fuera el cliente. Si no se resuelve, se crea un ticket con el resumen ya
          escrito para el agente.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[300px_400px_1fr]">
        <Tarjeta className="p-3">
          <Titulo>Conversaciones</Titulo>
          {!convs.datos?.length && (
            <div className="p-2 text-sm text-slate-500">
              Aún no hay conversaciones. Ejecute una acción desde{" "}
              <Link to="/clientes" className="font-semibold text-tigo underline">
                Clientes en riesgo
              </Link>{" "}
              o corra la demo.
            </div>
          )}
          <div className="space-y-1.5">
            {convs.datos?.map((c) => (
              <button
                key={c.cliente_id}
                onClick={() => setActiva(c.cliente_id)}
                className={clsx(
                  "w-full rounded-xl p-2.5 text-left transition",
                  c.cliente_id === activa ? "bg-tigo text-white" : "hover:bg-slate-50",
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate font-semibold">{c.nombre}</span>
                  <span className={clsx("rounded-full px-2 py-0.5 text-[11px] font-semibold", ESTADO[c.estado])}>
                    {c.estado}
                  </span>
                </div>
                <div className={clsx("truncate text-xs", c.cliente_id === activa ? "text-white/75" : "text-slate-500")}>
                  {c.accion_nombre}
                </div>
              </button>
            ))}
          </div>
        </Tarjeta>

        <Telefono conv={conv} onEnviar={enviar} sugerencias={conv ? SUGERENCIAS[conv.accion] : []} alto="clamp(420px, 70vh, 680px)" />

        <Tarjeta className="p-4">
          <Titulo extra={<span className="text-sm text-slate-500">{tickets.datos?.length ?? 0} tickets</span>}>
            Tickets para agentes
          </Titulo>
          <p className="mb-3 text-sm text-slate-500">
            <b>Experiencia del colaborador:</b> el agente recibe el caso con contexto, factores de la IA y pasos ya
            realizados. No tiene que volver a preguntarle nada al cliente.
          </p>
          {!tickets.datos?.length && <div className="text-sm text-slate-400">Sin tickets todavía.</div>}
          <div className="space-y-3">
            {tickets.datos?.map((t) => (
              <div key={t.ticket_id} className="aparecer rounded-xl border border-slate-200 p-3">
                <div className="flex items-center gap-2">
                  <IconoTicket size={16} className="text-tigo" />
                  <span className="font-semibold">{t.ticket_id}</span>
                  <span className="text-sm text-slate-500">· {t.tipo}</span>
                  <span className="ml-auto">
                    <PrioridadBadge p={t.prioridad} />
                  </span>
                </div>
                <pre className="mt-2 whitespace-pre-wrap rounded-lg bg-slate-50 p-3 font-sans text-[13px] leading-relaxed text-slate-700">
                  {t.resumen}
                </pre>
              </div>
            ))}
          </div>
        </Tarjeta>
      </div>
    </div>
  );
}
