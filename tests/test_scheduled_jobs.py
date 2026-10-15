"""Job schedulati da cron: digest settimanale (filtro accesso) e run_weekly
(salvataggio credenziali GSC dopo il refresh del token)."""
from datetime import datetime, timedelta, timezone

from app.gsc.sites import add_monitored_site


def test_weekly_digest_skips_active_status_with_expired_access(app, db_session, make_user, monkeypatch):
    import app.emails.digest as digest

    expired = make_user(
        plan_type="paddle_1m", subscription_status="active", subscription_source="paddle",
        subscription_expires_at=datetime.now(timezone.utc) - timedelta(days=2),
    )
    lifetime = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    for u in (expired, lifetime):
        add_monitored_site(u.id, "https://example.com/")

    sent_to = []
    monkeypatch.setattr(digest, "send_weekly_digest_for_user", lambda user, site: sent_to.append(user.id) or True)

    result = app.test_cli_runner().invoke(args=["send-weekly-digest"])
    assert result.exit_code == 0, result.output
    assert sent_to == [lifetime.id]


def test_run_weekly_saves_refreshed_credentials(app, db_session, make_user, monkeypatch):
    import app.gsc.gsc as gsc
    import app.gsc.page_history as page_history
    import app.gsc.repository as repository
    import app.rules.service as rules_service

    user = make_user()
    add_monitored_site(user.id, "https://example.com/")

    saved = []
    monkeypatch.setattr(gsc, "get_user_gsc_service", lambda uid: (object(), "fresh-creds"))
    monkeypatch.setattr(page_history, "sync_page_monthly", lambda *a: 0)
    monkeypatch.setattr(rules_service, "run_for_site", lambda *a: [])
    monkeypatch.setattr(repository, "credentials_to_dict", lambda c: {"token": c})
    monkeypatch.setattr(repository, "save_gsc_credentials", lambda uid, d: saved.append((uid, d)))

    result = rules_service.run_weekly()
    assert result == {"processed": 1, "errors": []}
    assert saved == [(user.id, {"token": "fresh-creds"})]
