// Presentación para AI Shark Tank (Tigo CX Month), con las secciones que pide el formato del concurso:
// categoría, problema, usuario, idea con IA e impacto esperado, más el pedido a los Sharks.
// Uso: node gen_shark.js <salida.pptx> <docs/capturas> <datos_deck.json> <fondo.png>
// Requiere NODE_PATH con pptxgenjs y APPLY_THEME: ruta a un módulo que escribe los colores de THEME en el tema del .pptx.
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.APPLY_THEME);

const [SALIDA, CAPT, DATOS, FONDO] = process.argv.slice(2);
const D = JSON.parse(fs.readFileSync(DATOS, "utf8"));
const C = D.cifras;
const PH = D.piloto_hogar;
// Espacios no separables: que una cifra como "L 15 M" nunca se parta entre dos líneas
const nb = (t) => t.replace(/(L) /g, "$1 ").replace(/ (M|mil|%)\b/g, " $1").replace(/ %/g, " %");
const num = (t) => Number(String(t).replace(/[^0-9.]/g, ""));
const llamadasTotales = (num(C.llamadas_evitadas_anio_base) + num(C.hogar_llamadas_evitadas_anio_base)).toLocaleString("en-US");

const THEME = {
  name: "AI Shark Tank - Tigo Predice", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: "0B1F5C", lt1: "FFFFFF", dk2: "0A22B8", lt2: "EEF3FD", accent1: "0A22B8", accent2: "4CC9F0",
    accent3: "FFC629", accent4: "1E5BBF", accent5: "F25C54", accent6: "2BB673", hlink: "1E5BBF", folHlink: "6A3FB5" },
};
const H = { navy: "0B1F5C", azul: "0A22B8", celeste: "4CC9F0", amarillo: "FFC629", rojo: "F25C54", verde: "2BB673",
  gris: "5B6575", suave: "C9D5FB", pie: "9FB2F0" };
const EMOJI = "Segoe UI Emoji";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 × 7.5 in
pres.title = "Tigo Predice — AI Shark Tank · Tigo CX Month";
pres.author = "Tigo Predice";
pres.theme = { headFontFace: "Calibri", bodyFontFace: "Calibri" };
const S = pres.SchemeColor;
const fondo = { path: FONDO };

pres.defineSlideMaster({
  title: "PORTADA", background: fondo,
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.35, w: 11.7, h: 1.3, fontSize: 66, bold: true, color: S.background1, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.7, w: 11.7, h: 0.8, fontSize: 28, color: H.celeste, valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "SECCION", background: fondo, margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "seccion", type: "body", x: 0.6, y: 0.35, w: 3.6, h: 0.72, fontSize: 24, bold: true, color: H.navy, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: "AI Shark Tank · Tigo CX Month", options: { x: 8.33, y: 0.46, w: 4.4, h: 0.5, fontSize: 15, bold: true, color: "FFFFFF", align: "right", valign: "middle", margin: 0 } } },
    { placeholder: { options: { name: "pregunta", type: "body", x: 0.6, y: 1.25, w: 12.1, h: 0.4, fontSize: 17, bold: true, color: H.celeste, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.65, w: 12.1, h: 0.85, fontSize: 30, bold: true, color: S.background1, valign: "top", align: "left", margin: 0 }, text: "" } },
    { text: { text: "Tigo Predice · Clientes: Millicom 20-F 2025 · Costos y efectos: supuestos a validar con Tigo", options: { x: 0.6, y: 7.02, w: 8, h: 0.3, fontSize: 10, color: H.pie, margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.02, w: 0.5, h: 0.3, fontSize: 10, color: H.pie, align: "right" },
});
pres.defineSlideMaster({
  title: "CIERRE", background: fondo,
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.6, w: 11.7, h: 2.4, fontSize: 48, bold: true, color: S.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.2, w: 11.7, h: 0.9, fontSize: 30, italic: true, color: H.celeste, valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});

const txt = (s, texto, o) => s.addText(texto, { isTextBox: true, fontSize: 16, color: S.text1, margin: 0, ...o });
const sombra = () => ({ type: "outer", color: "000A33", opacity: 0.25, blur: 8, offset: 3, angle: 90 });
function tarjeta(s, x, y, w, h, nombre, fill = "FFFFFF") {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.14, fill: { color: fill }, line: { color: fill }, shadow: sombra(), objectName: nombre });
}
function vidrio(s, x, y, w, h, nombre) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.14, fill: { color: "FFFFFF", transparency: 88 }, line: { color: "FFFFFF", transparency: 70, width: 1 }, objectName: nombre });
}
function circulo(s, x, y, d, texto, nombre, fill = H.celeste, color = H.navy) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: nombre });
  s.addText(texto, { isTextBox: true, x, y, w: d, h: d, align: "center", valign: "middle", fontSize: Math.round(d * 30), bold: true, color, margin: 0, objectName: nombre + "-t" });
}
function encabezado(s, seccion, pregunta, titulo) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: -0.5, y: 0.35, w: 4.8, h: 0.72, rectRadius: 0.36, fill: { color: "FFFFFF" }, line: { color: "FFFFFF" }, objectName: "pastilla" });
  s.addText(seccion, { placeholder: "seccion" });
  s.addText(pregunta, { placeholder: "pregunta" });
  s.addText(nb(titulo), { placeholder: "title" });
}
const ejes = { catAxisLabelColor: "334155", catAxisLabelFontSize: 13, catAxisLabelFontFace: "+mn-lt", valAxisLabelColor: "5B6575",
  valAxisLabelFontSize: 11, valAxisLabelFontFace: "+mn-lt", valGridLine: { color: "E8EDF4", size: 1 }, catGridLine: { style: "none" },
  dataLabelFontSize: 13, dataLabelColor: "0B1F5C", dataLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt", titleColor: "0B1F5C", titleFontSize: 15 };

// ───────────── 1 · Portada
pres.addSection({ title: "Apertura" });
let s = pres.addSlide({ masterName: "PORTADA", sectionTitle: "Apertura" });
txt(s, "AI SHARK TANK · TIGO CX MONTH 2026", { x: 0.8, y: 1.55, w: 9, h: 0.45, fontSize: 18, bold: true, color: H.celeste, charSpacing: 3, objectName: "evento" });
s.addText("Tigo Predice", { placeholder: "title" });
s.addText("La IA que resuelve la falla antes de que el cliente llame", { placeholder: "body" });
txt(s, [
  { text: "Categoría: ", options: { bold: true, color: "FFFFFF" } },
  { text: "📞 ", options: { fontFace: EMOJI } }, { text: "Experiencia del cliente / CX   ·   " },
  { text: "📡 ", options: { fontFace: EMOJI } }, { text: "Red y operaciones   ·   " },
  { text: "💰 ", options: { fontFace: EMOJI } }, { text: "Eficiencia / reducción de costos" },
], { x: 0.8, y: 4.75, w: 11.7, h: 0.45, fontSize: 18, color: H.suave, objectName: "categoria" });
txt(s, [
  { text: "Integrantes: ", options: { bold: true, color: "FFFFFF" } },
  { text: "[Nombre 1] · [Nombre 2] · [Nombre 3]", options: { color: H.amarillo } },
], { x: 0.8, y: 5.35, w: 11.7, h: 0.45, fontSize: 18, color: H.suave, objectName: "integrantes" });
s.addNotes("Saludo breve y una sola frase: 'En los próximos minutos les muestro cómo evitar la llamada y la visita del técnico antes de que el cliente note la falla.' (Completar los nombres del equipo antes de enviar.)");

// ───────────── 2 · Categoría y apuesta
s = pres.addSlide({ masterName: "SECCION", sectionTitle: "Apertura" });
encabezado(s, "Nuestra apuesta", "Categoría de impacto", "Experiencia del cliente, con ahorro medible en red y operaciones");
const CATS = [["📞", "Experiencia del cliente / CX", "principal"], ["🤖", "Self-service y canales digitales"], ["🛍️", "Ventas y comercial"],
  ["📡", "Red y operaciones", "si"], ["💰", "Eficiencia / reducción de costos", "si"], ["🧑‍💼", "Experiencia del colaborador"],
  ["📊", "Analítica y toma de decisiones"], ["🔐", "Prevención de fraude"], ["💡", "Nuevos productos o ingresos"]];
CATS.forEach(([e, t, sel], i) => {
  const x = 0.6 + (i % 3) * 2.55, y = 2.75 + Math.floor(i / 3) * 1.33, w = 2.4, h = 1.18;
  if (sel) tarjeta(s, x, y, w, h, `cat${i}`); else vidrio(s, x, y, w, h, `cat${i}`);
  txt(s, e, { x: x + 0.18, y: y + 0.14, w: 0.6, h: 0.5, fontSize: 24, fontFace: EMOJI, objectName: `cate${i}`, transparency: sel ? 0 : 45 });
  txt(s, t, { x: x + 0.18, y: y + 0.6, w: w - 0.3, h: 0.5, fontSize: 14, bold: !!sel, color: sel ? H.navy : "A9B8EE", valign: "top", objectName: `catt${i}` });
  if (sel === "principal") txt(s, "PRINCIPAL", { x: x + 1.2, y: y + 0.17, w: 1.05, h: 0.3, fontSize: 10, bold: true, color: H.azul, align: "right", charSpacing: 1, objectName: "principal" });
});
tarjeta(s, 8.45, 2.75, 4.28, 3.84, "apuesta", H.navy);
txt(s, [
  { text: "En una frase", options: { fontSize: 16, bold: true, color: H.celeste, breakLine: true } },
  { text: "Los chatbots y copilotos atienden la llamada.", options: { fontSize: 24, bold: true, color: "FFFFFF", breakLine: true } },
  { text: "Tigo Predice evita que ocurra.", options: { fontSize: 24, bold: true, color: H.amarillo, breakLine: true } },
  { text: "Detecta la falla en el módem días antes, la corrige a distancia y avisa al cliente por WhatsApp.", options: { fontSize: 15, color: H.suave } },
], { x: 8.8, y: 3.0, w: 3.6, h: 3.4, valign: "top", paraSpaceAfter: 10, objectName: "apuesta-t" });
s.addNotes("Elegimos Experiencia del cliente como categoría principal, porque el objetivo es que el cliente no sufra la falla. Pero el beneficio se mide en red y operaciones y en eficiencia: menos visitas técnicas y menos llamadas.");

// ───────────── 3 · Problema
pres.addSection({ title: "Problema" });
s = pres.addSlide({ masterName: "SECCION", sectionTitle: "Problema" });
encabezado(s, "Problema", "¿Qué queremos solucionar?", "Llegamos tarde: el módem avisa y esperamos la llamada");
const PASOS = [
  ["El módem se degrada", "Baja la señal, se satura el WiFi, se reinicia solo. El cliente aún no nota nada."],
  ["El cliente llama", "Ya sin servicio, llama al call center, espera y le agendan un técnico."],
  ["Recién alarma la regla", "La alarma por umbral se activa cuando el problema ya es evidente."],
  ["El técnico no encuentra nada físico", "Cambia el canal del WiFi o actualiza el firmware… y se va."],
];
s.addShape(pres.shapes.LINE, { x: 0.95, y: 3.1, w: 3 * 3.06, h: 0, line: { color: H.suave, width: 2, dashType: "dash" }, objectName: "linea" });
PASOS.forEach(([t, d], i) => {
  const x = 0.6 + i * 3.06;
  circulo(s, x, 2.75, 0.7, String(i + 1), `paso${i}`, i === 3 ? H.rojo : H.celeste, i === 3 ? "FFFFFF" : H.navy);
  txt(s, [{ text: t, options: { bold: true, fontSize: 17, color: "FFFFFF", breakLine: true } }, { text: d, options: { fontSize: 14, color: H.suave } }],
    { x, y: 3.6, w: 2.85, h: 1.4, valign: "top", paraSpaceAfter: 4, objectName: `pasot${i}` });
});
[[nb(C.hogar_visitas_mes), `visitas técnicas al mes en ${nb(C.hogares_nacional)} hogares (estimado)`], ["1 de cada 4", nb("visitas se podían evitar (la industria: 17–20 % «sin falla»)")],
  [nb(C.costo_por_visita), "por visita, más 2 llamadas al call center antes de agendarla"]].forEach(([v, e], i) => {
  const x = 0.6 + i * 4.08;
  tarjeta(s, x, 5.2, 3.97, 1.55, `dato${i}`);
  txt(s, v, { x: x + 0.3, y: 5.32, w: 3.4, h: 0.7, fontSize: 34, bold: true, color: i === 1 ? H.rojo : H.azul, objectName: `datov${i}` });
  txt(s, e, { x: x + 0.3, y: 6.02, w: 3.4, h: 0.6, fontSize: 14, color: H.gris, valign: "top", objectName: `datoe${i}` });
});
s.addNotes("Contar la historia: un hogar empieza a tener problemas de WiFi. El módem lo reporta, pero nadie lo mira hasta que cruza un umbral. El cliente llama, esperamos, mandamos un técnico, y en 1 de cada 4 visitas no hay nada físico que arreglar. Tigo tiene 191 mil hogares, según el 20-F 2025 de Millicom. Decir con naturalidad que las cifras son supuestos a validar con Tigo.");

// ───────────── 4 · Usuario
pres.addSection({ title: "Usuario" });
s = pres.addSlide({ masterName: "SECCION", sectionTitle: "Usuario" });
encabezado(s, "Usuario", "¿A quién le afecta?", "Afecta al cliente, a quienes lo atienden y al negocio");
[["🏠", "Cliente de Internet Hogar", `Pierde el servicio, llama, espera y debe quedarse en casa para el técnico. ${nb(C.hogares_nacional)} hogares de Tigo (Millicom, 2025).`],
  ["📱", "Cliente móvil en una falla masiva", "5.0 M de clientes. En una falla masiva no sabe qué pasa: sin aviso, 1 de cada 3 afectados llama."],
  ["🎧", "Agentes del call center", "Atienden llamadas repetidas sobre fallas que la red ya conocía y no pueden resolver."],
  ["🛠️", "Técnicos de campo", "1 de cada 4 visitas es a un hogar sin falla física: tiempo que no llega a quien sí lo necesita."]].forEach(([e, t, d], i) => {
  const x = 0.6 + i * 3.06;
  tarjeta(s, x, 2.75, 2.95, 3.0, `u${i}`);
  txt(s, e, { x: x + 0.25, y: 2.92, w: 0.8, h: 0.65, fontSize: 32, fontFace: EMOJI, objectName: `ue${i}` });
  txt(s, [{ text: t, options: { bold: true, fontSize: 18, color: H.navy, breakLine: true } }, { text: d, options: { fontSize: 14, color: "334155" } }],
    { x: x + 0.25, y: 3.65, w: 2.5, h: 2.0, valign: "top", paraSpaceAfter: 6, objectName: `ut${i}` });
});
vidrio(s, 0.6, 5.95, 12.13, 0.8, "negocio");
txt(s, [{ text: "Y para Tigo: ", options: { bold: true, color: H.amarillo } },
  { text: nb(`${C.costo_por_visita} por visita, ${C.costo_por_llamada} por llamada y un cliente que recuerda que tuvo que llamar (NPS).`), options: { color: "FFFFFF" } }],
  { x: 0.9, y: 5.95, w: 11.6, h: 0.8, fontSize: 17, valign: "middle", objectName: "negocio-t" });
s.addNotes("Cuatro usuarios con el mismo dolor. El cliente es el centro, pero también ganan los agentes y los técnicos, que dejan de atender problemas que se podían prevenir.");

// ───────────── 5 · Idea con IA
pres.addSection({ title: "Idea con IA" });
s = pres.addSlide({ masterName: "SECCION", sectionTitle: "Idea con IA" });
encabezado(s, "Nuestra idea con IA", "¿Cómo solucionamos el problema?", "La IA detecta, explica y resuelve antes de que el cliente llame");
[["Detecta", "Cada semana la IA lee la telemetría de todos los módems y marca al 2 % con más riesgo de fallar en 7 días."],
  ["Explica", "Dice por qué, en palabras simples: «el WiFi empeora día a día», «firmware con fallas conocidas»."],
  ["Resuelve", "Si es WiFi o firmware, se corrige a distancia y llega un WhatsApp. Si es físico, el técnico va una vez y con diagnóstico."],
  ["Mide", "Un 15 % de control al azar no recibe la acción: así se prueba el efecto real, no se supone."]].forEach(([t, d], i) => {
  const x = 0.6 + i * 3.06;
  tarjeta(s, x, 2.75, 2.95, 2.9, `idea${i}`);
  circulo(s, x + 0.25, 2.98, 0.62, String(i + 1), `idean${i}`, i === 2 ? H.amarillo : H.celeste);
  txt(s, t, { x: x + 1.0, y: 2.98, w: 1.8, h: 0.62, fontSize: 24, bold: true, color: H.navy, valign: "middle", objectName: `ideat${i}` });
  txt(s, d, { x: x + 0.25, y: 3.75, w: 2.5, h: 1.8, fontSize: 14, color: "334155", valign: "top", objectName: `idead${i}` });
});
vidrio(s, 0.6, 5.85, 5.95, 0.9, "movil");
txt(s, [{ text: "El mismo motor en Móvil: ", options: { bold: true, color: H.amarillo } }, { text: "cuando cae un sitio, aviso por WhatsApp antes de que llamen.", options: { color: "FFFFFF" } }],
  { x: 0.85, y: 5.85, w: 5.5, h: 0.9, fontSize: 15, valign: "middle", objectName: "movil-t" });
vidrio(s, 6.78, 5.85, 5.95, 0.9, "tecno");
txt(s, [{ text: "IA: ", options: { bold: true, color: H.amarillo } }, { text: "modelo predictivo calibrado, explicación por variable y Claude redacta los mensajes con controles.", options: { color: "FFFFFF" } }],
  { x: 7.03, y: 5.85, w: 5.5, h: 0.9, fontSize: 15, valign: "middle", objectName: "tecno-t" });
s.addNotes("Cuatro verbos: detecta, explica, resuelve y mide. La IA no reemplaza a nadie: le da a soporte una lista de trabajo diaria con el porqué de cada hogar. Las acciones remotas las ejecuta el sistema de gestión de módems (ACS), nunca la IA generativa.");

// ───────────── 6 · Demo
s = pres.addSlide({ masterName: "SECCION", sectionTitle: "Idea con IA" });
encabezado(s, "Nuestra idea con IA", "Así se ve en el prototipo", "Un hogar del modelo: la IA lo marca 4 días antes de la llamada");
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 2.6, w: 7.5, h: 4.22, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: "FFFFFF" }, shadow: sombra(), objectName: "marco" });
s.addImage({ path: path.join(CAPT, "hogar.png"), x: 0.6, y: 2.65, w: 7.4, h: 4.12, sizing: { type: "cover", w: 7.4, h: 4.12 }, objectName: "captura", altText: "Pantalla Hogar en vivo del prototipo Tigo Predice" });
[["28/09: la IA lo marca", "entra al 2 % de mayor riesgo"],
  ["Explica el porqué", "el WiFi empeora día a día"],
  ["Se corrige a distancia", "y llega un WhatsApp al cliente"],
  ["02/10: habría llamado", "la regla alarmaba recién el 03/10"],
  [nb("Visita evitada"), nb("L 780 de ahorro por L 0.31")]].forEach(([t, d], i) => {
  const y = 2.62 + i * 0.84;
  circulo(s, 8.4, y + 0.05, 0.48, String(i + 1), `d${i}`, i === 4 ? H.amarillo : H.celeste);
  txt(s, [{ text: t, options: { bold: true, color: "FFFFFF", breakLine: true } }, { text: d, options: { fontSize: 14, color: H.suave } }],
    { x: 9.05, y, w: 3.7, h: 0.78, fontSize: 16, valign: "top", objectName: `dt${i}` });
});
s.addNotes("Si hay pantalla, mostrar la demo 'Hogar en vivo' (77 segundos) o el video de respaldo. El riesgo diario y la explicación los calcula el modelo real sobre datos simulados.");

// ───────────── 7 · Por qué IA
s = pres.addSlide({ masterName: "SECCION", sectionTitle: "Idea con IA" });
encabezado(s, "Nuestra idea con IA", "¿Por qué IA y no una regla?", "En la simulación, anticipa el doble que las alarmas de hoy");
tarjeta(s, 0.6, 2.7, 7.0, 4.05, "graf-fondo");
const cv = D.captura_visitas_evitables;
s.addChart(pres.charts.BAR, [{ name: "% de visitas evitables anticipadas", labels: Object.keys(cv), values: Object.values(cv) }], {
  x: 0.75, y: 2.8, w: 6.7, h: 3.85, barDir: "bar", chartColors: [H.azul], showTitle: true,
  title: "% de visitas evitables anticipadas (simulado)", showValue: true, dataLabelPosition: "outEnd",
  dataLabelFormatCode: "0\" %\"", showLegend: false, valAxisMaxVal: 100, valAxisMinVal: 0, ...ejes, objectName: "graf-modelo" });
[[`${C.hogar_ia_vs_regla} lo que ve la regla`, nb(`La IA anticipa ${C.hogar_ia_captura} de las visitas evitables; la alarma por umbral, ${C.hogar_regla_captura}.`)],
  [nb(`${C.hogar_deteccion_temprana} sin ninguna alarma`), "La IA ve tendencias: la señal que baja, el WiFi que empeora. La regla ve cuando ya es tarde."],
  ["Hipótesis, no promesa", "Se valida con 3 meses de telemetría real en las semanas 0–2. Si no supera a la regla por 1.3×, se usa la regla."]].forEach(([t, d], i) => {
  const y = 2.7 + i * 1.38;
  vidrio(s, 7.9, y, 4.83, 1.25, `pq${i}`);
  txt(s, [{ text: t, options: { bold: true, fontSize: 19, color: i === 0 ? H.amarillo : "FFFFFF", breakLine: true } }, { text: d, options: { fontSize: 14, color: H.suave } }],
    { x: 8.15, y: y + 0.12, w: 4.4, h: 1.05, valign: "top", paraSpaceAfter: 2, objectName: `pqt${i}` });
});
s.addNotes("No medimos la IA contra nada: la medimos contra lo que Tigo ya tiene, la alarma por umbral. En datos simulados, con el mismo presupuesto, anticipa el doble. Decirlo claro: es una hipótesis que validamos con datos reales en dos semanas. Y si con datos reales no gana, usamos la regla: el piloto igual sirve.");

// ───────────── 8 · Impacto
pres.addSection({ title: "Impacto" });
s = pres.addSlide({ masterName: "SECCION", sectionTitle: "Impacto" });
encabezado(s, "Impacto esperado", "¿Qué beneficio se obtiene?", `${C.neto_anio1_base} netos el año 1, con costos reales de Honduras`);
[[nb(C.neto_anio1_base), "netos en el año 1 (escenario base, ya descontada la inversión)", H.amarillo, H.navy],
  [C.hogar_visitas_evitadas_anio_base, "visitas técnicas evitadas al año", "FFFFFF", H.azul],
  [llamadasTotales, "llamadas menos al call center al año (Hogar + Móvil)", "FFFFFF", H.azul],
  [nb(C.equilibrio_anio1), `menos llamadas y Móvil se paga en el año 1 (Hogar: ${C.hogar_equilibrio_anio1})`, "FFFFFF", H.azul]].forEach(([v, e, fill, col], i) => {
  const x = 0.6 + i * 3.06;
  tarjeta(s, x, 2.7, 2.95, 1.85, `imp${i}`, fill);
  txt(s, v, { x: x + 0.25, y: 2.82, w: 2.6, h: 0.8, fontSize: 40, bold: true, color: col, objectName: `impv${i}` });
  txt(s, e, { x: x + 0.25, y: 3.62, w: 2.55, h: 0.85, fontSize: 14, color: i === 0 ? H.navy : H.gris, valign: "top", objectName: `impe${i}` });
});
[["Para el cliente", "No pierde el servicio, no llama y no espera al técnico. Recibe un WhatsApp: «ya lo corregimos»."],
  ["Para agentes y técnicos", "Menos llamadas repetidas. Las visitas que sí van, van una sola vez y con el diagnóstico."],
  ["Para Tigo", nb(`Menos costo y mejor NPS. La retención (${C.potencial_retencion_base} al año) ni siquiera entra en el caso.`)]].forEach(([t, d], i) => {
  const x = 0.6 + i * 4.08;
  vidrio(s, x, 4.8, 3.97, 1.95, `ben${i}`);
  txt(s, [{ text: t, options: { bold: true, fontSize: 18, color: H.celeste, breakLine: true } }, { text: d, options: { fontSize: 15, color: "FFFFFF" } }],
    { x: x + 0.25, y: 4.95, w: 3.45, h: 1.7, valign: "top", paraSpaceAfter: 6, objectName: `bent${i}` });
});
s.addNotes(`Solo contamos beneficio duro: visitas y llamadas evitadas por su costo. ${C.neto_anio1_base} netos en el año 1 en el escenario base. Usamos la base real de Tigo Honduras y costos hondureños: visita ${C.costo_por_visita}, llamada ${C.costo_por_llamada}. Móvil se paga con ${C.equilibrio_anio1} menos llamadas y Hogar con ${C.hogar_equilibrio_anio1} menos visitas evitables. La retención y el NPS son upside, no están en el número.`);

// ───────────── 9 · Escenarios y medición
s = pres.addSlide({ masterName: "SECCION", sectionTitle: "Impacto" });
encabezado(s, "Impacto esperado", "¿Y si los supuestos fallan?", "Si todo sale mal se pierden L 3 M: por eso, primero un piloto");
tarjeta(s, 0.6, 2.7, 6.9, 4.05, "esc-fondo");
const esc = ["Conservador", "Base", "Optimista"];
const kk = ["conservador", "base", "optimista"];
s.addChart(pres.charts.BAR, [
  { name: "Hogar", labels: esc, values: kk.map((x) => D.neto_frente_millones[x]["Hogar"]) },
  { name: "Móvil", labels: esc, values: kk.map((x) => D.neto_frente_millones[x]["Móvil"]) },
], { x: 0.75, y: 2.8, w: 6.6, h: 3.85, barDir: "col", barGapWidthPct: 60, chartColors: [H.azul, H.celeste], showTitle: true,
  title: "Neto año 1 por frente (millones de L, con inversión)", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0",
  showLegend: true, legendPos: "b", legendFontSize: 13, legendFontFace: "+mn-lt", legendColor: "334155", ...ejes, objectName: "grafico" });
vidrio(s, 7.8, 2.7, 4.93, 4.05, "piloto");
txt(s, "Piloto Hogar simulado: tratados vs. control", { x: 8.05, y: 2.85, w: 4.5, h: 0.4, fontSize: 16, bold: true, color: H.celeste, objectName: "pil-t" });
txt(s, [{ text: String(PH.control_por_1000), options: { fontSize: 44, bold: true, color: H.rojo, breakLine: true } }, { text: "visitas por 1,000 hogares marcados sin acción", options: { fontSize: 13, color: H.suave } }],
  { x: 8.05, y: 3.3, w: 2.2, h: 1.5, valign: "top", objectName: "pil-c" });
txt(s, [{ text: String(PH.tratamiento_por_1000), options: { fontSize: 44, bold: true, color: H.verde, breakLine: true } }, { text: "con atención proactiva", options: { fontSize: 13, color: H.suave } }],
  { x: 10.4, y: 3.3, w: 2.2, h: 1.5, valign: "top", objectName: "pil-t2" });
txt(s, [{ text: nb(`−${PH.reduccion} visitas`), options: { fontSize: 26, bold: true, color: "FFFFFF", breakLine: true } },
  { text: nb(`IC 95 %: ${PH.ic} · llamadas técnicas −${PH.reduccion_llamadas}`), options: { fontSize: 14, color: H.suave, breakLine: true } },
  { text: "Simulado: muestra cómo se medirá, no promete un número.", options: { fontSize: 13, italic: true, color: H.pie } }],
  { x: 8.05, y: 4.7, w: 4.5, h: 1.8, valign: "top", paraSpaceAfter: 4, objectName: "pil-r" });
s.addNotes(`Rango completo: ${C.neto_anio1_rango}. Si todos los supuestos salen mal a la vez, escalar perdería hasta L 3 M. Por eso no pedimos escalar: pedimos un piloto de L 770 mil que lo averigua. El piloto se mide contra un grupo control, con intervalo de confianza: así la decisión se toma con datos de Tigo, no con nuestra simulación.`);

// ───────────── 10 · Cómo se hace realidad
pres.addSection({ title: "Pedido" });
s = pres.addSlide({ masterName: "SECCION", sectionTitle: "Pedido" });
encabezado(s, "Plan", "¿Cómo lo hacemos realidad?", "Piloto de 12 semanas en San Pedro Sula, con GO / NO-GO medible");
[["Semanas 0–2", "Preparación", "Datos del ACS, NOC, CRM, call center y campo por archivo diario. Prueba retrospectiva IA vs. regla."],
  ["Semanas 3–10", "Piloto en vivo", "La IA marca el 2 % semanal y soporte corrige a distancia. Avisos en fallas masivas. 15 % de control."],
  ["Semanas 11–12", "Decisión", "Efecto con intervalo de confianza, costo real por visita y llamada evitada, y GO / NO-GO por frente."]].forEach(([w, f, d], i) => {
  const x = 0.6 + i * 4.08;
  circulo(s, x, 2.72, 0.66, String(i + 1), `f${i}`);
  txt(s, [{ text: w, options: { fontSize: 13, color: H.suave, breakLine: true } }, { text: f, options: { bold: true, fontSize: 20, color: "FFFFFF" } }], { x: x + 0.82, y: 2.68, w: 3.0, h: 0.75, objectName: `ft${i}` });
  txt(s, d, { x, y: 3.55, w: 3.8, h: 1.1, fontSize: 14, color: H.suave, valign: "top", objectName: `fd${i}` });
});
tarjeta(s, 0.6, 4.85, 5.95, 1.9, "go");
txt(s, [{ text: "GO si…", options: { bold: true, color: H.verde, fontSize: 19, breakLine: true } },
  { text: nb("las visitas bajan 15 % o más (llamadas 12 % en Móvil), con significancia"), options: { bullet: { indent: 16 }, breakLine: true } },
  { text: nb("menos de 2 % de clientes pide no recibir mensajes"), options: { bullet: { indent: 16 }, breakLine: true } },
  { text: "la IA supera a la regla por 1.3× (si no, se usa la regla)", options: { bullet: { indent: 16 } } }],
  { x: 0.85, y: 4.97, w: 5.5, h: 1.7, fontSize: 14, color: "334155", valign: "top", paraSpaceAfter: 2, objectName: "go-t" });
tarjeta(s, 6.78, 4.85, 5.95, 1.9, "seg", H.navy);
txt(s, [{ text: "Privacidad y seguridad desde el día 1", options: { bold: true, color: H.celeste, fontSize: 19, breakLine: true } },
  { text: "Solo datos técnicos del módem y la línea: nunca contenido ni navegación", options: { bullet: { indent: 16 }, breakLine: true } },
  { text: "GDPR como estándar, ISO 27001/27701/42001 y OWASP", options: { bullet: { indent: 16 }, breakLine: true } },
  { text: "Red team propio: 12 ataques probados y corregidos", options: { bullet: { indent: 16 } } }],
  { x: 7.03, y: 4.97, w: 5.5, h: 1.7, fontSize: 14, color: "FFFFFF", valign: "top", paraSpaceAfter: 2, objectName: "seg-t" });
s.addNotes("El riesgo está acotado: 12 semanas, una ciudad y criterios de éxito definidos antes de empezar. Si no funciona, se detiene. Honduras aún no tiene una ley integral de datos personales, así que usamos GDPR como vara.");

// ───────────── 11 · Pedido
s = pres.addSlide({ masterName: "SECCION", sectionTitle: "Pedido" });
encabezado(s, "El pedido", "¿Qué necesitamos de los Sharks?", "Una inversión acotada para decidir con datos reales de Tigo");
[["Datos", "Archivos diarios del ACS, NOC, CRM, call center y órdenes de campo de San Pedro Sula"],
  ["Equipo", "Un patrocinador, enlaces de NOC e ingeniería de acceso, soporte N2 y un analista al 50 %"],
  ["Canal y cumplimiento", "Plantillas de WhatsApp Business y visto bueno de Legal y Seguridad"],
  ["Decisión", "En la semana 12, con números reales, ustedes deciden GO o NO-GO por frente"]].forEach(([t, d], i) => {
  const y = 2.72 + i * 1.02;
  circulo(s, 0.6, y, 0.62, String(i + 1), `k${i}`);
  txt(s, [{ text: t, options: { bold: true, fontSize: 19, color: "FFFFFF", breakLine: true } }, { text: d, options: { fontSize: 14, color: H.suave } }],
    { x: 1.45, y: y - 0.05, w: 6.3, h: 0.92, valign: "top", objectName: `kt${i}` });
});
tarjeta(s, 8.15, 2.7, 4.58, 4.05, "inv", H.amarillo);
txt(s, "Inversión del piloto", { x: 8.5, y: 2.95, w: 3.9, h: 0.45, fontSize: 19, bold: true, color: H.navy, objectName: "inv-t" });
txt(s, nb(C.piloto_costo_base), { x: 8.5, y: 3.4, w: 3.9, h: 1.0, fontSize: 54, bold: true, color: H.navy, objectName: "inv-v" });
txt(s, nb(`≈ ${C.piloto_costo_usd} · 12 semanas · 2 frentes`), { x: 8.5, y: 4.4, w: 3.9, h: 0.45, fontSize: 16, bold: true, color: H.navy, objectName: "inv-r" });
txt(s, nb(`Si es GO, el escenario base deja ${C.neto_anio1_base} netos en el año 1 a nivel nacional.`), { x: 8.5, y: 5.05, w: 3.9, h: 1.4, fontSize: 15, color: H.navy, valign: "top", objectName: "inv-n" });
s.addNotes(`Pedir con claridad: ${C.piloto_costo_base}, 12 semanas, datos y un equipo pequeño. Ustedes deciden en la semana 12 con datos reales.`);

// ───────────── 12 · Cierre
s = pres.addSlide({ masterName: "CIERRE", sectionTitle: "Pedido" });
s.addText([{ text: "Los chatbots atienden la llamada.", options: { breakLine: true } }, { text: "Tigo Predice evita que ocurra" }], { placeholder: "title" });
s.addText("…y evita la visita.", { placeholder: "body" });
txt(s, [{ text: "Tigo Predice · ", options: { bold: true, color: "FFFFFF" } }, { text: "[Nombre 1] · [Nombre 2] · [Nombre 3]", options: { color: H.amarillo } }],
  { x: 0.8, y: 6.2, w: 11.7, h: 0.45, fontSize: 18, objectName: "contacto" });
s.addNotes("Pausa. Bajar el ritmo para la frase final. Luego: 'Gracias. ¿Preguntas?' (El documento de preguntas frecuentes del jurado tiene las respuestas preparadas.)");

pres.writeFile({ fileName: SALIDA }).then(async () => { await applyTheme(SALIDA, THEME); console.log("OK", SALIDA); });
