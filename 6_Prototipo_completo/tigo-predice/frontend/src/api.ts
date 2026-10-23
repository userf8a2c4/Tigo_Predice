import type { FeatureCollection } from "geojson";

// Tipos y acceso a la API de Tigo Predice v03

export type Prioridad = "Alta" | "Media" | "Baja";
export type Nivel = "bajo" | "base" | "alto";

// ------------------------------------------------------------------ general
export interface Salud {
  ok: boolean;
  clientes: number;
  modelo: string;
  llm_modo: "IA" | "plantillas";
  llm_estado: string;
  llm_modelo: string;
}

export interface Supuesto {
  unidad: string;
  bajo: number;
  base: number;
  alto: number;
  fuente: "supuesto a validar" | "benchmark público" | "dato Tigo";
  nota: string;
}

export interface Config {
  posicionamiento: string;
  lema: string;
  fecha_corte: string;
  piloto: Record<string, number | string>;
  hogar: Record<string, number | string>;
  supuestos: Record<string, Supuesto>;
  modelo: string;
  llm_modo: "IA" | "plantillas";
  llm_estado: string;
}

export type Cifras = Record<string, string>;

export interface Inicio {
  posicionamiento: string;
  lema: string;
  cifras: Cifras;
  hogar: {
    reduccion_visitas: number;
    ic: [number, number];
    reduccion_llamadas: number;
    decision: "GO" | "NO-GO";
    ia_vs_regla: number;
    captura_ia: number;
    captura_regla: number;
    marcados_hoy: number;
    aviso: string;
  };
  piloto: {
    reduccion: number;
    ic: [number, number];
    decision: "GO" | "NO-GO";
    por_1000_control: number;
    por_1000_tratamiento: number;
    aviso: string;
  };
  criterios: { go_reduccion_min: number; go_optout_max: number; alfa: number };
}

export interface CiudadMapa {
  ciudad: string;
  departamento: string;
  lat: number;
  lon: number;
  clientes: number;
}

export interface CeldaMapa {
  celda_id: string;
  ciudad: string;
  zona: string;
  lat: number;
  lon: number;
  clientes: number;
  falla_activa: boolean;
}

export interface Falla {
  falla_id: string;
  ciudad: string;
  celdas: string;
  inicio: string;
  duracion_horas: number;
  estado: "activa" | "resuelta";
  causa: string;
  eta_horas: number | null;
}

export interface Mapa {
  ciudades: CiudadMapa[];
  celdas: CeldaMapa[];
  fallas: Falla[];
}

// ------------------------------------------------------------------ frente Hogar
export interface Motivo {
  variable: string;
  texto: string;
  valor: string;
  contribucion: number;
}

export interface DiaHogar {
  dia: number;
  fecha: string;
  senal: number;
  retrans: number;
  reinicios: number;
  desconexiones: number;
  latencia: number;
  riesgo: number;
  regla: boolean;
}

export interface EscenarioHogar {
  caso: "remoto" | "tecnico";
  titulo: string;
  ciudad: string;
  hogar: {
    hogar_id: string;
    nombre: string;
    telefono: string;
    nodo_id: string;
    tecnologia: string;
    modem: string;
    plan: string;
    senal_unidad: string;
    senal_umbral: number;
  };
  umbral_riesgo: number;
  presupuesto: number;
  eventos: {
    inicio: number;
    ia: number | null;
    regla: number | null;
    llamada: number;
    visita: number;
    correccion: number;
    dias_antes_llamada: number | null;
    dias_antes_regla: number | null;
  };
  riesgo_al_marcar: number;
  explicacion: Motivo[];
  diagnostico: string;
  acciones: string[];
  mensaje: { texto: string; fuente: string; guardrails: string; version_prompt: string };
  sin: DiaHogar[];
  con: DiaHogar[];
  kpis: { visita: string; llamadas_evitadas: number; ahorro: string; costo_accion: string; detalle: string };
  frase_final: string;
  aviso: string;
}

export interface ListaHoy {
  ciudad: string;
  fecha: string;
  hogares_ciudad: number;
  marcados: number;
  con_alarma_regla: number;
  umbral_riesgo: number;
  hogares: {
    hogar_id: string;
    nombre: string;
    nodo_id: string;
    tecnologia: string;
    riesgo: number;
    alarma_regla: boolean;
    motivos: Motivo[];
    accion: string;
    contacto: string;
  }[];
}

export interface Criterio {
  criterio: string;
  valor: string;
  cumple: boolean;
}

export interface PilotoHogar {
  aviso: string;
  ciudad: string;
  dias: number;
  semanas: number;
  hogares_piloto: number;
  marcados_por_semana: number;
  marcados: number;
  metrica_norte: Efecto;
  llamadas: Efecto;
  pct_con_visita: { tasa_tratamiento: number; tasa_control: number; valor_p: number };
  decision: { decision: "GO" | "NO-GO"; motivo: string; criterios: Criterio[] };
  ia_vs_regla: number;
  visitas_evitadas_estimadas: number;
  llamadas_evitadas_estimadas: number;
  valor_estimado: number;
  secundarias: { tasa_optout: number; acciones_remotas: number; riesgo_medio_marcados: number };
  por_semana: { semana: number; marcados: number; control_por_1000: number; tratamiento_por_1000: number }[];
  potencia: Potencia;
}

export interface MetricasHogar {
  auc: number;
  brier: number | null;
  marcados_por_semana: number;
  precision: number;
  captura_eventos: number;
  captura_visitas: number;
  captura_visitas_evitables: number;
  captura_visitas_prevenibles: number;
  visitas_por_100_marcados: number;
  visitas_evitables_por_100_marcados: number;
  lift: { decil: number; tasa: number; lift: number; captura_acumulada: number }[];
}

export interface ModeloHogar {
  version: string;
  pregunta: string;
  validacion: string;
  presupuesto: number;
  tasa_base_prueba: number;
  visitas_por_1000_prueba: number;
  pct_visitas_evitables_prueba: number;
  modelos: Record<string, MetricasHogar>;
  regla_umbrales: MetricasHogar;
  umbrales: Record<string, string>;
  azar: MetricasHogar;
  ia_vs_regla: number;
  deteccion_temprana: number;
  calibracion: Record<string, { prob_media: number; tasa_real: number; n: number }[]>;
  sesgo: Record<"tecnologia" | "zona", { grupo: string; n: number; tasa_real: number; prob_media: number; pct_marcado: number; captura_visitas_evitables: number; auc: number | null }[]>;
  importancia: { variable: string; nombre: string; valor: number }[];
}

// ------------------------------------------------------------------ frente Móvil: Falla en vivo
export interface EscenarioFalla {
  ciudad: string;
  sitio: {
    celdas: string[];
    lat: number;
    lon: number;
    radio_km: number;
    causa: string;
    causa_cliente: string;
    hora_inicio: number;
    eta_horas: number;
  };
  muestra: {
    afectados: number;
    tratamiento: number;
    control: number;
    pct_control: number;
    puntos: { lat: number; lon: number; grupo: "tratamiento" | "control"; prioridad: boolean }[];
  };
  mensajes: { etiqueta: string; cliente: string; telefono: string; texto: string; fuente: string; guardrails: string }[];
  linea_tiempo: { hora: number; control: number; tratados: number }[];
  por_1000: { sin_aviso: number; con_aviso: number };
  kpis: {
    afectados_reales: number;
    llamadas_sin_aviso: number;
    llamadas_evitadas: Record<Nivel, number>;
    llamadas_evitadas_texto: string;
    ahorro_texto: string;
    costo_accion_texto: string;
    compensados_por_modelo: number;
    neto_texto: string;
    supuestos: string;
  };
  frase_final: string;
  aviso: string;
}

// ------------------------------------------------------------------ Fase 1: piloto
export interface Efecto {
  n_tratamiento: number;
  n_control: number;
  por_1000_tratamiento: number;
  por_1000_control: number;
  diferencia_por_1000: number;
  ic_diferencia_por_1000: [number, number];
  reduccion_relativa: number;
  ic_reduccion_relativa: [number, number];
  valor_p: number;
  significativo: boolean;
}

export interface Potencia {
  tasa_base: number;
  reduccion_a_detectar: number;
  alfa: number;
  poder_objetivo: number;
  pct_control: number;
  afectados_necesarios: number;
  control_necesario: number;
  afectados_esperados_piloto: number;
  poder_alcanzado: number;
  dias_necesarios: number;
  nota: string;
}

export interface ResultadosPiloto {
  aviso: string;
  ciudad: string;
  dias: number;
  fallas: number;
  afectados: number;
  efecto_supuesto: number;
  metrica_norte: Efecto;
  pct_que_llama: { tasa_tratamiento: number; tasa_control: number; valor_p: number };
  decision: { decision: "GO" | "NO-GO"; motivo: string; criterios: { criterio: string; valor: string; cumple: boolean }[] };
  llamadas_evitadas_estimadas: number;
  secundarias: Record<string, number | string>;
  por_falla: { falla: number; afectados: number; eta_conocida: boolean; control_por_1000: number; tratamiento_por_1000: number }[];
  potencia: Potencia;
}

// ------------------------------------------------------------------ caso de negocio
interface FrenteNacional {
  beneficio_duro_anio: number;
  costos_recurrentes: Record<string, number>;
  costo_recurrente_anio: number;
  inversion_unica: number;
  neto_anio1: number;
  neto_regimen_anio: number;
  equilibrio_reduccion_anio1: number;
  equilibrio_reduccion_regimen: number;
}

export interface Escenario {
  escenario: string;
  supuestos: Record<string, number>;
  fuentes: Record<string, string>;
  movil: {
    piloto: {
      afectados: number;
      llamadas_sin_aviso: number;
      llamadas_evitadas: number;
      beneficio_duro: number;
      costos: Record<string, number>;
      costo_total: number;
      neto: number;
      equilibrio_reduccion: number;
    };
    nacional: FrenteNacional & { afectados_mes: number; llamadas_mes_por_fallas: number; llamadas_evitadas_anio: number };
  };
  hogar: {
    piloto: {
      hogares: number;
      marcados: number;
      visitas: number;
      visitas_evitadas: number;
      llamadas_evitadas: number;
      beneficio_duro: number;
      costos: Record<string, number>;
      costo_total: number;
      neto: number;
      equilibrio_reduccion: number;
    };
    nacional: FrenteNacional & {
      hogares: number;
      visitas_mes: number;
      marcados_anio: number;
      valor_por_visita: number;
      reduccion_total_visitas: number;
      visitas_evitadas_anio: number;
      llamadas_evitadas_anio: number;
    };
  };
  piloto: { ciudad: string; dias: number; costos: Record<string, number>; costo_total: number; beneficio_duro: number; neto: number };
  nacional: {
    beneficio_duro_anio: number;
    costos_recurrentes: Record<string, number>;
    costo_recurrente_anio: number;
    inversion_unica: number;
    neto_anio1: number;
    neto_regimen_anio: number;
    roi_anio1: number;
    payback_meses: number | null;
  };
  potencial_no_incluido: { clientes_retenidos_anio: number; margen_retenido_anio: number; nota: string };
  tipo_cambio: number;
}

export interface Tornado {
  supuesto: string;
  unidad: string;
  fuente: string;
  valor_bajo: number;
  valor_base: number;
  valor_alto: number;
  neto_con_bajo: number;
  neto_con_alto: number;
  neto_base: number;
  amplitud: number;
}

export interface CasoNegocio {
  escenarios: Record<"conservador" | "base" | "optimista", Escenario>;
  tornado: Tornado[];
  tus_numeros: Record<string, number>;
}

// ------------------------------------------------------------------ modelo
export interface MetricasModelo {
  auc: number;
  brier: number | null;
  precision_top10: number;
  recall_top10: number;
  llamadas_por_100_contactos_top20: number;
  lift: { decil: number; tasa: number; lift: number; captura_acumulada: number }[];
}

export interface ModeloInfo {
  hogar: ModeloHogar;
  fase1: {
    version: string;
    pregunta: string;
    validacion: string;
    tasa_base_prueba: number;
    llamadas_por_1000_prueba: number;
    modelos: Record<string, MetricasModelo>;
    regla_operativa: MetricasModelo;
    azar: { llamadas_por_100_contactos_top20: number };
    calibracion: Record<string, { prob_media: number; tasa_real: number; n: number }[]>;
    estrategias: Record<string, string | number | null>[];
    sesgo: Record<"zona" | "segmento", { grupo: string; n: number; tasa_real: number; prob_media: number; pct_priorizado: number; auc: number | null }[]>;
    importancia: { variable: string; nombre: string; valor: number }[];
    pct_prioridad: number;
  };
  fase2: Record<string, { descripcion: string; auc: number; auc_baseline: number }>;
}

export interface Produccion {
  consentimiento: { tema: string; detalle: string }[];
  integracion: { fuente: string; dato: string; frecuencia_piloto: string; frecuencia_produccion: string }[];
  riesgos: { riesgo: string; probabilidad: string; impacto: string; mitigacion: string }[];
  equipo: { rol: string; dedicacion: string; responsabilidad: string }[];
  plan: { semanas: string; fase: string; actividades: string }[];
  seguridad: { control: string; estado: string; produccion: string }[];
}

// ------------------------------------------------------------------ Fase 2 (visión)
export interface Factor {
  variable: string;
  grupo: string;
  texto: string;
  impacto: number;
}

export interface ClienteResumen {
  cliente_id: string;
  nombre: string;
  telefono: string;
  segmento: string;
  plan: string;
  ciudad: string;
  celda_id: string;
  arpu: number;
  clv: number;
  prob_incidencia: number;
  prob_churn: number;
  valor_en_riesgo: number;
  prioridad: Prioridad;
  riesgo_dominante: "churn" | "incidencia";
  factores: Factor[];
  accion: string;
  accion_nombre: string;
  motivo_accion: string;
  contactable: boolean;
  humano: boolean;
  conversacion: boolean;
}

export interface ClienteDetalle extends Omit<ClienteResumen, "conversacion"> {
  factores_churn: Factor[];
  factores_incidencia: Factor[];
  variables: Record<string, number | null>;
  antiguedad_meses: number;
  opt_out: boolean;
  conversacion: Conversacion | null;
}

export interface Mensaje {
  de: "tigo" | "cliente" | "sistema";
  texto: string;
  hora: string;
}

export interface Conversacion {
  cliente_id: string;
  nombre: string;
  telefono: string;
  segmento: string;
  ciudad: string;
  accion: string;
  accion_nombre: string;
  estado: "abierta" | "resuelta" | "escalada";
  resultado: string | null;
  fuente: "claude" | "plantilla";
  guardrails: string;
  mensajes: Mensaje[];
}

export interface Ticket {
  ticket_id: string;
  cliente_id: string;
  nombre: string;
  tipo: string;
  prioridad: Prioridad;
  creado: string;
  resumen: string;
}

/** Versión sin servidor (un solo HTML): las respuestas de la API vienen incrustadas en la página. */
export const ESTATICO = import.meta.env.VITE_ESTATICO === "1";
declare global {
  interface Window {
    __DATOS__?: Record<string, unknown>;
  }
}

function pedirIncrustado<T>(url: string): Promise<T> {
  const v = window.__DATOS__?.[url.replace(/\?$/, "")];
  if (v === undefined) return Promise.reject(new Error("Esta función necesita la versión completa de la demo (iniciar_demo.bat)."));
  return Promise.resolve(structuredClone(v) as T);
}

async function pedir<T>(url: string, init?: RequestInit): Promise<T> {
  if (ESTATICO) return pedirIncrustado<T>(url);
  const r = await fetch(url, init);
  if (!r.ok) {
    let detalle = r.statusText;
    try {
      detalle = (await r.json()).detail ?? detalle;
    } catch {
      /* respuesta sin JSON */
    }
    throw new Error(detalle);
  }
  return r.json() as Promise<T>;
}

const qs = (params: Record<string, string | number | undefined>) => {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => v !== undefined && v !== "" && q.set(k, String(v)));
  return q.toString();
};

export const api = {
  sesion: () => pedir<{ requiere: boolean; activa: boolean }>("/api/sesion"),
  abrirSesion: (token: string) =>
    pedir<{ ok: boolean }>("/api/sesion", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    }),
  salud: () => pedir<Salud>("/api/salud"),
  config: () => pedir<Config>("/api/config"),
  inicio: () => pedir<Inicio>("/api/inicio"),
  mapa: () => pedir<Mapa>("/api/mapa"),
  geojson: () => pedir<FeatureCollection>("/honduras.geojson"),
  falla: () => pedir<EscenarioFalla>("/api/falla/simular"),
  hogar: (caso: "remoto" | "tecnico") => pedir<EscenarioHogar>(`/api/hogar/simular?caso=${caso}`),
  hogarHoy: () => pedir<ListaHoy>("/api/hogar/hoy"),
  pilotoHogar: () => pedir<PilotoHogar>("/api/hogar/piloto"),
  piloto: () => pedir<ResultadosPiloto>("/api/piloto/resultados"),
  potencia: (p: Record<string, number>) => pedir<Potencia>(`/api/piloto/potencia?${qs(p)}`),
  roi: (tus: Record<string, number | undefined>) => pedir<CasoNegocio>(`/api/roi?${qs(tus)}`),
  modelo: () => pedir<ModeloInfo>("/api/modelo"),
  produccion: () => pedir<Produccion>("/api/produccion"),
  // Fase 2
  clientes: (params: Record<string, string | number | undefined>) =>
    pedir<{ total: number; clientes: ClienteResumen[] }>(`/api/clientes?${qs(params)}`),
  cliente: (id: string) => pedir<ClienteDetalle>(`/api/clientes/${id}`),
  ejecutar: (id: string) => pedir<Conversacion>(`/api/clientes/${id}/ejecutar`, { method: "POST" }),
  conversaciones: () => pedir<Conversacion[]>("/api/conversaciones"),
  responder: (id: string, texto: string) =>
    pedir<Conversacion>(`/api/conversaciones/${id}/responder`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto }),
    }),
  tickets: () => pedir<Ticket[]>("/api/tickets"),
};
