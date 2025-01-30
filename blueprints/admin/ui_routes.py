from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from db_helpers import DatabaseHelper
from models.stores_info import StoreInfo  # Importiamo il modello
from models.shoplist import ShopList
from models.cmsaddon import CMSAddon
from helpers import check_user_authentication
import logging

logging.basicConfig(level=logging.INFO)

# Blueprint
ui_bp = Blueprint('ui', __name__)
db_helper = DatabaseHelper()

# Rotte per la gestione
@ui_bp.route('/admin/cms/interface/')
@ui_bp.route('/admin/cms/interface/render')
def render_interface():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/interface/render.html', title='CMS Interface', username=username)
    return username  

@ui_bp.route('/admin/cms/pages/homepage')
def homepage():
    username = check_user_authentication()  # Verifica autenticazione utente
    logging.info(f"Session before homepage: {session}")

    if not isinstance(username, str):
        logging.error("User not authenticated. Redirecting to login.")
        return redirect(url_for('user.login'))

    # Ottieni il sottodominio o dominio come shop_name
    shop_name = request.host.split('.')[0]
    logging.info(f"Accessing shop: {shop_name}")

    # Usa la connessione corretta per ShopList
    with db_helper.get_auth_db_connection() as auth_db_conn:
        shop_list_model = ShopList(auth_db_conn)
        shop = shop_list_model.get_shop_by_name_or_domain(shop_name)

        if not shop:
            logging.critical(f"Shop '{shop_name}' not found in ShopList. This should not happen.")
            return render_template('admin/errors/shop_not_found.html', title="Error")

    # Usa la connessione standard per StoresInfo
    with db_helper.get_db_connection() as db_conn:
        store_info_model = StoreInfo(db_conn)
        store_info = store_info_model.get_store_by_shop_name(shop_name)

        if not store_info:
            logging.warning(f"Store info for '{shop_name}' missing in StoresInfo. Redirecting to setup.")
            return redirect(url_for('ui.setup_store'))

        # Aggiorna la sessione con i dati del negozio
        session['shop_id'] = shop['id']
        session['shop_name'] = shop['shop_name']
        session['domain'] = shop['domain']
        session['theme_options'] = shop['themeOptions']
        session['store_owner'] = store_info['owner_name']
        session['store_email'] = store_info['email']
        session['store_industry'] = store_info['industry']
        logging.info(f"Session updated: {session}")

    # Renderizza la homepage con i dati aggiornati
    return render_template(
        'admin/cms/pages/home.html',
        title='HomePage',
        username=session.get('username'),
        shop_name=session.get('shop_name'),
        store_owner=session.get('store_owner')
    )

# Rotta per la configurazione iniziale dello store
@ui_bp.route('/admin/cms/pages/setup', methods=['GET', 'POST'])
def setup_store():
    """
    Mostra la schermata di configurazione iniziale dello store.
    """
    shop_name = request.host.split('.')[0]  # Ottieni il sottodominio come shop_name

    if request.method == 'POST':
        # Ricezione dei dati inviati dal modulo
        owner_name = request.form.get('owner_name')
        email = request.form.get('email')
        phone = request.form.get('phone', None)
        industry = request.form.get('industry', None)
        description = request.form.get('description', None)
        website_url = request.form.get('website_url', None)
        revenue = request.form.get('revenue', None)

        with db_helper.get_db_connection() as db_conn:
            store_model = StoreInfo(db_conn)  # Creiamo l'istanza all'interno della richiesta
            success = store_model.create_store(
                shop_name=shop_name, 
                owner_name=owner_name, 
                email=email, 
                phone=phone, 
                industry=industry, 
                description=description, 
                website_url=website_url, 
                revenue=revenue
            )

        if success:
            return redirect(url_for('ui.ai_analysis'))  # Se il salvataggio è riuscito, reindirizza alla homepage

    return render_template('admin/cms/pages/store_setup.html', title='Store Setup', shop_name=shop_name)

@ui_bp.route('/admin/cms/pages/ai_analysis')
def ai_analysis():
    shop_name = request.host.split('.')[0]

    with db_helper.get_db_connection() as db_conn:
        store_info_model = StoreInfo(db_conn)
        store_info = store_info_model.get_store_by_shop_name(shop_name)

        if not store_info:
            flash("Store information is missing. Please complete the setup first.", "danger")
            return redirect(url_for('ui.setup_store'))

    return render_template('admin/cms/pages/ai_analysis.html', store_info=store_info)

@ui_bp.route('/admin/cms/pages/theme-selection')
def theme_selection():
    shop_name = request.host.split('.')[0]  # Ottieni il sottodominio del negozio

    with db_helper.get_db_connection() as db_conn:
        addon_model = CMSAddon(db_conn)
        theme_addons = addon_model.get_addons_by_type('theme')  # Recuperiamo SOLO quelli di tipo 'theme'

    return render_template(
        'admin/cms/pages/theme_selection.html',
        title='Select Your Theme',
        themes=theme_addons,  # Passiamo solo i temi
        shop_name=shop_name
    )
