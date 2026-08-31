"""Funzioni eseguite dal worker RQ. Devono essere referenziabili a livello di
modulo — RQ le serializza per percorso di import (`app.jobs.tasks.nome`), non
per closure — e costruirsi da sole il contesto Flask/DB (app/jobs/worker_app.py),
perché girano in un processo separato da quello che le ha messe in coda
(la web app, dentro una request)."""
from app.jobs.concurrency import release_scan_slot
from app.jobs.worker_app import get_worker_app


def run_gsc_scan_job(user_id: int, site_url: str) -> None:
    """Rinfresca storico giornaliero + mensile per pagina di un sito e
    rigenera gli alert — lo stesso lavoro che oggi girava sincrono dentro
    /gsc/api/insights, spostato in coda (vedi app/gsc/gsc.py::api_insights).
    Rilascia sempre lo slot di concorrenza acquisito dal chiamante, anche in
    caso di errore."""
    app = get_worker_app()
    with app.app_context():
        try:
            from app.entitlements.service import record_usage
            from app.extensions import db
            from app.gsc.gsc import get_user_gsc_service
            from app.gsc.history import sync_site_daily
            from app.gsc.page_history import sync_page_monthly
            from app.gsc.repository import credentials_to_dict, save_gsc_credentials
            from app.gsc.sites import touch_last_synced
            from app.models import User
            from app.rules.service import run_for_site

            service, credentials = get_user_gsc_service(user_id)
            if service is None:
                return
            sync_site_daily(service, user_id, site_url, days=28)
            sync_page_monthly(service, user_id, site_url)
            run_for_site(user_id, site_url)
            save_gsc_credentials(user_id, credentials_to_dict(credentials))
            touch_last_synced(user_id, site_url)
            user = db.session.get(User, user_id)
            if user:
                record_usage(user, "gsc_scan", site_url=site_url)
        finally:
            release_scan_slot(user_id)


def run_ai_analysis_job(user_id: int, site_url: str) -> dict:
    """Stessa logica che prima girava sincrona dentro POST /ai/analyze (vedi
    app/ai/routes.py): se il sito ha già alert attivi, analizza quelli
    (contesto dal rule engine, niente chiamata GSC); altrimenti analizza le
    pagine da build_insights.

    Ritorna sempre un dict {"ok": bool, ...} invece di propagare le
    eccezioni "attese" (provider AI non configurato/down, utente non
    connesso a GSC): quei casi sono normali esiti di business, non crash del
    job — tenerli distinti da "failed" (bug/crash imprevisto) evita che chi
    fa polling (GET /ai/analyze-status/<job_id>) li confonda."""
    app = get_worker_app()
    with app.app_context():
        from app.ai.deepseek import DeepSeekError
        from app.ai.service import AI_CREDIT_COST_PER_RUN, analyze_declining, analyze_site
        from app.entitlements.ai_credits import consume_credits
        from app.entitlements.service import get_plan_limits, record_usage
        from app.extensions import db
        from app.gsc.gsc import get_user_gsc_service
        from app.gsc.insights import build_insights
        from app.gsc.repository import credentials_to_dict, save_gsc_credentials
        from app.models import PageAlert, User

        has_alerts = (
            PageAlert.query.filter(
                PageAlert.user_id == user_id,
                PageAlert.site_url == site_url,
                PageAlert.status.in_(("new", "acknowledged")),
            ).first()
            is not None
        )

        try:
            if has_alerts:
                analyze_declining(user_id, site_url)
            else:
                service, credentials = get_user_gsc_service(user_id)
                if service is None:
                    return {"ok": False, "error": "not_connected"}
                data = build_insights(service, site_url, days=28)
                analyze_site(user_id, site_url, data["pages"])
                save_gsc_credentials(user_id, credentials_to_dict(credentials))
        except DeepSeekError as e:
            return {"ok": False, "error": "ai_failed", "message": str(e)}
        except Exception:
            app.logger.exception("AI analyze job failed for %s (user %s)", site_url, user_id)
            return {"ok": False, "error": "query_failed"}

        # Consumo crediti solo a run riuscita, solo per i piani a crediti
        # (Pro/AppSumo Tier 3) — i piani a cooldown non toccano il ledger,
        # il loro freno resta AiAnalyzerConfig.last_run_at (invariato).
        user = db.session.get(User, user_id)
        if user:
            limits = get_plan_limits(user)
            if limits.ai_mode == "credit":
                consume_credits(user, AI_CREDIT_COST_PER_RUN, site_url=site_url)
            record_usage(user, "ai_analysis", site_url=site_url, credits_consumed=AI_CREDIT_COST_PER_RUN if limits.ai_mode == "credit" else None)

        return {"ok": True}


def run_audit_presentation_job(user_id: int, site_url: str) -> dict:
    """Stessa forma di ritorno/gestione errori di run_ai_analysis_job — solo
    la generazione (app/audits/service.py::build_presentation) e il consumo
    crediti differiscono: qui il costo è AI_CREDIT_ACTION_COSTS["audit_presentation"]
    (5, non 1) e non c'è nessun freno a cooldown, solo il gate a crediti già
    fatto sincrono in app/audits/routes.py prima di accodare il job."""
    app = get_worker_app()
    with app.app_context():
        from app.ai.deepseek import DeepSeekError
        from app.audits.service import NoDataError, build_presentation
        from app.entitlements.ai_credits import consume_credits
        from app.entitlements.limits import AI_CREDIT_ACTION_COSTS
        from app.entitlements.service import get_plan_limits, record_usage
        from app.extensions import db
        from app.models import User

        try:
            presentation = build_presentation(user_id, site_url)
        except NoDataError:
            return {"ok": False, "error": "no_data"}
        except DeepSeekError as e:
            return {"ok": False, "error": "ai_failed", "message": str(e)}
        except Exception:
            app.logger.exception("Audit presentation job failed for %s (user %s)", site_url, user_id)
            return {"ok": False, "error": "query_failed"}

        cost = AI_CREDIT_ACTION_COSTS["audit_presentation"]
        user = db.session.get(User, user_id)
        if user:
            limits = get_plan_limits(user)
            if limits.ai_mode == "credit":
                consume_credits(user, cost, site_url=site_url)
            record_usage(
                user, "audit_presentation", site_url=site_url,
                credits_consumed=cost if limits.ai_mode == "credit" else None,
            )

        return {"ok": True, "presentation_id": presentation.id}
