"""La única puerta al modelo de lenguaje (CONTRATO.md, sección 5; D-34 y D-35).

El modelo de lenguaje propone el calce de columnas e interpreta una respuesta; nunca pone números.
`pedir` devuelve `(texto, proveedor)` o `None`, y quien la llama usa entonces la plantilla o la regla:
sin clave, sin internet, con un error del servicio o con una negativa, el demo sigue igual.

Proveedor por `KRYLOV_LENGUAJE`: `claude` (por omisión; el de Render y el del demo) o `groq`, que es
solo para pruebas locales mientras no hay clave de Anthropic. Lo que escribe `groq` nunca se precalcula
ni se rotula como Claude.
"""

from __future__ import annotations

import json
import os
from functools import cache

import anthropic
import httpx

TOPE_S = 8.0
MAX_TOKENS = 2000


def proveedor() -> str:
    return "groq" if os.environ.get("KRYLOV_LENGUAJE", "claude").strip().lower() == "groq" else "claude"


def disponible() -> bool:
    return bool(os.environ.get("GROQ_API_KEY" if proveedor() == "groq" else "ANTHROPIC_API_KEY"))


@cache
def _cliente() -> anthropic.Anthropic:
    return anthropic.Anthropic(timeout=TOPE_S, max_retries=1)


def _pedir_claude(sistema: str, usuario: str, esquema: dict | None) -> str | None:
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
    return next((b.text for b in respuesta.content if b.type == "text"), None)


def _sin_listas_largas(esquema):
    """El esquema sin los `enum` largos (los nombres de columna ya van en el mensaje): el plan gratuito de Groq cuenta tokens."""
    if isinstance(esquema, dict):
        return {k: _sin_listas_largas(v) for k, v in esquema.items() if not (k == "enum" and len(v) > 10)}
    return [_sin_listas_largas(v) for v in esquema] if isinstance(esquema, list) else esquema


def _pedir_groq(sistema: str, usuario: str, esquema: dict | None) -> str | None:
    """Solo pruebas locales: en Render y en el demo responde Claude. API compatible con la de OpenAI, sin SDK."""
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
        return r.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, ValueError):
        return None


def pedir(sistema: str, usuario: str, esquema: dict | None = None) -> tuple[str, str] | None:
    """El texto que escribe el modelo y quién lo escribió, o `None` si no hay modelo que responda."""
    if not disponible():
        return None
    quien = proveedor()
    texto = (_pedir_groq if quien == "groq" else _pedir_claude)(sistema, usuario, esquema)
    return (texto.strip(), quien) if texto and texto.strip() else None
