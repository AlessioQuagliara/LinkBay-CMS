from flask import render_template, request, jsonify, redirect, url_for, session, Response
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
from sqlalchemy import func
from werkzeug.security import check_password_hash
import json
import logging
from flask import g
import os
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

    return render_template(
        'landing/dashboard_shop.html',
        user=get_user_from_session(),
        shops=list(all_shops.values())
    )

@landing_bp.route('/dashboard/sales')
def dashboard_sales():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    return render_template('landing/dashboard_sell.html', user=get_user_from_session())

@landing_bp.route('/dashboard/apps')
def dashboard_apps():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_app.html', user=get_user_from_session())

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

@landing_bp.route('/dashboard/team')
def dashboard_team():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_team.html', user=get_user_from_session())

@landing_bp.route('/dashboard/settings')
def dashboard_settings():
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))
    return render_template('landing/dashboard_settings.html', user=get_user_from_session())


def get_user_from_session():
    return {
        "id": session.get('user_id'),
        "email": session.get('user_email'),
        "nome": session.get('user_name'),
        "profilo_foto": session.get('user_profilo_foto', '')
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
    theme_path = os.path.join('Themes', f'{theme_name}.json')

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
        return f"Errore nella visualizzazione del tema: {str(e)}", 500

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