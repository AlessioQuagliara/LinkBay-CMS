"""Coda RQ (app/jobs/): niente Redis reale nei test — fakeredis al posto del
client redis-py, e Queue(is_async=False) per eseguire i job in-process invece
che tramite un worker separato. get_worker_app() è monkeypatchato per puntare
alla stessa app/DB di test (SQLite in-memory) invece che a config.Config
"vera" (Postgres di default) — i due processi (web/worker) sono separati
apposta in produzione, ma nei test devono condividere lo stesso DB fittizio.
"""
import fakeredis
import pytest
from rq import Queue

from app.gsc.sites import add_monitored_site
from app.jobs import concurrency, queue as queue_module


def _dummy_ok_job():
    # RQ serializza i job per percorso di import: una lambda non è
    # referenziabile così, serve una funzione a livello di modulo.
    return {"ok": True}


@pytest.fixture()
def fake_redis():
    return fakeredis.FakeStrictRedis()


@pytest.fixture()
def patch_redis(monkeypatch, fake_redis):
    """get_redis() è importato per riferimento diretto in più moduli
    (app/jobs/queue.py e app/jobs/concurrency.py) — vanno patchati entrambi
    perché ciascuno guarda il proprio namespace, non quello dell'altro."""
    monkeypatch.setattr(queue_module, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(concurrency, "get_redis", lambda: fake_redis)
    return fake_redis


@pytest.fixture()
def patch_worker_app(monkeypatch, app):
    """run_gsc_scan_job/run_ai_analysis_job costruiscono da soli il loro
    app-context tramite get_worker_app() — nei test lo si fa puntare all'app
    di test (SQLite in-memory) invece che a config.Config "vera" (Postgres),
    altrimenti i job proverebbero a connettersi a un DB reale inesistente."""
    monkeypatch.setattr("app.jobs.tasks.get_worker_app", lambda: app)


# --- concurrency.py ----------------------------------------------------------


def test_acquire_scan_slot_allows_up_to_limit(app, patch_redis):
    with app.app_context():
        assert concurrency.acquire_scan_slot(1, limit=2) is True
        assert concurrency.acquire_scan_slot(1, limit=2) is True
        assert concurrency.acquire_scan_slot(1, limit=2) is False  # terzo slot: oltre il limite


def test_release_scan_slot_frees_capacity(app, patch_redis):
    with app.app_context():
        concurrency.acquire_scan_slot(1, limit=1)
        assert concurrency.acquire_scan_slot(1, limit=1) is False
        concurrency.release_scan_slot(1)
        assert concurrency.acquire_scan_slot(1, limit=1) is True


def test_release_scan_slot_does_not_go_negative(app, patch_redis, fake_redis):
    with app.app_context():
        concurrency.release_scan_slot(42)  # nessuna acquire precedente
        assert int(fake_redis.get("scan_slots:42") or 0) == 0


def test_scan_slots_are_isolated_per_user(app, patch_redis):
    with app.app_context():
        assert concurrency.acquire_scan_slot(1, limit=1) is True
        assert concurrency.acquire_scan_slot(2, limit=1) is True  # utente diverso, slot indipendente


# --- queue.py ------------------------------------------------------------


def test_queue_name_for_user_reads_plan_priority(db_session, make_user):
    user = make_user(plan_type="appsumo_tier3")  # queue_priority="high" in PLAN_LIMITS
    assert queue_module.queue_name_for_user(user) == "high"


def test_get_queue_falls_back_to_default_for_unknown_name(app, patch_redis):
    with app.app_context():
        q = queue_module.get_queue("not-a-real-queue")
        assert q.name == "default"


def test_job_status_payload_not_found(app, patch_redis):
    with app.app_context():
        assert queue_module.job_status_payload("does-not-exist") == {"status": "not_found"}


def test_job_status_payload_finished_includes_job_result(app, patch_redis, fake_redis):
    with app.app_context():
        q = Queue("default", connection=fake_redis, is_async=False)
        job = q.enqueue(_dummy_ok_job)
        payload = queue_module.job_status_payload(job.id)
        assert payload["status"] == "finished"
        assert payload["job_result"] == {"ok": True}


# --- job functions (eseguiti in-process, non tramite worker) -----------------


def test_run_gsc_scan_job_returns_early_without_gsc_connection(
    app, db_session, make_user, patch_redis, patch_worker_app
):
    from app.jobs.tasks import run_gsc_scan_job

    user = make_user()
    add_monitored_site(user.id, "https://example.com/")
    concurrency.acquire_scan_slot(user.id, limit=1)

    # Nessun GscConnection per l'utente: get_user_gsc_service ritorna (None, None),
    # il job deve uscire subito SENZA sollevare — e comunque rilasciare lo slot.
    run_gsc_scan_job(user.id, "https://example.com/")

    assert int((patch_redis.get(f"scan_slots:{user.id}")) or 0) == 0


def test_run_ai_analysis_job_returns_not_connected_without_gsc(
    app, db_session, make_user, patch_worker_app
):
    from app.jobs.tasks import run_ai_analysis_job

    user = make_user()
    result = run_ai_analysis_job(user.id, "https://example.com/")
    assert result == {"ok": False, "error": "not_connected"}
