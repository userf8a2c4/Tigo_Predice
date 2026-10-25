import type { FeatureCollection } from "geojson";
import L from "leaflet";
import { useEffect, useState, type ReactNode } from "react";
import { CircleMarker, GeoJSON, MapContainer, Marker, Tooltip, useMap } from "react-leaflet";
import { api, type Mapa } from "../api";
import { entero } from "../formato";

const LIMITES: L.LatLngBoundsExpression = [
  [12.9, -89.4],
  [16.55, -83.1],
];
const NOMBRE_DEPTO: Record<string, string> = { "Bay Islands": "Islas de la Bahía" };
const ETIQUETAS = ["Tegucigalpa", "San Pedro Sula", "La Ceiba", "Choluteca", "Juticalpa", "Santa Rosa de Copán"];

export const iconoPulso = (color: "rojo" | "verde" = "rojo") =>
  L.divIcon({
    className: "",
    // Contenedor de 24 px (WCAG 2.2, criterio 2.5.8) con el punto de 18 px centrado
    html: `<div style="width:24px;height:24px;display:flex;align-items:center;justify-content:center"><div class="pulso ${color === "verde" ? "pulso-verde" : ""}"></div></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });

/** Encuadra Honduras o vuela a un punto; se reajusta si cambia el tamaño del contenedor. */
function Vista({ centro, zoom, margenSuperior }: { centro?: [number, number]; zoom?: number; margenSuperior: number }) {
  const map = useMap();
  useEffect(() => {
    const ajustar = (animar: boolean) => {
      map.invalidateSize();
      if (centro) map.flyTo(centro, zoom ?? 12, { duration: animar ? 2.5 : 0, animate: animar });
      else map.fitBounds(LIMITES, { paddingTopLeft: [0, margenSuperior], animate: false });
    };
    ajustar(true);
    const obs = new ResizeObserver(() => ajustar(false));
    obs.observe(map.getContainer());
    return () => obs.disconnect();
  }, [map, centro, zoom, margenSuperior]);
  return null;
}

export function MapaBase({
  altura = 420,
  centro,
  zoom,
  margenSuperior = 0,
  children,
}: {
  altura?: number | string;
  centro?: [number, number];
  zoom?: number;
  margenSuperior?: number;
  children?: ReactNode;
}) {
  const [geo, setGeo] = useState<FeatureCollection | null>(null);
  useEffect(() => {
    api
      .geojson()
      .then(setGeo)
      .catch(() => setGeo(null));
  }, []);
  return (
    <div style={{ height: altura }} className="relative">
      <MapContainer bounds={LIMITES} zoomSnap={0.25} scrollWheelZoom={false} attributionControl={false} style={{ height: "100%", width: "100%" }}>
        {geo && (
          <GeoJSON
            data={geo}
            style={{ color: "#ffffff", weight: 1.5, fillColor: "#c9d6e6", fillOpacity: 0.6 }}
            onEachFeature={(f, capa) => {
              const n = (f.properties as { shapeName: string }).shapeName;
              capa.bindTooltip(NOMBRE_DEPTO[n] ?? n, { sticky: true });
            }}
          />
        )}
        <Vista centro={centro} zoom={zoom} margenSuperior={margenSuperior} />
        {children}
      </MapContainer>
    </div>
  );
}

/** Honduras con las ciudades (tamaño = clientes) y las fallas masivas históricas. */
export default function MapaHonduras({ mapa, altura = 420 }: { mapa: Mapa; altura?: number | string }) {
  const max = Math.max(...mapa.ciudades.map((c) => c.clientes));
  const enFalla = new Set(mapa.fallas.flatMap((f) => f.celdas.split(",")));
  return (
    <MapaBase altura={altura}>
      {mapa.celdas
        .filter((c) => enFalla.has(c.celda_id) && !c.falla_activa)
        .map((c) => (
          <CircleMarker key={c.celda_id} center={[c.lat, c.lon]} radius={4} pathOptions={{ color: "#e0303a", weight: 0, fillOpacity: 0.7 }}>
            <Tooltip>Sitio {c.celda_id}: tuvo al menos una falla masiva en 90 días</Tooltip>
          </CircleMarker>
        ))}
      {mapa.ciudades.map((c) => (
        <CircleMarker
          key={c.ciudad}
          center={[c.lat, c.lon]}
          radius={7 + 18 * Math.sqrt(c.clientes / max)}
          pathOptions={{ color: "#00377b", weight: 1.5, fillColor: "#1E5BBF", fillOpacity: 0.25 }}
        >
          <Tooltip direction="top">
            <b>{c.ciudad}</b> · {entero(c.clientes)} clientes en la muestra
          </Tooltip>
        </CircleMarker>
      ))}
      {mapa.ciudades
        .filter((c) => ETIQUETAS.includes(c.ciudad))
        .map((c) => (
          <Marker
            key={`etq-${c.ciudad}`}
            position={[c.lat, c.lon]}
            interactive={false}
            icon={L.divIcon({ className: "etiqueta-ciudad", html: c.ciudad, iconSize: [0, 0], iconAnchor: [-12 - 14 * Math.sqrt(c.clientes / max), 8] })}
          />
        ))}
      {mapa.celdas
        .filter((c) => c.falla_activa)
        .map((c) => (
          // Informativos (la leyenda del mapa los explica): no son controles, así no compiten como objetivos táctiles
          <Marker key={c.celda_id} position={[c.lat, c.lon]} icon={iconoPulso()} interactive={false} keyboard={false}
            title={`Falla masiva activa en el sitio ${c.celda_id}`} />
        ))}
    </MapaBase>
  );
}
