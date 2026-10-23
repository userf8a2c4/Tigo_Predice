import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { Conversacion } from "../api";
import Telefono from "../components/Telefono";
import { Factores, PrioridadBadge } from "../components/ui";
import { colorRiesgo, lempiras, lempirasCorto, lempirasSig, pct, pctRiesgo, rangoL, sig } from "../formato";

describe("redondeo sin falsa precisión", () => {
  it("redondea a 2 cifras significativas", () => {
    expect(sig(5_123_456)).toBe(5_100_000);
    expect(sig(0.0876)).toBeCloseTo(0.088);
    expect(sig(0)).toBe(0);
  });

  it("formatea Lempiras como lo hace el backend", () => {
    expect(lempirasSig(5_123_456)).toBe("L 5.1 M");
    expect(lempirasSig(-1_480_000)).toBe("−L 1.5 M");
    expect(lempirasSig(523_000)).toBe("L 520 mil");
  });

  it("muestra rangos ordenados", () => {
    expect(rangoL(15_000_000, -1_500_000)).toBe("−L 1.5 M a L 15 M");
  });
});

describe("formato", () => {
  it("formatea Lempiras para Honduras", () => {
    expect(lempiras(7583.4)).toBe("L 7,583");
    expect(lempirasCorto(22_169_700)).toBe("L 22.2 M");
    expect(pct(0.355)).toBe("36 %");
    expect(pctRiesgo(1)).toBe("> 99 %");
    expect(pctRiesgo(0.001)).toBe("< 1 %");
    expect(pctRiesgo(0.131)).toBe("13 %");
  });

  it("la escala de riesgo va de claro a oscuro", () => {
    const luz = (c: string) => c.match(/\d+/g)!.map(Number).reduce((a, b) => a + b, 0);
    expect(luz(colorRiesgo(0))).toBeGreaterThan(luz(colorRiesgo(0.25)));
  });
});

describe("componentes", () => {
  it("muestra la prioridad y las explicaciones de la IA", () => {
    render(
      <>
        <PrioridadBadge p="Alta" />
        <Factores factores={[{ variable: "dias_atraso", grupo: "Facturación", texto: "Pago atrasado 12 días", impacto: 0.4 }]} />
      </>,
    );
    expect(screen.getByText("Alta")).toBeInTheDocument();
    expect(screen.getByText("Pago atrasado 12 días")).toBeInTheDocument();
  });

  it("el teléfono muestra la conversación y el resultado", () => {
    const conv: Conversacion = {
      cliente_id: "C1",
      nombre: "María López",
      telefono: "+504 9***-1234",
      segmento: "hogar",
      ciudad: "San Pedro Sula",
      accion: "aviso_falla",
      accion_nombre: "Aviso",
      estado: "resuelta",
      resultado: "llamada_evitada",
      fuente: "plantilla",
      guardrails: "aprobado",
      mensajes: [
        { de: "tigo", texto: "Hola María, hay una falla en su zona.", hora: "10:00" },
        { de: "cliente", texto: "Gracias por avisar", hora: "10:01" },
      ],
    };
    render(<Telefono conv={conv} />);
    expect(screen.getByText("Gracias por avisar")).toBeInTheDocument();
    expect(screen.getByText("✅ Llamada evitada")).toBeInTheDocument();
  });
});
