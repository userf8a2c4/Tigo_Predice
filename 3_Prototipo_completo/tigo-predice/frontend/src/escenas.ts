// Escenas del modo presentación: cada una abre una pantalla real del sistema y la acompaña con una tarjeta.
// Los subtítulos son el mismo texto del guion (docs/pitch.md; una prueba verifica que coincidan).
// Las cifras no van aquí: la tarjeta las toma de la API.

/** [segundo de la escena en que aparece, texto] */
export type Subtitulo = [number, string];

/**
 * Capturas del sistema que usan las láminas del modo resumen. Cada nombre es una tarjeta marcada con `foco` en su
 * página; docs/entregables/gen_capturas.mjs la recorta y la guarda en src/assets/capturas.
 */
export const CAPTURAS_SISTEMA = [
  "hogar-casa", "hogar-diagnostico", "hogar-telefono", "modelo-captura", "falla-resultado", "negocio-escenarios",
  "produccion-seguridad", "piloto-decision",
] as const;

export interface Escena {
  id: "portada" | "karla" | "escala" | "idea" | "demo" | "ia" | "movil" | "negocio" | "confianza" | "pedido" | "cierre";
  titulo: string;
  seg: number;
  /** Pantalla del sistema que se ve durante la escena. */
  ruta: string;
  /** id de la sección a la que se desplaza la pantalla (si no, va arriba). */
  foco?: string;
  /** Modo resumen: capturas del sistema que respaldan la lámina de esta escena. */
  capturas?: (typeof CAPTURAS_SISTEMA)[number][];
  subtitulos: Subtitulo[];
}

export const ESCENAS: Escena[] = [
  { id: "portada", titulo: "Inicio", seg: 10, ruta: "/", subtitulos: [
    [0.5, "Buenos días. Les quiero contar la historia de una clienta…"],
    [5, "…y de cómo evitar que se repita."],
  ] },
  { id: "karla", titulo: "Karla", seg: 26, ruta: "/hogar", capturas: ["hogar-casa"], subtitulos: [
    [0, "Karla trabaja desde su casa, en San Pedro Sula."],
    [4, "Un día su internet empieza a fallar, y ella aguanta unos días."],
    [8.5, "Llama a Tigo, espera, vuelve a llamar. Le mandan un técnico…"],
    [14, "…que no encuentra nada roto: solo ajusta el WiFi y se va."],
    [19.5, "A Tigo le cuesta dinero; a Karla, la paciencia."],
    [23, "Y Karla no es la única."],
  ] },
  { id: "escala", titulo: "No es un caso aislado", seg: 20, ruta: "/", subtitulos: [
    [0, "Tigo tiene cientos de miles de hogares con internet."],
    [4.5, "Cada mes, los técnicos visitan miles de esas casas."],
    [9, "Calculamos que una de cada cuatro visitas se podía resolver sin ir."],
    [15, "Son cálculos que confirmaremos con los datos de Tigo."],
  ] },
  { id: "idea", titulo: "Nuestra idea", seg: 20, ruta: "/", foco: "como-funciona", capturas: ["hogar-diagnostico", "hogar-telefono"], subtitulos: [
    [0, "El módem, el aparato de internet de la casa, avisa días antes cuando algo va mal."],
    [5, "Pero hoy esas señales se revisan cuando el problema ya es grande."],
    [9, "Nuestra idea: que una inteligencia artificial las revise a tiempo."],
    [13, "Se arregla a distancia, sin que el cliente tenga que llamar."],
    [17, "Veamos qué habría pasado con Karla."],
  ] },
  // Tiempos alineados con «Hogar en vivo» a 1× (arranca 0.6 s después de entrar a la escena)
  { id: "demo", titulo: "Demo en vivo", seg: 80, ruta: "/hogar", subtitulos: [
    [1, "Este es el internet de Karla en un día normal."],
    [9.5, "Empieza el problema. Karla todavía no nota nada."],
    [14.5, "La inteligencia artificial lo detecta. La alarma de siempre, todavía no."],
    [19.5, "A la derecha, el porqué: su WiFi empeora cada día."],
    [24, "De madrugada se arregla a distancia, y a Karla le llega un WhatsApp."],
    [31, "Ahora vemos dos caminos: en rojo, sin Tigo Predice; en verde, con Tigo Predice."],
    [38.5, "Sin Tigo Predice, ese día Karla habría llamado a Tigo…"],
    [44, "…recién ahí habría sonado la alarma de siempre…"],
    [48.5, "…y habría ido un técnico a arreglar algo que se resolvía a distancia."],
    [56, "Con Tigo Predice, su internet sigue bien y ella no tuvo que hacer nada."],
    [70.5, "Resultado: ni visita ni llamadas, por el costo de un mensaje."],
  ] },
  { id: "ia", titulo: "IA frente a las alarmas", seg: 20, ruta: "/modelo", capturas: ["modelo-captura"], subtitulos: [
    [0, "Tigo ya tiene alarmas que avisan cuando una señal pasa cierto límite."],
    [4.5, "La pregunta es si la inteligencia artificial ve más que esas alarmas."],
    [9, "En nuestra prueba con datos de ejemplo, ve el doble."],
    [13, "Si con datos reales no gana, usamos las alarmas de siempre."],
  ] },
  { id: "movil", titulo: "Celulares", seg: 22, ruta: "/falla?final", capturas: ["falla-resultado"], subtitulos: [
    [0, "Lo mismo sirve para los celulares."],
    [3.5, "Si se cae una antena, el cliente se entera por Tigo antes de tener que llamar."],
    [10, "Avisar de las fallas ya es obligatorio para CONATEL, el ente regulador."],
    [16, "Así cumplimos la norma y, además, ahorramos."],
  ] },
  { id: "negocio", titulo: "Cuánto se ahorra", seg: 26, ruta: "/negocio", capturas: ["negocio-escenarios"], subtitulos: [
    [0, "Solo contamos el ahorro que se puede medir: visitas y llamadas que no hacen falta."],
    [6.5, "Si además se quedan más clientes, mejor, pero no lo sumamos hasta medirlo."],
    [12.5, "Y con muy poco, la idea se paga sola en el primer año…"],
    [17, "…tanto en el internet de las casas como en los celulares."],
  ] },
  { id: "confianza", titulo: "Confianza", seg: 14, ruta: "/produccion", capturas: ["produccion-seguridad"], subtitulos: [
    [0, "No vemos lo que el cliente hace en internet:"],
    [4, "solo si su aparato funciona bien."],
    [7.5, "Y medimos el resultado comparando con clientes que no reciben el servicio."],
  ] },
  { id: "pedido", titulo: "Lo que pedimos", seg: 26, ruta: "/piloto", capturas: ["piloto-decision"], subtitulos: [
    [0, "Lo que pedimos es una prueba pequeña:"],
    [3, "una ciudad, doce semanas, datos que Tigo ya tiene y un equipo pequeño."],
    [11, "Al final, con resultados reales…"],
    [15.5, "…ustedes deciden si sigue o no."],
  ] },
  { id: "cierre", titulo: "Cierre", seg: 8, ruta: "/", subtitulos: [
    [0, "Los chatbots atienden la llamada. Tigo Predice evita que ocurra."],
    [5, "Gracias."],
  ] },
];

export const DURACION_TOTAL = ESCENAS.reduce((s, e) => s + e.seg, 0);

/** Un subtítulo queda en pantalla hasta el siguiente, y como máximo este tiempo. */
export const SUBTITULO_MAX_SEG = 8;

/** Subtítulo visible en el segundo `t` de la escena (o null entre frases). */
export function subtituloEn(escena: Escena, t: number): string | null {
  const s = escena.subtitulos;
  for (let k = s.length - 1; k >= 0; k--) {
    const [inicio, texto] = s[k];
    if (t < inicio) continue;
    const fin = Math.min(k + 1 < s.length ? s[k + 1][0] : escena.seg, inicio + SUBTITULO_MAX_SEG);
    return t < fin ? texto : null;
  }
  return null;
}

/** 272 → "4:32" */
export function reloj(seg: number) {
  const s = Math.max(0, Math.round(seg));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}
