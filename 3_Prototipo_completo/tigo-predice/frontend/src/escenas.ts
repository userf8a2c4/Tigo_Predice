// Escenas del modo presentación: cada una abre una pantalla real del sistema y la acompaña con una tarjeta.
// El guion de la relatora va aparte (docs/pitch.md). Las cifras no van aquí: la tarjeta las toma de la API.

export interface Escena {
  id: "portada" | "karla" | "escala" | "idea" | "demo" | "ia" | "movil" | "negocio" | "confianza" | "pedido" | "cierre";
  titulo: string;
  seg: number;
  /** Pantalla del sistema que se ve durante la escena. */
  ruta: string;
  /** id de la sección a la que se desplaza la pantalla (si no, va arriba). */
  foco?: string;
}

export const ESCENAS: Escena[] = [
  { id: "portada", titulo: "Inicio", seg: 10, ruta: "/" },
  { id: "karla", titulo: "Karla", seg: 26, ruta: "/hogar" },
  { id: "escala", titulo: "No es un caso aislado", seg: 20, ruta: "/" },
  { id: "idea", titulo: "Nuestra idea", seg: 20, ruta: "/", foco: "como-funciona" },
  { id: "demo", titulo: "Demo en vivo", seg: 80, ruta: "/hogar" },
  { id: "ia", titulo: "IA vs. regla", seg: 20, ruta: "/modelo" },
  { id: "movil", titulo: "Móvil", seg: 22, ruta: "/falla?final" },
  { id: "negocio", titulo: "Caso de negocio", seg: 26, ruta: "/negocio" },
  { id: "confianza", titulo: "Confianza", seg: 14, ruta: "/produccion" },
  { id: "pedido", titulo: "El pedido", seg: 26, ruta: "/piloto" },
  { id: "cierre", titulo: "Cierre", seg: 8, ruta: "/" },
];

export const DURACION_TOTAL = ESCENAS.reduce((s, e) => s + e.seg, 0);

/** 272 → "4:32" */
export function reloj(seg: number) {
  const s = Math.max(0, Math.round(seg));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}
