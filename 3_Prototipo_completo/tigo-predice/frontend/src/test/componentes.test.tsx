import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { Conversacion } from "../api";
import Telefono from "../components/Telefono";
import { Factores, PrioridadBadge } from "../components/ui";
import guion from "../../../docs/pitch.md?raw";
import { DURACION_TOTAL, ESCENAS, reloj, subtituloEn, SUBTITULO_MAX_SEG } from "../escenas";
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

describe("modo presentación", () => {
  it("cabe en los 5 minutos del concurso, con margen", () => {
    expect(DURACION_TOTAL).toBeLessThanOrEqual(285);
    expect(reloj(DURACION_TOTAL)).toBe("4:32");
  });

  it("deja a la demo en vivo el tiempo que dura (~77 s a 1×)", () => {
    expect(ESCENAS.find((e) => e.id === "demo")?.seg).toBeGreaterThanOrEqual(78);
  });
});

describe("escenas de la presentación", () => {
  it("cada escena abre una pantalla que existe en el sistema", () => {
    const rutas = ["/", "/hogar", "/falla", "/piloto", "/negocio", "/modelo", "/produccion"];
    for (const e of ESCENAS) expect(rutas).toContain(e.ruta.split("?")[0]);
  });

  it("la demo en vivo corre en Hogar en vivo, después de presentar a Karla", () => {
    const k = ESCENAS.findIndex((e) => e.id === "karla");
    const d = ESCENAS.findIndex((e) => e.id === "demo");
    expect(d).toBeGreaterThan(k);
    expect(ESCENAS[d].ruta).toBe("/hogar");
  });
});

describe("subtítulos de la presentación", () => {
  it("dicen lo mismo que el guion (docs/pitch.md)", () => {
    const plano = (s: string) => s.replace(/\s+/g, " ");
    const texto = plano(guion);
    for (const e of ESCENAS)
      for (const [, linea] of e.subtitulos) expect(texto).toContain(plano(linea.replace(/^…|…$/g, "")));
  });

  it("cada escena tiene subtítulos ordenados y dentro de su duración", () => {
    for (const e of ESCENAS) {
      expect(e.subtitulos.length).toBeGreaterThan(0);
      const inicios = e.subtitulos.map(([t]) => t);
      expect([...inicios].sort((a, b) => a - b)).toEqual(inicios);
      expect(inicios[inicios.length - 1]).toBeLessThan(e.seg);
    }
  });

  it("se pueden leer: como máximo unos 17 caracteres por segundo en pantalla", () => {
    for (const e of ESCENAS)
      e.subtitulos.forEach(([inicio, linea], k) => {
        const fin = Math.min(k + 1 < e.subtitulos.length ? e.subtitulos[k + 1][0] : e.seg, inicio + SUBTITULO_MAX_SEG);
        expect(linea.length / (fin - inicio)).toBeLessThanOrEqual(17);
      });
  });

  it("muestran la frase que corresponde a cada momento", () => {
    const karla = ESCENAS.find((e) => e.id === "karla")!;
    expect(subtituloEn(karla, 0)).toBe(karla.subtitulos[0][1]);
    expect(subtituloEn(karla, 9)).toBe(karla.subtitulos[2][1]);
    const demo = ESCENAS.find((e) => e.id === "demo")!;
    expect(subtituloEn(demo, 0.5)).toBeNull(); // antes de la primera frase
    expect(subtituloEn(demo, 66)).toBeNull(); // pausa larga: el subtítulo se retira a los 8 s
  });
});
