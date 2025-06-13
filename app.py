from flask import Flask, g, session, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from logging.handlers import RotatingFileHandler
import openai
from dotenv import load_dotenv
import json
from extensions import mail

# 📌 Carica le variabili d'ambiente dal file .env
load_dotenv()

# 🔹 Inizializza l'app Flask
app = Flask(__name__)

# 📌 Aumenta il limite massimo
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

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

# 📌 Prima importiamo le tabelle fondamentali (User e ShopList) per evitare errori di riferimento
from models.user import User
from models.shoplist import ShopList

# 📌 Tabelle collegate agli utenti e ai negozi
from models.userstoreaccess import UserStoreAccess
from models.websettings import WebSettings
from models.cookiepolicy import CookiePolicy
from models.subscription import Subscription

# 📌 Tabelle delle agenzie e dipendenti
from models.agency import Agency
from models.agency import AgencyStoreAccess
from models.agency import AgencyEmployee

# 📌 Tabelle delle opportunità di lavoro
from models.opportunities import Opportunity
from models.opportunities import AgencyOpportunity
from models.opportunities import OpportunityMessage

# 📌 Tabelle relative ai negozi e ai servizi
from models.stores_info import StoreInfo
from models.domain import Domain
from models.site_visits import SiteVisit
from models.site_visit_intern import SiteVisitIntern
from models.storepayment import StorePayment

# 📌 Tabelle relative alla gestione delle categorie e prodotti
from models.products import Product, ProductVariant, ProductImage, Category, Collection, CollectionImage, CollectionProduct
from models.warehouse import Warehouse, Inventory, Location, InventoryMovement

# 📌 Tabelle per gli ordini e pagamenti
from models.orders import Order
from models.orders import OrderItem
from models.payments import Payment
from models.payment_methods import PaymentMethod

# 📌 Tabelle relative alla gestione della spedizione
from models.shipping import Shipping
from models.shippingmethods import ShippingMethod

# 📌 Tabelle per le pagine e il contenuto del CMS
from models.page import Page
from models.navbar import NavbarLink
from models.cmsaddon import CMSAddon
from models.cmsaddon import ShopAddon

# 📌 Tabelle per suggerimenti di miglioramento e contatti
from models.improvement_suggestion import ImprovementSuggestion
from models.contacts import Contact

# 📌 Tabelle per la gestione delle email, ticket di supporto e messaggi
from models.support_tickets import SupportTicket
from models.ticket_messages import TicketMessage
from models.message import ChatMessage
from models.request import uRequests

# 📌 Tabelle per i superadmin
from models.superadmin_models import SuperAdmin
from models.superadmin_models import SuperPages
from models.superadmin_models import SuperMedia
from models.superadmin_models import SuperInvoice
from models.superadmin_models import SuperMessages
from models.superadmin_models import SuperSupport


# 📌 Registrazione dei Blueprint (Modularizzazione delle route)
from blueprints.admin import register_admin_blueprints
from blueprints.shop import register_user_blueprints
from blueprints.api import register_api_blueprints
from blueprints.main import main_bp
from errors import register_error_handlers # Blueprint del sito ufficiale LinkBay


app.register_blueprint(main_bp)  # Blueprint per la parte pubblica
register_admin_blueprints(app)   # Blueprint per il pannello admin
register_api_blueprints(app)  # Blueprint per le chiamate
register_user_blueprints(app)    # Blueprint per la gestione utenti
register_error_handlers(app)     # Gestione degli errori personalizzata

# 📌 Configura Flask-Mail per l'invio della email
mail.init_app(app)


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


if os.getenv('ENVIRONMENT') == 'development':
    file_handler = RotatingFileHandler('logs/linkbay.log', maxBytes=10240, backupCount=5)
else:
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

@app.before_request
def detect_shop():
    hostname = request.host.split(':')[0].lower()

    if hostname.endswith(".localhost") or hostname.endswith(".yoursite-linkbay-cms.com"):
        subdomain = hostname.split('.')[0]
        g.shop_name = subdomain
        g.shop = ShopList.query.filter_by(shop_name=subdomain).first()
    else:
        domain_entry = Domain.query.filter_by(domain=hostname).first()
        if domain_entry:
            g.shop = ShopList.query.get(domain_entry.shop_id)
            g.shop_name = g.shop.shop_name if g.shop else None
        else:
            g.shop = None
            g.shop_name = None

# 📌 Avvio dell'applicazione Flask
if __name__ == "__main__":
    """
    L'app viene eseguita in modalità debug sulla porta 5001.
    L'host è impostato su "0.0.0.0" per consentire l'accesso da remoto se necessario.
    """
    app.run(host="0.0.0.0", port=5001, debug=True)
