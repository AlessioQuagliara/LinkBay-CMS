"""Tagging "heavy user" per il monitoraggio dei costi infrastrutturali —
segnala chi consuma molto più della norma (scan, run AI, export) così il
supporto/prodotto può intervenire (upsell mirato, o verificare abuso) senza
dover interrogare a mano ResourceUsageLog. Rivalutato ad ogni run (non è
one-way): un utente che torna sotto soglia si sflagga automaticamente."""
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models import ResourceUsageLog, User

WINDOW_DAYS = 30

# PLACEHOLDER — soglie non specificate nella richiesta originale, da tarare
# sui costi infrastrutturali reali (chiamate GSC/DeepSeek) prima del lancio.
HEAVY_USER_THRESHOLDS = {
    "gsc_scan": 200,
    "ai_analysis": 50,
    "export_csv": 100,
    "export_pdf": 100,
}


def _usage_counts(user_id: int, since: datetime) -> dict:
    rows = (
        db.session.query(ResourceUsageLog.action, db.func.count(ResourceUsageLog.id))
        .filter(
            ResourceUsageLog.user_id == user_id,
            ResourceUsageLog.created_at >= since,
            ResourceUsageLog.counted_against_limit.is_(True),
        )
        .group_by(ResourceUsageLog.action)
        .all()
    )
    return {action: count for action, count in rows}


def _is_heavy(counts: dict) -> bool:
    return any(counts.get(action, 0) > threshold for action, threshold in HEAVY_USER_THRESHOLDS.items())


def flag_heavy_users() -> dict:
    """Rivaluta ogni utente con almeno un'azione tracciata negli ultimi
    WINDOW_DAYS giorni. Ritorna {"flagged": [...], "unflagged": [...]} (id
    utente) per il log del comando CLI."""
    since = datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)
    user_ids = {
        row[0]
        for row in db.session.query(ResourceUsageLog.user_id)
        .filter(ResourceUsageLog.created_at >= since)
        .distinct()
        .all()
    }

    flagged, unflagged = [], []
    for user_id in user_ids:
        user = db.session.get(User, user_id)
        if user is None:
            continue
        counts = _usage_counts(user_id, since)
        heavy = _is_heavy(counts)
        if heavy and not user.heavy_user_flag:
            user.heavy_user_flag = True
            user.heavy_user_flagged_at = datetime.now(timezone.utc)
            flagged.append(user_id)
        elif not heavy and user.heavy_user_flag:
            user.heavy_user_flag = False
            unflagged.append(user_id)
    db.session.commit()
    return {"flagged": flagged, "unflagged": unflagged}
