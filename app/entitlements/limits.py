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
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=100, ai_credit_topups_allowed=True,
        white_label=False, concurrent_scans=1, api_rate_per_min=30, queue_priority="default",
    ),
    # AppSumo Tier 2 — $149 one-time.
    "appsumo_tier2": PlanLimits(
        name="AppSumo Tier 2",
        site_limit=10, page_limit=8_000, refresh_days=3, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=500, ai_credit_topups_allowed=True,
        white_label=False, concurrent_scans=2, api_rate_per_min=60, queue_priority="default",
    ),
    # AppSumo Tier 3 — $239 one-time.
    "appsumo_tier3": PlanLimits(
        name="AppSumo Tier 3",
        site_limit=50, page_limit=40_000, refresh_days=1, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=1_500, ai_credit_topups_allowed=True,
        white_label=True, concurrent_scans=3, api_rate_per_min=120, queue_priority="high",
    ),
    # Pro Mensile — €79/mese, Lemon Squeezy.
    "subscription_monthly": PlanLimits(
        name="Pro Monthly",
        site_limit=100, page_limit=250_000, refresh_days=1, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=5_000, ai_credit_topups_allowed=False,
        white_label=True, concurrent_scans=5, api_rate_per_min=180, queue_priority="high",
    ),
    # Pro Annuale — €790/anno (~16.7% di sconto vs mensile), stessi limiti tecnici del mensile.
    "subscription_annual": PlanLimits(
        name="Pro Annual",
        site_limit=100, page_limit=250_000, refresh_days=1, export_limit_month=-1,
        ai_mode="credit", ai_cooldown_days=None, ai_credit_grant=5_000, ai_credit_topups_allowed=False,
        white_label=True, concurrent_scans=5, api_rate_per_min=180, queue_priority="high",
    ),
}

DEFAULT_PLAN_TYPE = "trial"

# Prezzi dei pacchetti crediti AI one-time (solo AppSumo — vedi
# ai_credit_topups_allowed). Placeholder di prezzo, non specificati nella
# scheda tecnica: da confermare prima del lancio.
AI_CREDIT_PACKS = {
    500: 19,
    1500: 49,
    5000: 129,
}

# Prezzi/etichette dei piani ricorrenti e one-time, per la UI (pricing landing,
# pagina upgrade, redeem). Fonte unica anche per queste stringhe, invece di
# hardcoderle in più template.
APPSUMO_TIER_PRICES = {
    "appsumo_tier1": 79,
    "appsumo_tier2": 149,
    "appsumo_tier3": 239,
}
PRO_MONTHLY_PRICE = 79
PRO_ANNUAL_PRICE = 790
TRIAL_DAYS = 13
