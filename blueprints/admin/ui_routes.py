from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from models.database import db  # Importiamo il database SQLAlchemy
from models.stores_info import StoreInfo  # Modello per le informazioni del negozio
from models.shoplist import ShopList  # Modello per la gestione dei negozi
from models.cmsaddon import CMSAddon  # Modello per gli add-on (temi)
from helpers import check_user_authentication
import logging

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
    shop_name = request.host.split('.')[0]  # Ottieni il sottodominio del negozio

    # Recuperiamo SOLO gli add-on di tipo "theme"
    theme_addons = CMSAddon.query.filter_by(addon_type='theme').all()

    return render_template(
        'admin/cms/pages/theme_selection.html',
        title='Select Your Theme',
        themes=theme_addons,
        shop_name=shop_name
    )