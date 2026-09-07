"""Widget di chat pubblico sulla landing (nessun login) — risponde a domande
su piani/prezzi/funzionalità usando DeepSeek + app/chat/knowledge.py.

Endpoint pubblico e non autenticato: niente sessione utile a un CSRF token
di sessione, e nessuna azione con effetti collaterali sui dati (solo lettura
+ una chiamata AI) — esente da CSRF di proposito, non per svista (assenza di
stato da proteggere, non una chiamata esterna firmata).
"""
from flask import Blueprint, current_app, jsonify, request

from app.ai.deepseek import DeepSeekError, chat_reply
from app.chat.knowledge import MAX_HISTORY_MESSAGES, MAX_MESSAGE_CHARS, SYSTEM_PROMPT
from app.extensions import csrf, limiter

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

ALLOWED_ROLES = {"user", "assistant"}


def _clean_history(raw) -> list[dict]:
    """Valida e tronca la cronologia mandata dal client (stateless: nessuna
    persistenza server-side dei messaggi, il client rimanda tutto ad ogni
    turno) — non fidarsi della forma/lunghezza in arrivo, è input pubblico
    non autenticato."""
    if not isinstance(raw, list):
        return []
    cleaned = []
    for item in raw[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in ALLOWED_ROLES or not isinstance(content, str):
            continue
        content = content.strip()[:MAX_MESSAGE_CHARS]
        if content:
            cleaned.append({"role": role, "content": content})
    return cleaned


@chat_bp.route("/ask", methods=["POST"])
@csrf.exempt
@limiter.limit("8 per minute; 60 per hour")
def ask():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()[:MAX_MESSAGE_CHARS]
    if not message:
        return jsonify({"error": "empty_message"}), 400

    history = _clean_history(data.get("history"))
    messages = history + [{"role": "user", "content": message}]

    try:
        reply = chat_reply(SYSTEM_PROMPT, messages)
    except DeepSeekError as e:
        current_app.logger.warning("Chat widget: DeepSeek fallito: %s", e)
        return jsonify({"error": "ai_unavailable"}), 502

    return jsonify({"reply": reply})
