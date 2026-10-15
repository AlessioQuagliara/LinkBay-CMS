"""Ponte tra il rule engine puro (app/rules/engine.py) e il database.

A differenza degli altri file di app/rules/, QUESTO modulo può importare Flask e
SQLAlchemy: il suo compito è leggere lo storico da DB, costruire i dataclass che
l'engine si aspetta, e riscrivere il risultato in page_alerts. La logica delle
regole resta interamente in engine.py/filters.py/scoring.py, qui non si decide
nulla — si orchestra soltanto.
"""
from datetime import date

from flask import current_app
from sqlalchemy import extract, func

from app.extensions import db
from app.gsc.page_history import _months_back, get_page_series
from app.models import GscPageMonthly, GscSiteDaily, MonitoredSite, PageAlert
from app.rules.engine import evaluate_site
from app.rules.types import PageSeries, SiteSeries


def _build_site_series(user_id: int, site_url: str, months: int = 16) -> SiteSeries:
    """Costruisce la serie mensile del sito aggregando GscSiteDaily per mese.

    Non serve una tabella site_monthly dedicata: il dato giornaliero esiste già
    ed è sufficiente aggregarlo al volo con una query raggruppata per mese
    (SUM di clicks/impressions, media pesata per impression di ctr/position).
    `extract` è portabile tra PostgreSQL e SQLite.
    """
    cutoff = _months_back(months)[0]
    y = extract("year", GscSiteDaily.date)
    m = extract("month", GscSiteDaily.date)

    rows = (
        db.session.query(
            y.label("y"),
            m.label("m"),
            func.sum(GscSiteDaily.clicks).label("clicks"),
            func.sum(GscSiteDaily.impressions).label("impressions"),
            func.sum(GscSiteDaily.ctr * GscSiteDaily.impressions).label("ctr_weighted"),
            func.sum(GscSiteDaily.position * GscSiteDaily.impressions).label("pos_weighted"),
        )
        .filter(
            GscSiteDaily.user_id == user_id,
            GscSiteDaily.site_url == site_url,
            GscSiteDaily.date >= cutoff,
        )
        .group_by(y, m)
        .order_by(y, m)
        .all()
    )

    monthly = []
    for r in rows:
        impressions = int(r.impressions or 0)
        clicks = int(r.clicks or 0)
        # Media pesata per impression; se un mese non ha impression, resta 0.
        ctr = (float(r.ctr_weighted) / impressions) if impressions else 0.0
        position = (float(r.pos_weighted) / impressions) if impressions else 0.0
        monthly.append({
            "month": date(int(r.y), int(r.m), 1),
            "clicks": clicks,
            "impressions": impressions,
            "ctr": ctr,
            "position": position,
        })
    return SiteSeries(monthly=monthly)


def run_for_site(user_id: int, site_url: str) -> list:
    """Applica le regole a tutte le pagine note del sito e upserta i risultati in
    page_alerts con window_end = mese più recente disponibile. Ritorna la lista
    degli AlertCandidate prodotti in questo run."""
    page_urls = [
        row[0]
        for row in db.session.query(GscPageMonthly.page_url)
        .filter_by(user_id=user_id, site_url=site_url)
        .distinct()
        .all()
    ]
    if not page_urls:
        return []

    site_series = _build_site_series(user_id, site_url)
    pages = [PageSeries(url=p, monthly=get_page_series(user_id, site_url, p, months=16)) for p in page_urls]
    candidates = evaluate_site(pages, site_series)

    # window_end: l'ultimo mese chiuso presente nello storico per pagina.
    window_end = (
        db.session.query(func.max(GscPageMonthly.month))
        .filter_by(user_id=user_id, site_url=site_url)
        .scalar()
    )
    if window_end is None:
        return candidates

    # Carica gli alert già presenti per questa finestra per decidere update vs
    # insert. Gli alert di finestre precedenti (window_end diverso) non vengono
    # toccati: sono storico e restano anche se la pagina non è più in calo.
    existing = {
        a.url: a
        for a in PageAlert.query.filter_by(
            user_id=user_id, site_url=site_url, window_end=window_end
        ).all()
    }

    for c in candidates:
        row = existing.get(c.url)
        if row is None:
            db.session.add(PageAlert(
                user_id=user_id, site_url=site_url, url=c.url, window_end=window_end,
                best_month_clicks=c.best_month_clicks,
                click_loss_abs=c.click_loss_abs,
                click_loss_pct=c.click_loss_pct,
                position_before=c.position_before,
                position_after=c.position_after,
                impressions_trend_pct=c.impressions_trend_pct,
                site_relative_drop_pct=c.site_relative_drop_pct,
                yoy_confirmed=c.yoy_confirmed,
                priority_score=c.priority_score,
                reason_text=c.reason_text,
            ))
        else:
            # Rinfresca i numeri; `status` non si tocca (lo cambia l'utente da UI).
            row.best_month_clicks = c.best_month_clicks
            row.click_loss_abs = c.click_loss_abs
            row.click_loss_pct = c.click_loss_pct
            row.position_before = c.position_before
            row.position_after = c.position_after
            row.impressions_trend_pct = c.impressions_trend_pct
            row.site_relative_drop_pct = c.site_relative_drop_pct
            row.yoy_confirmed = c.yoy_confirmed
            row.priority_score = c.priority_score
            row.reason_text = c.reason_text

    db.session.commit()
    return candidates


def run_weekly() -> dict:
    """Job settimanale: per ogni sito attivamente monitorato, sincronizza lo
    storico mensile per pagina e applica le regole. Un utente/sito che va in
    errore (es. token scaduto) non ferma il job: si logga e si passa al
    prossimo. Da quando esiste il multi-sito (app/models/monitored_site.py),
    itera MonitoredSite invece di GscConnection.monitored_site_url — un
    utente con più siti viene processato una volta per sito."""
    from app.gsc import page_history
    from app.gsc.gsc import get_user_gsc_service
    from app.gsc.repository import credentials_to_dict, save_gsc_credentials
    from app.gsc.sites import touch_last_synced

    sites = MonitoredSite.query.filter_by(is_active=True).all()

    processed = 0
    errors = []
    for row in sites:
        try:
            service, credentials = get_user_gsc_service(row.user_id)
            if service is None:
                errors.append(f"user {row.user_id}: non connesso a GSC")
                continue
            page_history.sync_page_monthly(service, row.user_id, row.site_url)
            save_gsc_credentials(row.user_id, credentials_to_dict(credentials))
            run_for_site(row.user_id, row.site_url)
            touch_last_synced(row.user_id, row.site_url)
            processed += 1
        except Exception as exc:  # noqa: BLE001 — un sito non deve fermare il job
            current_app.logger.exception(
                "run_weekly fallito per user %s (%s)", row.user_id, row.site_url
            )
            # Annulla la transazione fallita, altrimenti il prossimo utente
            # eredita una sessione in stato di errore (Postgres aborta la tx).
            db.session.rollback()
            errors.append(f"user {row.user_id} ({row.site_url}): {exc}")

    return {"processed": processed, "errors": errors}
