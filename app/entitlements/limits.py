"""Definizione dei limiti tecnici per piano (`User.plan_type`).

Fonte unica di verità per quanto un utente può fare — letta da
app/entitlements/service.py e da ogni punto di enforcement (aggiunta sito,
scan, run AI, export). Numeri allineati alla scheda tecnica ufficiale
"LinkBayCMS — Piani, licenze e billing" (autorevole, sostituisce i
placeholder di una versione precedente di questo file).
"""
from dataclasses import dataclass
from typing import Literal

AiMode = Literal["cooldown", "credit"]
QueuePriority = Literal["high", "default", "low"]


@dataclass(frozen=True)
class PlanLimits:
    name: str
    site_limit: int
    page_limit: int  # somma pagine monitorate su tutti i siti attivi
    refresh_days: int  # intervallo minimo tra un refresh e l'altro (anche manuale)
    export_limit_month: int  # -1 = illimitato, 0 = non disponibile
    ai_mode: AiMode  # "cooldown" = tempo tra un run e l'altro; "credit" = scala dal saldo
    ai_cooldown_days: int | None  # solo per ai_mode == "cooldown"
    ai_credit_grant: int  # crediti accreditati al mese (ai_mode == "credit")
    ai_credit_topups_allowed: bool  # pacchetti one-time acquistabili (solo AppSumo)
    white_label: bool
    concurrent_scans: int
    api_rate_per_min: int
    queue_priority: QueuePriority = "default"


PLAN_LIMITS: dict[str, PlanLimits] = {
    # Trial: prova del piano Pro per intero (13gg, nessuna carta) — stessi
    # limiti di Pro Mensile, non un tier separato. L'AI resta a cooldown (non
    # a crediti): durante un trial non pagato non c'è un evento di billing
    # che possa accreditare una quota mensile.
    "trial": PlanLimits(
        name="Trial (Pro)",
        site_limit=100, page_limit=250_000, refresh_days=1, export_limit_month=-1,
        ai_mode="cooldown", ai_cooldown_days=7, ai_credit_grant=0, ai_credit_topups_allowed=False,
        white_label=True, concurrent_scans=5, api_rate_per_min=180, queue_priority="low",
    ),
    # AppSumo Tier 1 — $79 one-time.
    "appsumo_tier1": PlanLimits(
        name="AppSumo Tier 1",
        site_limit=3, page_limit=1_500, refresh_days=7, export_limit_month=1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=10, ai_credit_topups_allowed=True,
        white_label=False, concurrent_scans=1, api_rate_per_min=30, queue_priority="default",
    ),
    # AppSumo Tier 2 — $149 one-time.
    "appsumo_tier2": PlanLimits(
        name="AppSumo Tier 2",
        site_limit=10, page_limit=8_000, refresh_days=3, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=30, ai_credit_topups_allowed=True,
        white_label=False, concurrent_scans=2, api_rate_per_min=60, queue_priority="default",
    ),
    # AppSumo Tier 3 — $239 one-time.
    "appsumo_tier3": PlanLimits(
        name="AppSumo Tier 3",
        site_limit=50, page_limit=40_000, refresh_days=1, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=75, ai_credit_topups_allowed=True,
        white_label=True, concurrent_scans=3, api_rate_per_min=120, queue_priority="high",
    ),
    # Pro Mensile — legacy Lemon Squeezy, dismesso dal flusso commerciale
    # (vedi app/billing/revolut_manual_activation.py). Voce mantenuta per gli
    # utenti già su questo plan_type: stessi limiti tecnici di sempre, solo
    # non più assegnabile a un nuovo utente.
    "subscription_monthly": PlanLimits(
        name="Pro Monthly (legacy)",
        site_limit=100, page_limit=250_000, refresh_days=1, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=100, ai_credit_topups_allowed=False,
        white_label=True, concurrent_scans=5, api_rate_per_min=180, queue_priority="high",
    ),
    # Pro Annuale — legacy Lemon Squeezy, stessa nota di subscription_monthly.
    "subscription_annual": PlanLimits(
        name="Pro Annual (legacy)",
        site_limit=100, page_limit=250_000, refresh_days=1, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=100, ai_credit_topups_allowed=False,
        white_label=True, concurrent_scans=5, api_rate_per_min=180, queue_priority="high",
    ),
    # Pro via Revolut (link di pagamento manuale, attivazione da Flask-Admin —
    # vedi app/billing/revolut_manual_activation.py). Stessi limiti tecnici
    # del Pro storico: cambia solo come si paga e si attiva, non cosa si
    # ottiene. Tre durate diverse, nessuna differenza di limiti tra loro.
    "revolut_1m": PlanLimits(
        name="Pro — 1 Month (Revolut)",
        site_limit=100, page_limit=250_000, refresh_days=1, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=100, ai_credit_topups_allowed=False,
        white_label=True, concurrent_scans=5, api_rate_per_min=180, queue_priority="high",
    ),
    "revolut_3m": PlanLimits(
        name="Pro — 3 Months (Revolut)",
        site_limit=100, page_limit=250_000, refresh_days=1, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=100, ai_credit_topups_allowed=False,
        white_label=True, concurrent_scans=5, api_rate_per_min=180, queue_priority="high",
    ),
    "revolut_12m": PlanLimits(
        name="Pro — 12 Months (Revolut)",
        site_limit=100, page_limit=250_000, refresh_days=1, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=100, ai_credit_topups_allowed=False,
        white_label=True, concurrent_scans=5, api_rate_per_min=180, queue_priority="high",
    ),
    # Pro via Paddle Billing (checkout server-driven, abbonamento RICORRENTE
    # — a differenza dei piani Revolut sopra, Paddle rinnova da solo a ogni
    # ciclo; vedi app/billing/paddle_subscriptions.py). Stessi identici
    # limiti tecnici dei tre piani Revolut equivalenti: è lo stesso piano
    # Pro, cambia solo processore e meccanica di rinnovo — non un tier
    # diverso, vedi app/billing/paddle_products.py.
    "paddle_1m": PlanLimits(
        name="Pro — Monthly (Paddle)",
        site_limit=100, page_limit=250_000, refresh_days=1, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=100, ai_credit_topups_allowed=False,
        white_label=True, concurrent_scans=5, api_rate_per_min=180, queue_priority="high",
    ),
    "paddle_3m": PlanLimits(
        name="Pro — Quarterly (Paddle)",
        site_limit=100, page_limit=250_000, refresh_days=1, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=100, ai_credit_topups_allowed=False,
        white_label=True, concurrent_scans=5, api_rate_per_min=180, queue_priority="high",
    ),
    "paddle_12m": PlanLimits(
        name="Pro — Annual (Paddle)",
        site_limit=100, page_limit=250_000, refresh_days=1, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=100, ai_credit_topups_allowed=False,
        white_label=True, concurrent_scans=5, api_rate_per_min=180, queue_priority="high",
    ),
}

DEFAULT_PLAN_TYPE = "trial"

# Prezzi dei pacchetti crediti AI one-time (solo AppSumo — vedi
# ai_credit_topups_allowed). Non scadono mai (nessuna logica di expiry nel
# ledger, vedi app/entitlements/ai_credits.py).
AI_CREDIT_PACKS = {
    50: 7,
    150: 15,
    500: 39,
}

# Etichette commerciali dei pacchetti sopra, per la landing /ai-credits e la
# pagina di acquisto — stessa chiave (crediti) di AI_CREDIT_PACKS, un solo
# posto da aggiornare se cambia il naming.
AI_CREDIT_PACK_LABELS = {
    50: "AI Starter",
    150: "AI Growth",
    500: "AI Scale",
}

# Costo in crediti di ogni tipo di azione AI (AI Analyzer, audit presentation).
# Fonte unica per app/audits/service.py e per la tabella "Come funzionano" della
# landing /ai-credits — non duplicare questi numeri altrove.
AI_CREDIT_ACTION_COSTS = {
    "explain": 1,               # spiegazione breve di una pagina
    "suggestion": 2,            # suggerimento operativo dettagliato
    "full_analysis": 3,         # analisi completa di una pagina
    "recovery_plan": 5,         # recovery plan multi-step
    "audit_presentation": 5,    # presentazione reveal.js delle criticità di un sito
    "site_report": 10,          # report AI per sito
    "multi_site_report": 25,    # report AI multi-sito/agency (20-30 crediti)
}

# Prezzi/etichette dei piani, per la UI (pricing landing, pagina upgrade,
# redeem). Fonte unica anche per queste stringhe, invece di hardcoderle in
# più template.
APPSUMO_TIER_PRICES = {
    "appsumo_tier1": 79,
    "appsumo_tier2": 149,
    "appsumo_tier3": 239,
}
# Legacy Lemon Squeezy — non più in vendita, mantenuti solo per il testo
# "Pro — attivo/legacy" mostrato agli utenti già su questi plan_type
# (vedi app/templates/billing/subscription.html).
PRO_MONTHLY_PRICE = 79
PRO_ANNUAL_PRICE = 790
TRIAL_DAYS = 13

# Piani Pro attivabili via Revolut (link di pagamento manuale — vedi
# app/billing/revolut_manual_activation.py). Prezzo in euro come mostrato
# nella pagina /billing/upgrade; durata in giorni per il calcolo scadenza è
# in REVOLUT_PLAN_DAYS dentro il service, non qui (questo dizionario è solo
# per la UI, non guida alcuna logica di attivazione).
REVOLUT_PLAN_PRICES = {
    "revolut_1m": 79.90,
    "revolut_3m": 209.90,
    "revolut_12m": 790.00,
}
# Etichette commerciali "risparmi ~X%" mostrate come badge sulla card,
# calcolate a mano una volta sola rispetto al costo mensile equivalente
# (79.90 x 3 = 239.70, x 12 = 958.80) — non ricalcolate a runtime per
# evitare arrotondamenti diversi da quanto comunicato commercialmente.
REVOLUT_PLAN_SAVINGS_LABEL = {
    "revolut_1m": None,
    "revolut_3m": "~13%",
    "revolut_12m": "~17%",
}
