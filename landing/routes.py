from flask import render_template, request, jsonify, redirect, url_for, session, Response, flash
from flask import current_app
from flask_mail import Message
from extensions import mail
from models.request import uRequests, create_request
from datetime import datetime
from . import landing_bp
from models.database import db
from models.user import User
from models.shoplist import ShopList
from models.userstoreaccess import UserStoreAccess
from models.subscription import Subscription
from models.orders import Order
from models.support_tickets import SupportTicket
from models.cmsaddon import CMSAddon
from models.cmsaddon import ShopAddon
from models.site_visits import SiteVisit
from models.stores_info import StoreInfo
from models.websettings import WebSettings
from models.domain import Domain
from models.improvement_suggestion import ImprovementSuggestion
from sqlalchemy import func
from werkzeug.security import check_password_hash
import json
import logging
from flask import g
import os
from datetime import datetime, timedelta
from flask import send_file
from dotenv import load_dotenv

load_dotenv()

@landing_bp.before_request
def set_shop_name():
    # Ottieni shop_name solo quando esiste un contesto di richiesta
    if request.host:
        g.shop_name = request.host.split(':')[0].lower()
    else:
        g.shop_name = "default_shop"  # Valore di fallback

def load_release_notes(language="it"):
    try:
        with open("release_note.json", "r", encoding="utf-8") as f:
            all_notes = json.load(f)
            return [note for note in all_notes if note["lang"] == language]
    except Exception as e:
        logging.error(f"❌ Errore nel caricamento delle note di rilascio: {e}")
        return []

@landing_bp.route('/')
def home():
    return render_template('landing/landing_home.html')

@landing_bp.route('/partner')
def partner():
    return render_template('landing/partner.html')

@landing_bp.route('/price')
def prices():
    return render_template('landing/price.html')

@landing_bp.route('/integration')
def integration():
    return render_template('landing/integration.html')

@landing_bp.route('/login')
def login():
    return render_template('landing/login.html')

@landing_bp.route('/login', methods=['POST'])
def login_post():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.nome
            session['profile_photo'] = user.profilo_foto

            return jsonify(success=True, message="Login effettuato con successo!", redirect='/dashboard')
        else:
            return jsonify(success=False, message="Email o password non validi."), 401
    else:
        return redirect(url_for('landing.login'))
    
@landing_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    user = User.query.get(session['user_id'])  # Recupera l'oggetto utente
    if not user:
        return redirect(url_for('landing.login'))
    
    lang = session.get('lang', 'it')  # oppure rilevato da intestazione browser
    release_notes = load_release_notes(lang)

    return render_template('landing/dashboard.html', user=user, notes=release_notes)

@landing_bp.route('/dashboard/stores')
def dashboard_stores():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    user_id = session['user_id']

    # Recupera negozi di proprietà
    owned_shops = ShopList.query.filter_by(user_id=user_id).all()

    # Recupera accessi aggiuntivi
    access_entries = UserStoreAccess.query.filter_by(user_id=user_id).all()
    access_map = {entry.shop_id: entry.access_level for entry in access_entries}

    # Recupera tutti i negozi accessibili (anche quelli posseduti già compresi)
    access_shop_ids = list(access_map.keys())
    accessible_shops = ShopList.query.filter(ShopList.id.in_(access_shop_ids)).all()

    # Merge negozi
    all_shops = {}

    # Inserisce i negozi di proprietà come admin
    for shop in owned_shops:
        s_dict = shop.to_dict()
        s_dict['access_level'] = 'admin'  # Proprietario = admin
        all_shops[shop.id] = s_dict

    # Inserisce negozi accessibili da altri ruoli (editor/viewer)
    for shop in accessible_shops:
        if shop.id not in all_shops:
            s_dict = shop.to_dict()
            s_dict['access_level'] = access_map.get(shop.id, 'viewer')  # fallback viewer
            all_shops[shop.id] = s_dict

    # Aggiunge l'abbonamento
    for shop in all_shops.values():
        subscription = Subscription.query.filter_by(shop_name=shop['shop_name'], user_id=user_id).first()
        shop['subscription'] = subscription.to_dict() if subscription else None

        # VISITE RESTANTI per piano Freemium
        if not subscription or (subscription and subscription.plan_name == "Freemium"):

            now = datetime.utcnow()
            start_month = datetime(now.year, now.month, 1)

            visit_count = db.session.query(func.count(SiteVisit.id)).filter(
                SiteVisit.shop_name == shop['shop_name'],
                SiteVisit.visit_time >= start_month
            ).scalar()

            shop['visits_left'] = max(0, 1000 - visit_count)
        else:
            shop['visits_left'] = None

    # Aggiungo la variabile di sviluppo
    variable = os.getenv('ENVIRONMENT')

    return render_template(
        'landing/dashboard_shop.html',
        user=get_user_from_session(),
        shops=list(all_shops.values()),
        variable=variable,  # Variabile di ambiente per sviluppo
    )

@landing_bp.route('/dashboard/chats')
def dashboard_chats_list():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    user_id = session['user_id']

    # Tutti gli altri utenti
    chat_users = User.query.filter(User.id != user_id).all()

    # Recupera conteggio messaggi non letti per ciascun utente
    from models.message import ChatMessage
    unread_counts = (
        db.session.query(ChatMessage.sender_id, db.func.count(ChatMessage.id))
        .filter(ChatMessage.receiver_id == user_id, ChatMessage.is_read == False)
        .group_by(ChatMessage.sender_id)
        .all()
    )
    # Crea un dizionario {sender_id: count}
    unread_dict = {sender_id: count for sender_id, count in unread_counts}

    # Aggiunge il campo unread_count a ogni utente
    for u in chat_users:
        u.unread_count = unread_dict.get(u.id, 0)

    return render_template(
        'landing/dashboard_chats.html',
        user=get_user_from_session(),
        chat_users=chat_users
    )

@landing_bp.route('/dashboard/chat/<int:target_user_id>')
def dashboard_private_chat(target_user_id):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    target_user = User.query.get(target_user_id)
    if not target_user:
        flash("Utente non trovato.", "warning")
        return redirect(url_for('landing.dashboard_team'))

    return render_template(
        'landing/dashboard_private_chat.html',
        user=get_user_from_session(),
        target_user=target_user
    )


@landing_bp.route('/dashboard/team/user/<int:user_id>')
def dashboard_user_profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    user = User.query.get(user_id)
    if not user:
        flash("Utente non trovato.", "warning")
        return redirect(url_for('landing.dashboard_team'))

    # Ottieni shop_name dal contesto g
    shop_name = g.get('shop_name', 'default_shop')
    
    # Recupera i negozi dell'utente filtrati per nome
    shops = ShopList.query.filter_by(
        user_id=user_id,
        shop_name=shop_name
    ).all()

    # Statistiche filtrate per shop_id dei negozi trovati
    total_revenue = 0
    total_orders = 0
    shop_ids = [shop.id for shop in shops]  # Lista di ID negozi

    if shop_ids:  # Solo se ci sono negozi
        orders = Order.query.filter(Order.shop_id.in_(shop_ids)).all()
        for order in orders:
            total_revenue += order.total_amount or 0
            total_orders += 1

    return render_template(
        'landing/dashboard_user_profile.html',
        user=get_user_from_session(),
        target_user=user,
        total_revenue=round(total_revenue, 2),
        total_orders=total_orders,
        shops=shops
    )


@landing_bp.route('/dashboard/sales')
def dashboard_sales():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    return render_template('landing/dashboard_sell.html', user=get_user_from_session())

@landing_bp.route('/dashboard/themes')
def dashboard_themes():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    themes_dir = os.path.join(os.getcwd(), 'themes')
    json_themes = []

    try:
        for filename in os.listdir(themes_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(themes_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                    theme_name = os.path.splitext(filename)[0]
                    json_themes.append({
                        'name': theme_name,
                        'data': theme_data
                    })
    except Exception as e:
        logging.error(f"Errore nel caricamento dei temi da cartella: {e}")

    return render_template(
        'landing/dashboard_themes.html',
        user=get_user_from_session(),
        json_themes=json_themes  # 👈 qui la lista dei temi da visualizzare
    )

@landing_bp.route('/dashboard/support')
def dashboard_support():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_support.html', user=get_user_from_session())

@landing_bp.route('/dashboard/payouts')
def dashboard_payments():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_payments.html', user=get_user_from_session())

# 💳 Stripe - Configurazione pagamento
@landing_bp.route('/dashboard/payments/stripe/<shop_name>')
def dashboard_payment_stripe(shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_payment_stripe.html', user=get_user_from_session(), shop_name=shop_name)

# 💳 PayPal - Configurazione pagamento
@landing_bp.route('/dashboard/payments/paypal/<shop_name>')
def dashboard_payment_paypal(shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_payment_paypal.html', user=get_user_from_session(), shop_name=shop_name)

@landing_bp.route('/dashboard/settings')
def dashboard_settings():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    user = User.query.get(session['user_id'])

    if not user:
        flash("Utente non trovato.", "danger")
        return redirect(url_for('landing.login'))

    return render_template('landing/dashboard_settings.html', user=user.to_dict())

@landing_bp.route('/subscription/select/<shop_name>')
def subscription_select(shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    # Recupera i dati dello shop
    shop = ShopList.query.filter_by(shop_name=shop_name).first()
    if not shop:
        return redirect(url_for('landing.dashboard_stores'))

    # Verifica se l'utente ha accesso a questo shop
    is_owner = shop.user_id == session['user_id']
    has_access = UserStoreAccess.query.filter_by(shop_id=shop.id, user_id=session['user_id']).first()
    if not is_owner and not has_access:
        return redirect(url_for('landing.dashboard_stores'))

    return render_template('landing/dashboard_shop_plan.html', user=get_user_from_session(), shop_name=shop_name)

def get_user_from_session():
    return {
        "id": session.get('user_id'),
        "email": session.get('user_email'),
        "nome": session.get('user_name'),
        "profilo_foto": session.get('user_avatar', '')
    }

@landing_bp.route('/logout')
def logout():
    session.clear()  # Elimina tutti i dati della sessione
    return redirect(url_for('landing.login'))  # Reindirizza alla pagina di login


@landing_bp.route('/dashboard/support/chat/<int:ticket_id>')
def dashboard_support_chat(ticket_id):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    ticket = SupportTicket.query.filter_by(id=ticket_id, user_id=session['user_id']).first()
    if not ticket:
        return redirect(url_for('landing.dashboard_support'))

    return render_template('landing/dashboard_support_chat.html', user=get_user_from_session(), ticket=ticket)

@landing_bp.route('/preview-theme/<theme_name>')
def preview_theme(theme_name):

    # Path assoluto della cartella Themes
    base_dir = os.path.dirname(os.path.abspath(__file__))
    themes_dir = os.path.abspath(os.path.join(base_dir, '..', 'themes'))
    theme_path = os.path.join(themes_dir, f'{theme_name.lower()}.json')

    # Se il tema non esiste
    if not os.path.exists(theme_path):
        return f"Tema '{theme_name}' non trovato.", 404

    try:
        with open(theme_path, 'r', encoding='utf-8') as f:
            theme_data = json.load(f)

        head = theme_data.get('head', '')
        foot = theme_data.get('foot', '')
        script = theme_data.get('script', '')
        pages = theme_data.get('pages', [])

        # Recupera le pagine 'home', 'navbar' e 'footer'
        page_home = next((p for p in pages if p.get('slug') == 'home'), None)
        page_navbar = next((p for p in pages if p.get('slug') == 'navbar'), None)
        page_footer = next((p for p in pages if p.get('slug') == 'footer'), None)

        if not page_home:
            return "La pagina 'home' non è presente nel tema.", 404

        html = f"""
        <!DOCTYPE html>
        <html lang="{page_home.get('language', 'en')}">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>{page_home.get('title')}</title>
          {head}
          <style>{page_home.get('styles', '')}</style>
        </head>
        <body>
          {page_navbar.get('content') if page_navbar else ''}
          <main>
            {page_home.get('content')}
          </main>
          {page_footer.get('content') if page_footer else ''}
          {foot}
          <script>{script}</script>
          <script>AOS.init();</script>
        </body>
        </html>
        """
        return Response(html, mimetype='text/html')

    except Exception as e:
        # Mostra l’errore dettagliato in dev, generico in prod
        if current_app.config.get("ENVIRONMENT") == "development":
            return f"Errore nella visualizzazione del tema: {str(e)}", 500
        return "Errore durante la visualizzazione del tema.", 500

@landing_bp.route('/dashboard/themes/explore')
def explore_themes():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    themes = CMSAddon.query.filter_by(addon_type='themes').all()

    return render_template('landing/themes_explore.html', user=get_user_from_session(), themes=themes)

@landing_bp.route('/dashboard/themes/upload')
def upload_themes():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    themes = CMSAddon.query.filter_by(addon_type='themes').all()

    return render_template('landing/themes_upload.html', user=get_user_from_session(), themes=themes)

@landing_bp.route('/subscription/cancel')
def subscription_cancel():
    shop_name = request.args.get("shop", "")
    return render_template("landing/subscription_cancel.html", shop_name=shop_name)

@landing_bp.route('/subscription/success')
def subscription_success():
    shop_name = request.args.get("shop", "")
    return render_template("landing/subscription_success.html", shop_name=shop_name)

@landing_bp.route('/dashboard/manage/<shop_name>')
def dashboard_manage_shop(shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    user_id = session['user_id']
    shop = ShopList.query.filter_by(shop_name=shop_name).first()

    if not shop:
        flash("Negozio non trovato.", "warning")
        return redirect(url_for('landing.dashboard_stores'))

    is_owner = shop.user_id == user_id
    has_access = UserStoreAccess.query.filter_by(shop_id=shop.id, user_id=user_id).first()

    if not is_owner and not has_access:
        flash("Questo store non è tuo. Per collaborare, invia una richiesta al proprietario.", "warning")
        return redirect(url_for('landing.dashboard_stores'))

    # 👇 Dati per la dashboard
    subscription = Subscription.query.filter_by(shop_name=shop_name).first()
    addons = ShopAddon.query.filter_by(shop_name=shop_name).all()
    domains = Domain.query.join(ShopList, Domain.shop_id == ShopList.id).filter(ShopList.shop_name == shop_name).all()
    suggestions = ImprovementSuggestion.query.filter_by(shop_name=shop_name).all()

    return render_template(
        'landing/dashboard_shop_manage.html',
        shop_name=shop_name,
        subscription=subscription,
        addons=addons,
        domains=domains,
        suggestions=suggestions,
        user=get_user_from_session()
    )

@landing_bp.route('/dashboard/team')
def store_list():
    """Visualizza la lista completa degli store con i loro proprietari"""
    # Verifica autenticazione
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    
    # Paginazione
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Query per ottenere tutti gli store con i proprietari
    stores_query = db.session.query(
        ShopList.id,
        ShopList.shop_name,
        ShopList.shop_type,
        ShopList.domain,
        User.id.label('owner_id'),
        User.nome,
        User.cognome,
        User.email
    ).join(User, ShopList.user_id == User.id
    ).order_by(ShopList.shop_name.asc())
    
    # Applica paginazione
    stores = stores_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        'landing/dashboard_team.html',  # Usiamo lo stesso template
        user=get_user_from_session(),
        stores=stores.items,
        page=page,
        total_pages=stores.pages
    )

@landing_bp.route("/blog")
def blog():
    return render_template("landing/blog.html")

@landing_bp.route("/docs")
def docs():
    return render_template("landing/docs.html")

@landing_bp.route("/news")
def news():
    return render_template("landing/news.html")


 # 📊 Google Analytics
@landing_bp.route('/dashboard/analytics/google_analytics/<shop_name>')
def dashboard_google_analytics(shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    
    websettings = WebSettings.query.filter_by(shop_name=shop_name).all()

    return render_template('landing/dashboard_google_analytics.html', user=get_user_from_session(), shop_name=shop_name, websettings=websettings)

# 📘 Facebook Pixel
@landing_bp.route('/dashboard/analytics/facebook_pixel/<shop_name>')
def dashboard_facebook_pixel(shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_facebook_pixel.html', user=get_user_from_session(), shop_name=shop_name)

# 🎵 TikTok Pixel
@landing_bp.route('/dashboard/analytics/tiktok_pixel/<shop_name>')
def dashboard_tiktok_pixel(shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_tiktok_pixel.html', user=get_user_from_session(), shop_name=shop_name)

# 🔌 Plugin generici (fatturazione, zapier, ecc.)
@landing_bp.route('/dashboard/integrations/<plugin>/<shop_name>')
def dashboard_plugin_integration(plugin, shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_integration_plugin.html', user=get_user_from_session(), plugin=plugin, shop_name=shop_name)

# 🧠 Analisi con AI
@landing_bp.route('/dashboard/ai/analytics/<shop_name>')
def dashboard_ai_analytics(shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_ai_analytics.html', user=get_user_from_session(), shop_name=shop_name)

# 📢 Campagne con AI
@landing_bp.route('/dashboard/ai/campaigns/<shop_name>')
def dashboard_ai_campaigns(shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_ai_campaigns.html', user=get_user_from_session(), shop_name=shop_name)

# 🌐 Gestione domini
@landing_bp.route('/dashboard/domains/<shop_name>')
def dashboard_manage_domains(shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    subscription = Subscription.query.filter_by(shop_name=shop_name).first()

    shop = ShopList.query.filter_by(shop_name=shop_name).first()
    if not shop:
        return redirect(url_for('landing.dashboard_stores'))

    domains = Domain.query.filter_by(shop_id=shop.id).all()
    domain_data = [d.__dict__ for d in domains]
    
    from config import Config
    return render_template(
        'landing/dashboard_domains.html',
        user=get_user_from_session(),
        shop_name=shop_name,
        domains=domain_data,
        stripe_pk=Config.STRIPE_PUBLISHABLE_KEY
    )

# 👥 Gestione utenti
@landing_bp.route('/dashboard/users/<shop_name>')
def dashboard_manage_users(shop_name):
    """
    Pagina di gestione degli utenti autorizzati a un negozio.

    1. Verifica che l'utente sia loggato.
    2. Recupera lo store tramite shop_name o restituisce 404.
    3. Consente l’accesso solo al proprietario o a chi ha access_level = 'admin'.
    4. Costruisce la lista di tutti gli utenti abilitati (owner + collaboratori) e
       la passa al template come `authorized_users`.
    """
    # ✅ Utente loggato
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    # 🔎 Recupero negozio
    shop = ShopList.query.filter_by(shop_name=shop_name).first_or_404()

    # 👮‍♂️ Permessi: proprietario oppure admin nello store
    current_user_id = session['user_id']
    is_owner = shop.user_id == current_user_id
    admin_entry = UserStoreAccess.query.filter_by(
        shop_id=shop.id,
        user_id=current_user_id,
        access_level='admin'
    ).first()

    if not is_owner and not admin_entry:
        flash("Non hai i permessi per gestire gli utenti di questo store.", "warning")
        return redirect(url_for('landing.dashboard_stores'))

    # 💳 Abbonamento corrente dello store
    subscription = Subscription.query.filter_by(shop_name=shop_name).first()

    # 👥 Tutti i collaboratori presenti in UserStoreAccess
    collaborator_rows = (
        db.session.query(User, UserStoreAccess.access_level)
        .join(UserStoreAccess, User.id == UserStoreAccess.user_id)
        .filter(UserStoreAccess.shop_id == shop.id)
        .all()
    )

    authorized_users = [
        {
            "id": u.id,
            "nome": u.nome,
            "cognome": u.cognome,
            "email": u.email,
            "profilo_foto": u.profilo_foto,
            "access_level": lvl,
        }
        for u, lvl in collaborator_rows
    ]

    # ➕ Aggiunge il proprietario se non già presente
    if not any(u["id"] == shop.user_id for u in authorized_users):
        owner = User.query.get(shop.user_id)
        authorized_users.insert(
            0,
            {
                "id": owner.id,
                "nome": owner.nome,
                "cognome": owner.cognome,
                "email": owner.email,
                "profilo_foto": owner.profilo_foto,
                "access_level": "admin",
            },
        )

    return render_template(
        'landing/dashboard_users.html',
        user=get_user_from_session(),
        shop_name=shop_name,
        subscription=subscription,
        authorized_users=authorized_users,
        is_owner=is_owner
    )

#
# --------------------------------------------------------------------------------------------
# Helper funzioni per inviti / richieste
# --------------------------------------------------------------------------------------------
def _extract_shop_from_referrer(ref):
    """Restituisce lo shop_name dall'URL /dashboard/users/<shop_name> presente nel referrer."""
    if not ref:
        return None
    marker = '/dashboard/users/'
    if marker in ref:
        tail = ref.split(marker, 1)[-1]
        return tail.split('?')[0].split('#')[0]
    return None


def _user_is_owner_or_admin(user_id, shop):
    """True se user_id è proprietario o admin nello shop."""
    if shop.user_id == user_id:
        return True
    return UserStoreAccess.query.filter_by(
        shop_id=shop.id, user_id=user_id, access_level='admin'
    ).first() is not None


# --------------------------------------------------------------------------------------------
# ➕ Invia invito / richiesta collaborazione
# --------------------------------------------------------------------------------------------
@landing_bp.route('/dashboard/users/add', methods=['POST'])
def add_shop_user():
    """
    Endpoint AJAX chiamato dal popup SweetAlert2.

    • Se l'email è già di un utente registrato → crea Request + messaggio interno.
    • Se non esiste → crea Request + manda e‑mail di invito a registrarsi.
    """
    if 'user_id' not in session:
        return jsonify(success=False, message="Utente non autenticato"), 401

    data = request.get_json(silent=True) or request.form.to_dict()
    email = (data.get('email') or '').strip().lower()
    access_level = (data.get('access_level') or 'viewer').strip().lower()

    shop_name = (data.get('shop_name') or
                 request.args.get('shop_name') or
                 _extract_shop_from_referrer(request.referrer))

    if not email or not shop_name:
        return jsonify(success=False, message="Parametri mancanti"), 400

    shop = ShopList.query.filter_by(shop_name=shop_name).first()
    if not shop:
        return jsonify(success=False, message="Negozio non trovato"), 404

    if not _user_is_owner_or_admin(session['user_id'], shop):
        return jsonify(success=False, message="Permessi insufficienti"), 403

    # ------------------------------------------------------------
    # Genera o recupera utente destinatario
    # ------------------------------------------------------------
    target_user = User.query.filter_by(email=email).first()

    # Crea record Request
    req_id = create_request({
        "sender_id": session['user_id'],
        "recipient_id": target_user.id if target_user else None,
        "recipient_email": email,
        "shop_id": shop.id,
        "request_type": "collaboration",
        "access_level": access_level,
        "message": data.get('personal_message'),
        "expires_in_days": 3
    })
    if not req_id:
        return jsonify(success=False, message="Errore interno"), 500

    # Recupera il token appena creato
    req = uRequests.query.get(req_id)
    invite_link = url_for('landing.accept_invite', token=req.token, _external=True)

    # ------------------------------------------------------------
    # CASO 1: Utente registrato → messaggistica interna
    # ------------------------------------------------------------
    if target_user:
        # TODO: integrare con sistema chat/notifiche
        # send_chat_message(sender_id=session['user_id'],
        #                   recipient_id=target_user.id,
        #                   text=f"Hai ricevuto un invito a collaborare sullo shop {shop.shop_name}.",
        #                   link=invite_link)
        return jsonify(success=True, message="Invito inviato tramite messaggistica interna")

    # ------------------------------------------------------------
    # CASO 2: Utente non registrato → invio e‑mail
    # ------------------------------------------------------------
    try:
        msg = Message(
            subject=f"Invito a collaborare sullo shop {shop.shop_name}",
            recipients=[email],
            html=f"""
                <p>Ciao!</p>
                <p>Sei stato invitato ad accedere allo shop <strong>{shop.shop_name}</strong>
                come <strong>{access_level}</strong>.</p>
                <p>Clicca sul link per accettare l'invito e registrarti:</p>
                <p><a href="{invite_link}">{invite_link}</a></p>
                <p>Il link scade tra 3 giorni.</p>
            """
        )
        mail.send(msg)
        return jsonify(success=True, message="Invito inviato via email")
    except Exception:
        current_app.logger.exception("Errore invio email")
        return jsonify(success=False, message="Impossibile inviare l'invito"), 500


# --------------------------------------------------------------------------------------------
# ✔️ Accetta invito
# --------------------------------------------------------------------------------------------
@landing_bp.route('/accept-invite/<token>', methods=['GET', 'POST'])
def accept_invite(token):
    """
    1. Verifica token e richiesta pendente.
    2. Se POST → registra (o logga) l'utente, concede permesso e marca accepted.
    3. Se GET  → mostra form di registrazione/accettazione.
    """
    req = uRequests.query.filter_by(token=token, status='pending').first()
    if not req or datetime.utcnow() > req.expires_at:
        flash("Invito non valido o scaduto", "danger")
        return redirect(url_for('landing.login'))

    email = req.recipient_email
    shop = ShopList.query.get(req.shop_id)

    if request.method == 'POST':
        # Se l'utente è già loggato, usa sessione; altrimenti crea account
        if 'user_id' in session:
            new_user = User.query.get(session['user_id'])
        else:
            password = request.form.get('password')
            nome = request.form.get('nome')
            cognome = request.form.get('cognome')
            if not all([password, nome, cognome]):
                flash("Compila tutti i campi.", "warning")
                return render_template('landing/accept_invite.html', email=email)

            if User.query.filter_by(email=email).first():
                flash("Email già registrata, effettua il login.", "info")
                return redirect(url_for('landing.login'))

            new_user = User(email=email, nome=nome, cognome=cognome)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

        # Concede accesso
        if not UserStoreAccess.query.filter_by(user_id=new_user.id, shop_id=shop.id).first():
            db.session.add(UserStoreAccess(
                user_id=new_user.id,
                shop_id=shop.id,
                access_level=req.access_level
            ))
            db.session.commit()

        req.status = 'accepted'
        req.recipient_id = new_user.id
        db.session.commit()

        flash("Invito accettato! Ora puoi accedere al negozio.", "success")
        return redirect(url_for('landing.login'))

    return render_template('landing/accept_invite.html', email=email, shop_name=shop.shop_name)

# --------------------------------------------------------------------------------------------
# 🗺️ SITEMAP
# --------------------------------------------------------------------------------------------
@landing_bp.route('/sitemap.xml', methods=['GET'])
def sitemap():
    from flask import current_app
    import urllib.parse
    import datetime

    allowed_paths = [
        '/',
        '/partner',
        '/price',
        '/integration',
        '/login',
        '/docs',
        '/blog',
        '/news'
    ]

    pages = []
    lastmod = datetime.datetime.now().date().isoformat()

    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            if rule.rule in allowed_paths:
                url = url_for(rule.endpoint, _external=True)
                pages.append({
                    'loc': urllib.parse.quote(url, safe=':/'),
                    'lastmod': lastmod
                })

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        sitemap_xml += '  <url>\n'
        sitemap_xml += f"    <loc>{page['loc']}</loc>\n"
        sitemap_xml += f"    <lastmod>{page['lastmod']}</lastmod>\n"
        sitemap_xml += '  </url>\n'

    sitemap_xml += '</urlset>\n'

    return Response(sitemap_xml, mimetype='application/xml')