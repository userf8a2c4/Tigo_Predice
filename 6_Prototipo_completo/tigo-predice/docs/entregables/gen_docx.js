// Propuesta v03 en Word. Uso: node gen_docx.js <salida.docx> <docs/capturas> <docs/cifras.json>
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, HeadingLevel, BorderStyle, LevelFormat, Footer, PageNumber, ImageRun,
} = require("docx");

const [SALIDA, CAPT, CIFRAS] = process.argv.slice(2);
const C = JSON.parse(fs.readFileSync(CIFRAS, "utf8"));
const AZUL = "00377B", CELESTE = "00A3CC", GRIS = "5B6575", VERDE = "16A35A", ROJO = "E0303A";
const ANCHO = 9360;

const t = (text, o = {}) => new TextRun({ text, font: "Calibri", size: 22, ...o });
const p = (runs, o = {}) => new Paragraph({ spacing: { after: 120, line: 276 }, ...o, children: Array.isArray(runs) ? runs : [t(runs)] });
const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1, spacing: { before: 260, after: 110 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: CELESTE, space: 2 } },
  children: [new TextRun({ text, font: "Calibri", size: 28, bold: true, color: AZUL })],
});
const bullet = (runs) => new Paragraph({ numbering: { reference: "vinetas", level: 0 }, spacing: { after: 60 }, children: Array.isArray(runs) ? runs : [t(runs)] });
const borde = { style: BorderStyle.SINGLE, size: 4, color: "D5DCE6" };
const bordes = { top: borde, bottom: borde, left: borde, right: borde };
const imagen = (archivo, titulo, ancho = 600) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 },
  children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(CAPT, archivo)), transformation: { width: ancho, height: Math.round(ancho * 900 / 1600) }, altText: { title: titulo, description: titulo, name: archivo } })],
});
const pie = (texto) => p([t(texto, { size: 18, italics: true, color: GRIS })], { alignment: AlignmentType.CENTER });

function tabla(filas, anchos, { cabecera = true, primeraNegrita = false } = {}) {
  return new Table({
    width: { size: ANCHO, type: WidthType.DXA }, columnWidths: anchos,
    rows: filas.map((fila, i) => new TableRow({
      tableHeader: cabecera && i === 0,
      children: fila.map((celda, j) => new TableCell({
        width: { size: anchos[j], type: WidthType.DXA }, borders: bordes,
        margins: { top: 70, bottom: 70, left: 110, right: 110 },
        shading: cabecera && i === 0 ? { fill: AZUL, type: ShadingType.CLEAR, color: "auto" }
          : (primeraNegrita && j === 0 ? { fill: "EEF3F9", type: ShadingType.CLEAR, color: "auto" } : undefined),
        children: [new Paragraph({ children: Array.isArray(celda) ? celda : [t(String(celda), {
          size: 20, bold: (cabecera && i === 0) || (primeraNegrita && j === 0), color: cabecera && i === 0 ? "FFFFFF" : undefined })] })],
      })),
    })),
  });
}

const contenido = [
  new Paragraph({ children: [t("TIGO CX MONTH · CONCURSO SHARKS DE IA", { size: 18, bold: true, color: CELESTE })] }),
  new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text: "Tigo Predice", font: "Calibri", size: 56, bold: true, color: AZUL })] }),
  new Paragraph({ spacing: { after: 40 }, children: [t("«Los chatbots y copilotos atienden la llamada. Tigo Predice evita que ocurra.»", { size: 24, italics: true, color: GRIS })] }),
  new Paragraph({ spacing: { after: 220 }, children: [t("La IA que detecta el problema antes que el cliente, y lo resuelve antes de que llame o de que haya que mandar un técnico.", { size: 22, color: AZUL })] }),

  tabla([
    ["Nombre de la idea", "Tigo Predice: la IA que resuelve antes de que el cliente llame"],
    ["Autoría", [t("Sandra Jimenez · Asistente de Experiencia B2B · sandra.jimenez@tigo.com.hn")]],
    ["Categoría principal", "Experiencia del Cliente / CX"],
    ["Otras categorías", "Red y Operaciones · Eficiencia / Reducción de Costos · Self-Service y Canales Digitales · Analítica"],
    ["Propuesta", "Piloto de 60 días en San Pedro Sula: Hogar (telemetría de módems) + Móvil (fallas masivas), con grupo control del 15 %"],
    ["Estado", "Prototipo funcional con dos demos en vivo y más de 200 pruebas automáticas (datos simulados)"],
  ], [2600, 6760], { cabecera: false, primeraNegrita: true }),

  h1("1. El problema"),
  bullet([t("Hogar: ", { bold: true, color: AZUL }), t("los problemas de internet se ven en la telemetría del módem días antes de que el cliente los sufra (señal que baja, WiFi saturado, reinicios), pero hoy solo se miran cuando cruzan un umbral. El cliente llama, espera y se agenda un técnico, aunque 1 de cada 4 visitas es evitable (supuesto a validar con los códigos de cierre; la industria reporta 17–20 % «sin falla encontrada»).")]),
  bullet([t("Móvil: ", { bold: true, color: AZUL }), t("cuando cae un sitio, el NOC lo sabe en minutos, pero los clientes se enteran por la falla. Un benchmark público indica que 1 de cada 3 afectados llama si no recibe aviso.")]),

  h1("2. La solución"),
  p([t("Frente Hogar (principal). ", { bold: true }), t(`Cada semana la IA califica la telemetría de todos los módems y marca al 2 % con más riesgo de llamar o necesitar visita en 7 días, con la explicación de por qué. Si es WiFi o firmware, se corrige a distancia y el cliente recibe un WhatsApp. Si es físico, la visita se agenda antes del corte y el técnico llega con el diagnóstico.`)]),
  p([t("Frente Móvil. ", { bold: true }), t("En fallas masivas, WhatsApp en minutos con la causa en palabras simples, la hora del NOC (solo si la tiene) y un mensaje de cierre.")]),
  p([t("Medición. ", { bold: true }), t("En ambos frentes, un grupo control aleatorio del 15 % mide el efecto real.")]),
  imagen("hogar.png", "Demo Hogar en vivo"),
  pie("Demo «Hogar en vivo»: la IA marca el hogar el 28/09 (la regla de umbrales recién el 03/10 y el cliente habría llamado el 02/10), explica por qué y se corrige a distancia: visita evitada, L 780 de ahorro por L 0.31. Datos simulados."),

  h1("3. ¿Cómo usa la IA?"),
  bullet([t("IA predictiva (corazón del producto): ", { bold: true }), t(`modelo de machine learning sobre la telemetría de módems, con validación temporal. Con el mismo presupuesto anticipa el ${C.hogar_ia_captura} de las visitas evitables, frente al ${C.hogar_regla_captura} de una regla de umbrales (${C.hogar_ia_vs_regla}; AUC ${C.hogar_ia_auc}). El ${C.hogar_deteccion_temprana} de lo que anticipa todavía no tenía ninguna alarma. Cada caso se explica por variables (SHAP).`)]),
  bullet([t("Honestidad: ", { bold: true }), t("una regresión logística simple rinde casi igual, así que se puede empezar simple. Si con datos reales la IA no supera a la regla por 1.3×, el piloto usa la regla.")]),
  bullet([t("IA generativa (Claude): ", { bold: true }), t("redacta los avisos con guardrails (usted, sin datos sensibles, sin horas inventadas, sin enlaces no oficiales, siempre opción de agente). Si falla, se usa la plantilla aprobada.")]),
  bullet([t("Diseño experimental: ", { bold: true }), t("tratados vs. control, con intervalo de confianza del 95 % y decisión GO/NO-GO por frente.")]),

  h1("4. Beneficios"),
  tabla([
    ["Para el cliente", "Para Tigo", "Para los colaboradores"],
    ["No sufre la falla o se entera por Tigo; no tiene que llamar ni esperar, y el técnico llega una sola vez.",
      "Menos visitas técnicas evitables y menos llamadas; técnicos enfocados en lo que de verdad necesita ir a campo.",
      "Soporte recibe una lista diaria priorizada y explicada; menos llamadas repetitivas en el call center."],
  ], [3120, 3120, 3120]),

  h1("5. Caso de negocio conservador (solo beneficio duro)"),
  p([t(`Neto del año 1 (Hogar + Móvil, base): ${C.neto_anio1_base}`, { bold: true, color: AZUL }), t(`, rango ${C.neto_anio1_rango}. Hogar se paga con solo ${C.hogar_equilibrio_anio1} menos visitas evitables en los hogares marcados; Móvil, con solo ${C.equilibrio_anio1} menos llamadas.`)]),
  tabla([
    ["Indicador", "Valor (escenario base)", "Rango / nota"],
    ["Hogar · neto año 1", C.hogar_neto_anio1_base, C.hogar_neto_anio1_rango],
    ["Hogar · visitas evitadas al año", C.hogar_visitas_evitadas_anio_base, `${C.hogar_visitas_evitadas_anio_rango} · solo ${C.hogar_reduccion_total_visitas} del total de visitas`],
    ["Móvil · neto año 1", C.movil_neto_anio1_base, C.movil_neto_anio1_rango],
    ["Móvil · llamadas evitadas al año", C.llamadas_evitadas_anio_base, C.llamadas_evitadas_anio_rango],
    ["Neto anual en régimen (ambos)", C.neto_regimen_base, "año 2 en adelante"],
    ["Beneficio duro / costo recurrente", `${C.beneficio_duro_anio_base} / ${C.costo_recurrente_anio_base}`, `inversión única ${C.inversion_unica_base}`],
    ["Potencial NO incluido (retención)", C.potencial_retencion_base, "margen, no ingreso bruto; vale cero hasta medirlo"],
  ], [3200, 2400, 3760]),
  p([t(`Supuestos clave: visita técnica ${C.costo_por_visita}, llamada ${C.costo_por_llamada}, ${C.hogar_visitas_mes} visitas al mes en ${C.hogares_nacional} hogares. Se reemplazan con datos de Tigo en «Pon tus números».`, { size: 18, color: GRIS })]),

  h1("6. Piloto, inversión y criterios de decisión"),
  p([t(`Inversión del piloto (ambos frentes): ${C.piloto_costo_base} (≈ ${C.piloto_costo_usd}), rango ${C.piloto_costo_rango}. `, { bold: true }), t("Incluye integración por CSV, equipo, infraestructura, mensajes y compensaciones con tope.")]),
  bullet("Semanas 0–2: CSV del ACS/OLT, NOC, CRM, call center y campo; análisis retrospectivo (¿la IA le gana a la regla con 3 meses reales?); plantillas y evaluación de impacto aprobadas."),
  bullet("Semanas 3–10: Hogar (la IA marca el 2 % semanal; soporte N2 corrige a distancia) y Móvil (avisos y cierres), con 15 % de control."),
  bullet("Semanas 11–12: análisis con IC 95 % y decisión GO/NO-GO por frente al comité."),
  p([t("GO Hogar ", { bold: true, color: VERDE }), t("si las visitas en hogares marcados bajan ≥ 15 %, significativo y con opt-out < 2 % (si la IA no supera a la regla por 1.3×, se usa la regla). "), t("GO Móvil ", { bold: true, color: VERDE }), t("si las llamadas bajan ≥ 12 % (su punto de equilibrio), significativo y con opt-out < 2 %. "), t("NO-GO ", { bold: true, color: ROJO }), t("en cualquier otro caso.")]),
  p([t("Simulación del diseño (datos sintéticos, efectos supuestos): ", { italics: true }), t("Hogar −19 % de visitas (IC 95 % 12 % a 25 %) y −56 % de llamadas técnicas; Móvil −16 % de llamadas (IC 95 % 12 % a 19 %).", { italics: true })]),

  h1("7. Seguridad y privacidad (vara de hiperescalador)"),
  bullet([t("Datos mínimos: ", { bold: true }), t("solo desempeño del módem y de la línea; nunca contenido de comunicaciones, navegación ni dispositivos del cliente.")]),
  bullet([t("Marco: ", { bold: true }), t("GDPR como estándar de referencia (Honduras aún no tiene ley integral), Constitución (arts. 76, 100 y 182), política de Millicom, ISO 27001/27701/42001, SOC 2, NIST y OWASP.")]),
  bullet([t("Red team propio: ", { bold: true }), t("12 ataques confirmados y corregidos (sesiones robadas, falta de roles, CSRF, phishing por IA, modelos alterados, entre otros), cada uno con su prueba automática.")]),
  bullet([t("Antes del primer mensaje: ", { bold: true }), t("evaluación de impacto aprobada por Legal, SSO con MFA y prueba de penetración.")]),

  h1("8. Lo que pedimos a los Sharks (12 semanas)"),
  bullet([t("Datos: ", { bold: true }), t("CSV diarios del NOC, ACS/OLT, CRM, call center y órdenes de campo de San Pedro Sula.")]),
  bullet([t("Equipo: ", { bold: true }), t("un patrocinador, enlaces del NOC y de ingeniería de acceso, soporte nivel 2 y un analista de datos al 50 %.")]),
  bullet([t("Canal y cumplimiento: ", { bold: true }), t("plantillas de WhatsApp Business, evaluación de impacto y visto bueno de Legal.")]),
  bullet([t("Inversión: ", { bold: true }), t(`${C.piloto_costo_base}, con decisión GO/NO-GO por frente en la semana 12.`)]),

  h1("9. Riesgos y mitigación"),
  tabla([
    ["Riesgo", "Mitigación"],
    ["La IA no supera a la regla con datos reales", "Análisis retrospectivo en semanas 0–2; si no llega a 1.3×, se usa la regla (el producto funciona igual)."],
    ["Una acción remota deja al cliente sin servicio", "Lista cerrada de acciones, firmware certificado, de madrugada, por lotes y con reversión."],
    ["Fatiga de mensajes", "Máximo 1 mensaje por acción en Hogar y 2 por falla en Móvil; NO-GO si el opt-out supera 2 %."],
    ["Calidad de datos cliente ↔ nodo/sitio", "Auditar una muestra en las semanas 0–2; medir el % de avisos a no afectados."],
    ["Privacidad y regulación", "Evaluación de impacto, datos mínimos, seudonimización, cifrado, roles y bitácoras. Validar con Legal los requisitos de CONATEL."],
  ], [3000, 6360]),
];

const doc = new Document({
  creator: "Sandra Jimenez", title: "Propuesta Tigo Predice v03 — Tigo CX Month",
  styles: { default: { document: { run: { font: "Calibri", size: 22 } } } },
  numbering: { config: [{ reference: "vinetas", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1200, bottom: 1200, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [t("Tigo Predice · Datos simulados — supuestos a validar con Tigo · Página ", { size: 16, color: GRIS }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: GRIS, font: "Calibri" })] })] }) },
    children: contenido,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(SALIDA, b); console.log("OK", SALIDA); });
