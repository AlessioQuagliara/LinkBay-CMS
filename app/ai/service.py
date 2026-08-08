"""Orchestrazione dell'AI Analyzer.

Strategia (per contenere il costo): UNA sola chiamata DeepSeek per sito, con un
contesto compatto delle pagine più rilevanti, e una risposta JSON dettagliata
per pagina (score 0-100 + max 5 suggerimenti). Cadenza settimanale, e solo se
l'utente ha attivato lo switch. I risultati si salvano in AiPageAnalysis.
"""
from datetime import date, datetime, timedelta, timezone

from app.ai.deepseek import chat_json
from app.extensions import db
from app.models import AiAnalyzerConfig, AiPageAnalysis

MAX_PAGES = 25          # pagine inviate al prompt (limite costo/token)
MAX_SUGGESTIONS = 5
SUGGESTION_MAXLEN = 200
RUN_COOLDOWN_DAYS = 7   # una vera analisi a settimana

SYSTEM_PROMPT = (
    "You are a senior technical SEO consultant. You receive Google Search Console "
    "metrics for a set of pages from one website and must return concrete, "
    "prioritized advice. Respond with STRICT JSON only, no prose, shaped exactly "
    'as: {"pages": [{"url": "<echo the exact url>", "score": <int 0-100>, '
    '"suggestions": ["<short actionable tip>", ...]}]}. '
    "score is an SEO health/opportunity score for that page: 100 = healthy and "
    "stable, low = urgent, losing traffic and worth fixing now. Base it on the "
    "clicks trend, CTR vs. average position, and impressions. Give at most 5 "
    "suggestions per page, each under 160 characters, specific to that page's "
    "numbers (e.g. title/meta CTR fixes, content refresh, internal linking, "
    "intent mismatch, cannibalization). Only include pages present in the input."
)


def get_or_create_config(user_id, site_url):
    cfg = AiAnalyzerConfig.query.filter_by(user_id=user_id, site_url=site_url).first()
    if cfg is None:
        cfg = AiAnalyzerConfig(user_id=user_id, site_url=site_url, enabled=False)
        db.session.add(cfg)
        db.session.commit()
    return cfg


def set_enabled(user_id, site_url, enabled: bool):
    cfg = get_or_create_config(user_id, site_url)
    cfg.enabled = enabled
    db.session.commit()
    return cfg


def _cooldown_remaining(cfg):
    """Giorni mancanti al prossimo run consentito (0 se disponibile ora)."""
    if not cfg.last_run_at:
        return 0
    next_run = cfg.last_run_at + timedelta(days=RUN_COOLDOWN_DAYS)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return max(0, (next_run - now).days + (1 if next_run > now else 0))


def _week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _compact_pages(pages):
    """Riduce le pagine al minimo informativo per il prompt (meno token)."""
    subset = pages[:MAX_PAGES]
    return [
        {
            "url": p["url"],
            "clicks": round(p.get("clicks", 0)),
            "impressions": round(p.get("impressions", 0)),
            "ctr_pct": round(100 * p.get("ctr", 0.0), 2),
            "avg_position": round(p.get("position", 0.0), 1),
            "clicks_change_pct": (
                None if p.get("clicks_delta_pct") is None else round(p["clicks_delta_pct"], 1)
            ),
        }
        for p in subset
    ]


def analyze_site(user_id, site_url, pages):
    """Esegue l'analisi AI e salva i risultati. Ritorna la mappa url->risultato.
    Solleva DeepSeekError se la chiamata fallisce o non è configurata."""
    compact = _compact_pages(pages)
    known_urls = {p["url"] for p in compact}

    user_prompt = (
        f"Website: {site_url}\n"
        f"Pages (last 28 days vs previous 28 days):\n"
        f"{compact}\n\n"
        "Return the JSON described in the system prompt."
    )

    result = chat_json(SYSTEM_PROMPT, user_prompt)

    week = _week_start(date.today())
    stored = {}
    for item in result.get("pages", []):
        url = item.get("url")
        if url not in known_urls:
            continue  # ignora url che l'AI non ha ricevuto (allucinati)

        score = item.get("score", 0)
        try:
            score = max(0, min(100, int(score)))
        except (TypeError, ValueError):
            score = 0

        suggestions = [
            str(s).strip()[:SUGGESTION_MAXLEN]
            for s in (item.get("suggestions") or [])
            if str(s).strip()
        ][:MAX_SUGGESTIONS]

        row = AiPageAnalysis.query.filter_by(
            user_id=user_id, site_url=site_url, page_url=url
        ).first()
        if row is None:
            row = AiPageAnalysis(user_id=user_id, site_url=site_url, page_url=url)
            db.session.add(row)
        row.score = score
        row.suggestions = suggestions
        row.week_start = week

        stored[url] = {"score": score, "suggestions": suggestions, "week_start": week.isoformat()}

    cfg = get_or_create_config(user_id, site_url)
    cfg.last_run_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.session.commit()

    return stored


def get_status(user_id, site_url):
    """Stato AI per la UI: switch, ultimo run, cooldown, risultati salvati."""
    cfg = AiAnalyzerConfig.query.filter_by(user_id=user_id, site_url=site_url).first()
    rows = AiPageAnalysis.query.filter_by(user_id=user_id, site_url=site_url).all()
    analyses = {
        r.page_url: {
            "score": r.score,
            "suggestions": r.suggestions or [],
            "week_start": r.week_start.isoformat() if r.week_start else None,
        }
        for r in rows
    }
    return {
        "enabled": bool(cfg and cfg.enabled),
        "last_run_at": cfg.last_run_at.isoformat() if cfg and cfg.last_run_at else None,
        "cooldown_days_left": _cooldown_remaining(cfg) if cfg else 0,
        "analyses": analyses,
    }
