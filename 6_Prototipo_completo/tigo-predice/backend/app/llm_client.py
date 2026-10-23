"""Capa de acceso al LLM (Claude) con caída segura a plantillas.

- Se activa solo si existe ANTHROPIC_API_KEY (en el entorno o en el archivo .env).
- Timeout corto y sin reintentos: si Claude no responde a tiempo, la demo sigue con plantillas.
- Modelo configurable con TIGO_LLM_MODEL (por defecto claude-opus-5-5, esfuerzo bajo).
"""

from __future__ import annotations

import logging
import os

log = logging.getLogger("tigo.llm")

MODELO_DEFECTO = "claude-opus-5-5"


class ClienteLLM:
    def __init__(self) -> None:
        self.modelo = os.getenv("TIGO_LLM_MODEL", MODELO_DEFECTO)
        self.activo = bool(os.getenv("ANTHROPIC_API_KEY")) and os.getenv("TIGO_LLM_DESACTIVADO") != "1"
        self.estado = "Modo plantillas (sin clave de API)" if not self.activo else "sin verificar"
        self._client = None
        if self.activo:
            import anthropic

            self._anthropic = anthropic
            self._client = anthropic.Anthropic(timeout=8.0, max_retries=0)

    @property
    def modo(self) -> str:
        return "IA" if self.activo else "plantillas"

    def verificar(self) -> str:
        """Comprueba al arrancar que la clave y el modelo funcionan (Models API). Nunca lanza excepciones."""
        if not self.activo or self._client is None:
            return self.estado
        a = self._anthropic
        try:
            info = self._client.with_options(timeout=5.0).models.retrieve(self.modelo)
            self.estado = f"Modo IA ({info.id})"
        except a.AuthenticationError:
            self.activo, self.estado = False, "Modo plantillas: clave de API inválida"
        except a.NotFoundError:
            self.activo, self.estado = False, f"Modo plantillas: el modelo {self.modelo} no está disponible"
        except a.PermissionDeniedError:
            self.activo, self.estado = False, "Modo plantillas: la clave no tiene permiso para este modelo"
        except a.APIConnectionError:
            self.activo, self.estado = False, "Modo plantillas: sin conexión a internet"
        except a.APIStatusError as e:
            self.activo, self.estado = False, f"Modo plantillas: error de la API ({e.status_code})"
        log.info("LLM: %s", self.estado)
        return self.estado

    def completar(self, sistema: str, usuario: str, max_tokens: int = 2000) -> str | None:
        """Devuelve el texto de Claude o None si no está disponible / falla / se niega."""
        if not self.activo or self._client is None:
            return None
        a = self._anthropic
        try:
            resp = self._client.beta.messages.create(
                model=self.modelo,
                max_tokens=max_tokens,
                system=sistema,
                messages=[{"role": "user", "content": usuario}],
                output_config={"effort": "low"},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
        except a.AuthenticationError:
            log.warning("ANTHROPIC_API_KEY inválida: se usan plantillas.")
            self.activo = False
            return None
        except a.RateLimitError:
            log.warning("Límite de uso del LLM alcanzado: se usa plantilla.")
            return None
        except a.APIStatusError as e:
            log.warning("Error del LLM (%s): se usa plantilla.", e.status_code)
            return None
        except a.APIConnectionError:  # incluye timeout: sin internet la demo sigue
            log.warning("Sin conexión con el LLM: se usa plantilla.")
            return None
        if resp.stop_reason in ("refusal", "max_tokens"):
            return None
        texto = "".join(b.text for b in resp.content if b.type == "text").strip()
        return texto or None


def cargar_env(ruta) -> None:
    """Carga KEY=VALOR de un archivo .env sin dependencias externas (no pisa variables existentes)."""
    try:
        with open(ruta, encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#") or "=" not in linea:
                    continue
                k, v = linea.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass
