"""Storico giornaliero Search Console salvato su DB.

Due responsabilità:
  - `sync_site_daily`: scarica le metriche per-giorno (dimensions=["date"]) e le
    fa upsert in GscSiteDaily. Idempotente: rifare il sync aggiorna i giorni,
    non li duplica. Alla prima connessione fa backfill ampio (GSC conserva ~16
    mesi), poi rinfresca solo la coda recente (che GSC può ancora consolidare).
  - `get_site_series`: rilegge dal DB la serie del periodo per il grafico.

I totali/delta dell'overview restano calcolati live in app/gsc/insights.py
(valori esatti dall'API); qui teniamo la serie storica e la persistenza.
"""
from datetime import date, timedelta

from app.extensions import db
from app.models import GscSiteDaily

BACKFILL_DAYS = 480  # prima connessione: prendi più storico possibile
FRESH_DAYS = 5       # sync successivi: rinfresca la coda recente non ancora consolidata
MAX_ROWS = 25000     # limite righe API (dimensions=["date"] resta ben sotto)


def _query_daily(service, site_url, start, end):
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": ["date"],
        "rowLimit": MAX_ROWS,
    }
    return service.searchanalytics().query(siteUrl=site_url, body=body).execute().get("rows", [])


def sync_site_daily(service, user_id, site_url, days):
    """Allinea il DB allo storico GSC per il periodo che serve alla vista."""
    end = date.today() - timedelta(days=1)  # GSC ha ~2-3 giorni di ritardo
    has_history = (
        db.session.query(GscSiteDaily.id)
        .filter_by(user_id=user_id, site_url=site_url)
        .first()
        is not None
    )
    window = BACKFILL_DAYS if not has_history else max(days + FRESH_DAYS, days)
    start = end - timedelta(days=window - 1)

    rows = _query_daily(service, site_url, start, end)

    # Carica i giorni già presenti nel range per decidere update vs insert.
    existing = {
        r.date: r
        for r in GscSiteDaily.query.filter(
            GscSiteDaily.user_id == user_id,
            GscSiteDaily.site_url == site_url,
            GscSiteDaily.date >= start,
            GscSiteDaily.date <= end,
        ).all()
    }

    for r in rows:
        day = date.fromisoformat(r["keys"][0])
        clicks = int(r.get("clicks", 0))
        impressions = int(r.get("impressions", 0))
        ctr = float(r.get("ctr", 0.0))
        position = float(r.get("position", 0.0))

        row = existing.get(day)
        if row is None:
            db.session.add(GscSiteDaily(
                user_id=user_id, site_url=site_url, date=day,
                clicks=clicks, impressions=impressions, ctr=ctr, position=position,
            ))
        else:
            row.clicks = clicks
            row.impressions = impressions
            row.ctr = ctr
            row.position = position

    db.session.commit()


def get_site_series(user_id, site_url, days):
    """Serie giornaliera del periodo (per il grafico andamento click)."""
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    rows = (
        GscSiteDaily.query.filter(
            GscSiteDaily.user_id == user_id,
            GscSiteDaily.site_url == site_url,
            GscSiteDaily.date >= start,
            GscSiteDaily.date <= end,
        )
        .order_by(GscSiteDaily.date.asc())
        .all()
    )
    return [
        {
            "date": r.date.isoformat(),
            "clicks": r.clicks,
            "impressions": r.impressions,
        }
        for r in rows
    ]
