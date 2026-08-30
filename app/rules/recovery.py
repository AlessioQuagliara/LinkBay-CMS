"""Recovery-check: per le pagine marcate "done" da 30 o 60 giorni, verifica se
il traffico è davvero tornato e aggiorna lo stato a "recovered".

Riusa `best_month_clicks` già salvato su ogni PageAlert (il picco pre-calo
individuato dal rule engine, app/rules/engine.py) come baseline: nessun nuovo
calcolo, solo un confronto con i click più recenti disponibili in
GscPageMonthly (tenuti freschi dal job settimanale run-decay-rules, vedi
app/rules/service.py::run_weekly)."""
from datetime import datetime, timedelta, timezone

from flask import current_app

from app.extensions import db
from app.models import GscPageMonthly, PageAlert

RECOVERY_THRESHOLD = 0.8  # click recenti >= 80% del picco pre-calo = recuperata
CHECKPOINTS = (30, 60)


def _aware(dt):
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _latest_clicks(user_id, site_url, page_url):
    row = (
        GscPageMonthly.query.filter_by(user_id=user_id, site_url=site_url, page_url=page_url)
        .order_by(GscPageMonthly.month.desc())
        .first()
    )
    return row.clicks if row else None


def _evaluate(alert):
    recent_clicks = _latest_clicks(alert.user_id, alert.site_url, alert.url)
    if recent_clicks is None or not alert.best_month_clicks:
        return False  # storico insufficiente: non decidiamo, si ricontrolla al checkpoint successivo
    return recent_clicks >= RECOVERY_THRESHOLD * alert.best_month_clicks


def check_due_alerts() -> dict:
    """Valuta ogni alert "done" scaduto per un checkpoint non ancora
    controllato. Un alert fallito non ferma gli altri."""
    now = datetime.now(timezone.utc)
    alerts = PageAlert.query.filter(PageAlert.status == "done", PageAlert.done_at.isnot(None)).all()

    checked = recovered = errors = 0
    for alert in alerts:
        try:
            days_since_done = (now - _aware(alert.done_at)).days
            evaluated = False

            if days_since_done >= 30 and alert.checked_30d_at is None:
                if _evaluate(alert):
                    alert.status = "recovered"
                alert.checked_30d_at = now
                evaluated = True

            if not alert.status == "recovered" and days_since_done >= 60 and alert.checked_60d_at is None:
                if _evaluate(alert):
                    alert.status = "recovered"
                alert.checked_60d_at = now
                evaluated = True

            if evaluated:
                db.session.commit()
                checked += 1
                if alert.status == "recovered":
                    recovered += 1
        except Exception:  # noqa: BLE001 — un alert non deve fermare il job
            db.session.rollback()
            current_app.logger.exception("Recovery-check fallito per alert %s", alert.id)
            errors += 1

    return {"checked": checked, "recovered": recovered, "errors": errors}
