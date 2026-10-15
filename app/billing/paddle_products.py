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

# Piani Pro (abbonamento ricorrente). billing_cycle usa il vocabolario
# dell'API Paddle (interval: day|week|month|year). "price" è il prezzo in euro
# mostrato in /billing/upgrade e nella landing #pricing: non guida alcuna
# logica di attivazione (quella vive nel webhook). "savings_label" è calcolato
# a mano rispetto al mensile (79.90 x 3 = 239.70, x 12 = 958.80) per non
# divergere da quanto comunicato commercialmente.
PADDLE_SUBSCRIPTION_PLANS = {
    "paddle_1m": {
        "label": "1 month", "price": 79.90, "savings_label": None,
        "billing_cycle": {"interval": "month", "frequency": 1},
        "sandbox_env": "PADDLE_SANDBOX_PRICE_ID_1M", "production_env": "PADDLE_PRODUCTION_PRICE_ID_1M",
    },
    "paddle_3m": {
        "label": "3 months", "price": 209.90, "savings_label": "~13%",
        "billing_cycle": {"interval": "month", "frequency": 3},
        "sandbox_env": "PADDLE_SANDBOX_PRICE_ID_3M", "production_env": "PADDLE_PRODUCTION_PRICE_ID_3M",
    },
    "paddle_12m": {
        "label": "12 months", "price": 790.00, "savings_label": "~17%",
        "billing_cycle": {"interval": "year", "frequency": 1},
        "sandbox_env": "PADDLE_SANDBOX_PRICE_ID_12M", "production_env": "PADDLE_PRODUCTION_PRICE_ID_12M",
    },
}


def _credit_package(credits: int, env_suffix: str) -> dict:
    return {
        "label": AI_CREDIT_PACK_LABELS[credits],
        "credits": credits,
        "price": AI_CREDIT_PACKS[credits],
        "sandbox_env": f"PADDLE_SANDBOX_PRICE_ID_AI_TOPUP_{env_suffix}",
        "production_env": f"PADDLE_PRODUCTION_PRICE_ID_AI_TOPUP_{env_suffix}",
    }


# Pacchetti crediti AI one-time: stessi crediti/prezzi di AI_CREDIT_PACKS.
PADDLE_CREDIT_PACKAGES = {
    "ai_topup_starter": _credit_package(50, "STARTER"),
    "ai_topup_growth": _credit_package(150, "GROWTH"),
    "ai_topup_scale": _credit_package(500, "SCALE"),
}


def env_var_for(entry: dict, environment: str) -> str:
    return entry["production_env"] if environment == "production" else entry["sandbox_env"]


def resolve_price_id(catalog: dict, key: str) -> str | None:
    """Price ID configurato per `key` nell'environment corrente, o None se la
    env var non è (ancora) valorizzata — mai un default/placeholder
    hardcoded: il chiamante deve trattare None come "checkout non
    disponibile"."""
    entry = catalog.get(key)
    if entry is None:
        return None
    from app.billing.paddle_client import get_environment

    return current_app.config.get(env_var_for(entry, get_environment())) or None


def reverse_lookup(catalog: dict, price_id: str) -> str | None:
    """Dato un price_id Paddle (dai dati di un webhook, quindi già
    autenticato dalla firma), risale alla chiave interna del catalogo — o None
    se non corrisponde a nessun price_id whitelistato nell'environment
    corrente. Non solleva mai: un price_id sconosciuto è un caso legittimo."""
    for key in catalog:
        if resolve_price_id(catalog, key) == price_id:
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
