import clsx from "clsx";
import { Bar, BarChart, CartesianGrid, LabelList, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useState } from "react";
import { api, type ModeloInfo } from "../api";
import { Cargando, ErrorCaja, Pestanas, Tarjeta, Titulo, type Frente } from "../components/ui";
import { EJES, GRILLA, SERIES, entero, pct } from "../formato";
import { useAncho, useDatos } from "../hooks";

const ORDEN = ["azar", "regla operativa", "regresión logística", "LightGBM", "LightGBM calibrado"];

export default function Modelo() {
  const { datos, error } = useDatos(api.modelo);
  const [frente, setFrente] = useState<Frente>("hogar");
  if (error) return <ErrorCaja error={error} />;
  if (!datos) return <Cargando />;
  return (
    <div className="space-y-4">
      <Pestanas valor={frente} onCambio={setFrente} />
      {frente === "hogar" ? <ModeloHogar datos={datos} /> : <ModeloMovil datos={datos} />}
    </div>
  );
}

const ORDEN_HOGAR = ["azar", "regla de umbrales", "regresión logística", "LightGBM", "LightGBM calibrado"];

function ModeloHogar({ datos }: { datos: ModeloInfo }) {
  const ancho = useAncho();
  const m = datos.hogar;
  const todos = { ...m.modelos, "regla de umbrales": m.regla_umbrales, azar: m.azar } as Record<string, (typeof m.modelos)[string]>;
  const ia = todos["LightGBM calibrado"];
  const regla = todos["regla de umbrales"];
  const barras = ORDEN_HOGAR.map((k) => ({ nombre: k, valor: Math.round(todos[k].captura_visitas_evitables * 1000) / 10 }));
  const cal = m.calibracion["LightGBM calibrado"].map((c) => ({ ...c, ideal: c.prob_media }));
  const importancia = m.importancia.map((i) => ({ ...i, pct: Math.round(i.valor * 1000) / 10 }));
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 lg:text-3xl">Modelo de IA · Hogar: medido contra la regla de umbrales</h1>
        <p className="text-slate-500">{m.pregunta} · {m.validacion}</p>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.2fr_1fr]">
        <Tarjeta foco="modelo-captura" className="p-4">
          <Titulo>% de las visitas evitables que se anticipan (mismo presupuesto: {pct(m.presupuesto)} de hogares por semana)</Titulo>
          <div className="h-[clamp(220px,34vh,380px)]">
            <ResponsiveContainer>
              <BarChart data={barras} layout="vertical" margin={{ left: 8, right: 48 }}>
                <CartesianGrid stroke={GRILLA} horizontal={false} />
                <XAxis type="number" {...EJES} domain={[0, 100]} tickFormatter={(v: number) => `${v} %`} />
                <YAxis type="category" dataKey="nombre" width={ancho < 640 ? 110 : 150} {...EJES} tick={{ fontSize: ancho < 640 ? 11 : 13, fill: "#334155" }} />
                <Tooltip formatter={(v) => [`${Number(v).toFixed(0)} % de las visitas evitables`, ""]} />
                <Bar isAnimationActive={false} dataKey="valor" fill={SERIES[0]} radius={[0, 4, 4, 0]}>
                  <LabelList dataKey="valor" position="right" fontSize={12} fill="#334155" formatter={(v) => `${Number(v).toFixed(0)} %`} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500">
            Semanas de prueba (validación temporal): {pct(m.tasa_base_prueba, 1)} de hogares llama o necesita visita en 7 días ·{" "}
            {m.visitas_por_1000_prueba.toFixed(0)} visitas por 1,000 hogares · {pct(m.pct_visitas_evitables_prueba)} de las visitas son evitables.
          </p>
        </Tarjeta>

        <Tarjeta className="bg-celeste-50/60 p-5">
          <Titulo>Lectura honesta</Titulo>
          <ul className="list-disc space-y-2 pl-5 text-sm text-slate-700">
            <li>Con el mismo presupuesto, la IA anticipa <b>{pct(ia.captura_visitas_evitables)}</b> de las visitas evitables; la regla de umbrales, <b>{pct(regla.captura_visitas_evitables)}</b>: <b>{m.ia_vs_regla.toFixed(1)}×</b>.</li>
            <li><b>{pct(m.deteccion_temprana)}</b> de las visitas que la IA anticipó todavía no tenían <b>ninguna</b> alarma de umbral: la IA ve tendencias (señal que baja, WiFi que empeora, vecinos con cortes), no solo umbrales.</li>
            <li>Una <b>regresión logística sencilla</b> logra {pct(todos["regresión logística"].captura_visitas_evitables)}: se puede empezar simple y auditable.</li>
            <li>Si con datos reales la IA no supera a la regla por 1.3×, <b>el piloto usa la regla</b>: el producto funciona igual, con menos captura.</li>
            <li>Datos sintéticos: antes del piloto se valida con 3 meses de telemetría real de Tigo (análisis retrospectivo).</li>
          </ul>
        </Tarjeta>
      </div>

      <Tarjeta className="p-5" desplazable="Comparación con el presupuesto semanal">
        <Titulo>Comparación con el presupuesto semanal ({pct(m.presupuesto)} de hogares, ~{ia.marcados_por_semana} marcados por semana en la muestra)</Titulo>
        <table className="w-full min-w-[760px] text-sm">
          <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-500"><th className="pb-2">Estrategia</th><th>AUC</th><th>Precisión</th><th>Captura de eventos</th><th>Captura de visitas evitables</th><th>Visitas por 100 marcados</th></tr></thead>
          <tbody>
            {ORDEN_HOGAR.map((k) => (
              <tr key={k} className={clsx("border-t border-slate-100", k === "LightGBM calibrado" && "bg-celeste-50/60 font-semibold")}>
                <td className="py-2 pr-3 text-slate-800">{k}</td>
                <td className="tabular-nums">{todos[k].auc.toFixed(2)}</td>
                <td className="tabular-nums">{pct(todos[k].precision)}</td>
                <td className="tabular-nums">{pct(todos[k].captura_eventos)}</td>
                <td className="tabular-nums">{pct(todos[k].captura_visitas_evitables)}</td>
                <td className="tabular-nums">{todos[k].visitas_por_100_marcados.toFixed(0)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-2 text-xs text-slate-500">Regla de umbrales: {Object.values(m.umbrales).join(" · ")}. Precisión = % de marcados que llamó o necesitó visita en 7 días.</p>
      </Tarjeta>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Tarjeta className="p-4">
          <Titulo>Qué mira la IA (importancia)</Titulo>
          <div className="h-[clamp(240px,36vh,400px)]">
            <ResponsiveContainer>
              <BarChart data={importancia} layout="vertical" margin={{ left: 8, right: 40 }}>
                <CartesianGrid stroke={GRILLA} horizontal={false} />
                <XAxis type="number" {...EJES} tickFormatter={(v: number) => `${v} %`} />
                <YAxis type="category" dataKey="nombre" width={ancho < 640 ? 120 : 190} {...EJES} tick={{ fontSize: 11, fill: "#334155" }} />
                <Tooltip formatter={(v) => [`${Number(v).toFixed(1)} %`, "Importancia"]} />
                <Bar isAnimationActive={false} dataKey="pct" fill={SERIES[1]} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Tarjeta>

        <Tarjeta className="p-4">
          <Titulo>Calibración</Titulo>
          <div className="h-[clamp(220px,34vh,380px)]">
            <ResponsiveContainer>
              <LineChart data={cal} margin={{ right: 12 }}>
                <CartesianGrid stroke={GRILLA} />
                <XAxis dataKey="prob_media" type="number" domain={[0, 1]} {...EJES} tickFormatter={(v: number) => pct(v)} />
                <YAxis type="number" domain={[0, 1]} {...EJES} width={44} tickFormatter={(v: number) => pct(v)} />
                <Tooltip formatter={(v, n) => [pct(Number(v)), n]} labelFormatter={(v) => `Predicho ${pct(Number(v))}`} />
                <Legend />
                <Line isAnimationActive={false} dataKey="tasa_real" name="Tasa real" stroke={SERIES[0]} strokeWidth={2} dot={{ r: 4 }} />
                <Line isAnimationActive={false} dataKey="ideal" name="Calibración perfecta" stroke="#94a3b8" strokeDasharray="4 4" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500">Brier: LightGBM {todos.LightGBM.brier?.toFixed(4)} → calibrado {ia.brier?.toFixed(4)} (menor es mejor). La mayoría de los hogares tiene riesgo muy bajo.</p>
        </Tarjeta>

        <Tarjeta className="p-4">
          <Titulo>Sesgo: ¿se descuida a algún grupo?</Titulo>
          {(["tecnologia", "zona"] as const).map((dim) => (
            <table key={dim} className="mb-3 w-full text-sm">
              <thead><tr className="text-left text-xs uppercase text-slate-500"><th className="pb-1">{dim === "tecnologia" ? "Tecnología" : "Zona"}</th><th>Tasa real</th><th>% marcado</th><th>Captura</th></tr></thead>
              <tbody>
                {m.sesgo[dim].map((g) => (
                  <tr key={g.grupo} className="border-t border-slate-100">
                    <td className="py-1.5 capitalize">{g.grupo}</td>
                    <td className="tabular-nums">{pct(g.tasa_real, 1)}</td>
                    <td className="tabular-nums">{pct(g.pct_marcado, 1)}</td>
                    <td className="tabular-nums">{pct(g.captura_visitas_evitables)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ))}
          <p className="text-xs text-slate-500">Se marca más donde hay más problemas (HFC, periurbano), en proporción a su tasa real. Captura = % de sus visitas evitables anticipadas.</p>
        </Tarjeta>
      </div>
    </div>
  );
}

function ModeloMovil({ datos }: { datos: ModeloInfo }) {
  const ancho = useAncho();
  const m = datos.fase1;
  const todos = { ...m.modelos, "regla operativa": m.regla_operativa } as Record<string, (typeof m.modelos)[string]>;
  const barras = ORDEN.map((k) => ({
    nombre: k,
    valor: k === "azar" ? m.azar.llamadas_por_100_contactos_top20 : todos[k].llamadas_por_100_contactos_top20,
  }));
  const cal = m.calibracion["LightGBM calibrado"].map((c) => ({ ...c, ideal: c.prob_media }));
  const lift = m.modelos["LightGBM calibrado"].lift;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 lg:text-3xl">Modelo de IA · Móvil (fallas masivas): honesto y medido contra la regla</h1>
        <p className="text-slate-500">{m.pregunta} · {m.validacion}</p>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.2fr_1fr]">
        <Tarjeta className="p-4">
          <Titulo>Llamadas capturadas por cada 100 contactos (presupuesto para el {pct(m.pct_prioridad)} de los afectados)</Titulo>
          <div className="h-[clamp(220px,34vh,380px)]">
            <ResponsiveContainer>
              <BarChart data={barras} layout="vertical" margin={{ left: 8, right: 40 }}>
                <CartesianGrid stroke={GRILLA} horizontal={false} />
                <XAxis type="number" {...EJES} domain={[0, 100]} />
                <YAxis type="category" dataKey="nombre" width={ancho < 640 ? 105 : 150} {...EJES} tick={{ fontSize: ancho < 640 ? 11 : 13, fill: "#334155" }} />
                <Tooltip formatter={(v) => [`${Number(v).toFixed(0)} llamadas por 100 contactos`, ""]} />
                <Bar isAnimationActive={false} dataKey="valor" fill={SERIES[0]} radius={[0, 4, 4, 0]}>
                  <LabelList dataKey="valor" position="right" fontSize={12} fill="#334155" formatter={(v) => Number(v).toFixed(0)} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500">
            En fallas de prueba (validación temporal): tasa base {pct(m.tasa_base_prueba)} · {entero(m.llamadas_por_1000_prueba)} llamadas
            por 1,000 afectados. AUC: regla {todos["regla operativa"].auc.toFixed(2)}, regresión logística{" "}
            {todos["regresión logística"].auc.toFixed(2)}, LightGBM calibrado {todos["LightGBM calibrado"].auc.toFixed(2)}.
          </p>
        </Tarjeta>

        <Tarjeta className="border-l-0 bg-celeste-50/60 p-5">
          <Titulo>Lectura honesta</Titulo>
          <ul className="list-disc space-y-2 pl-5 text-sm text-slate-700">
            <li>Para el <b>aviso por WhatsApp</b> (centavos por mensaje) lo mejor es <b>avisar a TODOS los afectados</b>. No hace falta un modelo para eso.</li>
            <li>El modelo sirve para <b>priorizar acciones caras</b> (compensaciones y llamadas salientes) cuando el presupuesto no alcanza para todos: captura casi el doble de llamadas que elegir al azar y más que la regla «hogar primero».</li>
            <li>Una <b>regresión logística sencilla</b> rinde casi igual que LightGBM: se puede empezar simple.</li>
            <li>Con datos reales del piloto se recalibra. Hoy la muestra de prueba tiene solo 5 fallas.</li>
          </ul>
        </Tarjeta>
      </div>

      <Tarjeta className="p-5" desplazable="Costo-efectividad por estrategia">
        <Titulo>Costo-efectividad por estrategia (supuestos base)</Titulo>
        <table className="w-full min-w-[760px] text-sm">
          <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-500"><th className="pb-2">Estrategia</th><th>Contactos</th><th>Costo</th><th>Llamadas evitadas / capturadas</th><th>Llamadas por 100 contactos</th><th>Costo por llamada</th></tr></thead>
          <tbody>
            {m.estrategias.map((e) => (
              <tr key={String(e.estrategia)} className="border-t border-slate-100">
                <td className="py-2 pr-3 font-medium text-slate-800">{String(e.estrategia)}</td>
                <td className="tabular-nums">{entero(Number(e.contactos))}</td>
                <td className="whitespace-nowrap tabular-nums">L {entero(Number(e.costo))}</td>
                <td className="tabular-nums">{entero(Number(e.llamadas_evitadas ?? e.llamadas_capturadas ?? 0))}</td>
                <td className="tabular-nums">{e.llamadas_por_100 == null ? "—" : Number(e.llamadas_por_100).toFixed(0)}</td>
                <td className="whitespace-nowrap tabular-nums">{(e.costo_por_llamada_evitada ?? e.costo_por_llamada_capturada) == null ? "—" : `L ${Number(e.costo_por_llamada_evitada ?? e.costo_por_llamada_capturada).toFixed(2)}`}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-2 text-xs text-slate-500">Avisar a todos: costo por llamada evitada con la reducción supuesta. Compensar: costo por llamada <i>capturada</i> (clientes que sí iban a llamar).</p>
      </Tarjeta>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Tarjeta className="p-4">
          <Titulo>Calibración</Titulo>
          <div className="h-[clamp(220px,34vh,380px)]">
            <ResponsiveContainer>
              <LineChart data={cal} margin={{ right: 12 }}>
                <CartesianGrid stroke={GRILLA} />
                <XAxis dataKey="prob_media" type="number" domain={[0, 1]} {...EJES} tickFormatter={(v: number) => pct(v)} />
                <YAxis type="number" domain={[0, 1]} {...EJES} width={44} tickFormatter={(v: number) => pct(v)} />
                <Tooltip formatter={(v, n) => [pct(Number(v)), n]} labelFormatter={(v) => `Predicho ${pct(Number(v))}`} />
                <Legend />
                <Line isAnimationActive={false} dataKey="tasa_real" name="Tasa real" stroke={SERIES[0]} strokeWidth={2} dot={{ r: 4 }} />
                <Line isAnimationActive={false} dataKey="ideal" name="Calibración perfecta" stroke="#94a3b8" strokeDasharray="4 4" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500">Brier: LightGBM {todos.LightGBM.brier?.toFixed(3)} → calibrado {todos["LightGBM calibrado"].brier?.toFixed(3)} (menor es mejor).</p>
        </Tarjeta>

        <Tarjeta className="p-4">
          <Titulo>Lift por decil</Titulo>
          <div className="h-[clamp(220px,34vh,380px)]">
            <ResponsiveContainer>
              <BarChart data={lift} margin={{ top: 20, right: 8 }}>
                <CartesianGrid stroke={GRILLA} vertical={false} />
                <XAxis dataKey="decil" {...EJES} tickFormatter={(d) => `D${d}`} />
                <YAxis {...EJES} width={36} />
                <ReferenceLine y={1} stroke="#64748b" strokeDasharray="4 4" />
                <Tooltip formatter={(v) => [`${Number(v).toFixed(2)}×`, "Lift"]} labelFormatter={(d) => `Decil ${d}`} />
                <Bar isAnimationActive={false} dataKey="lift" fill={SERIES[0]} radius={[4, 4, 0, 0]}>
                  <LabelList dataKey="lift" position="top" fontSize={11} fill="#334155" formatter={(v) => `${Number(v).toFixed(1)}×`} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-slate-500">D1 = 10 % de afectados con mayor probabilidad de llamar. Línea punteada = azar.</p>
        </Tarjeta>

        <Tarjeta className="p-4">
          <Titulo>Sesgo: % priorizado vs. tasa real</Titulo>
          {(["zona", "segmento"] as const).map((dim) => (
            <table key={dim} className="mb-3 w-full text-sm">
              <thead><tr className="text-left text-xs uppercase text-slate-500"><th className="pb-1 capitalize">{dim}</th><th>Tasa real</th><th>Prob. media</th><th>% priorizado</th></tr></thead>
              <tbody>
                {m.sesgo[dim].map((g) => (
                  <tr key={g.grupo} className="border-t border-slate-100">
                    <td className="py-1.5 capitalize">{g.grupo}</td>
                    <td className="tabular-nums">{pct(g.tasa_real)}</td>
                    <td className="tabular-nums">{pct(g.prob_media)}</td>
                    <td className="tabular-nums">{pct(g.pct_priorizado)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ))}
          <p className="text-xs text-slate-500">Las zonas rurales no quedan relegadas en el aviso: avisar a todos los afectados es la regla del piloto.</p>
        </Tarjeta>
      </div>

      <Tarjeta className="p-5 text-sm text-slate-600">
        <Titulo>Fase 2 (visión, no entra al caso base)</Titulo>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {Object.entries(datos.fase2).map(([k, v]) => (
            <div key={k} className="rounded-xl border border-slate-200 p-3">
              <div className="font-semibold text-slate-800">{k === "churn" ? "Abandono en 30 días" : "Llamada general en 7 días"}</div>
              <div className="text-xs text-slate-500">{v.descripcion}</div>
              <div className="mt-1">AUC LightGBM <b>{v.auc.toFixed(3)}</b> · regresión logística {v.auc_baseline.toFixed(3)}</div>
            </div>
          ))}
        </div>
      </Tarjeta>
    </div>
  );
}
