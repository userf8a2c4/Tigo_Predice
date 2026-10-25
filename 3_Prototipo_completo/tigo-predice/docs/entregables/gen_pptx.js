// Presentación v03 (Hogar + Móvil). Uso: node gen_pptx.js <salida.pptx> <docs/capturas> <datos_deck.json>
// Requiere NODE_PATH con pptxgenjs y APPLY_THEME: ruta a un módulo que escribe los colores de THEME en el tema del .pptx.
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.APPLY_THEME);

const [SALIDA, CAPT, DATOS] = process.argv.slice(2);
const D = JSON.parse(fs.readFileSync(DATOS, "utf8"));
const C = D.cifras;
const PH = D.piloto_hogar;
// Espacios no separables: que una cifra como "L 15 M" nunca se parta entre dos líneas
const nb = (t) => t.replace(/(L) /g, "$1 ").replace(/ (M|mil|%)\b/g, " $1").replace(/ %/g, " %");

const THEME = {
  name: "Tigo Predice", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: "0F1B2D", lt1: "FFFFFF", dk2: "00377B", lt2: "EEF3F9", accent1: "00377B", accent2: "00A3CC",
    accent3: "B0479B", accent4: "1E5BBF", accent5: "F2A20C", accent6: "16A35A", hlink: "1E5BBF", folHlink: "B0479B" },
};
const HEX = { navy: "00377B", celeste: "00C8FF", gris: "5B6575", rojo: "E0303A", verde: "16A35A" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Tigo Predice v03 — Tigo CX Month";
pres.author = "Sandra Michel Jimenez Zelaya";
pres.theme = { headFontFace: "Calibri", bodyFontFace: "Calibri" };
const S = pres.SchemeColor;

pres.defineSlideMaster({
  title: "PORTADA", background: { color: HEX.navy },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.9, w: 11.7, h: 1.4, fontSize: 60, bold: true, color: S.background1, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.4, w: 11.7, h: 1.3, fontSize: 28, italic: true, color: "00C8FF", valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CIERRE", background: { color: HEX.navy },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.3, w: 11.7, h: 2.7, fontSize: 46, bold: true, color: S.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.3, w: 11.7, h: 1.0, fontSize: 24, italic: true, color: "00C8FF", valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENIDO", background: { color: "FFFFFF" }, margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.9, fontSize: 32, bold: true, color: S.text2, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: "Tigo Predice · Datos simulados — supuestos a validar con Tigo", options: { x: 0.6, y: 7.0, w: 8, h: 0.3, fontSize: 10, color: HEX.gris, margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: HEX.gris, align: "right" },
});

const sombra = () => ({ type: "outer", color: "0F1B2D", opacity: 0.12, blur: 6, offset: 2, angle: 90 });
const txt = (s, texto, o) => s.addText(texto, { isTextBox: true, fontSize: 16, color: S.text1, ...o });
function tarjeta(s, x, y, w, h, nombre, fill = S.background2) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill }, shadow: sombra(), objectName: nombre });
}
function circulo(s, x, y, d, texto, nombre, fill = HEX.celeste, color = HEX.navy) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: nombre });
  s.addText(texto, { isTextBox: true, x, y, w: d, h: d, align: "center", valign: "middle", fontSize: d * 26, bold: true, color, margin: 0, objectName: nombre + "-t" });
}
function cifra(s, x, y, w, valor, etiqueta, nombre, color = S.text2, tam = 44) {
  txt(s, valor, { x, y, w, h: 0.85, fontSize: tam, bold: true, color, margin: 0, objectName: nombre });
  txt(s, etiqueta, { x, y: y + 0.85, w, h: 0.7, fontSize: 14, color: HEX.gris, margin: 0, valign: "top", objectName: nombre + "-e" });
}
function tarjetas(s, filas, x, y0, w, h, paso, prefijo, tam = 17) {
  filas.forEach(([t1, d], i) => {
    tarjeta(s, x, y0 + i * paso, w, h, `${prefijo}${i}`);
    txt(s, [{ text: t1, options: { bold: true, color: S.text2, breakLine: true } }, { text: d, options: { fontSize: 14 } }],
      { x: x + 0.25, y: y0 + 0.1 + i * paso, w: w - 0.5, h: h - 0.2, fontSize: tam, margin: 0, valign: "top", objectName: `${prefijo}t${i}` });
  });
}
const ejes = { catAxisLabelColor: "334155", catAxisLabelFontSize: 13, catAxisLabelFontFace: "+mn-lt", valAxisLabelColor: "5B6575",
  valAxisLabelFontSize: 11, valAxisLabelFontFace: "+mn-lt", valGridLine: { color: "E8EDF4", size: 1 }, catGridLine: { style: "none" },
  dataLabelFontSize: 12, dataLabelColor: "334155", dataLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt", titleColor: "0F1B2D", titleFontSize: 15 };

// 1 Portada
pres.addSection({ title: "Apertura" });
let s = pres.addSlide({ masterName: "PORTADA", sectionTitle: "Apertura" });
s.addText("Tigo Predice", { placeholder: "title" });
s.addText("Los chatbots y copilotos atienden la llamada. Tigo Predice evita que ocurra.", { placeholder: "body" });
txt(s, "TIGO CX MONTH · CONCURSO SHARKS DE IA", { x: 0.8, y: 1.2, w: 8, h: 0.4, fontSize: 14, bold: true, color: "00C8FF", charSpacing: 2, margin: 0, objectName: "evento" });
txt(s, "La IA que detecta el problema antes que el cliente, y lo resuelve antes de que llame o de que haya que mandar un técnico.", { x: 0.8, y: 4.75, w: 11.2, h: 0.8, fontSize: 18, color: "FFFFFF", margin: 0, objectName: "lema" });
txt(s, "Atención proactiva · Piloto Hogar + Móvil · San Pedro Sula · 60 días · grupo control", { x: 0.8, y: 5.65, w: 11, h: 0.4, fontSize: 15, color: "CADCFC", margin: 0, objectName: "sub" });
txt(s, "Presenta: Sandra Michel Jimenez Zelaya · Asistente de Experiencia B2B · Octubre 2026", { x: 0.8, y: 6.4, w: 9, h: 0.4, fontSize: 15, color: "CADCFC", margin: 0, objectName: "presenta" });
s.addNotes("Saludo. 'En 5 minutos les muestro cómo resolver problemas antes de que el cliente llame o de mandar un técnico.'");

// 2 Dolor
pres.addSection({ title: "Problema" });
s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Problema" });
s.addText("El módem avisa días antes: escuchémoslo a tiempo", { placeholder: "title" });
[["Día 1", "El WiFi de Karla empieza a empeorar. La telemetría del módem ya lo muestra."],
  ["Día 6", "Karla no aguanta más: llama, espera y le agendan un técnico."],
  ["Día 8", "El técnico va, no encuentra nada físico, cambia el canal del WiFi y se va."]].forEach(([h, d], i) => {
  const y = 1.6 + i * 1.25;
  circulo(s, 0.7, y, 0.65, String(i + 1), `p${i}`, i === 2 ? HEX.rojo : HEX.celeste, i === 2 ? "FFFFFF" : HEX.navy);
  txt(s, [{ text: h, options: { bold: true, color: S.text2, breakLine: true } }, { text: d }], { x: 1.6, y: y - 0.05, w: 5.5, h: 0.95, fontSize: 17, margin: 0, valign: "top", objectName: `pt${i}` });
});
tarjeta(s, 7.6, 1.55, 5.1, 4.5, "dato");
cifra(s, 7.95, 1.85, 4.5, "1 de cada 4", "visitas técnicas son evitables: WiFi, firmware o «sin falla encontrada» (supuesto a validar)", "c1", S.text2, 44);
cifra(s, 7.95, 3.75, 4.5, nb(`${C.costo_por_visita} + 2 llamadas`), `por visita (supuestos) · ${C.hogar_visitas_mes} visitas al mes en ${C.hogares_nacional} hogares`, "c2", S.accent2, 36);
txt(s, "Y en móvil: cuando cae un sitio, 1 de cada 3 afectados llama si no recibe aviso (benchmark público).", { x: 0.6, y: 5.6, w: 6.6, h: 0.6, fontSize: 14, italic: true, color: HEX.gris, margin: 0, objectName: "movil" });
s.addNotes("Contar la escena de Karla. Decir 'supuesto' sin miedo: es lo que da credibilidad.");

// 3 Por qué ahora
s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Problema" });
s.addText("Por qué ahora", { placeholder: "title" });
[["Los datos ya existen", "Los módems reportan señal, errores, reinicios y WiFi al ACS. Hoy solo se miran cuando cruzan un umbral."],
  ["La IA predictiva", "califica cada semana a todos los hogares y marca al 2 % que va a fallar, días antes y con su porqué."],
  ["Acción a distancia", "Firmware, canal WiFi y reinicio desde el ACS. Avisar por WhatsApp cuesta US$0.011."]].forEach(([v, d], i) => {
  const x = 0.6 + i * 4.15;
  tarjeta(s, x, 1.6, 3.85, 3.6, `w${i}`);
  txt(s, v, { x: x + 0.35, y: 1.95, w: 3.2, h: 0.9, fontSize: 28, bold: true, color: i === 1 ? S.accent2 : S.text2, margin: 0, objectName: `wv${i}` });
  txt(s, d, { x: x + 0.35, y: 2.95, w: 3.2, h: 2.0, fontSize: 16, margin: 0, valign: "top", objectName: `wd${i}` });
});
txt(s, "Los chatbots y copilotos atienden la llamada. Tigo Predice evita que ocurra.", { x: 0.6, y: 5.7, w: 12.1, h: 0.6, fontSize: 22, bold: true, italic: true, color: S.text2, margin: 0, objectName: "pos" });

// 4 Solución
pres.addSection({ title: "Solución" });
s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Solución" });
s.addText("Detecta, resuelve y mide contra un grupo control", { placeholder: "title" });
[["1", "Detecta", "Cada semana la IA califica la telemetría de todos los módems y marca al 2 % con más riesgo, con su explicación."],
  ["2", "Resuelve", "Si es WiFi o firmware, se corrige a distancia y llega un WhatsApp. Si es físico, el técnico va una sola vez y con el diagnóstico."],
  ["3", "Mide", "El 15 % de los hogares marcados, al azar, queda como control. Se comparan las visitas por 1,000 marcados."]].forEach(([n, t1, d], i) => {
  const x = 0.6 + i * 4.15;
  tarjeta(s, x, 1.6, 3.85, 4.2, `s${n}`);
  circulo(s, x + 0.35, 1.9, 0.8, n, `sn${n}`);
  txt(s, t1, { x: x + 0.35, y: 2.9, w: 3.2, h: 0.6, fontSize: 26, bold: true, color: S.text2, margin: 0, objectName: `st${n}` });
  txt(s, d, { x: x + 0.35, y: 3.55, w: 3.2, h: 2.1, fontSize: 16, margin: 0, valign: "top", objectName: `sd${n}` });
});
txt(s, "El mismo motor cubre Móvil: en fallas masivas, aviso por WhatsApp antes de que llamen.", { x: 0.6, y: 6.15, w: 12.1, h: 0.45, fontSize: 16, bold: true, color: S.accent2, margin: 0, objectName: "nota" });

// 5 Demo Hogar
pres.addSection({ title: "Demo" });
s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Demo" });
s.addText("Demo «Hogar en vivo»: 80 segundos", { placeholder: "title" });
s.addImage({ path: path.join(CAPT, "hogar.png"), x: 0.6, y: 1.4, w: 7.7, h: 4.33, objectName: "captura", altText: "Pantalla Hogar en vivo" });
["26/09: empieza el problema; Karla no nota nada", "28/09: la IA lo marca (top 2 %), la regla no ve nada", "Explica por qué: el WiFi empeora día a día", "Se corrige a distancia + WhatsApp", "02/10: sin Tigo Predice, Karla habría llamado", nb("Visita evitada: L 780 por L 0.31")].forEach((t1, i) => {
  circulo(s, 8.7, 1.5 + i * 0.8, 0.5, String(i + 1), `d${i}`);
  txt(s, t1, { x: 9.35, y: 1.45 + i * 0.8, w: 3.4, h: 0.6, fontSize: 14, valign: "middle", margin: 0, objectName: `dt${i}` });
});
txt(s, "El riesgo diario y la explicación los calcula el modelo real. Incluye la lista de trabajo de hoy para soporte.", { x: 0.6, y: 5.95, w: 7.7, h: 0.5, fontSize: 13, italic: true, color: HEX.gris, margin: 0, objectName: "pie" });
s.addNotes("Cambiar a la app: Hogar en vivo, caso A distancia, 1x, Iniciar. Respaldo: video o /hogar?final.");

// 6 IA vs regla
s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Demo" });
s.addText("La IA, medida contra la regla (no contra nada)", { placeholder: "title" });
const cv = D.captura_visitas_evitables;
s.addChart(pres.charts.BAR, [{ name: "% de visitas evitables anticipadas", labels: Object.keys(cv), values: Object.values(cv) }], {
  x: 0.6, y: 1.45, w: 6.6, h: 4.6, barDir: "bar", chartColors: ["1E5BBF"], showTitle: true,
  title: "% de visitas evitables anticipadas (mismo presupuesto: 2 % semanal)", showValue: true, dataLabelPosition: "outEnd",
  dataLabelFormatCode: "0\" %\"", showLegend: false, valAxisMaxVal: 100, valAxisMinVal: 0, ...ejes, objectName: "graf-modelo" });
tarjetas(s, [
  [`${C.hogar_ia_vs_regla} lo que ve la regla`, `La IA anticipa ${nb(C.hogar_ia_captura)} de las visitas evitables; la regla de umbrales, ${nb(C.hogar_regla_captura)}.`],
  [`${nb(C.hogar_deteccion_temprana)} sin ninguna alarma`, "La IA ve tendencias (señal que baja, WiFi que empeora); la regla ve cuando ya es tarde."],
  ["Honesta y con salida", "Una regresión simple casi iguala. Si con datos reales no gana por 1.3×, se usa la regla."],
], 7.6, 1.5, 5.1, 1.35, 1.55, "h");

// 7 Piloto Hogar simulado
s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Demo" });
s.addText("Cómo se medirá: piloto Hogar simulado con grupo control", { placeholder: "title" });
cifra(s, 0.6, 1.6, 3.6, String(PH.control_por_1000), "visitas por 1,000 hogares marcados SIN acción (control)", "ctl", HEX.rojo, 60);
cifra(s, 4.4, 1.6, 3.6, String(PH.tratamiento_por_1000), "visitas por 1,000 hogares marcados CON atención proactiva", "trt", HEX.verde, 60);
tarjeta(s, 8.4, 1.5, 4.3, 2.5, "red", HEX.navy);
txt(s, [{ text: nb(`−${PH.reduccion}`), options: { fontSize: 54, bold: true, color: "FFFFFF", breakLine: true } }, { text: nb(`IC 95 %: ${PH.ic} · llamadas −${PH.reduccion_llamadas}`), options: { fontSize: 15, color: "CADCFC", breakLine: true } }, { text: `Decisión simulada: ${PH.decision}`, options: { fontSize: 15, bold: true, color: "00C8FF" } }], { x: 8.7, y: 1.7, w: 3.8, h: 2.2, margin: 0, objectName: "red-t" });
tarjeta(s, 0.6, 4.3, 12.1, 1.9, "aviso", "FFF4D6");
txt(s, [{ text: "Resultado SIMULADO: ", options: { bold: true } }, { text: `60 días en San Pedro Sula, ${PH.marcados.toLocaleString("en-US")} hogares marcados, con el riesgo que la IA predijo fuera de muestra. Supone que el 70 % de los problemas resolubles a distancia se corrigen. Poder estadístico: ${PH.poder}. Muestra cómo se medirá; no promete un número.` }], { x: 0.9, y: 4.45, w: 11.5, h: 1.6, fontSize: 16, color: "7A4B00", margin: 0, valign: "middle", objectName: "aviso-t" });

// 8 Móvil
s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Demo" });
s.addText("Móvil: el mismo motor en fallas masivas", { placeholder: "title" });
s.addImage({ path: path.join(CAPT, "falla.png"), x: 0.6, y: 1.4, w: 7.7, h: 4.33, objectName: "captura-falla", altText: "Pantalla Falla masiva en vivo" });
tarjetas(s, [
  ["Aviso en minutos", "Causa en palabras simples y hora del NOC solo si la tiene. Cierre al restablecer."],
  [nb("−16 % de llamadas"), nb("IC 95 %: 12 % a 19 % en la simulación del piloto (efecto supuesto de 20 %).")],
  [nb(`Se paga con ${C.equilibrio_anio1}`), "de reducción de llamadas en los avisados. Benchmarks públicos: 18 % a 88 %."],
], 8.6, 1.45, 4.1, 1.35, 1.5, "m", 16);

// 9 Negocio
pres.addSection({ title: "Negocio" });
s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Negocio" });
s.addText(nb(`${C.neto_anio1_base} netos en el año 1, solo beneficio duro`), { placeholder: "title" });
cifra(s, 0.6, 1.55, 3.8, nb(C.hogar_equilibrio_anio1), "menos visitas evitables y el frente Hogar se paga en el año 1 (caso base 45 %)", "eqh");
cifra(s, 0.6, 3.15, 3.8, nb(C.equilibrio_anio1), "menos llamadas y el frente Móvil se paga en el año 1 (caso base 20 %)", "eqm", S.accent2);
cifra(s, 0.6, 4.75, 3.8, nb(C.neto_anio1_rango), "rango conservador a optimista (con costos hondureños)", "rng", HEX.gris, 26);
const esc = ["Conservador", "Base", "Optimista"];
const k = ["conservador", "base", "optimista"];
s.addChart(pres.charts.BAR, [
  { name: "Hogar", labels: esc, values: k.map((x) => D.neto_frente_millones[x]["Hogar"]) },
  { name: "Móvil", labels: esc, values: k.map((x) => D.neto_frente_millones[x]["Móvil"]) },
], { x: 4.8, y: 1.45, w: 7.9, h: 4.6, barDir: "col", barGapWidthPct: 60, chartColors: ["1E5BBF", "00A3CC"], showTitle: true,
  title: "Neto año 1 por frente (millones de L, con inversión)", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0",
  showLegend: true, legendPos: "b", legendFontSize: 13, legendFontFace: "+mn-lt", legendColor: "334155", ...ejes, objectName: "grafico" });
txt(s, nb(`Supuestos: visita ${C.costo_por_visita}, llamada ${C.costo_por_llamada}. Hogar equivale a solo ${C.hogar_reduccion_total_visitas} menos del total de visitas. Retención (${C.potencial_retencion_base}) NO incluida.`), { x: 0.6, y: 6.25, w: 12.1, h: 0.5, fontSize: 13, italic: true, color: HEX.gris, margin: 0, objectName: "nota-roi" });
s.addNotes("Usar 'Pon tus números' con visitas y costo por visita reales si los tienen.");

// 10 Piloto y GO/NO-GO
pres.addSection({ title: "Piloto" });
s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Piloto" });
s.addText("Piloto de 12 semanas con GO / NO-GO por frente", { placeholder: "title" });
[["Semanas 0–2", "Preparación", "CSV del ACS/OLT, NOC, CRM, call center y campo; análisis retrospectivo IA vs. regla; evaluación de impacto"],
  ["Semanas 3–10", "Piloto en vivo", "Hogar: la IA marca el 2 % y soporte N2 corrige. Móvil: avisos. 15 % de control"],
  ["Semanas 11–12", "Decisión", "Efecto con IC 95 %, costo real por visita y llamada evitada, GO/NO-GO"]].forEach(([w, f, d], i) => {
  const x = 0.6 + i * 4.15;
  circulo(s, x, 1.55, 0.7, String(i + 1), `f${i}`);
  txt(s, [{ text: w, options: { fontSize: 14, color: HEX.gris, breakLine: true } }, { text: f, options: { bold: true, color: S.text2 } }], { x: x + 0.85, y: 1.5, w: 3.0, h: 0.85, fontSize: 20, margin: 0, objectName: `ft${i}` });
  txt(s, d, { x, y: 2.5, w: 3.8, h: 1.1, fontSize: 14, margin: 0, valign: "top", objectName: `fd${i}` });
});
tarjeta(s, 0.6, 3.85, 6.0, 2.45, "go", "E8F7EE");
txt(s, [{ text: "GO Hogar si…", options: { bold: true, color: HEX.verde, fontSize: 20, breakLine: true } }, { text: "Visitas en marcados −15 % o más, significativo, opt-out < 2 %", options: { bullet: true, breakLine: true } }, { text: "La IA supera a la regla por 1.3× (si no, se usa la regla)", options: { bullet: true, breakLine: true } }, { text: "GO Móvil si…", options: { bold: true, color: HEX.verde, fontSize: 20, breakLine: true } }, { text: "Llamadas −12 % o más, significativo, opt-out < 2 %", options: { bullet: true } }], { x: 0.9, y: 3.95, w: 5.5, h: 2.3, fontSize: 15, margin: 0, valign: "top", paraSpaceAfter: 3, objectName: "go-t" });
tarjeta(s, 6.9, 3.85, 5.8, 2.45, "nogo", "FDECEC");
txt(s, [{ text: "NO-GO si…", options: { bold: true, color: HEX.rojo, fontSize: 20, breakLine: true } }, { text: "No hay diferencia significativa", options: { bullet: true, breakLine: true } }, { text: "El efecto no supera el mínimo", options: { bullet: true, breakLine: true } }, { text: "Los clientes rechazan los mensajes. Se detiene con costo acotado", options: { bullet: true } }], { x: 7.2, y: 3.95, w: 5.3, h: 2.3, fontSize: 15, margin: 0, valign: "top", paraSpaceAfter: 3, objectName: "nogo-t" });

// 11 Seguridad y privacidad
s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Piloto" });
s.addText("Seguridad y privacidad con marcos internacionales", { placeholder: "title" });
tarjetas(s, [
  ["Datos mínimos", "Solo desempeño del módem y la línea. Nunca contenido, navegación ni dispositivos del cliente (art. 100 de la Constitución)."],
  ["Estándar más exigente", "GDPR como referencia (Honduras aún no tiene ley integral), ISO 27001/27701/42001, SOC 2, NIST, OWASP API y LLM."],
  ["Al LLM, casi nada", "Nombre de pila saneado y tipo de situación. Sin ID, teléfono ni ubicación. Guardrail anti-phishing."],
], 0.6, 1.5, 6.0, 1.45, 1.6, "sp", 17);
tarjeta(s, 6.9, 1.5, 5.8, 4.65, "red-team", HEX.navy);
txt(s, [{ text: "Red team propio", options: { bold: true, color: "00C8FF", fontSize: 20, breakLine: true } }, { text: "12 ataques confirmados y corregidos", options: { bold: true, color: "FFFFFF", fontSize: 26, breakLine: true } }, { text: "Sesiones robadas, falta de roles, CSRF, phishing por IA, inyección, modelos alterados, tokens débiles, servidor expuesto…", options: { color: "CADCFC", fontSize: 15, breakLine: true } }, { text: "Cada uno con su prueba automática. Más de 200 pruebas en total.", options: { color: "FFFFFF", fontSize: 15, breakLine: true } }, { text: "Producción: SSO con MFA, cifrado con KMS, WAF y pentest independiente.", options: { color: "00C8FF", fontSize: 15 } }], { x: 7.2, y: 1.75, w: 5.2, h: 4.2, margin: 0, valign: "top", paraSpaceAfter: 8, objectName: "rt" });

// 12 Producción
s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Piloto" });
s.addText("Listo para producción, sin integraciones grandes", { placeholder: "title" });
[["ACS / OLT / CMTS", "telemetría diaria de módems", "CSV diario"], ["Órdenes de campo", "visitas y código de cierre", "CSV diario"], ["NOC / OSS", "sitios caídos, causa, hora", "CSV 15 min"], ["CRM / BSS", "consentimiento, opt-out", "CSV diario"], ["Call center / IVR", "llamadas (métrica norte)", "CSV diario"], ["WhatsApp Business", "entrega, respuestas, opt-out", "webhook"]].forEach(([f, d, fr], i) => {
  const y = 1.45 + i * 0.75;
  tarjeta(s, 0.6, y, 6.3, 0.64, `i${i}`);
  txt(s, [{ text: `${f}: `, options: { bold: true, color: S.text2 } }, { text: d }], { x: 0.85, y: y + 0.07, w: 4.3, h: 0.5, fontSize: 14, margin: 0, valign: "middle", objectName: `it${i}` });
  txt(s, fr, { x: 5.15, y: y + 0.07, w: 1.6, h: 0.5, fontSize: 12, color: S.accent2, bold: true, margin: 0, valign: "middle", align: "right", objectName: `if${i}` });
});
tarjetas(s, [
  ["Acciones remotas seguras", "Lista cerrada, de madrugada, por lotes y con reversión. Las ejecuta el ACS, nunca el LLM."],
  ["Riesgo principal", "Que la IA no gane con datos reales: se prueba antes, en las semanas 0–2. Si no, se usa la regla."],
  ["Cumplimiento", "Evaluación de impacto, plantillas aprobadas y visto bueno de Legal antes del primer mensaje."],
], 7.3, 1.45, 5.4, 1.35, 1.5, "r");

// 13 Pedido
pres.addSection({ title: "Cierre" });
s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: "Cierre" });
s.addText("Lo que pedimos a los Sharks", { placeholder: "title" });
[["Datos", "CSV diarios del NOC, ACS/OLT, CRM, call center y órdenes de campo de San Pedro Sula"], ["Equipo", "Patrocinador, enlaces del NOC y de ingeniería de acceso, soporte N2 y un analista al 50 %"], ["Canal y cumplimiento", "Plantillas de WhatsApp Business, evaluación de impacto y visto bueno de Legal"], ["Decisión", "En la semana 12, con números reales, ustedes deciden GO o NO-GO por frente"]].forEach(([t1, d], i) => {
  const y = 1.55 + i * 1.15;
  circulo(s, 0.6, y, 0.75, String(i + 1), `k${i}`);
  txt(s, [{ text: t1, options: { bold: true, color: S.text2, breakLine: true } }, { text: d, options: { fontSize: 15 } }], { x: 1.6, y: y - 0.05, w: 6.4, h: 0.95, fontSize: 18, margin: 0, valign: "top", objectName: `kt${i}` });
});
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.4, y: 1.55, w: 4.3, h: 4.4, rectRadius: 0.15, fill: { color: HEX.navy }, line: { color: HEX.navy }, shadow: sombra(), objectName: "inv" });
txt(s, "Inversión del piloto", { x: 8.75, y: 1.9, w: 3.6, h: 0.5, fontSize: 18, color: "00C8FF", bold: true, margin: 0, objectName: "inv-t" });
txt(s, nb(C.piloto_costo_base), { x: 8.75, y: 2.5, w: 3.6, h: 1.0, fontSize: 46, bold: true, color: "FFFFFF", margin: 0, objectName: "inv-v" });
txt(s, nb(`≈ ${C.piloto_costo_usd} · rango ${C.piloto_costo_rango}`), { x: 8.75, y: 3.5, w: 3.6, h: 0.8, fontSize: 15, color: "FFFFFF", margin: 0, valign: "top", objectName: "inv-r" });
txt(s, "Hogar + Móvil: integración por CSV, equipo, infraestructura, mensajes y compensaciones con tope.", { x: 8.75, y: 4.4, w: 3.6, h: 1.2, fontSize: 14, italic: true, color: "CADCFC", margin: 0, valign: "top", objectName: "inv-n" });

// 14 Cierre
s = pres.addSlide({ masterName: "CIERRE", sectionTitle: "Cierre" });
s.addText("Los chatbots atienden la llamada. Tigo Predice evita que ocurra", { placeholder: "title" });
s.addText("…y evita la visita.", { placeholder: "body" });
txt(s, "Tigo Predice · Sandra Michel Jimenez Zelaya · sandra.jimenez@tigo.com.hn", { x: 0.8, y: 6.3, w: 9, h: 0.4, fontSize: 16, color: "FFFFFF", margin: 0, objectName: "contacto" });

pres.writeFile({ fileName: SALIDA }).then(async () => { await applyTheme(SALIDA, THEME); console.log("OK", SALIDA); });
