from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash, Response, current_app
from models.database import db  # Importiamo il database SQLAlchemy
from models.stores_info import StoreInfo  # Modello per le informazioni del negozio
from models.shoplist import ShopList  # Modello per la gestione dei negozi
from models.cmsaddon import CMSAddon  # Modello per gli add-on (temi)
from helpers import check_user_authentication
import logging
import os
import json

logging.basicConfig(level=logging.INFO)

# 📌 Blueprint per la gestione dell'interfaccia UI
ui_bp = Blueprint('ui', __name__)

# 🔹 **Pagina principale dell'interfaccia del CMS**
@ui_bp.route('/admin/cms/interface/')
@ui_bp.route('/admin/cms/interface/render')
def render_interface():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/interface/render.html', title='CMS Interface', username=username)
    return username  

# 🔹 **Pagina Homepage del CMS**
@ui_bp.route('/admin/cms/pages/homepage')
def homepage():
    username = check_user_authentication()
    logging.info(f"📌 Session before homepage: {session}")

    if not isinstance(username, str):
        logging.error("❌ User not authenticated. Redirecting to login.")
        return redirect(url_for('user.login'))

    # Ottieni il sottodominio del negozio
    shop_name = request.host.split('.')[0]
    logging.info(f"📌 Accessing shop: {shop_name}")

    try:
        # Verifica se il negozio esiste in ShopList
        shop = ShopList.query.filter_by(shop_name=shop_name).first()
        if not shop:
            logging.critical(f"❌ Shop '{shop_name}' not found in ShopList.")
            return render_template('admin/errors/shop_not_found.html', title="Error")

        # Recupera le informazioni sul negozio
        store_info = StoreInfo.query.filter_by(shop_name=shop_name).first()
        if not store_info:
            logging.warning(f"⚠️ Store info for '{shop_name}' missing. Redirecting to setup.")
            return redirect(url_for('ui.setup_store'))

        # Aggiorna la sessione con i dati del negozio
        session.update({
            'shop_id': shop.id,
            'shop_name': shop.shop_name,
            'domain': shop.domain,
            'shop_type': shop.shop_type,
            'store_owner': store_info.owner_name,
            'store_email': store_info.email,
            'store_industry': store_info.industry
        })
        logging.info(f"✅ Session updated: {session}")

        # Renderizza la homepage con i dati aggiornati
        return render_template(
            'admin/cms/pages/home.html',
            title='HomePage',
            username=session.get('username'),
            shop_name=session.get('shop_name'),
            store_owner=session.get('store_owner')
        )

    except Exception as e:
        logging.error(f"❌ Error loading homepage: {str(e)}")
        return render_template('errors/500.html', title="Error 500"), 500

# 🔹 **Pagina di configurazione iniziale del negozio**
@ui_bp.route('/admin/cms/pages/setup', methods=['GET', 'POST'])
def setup_store():
    shop_name = request.host.split('.')[0]  # Ottieni il nome del negozio

    if request.method == 'POST':
        try:
            # Ricezione dei dati inviati dal modulo
            new_store = StoreInfo(
                shop_name=shop_name,
                owner_name=request.form.get('owner_name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                industry=request.form.get('industry'),
                description=request.form.get('description'),
                website_url=request.form.get('website_url'),
                revenue=request.form.get('revenue')
            )

            db.session.add(new_store)
            db.session.commit()
            logging.info(f"✅ Store '{shop_name}' created successfully!")

            return redirect(url_for('ui.ai_analysis'))

        except Exception as e:
            db.session.rollback()
            logging.error(f"❌ Error setting up store: {str(e)}")
            flash("An error occurred while setting up the store. Please try again.", "danger")

    return render_template('admin/cms/pages/store_setup.html', title='Store Setup', shop_name=shop_name)

# 🔹 **Pagina di analisi AI per il negozio**
@ui_bp.route('/admin/cms/pages/ai_analysis')
def ai_analysis():
    shop_name = request.host.split('.')[0]

    # Recupera le informazioni del negozio
    store_info = StoreInfo.query.filter_by(shop_name=shop_name).first()

    if not store_info:
        flash("⚠️ Store information is missing. Please complete the setup first.", "danger")
        return redirect(url_for('ui.setup_store'))

    return render_template('admin/cms/pages/ai_analysis.html', store_info=store_info)

# 🔹 **Selezione del tema del negozio**
@ui_bp.route('/admin/cms/pages/theme-selection')
def theme_selection():
    shop_name = request.host.split('.')[0]
    themes_folder = os.path.join(os.getcwd(), 'Themes')
    theme_files = [f for f in os.listdir(themes_folder) if f.endswith('.json')]

    theme_data = []

    for filename in theme_files:
        try:
            with open(os.path.join(themes_folder, filename), 'r', encoding='utf-8') as f:
                theme_json = json.load(f)
                if isinstance(theme_json.get("pages"), list):
                    # Ricava l'anteprima della navbar e del footer se esistono
                    navbar = next((p for p in theme_json["pages"] if p["slug"] == "navbar"), None)
                    footer = next((p for p in theme_json["pages"] if p["slug"] == "footer"), None)
                    theme_data.append({
                        "name": theme_json["pages"][0].get("theme_name", filename.replace('.json', '')),
                        "paid": theme_json["pages"][0].get("paid", "No"),
                        "language": theme_json["pages"][0].get("language", "en"),
                        "navbar": navbar,
                        "footer": footer
                    })
        except Exception as e:
            print(f"Errore nel caricamento del tema {filename}: {e}")
            continue

    return render_template(
        'admin/cms/pages/theme_selection.html',
        title='Select Your Theme',
        themes=theme_data,
        shop_name=shop_name
    )

@ui_bp.route('/preview-theme/<theme_name>')
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