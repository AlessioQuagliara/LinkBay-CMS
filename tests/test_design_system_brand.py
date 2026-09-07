"""Design system: la palette del brand (rosso #FF5758, vedi
app/static/css/brand-theme.css) deve applicarsi ovunque — dashboard, billing,
landing, AI credits — non solo alla dashboard come prima di questa modifica.
La landing/AI credits girava sul tema di default della CDN daisyUI (blu/viola,
mai brandizzato) perché non caricava affatto brand-theme.css né impostava
data-theme="linkbay": non c'era alcun colore viola hardcoded da sostituire,
il problema era l'assenza del tema brand su quelle pagine."""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = REPO_ROOT / "app" / "templates"
STATIC = REPO_ROOT / "app" / "static"

FORBIDDEN_BRAND_COLORS = re.compile(r"\b(purple|violet|indigo|fuchsia)\b", re.IGNORECASE)


def _all_text_files(*dirs, suffixes=(".html", ".css", ".js")):
    for d in dirs:
        for path in d.rglob("*"):
            if path.is_file() and path.suffix in suffixes:
                yield path


def test_no_hardcoded_purple_violet_indigo_fuchsia_anywhere():
    # Nessuna occorrenza in tutto templates/ e static/ — non solo nei punti di
    # branding: la ricerca ha già confermato in fase di audit che questi
    # colori non sono mai usati nel codice (il viola veniva dal tema di
    # default della CDN daisyUI, non da una classe/colore scritto a mano).
    offenders = []
    for path in _all_text_files(TEMPLATES, STATIC):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if FORBIDDEN_BRAND_COLORS.search(text):
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == []


def test_brand_theme_defines_the_single_source_of_truth_palette():
    css = (STATIC / "css" / "brand-theme.css").read_text()
    assert "--color-primary: #ff5758" in css
    # Colori semantici invariati — non toccati da questa modifica.
    assert "--color-success:" in css
    assert "--color-warning:" in css
    assert "--color-error:" in css


def test_landing_pages_apply_brand_theme():
    for name in ("index.html", "ai_credits.html", "legal_base.html"):
        html = (TEMPLATES / "landing" / name).read_text()
        assert 'data-theme="linkbay"' in html, f"{name} missing data-theme=linkbay"

    head_assets = (TEMPLATES / "landing" / "partials" / "head-assets.html").read_text()
    assert "brand-theme.css" in head_assets


def test_base_html_still_loads_brand_theme():
    base = (TEMPLATES / "base.html").read_text()
    assert "brand-theme.css" in base
    assert "dashboard-theme.css" not in base  # rinominato, nessun riferimento residuo


def test_start_free_trial_cta_uses_brand_primary_class():
    html = (TEMPLATES / "landing" / "index.html").read_text()
    # Il bottone "Start your free trial" deve usare btn-primary (rosso brand
    # una volta applicato data-theme="linkbay", verificato sopra).
    idx = html.find("Start your free trial")
    assert idx != -1
    surrounding = html[max(0, idx - 300):idx]
    assert "btn-primary" in surrounding


def test_revolut_plan_cards_use_brand_primary_cta():
    for path in (TEMPLATES / "billing" / "upgrade.html", TEMPLATES / "landing" / "index.html"):
        html = path.read_text()
        assert "btn-primary" in html
        assert "Pay with Revolut" in html or "btn-primary" in html


def test_ai_credits_pages_use_brand_primary_icons_and_cta():
    for path in (TEMPLATES / "billing" / "credits.html", TEMPLATES / "landing" / "ai_credits.html"):
        html = path.read_text()
        assert "text-primary" in html  # icone sparkles brandizzate
        assert "btn-primary" in html  # CTA "Pay with Revolut"


# --- rendering effettivo (non solo grep statico) ----------------------------


def test_landing_response_contains_brand_theme_and_no_forbidden_colors(client):
    res = client.get("/")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert 'data-theme="linkbay"' in body
    assert "brand-theme.css" in body
    assert not FORBIDDEN_BRAND_COLORS.search(body)


def test_ai_credits_landing_response_contains_brand_theme(client):
    res = client.get("/ai-credits")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert 'data-theme="linkbay"' in body
    assert "brand-theme.css" in body
