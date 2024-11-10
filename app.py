from flask import Flask, render_template, redirect, url_for, request, flash, session, g, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import Database, User, ShopList, Page, WebSettings  # Importiamo le classi dal tuo models.py
import mysql.connector

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Crea un'istanza della classe Database
db = Database(app.config)

# Selettore di localizzazione tramite richiesta
@app.route('/set-language', methods=['GET'])
def set_language():
    lang = request.args.get('lang', 'en')  # Imposta 'en' come predefinito
    if lang in app.config['LANGUAGES']:
        session['language'] = lang
        return jsonify({"success": True, "message": f"Language set to {lang}"})
    return jsonify({"success": False, "message": "Invalid language"}), 400

# Funzione per ottenere la lingua corrente
def get_language():
    return session.get('language', 'en')  # 'en' come predefinito se non è impostato

# Connessione al database tramite la classe Database
def get_db_connection():
    if 'db' not in g:
        g.db = db.connect()
    return g.db

# Connessione al database globale
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

# Funzione per caricare il contenuto della pagina in base al sottodominio
def load_page_content(slug, shop_subdomain):
    # Connessione per i dati della pagina (usa cms_def)
    conn = get_db_connection()
    page_model = Page(conn)

    # Rimuovi ".local" dal sottodominio
    shop_subdomain = shop_subdomain.split('.')[0]

    # Usa la connessione al database cms_index per recuperare il negozio
    auth_conn = get_auth_db_connection()
    shoplist_model = ShopList(auth_conn)
    shop = shoplist_model.get_shop_by_name(shop_subdomain)

    if shop:
        # Carica i dati della pagina associati al negozio dal database cms_def
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

# Rotta per gestire i negozi in base al sottodominio
@app.route('/', defaults={'slug': 'home'})
@app.route('/<slug>')
def render_dynamic_page(slug=None):
    # Ottieni il sottodominio dalla richiesta (prima parte del request.host)
    shop_subdomain = request.host.split('.')[0]

    # Carica il contenuto della pagina per il negozio e il sottodominio
    page = load_page_content(slug, shop_subdomain)

    if page:
        # Ottieni la lingua corrente
        language = get_language()

        # Ottieni la navbar e il footer specifici per il negozio
        navbar_content = get_navbar_content(shop_subdomain)
        footer_content = get_footer_content(shop_subdomain)

        # Ottieni i dati da web_settings
        web_settings = get_web_settings(shop_subdomain)

        # Estrai 'head', 'script', e 'foot' da web_settings
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

# Funzione per ottenere i contenuti della navbar
def get_navbar_content(shop_subdomain):
    conn = get_db_connection()  # Connessione al database cms_def
    auth_conn = get_auth_db_connection()  # Connessione al database cms_index
    shoplist_model = ShopList(auth_conn)
    # Rimuovi ".local" dal sottodominio
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

# Funzione per ottenere i contenuti del footer
def get_footer_content(shop_subdomain):
    conn = get_db_connection()  # Connessione al database cms_def
    auth_conn = get_auth_db_connection()  # Connessione al database cms_index
    shoplist_model = ShopList(auth_conn)
    # Rimuovi ".local" dal sottodominio
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

# Funzione per ottenere le impostazioni web del negozio
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

# Includo le rotte statiche definite nel file routes.py
from routes import *


if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), host="0.0.0.0", port=443)