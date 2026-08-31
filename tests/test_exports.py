"""Export CSV/PDF (app/exports/) — limite export/mese del piano, white label
onorato solo server-side, e un vero smoke test PDF (skippato se WeasyPrint
non trova le librerie di sistema — locale su una macchina senza Docker,
tipicamente macOS senza Pango/Cairo installati)."""
from datetime import date

import pytest

from app.models import PageAlert, ResourceUsageLog


def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


def _make_alert(db_session, user, site_url="https://example.com/", url="https://example.com/page-1"):
    alert = PageAlert(
        user_id=user.id, site_url=site_url, url=url, window_end=date(2026, 1, 1),
        best_month_clicks=100, click_loss_abs=40, click_loss_pct=-40.0,
        position_before=3.0, position_after=8.0, priority_score=90.0,
        reason_text="Traffic dropped.", status="new",
    )
    db_session.add(alert)
    db_session.commit()
    return alert


# --- CSV -------------------------------------------------------------------


def test_declining_csv_returns_header_and_rows(client, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    _make_alert(db_session, user)
    _login(client, user)

    res = client.get("/exports/declining.csv?site=https://example.com/")
    assert res.status_code == 200
    assert res.mimetype == "text/csv"
    assert "attachment" in res.headers["Content-Disposition"]
    body = res.get_data(as_text=True)
    assert body.startswith("url,status,")
    assert "https://example.com/page-1" in body


def test_declining_csv_records_usage(client, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    _login(client, user)
    client.get("/exports/declining.csv?site=https://example.com/").get_data()
    entry = ResourceUsageLog.query.filter_by(user_id=user.id, action="export_csv").first()
    assert entry is not None
    assert entry.site_url == "https://example.com/"


def test_declining_csv_missing_site_param(client, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    _login(client, user)
    res = client.get("/exports/declining.csv")
    assert res.status_code == 400


# --- limite export/mese -----------------------------------------------------


def test_export_blocked_at_monthly_limit(client, db_session, make_user):
    # appsumo_tier1: export_limit_month=1 (dalla richiesta originale).
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    _login(client, user)

    first = client.get("/exports/declining.csv?site=https://example.com/")
    assert first.status_code == 200
    first.get_data()  # consuma lo stream (evita GeneratorExit non gestito dal test client)

    second = client.get("/exports/declining.csv?site=https://example.com/")
    assert second.status_code == 403
    data = second.get_json()
    assert data["error"] == "export_limit_reached"
    assert data["upsell"] is not None


def test_export_unlimited_for_pro_plan(client, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    _login(client, user)
    for _ in range(5):
        res = client.get("/exports/declining.csv?site=https://example.com/")
        assert res.status_code == 200
        res.get_data()


# --- white label -------------------------------------------------------------


def test_report_template_shows_branding_when_not_white_label(app, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", white_label_enabled=False)
    with app.test_request_context():
        html = app.jinja_env.get_template("exports/declining_report.html").render(
            user=user, site_url="https://example.com/", pages=[], white_label=False, generated_at="2026-01-01",
        )
    assert "LinkBayCMS" in html


def test_report_template_hides_branding_when_white_label(app, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", white_label_enabled=True)
    with app.test_request_context():
        html = app.jinja_env.get_template("exports/declining_report.html").render(
            user=user, site_url="https://example.com/", pages=[], white_label=True, generated_at="2026-01-01",
        )
    assert "LinkBayCMS" not in html


def test_white_label_ignored_for_plan_without_it(client, db_session, make_user, monkeypatch):
    # appsumo_tier1 non include white_label (dalla richiesta) — anche se
    # l'utente avesse comunque white_label_enabled=True sul suo record (non
    # dovrebbe succedere da UI, ma è una difesa in profondità da testare),
    # l'export non deve onorarlo.
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", white_label_enabled=True)
    _login(client, user)

    captured = {}

    def fake_build(user, site_url, white_label):
        captured["white_label"] = white_label
        return b"%PDF-fake"

    monkeypatch.setattr("app.exports.routes.build_declining_pages_pdf", fake_build)
    res = client.get("/exports/declining.pdf?site=https://example.com/")
    assert res.status_code == 200
    assert captured["white_label"] is False


def test_white_label_honored_for_plan_with_it(client, db_session, make_user, monkeypatch):
    user = make_user(plan_type="subscription_monthly", subscription_status="active", white_label_enabled=True)
    _login(client, user)

    captured = {}

    def fake_build(user, site_url, white_label):
        captured["white_label"] = white_label
        return b"%PDF-fake"

    monkeypatch.setattr("app.exports.routes.build_declining_pages_pdf", fake_build)
    res = client.get("/exports/declining.pdf?site=https://example.com/")
    assert res.status_code == 200
    assert captured["white_label"] is True
    assert res.mimetype == "application/pdf"


# --- PDF reale (WeasyPrint) --------------------------------------------------


def test_real_pdf_generation_smoke(app, db_session, make_user):
    """Prova vera con WeasyPrint — skippata se le librerie di sistema
    (Pango/Cairo) non sono disponibili sulla macchina che esegue i test
    (tipico su macOS senza Docker); gira per davvero nel container di
    produzione, che le installa (vedi Dockerfile)."""
    from app.exports.pdf_export import build_declining_pages_pdf

    user = make_user(plan_type="subscription_monthly")
    _make_alert(db_session, user)

    with app.test_request_context():
        try:
            pdf_bytes = build_declining_pages_pdf(user, "https://example.com/", white_label=False)
        except OSError as e:
            pytest.skip(f"WeasyPrint system libraries not available: {e}")

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 100
