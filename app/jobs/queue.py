"""Code RQ: job asincroni (scan GSC on-demand, run AI Analyzer) invece di
lavoro sincrono dentro la request. Tre code per priorità
(PlanLimits.queue_priority) — "high" (Pro, AppSumo Tier 3), "default"
(AppSumo Tier 1/2), "low" (trial) — consumate in quest'ordine dal worker
(vedi command del servizio "worker" in compose.yml/compose.prod.yml)."""
from flask import current_app
from redis import Redis
from rq import Queue
from rq.job import Job

QUEUE_NAMES = ("high", "default", "low")


def get_redis() -> Redis:
    return Redis.from_url(current_app.config["REDIS_URL"])


def get_queue(name: str = "default") -> Queue:
    if name not in QUEUE_NAMES:
        name = "default"
    return Queue(name, connection=get_redis())


def queue_name_for_user(user) -> str:
    from app.entitlements.service import get_plan_limits

    return get_plan_limits(user).queue_priority


def job_status_payload(job_id: str) -> dict:
    """Payload JSON generico per gli endpoint di polling (analyze-status,
    audit generate-status): stato RQ + esito se già concluso. "failed" qui indica un
    crash imprevisto del job (bug) — un fallimento "atteso" (DeepSeek non
    configurato, utente non connesso a GSC, ecc.) è invece incapsulato nel
    valore di ritorno del job stesso (status "finished" con result["ok"] =
    False), per non confondere errori di business con crash veri. Vedi
    app/jobs/tasks.py::run_ai_analysis_job."""
    try:
        job = Job.fetch(job_id, connection=get_redis())
    except Exception:  # noqa: BLE001 — job_id inesistente/scaduto: nessun job, non un errore
        return {"status": "not_found"}
    status = job.get_status(refresh=True)
    payload = {"status": status}
    if status == "failed":
        payload["error"] = "job_failed"
    else:
        return_value = job.return_value()
        if status == "finished" and return_value is not None:
            payload["job_result"] = return_value
    return payload
