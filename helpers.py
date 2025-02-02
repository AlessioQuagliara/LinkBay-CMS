from flask import session, request
from models import ShopList
from models.cookiepolicy import CookiePolicy
from db_helpers import DatabaseHelper
import re

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


import re
from flask import request
from db_helpers import DatabaseHelper

db_helper = DatabaseHelper()

def get_navbar_content(shop_subdomain):
    """
    Recupera l'HTML della navbar da `pages.content` e inserisce dinamicamente i link, comandi speciali e azioni.
    """
    conn = db_helper.get_db_connection()
    shop_name = shop_subdomain.split('.')[0]

    # Recupera l'HTML della navbar dalla tabella `pages`
    query_navbar = "SELECT content FROM pages WHERE slug = 'navbar' AND shop_name = %s"
    result = db_helper.execute_query(query_navbar, (shop_name,))
    navbar_html = result[0]['content'] if result else ''

    # Recupera i link della navbar dalla tabella `navbar_links`
    query_links = """
        SELECT id, link_text, link_url, link_type, parent_id, position 
        FROM navbar_links 
        WHERE shop_name = %s 
        ORDER BY position ASC
    """
    links = db_helper.execute_query(query_links, (shop_name,))
    
    if not links or not navbar_html:
        return navbar_html  # Se non ci sono link o navbar, restituiamo l'HTML originale

    # Recupera le collezioni attive per il dropdown
    query_collections = """
        SELECT name, slug FROM collections 
        WHERE shop_name = %s AND is_active = 1
    """
    collections = db_helper.execute_query(query_collections, (shop_name,))

    # Organizzazione dei link per dropdown
    top_level_links = [link for link in links if link['parent_id'] is None]
    dropdown_links = {link['parent_id']: [] for link in links if link['parent_id']}

    for link in links:
        if link['parent_id']:
            dropdown_links[link['parent_id']].append(link)

    # **Generazione dell'HTML della navbar**
    nav_items_html = ""

    for link in top_level_links:
        # **Dropdown automatico per le collezioni**
        if link['link_url'] == "show_collections":
            nav_items_html += """""
                <li class='nav-item dropdown'>
                    <a class='nav-link dropdown-toggle' href='#' id="dropdown-collections' role='button' data-bs-toggle='dropdown' aria-expanded='false'>
                        Collections
                    </a>
                    <ul class='dropdown-menu' aria-labelledby='dropdown-collections'>
            """
            for collection in collections:
                nav_items_html += f"<li><a class='dropdown-item' href='/collections/{collection['slug']}'>{collection['name']}</a></li>"
            nav_items_html += "</ul></li>"

        # **Dropdown personalizzati**
        elif link['id'] in dropdown_links:
            nav_items_html += f'''
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="dropdown-{link['id']}" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        {link['link_text']}
                    </a>
                    <ul class="dropdown-menu" aria-labelledby="dropdown-{link['id']}">
            '''
            for sub_link in dropdown_links[link['id']]:
                nav_items_html += f"<li><a class='dropdown-item' href='{sub_link['link_url']}'>{sub_link['link_text']}</a></li>"
            nav_items_html += "</ul></li>"

        # **Azioni speciali senza link ma con ID**
        elif link['link_url'] in ["cart", "account", "search"]:
            nav_items_html += f"<li class='nav-item'><a class='nav-link' id='{link['link_url']}'>{link['link_text']}</a></li>"

        # **Link standard**
        else:
            nav_items_html += f'<li class="nav-item"><a class="nav-link" href="{link["link_url"]}">{link["link_text"]}</a></li>'

    # **Sostituzione dinamica dell'HTML nella navbar**
    navbar_html = re.sub(r"<ul class=\"navbar-nav.*?</ul>", f"<ul class='navbar-nav ms-auto'>{nav_items_html}</ul>", navbar_html, flags=re.DOTALL)

    return navbar_html


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