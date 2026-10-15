"""Digest email del lunedì con le top declining pages dell'utente.

Gira da CLI (flask send-weekly-digest, schedulato dal servizio "cron"), fuori
da una request: niente sessione, quindi la lingua va forzata esplicitamente
con la preferenza salvata dell'utente (User.locale), non dedotta da
Accept-Language o dalla sessione come fa app/i18n.py::get_locale durante una
richiesta web normale.
"""
from flask import current_app, render_template
from flask_babel import force_locale

from app.emails import send_email
from app.models import PageAlert

TOP_N = 5


def build_top_declining(user_id, site_url):
    """Le pagine "new" con priorità più alta per (utente, sito) — stessa query
    di app/alerts/routes.py::api_list, limitata alle top N."""
    return (
        PageAlert.query.filter_by(user_id=user_id, site_url=site_url, status="new")
        .order_by(PageAlert.priority_score.desc())
        .limit(TOP_N)
        .all()
    )


def send_weekly_digest_for_user(user, site_url):
    """Invia il digest a `user` per `site_url`. Non invia nulla se non ci sono
    pagine "new" da segnalare (niente email vuote). Ritorna None se saltato
    (nessun alert — non è un errore), altrimenti True/False a seconda
    dell'esito dell'invio: i due casi vanno tenuti distinti dal chiamante,
    "niente da segnalare" non è la stessa cosa di "invio fallito"."""
    pages = build_top_declining(user.id, site_url)
    if not pages:
        return None

    base_url = (current_app.config.get("APP_BASE_URL") or "").rstrip("/")
    dashboard_url = base_url + "/dashboard/declining"

    with force_locale(user.locale):
        html = render_template(
            "emails/weekly_digest.html",
            name=user.name,
            site_url=site_url,
            pages=pages,
            dashboard_url=dashboard_url,
            locale=user.locale,
        )
        from flask_babel import gettext as _

        subject = _("Your top declining pages this week")

    return send_email(user.email, subject, html)
