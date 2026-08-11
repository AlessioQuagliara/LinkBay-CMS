"""Storico mensile per pagina di Search Console salvato su DB.

A differenza di app/gsc/history.py (serie giornaliera a livello di sito), qui
si tiene una riga per (utente, sito, pagina, mese). Il perché di "un mese per
volta con dimensions=['page']", e non per giorno, è in ARCHITECTURE.md §6-7:
le query raggruppate per `page` sono le più costose e il costo cresce con
l'ampiezza dell'intervallo; interrogando un mese alla volta, Google restituisce
già click/impression/CTR/posizione aggregati per quel mese in un'unica chiamata
da massimo 25.000 righe.

Due responsabilità, come in history.py:
  - `sync_page_monthly`: upsert idempotente delle metriche mensili per pagina.
    Alla prima connessione fa backfill di ~16 mesi (quanto GSC conserva), poi
    rinfresca solo il mese corrente e quello appena chiuso (che GSC corregge
    ancora retroattivamente); i mesi più vecchi sono definitivi e non si
    toccano più.
  - `get_page_series`: rilegge dal DB il trend a più mesi di una pagina.
"""
from datetime import date, timedelta

from app.extensions import db
from app.models import GscPageMonthly

BACKFILL_MONTHS = 16  # prima connessione: GSC conserva circa 16 mesi
REFRESH_MONTHS = 2    # sync successivi: solo mese corrente + quello appena chiuso
MAX_ROWS = 25000      # limite righe API per chiamata (dimensions=["page"])


def _month_bounds(d: date) -> tuple[date, date]:
    """Dato un giorno qualsiasi del mese, ritorna (primo giorno, ultimo giorno)
    del mese. L'ultimo giorno è clampato a ieri se `d` cade nel mese corrente:
    GSC ha 2-3 giorni di ritardo e non ha senso chiedere date future."""
    first = d.replace(day=1)
    next_first = (
        first.replace(year=first.year + 1, month=1)
        if first.month == 12
        else first.replace(month=first.month + 1)
    )
    last = next_first - timedelta(days=1)

    yesterday = date.today() - timedelta(days=1)
    if last > yesterday:
        last = yesterday
    return first, last


def _months_back(n: int) -> list[date]:
    """Primi-del-mese degli ultimi `n` mesi (incluso quello corrente), dal più
    vecchio al più recente."""
    anchor = date.today().replace(day=1)
    y, m = anchor.year, anchor.month
    months = []
    for _ in range(n):
        months.append(date(y, m, 1))
        m -= 1
        if m == 0:
            y -= 1
            m = 12
    months.reverse()
    return months


def _query_pages(service, site_url, start, end):
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": ["page"],
        "rowLimit": MAX_ROWS,
    }
    return service.searchanalytics().query(siteUrl=site_url, body=body).execute().get("rows", [])


def sync_page_monthly(service, user_id, site_url):
    """Allinea il DB allo storico mensile per pagina di GSC. Ritorna il numero
    di righe scritte o aggiornate."""
    has_history = (
        db.session.query(GscPageMonthly.id)
        .filter_by(user_id=user_id, site_url=site_url)
        .first()
        is not None
    )
    months = _months_back(BACKFILL_MONTHS if not has_history else REFRESH_MONTHS)

    written = 0
    for first in months:
        month_start, month_end = _month_bounds(first)
        if month_end < month_start:
            continue  # mese non ancora iniziato (es. oggi è il 1°): niente da chiedere

        rows = _query_pages(service, site_url, month_start, month_end)

        # Carica le pagine già presenti per quel mese per decidere update vs insert.
        existing = {
            r.page_url: r
            for r in GscPageMonthly.query.filter(
                GscPageMonthly.user_id == user_id,
                GscPageMonthly.site_url == site_url,
                GscPageMonthly.month == month_start,
            ).all()
        }

        for r in rows:
            page_url = r["keys"][0]
            clicks = int(r.get("clicks", 0))
            impressions = int(r.get("impressions", 0))
            ctr = float(r.get("ctr", 0.0))
            position = float(r.get("position", 0.0))

            row = existing.get(page_url)
            if row is None:
                db.session.add(GscPageMonthly(
                    user_id=user_id, site_url=site_url, page_url=page_url, month=month_start,
                    clicks=clicks, impressions=impressions, ctr=ctr, position=position,
                ))
            else:
                row.clicks = clicks
                row.impressions = impressions
                row.ctr = ctr
                row.position = position
            written += 1

    db.session.commit()
    return written


def get_page_series(user_id, site_url, page_url, months=6):
    """Trend degli ultimi `months` mesi di una pagina, in ordine cronologico
    crescente (per il grafico a 6 mesi in dashboard)."""
    rows = (
        GscPageMonthly.query.filter(
            GscPageMonthly.user_id == user_id,
            GscPageMonthly.site_url == site_url,
            GscPageMonthly.page_url == page_url,
        )
        .order_by(GscPageMonthly.month.desc())
        .limit(months)
        .all()
    )
    rows.reverse()  # da desc+limit (ultimi N) a cronologico crescente
    return [
        {
            "month": r.month.isoformat(),
            "clicks": r.clicks,
            "impressions": r.impressions,
            "ctr": r.ctr,
            "position": r.position,
        }
        for r in rows
    ]
