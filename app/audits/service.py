"""Generazione dell'Audit Presentation: parte SEMPRE dai page_alerts già
calcolati dal rule engine (stessi numeri di Declining Pages/Insights, mai
ricalcolati o inventati) e chiede a DeepSeek solo di trasformarli in slide
JSON (titolo + bullet). Il markdown reveal.js finale è assemblato in modo
deterministico in Python da quel JSON — l'AI non scrive mai il markdown
grezzo, così i separatori di slide e la struttura sono sempre corretti e i
numeri restano esattamente quelli osservati."""
import json
from datetime import date, datetime, timezone

from app.ai.deepseek import chat_json
from app.audits.charts import compute_chart_data
from app.extensions import db
from app.models import AuditPresentation, PageAlert

MAX_PAGES = 8
MAX_BULLETS = 6
BULLET_MAXLEN = 200
HEADING_MAXLEN = 120
TITLE_MAXLEN = 160

SYSTEM_PROMPT = (
    "You are a senior SEO consultant preparing slide content for a client audit presentation "
    "about pages losing organic traffic on one website. You receive Google Search Console "
    "metrics already computed by a rule engine (real, verified declines — not raw noise) and "
    "must turn them into concise slide content. Respond with STRICT JSON only, no prose, shaped "
    'exactly as: {"title": "<presentation title, mentions the site>", "slides": '
    '[{"heading": "<short slide heading>", "bullets": ["<short bullet>", ...]}, ...]}. '
    "Rules: use ONLY the numbers given in the input, never invent clicks/percentages/positions; "
    "the first slide must be an overview of the site's situation; one slide per page given, "
    "referencing its real numbers (best_month_clicks, click_loss_pct, position_before/after, "
    "reason_text) — when suggesting a cause, phrase it as a hypothesis, not a certainty; the "
    "last slide must be concrete next-step recommendations grounded in the data, and must NOT "
    "promise that traffic will recover. Max 5 bullets per slide, each under 160 characters."
)


class NoDataError(Exception):
    """Nessun page_alert attivo per questo sito: niente da mettere in slide,
    niente chiamata AI da sprecare."""


def _top_alerts(user_id: int, site_url: str) -> list[PageAlert]:
    return PageAlert.active(user_id, site_url).order_by(PageAlert.priority_score.desc()).limit(MAX_PAGES).all()


def _compact_alerts(alerts: list[PageAlert]) -> list[dict]:
    return [
        {
            "url": a.url,
            "best_month_clicks": a.best_month_clicks,
            "click_loss_abs": a.click_loss_abs,
            "click_loss_pct": None if a.click_loss_pct is None else round(a.click_loss_pct, 1),
            "position_before": None if a.position_before is None else round(a.position_before, 1),
            "position_after": None if a.position_after is None else round(a.position_after, 1),
            "priority_score": None if a.priority_score is None else round(a.priority_score, 1),
            "reason_text": a.reason_text,
        }
        for a in alerts
    ]


def _sanitize_slides(result: dict, site_url: str) -> tuple[str, list[dict]]:
    title = str(result.get("title") or f"SEO Audit — {site_url}").strip()[:TITLE_MAXLEN]

    slides = []
    for item in (result.get("slides") or [])[: MAX_PAGES + 2]:
        heading = str(item.get("heading") or "").strip()[:HEADING_MAXLEN]
        bullets = [
            str(b).strip()[:BULLET_MAXLEN]
            for b in (item.get("bullets") or [])
            if str(b).strip()
        ][:MAX_BULLETS]
        if heading and bullets:
            slides.append({"heading": heading, "bullets": bullets})

    return title, slides


def _assemble_markdown(title: str, site_url: str, slides: list[dict]) -> str:
    today = date.today().isoformat()
    parts = [f"# {title}\n\n{site_url}\n\n_Generated {today} by LinkBayCMS_"]
    for slide in slides:
        bullet_lines = "\n".join(f"- {b}" for b in slide["bullets"])
        parts.append(f"## {slide['heading']}\n\n{bullet_lines}")
    return "\n\n---\n\n".join(parts)


def build_presentation(user_id: int, site_url: str) -> AuditPresentation:
    """Solleva NoDataError (nessun alert attivo) o DeepSeekError (chiamata
    fallita/non configurata, vedi app.ai.deepseek) — il chiamante (il job)
    decide come tradurre questi casi in un esito di business, non consuma
    crediti né salva nulla se questa funzione non ritorna."""
    alerts = _top_alerts(user_id, site_url)
    if not alerts:
        raise NoDataError(f"No active page alerts for {site_url}")

    compact = _compact_alerts(alerts)
    user_prompt = f"Website: {site_url}\nDeclining pages (rule-engine verified):\n{compact}\n\nReturn the JSON described in the system prompt."

    result = chat_json(SYSTEM_PROMPT, user_prompt)
    title, slides = _sanitize_slides(result, site_url)
    if not slides:
        raise NoDataError("AI returned no usable slides")

    markdown = _assemble_markdown(title, site_url, slides)

    # Grafici: SOLO dati deterministici (stessi `alerts` già interrogati
    # sopra + storico GscSiteDaily), mai l'output AI — vedi
    # app/audits/charts.py. Salvato come JSON testuale così la presentazione
    # resta riproducibile esattamente come generata (vedi
    # AuditPresentation.chart_data).
    chart_data = compute_chart_data(user_id, site_url, alerts)

    presentation = AuditPresentation(
        user_id=user_id, site_url=site_url, title=title, markdown=markdown,
        chart_data=json.dumps(chart_data),
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(presentation)
    db.session.commit()
    return presentation
