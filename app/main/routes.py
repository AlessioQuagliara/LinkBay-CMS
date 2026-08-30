from datetime import date

from flask import Blueprint, Response, current_app, redirect, render_template, request, session, url_for
from flask_login import current_user

from app.i18n import SUPPORTED_LOCALES

main_bp = Blueprint("main", __name__)

# Dati comuni alle pagine legali. Cambiando qui l'email o l'operatore si
# aggiornano di colpo Terms, Privacy e Cookie policy.
LEGAL_OPERATOR = "LinkBayCMS (Alessio Quagliara)"
LEGAL_CONTACT_EMAIL = "quagliara.alessio@gmail.com"
LEGAL_LAST_UPDATED = "August 9, 2026"


@main_bp.app_context_processor
def inject_site_url():
    """Rende disponibile in ogni template `site_url` (host pubblico canonico,
    senza slash finale), usato per canonical, Open Graph e JSON-LD. Deriva da
    APP_BASE_URL così resta stabile su https://www.linkbay-cms.com anche dietro
    proxy, indipendentemente dall'host con cui arriva la singola richiesta."""
    return {"site_url": _public_base()}


def _public_base():
    return current_app.config.get("APP_BASE_URL", "").rstrip("/")


@main_bp.route("/")
def index():
    return render_template("landing/index.html")


@main_bp.route("/lang/<code>")
def set_locale(code):
    """Cambia lingua (EN/IT). Per chi è loggato persiste su User.locale
    (sovrascritta comunque dalla pagina Settings); per gli anonimi resta
    solo in sessione. Vedi app/i18n.py::get_locale per l'ordine di priorità."""
    if code in SUPPORTED_LOCALES:
        session["locale"] = code
        if current_user.is_authenticated:
            from app.extensions import db

            current_user.locale = code
            db.session.commit()
    return redirect(request.referrer or url_for("main.index"))


def _legal_ctx(page_title, page_description):
    return {
        "page_title": page_title,
        "page_description": page_description,
        "operator": LEGAL_OPERATOR,
        "contact_email": LEGAL_CONTACT_EMAIL,
        "last_updated": LEGAL_LAST_UPDATED,
    }


@main_bp.route("/terms-of-service")
def terms_of_service():
    return render_template(
        "landing/terms.html",
        **_legal_ctx(
            "Terms of Service",
            "The terms that govern your use of LinkBayCMS.",
        ),
    )


@main_bp.route("/privacy-policy")
def privacy_policy():
    return render_template(
        "landing/privacy.html",
        **_legal_ctx(
            "Privacy Policy",
            "How LinkBayCMS collects, uses, and protects your personal data.",
        ),
    )


@main_bp.route("/cookie-policy")
def cookie_policy():
    return render_template(
        "landing/cookie.html",
        **_legal_ctx(
            "Cookie Policy",
            "How LinkBayCMS uses cookies and how to manage your preferences.",
        ),
    )


# Pagine pubbliche e indicizzabili incluse nella sitemap. (endpoint, priority,
# changefreq): l'host assoluto viene anteposto usando APP_BASE_URL.
_SITEMAP_ROUTES = [
    ("main.index", 1.0, "weekly"),
    ("auth.register", 0.8, "monthly"),
]


@main_bp.route("/sitemap.xml")
def sitemap():
    base = _public_base()
    lastmod = date.today().isoformat()
    urls = [
        (base + url_for(endpoint), lastmod, changefreq, priority)
        for endpoint, priority, changefreq in _SITEMAP_ROUTES
    ]
    xml = render_template("sitemap.xml", urls=urls)
    return Response(xml, mimetype="application/xml")


@main_bp.route("/robots.txt")
def robots():
    body = render_template("robots.txt", sitemap_url=_public_base() + url_for("main.sitemap"))
    return Response(body, mimetype="text/plain")
