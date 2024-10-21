from flask import Flask, render_template, redirect, url_for, request, flash, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from database import Database 
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

# Funzione per caricare il contenuto della pagina
def load_page_content(slug):
    conn = get_db_connection()
    query = "SELECT title, description, keywords, content, language FROM pages WHERE slug = %s"
    page = db.query(query, (slug,))
    return page[0] if page else None

# Funzione che renderizza il contenuto dinamico
@app.route('/')
@app.route('/<slug>')
def render_dynamic_page(slug=None):
    if slug is None:
        slug = 'home'  # Imposta la pagina predefinita come 'home'

    # Ottieni la connessione al DB e crea l'istanza della classe Page
    db_conn = get_db_connection()
    page_model = Page(db_conn)

    # Carica il contenuto della pagina
    page = page_model.get_page_by_slug(slug)

    # Ottieni la lingua corrente
    language = get_language()

    # Ottieni la navbar e il footer
    navbar_content = page_model.get_navbar()
    footer_content = page_model.get_footer()

    # Ottieni i dati da web_settings
    web_settings_model = WebSettings(db_conn)
    web_settings = web_settings_model.get_web_settings()

    # Estrai 'head', 'script', e 'foot' da web_settings
    head_content = web_settings['head'] if 'head' in web_settings else ''
    script_content = web_settings['script'] if 'script' in web_settings else ''
    foot_content = web_settings['foot'] if 'foot' in web_settings else ''

    if page:
        return render_template('index.html',
                               title=page['title'], 
                               description=page['description'], 
                               keywords=page['keywords'], 
                               content=page['content'], 
                               navbar=navbar_content,  # Passa la navbar al template
                               footer=footer_content,  # Passa il footer al template
                               language=language,
                               head=head_content,  # Passa il contenuto del tag head
                               script=script_content,  # Passa i script personalizzati
                               foot=foot_content)  # Passa il contenuto del footer script
    else:
        return render_template('404.html'), 404
    

# Includo le rotte statiche definite nel file routes.py
from routes import *


if __name__ == '__main__':
    app.run(debug=True)