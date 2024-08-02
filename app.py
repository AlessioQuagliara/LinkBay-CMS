from flask import Flask, render_template, redirect, url_for, request, flash, session
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
    return mysql.connector.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME'],
        port=app.config['DB_PORT']
    )

# Includo le rotte
from routes import *

if __name__ == '__main__':
    app.run(debug=True)