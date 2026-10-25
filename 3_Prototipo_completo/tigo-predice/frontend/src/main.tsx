import { StrictMode, type ReactNode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, MemoryRouter, Navigate, Route, Routes } from "react-router-dom";
import { ESTATICO } from "./api";
import Layout from "./components/Layout";
import Sesion from "./components/Sesion";
import "./index.css";
import CasoNegocio from "./pages/CasoNegocio";
import Clientes from "./pages/Clientes";
import FallaEnVivo from "./pages/FallaEnVivo";
import HogarEnVivo from "./pages/HogarEnVivo";
import Inicio from "./pages/Inicio";
import Modelo from "./pages/Modelo";
import Piloto from "./pages/Piloto";
import Produccion from "./pages/Produccion";
import WhatsApp from "./pages/WhatsApp";

// Sin servidor (archivo local u hosting estático) las rutas viven en memoria: la barra del navegador muestra solo el
// dominio (o el archivo). Un enlace con # (p. ej. …/#/hogar?final) abre esa pantalla y la dirección queda limpia.
const INICIAL = window.location.hash.replace(/^#/, "") || "/";
if (ESTATICO && window.location.hash) {
  try {
    window.history.replaceState(null, "", window.location.pathname + window.location.search);
  } catch {
    // Algunos navegadores no permiten cambiar la dirección de un archivo local: la demo funciona igual
  }
}

function Router({ children }: { children: ReactNode }) {
  return ESTATICO ? <MemoryRouter initialEntries={[INICIAL]}>{children}</MemoryRouter> : <BrowserRouter>{children}</BrowserRouter>;
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Sesion>
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Inicio />} />
          <Route path="/hogar" element={<HogarEnVivo />} />
          <Route path="/falla" element={<FallaEnVivo />} />
          <Route path="/piloto" element={<Piloto />} />
          <Route path="/negocio" element={<CasoNegocio />} />
          <Route path="/modelo" element={<Modelo />} />
          <Route path="/produccion" element={<Produccion />} />
          <Route path="/clientes" element={<Clientes />} />
          <Route path="/whatsapp" element={<WhatsApp />} />
          <Route path="/demo" element={<Navigate to="/falla" replace />} />
          <Route path="/roi" element={<Navigate to="/negocio" replace />} />
        </Route>
      </Routes>
    </Router>
    </Sesion>
  </StrictMode>,
);
