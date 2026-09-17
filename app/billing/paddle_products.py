"""Catalogo whitelist server-side per Paddle Billing — stesso spirito di
app/billing/revolut_products.py: fonte unica per i checkout route
(app/billing/paddle_routes.py), il webhook (app/webhooks/routes.py, per
risalire dal price_id al piano/pacchetto interno) e lo script di sync
catalogo (app/billing/paddle_catalog_sync.py). Nessun price_id, importo o
piano è mai inventato qui: i numeri vengono SEMPRE da
app/entitlements/limits.py (REVOLUT_PLAN_PRICES, AI_CREDIT_PACKS), la stessa
fonte già usata dal flusso Revolut — Paddle vende esattamente lo stesso
prodotto, solo con un processore di pagamento diverso.

Due cataloghi distinti, stessa forma:
- PADDLE_SUBSCRIPTION_PLANS: abbonamento RICORRENTE (Paddle rinnova da solo
  a ogni ciclo — diverso dal piano Revolut a termine, che non si rinnova mai
  da solo). Stesso prezzo/durata del ciclo di REVOLUT_PLAN_PRICES: un piano
  "3 mesi" diventa un abbonamento fatturato ogni 3 mesi (non tre fatture
  mensili), un piano "12 mesi" un abbonamento fatturato annualmente. Stessi
  limiti tecnici del corrispondente piano Revolut (vedi
  app/entitlements/limits.py::PLAN_LIMITS) — è lo stesso piano Pro, cambia
  solo come si paga e si rinnova.
- PADDLE_CREDIT_PACKAGES: vendita one-time, stessa chiave/crediti/prezzo di
  app/billing/revolut_products.py::AI_TOPUP_CATALOG (product_key condiviso
  di proposito: lo stesso pacchetto ha lo stesso nome interno qualunque sia
  il processore, così il ledger AiCreditTransaction.product_key resta
  leggibile senza doversi chiedere quale flusso l'ha creato)."""
from flask import current_app

from app.entitlements.limits import AI_CREDIT_PACK_LABELS, AI_CREDIT_PACKS, REVOLUT_PLAN_PRICES

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
# Stessa fonte prezzo di REVOLUT_PLAN_PRICES — un piano Paddle "paddle_Xm" e
# il suo equivalente Revolut "revolut_Xm" costano sempre lo stesso.
PADDLE_PLAN_PRICE_SOURCE = {
    "paddle_1m": "revolut_1m",
    "paddle_3m": "revolut_3m",
    "paddle_12m": "revolut_12m",
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
        "price": REVOLUT_PLAN_PRICES[PADDLE_PLAN_PRICE_SOURCE[key]],
        "billing_cycle": PADDLE_PLAN_BILLING_CYCLE[key],
        "sandbox_env": PADDLE_PLAN_SANDBOX_ENV[key],
        "production_env": PADDLE_PLAN_PRODUCTION_ENV[key],
    }
    for key in PADDLE_PLAN_BILLING_CYCLE
}

# --- Pacchetti crediti AI (one-time) ----------------------------------------

# Stesse chiavi/crediti di app/billing/revolut_products.py::AI_TOPUP_CREDITS
# — deliberatamente condivise (vedi docstring del modulo).
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
    disponibile", stessa convenzione delle CTA Revolut disabilitate."""
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
    """Le card mostrate in /billing/upgrade accanto a quelle Revolut — stessa
    forma di revolut_products.py::revolut_pro_plans()."""
    return [
        {
            "plan": key,
            "label": entry["label"],
            "price": entry["price"],
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
