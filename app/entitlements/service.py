"""Service di entitlement centralizzato: dato un utente, risponde a "quali
limiti si applicano" (get_plan_limits), "quanto ha già usato" (get_usage_summary)
e "può fare ancora questa azione" (i check_*). Ogni punto di enforcement
(aggiunta sito, scan, run AI, export) passa da qui — nessuna logica di limite
duplicata altrove.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from flask import url_for
from werkzeug.routing import BuildError

from app.entitlements.limits import DEFAULT_PLAN_TYPE, PLAN_LIMITS, PlanLimits
from app.extensions import db
from app.models import GscPageMonthly, MonitoredSite, ResourceUsageLog

Level = Literal["ok", "warn_80", "warn_95", "blocked"]


def _safe_url_for(endpoint: str, fallback_endpoint: str) -> str:
    """`billing.credits` (pacchetti crediti AI) nasce in una fase successiva
    del piano multi-tier — finché non esiste, l'upsell ripiega su
    `billing.upgrade` (sempre presente) invece di far esplodere la richiesta
    con un BuildError."""
    try:
        return url_for(endpoint)
    except BuildError:
        return url_for(fallback_endpoint)


def get_plan_limits(user) -> PlanLimits:
    """Non solleva mai eccezioni: un utente con plan_type non ancora
    migrato/valorizzato (NULL, o un valore non più valido) ricade sul piano
    più restrittivo (trial) invece di un errore 500 o un accesso illimitato
    per errore."""
    plan_type = getattr(user, "plan_type", None)
    return PLAN_LIMITS.get(plan_type, PLAN_LIMITS[DEFAULT_PLAN_TYPE])


def _is_appsumo(user) -> bool:
    return bool(user.plan_type) and user.plan_type.startswith("appsumo")


@dataclass(frozen=True)
class UsageSummary:
    sites_used: int
    sites_limit: int
    pages_used: int
    pages_limit: int
    ai_credits_balance: int
    ai_credits_monthly_quota: int
    exports_used_this_month: int
    exports_limit: int


@dataclass(frozen=True)
class LimitCheckResult:
    allowed: bool
    level: Level
    message: str
    upsell: dict | None = None


def _level_for_ratio(used: int, limit: int) -> Level:
    """Soglie 80%/95%/100% condivise da ogni check_*. limit=-1 = illimitato
    (sempre "ok", non esistono soglie da superare)."""
    if limit < 0:
        return "ok"
    if limit == 0:
        return "blocked" if used > 0 else "blocked"
    ratio = used / limit
    if ratio >= 1:
        return "blocked"
    if ratio >= 0.95:
        return "warn_95"
    if ratio >= 0.80:
        return "warn_80"
    return "ok"


def _upsell_for(user) -> dict | None:
    if _is_appsumo(user):
        return {"type": "ai_credits", "url": _safe_url_for("billing.credits", "billing.upgrade")}
    return {"type": "subscription_upgrade", "url": url_for("billing.upgrade")}


def _check_result(user, used: int, limit: int, resource_label: str) -> LimitCheckResult:
    """Corpo comune a check_site_limit/check_page_limit/check_export_limit:
    stessa forma (livello dai numeri, messaggio, upsell se bloccato), cambia
    solo l'etichetta della risorsa."""
    level = _level_for_ratio(used, limit)
    if level == "blocked":
        return LimitCheckResult(
            allowed=False, level=level,
            message=f"You've reached the {resource_label} limit for your plan.",
            upsell=_upsell_for(user),
        )
    message = "" if level == "ok" else f"You're using {used} of {limit} {resource_label}."
    return LimitCheckResult(allowed=True, level=level, message=message)


def _active_site_urls(user_id: int) -> list[str]:
    return [
        row[0] for row in
        db.session.query(MonitoredSite.site_url).filter_by(user_id=user_id, is_active=True).all()
    ]


def _count_active_pages(user_id: int, site_urls: list[str]) -> int:
    if not site_urls:
        return 0
    return (
        db.session.query(GscPageMonthly.page_url, GscPageMonthly.site_url)
        .filter(GscPageMonthly.user_id == user_id, GscPageMonthly.site_url.in_(site_urls))
        .distinct()
        .count()
    )


def _exports_used_this_month(user_id: int) -> int:
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return (
        ResourceUsageLog.query.filter(
            ResourceUsageLog.user_id == user_id,
            ResourceUsageLog.action.in_(("export_csv", "export_pdf")),
            ResourceUsageLog.counted_against_limit.is_(True),
            ResourceUsageLog.created_at >= month_start,
        ).count()
    )


def get_usage_summary(user) -> UsageSummary:
    limits = get_plan_limits(user)
    site_urls = _active_site_urls(user.id)

    return UsageSummary(
        sites_used=len(site_urls),
        sites_limit=limits.site_limit,
        pages_used=_count_active_pages(user.id, site_urls),
        pages_limit=limits.page_limit,
        ai_credits_balance=user.ai_credit_balance,
        ai_credits_monthly_quota=limits.ai_credit_grant,
        exports_used_this_month=_exports_used_this_month(user.id),
        exports_limit=limits.export_limit_month,
    )


def levels_from_usage(usage: UsageSummary) -> dict[str, Level]:
    """Livelli 80/95/100% derivati da un UsageSummary già calcolato — per chi
    (es. la dashboard) deve mostrare più dimensioni insieme e non deve
    rifare le query di check_site_limit/check_page_limit/check_export_limit:
    una sola get_usage_summary invece di quattro round-trip separati."""
    return {
        "sites": _level_for_ratio(usage.sites_used, usage.sites_limit),
        "pages": _level_for_ratio(usage.pages_used, usage.pages_limit),
        "exports": _level_for_ratio(usage.exports_used_this_month, usage.exports_limit),
    }


def check_site_limit(user) -> LimitCheckResult:
    limits = get_plan_limits(user)
    used = len(_active_site_urls(user.id))
    return _check_result(user, used, limits.site_limit, "site")


def check_page_limit(user, site_url: str | None = None) -> LimitCheckResult:
    limits = get_plan_limits(user)
    used = _count_active_pages(user.id, _active_site_urls(user.id))
    return _check_result(user, used, limits.page_limit, "page")


def check_export_limit(user) -> LimitCheckResult:
    limits = get_plan_limits(user)
    used = _exports_used_this_month(user.id)
    return _check_result(user, used, limits.export_limit_month, "export")


def check_ai_credits(user, cost: int = 1) -> LimitCheckResult:
    """Si applica solo ai piani a crediti (ai_mode == 'credit'); il piano
    trial resta a cooldown (freno gestito da
    app/ai/service.py::_cooldown_remaining, invariato). Se il piano non
    consente pacchetti extra (Pro — la quota mensile è già generosa), niente
    upsell verso /billing/credits: non c'è nulla da comprare, si aspetta il
    rinnovo mensile."""
    limits = get_plan_limits(user)
    if limits.ai_mode != "credit":
        return LimitCheckResult(allowed=True, level="ok", message="")
    if user.ai_credit_balance < cost:
        upsell = (
            {"type": "ai_credits", "url": _safe_url_for("billing.credits", "billing.upgrade")}
            if limits.ai_credit_topups_allowed
            else None
        )
        message = (
            "You're out of AI credits."
            if limits.ai_credit_topups_allowed
            else "You've used this month's AI credits. Your quota resets on your next billing cycle."
        )
        return LimitCheckResult(allowed=False, level="blocked", message=message, upsell=upsell)
    level = _level_for_ratio(limits.ai_credit_grant - user.ai_credit_balance, limits.ai_credit_grant) if limits.ai_credit_grant else "ok"
    return LimitCheckResult(allowed=True, level=level, message="")


def record_usage(
    user,
    action: str,
    site_url: str | None = None,
    counted_against_limit: bool = True,
    credits_consumed: int | None = None,
    meta: dict | None = None,
) -> ResourceUsageLog:
    entry = ResourceUsageLog(
        user_id=user.id,
        site_url=site_url,
        action=action,
        counted_against_limit=counted_against_limit,
        credits_consumed=credits_consumed,
        meta=meta,
    )
    db.session.add(entry)
    db.session.commit()
    return entry
