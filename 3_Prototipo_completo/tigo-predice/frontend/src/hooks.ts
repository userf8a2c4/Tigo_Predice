import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import type { Config } from "./api";
import type { Escena } from "./escenas";

/** Carga datos de la API y permite recargarlos. Vuelve a cargar cuando cambian `deps`. */
export function useDatos<T>(cargar: () => Promise<T>, deps: unknown[] = []) {
  const [datos, setDatos] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);
  const funcion = useRef(cargar);
  useEffect(() => {
    funcion.current = cargar;
  });

  const recargar = useCallback(async () => {
    setCargando(true);
    try {
      setDatos(await funcion.current());
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setCargando(false);
    }
  }, []);

  const clave = JSON.stringify(deps);
  useEffect(() => {
    recargar();
  }, [recargar, clave]);

  return { datos, error, cargando, recargar, setDatos };
}

export const ConfigContext = createContext<Config | null>(null);
export const useConfig = () => useContext(ConfigContext);

/** Ancho actual de la ventana (para ajustar gráficos con etiquetas largas en pantallas chicas). */
export function useAncho() {
  const [ancho, setAncho] = useState(() => (typeof window === "undefined" ? 1366 : window.innerWidth));
  useEffect(() => {
    const f = () => setAncho(window.innerWidth);
    window.addEventListener("resize", f);
    return () => window.removeEventListener("resize", f);
  }, []);
  return ancho;
}

/** `?final` abre directo el resultado de una demo (respaldo del presentador y revisión visual). */
export function usePideFinal() {
  return new URLSearchParams(useLocation().search).has("final");
}

/** Modo presentación: escena en curso (null si no se está presentando) y cómo abrirlo desde cualquier pantalla. */
export interface EstadoPresentacion {
  escena: Escena["id"] | null;
  abrir: () => void;
}
export const PresentacionContext = createContext<EstadoPresentacion>({ escena: null, abrir: () => undefined });
export const usePresentacion = () => useContext(PresentacionContext);
