from flask import render_template, request, jsonify, redirect, url_for, session, Response, flash
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

    return render_template(
        'landing/dashboard_shop.html',
        user=get_user_from_session(),
        shops=list(all_shops.values())
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

    # Recupera i negozi di proprietà dell'utente
    shops = ShopList.query.filter_by(user_id=user_id).all()

    # Statistiche globali
    total_revenue = 0
    total_orders = 0

    for shop in shops:
        orders = Order.query.filter_by(shop_name=shop.shop_name).all()
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
    import os
    from flask import current_app
    from flask import Response
    import json

    # Path assoluto della cartella Themes
    base_dir = os.path.dirname(os.path.abspath(__file__))
    themes_dir = os.path.join(base_dir, '..', 'themes')
    theme_path = os.path.join(themes_dir, f'{theme_name}.json')

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
def dashboard_admin_leaderboard():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    page = request.args.get('page', 1, type=int)
    per_page = 10

    admin_entries = UserStoreAccess.query.filter_by(access_level='admin').all()
    user_ids = list(set([entry.user_id for entry in admin_entries]))

    leaderboard_data = []

    for uid in user_ids:
        user = User.query.get(uid)
        user_shops = ShopList.query.filter_by(user_id=uid).all()

        total_revenue = 0
        total_orders = 0
        best_store = None
        max_revenue = 0

        shop_names = [shop.shop_name for shop in user_shops]

        if shop_names:
            order_stats = db.session.query(
                func.sum(Order.total_amount),
                func.count(Order.id),
                Order.shop_name
            ).filter(Order.shop_name.in_(shop_names)).group_by(Order.shop_name).all()

            for revenue, order_count, name in order_stats:
                revenue = revenue or 0
                total_revenue += revenue
                total_orders += order_count or 0
                if revenue > max_revenue:
                    max_revenue = revenue
                    best_store = name

        leaderboard_data.append({
            "user_id": uid,
            "nome": user.nome,
            "cognome": user.cognome,
            "profilo_foto": user.profilo_foto or "/static/images/superadmin/admin_avatar.png",
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "best_store": best_store or "Nessun negozio"
        })

    leaderboard_data.sort(key=lambda x: x["total_revenue"], reverse=True)

    # 🔢 Applica la paginazione
    total_entries = len(leaderboard_data)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = leaderboard_data[start:end]

    return render_template(
        'landing/dashboard_team.html',
        user=get_user_from_session(),
        leaderboard=paginated_data,
        page=page,
        total_pages=(total_entries + per_page - 1) // per_page
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
    return render_template('landing/dashboard_google_analytics.html', user=get_user_from_session(), shop_name=shop_name)

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
    return render_template('landing/dashboard_domains.html', user=get_user_from_session(), shop_name=shop_name)

# 👥 Gestione utenti
@landing_bp.route('/dashboard/users/<shop_name>')
def dashboard_manage_users(shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_users.html', user=get_user_from_session(), shop_name=shop_name)

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


