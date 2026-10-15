"""Client minimale per DeepSeek (API OpenAI-compatibile).

`chat_json` pretende una risposta JSON (`response_format=json_object`), così
il chiamante lavora su un dict; `chat_reply` restituisce testo libero.
Nessuna dipendenza nuova: usa `requests` (già nel progetto).
"""
import json

import requests
from flask import current_app


class DeepSeekError(Exception):
    pass


def _complete(messages: list[dict], *, temperature: float, max_tokens: int, timeout: int, json_mode: bool) -> str:
    api_key = current_app.config.get("DEEPSEEK_API")
    if not api_key:
        raise DeepSeekError("DeepSeek non è configurato (DEEPSEEK_API mancante).")

    base = current_app.config.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    body = {
        "model": current_app.config.get("DEEPSEEK_MODEL", "deepseek-chat"),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    try:
        resp = requests.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=body,
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise DeepSeekError(f"Chiamata DeepSeek fallita: {e}") from e

    if resp.status_code != 200:
        raise DeepSeekError(f"DeepSeek HTTP {resp.status_code}: {resp.text[:200]}")

    try:
        return resp.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as e:
        raise DeepSeekError(f"Risposta DeepSeek non valida: {e}") from e


def chat_json(system: str, user: str) -> dict:
    content = _complete(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.2, max_tokens=4000, timeout=90, json_mode=True,
    )
    try:
        return json.loads(content)
    except ValueError as e:
        raise DeepSeekError(f"Risposta DeepSeek non valida: {e}") from e


def chat_reply(system: str, messages: list[dict]) -> str:
    """Risposta testuale libera per il widget di chat (app/chat/): `messages`
    è la cronologia (ruoli "user"/"assistant"), il chiamante decide quanta
    tenerne (vedi app/chat/routes.py per i limiti anti-abuso)."""
    return _complete(
        [{"role": "system", "content": system}] + messages,
        temperature=0.3, max_tokens=500, timeout=30, json_mode=False,
    ).strip()
