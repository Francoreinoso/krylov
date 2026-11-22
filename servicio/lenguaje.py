"""La única puerta al modelo de lenguaje (CONTRATO.md, sección 5; D-34 y D-35).

El modelo de lenguaje propone el calce de columnas e interpreta una respuesta; nunca pone números.
`pedir` devuelve un `Escrito` (el texto, el proveedor y el modelo que respondió) o `None`, y quien la
llama usa entonces la plantilla o la regla: sin clave, sin internet, con un error del servicio o con una
negativa, el demo sigue igual.

Proveedor por `KRYLOV_LENGUAJE`: `groq` (el de la API pública en Render desde D-41, con `GROQ_API_KEY`)
o `claude` (por omisión, con `ANTHROPIC_API_KEY`). Cada calce e interpretación dice quién la escribió en
`propuesto_por`, con el modelo que de verdad respondió: lo de un proveedor nunca se rotula con el nombre
de otro. El modo estático solo guarda interpretaciones de Claude (`servicio/exportar_estatico.py`).
"""

from __future__ import annotations

import json
import os
from functools import cache
from typing import NamedTuple

import anthropic
import httpx

TOPE_S = 8.0
MAX_TOKENS = 2000
NOMBRE_DEL_PROVEEDOR = {"claude": "Anthropic", "groq": "Groq"}


class Escrito(NamedTuple):
    texto: str
    proveedor: str          # `claude` o `groq`
    modelo: str             # el identificador del modelo que respondió, según el proveedor


def propuesto_por(escrito: Escrito | None, sin_modelo: str) -> dict:
    """Quién escribió un calce o una interpretación (D-42): el modelo, o `sin_modelo` (la regla, la plantilla o el equipo)."""
    if escrito is None:
        return {"tipo": sin_modelo, "proveedor": None, "modelo": None}
    return {"tipo": "modelo", "proveedor": NOMBRE_DEL_PROVEEDOR[escrito.proveedor], "modelo": escrito.modelo}


def proveedor() -> str:
    return "groq" if os.environ.get("KRYLOV_LENGUAJE", "claude").strip().lower() == "groq" else "claude"


def disponible() -> bool:
    return bool(os.environ.get("GROQ_API_KEY" if proveedor() == "groq" else "ANTHROPIC_API_KEY"))


@cache
def _cliente() -> anthropic.Anthropic:
    return anthropic.Anthropic(timeout=TOPE_S, max_retries=1)


def _pedir_claude(sistema: str, usuario: str, esquema: dict | None) -> tuple[str | None, str] | None:
    config: dict = {"effort": "low"}
    if esquema:
        config["format"] = {"type": "json_schema", "schema": esquema}
    try:
        respuesta = _cliente().beta.messages.create(
            model=os.environ.get("KRYLOV_MODELO_LENGUAJE", "claude-opus-5-5"),
            max_tokens=MAX_TOKENS,
            system=[{"type": "text", "text": sistema, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": usuario}],
            output_config=config,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except (anthropic.APIStatusError, anthropic.APIConnectionError):   # incluye 429, 5xx y el tope de tiempo
        return None
    if respuesta.stop_reason != "end_turn":
        return None
    return next((b.text for b in respuesta.content if b.type == "text"), None), respuesta.model


def _sin_listas_largas(esquema):
    """El esquema sin los `enum` largos (los nombres de columna ya van en el mensaje): el plan gratuito de Groq cuenta tokens."""
    if isinstance(esquema, dict):
        return {k: _sin_listas_largas(v) for k, v in esquema.items() if not (k == "enum" and len(v) > 10)}
    return [_sin_listas_largas(v) for v in esquema] if isinstance(esquema, list) else esquema


def _pedir_groq(sistema: str, usuario: str, esquema: dict | None) -> tuple[str | None, str] | None:
    """Groq, el proveedor de la API pública (D-41). API compatible con la de OpenAI, sin SDK."""
    if esquema:
        sistema += "\n\nResponde solo con un objeto JSON que cumpla este esquema:\n" + json.dumps(
            _sin_listas_largas(esquema), ensure_ascii=False, separators=(",", ":"))
    cuerpo = {
        "model": os.environ.get("KRYLOV_MODELO_GROQ", "openai/gpt-oss-120b"),
        "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}],
        "max_tokens": MAX_TOKENS,
    }
    if esquema:
        cuerpo["response_format"] = {"type": "json_object"}
    try:
        r = httpx.post("https://api.groq.com/openai/v1/chat/completions", json=cuerpo, timeout=TOPE_S,
                       headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"})
        r.raise_for_status()
        cuerpo_r = r.json()
        return cuerpo_r["choices"][0]["message"]["content"], cuerpo_r.get("model") or cuerpo["model"]
    except (httpx.HTTPError, KeyError, IndexError, ValueError):
        return None


def pedir(sistema: str, usuario: str, esquema: dict | None = None) -> Escrito | None:
    """El texto que escribe el modelo, con el proveedor y el modelo que lo escribieron, o `None` si no hay modelo que responda."""
    if not disponible():
        return None
    quien = proveedor()
    respuesta = (_pedir_groq if quien == "groq" else _pedir_claude)(sistema, usuario, esquema)
    if respuesta is None or not (respuesta[0] or "").strip():
        return None
    return Escrito(respuesta[0].strip(), quien, respuesta[1])
