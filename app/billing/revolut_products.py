"""Catalogo centralizzato dei prodotti pagabili via Revolut Business Payment
Link — fonte unica per landing (#pricing, /ai-credits), /billing/upgrade,
/billing/credits, il form Flask-Admin di accredito top-up e l'email di
conferma. Nessuno di questi template/route reinventa numeri o nomi: leggono
tutti da qui.

Due prodotti commerciali distinti, stesso metodo di pagamento (link statico,
verifica e attivazione manuale da un admin) ma semantica diversa:

- piani Pro (`revolut_pro_plans`): abbonamento a termine, tocca
  subscription_status/subscription_expires_at/plan_type — vedi
  app/billing/revolut_manual_activation.py;
- pacchetti crediti AI (`ai_topup_packages`): vendita una tantum, tocca solo
  il ledger AiCreditTransaction — vedi app/billing/revolut_ai_topup.py. Non
  aggiorna MAI subscription_status/subscription_expires_at/plan_type, non
  sostituisce né declassa l'accesso lifetime AppSumo.

Eleggibilità ai pacchetti AI: non è una proprietà del catalogo (tutti e tre i
pacchetti hanno la stessa regola), ma del piano dell'utente — vedi
app/entitlements/service.py::get_plan_limits(user).ai_credit_topups_allowed
(oggi True solo per i tier AppSumo). Stessa fonte di verità già usata prima
di questa migrazione, non duplicata qui.
"""
from flask import current_app

from app.entitlements.limits import (
    AI_CREDIT_PACK_LABELS,
    AI_CREDIT_PACKS,
    REVOLUT_PLAN_PRICES,
    REVOLUT_PLAN_SAVINGS_LABEL,
)

# --- Piani Pro (abbonamento a termine, pagamento non ricorrente) -----------

REVOLUT_PLAN_LINK_ENV = {
    "revolut_1m": "REVOLUT_PAYMENT_LINK_1M",
    "revolut_3m": "REVOLUT_PAYMENT_LINK_3M",
    "revolut_12m": "REVOLUT_PAYMENT_LINK_12M",
}
REVOLUT_PLAN_LABELS = {
    "revolut_1m": "1 month",
    "revolut_3m": "3 months",
    "revolut_12m": "12 months",
}


def revolut_pro_plans() -> list[dict]:
    """Le tre card mostrate in /billing/upgrade e nella landing #pricing.
    `link` è None se la env var corrispondente non è configurata — i
    template disabilitano la CTA invece di puntare a un placeholder."""
    return [
        {
            "plan": plan,
            "label": REVOLUT_PLAN_LABELS[plan],
            "price": REVOLUT_PLAN_PRICES[plan],
            "savings_label": REVOLUT_PLAN_SAVINGS_LABEL[plan],
            "link": current_app.config.get(env_name) or None,
        }
        for plan, env_name in REVOLUT_PLAN_LINK_ENV.items()
    ]


# --- Pacchetti di credito AI (vendita una tantum) ---------------------------

# Chiave interna stabile, deliberatamente diversa dal vecchio "credits_<amount>"
# Lemon Squeezy (mai riusata, per non confondere storico e nuovo flusso nel
# ledger — vedi app/models/ai_credit_transaction.py::product_key). Numero di
# crediti e prezzo restano quelli di
# app/entitlements/limits.py::AI_CREDIT_PACKS/AI_CREDIT_PACK_LABELS, unica
# fonte di verità per questi numeri: non vengono reinventati qui.
AI_TOPUP_CREDITS = {
    "ai_topup_starter": 50,
    "ai_topup_growth": 150,
    "ai_topup_scale": 500,
}
# Nome della env var determinato dal valore reale già presente nel catalogo
# (il numero di crediti, non l'etichetta commerciale) — stessa convenzione
# del vecchio LEMONSQUEEZY_VARIANT_CREDITS_<amount> che sostituisce.
AI_TOPUP_LINK_ENV = {
    "ai_topup_starter": "REVOLUT_AI_TOPUP_LINK_50",
    "ai_topup_growth": "REVOLUT_AI_TOPUP_LINK_150",
    "ai_topup_scale": "REVOLUT_AI_TOPUP_LINK_500",
}

AI_TOPUP_CATALOG = {
    product_key: {
        "credits": credits,
        "label": AI_CREDIT_PACK_LABELS[credits],
        "price": AI_CREDIT_PACKS[credits],
        "link_env": AI_TOPUP_LINK_ENV[product_key],
    }
    for product_key, credits in AI_TOPUP_CREDITS.items()
}


def ai_topup_packages() -> list[dict]:
    """Le card mostrate in /billing/credits e nella landing /ai-credits, più
    le scelte del SelectField in RevolutAiTopupForm (vedi app/admin/views.py).
    `link` è None se la env var non è configurata, stessa convenzione di
    revolut_pro_plans()."""
    return [
        {
            "product_key": key,
            "label": entry["label"],
            "credits": entry["credits"],
            "price": entry["price"],
            "link": current_app.config.get(entry["link_env"]) or None,
        }
        for key, entry in AI_TOPUP_CATALOG.items()
    ]
