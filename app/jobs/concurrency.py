"""Semaforo Redis per il limite di scan concorrenti per utente
(PlanLimits.concurrent_scans — es. Tier 3 AppSumo: max 3, dalla richiesta
originale). Un contatore per utente con TTL: il TTL è la rete di sicurezza
se un worker muore prima di chiamare release_scan_slot (es. SIGKILL, che
salta i blocchi `finally`) — lo slot si libera comunque da solo dopo
TTL_SECONDS invece di restare bloccato per sempre."""
from app.jobs.queue import get_redis

TTL_SECONDS = 600  # allineato al job_timeout dei job di scan (vedi app/jobs/tasks.py)


def _key(user_id: int) -> str:
    return f"scan_slots:{user_id}"


def acquire_scan_slot(user_id: int, limit: int) -> bool:
    """True se lo slot è stato acquisito (il chiamante DEVE poi rilasciarlo
    con release_scan_slot, tipicamente in un blocco finally)."""
    redis = get_redis()
    key = _key(user_id)
    current = redis.incr(key)
    if current == 1:
        redis.expire(key, TTL_SECONDS)
    if current > limit:
        redis.decr(key)
        return False
    return True


def release_scan_slot(user_id: int) -> None:
    redis = get_redis()
    key = _key(user_id)
    # Non scendere sotto zero: una release senza una acquire corrispondente
    # (bug, o slot già scaduto per TTL) non deve intaccare il conteggio del
    # prossimo ciclo di acquisizioni.
    if int(redis.get(key) or 0) > 0:
        redis.decr(key)
