"""Orchestrazione dell'AI Analyzer.

Strategia (per contenere il costo): UNA sola chiamata DeepSeek per sito, con un
contesto compatto delle pagine più rilevanti, e una risposta JSON dettagliata
per pagina (score 0-100 + max 5 suggerimenti). Cadenza settimanale, e solo se
l'utente ha attivato lo switch. I risultati si salvano in AiPageAnalysis.
"""
from datetime import date, datetime, timedelta, timezone

from app.ai.deepseek import chat_json
from app.extensions import db
from app.models import AiAnalyzerConfig, AiPageAnalysis, PageAlert

MAX_PAGES = 25          # pagine inviate al prompt (limite costo/token)
MAX_SUGGESTIONS = 5
SUGGESTION_MAXLEN = 200
RUN_COOLDOWN_DAYS = 7   # freno per i piani ai_mode=="cooldown" (AppSumo Tier 1/2)
AI_CREDIT_COST_PER_RUN = 1  # crediti consumati per run, piani ai_mode=="credit"

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

# Aggiunta al system prompt per il contesto "decay": qui le pagine arrivano già
# filtrate dal rule engine (page_alerts), con la perdita reale su base mensile e
# una motivazione pronta. Diciamo al modello di FIDARSI di quei numeri invece di
# ricalcolare la severità dal solo delta 28gg, e di legare i consigli al motivo.
DECAY_PROMPT_ADDENDUM = (
    " These pages were already flagged as genuinely declining by a rule engine. "
    "Use best_month_clicks, click_loss_pct and reason_text as the primary context "
    "for severity and advice — do NOT recompute how bad the drop is from scratch. "
    "Let the score reflect that loss, and make each suggestion refer explicitly to "
    "the reason: when impressions hold but position worsened (position_before -> "
    "position_after), it's lost ranking not lost demand, so focus on title/meta and "
    "on-page relevance; when impressions dropped too (site_relative_drop_pct, "
    "yoy_confirmed), demand itself fell, so advise whether a refresh is still worth it."
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


def _cooldown_remaining(cfg, limits):
    """Giorni mancanti al prossimo run consentito (0 se disponibile ora).
    Se limits.ai_mode == "credit" il freno è a crediti, non a tempo: il
    controllo reale è app.entitlements.service.check_ai_credits."""
    if limits.ai_mode == "credit":
        return 0
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


def _compact_alerts(alerts):
    """Payload arricchito per il contesto "decay": oltre alle metriche base,
    porta i numeri già calcolati dal rule engine (perdita reale su base mensile,
    posizione prima/dopo, trend impression, YoY) e la motivazione testuale, così
    il modello non deve indovinare il contesto del calo."""
    subset = alerts[:MAX_PAGES]
    return [
        {
            "url": a.url,
            "best_month_clicks": a.best_month_clicks,
            "click_loss_pct": (
                None if a.click_loss_pct is None else round(a.click_loss_pct, 1)
            ),
            "position_before": (
                None if a.position_before is None else round(a.position_before, 1)
            ),
            "position_after": (
                None if a.position_after is None else round(a.position_after, 1)
            ),
            "site_relative_drop_pct": (
                None if a.site_relative_drop_pct is None else round(a.site_relative_drop_pct, 1)
            ),
            "yoy_confirmed": bool(a.yoy_confirmed),
            "reason_text": a.reason_text,
        }
        for a in subset
    ]


def _store_analysis(user_id, site_url, result, known_urls):
    """Salva la risposta DeepSeek in AiPageAnalysis e aggiorna last_run_at.
    Condiviso da analyze_site e analyze_declining: stesso schema, stesso
    cooldown settimanale (un solo last_run_at per sito)."""
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
    return _store_analysis(user_id, site_url, result, known_urls)


def analyze_declining(user_id, site_url):
    """Analisi AI mirata alle pagine già segnalate in calo (page_alerts).

    Legge gli alert "attivi" (new/acknowledged) del sito, ordinati per priorità,
    e passa al modello il contesto arricchito del rule engine invece del solo
    delta 28gg. Salva in AiPageAnalysis e rispetta lo stesso cooldown settimanale
    di analyze_site (nessun secondo cooldown parallelo).
    Solleva DeepSeekError se la chiamata fallisce o non è configurata."""
    alerts = PageAlert.active(user_id, site_url).order_by(PageAlert.priority_score.desc()).limit(MAX_PAGES).all()
    compact = _compact_alerts(alerts)
    known_urls = {a["url"] for a in compact}

    user_prompt = (
        f"Website: {site_url}\n"
        "Pages already flagged as declining (monthly figures from a rule engine):\n"
        f"{compact}\n\n"
        "Return the JSON described in the system prompt."
    )

    result = chat_json(SYSTEM_PROMPT + DECAY_PROMPT_ADDENDUM, user_prompt)
    return _store_analysis(user_id, site_url, result, known_urls)


def get_status(user_id, site_url):
    """Stato AI per la UI: switch, ultimo run, cooldown/crediti, risultati
    salvati."""
    from app.entitlements.service import get_plan_limits
    from app.extensions import db
    from app.models import User

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

    user = db.session.get(User, user_id)
    limits = get_plan_limits(user) if user else None

    return {
        "enabled": bool(cfg and cfg.enabled),
        "last_run_at": cfg.last_run_at.isoformat() if cfg and cfg.last_run_at else None,
        "cooldown_days_left": _cooldown_remaining(cfg, limits) if cfg else 0,
        "ai_mode": limits.ai_mode if limits else "cooldown",
        "ai_credit_balance": user.ai_credit_balance if user else 0,
        "analyses": analyses,
    }
