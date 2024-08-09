from flask import Flask, render_template, redirect, url_for, request, flash, session, g
from flask_babel import Babel, _
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

babel = Babel(app)

# Selettore di localizzazione
def get_locale():
    selected_locale = request.accept_languages.best_match(app.config['LANGUAGES'])
    return selected_locale

babel.locale_selector_func = get_locale

# Connessione al database "Globale"
def get_db_connection():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME'],
            port=app.config['DB_PORT']
        )
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    close_db_connection()

def close_db_connection(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Funzione per caricare il contenuto della pagina
def load_page_content(slug):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT title, description, keywords, content, language FROM pages WHERE slug = %s", (slug,))
    page = cursor.fetchone()
    cursor.close()
    conn.close()
    return page

# Funzione che renderizza il contenuto dinamico
def render_dynamic_page(slug):
    page = load_page_content(slug)
    if page:
        return render_template('index.html', 
                               title=page['title'], 
                               description=page['description'], 
                               keywords=page['keywords'], 
                               content=page['content'], 
                               language=page['language'])
    else:
        return render_template('404.html'), 404

# Funzione per creare le rotte dinamiche
def create_dynamic_routes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT slug FROM pages")
    pages = cursor.fetchall()
    cursor.close()
    conn.close()

    for page in pages:
        endpoint_name = f"dynamic_page_{page['slug']}"
        app.add_url_rule(f"/{page['slug']}", endpoint=endpoint_name, view_func=lambda slug=page['slug']: render_dynamic_page(slug))


# Creazione delle rotte dinamiche
with app.app_context():
    create_dynamic_routes()

# Includo le rotte
from routes import *

if __name__ == '__main__':
    app.run(debug=True)