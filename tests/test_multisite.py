from app.gsc.sites import (
    add_monitored_site,
    count_active_sites,
    deactivate_monitored_site,
    list_monitored_sites,
)
from app.models import MonitoredSite


def test_add_monitored_site_creates_row(db_session, make_user):
    user = make_user()
    row = add_monitored_site(user.id, "https://example.com/")
    assert row.id is not None
    assert row.is_active is True
    assert count_active_sites(user.id) == 1


def test_add_monitored_site_is_idempotent(db_session, make_user):
    user = make_user()
    add_monitored_site(user.id, "https://example.com/")
    add_monitored_site(user.id, "https://example.com/")
    assert MonitoredSite.query.filter_by(user_id=user.id).count() == 1
    assert count_active_sites(user.id) == 1


def test_deactivate_then_readd_reactivates_same_row(db_session, make_user):
    user = make_user()
    row = add_monitored_site(user.id, "https://example.com/")
    original_id = row.id

    assert deactivate_monitored_site(user.id, "https://example.com/") is True
    assert count_active_sites(user.id) == 0

    reactivated = add_monitored_site(user.id, "https://example.com/")
    assert reactivated.id == original_id
    assert reactivated.is_active is True
    assert MonitoredSite.query.filter_by(user_id=user.id).count() == 1


def test_deactivate_unknown_site_returns_false(db_session, make_user):
    user = make_user()
    assert deactivate_monitored_site(user.id, "https://nope.example.com/") is False


def test_list_monitored_sites_excludes_inactive_by_default(db_session, make_user):
    user = make_user()
    add_monitored_site(user.id, "https://a.example.com/")
    add_monitored_site(user.id, "https://b.example.com/")
    deactivate_monitored_site(user.id, "https://a.example.com/")

    active = list_monitored_sites(user.id)
    assert [row.site_url for row in active] == ["https://b.example.com/"]

    all_rows = list_monitored_sites(user.id, active_only=False)
    assert len(all_rows) == 2


def test_sites_are_scoped_per_user(db_session, make_user):
    user_a = make_user(email="a@example.com")
    user_b = make_user(email="b@example.com")
    add_monitored_site(user_a.id, "https://shared-domain.example.com/")
    add_monitored_site(user_b.id, "https://shared-domain.example.com/")

    assert count_active_sites(user_a.id) == 1
    assert count_active_sites(user_b.id) == 1
