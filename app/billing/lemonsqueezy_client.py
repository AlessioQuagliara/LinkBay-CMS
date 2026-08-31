"""Wrapper sottile sulle API REST di Lemon Squeezy (Checkout + webhook).

Un solo punto di ingresso per parlare con Lemon Squeezy, così il resto del
codice (app/billing/routes.py) non tocca mai l'HTTP/JSON:API direttamente.
Nessun SDK dedicato: l'API di Lemon Squeezy è REST/JSON:API semplice, e
`requests` è già una dipendenza del progetto. Stesso stile "thin wrapper" di
app/emails/__init__.py e app/ai/deepseek.py: legge la config dell'app al
momento della chiamata, non a import-time.
"""
import hashlib
import hmac

import requests
from flask import current_app, url_for

from app.billing.products import variant_id_for

API_BASE = "https://api.lemonsqueezy.com/v1"


def _headers():
    return {
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
        "Authorization": f"Bearer {current_app.config['LEMONSQUEEZY_API_KEY']}",
    }


def create_checkout_url(user, product_key: str = "pro_monthly"):
    """Crea una Checkout Session Lemon Squeezy per `product_key` (vedi
    app/billing/products.py::PRODUCT_CATALOG — piano ricorrente o pacchetto
    crediti one-time). Ritorna l'URL hosted a cui reindirizzare il browser.

    `custom.user_id` torna intatto nel webhook (meta.custom_data): è così che
    colleghiamo l'ordine/abbonamento creato su Lemon Squeezy al nostro User.
    `custom.product_key` è necessario in più per gli acquisti one-time (i
    pacchetti crediti): un evento order_created non porta contesto di
    abbonamento, quindi senza questo il webhook non saprebbe cosa è stato
    comprato."""
    payload = {
        "data": {
            "type": "checkouts",
            "attributes": {
                "checkout_data": {
                    "email": user.email,
                    "custom": {"user_id": str(user.id), "product_key": product_key},
                },
                "product_options": {
                    "redirect_url": url_for("billing.success", _external=True),
                },
            },
            "relationships": {
                "store": {
                    "data": {"type": "stores", "id": str(current_app.config["LEMONSQUEEZY_STORE_ID"])}
                },
                "variant": {
                    "data": {"type": "variants", "id": variant_id_for(product_key)}
                },
            },
        }
    }
    resp = requests.post(f"{API_BASE}/checkouts", headers=_headers(), json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()["data"]["attributes"]["url"]


def get_customer_portal_url(ls_subscription_id):
    """Recupera al volo l'URL del customer portal ospitato da Lemon Squeezy
    per un abbonamento esistente (nessuna cache: evita URL scaduti)."""
    resp = requests.get(f"{API_BASE}/subscriptions/{ls_subscription_id}", headers=_headers(), timeout=10)
    resp.raise_for_status()
    return resp.json()["data"]["attributes"]["urls"]["customer_portal"]


def verify_webhook_signature(payload, signature_header):
    """Lemon Squeezy firma il corpo raw della richiesta con HMAC-SHA256
    (header X-Signature, hex digest) usando il webhook signing secret."""
    secret = current_app.config["LEMONSQUEEZY_WEBHOOK_SECRET"].encode()
    digest = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature_header or "")
