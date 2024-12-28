from flask import session
from models import ShopList, WebSettings, Page
from db_helpers import DatabaseHelper

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


def get_navbar_content(shop_subdomain):
    """
    Recupera il contenuto della navbar specifico per il negozio.
    """
    conn = db_helper.get_db_connection()
    auth_conn = db_helper.get_auth_db_connection()
    shoplist_model = ShopList(auth_conn)

    shop_subdomain = shop_subdomain.split('.')[0]
    shop = shoplist_model.get_shop_by_name(shop_subdomain)

    if shop:
        query = """
        SELECT content FROM pages 
        WHERE slug = 'navbar' AND shop_name = %s
        """
        params = (shop['shop_name'],)
        result = db_helper.execute_query(query, params)
        return result[0]['content'] if result else ''
    return ''


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