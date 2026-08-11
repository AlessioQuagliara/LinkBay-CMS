"""Orchestrazione del rule engine: applica i filtri in sequenza, calcola gli
score e produce l'AlertCandidate. Nessuna dipendenza da Flask/SQLAlchemy.

L'ordine dei filtri segue il diagramma di ARCHITECTURE.md §9:
relevance -> window averages -> pct_loss -> abs_loss -> persistence ->
seasonality -> site_relative. Ci si ferma al primo filtro fallito.
"""
from app.rules.filters import (
    check_seasonality,
    compute_window_averages,
    passes_abs_loss,
    passes_pct_loss,
    passes_persistence,
    passes_relevance,
    passes_site_relative,
)
from app.rules.scoring import (
    build_reason_text,
    demand_score,
    priority_score,
    recoverability_score,
    severity_score,
    value_score,
)
from app.rules.types import AlertCandidate, PageSeries, SiteSeries, Thresholds


def _window_mean(monthly: list[dict], key: str, window: int, offset: int) -> float:
    """Media di `key` su una finestra di `window` mesi. offset=0 = ultimi mesi,
    offset=1 = i `window` mesi precedenti."""
    end = len(monthly) - offset * window
    start = end - window
    chunk = monthly[start:end]
    return sum(float(m[key]) for m in chunk) / len(chunk) if chunk else 0.0


def evaluate_page(
    series: PageSeries, site: SiteSeries, t: Thresholds = Thresholds()
) -> AlertCandidate | None:
    """Applica i filtri in sequenza; None al primo che fallisce, altrimenti
    l'AlertCandidate completo di score e motivazione."""
    relevance = passes_relevance(series, t)
    if not relevance.passed:
        return None
    best_month_clicks = relevance.data["best_month_clicks"]

    current_avg, previous_avg = compute_window_averages(series, t)
    if current_avg is None:
        return None  # storico insufficiente per la finestra

    pct = passes_pct_loss(current_avg, previous_avg, t)
    if not pct.passed:
        return None
    click_loss_pct = pct.data["click_loss_pct"]

    abs_loss = passes_abs_loss(current_avg, previous_avg, t)
    if not abs_loss.passed:
        return None
    click_loss_abs = abs_loss.data["click_loss_abs"]

    persistence = passes_persistence(series, t)
    if not persistence.passed:
        return None

    seasonality = check_seasonality(series, t)
    if not seasonality.passed:
        return None
    yoy_applicable = seasonality.data.get("yoy_applicable", False)
    yoy_confirmed = seasonality.data.get("yoy_confirmed", False)

    site_relative = passes_site_relative(series, site, t)
    if not site_relative.passed:
        return None
    site_relative_drop_pct = site_relative.data["site_relative_drop_pct"]

    # Superati tutti i filtri: calcola posizioni, domanda e score.
    w = t.window_months
    position_before = _window_mean(series.monthly, "position", w, offset=1)
    position_after = _window_mean(series.monthly, "position", w, offset=0)

    impr_current = _window_mean(series.monthly, "impressions", w, offset=0)
    impr_previous = _window_mean(series.monthly, "impressions", w, offset=1)
    impressions_trend_pct = (
        (impr_current - impr_previous) / impr_previous * 100.0 if impr_previous > 0 else 0.0
    )

    v = value_score(best_month_clicks)
    s = severity_score(click_loss_pct)
    r = recoverability_score(position_before, position_after)
    d = demand_score(impressions_trend_pct)
    score = priority_score(v, s, r, d)

    candidate = AlertCandidate(
        url=series.url,
        best_month_clicks=best_month_clicks,
        click_loss_abs=click_loss_abs,
        click_loss_pct=click_loss_pct,
        position_before=position_before,
        position_after=position_after,
        impressions_trend_pct=impressions_trend_pct,
        site_relative_drop_pct=site_relative_drop_pct,
        yoy_confirmed=yoy_confirmed,
        yoy_applicable=yoy_applicable,
        priority_score=score,
        reason_text="",
    )
    candidate.reason_text = build_reason_text(candidate, window_months=w)
    return candidate


def evaluate_site(
    pages: list[PageSeries], site: SiteSeries, t: Thresholds = Thresholds()
) -> list[AlertCandidate]:
    """Valuta ogni pagina, scarta i None e ordina per priority_score
    decrescente (prima le pagine più importanti da sistemare)."""
    candidates = [c for c in (evaluate_page(p, site, t) for p in pages) if c is not None]
    candidates.sort(key=lambda c: c.priority_score, reverse=True)
    return candidates
