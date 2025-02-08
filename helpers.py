from flask import session, request
from models import ShopList
from models.cookiepolicy import CookiePolicy
from models.websettings import WebSettings
from db_helpers import DatabaseHelper
import re
from jinja2 import Template
import logging
logging.basicConfig(level=logging.INFO)

# Inizializza il gestore del database
db_helper = DatabaseHelper()

def check_user_authentication():
    """
    Verifica se l'utente è autenticato.
    """
    if 'user_id' not in session:
        return None
    return session.get('username')


def get_language():
    """
    Recupera la lingua corrente dalla sessione.
    """
    return session.get('language', 'en')


def load_page_content(slug, shop_subdomain):
    """
    Carica i contenuti della pagina dinamica dal database.
    """
    conn = db_helper.get_db_connection()
    shop_subdomain = shop_subdomain.split('.')[0]  # Rimuove il dominio locale
    auth_conn = db_helper.get_auth_db_connection()

    # Ottieni il negozio
    shoplist_model = ShopList(auth_conn)
    shop = shoplist_model.get_shop_by_name(shop_subdomain)

    if shop:
        query = """
        SELECT title, description, keywords, content, language 
        FROM pages 
        WHERE slug = %s AND shop_name = %s
        """
        params = (slug, shop['shop_name'])
        result = db_helper.execute_query(query, params)
        return result[0] if result else None
    return None

def render_theme_styles(shop_subdomain):
    """
    Recupera le impostazioni web per lo shop e, in base al valore di 'theme_name',
    restituisce uno style block con stili personalizzati.
    """
    # Recupera le impostazioni web dallo shop (funzione già definita)
    settings = get_web_settings(shop_subdomain)
    # Estrai il nome del tema; se non esiste, usa 'default'
    theme_name = settings.get('theme_name', 'Norman').lower()
    
    # Definisci dei template CSS per i vari temi
    if theme_name == 'norman':
        style_template = """
        <style>
        /* Stile per .navbar-nav dentro una navbar scura */
            .navbar-nav {
                margin-left: auto; /* Spinge i link a destra */
                display: flex;
                align-items: center;
                gap: 15px;
            }

            /* Stile per i link nella navbar */
            .navbar-nav .nav-link {
                color: #f8f9fa; /* Bianco Bootstrap */
                font-weight: 500;
                padding: 10px 15px;
                border-radius: 5px;
                transition: background 0.3s ease, color 0.3s ease;
            }

            /* Effetto hover per i link */
            .navbar-nav .nav-link:hover {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
            }

            /* Stile per la dropdown */
            .navbar-nav .dropdown-menu {
                background-color: #343a40; /* Dark grey */
                border: none;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
            }

            /* Stile per gli elementi della dropdown */
            .navbar-nav .dropdown-item {
                color: #f8f9fa;
                transition: background 0.3s ease, color 0.3s ease;
            }

            /* Effetto hover sulla dropdown */
            .navbar-nav .dropdown-item:hover {
                background-color: #495057;
                color: #ffffff;
            }

            /* Stile per la navbar toggler (mobile) */
            .navbar-toggler {
                border: none;
            }

            /* Icona toggler bianca */
            .navbar-toggler-icon {
                filter: invert(100%);
            }
        </style>
        """
    elif theme_name == 'motion':
        style_template = """
        <style>
            /* Stile per .navbar-nav dentro una navbar blu */
            .navbar-nav {
                margin-left: auto; /* Spinge i link a destra */
                display: flex;
                align-items: center;
                gap: 15px;
            }

            /* Stile per i link nella navbar */
            .navbar-nav .nav-link {
                color: #ffffff; /* Testo bianco per contrasto */
                font-weight: 500;
                padding: 10px 15px;
                border-radius: 5px;
                transition: background 0.3s ease, color 0.3s ease;
            }

            /* Effetto hover per i link */
            .navbar-nav .nav-link:hover {
                background: rgba(255, 255, 255, 0.2);
                color: #ffffff;
            }

            /* Stile per la dropdown */
            .navbar-nav .dropdown-menu {
                background-color: #002244; /* Blu più scuro */
                border: none;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
            }

            /* Stile per gli elementi della dropdown */
            .navbar-nav .dropdown-item {
                color: #ffffff;
                transition: background 0.3s ease, color 0.3s ease;
            }

            /* Effetto hover sulla dropdown */
            .navbar-nav .dropdown-item:hover {
                background-color: #004080;
                color: #ffffff;
            }

            /* Stile per la navbar toggler (mobile) */
            .navbar-toggler {
                border: none;
            }

            /* Icona toggler bianca */
            .navbar-toggler-icon {
                filter: invert(100%);
            }
        </style>
        """
    else:
        # Default theme: stili base
        style_template = """
        <style>
        </style>
        """
    
    # Usa Jinja2 per renderizzare il template (qui è statico, ma potresti aggiungere variabili dinamiche se serve)
    try:
        template = Template(style_template)
        rendered_style = template.render()
    except Exception as e:
        logging.error("Errore nel rendering del tema: " + str(e))
        rendered_style = style_template  # Fallback: usa il template statico
    return rendered_style

def render_navbar_template(navbar_html, nav_links_html):
    try:
        template = Template(navbar_html)
        # Il dizionario 'context' contiene le variabili da iniettare nel template
        context = {'navbar_links': nav_links_html}
        return template.render(**context)
    except Exception as e:
        logging.error("Errore nel rendering del template navbar: " + str(e))
        return navbar_html  # Fallback: restituisce l'HTML originale
    
def build_nav_items(top_links, dropdown_links, collections):
    nav_items_html = ""
    
    # Mappa per associare link_url a classi di icone
    icon_mapping = {
        "cart": "fa-solid fa-cart-shopping",
        "account": "fa-solid fa-user",
        "search": "fa-solid fa-magnifying-glass"
    }

    for link in top_links:
        if link['link_url'] == "show_collections":
            nav_items_html += f"""
                <li class='nav-item dropdown'>
                    <a class='nav-link dropdown-toggle' href='#' id='dropdown-collections' role='button' data-bs-toggle='dropdown' aria-expanded='false'>
                        {link['link_text']}
                    </a>
                    <ul class='dropdown-menu' aria-labelledby='dropdown-collections'>
            """
            for collection in collections:
                nav_items_html += f"<li><a class='dropdown-item' href='/collections/{collection['slug']}'>{collection['name']}</a></li>"
            nav_items_html += "</ul></li>"
        elif link['id'] in dropdown_links:
            nav_items_html += f"""
                <li class='nav-item dropdown'>
                    <a class='nav-link dropdown-toggle' href='#' id='dropdown-{link['id']}' role='button' data-bs-toggle='dropdown' aria-expanded='false'>
                        {link['link_text']}
                    </a>
                    <ul class='dropdown-menu' aria-labelledby='dropdown-{link['id']}'>
            """
            for sub_link in dropdown_links[link['id']]:
                nav_items_html += f"<li><a class='dropdown-item' href='{sub_link['link_url']}'>{sub_link['link_text']}</a></li>"
            nav_items_html += "</ul></li>"
        elif link['link_url'] in ["cart", "account", "search"]:
            # Recupera la classe icona dalla mappa; se non presente, usa una stringa vuota
            icon_class = icon_mapping.get(link['link_url'], "")
            # Genera l'HTML con l'icona; in questo esempio, aggiungo anche l'href uguale al link_url per eventuale navigazione
            nav_items_html += f"<li class='nav-item'><a class='nav-link' id='{link['link_url']}'><i class='{icon_class}'></i></a></li>"
        else:
            nav_items_html += f'<li class="nav-item"><a class="nav-link" href="{link["link_url"]}">{link["link_text"]}</a></li>'
    return nav_items_html


def get_navbar_content(shop_subdomain):
    """
    Recupera l'HTML della navbar dal database e sostituisce dinamicamente il placeholder con i link generati.
    """
    conn = db_helper.get_db_connection()
    shop_name = shop_subdomain.split('.')[0]

    # Recupera il template della navbar dalla tabella 'pages'
    query_navbar = "SELECT content FROM pages WHERE slug = 'navbar' AND shop_name = %s"
    result = db_helper.execute_query(query_navbar, (shop_name,))
    navbar_html = result[0]['content'] if result else ''

    # Recupera i link della navbar dalla tabella 'navbar_links'
    query_links = """
        SELECT id, link_text, link_url, link_type, parent_id, position 
        FROM navbar_links 
        WHERE shop_name = %s 
        ORDER BY position ASC
    """
    links = db_helper.execute_query(query_links, (shop_name,))

    # Recupera le collezioni attive per il dropdown
    query_collections = """
        SELECT name, slug FROM collections 
        WHERE shop_name = %s AND is_active = 1
    """
    collections = db_helper.execute_query(query_collections, (shop_name,))

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

    # Renderizza il template della navbar usando Jinja2 e il contesto dinamico
    from jinja2 import Template
    try:
        template = Template(navbar_html)
        rendered_navbar = template.render(navbar_links=nav_items_html)
    except Exception as e:
        logging.error("Errore nel rendering del template navbar: " + str(e))
        rendered_navbar = navbar_html

    return rendered_navbar


def get_footer_content(shop_subdomain):
    """
    Recupera il contenuto del footer specifico per il negozio.
    """
    conn = db_helper.get_db_connection()
    auth_conn = db_helper.get_auth_db_connection()
    shoplist_model = ShopList(auth_conn)

    shop_subdomain = shop_subdomain.split('.')[0]
    shop = shoplist_model.get_shop_by_name(shop_subdomain)

    if shop:
        query = """
        SELECT content FROM pages 
        WHERE slug = 'footer' AND shop_name = %s
        """
        params = (shop['shop_name'],)
        result = db_helper.execute_query(query, params)
        return result[0]['content'] if result else ''
    return ''


def get_web_settings(shop_subdomain):
    """
    Recupera le impostazioni web specifiche per il negozio.
    """
    conn = db_helper.get_db_connection()
    query = """
    SELECT * FROM web_settings 
    WHERE shop_name = %s
    """
    params = (shop_subdomain,)
    result = db_helper.execute_query(query, params)
    return result[0] if result else {}

def get_cookie_policy_content(shop_subdomain):
    """
    Recupera il contenuto HTML del banner cookie policy per il negozio.
    """
    conn = db_helper.get_db_connection()
    cookie_model = CookiePolicy(conn)

    shop_name = shop_subdomain.split('.')[0]
    cookie_data = cookie_model.get_cookie_policy(shop_name)


    if not cookie_data or int(cookie_data["use_third_party"]) == 1:
        return ""  # Nessun banner se `use_third_party = 1` o dati mancanti

    # Genera l'HTML del banner cookie
    return f"""
        <div id="cookie-bar" class="card text-white p-3 d-none" 
            style="background-color: {cookie_data.get('background_color')}; 
                position: fixed; bottom: 20px; left: 50%; 
                transform: translateX(-50%); width: auto; max-width: 90%; 
                border-radius: 8px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); 
                z-index: 1050;">
            <div class="container text-center">
                <h6>{cookie_data.get('title', 'Cookies Policy')}</h6>
                <p class="mb-3">{cookie_data.get('text_content', 'This website uses cookies to enhance user experience.')}</p>
                <div class="d-flex flex-column flex-md-row justify-content-center gap-2">
                    <button id="accept-cookies" class="btn" 
                            style="background-color:{cookie_data.get('button_color', '#28a745')}; 
                                color:{cookie_data.get('button_text_color', '#fff')};">
                        {cookie_data.get('button_text', 'Accept')}
                    </button>
                    <button id="reject-cookies" class="btn btn-danger">Reject</button>
                </div>
            </div>
        </div>
    """