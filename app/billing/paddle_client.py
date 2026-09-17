"""Client HTTP minimale per Paddle Billing — niente SDK ufficiale: il
progetto è già su `requests` (vedi requirements.txt) e la superficie usata
qui è piccola (creare transazioni, leggere subscription/transazioni, creare
una customer portal session, verificare la firma webhook). Un SDK aggiungerebbe
una dipendenza per poche chiamate REST dirette.

Un solo punto di ingresso per l'environment: `PADDLE_ENVIRONMENT` (sandbox|
production) decide sia il base URL sia — altrove, in app/billing/paddle_products.py
— quale set di price ID viene risolto. Nessuna altra condizione (host, DEBUG,
ecc.) deve mai influenzare questa scelta, per non rischiare di mescolare dati
sandbox e production (vedi docs/paddle-billing.md)."""
from __future__ import annotations

import hashlib
import hmac
import time

import requests
from flask import current_app

SANDBOX_BASE_URL = "https://sandbox-api.paddle.com"
PRODUCTION_BASE_URL = "https://api.paddle.com"

# Tolleranza di freschezza per la verifica della firma webhook (anti-replay).
# Non configurabile via env: è un dettaglio di sicurezza interno, non un
# comportamento di prodotto — vedi verify_webhook_signature.
WEBHOOK_TOLERANCE_SECONDS = 300

REQUEST_TIMEOUT_SECONDS = 15


class PaddleConfigError(Exception):
    """PADDLE_API_KEY mancante, o price ID non risolvibile per l'environment
    corrente — mai un 500 silenzioso, il chiamante lo trasforma in un errore
    applicativo chiaro (vedi app/billing/paddle_routes.py)."""


class PaddleAPIError(Exception):
    """La richiesta a Paddle è arrivata ma ha risposto con un errore
    (4xx/5xx) — il chiamante decide se è recuperabile (mai propagato con lo
    status/body grezzo di Paddle a un utente finale)."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def get_environment() -> str:
    env = (current_app.config.get("PADDLE_ENVIRONMENT") or "sandbox").strip().lower()
    if env not in ("sandbox", "production"):
        # Fail-safe: un valore inatteso non deve mai far cadere silenziosamente
        # in produzione — meglio bloccare con un errore esplicito.
        raise PaddleConfigError(f"PADDLE_ENVIRONMENT non valido: '{env}' (atteso 'sandbox' o 'production').")
    return env


def base_url() -> str:
    return PRODUCTION_BASE_URL if get_environment() == "production" else SANDBOX_BASE_URL


def _api_key() -> str:
    key = current_app.config.get("PADDLE_API_KEY")
    if not key:
        raise PaddleConfigError("PADDLE_API_KEY non configurata.")
    return key


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }


def _request(method: str, path: str, *, json: dict | None = None) -> dict:
    url = f"{base_url()}{path}"
    try:
        response = requests.request(
            method, url, headers=_headers(), json=json, timeout=REQUEST_TIMEOUT_SECONDS
        )
    except requests.RequestException as exc:
        # Non include mai l'header Authorization: solo il metodo/path, per un
        # log utile senza rischiare di stampare la API key negli errori.
        raise PaddleAPIError(f"Errore di rete verso Paddle ({method} {path}): {exc}") from exc

    if response.status_code >= 400:
        # Il body di un errore Paddle non contiene la nostra API key (è
        # un'intestazione, non un campo del payload), quindi è sicuro
        # includerlo nel messaggio per il debug — resta comunque loggato
        # solo lato server, mai restituito as-is all'utente finale.
        raise PaddleAPIError(
            f"Paddle {method} {path} -> {response.status_code}: {response.text[:500]}",
            status_code=response.status_code,
        )
    if not response.content:
        return {}
    return response.json()


def api_request(method: str, path: str, *, json: dict | None = None) -> dict:
    """Wrapper pubblico su _request — usato da app/billing/paddle_catalog_sync.py
    per le chiamate di gestione catalogo (list/create products/prices) che
    non hanno un metodo dedicato qui sopra (create_transaction, ecc.): niente
    da duplicare, lo script del catalogo resta l'unico chiamante di endpoint
    "di setup" invece di aggiungere qui funzioni usate una sola volta."""
    return _request(method, path, json=json)


def create_transaction(*, items: list[dict], custom_data: dict, customer_email: str | None = None,
                        success_url: str | None = None) -> dict:
    """POST /transactions — crea una transazione hosted-checkout. Ritorna il
    body grezzo di Paddle (contiene `id` e, se il checkout è abilitato,
    `checkout.url`). `items` deve già contenere solo price_id whitelistati
    lato server (vedi app/billing/paddle_products.py) — questo client non
    valida nulla, si fida di chi lo chiama."""
    payload: dict = {"items": items, "custom_data": custom_data}
    checkout: dict = {}
    if success_url:
        checkout["url"] = success_url
    if customer_email:
        # Paddle risolve/crea il customer dall'email se non forniamo un
        # customer_id esistente — evitiamo un round-trip separato per
        # cercare un customer_id quando l'utente non ne ha ancora uno.
        payload["customer"] = {"email": customer_email}
    if checkout:
        payload["checkout"] = checkout
    return _request("POST", "/transactions", json=payload)


def get_transaction(transaction_id: str) -> dict:
    return _request("GET", f"/transactions/{transaction_id}")


def get_subscription(subscription_id: str) -> dict:
    return _request("GET", f"/subscriptions/{subscription_id}")


def create_customer_portal_session(customer_id: str) -> dict:
    """POST /customers/{id}/portal-sessions — link "gestisci il mio
    abbonamento" ospitato da Paddle (cambio metodo di pagamento, fatture,
    cancellazione). Non sostituisce la logica di accesso: resta il webhook a
    decidere cosa succede dopo un'azione fatta lì dentro."""
    return _request("POST", f"/customers/{customer_id}/portal-sessions", json={})


def verify_webhook_signature(raw_body: bytes, signature_header: str | None, secret: str | None) -> bool:
    """Verifica l'header `Paddle-Signature: ts=<unix>;h1=<hex hmac-sha256>`
    sul RAW body (mai sul JSON riparsato — un dict Python non ha una
    serializzazione byte-per-byte garantita identica all'originale).

    Include il controllo di freschezza (anti-replay, WEBHOOK_TOLERANCE_SECONDS):
    una firma tecnicamente valida ma con timestamp troppo vecchio è comunque
    rifiutata. Ritorna sempre un bool, non solleva mai — il chiamante decide
    se loggare (senza includere firma/secret nel log, vedi
    app/webhooks/routes.py)."""
    if not secret or not signature_header:
        return False

    parts = {}
    for chunk in signature_header.split(";"):
        if "=" not in chunk:
            continue
        key, _, value = chunk.partition("=")
        parts[key.strip()] = value.strip()

    ts = parts.get("ts")
    h1 = parts.get("h1")
    if not ts or not h1:
        return False

    try:
        ts_int = int(ts)
    except ValueError:
        return False

    if abs(time.time() - ts_int) > WEBHOOK_TOLERANCE_SECONDS:
        return False

    signed_payload = f"{ts}:".encode() + raw_body
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()

    # Confronto a tempo costante — un webhook è un endpoint pubblico, non
    # deve essere possibile indovinare la firma byte per byte via timing.
    return hmac.compare_digest(expected, h1)
