"""Aggregazione dei dati Search Console per la vista dashboard.

Trasforma le righe grezze dell'API searchanalytics in una struttura pronta per
la UI: totali di sito (con delta vs periodo precedente), dettaglio per pagina
(con un rating di salute 1-5) e le query principali. Tenuto separato da
app/gsc/gsc.py, che resta responsabile solo di OAuth e delle route.
"""
from datetime import date, timedelta

DEFAULT_DAYS = 28


def _query(service, site_url, start, end, dimensions, row_limit=1000):
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "rowLimit": row_limit,
    }
    if dimensions:
        body["dimensions"] = dimensions
    return service.searchanalytics().query(siteUrl=site_url, body=body).execute().get("rows", [])


def _totals(rows):
    # Con dimensions=[] l'API restituisce una sola riga aggregata (senza "keys").
    if not rows:
        return {"clicks": 0, "impressions": 0, "ctr": 0.0, "position": 0.0}
    r = rows[0]
    return {
        "clicks": r.get("clicks", 0),
        "impressions": r.get("impressions", 0),
        "ctr": r.get("ctr", 0.0),
        "position": r.get("position", 0.0),
    }


def _pct_delta(current, previous):
    """Variazione percentuale; None quando non calcolabile (nessuno storico)."""
    if previous == 0:
        return None if current == 0 else 100.0
    return (current - previous) / previous * 100.0


def _health_stars(clicks_delta_pct):
    """Rating 1-5 basato sul calo di click: 5 = stabile/in crescita, 1 = crollo.
    Coerente con la promessa del prodotto (trovare le pagine che perdono
    traffico): meno stelle = più urgente da guardare."""
    if clicks_delta_pct is None:
        return 3
    if clicks_delta_pct >= -5:
        return 5
    if clicks_delta_pct >= -20:
        return 4
    if clicks_delta_pct >= -40:
        return 3
    if clicks_delta_pct >= -60:
        return 2
    return 1


def build_insights(service, site_url, days=DEFAULT_DAYS):
    today = date.today()
    # Search Console ha ~2-3 giorni di ritardo: chiudiamo la finestra a ieri
    # per non confrontare periodi con dati ancora incompleti.
    end = today - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)

    cur = _totals(_query(service, site_url, start, end, []))
    prev = _totals(_query(service, site_url, prev_start, prev_end, []))

    overview = {
        "range": {"start": start.isoformat(), "end": end.isoformat(), "days": days},
        "clicks": {"value": cur["clicks"], "delta_pct": _pct_delta(cur["clicks"], prev["clicks"])},
        "impressions": {"value": cur["impressions"], "delta_pct": _pct_delta(cur["impressions"], prev["impressions"])},
        "ctr": {"value": cur["ctr"], "delta_pct": _pct_delta(cur["ctr"], prev["ctr"])},
        # position: più basso è meglio (lower_is_better gestito lato UI).
        "position": {"value": cur["position"], "delta_pct": _pct_delta(cur["position"], prev["position"])},
    }

    cur_pages = {r["keys"][0]: r for r in _query(service, site_url, start, end, ["page"])}
    prev_pages = {r["keys"][0]: r for r in _query(service, site_url, prev_start, prev_end, ["page"])}

    pages = []
    for url, r in cur_pages.items():
        prev_clicks = prev_pages.get(url, {}).get("clicks", 0)
        delta_pct = _pct_delta(r.get("clicks", 0), prev_clicks)
        pages.append({
            "url": url,
            "clicks": r.get("clicks", 0),
            "impressions": r.get("impressions", 0),
            "ctr": r.get("ctr", 0.0),
            "position": r.get("position", 0.0),
            "clicks_prev": prev_clicks,
            "clicks_delta_pct": delta_pct,
            "stars": _health_stars(delta_pct),
        })
    # Le pagine più in sofferenza (calo maggiore) per prime.
    pages.sort(key=lambda p: (p["clicks_delta_pct"] if p["clicks_delta_pct"] is not None else 0))

    queries = [
        {
            "query": r["keys"][0],
            "clicks": r.get("clicks", 0),
            "impressions": r.get("impressions", 0),
            "ctr": r.get("ctr", 0.0),
            "position": r.get("position", 0.0),
        }
        for r in _query(service, site_url, start, end, ["query"], row_limit=50)
    ]

    return {"overview": overview, "pages": pages[:100], "queries": queries}
