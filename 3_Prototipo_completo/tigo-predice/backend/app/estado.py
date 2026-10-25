"""Estado de Tigo Predice v03.

- Frente Hogar: telemetría de módems, modelo de 7 días, lista de hogares marcados hoy y simulación
  del piloto Hogar (cacheada y determinista). La demo "Hogar en vivo" NO modifica este estado.
- Frente Móvil (fallas masivas): modelo 72 h, perfil de la ciudad piloto y simulación del
  piloto (cacheada y determinista). La demo "Falla en vivo" NO modifica este estado.
- Fase 2 (visión): clientes calificados por churn, acciones y conversaciones de WhatsApp.
  Lo que hace el usuario en Fase 2 vive en memoria y se limpia con `reiniciar()`.
"""

from __future__ import annotations

import json
import threading
from datetime import date, datetime

import pandas as pd
from sqlalchemy import create_engine

from backend.app.llm_client import ClienteLLM
from backend.app.services import acciones, bitacora, chat, mensajes, riesgo, roi
from experimento import simulacion, simulacion_hogar
from ml import features, manifiesto
from ml.comun import CIUDADES, MODELOS_DIR, REPORTES_DIR, cargar_config, supuesto, url_db


class Estado:
    def __init__(self, llm: ClienteLLM | None = None) -> None:
        self.lock = threading.RLock()
        self._demos: dict[tuple, dict] = {}
        self.cfg = cargar_config()
        self.llm = llm or ClienteLLM()
        self.hoy = date.fromisoformat(self.cfg["general"]["fecha_corte"])
        eng = create_engine(url_db())
        self.tablas = features.cargar_tablas(eng)
        feats = pd.read_sql_table("features", eng)
        punt = pd.read_sql_table("puntajes", eng)
        self.hogares = pd.read_sql_table("hogares", eng)
        self.nodos_hogar = pd.read_sql_table("nodos_hogar", eng)
        puntajes_hogar = pd.read_sql_table("puntajes_hogar", eng)
        self.hoy_hogar = (
            pd.read_sql_table("variables_hogar_hoy", eng)
            .merge(pd.read_sql_table("puntajes_hogar_hoy", eng), on="hogar_id")
            .merge(
                self.hogares[["hogar_id", "nombre", "ciudad", "nodo_id", "canal_preferido", "acepta_mensajes"]],
                on="hogar_id",
            )
        )
        eng.dispose()
        clientes = self.tablas["clientes"]
        self.celdas = self.tablas["celdas"]
        self.fallas = self.tablas["fallas_masivas"]

        info = json.loads((MODELOS_DIR / "actual.json").read_text(encoding="utf-8"))
        self.version_modelo = info["version"]
        # Cada modelo se verifica contra su huella SHA-256 antes de cargarse (ml/manifiesto.py)
        self.modelo72 = manifiesto.cargar(info["llamada_72h"])
        self.modelos_fase2 = {k: manifiesto.cargar(info[k]) for k in ("incidencia", "churn")}
        self.metricas_72h = json.loads((REPORTES_DIR / "metricas_72h.json").read_text(encoding="utf-8"))
        self.metricas_fase2 = json.loads((REPORTES_DIR / "metricas.json").read_text(encoding="utf-8"))
        self.modelo_hogar = manifiesto.cargar(info["hogar"])
        self.explicador_hogar = manifiesto.cargar(info["hogar_explicador"])
        self.metricas_hogar = json.loads((REPORTES_DIR / "metricas_hogar.json").read_text(encoding="utf-8"))
        self.roi_base = roi.calcular(self.cfg)

        # ---- Frente Hogar: umbral del presupuesto semanal y simulación del piloto (determinista)
        self.umbral_hogar = float(self.hoy_hogar["p"].quantile(1 - self.cfg["hogar"]["pct_marcados_semana"]))
        self.piloto_hogar = simulacion_hogar.simular(self.cfg, puntajes_hogar, self.metricas_hogar["ia_vs_regla"])

        # ---- Fase 1: perfil de la ciudad piloto y simulación (determinista, se calcula una vez)
        self.perfil_piloto = simulacion.perfil_ciudad(self.tablas, self.cfg, self.cfg["piloto"]["ciudad"])
        self.piloto = simulacion.simular(self.cfg, self.modelo72, self.perfil_piloto)

        # ---- Fase 2: clientes calificados
        repetidas = [c for c in feats.columns if c in clientes.columns and c != "cliente_id"]
        df = clientes.merge(feats.drop(columns=repetidas), on="cliente_id").merge(punt, on="cliente_id")
        df = riesgo.calcular_valor(df, self.cfg)
        self.umbrales = riesgo.umbrales(df, self.cfg)
        df = riesgo.asignar_prioridad(df, self.umbrales)
        df = acciones.asignar(df, self.cfg, self.hoy)
        self._df_base = df.set_index("cliente_id", drop=False)
        self._df_base.index.name = None
        self.reiniciar()

    def demo(self, clave: tuple, calcular):
        """Las demos son deterministas: se calculan una vez (y llaman al LLM una vez) y se reutilizan."""
        with self.lock:
            if clave not in self._demos:
                self._demos[clave] = calcular()
            return self._demos[clave]

    def reiniciar(self) -> None:
        with self.lock:
            self.df = self._df_base.copy()
            self.conversaciones: dict[str, dict] = {}
            self.tickets: list[dict] = []
            self.gasto_compensaciones = 0.0

    def _ahora(self) -> str:
        return datetime.now().strftime("%H:%M")

    # ------------------------------------------------------------------ mapa base
    def mapa(self) -> dict:
        gc = self.tablas["clientes"].groupby("ciudad").size()
        gcel = self.tablas["clientes"].groupby("celda_id").size()
        activas = set()
        for c in self.fallas.loc[self.fallas["estado"] == "activa", "celdas"]:
            activas.update(c.split(","))
        return {
            "ciudades": [
                {"ciudad": n, "departamento": d, "lat": la, "lon": lo, "clientes": int(gc.get(n, 0))}
                for n, d, la, lo, _ in CIUDADES
            ],
            "celdas": [
                {
                    "celda_id": r.celda_id,
                    "ciudad": r.ciudad,
                    "zona": r.zona,
                    "lat": round(r.lat, 4),
                    "lon": round(r.lon, 4),
                    "clientes": int(gcel.get(r.celda_id, 0)),
                    "falla_activa": r.celda_id in activas,
                }
                for r in self.celdas.itertuples()
            ],
            "fallas": self.fallas.astype(object).where(self.fallas.notna(), None).to_dict("records"),
        }

    # ================================================================== FASE 2
    def factores(self, c, cual: str | None = None) -> list[dict]:
        cual = cual or c["riesgo_dominante"]
        return json.loads(c[f"factores_{cual}"] or "[]")

    def _falla_de(self, celda_id: str) -> dict | None:
        act = self.fallas[self.fallas["estado"] == "activa"]
        for _, f in act.iterrows():
            if celda_id in f["celdas"].split(","):
                return {
                    "falla_id": f["falla_id"],
                    "eta_horas": f["eta_horas"],
                    "causa_publica": f["causa"],
                    "ciudad": f["ciudad"],
                }
        return None

    def _resumen(self, c: pd.Series) -> dict:
        cat = acciones.CATALOGO[c["accion"]]
        return {
            "cliente_id": c["cliente_id"],
            "nombre": c["nombre"],
            "telefono": c["telefono"],
            "segmento": c["segmento"],
            "plan": c["plan"],
            "ciudad": c["ciudad"],
            "celda_id": c["celda_id"],
            "arpu": float(c["arpu"]),
            "clv": float(c["clv"]),
            "prob_incidencia": round(float(c["prob_incidencia"]), 4),
            "prob_churn": round(float(c["prob_churn"]), 4),
            "valor_en_riesgo": round(float(c["valor_en_riesgo"]), 2),
            "prioridad": c["prioridad"],
            "riesgo_dominante": c["riesgo_dominante"],
            "factores": self.factores(c),
            "accion": c["accion"],
            "accion_nombre": cat["nombre"],
            "motivo_accion": c["motivo_accion"],
            "contactable": cat["contacta"],
            "humano": cat["humano"],
            "conversacion": c["cliente_id"] in self.conversaciones,
        }

    def listar(
        self, prioridad=None, ciudad=None, segmento=None, accion=None, q=None, limite: int = 50, offset: int = 0
    ) -> dict:
        with self.lock:
            df = self.df
            m = pd.Series(True, index=df.index)
            if prioridad:
                m &= df["prioridad"] == prioridad
            if ciudad:
                m &= df["ciudad"] == ciudad
            if segmento:
                m &= df["segmento"] == segmento
            if accion:
                m &= df["accion"] == accion
            if q:
                q = q.strip()  # búsqueda literal: el texto del usuario nunca se interpreta como regex
                m &= df["nombre"].str.contains(q, case=False, regex=False) | df["cliente_id"].str.contains(
                    q, case=False, regex=False
                )
            sel = df[m].sort_values("valor_en_riesgo", ascending=False)
            return {
                "total": int(len(sel)),
                "clientes": [self._resumen(c) for _, c in sel.iloc[offset : offset + limite].iterrows()],
            }

    def detalle(self, cliente_id: str) -> dict:
        with self.lock:
            c = self.df.loc[cliente_id]
            d = self._resumen(c)
            d["factores_churn"] = self.factores(c, "churn")
            d["factores_incidencia"] = self.factores(c, "incidencia")
            d["variables"] = {v: (None if pd.isna(c[v]) else float(c[v])) for v in features.NUMERICAS}
            d["antiguedad_meses"] = int(c["antiguedad_meses"])
            d["opt_out"] = bool(c["opt_out"])
            d["conversacion"] = self.conversaciones.get(cliente_id)
            return d

    def ejecutar(self, cliente_id: str, usar_llm: bool = True) -> dict:
        with self.lock:
            c = self.df.loc[cliente_id]
            accion = c["accion"]
            cat = acciones.CATALOGO[accion]
            if not cat["contacta"]:
                raise ValueError(f"No se contacta a este cliente: {c['motivo_accion']}")
            falla = self._falla_de(c["celda_id"]) if accion == "aviso_falla" else None
            gb = 0
            if falla is not None:  # compensación solo por falla masiva y con tope
                costo = supuesto(self.cfg, "costo_compensacion")
                if self.gasto_compensaciones + costo <= self.cfg["topes"]["compensaciones_mes_piloto"]:
                    gb = self.cfg["reglas"]["gb_compensacion"]
                    self.gasto_compensaciones += costo
            ctx = mensajes.contexto_mensaje(c.to_dict(), accion, falla, gb)
            msg = mensajes.generar(ctx, self.llm if usar_llm else None)
            bitacora.registrar(cliente_id, accion, msg)
            conv = {
                "cliente_id": cliente_id,
                "nombre": c["nombre"],
                "telefono": c["telefono"],
                "segmento": c["segmento"],
                "ciudad": c["ciudad"],
                "accion": accion,
                "accion_nombre": cat["nombre"],
                "estado": "abierta",
                "paso": 0,
                "resultado": None,
                "ctx": ctx,
                "fuente": msg["fuente"],
                "guardrails": msg["guardrails"],
                "mensajes": [{"de": "tigo", "texto": msg["texto"], "hora": self._ahora()}],
            }
            self.conversaciones[cliente_id] = conv
            self._marcar_contactado([cliente_id])
            if accion == "retencion_agente":
                self._crear_ticket(c, conv, tipo="Llamada saliente de retención")
            return conv

    def _marcar_contactado(self, ids: list[str]) -> None:
        self.df.loc[ids, "ultimo_contacto_proactivo"] = self.hoy.isoformat()
        sub = acciones.asignar(self.df.loc[ids].copy(), self.cfg, self.hoy)
        self.df.loc[ids, "accion"] = sub["accion"].to_numpy()
        self.df.loc[ids, "motivo_accion"] = sub["motivo_accion"].to_numpy()

    def responder(self, cliente_id: str, texto: str) -> dict:
        with self.lock:
            conv = self.conversaciones[cliente_id]
            c = self.df.loc[cliente_id]
            conv["mensajes"].append({"de": "cliente", "texto": texto, "hora": self._ahora()})
            r = chat.responder(conv, chat.detectar_intencion(texto, self.llm), conv["ctx"])
            for t in r["respuestas"]:
                conv["mensajes"].append({"de": "tigo", "texto": t, "hora": self._ahora()})
            conv.update(paso=r["paso"], estado=r["estado"])
            if r["ticket"]:
                t = self._crear_ticket(c, conv)
                conv["mensajes"].append(
                    {
                        "de": "sistema",
                        "texto": f"Ticket {t['ticket_id']} creado con resumen para el agente",
                        "hora": self._ahora(),
                    }
                )
            if r["resultado"] and not conv["resultado"]:
                conv["resultado"] = r["resultado"]
            return conv

    def _crear_ticket(self, c: pd.Series, conv: dict, tipo: str = "Escalamiento desde WhatsApp") -> dict:
        t = {
            "ticket_id": f"T-{len(self.tickets) + 1:04d}",
            "cliente_id": c["cliente_id"],
            "nombre": c["nombre"],
            "tipo": tipo,
            "prioridad": c["prioridad"],
            "creado": self._ahora(),
            "resumen": chat.resumen_ticket(c.to_dict(), conv, self.factores(c)),
        }
        self.tickets.append(t)
        return t
