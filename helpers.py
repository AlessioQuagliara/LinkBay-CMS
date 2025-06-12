from flask import session, jsonify
from models import ShopList
from models.cookiepolicy import CookiePolicy
from models.websettings import WebSettings
from models.page import Page
from models.database import db
from models.navbar import NavbarLink
from models.products import Collection
from functools import lru_cache
import logging
from markupsafe import escape
from jinja2 import Template

logging.basicConfig(level=logging.INFO)

# Funzione centralizzata per ottenere il nome del negozio dal sottodominio
def extract_shop_name(shop_subdomain):
    return shop_subdomain.split('.')[0] if '.' in shop_subdomain else shop_subdomain

def check_user_authentication():
    return session.get('username') if 'user_id' in session else None

def get_language():
    return session.get('language', 'en')

@lru_cache(maxsize=50)
def get_web_settings(shop_subdomain):
    """Recupera le impostazioni web per il negozio."""
    shop_name = extract_shop_name(shop_subdomain)
    try:
        return WebSettings.query.filter_by(shop_name=shop_name).first() or WebSettings()  # Restituisce un oggetto vuoto se non trovato
    except Exception as e:
        logging.error(f"Errore nel recupero delle impostazioni web per {shop_name}: {e}")
        return WebSettings()  # Restituisce un oggetto vuoto per evitare errori

def load_page_content(slug, shop_subdomain):
    shop_name = extract_shop_name(shop_subdomain)
    try:
        return Page.query.filter_by(slug=slug, shop_name=shop_name).first()
    except Exception as e:
        logging.error(f"Errore nel recupero della pagina {slug} per {shop_name}: {e}")
        return None

def get_cookie_policy_content(shop_subdomain):
    shop_name = extract_shop_name(shop_subdomain)
    try:
        policy = CookiePolicy.query.filter_by(shop_name=shop_name).first()
        if not policy or policy.use_third_party:
            return ""  # Nessun banner se `use_third_party = 1`

        return f"""
        <div id="cookie-bar" class="card text-white p-3 d-none" 
            style="background-color: {policy.background_color}; 
                position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
                width: auto; max-width: 90%; border-radius: 8px; z-index: 1050;">
            <div class="container text-center">
                <h6>{policy.title}</h6>
                <p class="mb-3">{policy.text_content}</p>
                <div class="d-flex flex-column flex-md-row justify-content-center gap-2">
                    <button id="accept-cookies" class="btn" 
                            style="background-color:{policy.button_color}; 
                                color:{policy.button_text_color};">
                        {policy.button_text}
                    </button>
                    <button id="reject-cookies" class="btn btn-danger">Reject</button>
                </div>
            </div>
        </div>
        """
    except Exception as e:
        logging.error(f"Errore nel recupero della Cookie Policy per {shop_name}: {e}")
        return ""

def render_theme_styles(shop_subdomain, page_slug):
    """
    Recupera gli stili CSS salvati nella colonna 'styles' della tabella 'Page' e li restituisce in un <style>.
    """
    try:
        page = db.session.query(Page).filter_by(slug=page_slug, shop_name=shop_subdomain).first()

        if not page or not page.styles:
            return "<style></style>"  # Nessuno stile trovato

        return f"<style>{page.styles}</style>"
    except Exception as e:
        logging.error(f"Errore nel recupero degli stili per {shop_subdomain}: {e}")
        return "<style></style>"


def get_navbar_content(shop_subdomain):
    shop_name = extract_shop_name(shop_subdomain)
    try:
        navbar = Page.query.filter_by(slug="navbar", shop_name=shop_name).first()
        if not navbar:
            return ""  # Se non esiste una navbar, restituisce stringa vuota

        # Renderizza direttamente il template con Jinja2
        template = Template(navbar.content)
        return template.render()
    except Exception as e:
        logging.error(f"Errore nel recupero della navbar per {shop_name}: {e}")
        return ""

def get_footer_content(shop_subdomain):
    shop_name = extract_shop_name(shop_subdomain)
    try:
        footer = Page.query.filter_by(slug="footer", shop_name=shop_name).first()
        if not footer:
            return ""  # Se non esiste un footer, restituisce stringa vuota

        # Renderizza direttamente il template con Jinja2
        template = Template(footer.content)
        return template.render()
    except Exception as e:
        logging.error(f"Errore nel recupero del footer per {shop_name}: {e}")
        return ""
    