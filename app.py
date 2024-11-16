from flask import Flask, render_template, redirect, url_for, request, flash, session, g, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import Database, ShopList, Page, WebSettings, Products  # Importiamo le classi dal tuo models.py
import mysql.connector

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

db = Database(app.config)

@app.route('/set-language', methods=['GET'])
def set_language():
    lang = request.args.get('lang', 'en')
    if lang in app.config['LANGUAGES']:
        session['language'] = lang
        return jsonify({"success": True, "message": f"Language set to {lang}"})
    return jsonify({"success": False, "message": "Invalid language"}), 400

def get_language():
    return session.get('language', 'en') 

# Per chi fa manutenzione = Qui prendo il db dal file db_helper.py, sotto mi connetto al database globale
def get_db_connection():
    if 'db' not in g:
        g.db = db.connect()
    return g.db

def get_auth_db_connection():
    if 'auth_db' not in g:
        g.auth_db = mysql.connector.connect(
            host=app.config['AUTH_DB_HOST'],
            user=app.config['AUTH_DB_USER'],
            password=app.config['AUTH_DB_PASSWORD'],
            database=app.config['AUTH_DB_NAME'],
            port=app.config['AUTH_DB_PORT']
        )
    return g.auth_db

@app.teardown_appcontext
def teardown_db(exception):
    db.close()

@app.teardown_appcontext
def close_db_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
    auth_db = g.pop('auth_db', None)
    if auth_db is not None:
        auth_db.close()

def load_page_content(slug, shop_subdomain):
    conn = get_db_connection()
    page_model = Page(conn)

    # cancellazione ".local" prendendo la stringa
    shop_subdomain = shop_subdomain.split('.')[0]

    # Connessione al Negozio
    auth_conn = get_auth_db_connection()
    shoplist_model = ShopList(auth_conn)
    shop = shoplist_model.get_shop_by_name(shop_subdomain)

    if shop:
        # darti associati
        query = """
        SELECT title, description, keywords, content, language 
        FROM pages 
        WHERE slug = %s AND shop_name = %s
        """
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (slug, shop['shop_name']))
        page = cursor.fetchone()
        cursor.close()

        return page if page else None
    else:
        return None

# Rotta principale
@app.route('/', defaults={'slug': 'home'})
@app.route('/<slug>')
def render_dynamic_page(slug=None):
    # ri-ottengo il sottodominio per problemi
    shop_subdomain = request.host.split('.')[0]

    page = load_page_content(slug, shop_subdomain)

    if page:
        # lingua corrente
        language = get_language()

        # navbar e il footer specifici 
        navbar_content = get_navbar_content(shop_subdomain)
        footer_content = get_footer_content(shop_subdomain)

        # dati da web_settings
        web_settings = get_web_settings(shop_subdomain)

        # 'head', 'script', e 'foot' da web_settings
        head_content = web_settings.get('head', '')
        script_content = web_settings.get('script', '')
        foot_content = web_settings.get('foot', '')

        return render_template('index.html',
                               title=page['title'], 
                               description=page['description'], 
                               keywords=page['keywords'], 
                               content=page['content'], 
                               navbar=navbar_content,  
                               footer=footer_content,  
                               language=language,
                               head=head_content,  
                               script=script_content,  
                               foot=foot_content)  
    else:
        return render_template('404.html'), 404

#  contenuti della navbar
def get_navbar_content(shop_subdomain):
    conn = get_db_connection()  # cms_def
    auth_conn = get_auth_db_connection()  # cms_index
    shoplist_model = ShopList(auth_conn)
    # sottodominio
    shop_subdomain = shop_subdomain.split('.')[0]
    shop = shoplist_model.get_shop_by_name(shop_subdomain)

    if shop:
        query = """
        SELECT content FROM pages 
        WHERE slug = 'navbar' AND shop_name = %s
        """
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (shop['shop_name'],))
        navbar = cursor.fetchone()
        cursor.close()

        return navbar['content'] if navbar else ''
    else:
        return ''

# footer
def get_footer_content(shop_subdomain):
    conn = get_db_connection()  # cms_def
    auth_conn = get_auth_db_connection()  # cms_index
    shoplist_model = ShopList(auth_conn)
    # cancello ".local"
    shop_subdomain = shop_subdomain.split('.')[0]
    shop = shoplist_model.get_shop_by_name(shop_subdomain)

    if shop:
        query = """
        SELECT content FROM pages 
        WHERE slug = 'footer' AND shop_name = %s
        """
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (shop['shop_name'],))
        footer = cursor.fetchone()
        cursor.close()

        return footer['content'] if footer else ''
    else:
        return ''

# impostazioni web del negozio
def get_web_settings(shop_subdomain):
    conn = get_db_connection()
    web_settings_model = WebSettings(conn)
    
    query = """
    SELECT * FROM web_settings 
    WHERE shop_name = %s
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (shop_subdomain,))
    settings = cursor.fetchone()
    cursor.close()

    return settings if settings else {}

# rotte statiche 
from routes import *


if __name__ == '__main__':
    #app.run(ssl_context=('cert.pem', 'key.pem'), host="0.0.0.0", port=443)
    app.run(debug=True)