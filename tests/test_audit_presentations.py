"""Audit Presentations (app/audits/): generazione via job in coda (come
/ai/analyze), isolamento tra utenti, gate crediti, nessun doppio consumo su
fallimento, markdown -> slide reveal.js deterministico."""
from datetime import date

import pytest

from app.audits.render import parse_markdown, slides_to_html
from app.audits.service import NoDataError, build_presentation
from app.models import AuditPresentation, MonitoredSite, PageAlert


def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


def _make_site(db_session, user, site_url="https://example.com/"):
    site = MonitoredSite(user_id=user.id, site_url=site_url, is_active=True)
    db_session.add(site)
    db_session.commit()
    return site


def _make_alert(db_session, user, site_url="https://example.com/", url="https://example.com/page-1"):
    alert = PageAlert(
        user_id=user.id, site_url=site_url, url=url, window_end=date(2026, 8, 1),
        best_month_clicks=500, click_loss_abs=200, click_loss_pct=-40.0,
        position_before=3.0, position_after=8.0, priority_score=90.0,
        reason_text="Traffic dropped after a title change.", status="new",
    )
    db_session.add(alert)
    db_session.commit()
    return alert


FAKE_AI_RESULT = {
    "title": "SEO Audit — example.com",
    "slides": [
        {"heading": "Overview", "bullets": ["1 page is losing traffic."]},
        {"heading": "example.com/page-1", "bullets": ["Lost 200 clicks (-40%).", "Position moved from 3.0 to 8.0."]},
        {"heading": "Recommendations", "bullets": ["Review the on-page content for page-1."]},
    ],
}


# --- service: costruzione markdown -----------------------------------------


def test_build_presentation_requires_active_alerts(db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    _make_site(db_session, user)
    with pytest.raises(NoDataError):
        build_presentation(user.id, "https://example.com/")


def test_build_presentation_persists_and_uses_only_given_numbers(db_session, make_user, monkeypatch):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    _make_site(db_session, user)
    _make_alert(db_session, user)

    monkeypatch.setattr("app.audits.service.chat_json", lambda system, user_prompt: FAKE_AI_RESULT)

    presentation = build_presentation(user.id, "https://example.com/")
    assert presentation.id is not None
    assert presentation.site_url == "https://example.com/"
    assert "200 clicks" in presentation.markdown
    assert "-40%" in presentation.markdown
    assert presentation.markdown.count("\n\n---\n\n") == 3  # title + 3 slide -> 3 separatori


def test_markdown_parses_into_reveal_sections(db_session, make_user, monkeypatch):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    _make_site(db_session, user)
    _make_alert(db_session, user)
    monkeypatch.setattr("app.audits.service.chat_json", lambda system, user_prompt: FAKE_AI_RESULT)

    presentation = build_presentation(user.id, "https://example.com/")
    slides = parse_markdown(presentation.markdown)
    assert slides[0].kind == "title"
    assert slides[1].kind == "content"
    html = slides_to_html(slides)
    assert html.count("<section") == 4  # title + 3 content slides
    assert "<script>" not in html  # niente injection dai dati (reason_text incluso)


def test_ai_content_cannot_inject_script_into_slides(db_session, make_user, monkeypatch):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    _make_site(db_session, user)
    _make_alert(db_session, user, url="https://example.com/xss")

    malicious = {
        "title": "<script>alert(1)</script>",
        "slides": [{"heading": "<img src=x onerror=alert(1)>", "bullets": ["<script>alert(2)</script>"]}],
    }
    monkeypatch.setattr("app.audits.service.chat_json", lambda system, user_prompt: malicious)

    presentation = build_presentation(user.id, "https://example.com/")
    slides = parse_markdown(presentation.markdown)
    html = slides_to_html(slides)
    # La sicurezza sta nell'escaping, non nell'assenza della sottostringa: il
    # tag deve arrivare come testo innocuo (&lt;img ...), mai come markup vero.
    assert "<script>" not in html
    assert "<img " not in html
    assert "&lt;img" in html and "&lt;script&gt;" in html


# --- job: coda, crediti, isolamento -----------------------------------------


def test_audit_job_consumes_credits_only_on_success(app, db_session, make_user, monkeypatch):
    from app.jobs.tasks import run_audit_presentation_job

    monkeypatch.setattr("app.jobs.tasks.get_worker_app", lambda: app)

    user = make_user(plan_type="subscription_monthly", subscription_status="active", ai_credit_balance=100)
    _make_site(db_session, user)
    _make_alert(db_session, user)
    monkeypatch.setattr("app.audits.service.chat_json", lambda system, user_prompt: FAKE_AI_RESULT)

    result = run_audit_presentation_job(user.id, "https://example.com/")
    assert result["ok"] is True
    db_session.refresh(user)
    assert user.ai_credit_balance == 95  # 100 - 5


def test_audit_job_does_not_consume_credits_on_no_data(app, db_session, make_user, monkeypatch):
    from app.jobs.tasks import run_audit_presentation_job

    monkeypatch.setattr("app.jobs.tasks.get_worker_app", lambda: app)

    user = make_user(plan_type="subscription_monthly", subscription_status="active", ai_credit_balance=100)
    _make_site(db_session, user)
    # nessun alert

    result = run_audit_presentation_job(user.id, "https://example.com/")
    assert result == {"ok": False, "error": "no_data"}
    db_session.refresh(user)
    assert user.ai_credit_balance == 100


def test_generate_route_blocks_when_insufficient_credits(client, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active", ai_credit_balance=0)
    _make_site(db_session, user)
    _login(client, user)

    res = client.post("/dashboard/audits/generate", data={"site": "https://example.com/"})
    assert res.status_code == 402
    data = res.get_json()
    assert data["error"] == "insufficient_credits"
    assert data["cost"] == 5


def test_generate_route_enqueues_job_when_allowed(client, db_session, make_user, monkeypatch):
    user = make_user(plan_type="subscription_monthly", subscription_status="active", ai_credit_balance=100)
    _make_site(db_session, user)
    _login(client, user)

    class FakeJob:
        id = "fake-job-id"

    class FakeQueue:
        def enqueue(self, fn, *args, **kwargs):
            return FakeJob()

    monkeypatch.setattr("app.audits.routes.get_queue", lambda name: FakeQueue())

    res = client.post("/dashboard/audits/generate", data={"site": "https://example.com/"})
    assert res.status_code == 200
    assert res.get_json() == {"status": "queued", "job_id": "fake-job-id"}


# --- isolamento tra utenti + view/download ----------------------------------


def _create_presentation(db_session, user, site_url="https://example.com/"):
    presentation = AuditPresentation(
        user_id=user.id, site_url=site_url, title="SEO Audit",
        markdown="# SEO Audit\n\nhttps://example.com/\n\n_Generated 2026-08-01 by LinkBayCMS_\n\n---\n\n## Overview\n\n- 1 page is losing traffic.",
    )
    db_session.add(presentation)
    db_session.commit()
    return presentation


def test_view_returns_404_for_other_users_presentation(client, db_session, make_user):
    owner = make_user(plan_type="subscription_monthly", subscription_status="active")
    other = make_user(plan_type="subscription_monthly", subscription_status="active")
    presentation = _create_presentation(db_session, owner)

    _login(client, other)
    res = client.get(f"/dashboard/audits/{presentation.id}")
    assert res.status_code == 404


def test_view_renders_reveal_js_presentation_for_owner(client, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    presentation = _create_presentation(db_session, user)
    _login(client, user)

    res = client.get(f"/dashboard/audits/{presentation.id}")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert "reveal.js" in body
    assert "SEO Audit" in body
    assert "audit-brand-footer" in body  # branding LinkBayCMS (onda + logo)


def test_download_sets_attachment_header(client, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    presentation = _create_presentation(db_session, user)
    _login(client, user)

    res = client.get(f"/dashboard/audits/{presentation.id}/download")
    assert res.status_code == 200
    assert "attachment" in res.headers["Content-Disposition"]
    assert res.headers["Content-Disposition"].endswith('.html"')
