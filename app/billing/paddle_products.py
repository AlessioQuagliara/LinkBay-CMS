"""Catalogo whitelist server-side per Paddle Billing — fonte unica per i
checkout route (app/billing/paddle_routes.py), il webhook
(app/webhooks/routes.py, per risalire dal price_id al piano/pacchetto
interno) e lo script di sync catalogo (app/billing/paddle_catalog_sync.py).
Nessun price_id o price_id è mai inventato qui: i price_id vengono sempre da
.env (popolati da `flask paddle-sync-catalog`), gli importi/etichette sono
definiti qui sotto e in app/entitlements/limits.py (AI_CREDIT_PACKS).

Due cataloghi distinti, stessa forma:
- PADDLE_SUBSCRIPTION_PLANS: abbonamento RICORRENTE (Paddle rinnova da solo
  a ogni ciclo). Un piano "3 mesi" è un abbonamento fatturato ogni 3 mesi
  (non tre fatture mensili), un piano "12 mesi" un abbonamento fatturato
  annualmente. Stessi limiti tecnici per ogni durata (vedi
  app/entitlements/limits.py::PLAN_LIMITS) — è lo stesso piano Pro, cambia
  solo la durata del ciclo di fatturazione.
- PADDLE_CREDIT_PACKAGES: vendita one-time, stessa chiave/crediti/prezzo di
  app/entitlements/limits.py::AI_CREDIT_PACKS (product_key stabile: il
  ledger AiCreditTransaction.product_key resta leggibile nel tempo anche se
  cambiano etichette commerciali)."""
from flask import current_app

from app.entitlements.limits import AI_CREDIT_PACK_LABELS, AI_CREDIT_PACKS

# --- Piani Pro (abbonamento ricorrente) -------------------------------------

# Chiave interna -> (durata del ciclo di fatturazione Paddle, giorni
# equivalenti per PLAN_LIMITS/subscription_expires_at di fallback). billing_cycle
# usa lo stesso vocabolario dell'API Paddle (interval: day|week|month|year).
PADDLE_PLAN_BILLING_CYCLE = {
    "paddle_1m": {"interval": "month", "frequency": 1},
    "paddle_3m": {"interval": "month", "frequency": 3},
    "paddle_12m": {"interval": "year", "frequency": 1},
}
PADDLE_PLAN_LABELS = {
    "paddle_1m": "1 month",
    "paddle_3m": "3 months",
    "paddle_12m": "12 months",
}
# Prezzo in euro mostrato in /billing/upgrade e nella landing #pricing; non
# guida alcuna logica di attivazione (quella vive nel webhook Paddle, vedi
# app/billing/paddle_subscriptions.py).
PADDLE_PLAN_PRICES = {
    "paddle_1m": 79.90,
    "paddle_3m": 209.90,
    "paddle_12m": 790.00,
}
# Etichette commerciali "risparmi ~X%" mostrate come badge sulla card,
# calcolate a mano una volta sola rispetto al costo mensile equivalente
# (79.90 x 3 = 239.70, x 12 = 958.80) — non ricalcolate a runtime per
# evitare arrotondamenti diversi da quanto comunicato commercialmente.
PADDLE_PLAN_SAVINGS_LABEL = {
    "paddle_1m": None,
    "paddle_3m": "~13%",
    "paddle_12m": "~17%",
}
# Env var che contiene il price_id sandbox per ciascun piano (vedi config.py).
PADDLE_PLAN_SANDBOX_ENV = {
    "paddle_1m": "PADDLE_SANDBOX_PRICE_ID_1M",
    "paddle_3m": "PADDLE_SANDBOX_PRICE_ID_3M",
    "paddle_12m": "PADDLE_SANDBOX_PRICE_ID_12M",
}
PADDLE_PLAN_PRODUCTION_ENV = {
    "paddle_1m": "PADDLE_PRODUCTION_PRICE_ID_1M",
    "paddle_3m": "PADDLE_PRODUCTION_PRICE_ID_3M",
    "paddle_12m": "PADDLE_PRODUCTION_PRICE_ID_12M",
}

PADDLE_SUBSCRIPTION_PLANS = {
    key: {
        "label": PADDLE_PLAN_LABELS[key],
        "price": PADDLE_PLAN_PRICES[key],
        "savings_label": PADDLE_PLAN_SAVINGS_LABEL[key],
        "billing_cycle": PADDLE_PLAN_BILLING_CYCLE[key],
        "sandbox_env": PADDLE_PLAN_SANDBOX_ENV[key],
        "production_env": PADDLE_PLAN_PRODUCTION_ENV[key],
    }
    for key in PADDLE_PLAN_BILLING_CYCLE
}

# --- Pacchetti crediti AI (one-time) ----------------------------------------

# Stessi crediti di app/entitlements/limits.py::AI_CREDIT_PACKS.
PADDLE_CREDIT_PACKAGE_CREDITS = {
    "ai_topup_starter": 50,
    "ai_topup_growth": 150,
    "ai_topup_scale": 500,
}
PADDLE_CREDIT_SANDBOX_ENV = {
    "ai_topup_starter": "PADDLE_SANDBOX_PRICE_ID_AI_TOPUP_STARTER",
    "ai_topup_growth": "PADDLE_SANDBOX_PRICE_ID_AI_TOPUP_GROWTH",
    "ai_topup_scale": "PADDLE_SANDBOX_PRICE_ID_AI_TOPUP_SCALE",
}
PADDLE_CREDIT_PRODUCTION_ENV = {
    "ai_topup_starter": "PADDLE_PRODUCTION_PRICE_ID_AI_TOPUP_STARTER",
    "ai_topup_growth": "PADDLE_PRODUCTION_PRICE_ID_AI_TOPUP_GROWTH",
    "ai_topup_scale": "PADDLE_PRODUCTION_PRICE_ID_AI_TOPUP_SCALE",
}

PADDLE_CREDIT_PACKAGES = {
    key: {
        "label": AI_CREDIT_PACK_LABELS[credits],
        "credits": credits,
        "price": AI_CREDIT_PACKS[credits],
        "sandbox_env": PADDLE_CREDIT_SANDBOX_ENV[key],
        "production_env": PADDLE_CREDIT_PRODUCTION_ENV[key],
    }
    for key, credits in PADDLE_CREDIT_PACKAGE_CREDITS.items()
}


def _env_key_for(entry: dict) -> str:
    from app.billing.paddle_client import get_environment

    return entry["production_env"] if get_environment() == "production" else entry["sandbox_env"]


def resolve_price_id(catalog: dict, key: str) -> str | None:
    """Price ID configurato per `key` nell'environment corrente, o None se la
    env var non è (ancora) valorizzata — mai un default/placeholder
    hardcoded: il chiamante deve trattare None come "checkout non
    disponibile"."""
    entry = catalog.get(key)
    if entry is None:
        return None
    return current_app.config.get(_env_key_for(entry)) or None


def reverse_lookup_plan(price_id: str) -> str | None:
    """Dato un price_id Paddle (dai dati di un webhook, quindi già
    autenticato dalla firma), risale alla chiave interna del piano — o None
    se non corrisponde a nessun price_id whitelistato nell'environment
    corrente (es. un price creato a mano nel dashboard Paddle e mai
    registrato qui). Non solleva mai: un price_id sconosciuto è un caso
    legittimo da gestire senza crash (vedi app/billing/paddle_subscriptions.py)."""
    for key in PADDLE_SUBSCRIPTION_PLANS:
        if resolve_price_id(PADDLE_SUBSCRIPTION_PLANS, key) == price_id:
            return key
    return None


def reverse_lookup_credit_package(price_id: str) -> str | None:
    for key in PADDLE_CREDIT_PACKAGES:
        if resolve_price_id(PADDLE_CREDIT_PACKAGES, key) == price_id:
            return key
    return None


def paddle_pro_plans() -> list[dict]:
    """Le card mostrate in /billing/upgrade e nella landing #pricing."""
    return [
        {
            "plan": key,
            "label": entry["label"],
            "price": entry["price"],
            "savings_label": entry["savings_label"],
            "price_id": resolve_price_id(PADDLE_SUBSCRIPTION_PLANS, key),
        }
        for key, entry in PADDLE_SUBSCRIPTION_PLANS.items()
    ]


def paddle_credit_packages() -> list[dict]:
    return [
        {
            "product_key": key,
            "label": entry["label"],
            "credits": entry["credits"],
            "price": entry["price"],
            "price_id": resolve_price_id(PADDLE_CREDIT_PACKAGES, key),
        }
        for key, entry in PADDLE_CREDIT_PACKAGES.items()
    ]
