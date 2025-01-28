from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect
from models.cmsaddon import CMSAddon  # importo la classe database
from models.page import Page  # importo la classe database
from db_helpers import DatabaseHelper
from helpers import check_user_authentication
import logging
logging.basicConfig(level=logging.INFO)

db_helper = DatabaseHelper()  # connessione al database

# Blueprint
cmsaddon_bp = Blueprint('cmsaddon', __name__)

# Rotte per la gestione

@cmsaddon_bp.route('/store-components/theme-ui')
def theme_ui():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]
        with db_helper.get_db_connection() as db_conn:
            addon_model = CMSAddon(db_conn)
            theme_ui_addons = addon_model.get_addons_by_type('theme_ui')
            for addon in theme_ui_addons:
                status = addon_model.get_addon_status(shop_name, addon['id'])
                addon['status'] = status if status else 'select'
        return render_template(
            'admin/cms/store-components/theme-ui.html',
            title='Theme UI',
            username=username,
            addons=theme_ui_addons
        )
    return username


@cmsaddon_bp.route('/store-components/plugin')
def plugin():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]
        with db_helper.get_db_connection() as db_conn:
            addon_model = CMSAddon(db_conn)
            plugin_addons = addon_model.get_addons_by_type('plugin')
            for addon in plugin_addons:
                status = addon_model.get_addon_status(shop_name, addon['id'])
                addon['status'] = status if status else 'select'
        return render_template(
            'admin/cms/store-components/plugin.html',
            title='Plugin',
            username=username,
            addons=plugin_addons
        )
    return username


@cmsaddon_bp.route('/store-components/services')
def services():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]
        with db_helper.get_db_connection() as db_conn:
            addon_model = CMSAddon(db_conn)
            service_addons = addon_model.get_addons_by_type('service')
            
            for addon in service_addons:
                status = addon_model.get_addon_status(shop_name, addon['id'])
                
                # Se lo stato è 'purchased', assicuriamoci che non possa essere modificato
                if status == 'purchased':
                    addon['status'] = 'purchased'
                elif status == 'selected':
                    addon['status'] = 'selected'
                else:
                    addon['status'] = 'select'  # Default per add-ons non selezionati né acquistati

        return render_template(
            'admin/cms/store-components/services.html',
            title='Services',
            username=username,
            addons=service_addons
        )
    
    return username


@cmsaddon_bp.route('/store-components/themes')
def themes():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]
        with db_helper.get_db_connection() as db_conn:
            addon_model = CMSAddon(db_conn)
            theme_addons = addon_model.get_addons_by_type('theme')
            for addon in theme_addons:
                status = addon_model.get_addon_status(shop_name, addon['id'])
                addon['status'] = status if status else 'select'
        return render_template(
            'admin/cms/store-components/themes.html',
            title='Themes',
            username=username,
            addons=theme_addons
        )
    return username


# Route per selezionare un addon
@cmsaddon_bp.route('/api/select-addon', methods=['POST'])
def select_addon():
    data = request.get_json()
    shop_name = request.host.split('.')[0]
    addon_id = data.get('addon_id')
    addon_type = data.get('addon_type')
    with db_helper.get_db_connection() as db_conn:
        addon_model = CMSAddon(db_conn)
        
        # Assicurati di impostare "selected" per l'addon attuale e "deselected" per tutti gli altri dello stesso tipo
        success = addon_model.update_shop_addon_status(shop_name, addon_id, addon_type, 'selected')
        if success:
            # Deseleziona altri addon dello stesso tipo per lo stesso negozio
            addon_model.deselect_other_addons(shop_name, addon_id, addon_type)

    if success:
        return jsonify({'status': 'success', 'message': 'Addon selected successfully'})
    return jsonify({'status': 'error', 'message': 'Failed to select addon'}), 500


# Route per acquistare un addon
@cmsaddon_bp.route('/api/purchase-addon', methods=['POST'])
def purchase_addon():
    data = request.get_json()
    shop_name = request.host.split('.')[0]
    addon_id = data.get('addon_id')
    addon_type = data.get('addon_type')
    with db_helper.get_db_connection() as db_conn:
        addon_model = CMSAddon(db_conn)
        success = addon_model.update_shop_addon_status(shop_name, addon_id, addon_type, 'purchased')
    if success:
        return jsonify({'status': 'success', 'message': 'Addon purchased successfully'})
    return jsonify({'status': 'error', 'message': 'Failed to purchase addon'}), 500


@cmsaddon_bp.route('/api/apply-theme', methods=['POST'])
def apply_theme():
    data = request.get_json()
    shop_name = request.host.split('.')[0]
    theme_name = data.get('theme_name')

    if not theme_name:
        return jsonify({'status': 'error', 'message': 'Theme name is required'}), 400

    try:
        page_model = Page(db_helper.get_db_connection())
        success = page_model.apply_theme(theme_name, shop_name)
        if success:
            return jsonify({'status': 'success', 'message': f"Theme '{theme_name}' applied successfully"})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to apply theme'}), 500
    except Exception as e:
        logging.error(f"Error applying theme: {e}")
        return jsonify({'status': 'error', 'message': 'Unexpected error occurred'}), 500