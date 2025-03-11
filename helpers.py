from flask import session, request, render_template_string, jsonify
from models import ShopList
from models.cookiepolicy import CookiePolicy
from models.websettings import WebSettings
from db_helpers import DatabaseHelper
import logging
from jinja2 import Template
from sqlalchemy.sql import text

logging.basicConfig(level=logging.INFO)

# Inizializza il gestore del database PostgreSQL
db_helper = DatabaseHelper()

def check_user_authentication():
    """
    Verifica se l'utente è autenticato.
    """
    return session.get('username') if 'user_id' in session else None

def get_language():
    """
    Recupera la lingua corrente dalla sessione.
    """
    return session.get('language', 'en')

def load_page_content(slug, shop_subdomain):
    """
    Carica i contenuti della pagina dinamica dal database PostgreSQL.
    """
    shop_name = shop_subdomain.split('.')[0]  # Rimuove il dominio locale

    query = text("""
        SELECT title, description, keywords, content, language 
        FROM pages 
        WHERE slug = :slug AND shop_name = :shop_name
    """)
    params = {'slug': slug, 'shop_name': shop_name}
    result = db_helper.execute_query(query, params)
    
    return result[0] if result else None

def render_theme_styles(shop_subdomain):
    """
    Recupera le impostazioni web per il negozio e restituisce gli stili CSS personalizzati.
    """
    settings = get_web_settings(shop_subdomain)
    theme_name = settings.get('theme_name', 'Norman').lower()

    # Template CSS dinamici per temi
    themes = {
        'norman': """
            <style>
                .navbar-nav {
                    margin-left: auto; display: flex; align-items: center; gap: 15px;
                }
                .navbar-nav .nav-link {
                    color: #f8f9fa; font-weight: 500; padding: 10px 15px;
                    border-radius: 5px; transition: background 0.3s ease, color 0.3s ease;
                }
                .navbar-nav .nav-link:hover {
                    background: rgba(255, 255, 255, 0.1); color: #ffffff;
                }
                .navbar-toggler-icon { filter: invert(100%); }
            </style>
        """,
        'motion': """
            <style>
                .navbar-nav {
                    margin-left: auto; display: flex; align-items: center; gap: 15px;
                }
                .navbar-nav .nav-link {
                    color: #ffffff; font-weight: 500; padding: 10px 15px;
                    border-radius: 5px; transition: background 0.3s ease, color 0.3s ease;
                }
                .navbar-nav .nav-link:hover {
                    background: rgba(255, 255, 255, 0.2); color: #ffffff;
                }
                .navbar-toggler-icon { filter: invert(100%); }
            </style>
        """
    }

    return themes.get(theme_name, "<style></style>")

def get_web_settings(shop_subdomain):
    """
    Recupera le impostazioni web per il negozio.
    """
    query = text("SELECT * FROM web_settings WHERE shop_name = :shop_name")
    params = {'shop_name': shop_subdomain}
    result = db_helper.execute_query(query, params)
    return result[0] if result else {}

def get_cookie_policy_content(shop_subdomain):
    """
    Recupera il contenuto del banner cookie policy per il negozio.
    """
    query = text("SELECT * FROM cookie_policy WHERE shop_name = :shop_name")
    params = {'shop_name': shop_subdomain}
    result = db_helper.execute_query(query, params)

    if not result or result[0]["use_third_party"] == 1:
        return ""  # Nessun banner se `use_third_party = 1`

    policy = result[0]
    return f"""
        <div id="cookie-bar" class="card text-white p-3 d-none" 
            style="background-color: {policy.get('background_color')}; 
                position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
                width: auto; max-width: 90%; border-radius: 8px; z-index: 1050;">
            <div class="container text-center">
                <h6>{policy.get('title', 'Cookies Policy')}</h6>
                <p class="mb-3">{policy.get('text_content', 'This website uses cookies.')}</p>
                <div class="d-flex flex-column flex-md-row justify-content-center gap-2">
                    <button id="accept-cookies" class="btn" 
                            style="background-color:{policy.get('button_color', '#28a745')}; 
                                color:{policy.get('button_text_color', '#fff')};">
                        {policy.get('button_text', 'Accept')}
                    </button>
                    <button id="reject-cookies" class="btn btn-danger">Reject</button>
                </div>
            </div>
        </div>
    """

def get_navbar_content(shop_subdomain):
    """
    Recupera l'HTML della navbar dal database e sostituisce i link dinamicamente.
    """
    shop_name = shop_subdomain.split('.')[0]

    # Recupera il template della navbar
    query_navbar = text("SELECT content FROM pages WHERE slug = 'navbar' AND shop_name = :shop_name")
    result = db_helper.execute_query(query_navbar, {'shop_name': shop_name})
    navbar_html = result[0]['content'] if result else ''

    # Recupera i link della navbar
    query_links = text("""
        SELECT id, link_text, link_url, link_type, parent_id, position 
        FROM navbar_links WHERE shop_name = :shop_name ORDER BY position ASC
    """)
    links = db_helper.execute_query(query_links, {'shop_name': shop_name})

    # Recupera le collezioni attive per il dropdown
    query_collections = text("SELECT name, slug FROM collections WHERE shop_name = :shop_name AND is_active = TRUE")
    collections = db_helper.execute_query(query_collections, {'shop_name': shop_name})

    if not links or not navbar_html:
        return navbar_html  # Se non ci sono dati dinamici, ritorna l'HTML originale

    # Organizza i link per dropdown
    top_level_links = [link for link in links if link['parent_id'] is None]
    dropdown_links = {link['parent_id']: [] for link in links if link['parent_id']}
    for link in links:
        if link['parent_id']:
            dropdown_links[link['parent_id']].append(link)

    # Costruisci il markup dinamico per i link
    nav_items_html = build_nav_items(top_level_links, dropdown_links, collections)

    # Renderizza il template della navbar
    try:
        template = Template(navbar_html)
        rendered_navbar = template.render(navbar_links=nav_items_html)
    except Exception as e:
        logging.error("Errore nel rendering del template navbar: " + str(e))
        rendered_navbar = navbar_html

    return rendered_navbar

def build_nav_items(top_links, dropdown_links, collections):
    """
    Costruisce la struttura HTML per la navbar, includendo dropdown e icone.
    """
    nav_items_html = ""
    icon_mapping = {
        "cart": "fa-solid fa-cart-shopping",
        "account": "fa-solid fa-user",
        "search": "fa-solid fa-magnifying-glass"
    }

    for link in top_links:
        if link['link_url'] == "show_collections":
            nav_items_html += "<li class='nav-item dropdown'>"
            nav_items_html += f"<a class='nav-link dropdown-toggle' href='#' data-bs-toggle='dropdown'>{link['link_text']}</a>"
            nav_items_html += "<ul class='dropdown-menu'>"
            for collection in collections:
                nav_items_html += f"<li><a class='dropdown-item' href='/collections/{collection['slug']}'>{collection['name']}</a></li>"
            nav_items_html += "</ul></li>"
        elif link['id'] in dropdown_links:
            nav_items_html += f"<li class='nav-item dropdown'><a class='nav-link dropdown-toggle' href='#' data-bs-toggle='dropdown'>{link['link_text']}</a>"
            nav_items_html += "<ul class='dropdown-menu'>"
            for sub_link in dropdown_links[link['id']]:
                nav_items_html += f"<li><a class='dropdown-item' href='{sub_link['link_url']}'>{sub_link['link_text']}</a></li>"
            nav_items_html += "</ul></li>"
        else:
            icon_class = icon_mapping.get(link['link_url'], "")
            nav_items_html += f"<li class='nav-item'><a class='nav-link' href='{link['link_url']}'><i class='{icon_class}'></i></a></li>"

    return nav_items_html

def get_footer_content(shop_subdomain):
    """
    Recupera l'HTML del footer dal database per il negozio specifico.
    """
    shop_name = shop_subdomain.split('.')[0]

    # Recupera il template del footer
    query_footer = "SELECT content FROM pages WHERE slug = 'footer' AND shop_name = :shop_name"
    result = db_helper.execute_query(query_footer, {'shop_name': shop_name})
    footer_html = result[0]['content'] if result else ''

    if not footer_html:
        return ""

    # Renderizza il template del footer
    try:
        template = Template(footer_html)
        rendered_footer = template.render()
    except Exception as e:
        logging.error("Errore nel rendering del template footer: " + str(e))
        rendered_footer = footer_html

    return rendered_footer
