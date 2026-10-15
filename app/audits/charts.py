"""Dati e markup SVG dei grafici nelle Audit Presentation — SOLO numeri già
calcolati dal rule engine (PageAlert, vedi app/rules/) e dallo storico
Search Console (GscSiteDaily), mai inventati né ricalcolati con una formula
nuova. `priority_score` e la soglia "priorità alta" restano quelli di
app/rules/scoring.py (nessuna seconda formula di scoring introdotta qui).

`compute_chart_data` produce un dict JSON-serializzabile, salvato su
AuditPresentation.chart_data (vedi app/audits/service.py) così la
presentazione resta riproducibile esattamente come generata, anche se i dati
sorgente cambiano dopo o il rule engine viene ritarato. Le funzioni render_*
leggono SOLO quel dict già salvato — mai una nuova query — e producono SVG
inline con escaping di ogni valore che potrebbe contenere testo/URL non
fidato.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from urllib.parse import urlsplit

from markupsafe import Markup, escape

from app.extensions import db
from app.models import GscSiteDaily, PageAlert

TREND_WINDOW_DAYS = 60
MIN_TREND_DAYS = 14  # sotto questa soglia il trend non è abbastanza leggibile
MAX_CHART_PAGES = 5  # "top 5" richiesto per i bar chart
# Soglia "priorità alta" — la stessa di app/rules/scoring.py::_priority_label
# (score >= 66 => "alta"), non una nuova formula introdotta qui.
HIGH_PRIORITY_THRESHOLD = 66

BRAND_RED = "#ff5758"
BRAND_GRAY = "#9aa0a6"
BRAND_GRAY_LIGHT = "#e7e7ea"


# --- Fase 1: costruzione dati (query + aggregazioni, nessun rendering) -----


def _sanitize_url_label(url: str, max_len: int = 42) -> str:
    """URL abbreviato per le etichette dei grafici: solo path (+ query se
    breve), troncato. Ritorna testo semplice — l'escaping per l'SVG avviene
    a valle, in chi costruisce il markup."""
    try:
        parsed = urlsplit(url)
        label = (parsed.path or "/") + (f"?{parsed.query}" if parsed.query else "")
    except ValueError:
        label = url
    if not label:
        label = url
    if len(label) > max_len:
        label = label[: max_len - 1] + "…"
    return label


def _trend_series(user_id: int, site_url: str) -> dict | None:
    since = date.today() - timedelta(days=TREND_WINDOW_DAYS)
    rows = (
        GscSiteDaily.query.filter(
            GscSiteDaily.user_id == user_id,
            GscSiteDaily.site_url == site_url,
            GscSiteDaily.date >= since,
        )
        .order_by(GscSiteDaily.date.asc())
        .all()
    )
    if len(rows) < MIN_TREND_DAYS:
        return None

    midpoint = len(rows) // 2
    previous_half, recent_half = rows[:midpoint], rows[midpoint:]

    return {
        "points": [
            {"date": r.date.isoformat(), "clicks": r.clicks, "impressions": r.impressions}
            for r in rows
        ],
        "range_start": rows[0].date.isoformat(),
        "range_end": rows[-1].date.isoformat(),
        "previous_period_clicks": sum(r.clicks for r in previous_half),
        "recent_period_clicks": sum(r.clicks for r in recent_half),
    }


def _declining_pages_series(alerts: list[PageAlert]) -> list[dict]:
    ranked = sorted(alerts, key=lambda a: (a.click_loss_abs or 0), reverse=True)[:MAX_CHART_PAGES]
    return [
        {
            "label": _sanitize_url_label(a.url),
            "click_loss_abs": a.click_loss_abs or 0,
            "click_loss_pct": None if a.click_loss_pct is None else round(a.click_loss_pct, 1),
        }
        for a in ranked
    ]


def _priority_series(alerts: list[PageAlert]) -> list[dict]:
    ranked = sorted(alerts, key=lambda a: (a.priority_score or 0), reverse=True)[:MAX_CHART_PAGES]
    return [
        {
            "label": _sanitize_url_label(a.url),
            "priority_score": None if a.priority_score is None else round(a.priority_score, 1),
        }
        for a in ranked
    ]


def compute_chart_data(user_id: int, site_url: str, alerts: list[PageAlert]) -> dict:
    """`alerts` è la stessa lista già interrogata da
    app/audits/service.py::build_presentation (_top_alerts, già filtrata su
    status new/acknowledged e limitata a MAX_PAGES) — non ri-querata qui, gli
    stessi identici alert usati per le slide di testo alimentano anche i
    grafici delle pagine/priorità."""
    active = PageAlert.active(user_id, site_url)
    total_alerts = active.count()
    total_click_loss = active.with_entities(db.func.coalesce(db.func.sum(PageAlert.click_loss_abs), 0)).scalar()
    high_priority_count = sum(1 for a in alerts if (a.priority_score or 0) >= HIGH_PRIORITY_THRESHOLD)

    return {
        "version": 1,
        "trend": _trend_series(user_id, site_url),
        "declining_pages": _declining_pages_series(alerts),
        "priority": _priority_series(alerts),
        "kpi": {
            "declining_pages_total": total_alerts,
            "click_loss_total": abs(total_click_loss),
            "high_priority_count": high_priority_count,
        },
    }


# --- Fase 2: rendering SVG/HTML (solo dal dict già salvato) -----------------


def _fmt_date(iso: str) -> str:
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b %Y")


def _fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def render_trend_section(trend: dict | None) -> str:
    """Line chart SVG dei clic organici nel periodo, con confronto testuale
    periodo precedente/recente. Section title always present; se `trend` è
    None (storico insufficiente) mostra il fallback dichiarato, non genera
    un grafico vuoto o inventato."""
    if not trend:
        return (
            "<section class='chart-slide'><h2>Traffic trend</h2>"
            "<p class='chart-fallback'>Not enough daily history yet to draw a trend chart.</p>"
            "</section>"
        )

    points = trend["points"]
    width, height = 760, 300
    pad_left, pad_right, pad_top, pad_bottom = 50, 20, 20, 30
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    clicks = [p["clicks"] for p in points]
    impressions = [p["impressions"] for p in points]
    has_impressions = any(impressions)
    y_max = max(clicks + (impressions if has_impressions else [])) or 1

    n = len(points)

    def _xy(i, value):
        x = pad_left + (plot_w * i / max(1, n - 1))
        y = pad_top + plot_h - (plot_h * value / y_max)
        return x, y

    clicks_path = " ".join(f"{x:.1f},{y:.1f}" for x, y in (_xy(i, p["clicks"]) for i, p in enumerate(points)))
    impressions_path = (
        " ".join(f"{x:.1f},{y:.1f}" for x, y in (_xy(i, p["impressions"]) for i, p in enumerate(points)))
        if has_impressions
        else None
    )

    delta = trend["recent_period_clicks"] - trend["previous_period_clicks"]
    delta_pct = None
    if trend["previous_period_clicks"] > 0:
        delta_pct = round(delta / trend["previous_period_clicks"] * 100, 1)
    delta_label = f"{'+' if delta >= 0 else ''}{_fmt_int(delta)} clicks"
    if delta_pct is not None:
        delta_label += f" ({'+' if delta_pct >= 0 else ''}{delta_pct}%)"
    delta_class = "chart-delta-up" if delta >= 0 else "chart-delta-down"

    legend = (
        f"<span class='chart-legend-item'><span class='chart-swatch' style='background:{BRAND_RED}'></span>Clicks</span>"
    )
    impressions_line = ""
    if has_impressions:
        impressions_line = (
            f"<polyline points='{escape(impressions_path)}' fill='none' "
            f"stroke='{BRAND_GRAY}' stroke-width='2' stroke-dasharray='4,4' />"
        )
        legend += (
            f"<span class='chart-legend-item'><span class='chart-swatch' style='background:{BRAND_GRAY}'></span>Impressions</span>"
        )

    svg = (
        f"<svg viewBox='0 0 {width} {height}' role='img' aria-labelledby='trend-title trend-desc' "
        f"class='chart-svg'>"
        f"<title id='trend-title'>Organic clicks trend</title>"
        f"<desc id='trend-desc'>Line chart of daily organic clicks from {escape(_fmt_date(trend['range_start']))} "
        f"to {escape(_fmt_date(trend['range_end']))}, source: Google Search Console.</desc>"
        f"<line x1='{pad_left}' y1='{pad_top + plot_h}' x2='{width - pad_right}' y2='{pad_top + plot_h}' "
        f"stroke='{BRAND_GRAY_LIGHT}' stroke-width='1' />"
        f"{impressions_line}"
        f"<polyline points='{escape(clicks_path)}' fill='none' stroke='{BRAND_RED}' stroke-width='3' "
        f"stroke-linejoin='round' stroke-linecap='round' />"
        f"<text x='{pad_left}' y='{height - 6}' class='chart-axis-label'>{escape(_fmt_date(trend['range_start']))}</text>"
        f"<text x='{width - pad_right}' y='{height - 6}' text-anchor='end' class='chart-axis-label'>{escape(_fmt_date(trend['range_end']))}</text>"
        f"<text x='{pad_left - 8}' y='{pad_top + 4}' text-anchor='end' class='chart-axis-label'>{_fmt_int(y_max)}</text>"
        f"<text x='{pad_left - 8}' y='{pad_top + plot_h}' text-anchor='end' class='chart-axis-label'>0</text>"
        f"</svg>"
    )

    return (
        "<section class='chart-slide'>"
        "<h2>Traffic trend</h2>"
        f"<p class='chart-meta'>{escape(_fmt_date(trend['range_start']))} – {escape(_fmt_date(trend['range_end']))} "
        f"· Source: Google Search Console</p>"
        f"{svg}"
        f"<div class='chart-legend'>{legend}</div>"
        f"<p class='chart-callout {delta_class}'>Recent vs previous period: {escape(delta_label)}</p>"
        "</section>"
    )


def _bar_section(title: str, subtitle: str, items: list[dict], value_key: str, value_max: float, fmt) -> str:
    """Corpo condiviso da declining-pages e priority: bar chart orizzontale,
    una riga per pagina, valore ed etichetta sempre in testo (non solo
    colore) per l'accessibilità."""
    if not items:
        return (
            f"<section class='chart-slide'><h2>{escape(title)}</h2>"
            "<p class='chart-fallback'>Not enough data to build this chart.</p></section>"
        )

    rows = []
    for item in items:
        value = item[value_key] or 0
        pct_width = max(2, round((value / value_max) * 100, 1)) if value_max else 2
        rows.append(
            "<div class='bar-row'>"
            f"<span class='bar-label' title='{escape(item['label'])}'>{escape(item['label'])}</span>"
            "<span class='bar-track'>"
            f"<span class='bar-fill' style='width:{pct_width}%'></span>"
            "</span>"
            f"<span class='bar-value'>{escape(fmt(item))}</span>"
            "</div>"
        )

    return (
        "<section class='chart-slide'>"
        f"<h2>{escape(title)}</h2>"
        f"<p class='chart-meta'>{escape(subtitle)}</p>"
        f"<div class='bar-chart' role='img' aria-label='{escape(title)}'>{''.join(rows)}</div>"
        "</section>"
    )


def render_declining_pages_section(pages: list[dict]) -> str:
    max_loss = max((p["click_loss_abs"] or 0) for p in pages) if pages else 0

    def _fmt(item):
        label = f"-{_fmt_int(item['click_loss_abs'])} clicks"
        if item["click_loss_pct"] is not None:
            label += f" ({item['click_loss_pct']}%)"
        return label

    return _bar_section(
        "Pages losing the most traffic",
        f"Top {len(pages)} declining pages by clicks lost, from the rule engine.",
        pages, "click_loss_abs", max_loss, _fmt,
    )


def render_priority_section(pages: list[dict]) -> str:
    def _fmt(item):
        return "—" if item["priority_score"] is None else f"{item['priority_score']}/100"

    return _bar_section(
        "Where to act first",
        "Pages ranked by priority score (value, severity, recoverability, demand).",
        pages, "priority_score", 100, _fmt,
    )


def render_kpi_section(kpi: dict) -> str:
    """Slide KPI: numeri, non un chart — nessun valore qui è calcolato da
    questo modulo, sono tutti già presenti in `kpi` (vedi compute_chart_data)."""
    cards = [
        ("Declining pages", _fmt_int(kpi["declining_pages_total"])),
        ("Clicks lost / month", _fmt_int(kpi["click_loss_total"])),
        ("High-priority pages", _fmt_int(kpi["high_priority_count"])),
    ]
    cards_html = "".join(
        f"<div class='kpi-card'><span class='kpi-value'>{escape(value)}</span>"
        f"<span class='kpi-label'>{escape(label)}</span></div>"
        for label, value in cards
    )
    return f"<section class='chart-slide'><h2>At a glance</h2><div class='kpi-grid'>{cards_html}</div></section>"


def render_chart_sections(chart_data: dict | None) -> Markup:
    """Assembla tutte le slide grafico in un unico blocco HTML da inserire
    nel deck reveal.js (vedi app/audits/routes.py). `chart_data` è quello
    salvato su AuditPresentation.chart_data (già un dict, non più una
    stringa JSON) — None per le presentazioni generate prima di questa
    colonna: fallback pulito, nessuna eccezione, nessuna nuova query."""
    if not chart_data:
        return Markup(
            "<section class='chart-slide'><h2>Charts</h2>"
            "<p class='chart-fallback'>Not enough data to generate charts for this presentation.</p>"
            "</section>"
        )

    parts = [
        render_kpi_section(chart_data.get("kpi") or {}),
        render_trend_section(chart_data.get("trend")),
        render_declining_pages_section(chart_data.get("declining_pages") or []),
        render_priority_section(chart_data.get("priority") or []),
    ]
    return Markup("\n".join(parts))
