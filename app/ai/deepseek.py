"""Client minimale per DeepSeek (API OpenAI-compatibile).

Una sola funzione: manda system+user e pretende una risposta JSON
(`response_format=json_object`), così il chiamante lavora su un dict, non su
testo libero. Nessuna dipendenza nuova: usa `requests` (già nel progetto).
"""
import json

import requests
from flask import current_app


class DeepSeekError(Exception):
    pass


def chat_json(system: str, user: str, temperature: float = 0.2, max_tokens: int = 4000) -> dict:
    api_key = current_app.config.get("DEEPSEEK_API")
    if not api_key:
        raise DeepSeekError("DeepSeek non è configurato (DEEPSEEK_API mancante).")

    base = current_app.config.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = current_app.config.get("DEEPSEEK_MODEL", "deepseek-chat")

    try:
        resp = requests.post(
            f"{base}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "response_format": {"type": "json_object"},
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            },
            timeout=90,
        )
    except requests.RequestException as e:
        raise DeepSeekError(f"Chiamata DeepSeek fallita: {e}") from e

    if resp.status_code != 200:
        raise DeepSeekError(f"DeepSeek HTTP {resp.status_code}: {resp.text[:200]}")

    try:
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except (KeyError, IndexError, ValueError) as e:
        raise DeepSeekError(f"Risposta DeepSeek non valida: {e}") from e
