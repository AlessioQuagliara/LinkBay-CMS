from datetime import date

from flask import Blueprint, Response, current_app, render_template, url_for

main_bp = Blueprint("main", __name__)


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
