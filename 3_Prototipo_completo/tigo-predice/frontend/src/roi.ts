// Caso de negocio calculado en el navegador, para la versión sin servidor («Pon tus números»).
// Es la misma cuenta de backend/app/services/roi.py, línea por línea, con los supuestos de config/negocio.toml.
// Una prueba compara este cálculo con el de Python en varios casos (src/test/roi_paridad.json).

import type { CasoNegocio } from "./api";

type Nivel = "bajo" | "base" | "alto";
type Valores = Record<string, number>;

export interface SupuestoNegocio {
  bajo: number;
  base: number;
  alto: number;
  unidad: string;
  fuente: string;
}

/** Lo que el cálculo necesita de config/negocio.toml. */
export interface ConfigNegocio {
  piloto: Record<string, number | string>;
  hogar: Record<string, number | string>;
  topes: Record<string, number>;
  base_real: Record<string, number | string>;
  supuestos: Record<string, SupuestoNegocio>;
}

// Supuestos que, al subir, AUMENTAN el beneficio neto (el resto lo reduce)
const A_FAVOR = new Set([
  "fallas_mes_piloto", "afectados_por_falla", "afectados_mes_nacional", "tasa_llamada_72h", "llamadas_por_cliente_que_llama",
  "reduccion_con_aviso", "tasa_entrega", "costo_por_llamada", "hogares_piloto", "tasa_visitas_hogar_mes",
  "pct_visitas_evitables", "llamadas_por_visita", "captura_modelo_hogar", "reduccion_visitas_marcados", "costo_por_visita",
]);
const NEUTROS = new Set(["tipo_cambio", "margen_contribucion", "churn_incremental_evitado", "arpu_afectado"]);
// Datos que Tigo ya tiene («Pon tus números»): en los escenarios quedan en su valor base
const VOLUMEN = new Set([
  "fallas_mes_piloto", "afectados_por_falla", "afectados_mes_nacional", "tasa_llamada_72h", "llamadas_por_cliente_que_llama",
  "costo_por_llamada", "hogares_piloto", "tasa_visitas_hogar_mes", "pct_visitas_evitables", "llamadas_por_visita",
  "costo_por_visita",
]);
// Solo afectan al piloto (no entran al tornado del neto nacional)
const SOLO_PILOTO = new Set([
  "fallas_mes_piloto", "afectados_por_falla", "desarrollo_piloto", "equipo_piloto", "hogares_piloto",
  "desarrollo_hogar_piloto", "equipo_hogar_piloto",
]);
const ESCENARIOS: Record<"conservador" | "base" | "optimista", [Nivel, Nivel]> = {
  conservador: ["bajo", "alto"],
  base: ["base", "base"],
  optimista: ["alto", "bajo"],
};
export const TUS_NUMEROS = ["llamadas_mes_fallas_nacional", "costo_por_llamada", "visitas_mes_hogar_nacional", "costo_por_visita"] as const;
// Qué supuesto reemplaza cada dato de Tigo (para no moverlo en el tornado)
const REEMPLAZA: Record<string, string> = {
  costo_por_llamada: "costo_por_llamada",
  llamadas_mes_fallas_nacional: "afectados_mes_nacional",
  costo_por_visita: "costo_por_visita",
  visitas_mes_hogar_nacional: "tasa_visitas_hogar_mes",
};
/** Límites que acepta la API para cada dato de Tigo (mayor que 0 y hasta este valor). */
export const LIMITES: Record<(typeof TUS_NUMEROS)[number], number> = {
  llamadas_mes_fallas_nacional: 10_000_000,
  costo_por_llamada: 100_000,
  visitas_mes_hogar_nacional: 1_000_000,
  costo_por_visita: 1_000_000,
};

const n = (v: number | string | undefined) => Number(v);
const suma = (o: Record<string, number>) => Object.values(o).reduce((a, b) => a + b, 0);

function supuestosNivel(cfg: ConfigNegocio, nivel: Nivel): Valores {
  return Object.fromEntries(Object.entries(cfg.supuestos).map(([k, v]) => [k, Number(v[nivel])]));
}

function valores(cfg: ConfigNegocio, escenario: keyof typeof ESCENARIOS): Valores {
  const [nivelFavor, nivelContra] = ESCENARIOS[escenario];
  const favor = supuestosNivel(cfg, nivelFavor), contra = supuestosNivel(cfg, nivelContra), base = supuestosNivel(cfg, "base");
  return Object.fromEntries(
    Object.keys(base).map((k) => [k, NEUTROS.has(k) || VOLUMEN.has(k) ? base[k] : A_FAVOR.has(k) ? favor[k] : contra[k]]),
  );
}

function movil(cfg: ConfigNegocio, s: Valores, tus: Valores, fuentes: Record<string, string>) {
  const pc = cfg.piloto;
  const llamadasPorAfectado = s.tasa_llamada_72h * s.llamadas_por_cliente_que_llama;
  const msgs = n(pc.mensajes_por_afectado), cWa = s.costo_whatsapp_mensaje;
  const efectoTratado = s.tasa_entrega * s.reduccion_con_aviso;

  const mesesP = n(pc.dias) / 30, tratP = 1 - n(pc.pct_control);
  const afectadosP = s.fallas_mes_piloto * s.afectados_por_falla * mesesP;
  const llamadasP = afectadosP * llamadasPorAfectado;
  const evitadasP = llamadasP * tratP * efectoTratado;
  const costosP = {
    desarrollo_integracion: s.desarrollo_piloto,
    equipo_piloto: s.equipo_piloto,
    infraestructura: s.infraestructura_mes * mesesP,
    whatsapp: afectadosP * tratP * msgs * cWa,
    compensaciones: Math.min(
      afectadosP * tratP * s.pct_compensados * s.costo_compensacion,
      cfg.topes.compensaciones_mes_piloto * mesesP,
    ),
  };
  const costoP = suma(costosP);
  const beneficioP = evitadasP * s.costo_por_llamada;

  const tratN = 1 - n(pc.holdout_escala);
  let llamadasMesN: number, afectadosMesN: number;
  if ("llamadas_mes_fallas_nacional" in tus) {
    llamadasMesN = tus.llamadas_mes_fallas_nacional;
    afectadosMesN = llamadasMesN / llamadasPorAfectado;
    fuentes.llamadas_mes_fallas_nacional = "dato Tigo";
  } else {
    afectadosMesN = s.afectados_mes_nacional;
    llamadasMesN = afectadosMesN * llamadasPorAfectado;
  }
  const evitadasN = llamadasMesN * 12 * tratN * efectoTratado;
  const beneficioN = evitadasN * s.costo_por_llamada;
  const recurrentes = {
    operacion_y_mantenimiento: s.operacion_anual,
    infraestructura: s.infraestructura_mes * 12,
    whatsapp: afectadosMesN * 12 * tratN * msgs * cWa,
    compensaciones: Math.min(
      afectadosMesN * 12 * tratN * s.pct_compensados * s.costo_compensacion,
      cfg.topes.compensaciones_mes_nacional * 12,
    ),
  };
  const costoRec = suma(recurrentes);
  const inversion = s.desarrollo_nacional;
  const valorPorPunto = llamadasMesN * 12 * tratN * s.tasa_entrega * s.costo_por_llamada;
  return {
    piloto: {
      afectados: afectadosP,
      llamadas_sin_aviso: llamadasP,
      llamadas_evitadas: evitadasP,
      beneficio_duro: beneficioP,
      costos: costosP,
      costo_total: costoP,
      neto: beneficioP - costoP,
      equilibrio_reduccion: costoP / (llamadasP * tratP * s.tasa_entrega * s.costo_por_llamada),
    },
    nacional: {
      afectados_mes: afectadosMesN,
      llamadas_mes_por_fallas: llamadasMesN,
      llamadas_evitadas_anio: evitadasN,
      beneficio_duro_anio: beneficioN,
      costos_recurrentes: recurrentes,
      costo_recurrente_anio: costoRec,
      inversion_unica: inversion,
      neto_anio1: beneficioN - costoRec - inversion,
      neto_regimen_anio: beneficioN - costoRec,
      equilibrio_reduccion_anio1: valorPorPunto ? (costoRec + inversion) / valorPorPunto : null,
      equilibrio_reduccion_regimen: valorPorPunto ? costoRec / valorPorPunto : null,
    },
  };
}

function hogar(cfg: ConfigNegocio, s: Valores, tus: Valores, fuentes: Record<string, string>) {
  const ch = cfg.hogar, pc = cfg.piloto;
  const cWa = s.costo_whatsapp_mensaje, msgs = n(ch.mensajes_por_marcado);
  const valorVisita = s.costo_por_visita + s.llamadas_por_visita * s.costo_por_llamada;
  const alcance = s.pct_visitas_evitables * s.captura_modelo_hogar; // visitas que la IA puede tocar
  const efecto = alcance * s.reduccion_visitas_marcados; // reducción sobre el TOTAL de visitas

  const mesesP = n(pc.dias) / 30, semanasP = n(pc.dias) / 7, tratP = 1 - n(pc.pct_control);
  const visitasP = s.hogares_piloto * s.tasa_visitas_hogar_mes * mesesP;
  const evitadasP = visitasP * tratP * efecto;
  const marcadosP = s.hogares_piloto * n(ch.pct_marcados_semana) * semanasP;
  const costosP = {
    desarrollo_hogar: s.desarrollo_hogar_piloto,
    equipo_hogar: s.equipo_hogar_piloto,
    whatsapp_hogar: marcadosP * tratP * msgs * cWa,
  };
  const costoP = suma(costosP);
  const beneficioP = evitadasP * valorVisita;

  const tratN = 1 - n(pc.holdout_escala);
  const hogaresN = n(cfg.base_real.clientes_hogar);
  let visitasMesN: number;
  if ("visitas_mes_hogar_nacional" in tus) {
    visitasMesN = tus.visitas_mes_hogar_nacional;
    fuentes.visitas_mes_hogar_nacional = "dato Tigo";
  } else {
    visitasMesN = hogaresN * s.tasa_visitas_hogar_mes;
  }
  const evitadasN = visitasMesN * 12 * tratN * efecto;
  const beneficioN = evitadasN * valorVisita;
  const marcadosN = hogaresN * n(ch.pct_marcados_semana) * 52;
  const recurrentes = {
    operacion_hogar: s.operacion_hogar_anual,
    whatsapp_hogar: marcadosN * tratN * msgs * cWa,
  };
  const costoRec = suma(recurrentes);
  const inversion = s.desarrollo_hogar_nacional;
  const valorPorPunto = visitasMesN * 12 * tratN * alcance * valorVisita;
  return {
    piloto: {
      hogares: s.hogares_piloto,
      marcados: marcadosP,
      visitas: visitasP,
      visitas_evitadas: evitadasP,
      llamadas_evitadas: evitadasP * s.llamadas_por_visita,
      beneficio_duro: beneficioP,
      costos: costosP,
      costo_total: costoP,
      neto: beneficioP - costoP,
      equilibrio_reduccion: costoP / (visitasP * tratP * alcance * valorVisita),
    },
    nacional: {
      hogares: hogaresN,
      visitas_mes: visitasMesN,
      marcados_anio: marcadosN,
      valor_por_visita: valorVisita,
      reduccion_total_visitas: efecto,
      visitas_evitadas_anio: evitadasN,
      llamadas_evitadas_anio: evitadasN * s.llamadas_por_visita,
      beneficio_duro_anio: beneficioN,
      costos_recurrentes: recurrentes,
      costo_recurrente_anio: costoRec,
      inversion_unica: inversion,
      neto_anio1: beneficioN - costoRec - inversion,
      neto_regimen_anio: beneficioN - costoRec,
      equilibrio_reduccion_anio1: valorPorPunto ? (costoRec + inversion) / valorPorPunto : null,
      equilibrio_reduccion_regimen: valorPorPunto ? costoRec / valorPorPunto : null,
    },
  };
}

/** Solo los datos de Tigo válidos, como números. */
function limpiar(tusNumeros: Record<string, number | string | undefined | null>): Valores {
  const tus: Valores = {};
  for (const [k, v] of Object.entries(tusNumeros))
    if ((TUS_NUMEROS as readonly string[]).includes(k) && v !== undefined && v !== null && v !== "") tus[k] = Number(v);
  return tus;
}

export function calcular(
  cfg: ConfigNegocio,
  escenario: keyof typeof ESCENARIOS = "base",
  tusNumeros: Record<string, number | string | undefined | null> = {},
  vals?: Valores,
) {
  const s: Valores = vals ? { ...vals } : valores(cfg, escenario);
  const pc = cfg.piloto;
  const fuentes: Record<string, string> = Object.fromEntries(Object.entries(cfg.supuestos).map(([k, v]) => [k, v.fuente]));
  const tus = limpiar(tusNumeros);
  for (const k of ["costo_por_llamada", "costo_por_visita"])
    if (k in tus) {
      s[k] = tus[k];
      fuentes[k] = "dato Tigo";
    }
  const mov = movil(cfg, s, tus, fuentes), hog = hogar(cfg, s, tus, fuentes);

  // ------------------------------------------------------------------ totales (ambos frentes)
  const mp = mov.piloto, hp = hog.piloto, mn = mov.nacional, hn = hog.nacional;
  const costoP = mp.costo_total + hp.costo_total;
  const beneficioP = mp.beneficio_duro + hp.beneficio_duro;
  const beneficioN = mn.beneficio_duro_anio + hn.beneficio_duro_anio;
  const costoRec = mn.costo_recurrente_anio + hn.costo_recurrente_anio;
  const inversion = mn.inversion_unica + hn.inversion_unica;
  const netoRegimen = beneficioN - costoRec;

  // -------------------------------- potencial NO incluido en el caso base (retención, frente móvil)
  const tratN = 1 - n(pc.holdout_escala);
  const retenidos = mn.afectados_mes * 12 * tratN * s.tasa_entrega * s.churn_incremental_evitado;
  const potencialRetencion = retenidos * s.arpu_afectado * s.margen_contribucion * 12;

  return {
    escenario,
    supuestos: s,
    fuentes,
    tus_numeros: tus,
    movil: mov,
    hogar: hog,
    piloto: {
      ciudad: pc.ciudad,
      dias: pc.dias,
      costos: { ...mp.costos, ...hp.costos },
      costo_total: costoP,
      beneficio_duro: beneficioP,
      neto: beneficioP - costoP,
    },
    nacional: {
      beneficio_duro_anio: beneficioN,
      costos_recurrentes: { ...mn.costos_recurrentes, ...hn.costos_recurrentes },
      costo_recurrente_anio: costoRec,
      inversion_unica: inversion,
      neto_anio1: netoRegimen - inversion,
      neto_regimen_anio: netoRegimen,
      roi_anio1: (netoRegimen - inversion) / (costoRec + inversion),
      payback_meses: netoRegimen > 0 ? inversion / (netoRegimen / 12) : null,
    },
    potencial_no_incluido: {
      clientes_retenidos_anio: retenidos,
      margen_retenido_anio: potencialRetencion,
      nota:
        "Solo se acredita si el piloto mide menos churn en tratados que en control; " +
        "se calcula con margen de contribución, no con ingreso bruto.",
    },
    tipo_cambio: s.tipo_cambio,
  };
}

export function escenarios(cfg: ConfigNegocio, tusNumeros: Record<string, number | string | undefined | null> = {}) {
  return {
    conservador: calcular(cfg, "conservador", tusNumeros),
    base: calcular(cfg, "base", tusNumeros),
    optimista: calcular(cfg, "optimista", tusNumeros),
  };
}

/** Cuánto se mueve el neto nacional del año 1 al llevar cada supuesto a su valor bajo y alto. */
export function tornado(cfg: ConfigNegocio, tusNumeros: Record<string, number | string | undefined | null> = {}) {
  const baseVals = valores(cfg, "base");
  const neto = (v: Valores) => calcular(cfg, "base", tusNumeros, v).nacional.neto_anio1;
  const base = neto(baseVals);
  const fijados = new Set(Object.keys(limpiar(tusNumeros)).map((k) => REEMPLAZA[k]));
  const salida = [];
  for (const [k, sup] of Object.entries(cfg.supuestos)) {
    if (NEUTROS.has(k) || SOLO_PILOTO.has(k) || fijados.has(k)) continue;
    const bajo = neto({ ...baseVals, [k]: Number(sup.bajo) });
    const alto = neto({ ...baseVals, [k]: Number(sup.alto) });
    salida.push({
      supuesto: k,
      unidad: sup.unidad,
      fuente: sup.fuente,
      valor_bajo: sup.bajo,
      valor_base: sup.base,
      valor_alto: sup.alto,
      neto_con_bajo: bajo,
      neto_con_alto: alto,
      neto_base: base,
      amplitud: Math.abs(alto - bajo),
    });
  }
  return salida.sort((a, b) => b.amplitud - a.amplitud);
}

/** Misma respuesta que GET /api/roi. */
export function casoNegocio(cfg: ConfigNegocio, tusNumeros: Record<string, number | string | undefined | null> = {}): CasoNegocio {
  return {
    escenarios: escenarios(cfg, tusNumeros),
    tornado: tornado(cfg, tusNumeros),
    tus_numeros: limpiar(tusNumeros),
  } as unknown as CasoNegocio;
}
