import { LockKeyhole } from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { api } from "../api";
import { Logo } from "./Layout";

/** Pide el token solo si el servidor corre en modo protegido (TIGO_TOKEN). En la demo local no aparece. */
export default function Sesion({ children }: { children: ReactNode }) {
  const [estado, setEstado] = useState<"cargando" | "abierta" | "cerrada">("cargando");
  const [token, setToken] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.sesion()
      .then((s) => setEstado(!s.requiere || s.activa ? "abierta" : "cerrada"))
      .catch(() => setEstado("abierta")); // si la API no responde, cada pantalla muestra su propio error
  }, []);

  if (estado === "cargando") return null;
  if (estado === "abierta") return <>{children}</>;
  return (
    <div className="flex h-full items-center justify-center bg-tigo-900 p-4">
      <form
        className="w-full max-w-sm space-y-4 rounded-2xl bg-white p-6 shadow-2xl"
        onSubmit={async (e) => {
          e.preventDefault();
          setError(null);
          try {
            await api.abrirSesion(token);
            setToken("");
            setEstado("abierta");
          } catch (err) {
            setError((err as Error).message);
          }
        }}
      >
        <Logo claro={false} />
        <div className="flex items-center gap-2 text-sm text-slate-600"><LockKeyhole size={16} /> Acceso restringido</div>
        <label htmlFor="token" className="block text-sm font-medium text-slate-700">Token de acceso</label>
        <input id="token" type="password" autoComplete="current-password" value={token} onChange={(e) => setToken(e.target.value)}
          className="w-full rounded-xl border border-slate-200 px-3 py-2 outline-none focus:ring-2 focus:ring-tigo" />
        {error && <div className="text-sm text-alerta">{error}</div>}
        <button type="submit" className="w-full rounded-xl bg-tigo px-4 py-2 font-semibold text-white">Entrar</button>
        <p className="text-xs text-slate-400">La sesión vence en 8 horas. En producción se usa el inicio de sesión corporativo (SSO).</p>
      </form>
    </div>
  );
}
