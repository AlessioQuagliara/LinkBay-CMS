from flask import Flask, g, session, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from logging.handlers import RotatingFileHandler
import openai
from dotenv import load_dotenv
import json

# 📌 Carica le variabili d'ambiente dal file .env
load_dotenv()

# 🔹 Inizializza l'app Flask
app = Flask(__name__)

# 📌 Configura le impostazioni dell'applicazione utilizzando il file config.py
from config import Config
app.config.from_object(Config)

# 📌 Configura la chiave segreta per la sicurezza delle sessioni Flask
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# 🔹 Configura l'API Key di OpenAI se disponibile nelle variabili d'ambiente
openai.api_key = app.config.get('OPENAI_API_KEY')

# 📌 Configura il database PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'postgresql+psycopg2://root:root@localhost/cms_def'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 🔹 Inizializza il gestore del database PostgreSQL personalizzato
from db_helpers import DatabaseHelper
db_helper = DatabaseHelper()

# 📌 Inizializza il database e il sistema di migrazione con Flask-Migrate
from models.database import db
db.init_app(app)
migrate = Migrate(app, db)

# 🔹 Importa i modelli per la gestione del database
from models import (
    User, ShopList, UserStoreAccess, WebSettings, CookiePolicy, Subscription, Agency, 
    AgencyStoreAccess, AgencyEmployee, Opportunity, AgencyOpportunity, 
    OpportunityMessage, StoreInfo, Domain, SiteVisit, SiteVisitIntern, StorePayment, 
    Category, Brand, ProductImage, ProductAttribute, Product, Collection, CollectionImage, CollectionProduct, Order, OrderItem, 
    Payment, PaymentMethod, Shipping, ShippingMethod, Page, NavbarLink, CMSAddon, ShopAddon, 
    ImprovementSuggestion, Contact, SupportTicket, TicketMessage, SuperAdmin, SuperPages, 
    SuperMedia, SuperInvoice, SuperMessages, SuperSupport
)

# 📌 Registrazione dei Blueprint (Modularizzazione delle route)
from blueprints.admin import register_admin_blueprints
from blueprints.shop import register_user_blueprints
from blueprints.api import register_api_blueprints
from blueprints.main import main_bp
from errors import register_error_handlers # Blueprint del sito ufficiale LinkBay

# 📌 Rotta del sito di facciata
from landing import landing_bp
app.register_blueprint(landing_bp, url_prefix='/')  # Serve le route per linkbay-cms.com


app.register_blueprint(main_bp)  # Blueprint per la parte pubblica
register_admin_blueprints(app)   # Blueprint per il pannello admin
register_api_blueprints(app)  # Blueprint per le chiamate
register_user_blueprints(app)    # Blueprint per la gestione utenti
register_error_handlers(app)     # Gestione degli errori personalizzata


# 📌 Chiude la sessione del database al termine della richiesta per ottimizzare le risorse
@app.teardown_appcontext
def teardown_connections(exception):
    """
    Chiude le connessioni al database PostgreSQL quando termina il contesto dell'applicazione.
    Questo aiuta a prevenire problemi di connessione persistente e di memory leak.
    """
    db_helper.close()

# 📌 Rotta per cambiare la lingua dell'applicazione
@app.route('/set-language', methods=['GET'])
def set_language():
    """
    Cambia la lingua corrente dell'utente e la salva nella sessione.
    Il valore della lingua deve essere tra quelle supportate dall'applicazione.
    """
    lang = request.args.get('lang', 'en')
    if lang in app.config['LANGUAGES']:
        session['language'] = lang
        return jsonify({"success": True, "message": f"Language set to {lang}"})
    return jsonify({"success": False, "message": "Invalid language"}), 400

# 📌 Gestione errori di Log
if not os.path.exists('logs'):
    os.mkdir('logs')


file_handler = RotatingFileHandler('logs/linkbay.log', maxBytes=10240, backupCount=5)
file_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] [%(levelname)s] in %(module)s: %(message)s'
))
file_handler.setLevel(logging.INFO)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('✅ LinkBayCMS avviato correttamente.')

# SISTEMA DI TRADUZIONE AUTOMATICA ----------------------------------------------------------------------
TRANSLATIONS_DIR = os.path.join(os.path.dirname(__file__), 'translations')

def load_translations(lang_code):
    try:
        with open(os.path.join(TRANSLATIONS_DIR, f"{lang_code}.json"), 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        with open(os.path.join(TRANSLATIONS_DIR, "en.json"), 'r', encoding='utf-8') as f:
            return json.load(f)

@app.before_request
def before_request():
    lang = request.accept_languages.best_match(['en', 'it', 'es'])  
    g.translations = load_translations(lang)

def translate(key):
    return g.translations.get(key, key)

# 🔁 Rendi disponibile la funzione translate nei template
app.jinja_env.globals.update(translate=translate)

# 📌 Avvio dell'applicazione Flask
if __name__ == "__main__":
    """
    L'app viene eseguita in modalità debug sulla porta 5001.
    L'host è impostato su "0.0.0.0" per consentire l'accesso da remoto se necessario.
    """
    app.run(host="0.0.0.0", port=5001, debug=True)