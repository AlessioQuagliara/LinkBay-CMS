from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from models.database import db  # Importiamo il database SQLAlchemy
from models.cmsaddon import CMSAddon  # Modello per gli add-on
from models.page import Page  # Modello per la gestione delle pagine
from models.websettings import WebSettings  # Modello per le impostazioni web
from helpers import check_user_authentication
import os
import json
import logging

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione degli add-on del CMS
cmsaddon_bp = Blueprint('cmsaddon' , __name__)

def get_addons_by_type(addon_type, shop_name):
    """
    Recupera gli add-on di un certo tipo e ne aggiorna lo stato per lo shop corrente.
    """
    addons = CMSAddon.query.filter_by(type=addon_type).all()
    
    for addon in addons:
        status = addon.get_addon_status(shop_name, addon.id)
        addon.status = status if status else 'select'  # Se non ha stato, imposta 'select'

    return addons

@cmsaddon_bp.route('/store-components/theme-ui')
def theme_ui():
    """
    Pagina che mostra gli add-on relativi alla UI del tema.
    """
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]
        theme_ui_addons = get_addons_by_type('theme_ui', shop_name)
        return render_template(
            'admin/cms/store-components/theme-ui.html',
            title='Theme UI',
            username=username,
            addons=theme_ui_addons
        )
    return username

@cmsaddon_bp.route('/store-components/plugin')
def plugin():
    """
    Pagina che mostra gli add-on relativi ai plugin.
    """
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]
        plugin_addons = get_addons_by_type('plugin', shop_name)
        return render_template(
            'admin/cms/store-components/plugin.html',
            title='Plugin',
            username=username,
            addons=plugin_addons
        )
    return username

@cmsaddon_bp.route('/store-components/services')
def services():
    """
    Pagina che mostra gli add-on relativi ai servizi.
    """
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]
        service_addons = CMSAddon.query.filter_by(type='service').all()
        
        for addon in service_addons:
            status = addon.get_addon_status(shop_name, addon.id)
            
            # Stato di default per add-ons non selezionati né acquistati
            if status == 'purchased':
                addon.status = 'purchased'
            elif status == 'selected':
                addon.status = 'selected'
            else:
                addon.status = 'select'  

        return render_template(
            'admin/cms/store-components/services.html',
            title='Services',
            username=username,
            addons=service_addons
        )
    
    return username

@cmsaddon_bp.route('/store-components/themes')
def themes():
    """
    Pagina che mostra gli add-on relativi ai temi.
    """
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]
        theme_addons = get_addons_by_type('theme', shop_name)
        return render_template(
            'admin/cms/store-components/themes.html',
            title='Themes',
            username=username,
            addons=theme_addons
        )
    return username

# 📌 Route per selezionare un add-on
@cmsaddon_bp.route('/api/select-addon', methods=['POST'])
def select_addon():
    """
    API per selezionare un add-on.
    Imposta lo stato su 'selected' per l'add-on scelto e su 'deselected' per gli altri dello stesso tipo.
    """
    try:
        data = request.get_json()
        shop_name = request.host.split('.')[0]
        addon_id = data.get('addon_id')
        addon_type = data.get('addon_type')

        if not addon_id or not addon_type:
            return jsonify({'status': 'error', 'message': 'Addon ID and type are required'}), 400

        # Aggiorna lo stato dell'add-on selezionato
        selected_addon = CMSAddon.query.filter_by(id=addon_id, type=addon_type).first()
        if not selected_addon:
            return jsonify({'status': 'error', 'message': 'Addon not found'}), 404

        # Deseleziona gli altri add-on dello stesso tipo per lo stesso negozio
        CMSAddon.query.filter_by(shop_name=shop_name, type=addon_type).update({'status': 'deselected'})

        # Imposta lo stato su 'selected' per l'add-on scelto
        selected_addon.status = 'selected'
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Addon selected successfully'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error selecting addon: {e}")
        return jsonify({'status': 'error', 'message': 'Unexpected error occurred'}), 500

# 📌 Route per acquistare un add-on
@cmsaddon_bp.route('/api/purchase-addon', methods=['POST'])
def purchase_addon():
    """
    API per acquistare un add-on.
    Imposta lo stato dell'add-on su 'purchased'.
    """
    try:
        data = request.get_json()
        shop_name = request.host.split('.')[0]
        addon_id = data.get('addon_id')
        addon_type = data.get('addon_type')

        if not addon_id or not addon_type:
            return jsonify({'status': 'error', 'message': 'Addon ID and type are required'}), 400

        # Aggiorna lo stato dell'add-on a 'purchased'
        purchased_addon = CMSAddon.query.filter_by(id=addon_id, type=addon_type).first()
        if not purchased_addon:
            return jsonify({'status': 'error', 'message': 'Addon not found'}), 404

        purchased_addon.status = 'purchased'
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Addon purchased successfully'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error purchasing addon: {e}")
        return jsonify({'status': 'error', 'message': 'Unexpected error occurred'}), 500

# 📌 Route per applicare un tema
@cmsaddon_bp.route('/api/apply-theme', methods=['POST'])
def apply_theme_api():
    """
    API per applicare un tema a un negozio.
    - Legge il tema da `themes/{theme_name}.json`
    - Aggiorna o inserisce le pagine nel database
    - Aggiorna `web_settings` con `head`, `foot` e `script`
    """
    try:
        data = request.get_json()
        shop_name = request.host.split('.')[0]
        theme_name = data.get("theme_name")

        if not theme_name:
            return jsonify({'status': 'error', 'message': 'Theme name is required'}), 400

        # 📌 Applica il tema
        success = apply_theme(theme_name, shop_name)

        if success:
            return jsonify({'status': 'success', 'message': f"Theme '{theme_name}' applied successfully"})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to apply theme'}), 500

    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Error applying theme '{theme_name}': {e}")
        return jsonify({'status': 'error', 'message': 'Unexpected error occurred'}), 500


# 📌 Funzione per applicare il tema dal file JSON
def apply_theme(theme_name, shop_name):
    theme_path = os.path.join("themes", f"{theme_name}.json")

    if not os.path.exists(theme_path):
        logging.error(f"❌ Theme file '{theme_path}' not found.")
        return False

    try:
        with open(theme_path, "r") as theme_file:
            theme_data = json.load(theme_file)

        # 📌 Aggiorna `web_settings`
        web_settings = WebSettings.query.filter_by(shop_name=shop_name).first()

        if web_settings:
            web_settings.theme_name = theme_name
            web_settings.head = theme_data.get("head", "")
            web_settings.foot = theme_data.get("foot", "")
            web_settings.script = theme_data.get("script", "")
        else:
            new_web_settings = WebSettings(
                shop_name=shop_name,
                theme_name=theme_name,
                head=theme_data.get("head", ""),
                foot=theme_data.get("foot", ""),
                script=theme_data.get("script", ""),
            )
            db.session.add(new_web_settings)

        # 📌 Aggiorna o inserisce le pagine
        for page in theme_data["pages"]:
            existing_page = Page.query.filter_by(slug=page["slug"], shop_name=shop_name).first()

            if existing_page:
                existing_page.content = page.get("content", "")
                existing_page.updated_at = datetime.utcnow()
            else:
                new_page = Page(
                    title=page.get("title", ""),
                    description=page.get("description", None),
                    keywords=page.get("keywords", None),
                    slug=page.get("slug", ""),
                    content=page.get("content", None),
                    theme_name=theme_name,
                    paid="Yes",
                    language=page.get("language", None),
                    published=bool(page.get("published", True)),
                    shop_name=shop_name,
                )
                db.session.add(new_page)

        db.session.commit()
        logging.info(f"✅ Tema '{theme_name}' applicato con successo a {shop_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'applicazione del tema '{theme_name}': {e}")
        return False