import clsx from "clsx";
import { CheckCheck, SendHorizontal, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { Conversacion } from "../api";

const RESULTADOS: Record<string, string> = {
  llamada_evitada: "✅ Llamada evitada",
  retenido: "💙 Cliente retenido",
  ticket: "🎫 Escalado con ticket",
  pago: "💳 Pago realizado",
  arreglo_pago: "🤝 Arreglo de pago",
  visita_agendada: "🛠️ Visita agendada con diagnóstico",
  visita_evitada: "✅ Visita técnica evitada",
};

export default function Telefono({
  conv,
  escribiendo,
  onEnviar,
  sugerencias = [],
  alto = 560,
}: {
  conv: Conversacion | null;
  escribiendo?: boolean;
  onEnviar?: (texto: string) => void;
  sugerencias?: string[];
  alto?: number | string;
}) {
  const [texto, setTexto] = useState("");
  const chat = useRef<HTMLDivElement>(null);

  // Baja solo dentro del chat (scrollIntoView movería toda la página durante la demo)
  useEffect(() => {
    const el = chat.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [conv?.mensajes.length, conv?.resultado, escribiendo]);

  const enviar = (t: string) => {
    if (!t.trim() || !onEnviar) return;
    onEnviar(t.trim());
    setTexto("");
  };

  return (
    <div
      className="mx-auto flex w-full max-w-[380px] flex-col overflow-hidden rounded-[2.2rem] border-[10px] border-slate-900 bg-slate-900 shadow-2xl"
      style={{ height: alto }}
    >
      <div className="flex items-center gap-3 bg-whatsapp px-4 py-3 text-white">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-sm font-bold text-tigo">
          {conv ? conv.nombre[0] : "T"}
        </div>
        <div className="min-w-0 flex-1">
          <div className="truncate font-semibold">{conv ? conv.nombre : "Tigo Honduras"}</div>
          <div className="truncate text-xs text-white/75">
            {escribiendo ? "escribiendo…" : conv ? `${conv.telefono} · ${conv.ciudad}` : "Cuenta de empresa"}
          </div>
        </div>
      </div>

      <div ref={chat} className="fondo-chat flex-1 space-y-2 overflow-y-auto px-3 py-3">
        {!conv && (
          <div className="mt-10 text-center text-sm text-slate-500">
            Aquí aparecerán los mensajes proactivos que Tigo Predice envía a los clientes.
          </div>
        )}
        {conv?.mensajes.map((m, i) =>
          m.de === "sistema" ? (
            <div key={i} className="aparecer mx-auto w-fit rounded-lg bg-amber-100 px-3 py-1 text-center text-xs text-amber-900">
              {m.texto}
            </div>
          ) : (
            <div key={i} className={clsx("aparecer flex", m.de === "cliente" ? "justify-end" : "justify-start")}>
              <div
                className={clsx(
                  "max-w-[85%] rounded-xl px-3 py-2 text-[15px] leading-snug shadow-sm",
                  m.de === "cliente" ? "rounded-tr-sm bg-burbuja" : "rounded-tl-sm bg-white",
                )}
              >
                {m.de === "tigo" && <div className="mb-0.5 text-xs font-semibold text-tigo">Tigo</div>}
                <div className="whitespace-pre-wrap text-slate-800">{m.texto}</div>
                <div className="mt-0.5 flex items-center justify-end gap-1 text-[11px] text-slate-400">
                  {m.hora}
                  {m.de === "cliente" && <CheckCheck size={14} className="text-sky-500" />}
                </div>
              </div>
            </div>
          ),
        )}
        {escribiendo && (
          <div className="flex justify-end">
            <div className="escribiendo rounded-xl bg-burbuja px-3 py-2.5">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
        {conv?.resultado && (
          <div className="aparecer mx-auto w-fit rounded-full bg-tigo px-3 py-1 text-xs font-semibold text-white">
            {RESULTADOS[conv.resultado] ?? conv.resultado}
          </div>
        )}
      </div>

      {conv && (
        <div className="flex items-center gap-1.5 bg-slate-100 px-3 py-1 text-[11px] text-slate-500">
          <Sparkles size={12} />
          {conv.fuente === "claude" ? "Mensaje redactado por IA (Claude)" : "Mensaje de plantilla aprobada"} ·
          guardrails: {conv.guardrails}
        </div>
      )}

      {onEnviar && conv && (
        <div className="bg-slate-100 px-2 pb-2">
          {sugerencias.length > 0 && conv.estado === "abierta" && (
            <div className="flex flex-wrap gap-1.5 py-1.5">
              {sugerencias.map((s) => (
                <button
                  key={s}
                  onClick={() => enviar(s)}
                  className="rounded-full border border-slate-300 bg-white px-2.5 py-1 text-xs text-slate-700 hover:border-tigo hover:text-tigo"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
          <form
            className="flex items-center gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              enviar(texto);
            }}
          >
            <input
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              placeholder="Responder como el cliente…"
              className="flex-1 rounded-full bg-white px-4 py-2 text-sm outline-none ring-1 ring-slate-200 focus:ring-tigo"
            />
            <button type="submit" className="rounded-full bg-whatsapp p-2.5 text-white" aria-label="Enviar">
              <SendHorizontal size={18} />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
