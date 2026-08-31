"""Catalogo prodotti/varianti Lemon Squeezy — un solo punto di verità per
mappare un "product_key" applicativo (usato nel form di checkout e in
meta.custom_data del webhook) al variant ID reale su Lemon Squeezy, e
viceversa. I 5 prodotti vanno creati a mano nella dashboard Lemon Squeezy
(nessun accesso API per crearli da qui) — vedi il piano multi-tier per
nome/prezzo/intervallo esatti di ciascuno."""
from flask import current_app

PRODUCT_CATALOG = {
    "pro_monthly": {
        "variant_env": "LEMONSQUEEZY_VARIANT_PRO_MONTHLY",
        "kind": "plan",
        "plan_type": "subscription_monthly",
        "billing_interval": "monthly",
        "recurring": True,
    },
    "pro_annual": {
        "variant_env": "LEMONSQUEEZY_VARIANT_PRO_ANNUAL",
        "kind": "plan",
        "plan_type": "subscription_annual",
        "billing_interval": "annual",
        "recurring": True,
    },
    "credits_500": {
        "variant_env": "LEMONSQUEEZY_VARIANT_CREDITS_500",
        "kind": "credits",
        "amount": 500,
        "recurring": False,
    },
    "credits_1500": {
        "variant_env": "LEMONSQUEEZY_VARIANT_CREDITS_1500",
        "kind": "credits",
        "amount": 1500,
        "recurring": False,
    },
    "credits_5000": {
        "variant_env": "LEMONSQUEEZY_VARIANT_CREDITS_5000",
        "kind": "credits",
        "amount": 5000,
        "recurring": False,
    },
}

DEFAULT_PRODUCT_KEY = "pro_monthly"


def variant_id_for(product_key: str) -> str:
    """Solleva KeyError se product_key non esiste nel catalogo, ValueError se
    la variante non è stata configurata (env var mancante) — due errori
    distinti: un bug applicativo (chiave sbagliata) vs configurazione
    incompleta (variante non ancora creata su Lemon Squeezy)."""
    entry = PRODUCT_CATALOG[product_key]
    variant_id = current_app.config.get(entry["variant_env"])
    # Fallback deprecato: LEMONSQUEEZY_VARIANT_ID (singolare, pre-esistente)
    # copre "pro_monthly" per un ciclo di deploy, finché non è stata creata
    # la variante dedicata LEMONSQUEEZY_VARIANT_PRO_MONTHLY.
    if not variant_id and product_key == "pro_monthly":
        variant_id = current_app.config.get("LEMONSQUEEZY_VARIANT_ID")
    if not variant_id:
        raise ValueError(f"Variant ID non configurato per '{product_key}' ({entry['variant_env']}).")
    return str(variant_id)


def product_key_for_variant(variant_id: str) -> str | None:
    """Ricerca inversa usata dal webhook: da un variant_id Lemon Squeezy
    risale al product_key applicativo. Letta a runtime dalla config
    dell'app corrente, non cachata — le varianti possono cambiare tra un
    deploy e l'altro."""
    if not variant_id:
        return None
    variant_id = str(variant_id)
    for key, entry in PRODUCT_CATALOG.items():
        configured = current_app.config.get(entry["variant_env"])
        if configured and str(configured) == variant_id:
            return key
    # Stesso fallback deprecato di variant_id_for: se il vecchio
    # LEMONSQUEEZY_VARIANT_ID combacia, trattalo come "pro_monthly".
    legacy = current_app.config.get("LEMONSQUEEZY_VARIANT_ID")
    if legacy and str(legacy) == variant_id:
        return "pro_monthly"
    return None
