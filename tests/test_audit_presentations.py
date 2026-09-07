"""Audit Presentations (app/audits/): generazione via job in coda (come
/ai/analyze), isolamento tra utenti, gate crediti, nessun doppio consumo su
fallimento, markdown -> slide reveal.js deterministico, grafici (vedi
app/audits/charts.py) costruiti solo da PageAlert/GscSiteDaily reali."""
import json
from datetime import date, timedelta

import pytest

from app.audits.charts import compute_chart_data, render_chart_sections
from app.audits.render import parse_markdown, slides_to_html
from app.audits.service import NoDataError, build_presentation
from app.models import AuditPresentation, GscSiteDaily, MonitoredSite, PageAlert


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


# --- Fase 4: grafici (app/audits/charts.py) ---------------------------------


def _make_gsc_history(db_session, user, site_url="https://example.com/", days=60, declining=True):
    today = date.today()
    for i in range(days):
        d = today - timedelta(days=days - 1 - i)
        clicks = (200 - i) if (declining and i < days // 2) else 90
        db_session.add(GscSiteDaily(
            user_id=user.id, site_url=site_url, date=d,
            clicks=clicks, impressions=clicks * 10, ctr=0.1, position=5.0,
        ))
    db_session.commit()


def test_chart_data_built_only_from_real_alerts_and_gsc_history(db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    _make_site(db_session, user)
    _make_gsc_history(db_session, user)
    alert = _make_alert(db_session, user)

    chart_data = compute_chart_data(user.id, "https://example.com/", [alert])

    assert chart_data["trend"] is not None
    assert chart_data["trend"]["range_start"] and chart_data["trend"]["range_end"]
    assert chart_data["declining_pages"] == [
        {"label": "/page-1", "click_loss_abs": 200, "click_loss_pct": -40.0}
    ]
    assert chart_data["priority"] == [{"label": "/page-1", "priority_score": 90.0}]
    # KPI: pagine in calo totali dal DB (query separata, non solo il campione passato).
    assert chart_data["kpi"]["declining_pages_total"] == 1
    assert chart_data["kpi"]["click_loss_total"] == 200
    assert chart_data["kpi"]["high_priority_count"] == 1  # priority_score 90 >= 66


def test_chart_data_trend_none_when_history_too_short(db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    _make_site(db_session, user)
    alert = _make_alert(db_session, user)
    # nessuno storico GscSiteDaily inserito

    chart_data = compute_chart_data(user.id, "https://example.com/", [alert])
    assert chart_data["trend"] is None
    assert chart_data["declining_pages"]  # le pagine in calo restano disponibili comunque


def test_render_chart_sections_fallback_without_exceptions_when_no_data():
    html = render_chart_sections(None)
    assert "Not enough data" in html
    assert "<section" in html


def test_render_chart_sections_trend_fallback_when_history_missing():
    html = render_chart_sections({"trend": None, "declining_pages": [], "priority": [], "kpi": {
        "declining_pages_total": 0, "click_loss_total": 0, "high_priority_count": 0,
    }})
    assert "Not enough" in html
    assert "<svg" not in html  # nessun grafico trend inventato senza dati


def test_build_presentation_persists_chart_data(db_session, make_user, monkeypatch):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    _make_site(db_session, user)
    _make_gsc_history(db_session, user)
    _make_alert(db_session, user)
    monkeypatch.setattr("app.audits.service.chat_json", lambda system, user_prompt: FAKE_AI_RESULT)

    presentation = build_presentation(user.id, "https://example.com/")
    assert presentation.chart_data is not None
    stored = json.loads(presentation.chart_data)
    assert stored["trend"] is not None
    assert stored["declining_pages"]


def test_view_includes_charts_when_data_available(client, db_session, make_user, monkeypatch):
    user = make_user(plan_type="subscription_monthly", subscription_status="active", ai_credit_balance=100)
    _make_site(db_session, user)
    _make_gsc_history(db_session, user)
    _make_alert(db_session, user, url="https://example.com/page-<script>")
    monkeypatch.setattr("app.audits.service.chat_json", lambda system, user_prompt: FAKE_AI_RESULT)

    presentation = build_presentation(user.id, "https://example.com/")
    _login(client, user)

    res = client.get(f"/dashboard/audits/{presentation.id}")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert "<svg" in body
    assert "kpi-grid" in body
    assert "bar-chart" in body
    # Escaping: l'URL iniettato nell'alert non deve comparire come tag vero.
    assert "page-<script>" not in body
    assert "&lt;script&gt;" in body


def test_download_includes_charts(client, db_session, make_user, monkeypatch):
    user = make_user(plan_type="subscription_monthly", subscription_status="active", ai_credit_balance=100)
    _make_site(db_session, user)
    _make_gsc_history(db_session, user)
    _make_alert(db_session, user)
    monkeypatch.setattr("app.audits.service.chat_json", lambda system, user_prompt: FAKE_AI_RESULT)

    presentation = build_presentation(user.id, "https://example.com/")
    _login(client, user)

    res = client.get(f"/dashboard/audits/{presentation.id}/download")
    assert res.status_code == 200
    assert "<svg" in res.get_data(as_text=True)


def test_legacy_presentation_without_chart_data_renders_with_fallback(client, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    presentation = _create_presentation(db_session, user)  # chart_data non impostato -> NULL
    assert presentation.chart_data is None
    _login(client, user)

    res = client.get(f"/dashboard/audits/{presentation.id}")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert "Not enough data" in body


def test_viewing_and_downloading_charts_does_not_consume_extra_credits(client, db_session, make_user, monkeypatch):
    user = make_user(plan_type="subscription_monthly", subscription_status="active", ai_credit_balance=100)
    _make_site(db_session, user)
    _make_gsc_history(db_session, user)
    _make_alert(db_session, user)
    monkeypatch.setattr("app.audits.service.chat_json", lambda system, user_prompt: FAKE_AI_RESULT)

    presentation = build_presentation(user.id, "https://example.com/")
    db_session.refresh(user)
    balance_after_generation = user.ai_credit_balance  # 100 - 5 (costo di generazione)

    _login(client, user)
    client.get(f"/dashboard/audits/{presentation.id}")
    client.get(f"/dashboard/audits/{presentation.id}")
    client.get(f"/dashboard/audits/{presentation.id}/download")

    db_session.refresh(user)
    assert user.ai_credit_balance == balance_after_generation  # invariato: solo rendering, nessun consumo
