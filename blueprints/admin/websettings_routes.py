from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from models.websettings import WebSettings  # importo la classe database
from db_helpers import DatabaseHelper
db_helper = DatabaseHelper()
from db_helpers import DatabaseHelper
from helpers import check_user_authentication
import logging
logging.basicConfig(level=logging.INFO)

# Blueprint
websettings_bp = Blueprint('websettings', __name__)

# Rotte per la gestione
@websettings_bp.route('/admin/web_settings/edit')
def edit_web_settings():
    username = check_user_authentication()

    if isinstance(username, str):
        db_conn = db_helper.get_db_connection()
        shop_subdomain = request.host.split('.')[0]  
        web_settings_model = WebSettings(db_conn)
        web_settings = web_settings_model.get_web_settings(shop_subdomain)  

        if web_settings:
            return render_template(
                'admin/cms/store_editor/script_editor.html',
                title='Edit Web Settings',
                username=username,
                web_settings=web_settings 
            )
        else:
            flash('Web settings not found for this shop.', 'danger')
            return redirect(url_for('homepage'))
        
    return redirect(url_for('login'))  

# Funzione per aggiornare le impostazioni web
@websettings_bp.route('/admin/web_settings/update', methods=['POST'])
def update_web_settings():
    try:
        data = request.get_json()
        head_content = data.get('head')
        script_content = data.get('script')
        foot_content = data.get('foot')

        if not head_content or not script_content or not foot_content:
            return jsonify({'success': False, 'error': 'Missing content'}), 400

        db_conn = db_helper.get_db_connection()
        shop_subdomain = request.host.split('.')[0]  
        web_settings_model = WebSettings(db_conn)
        success = web_settings_model.update_web_settings(shop_subdomain, head_content, script_content, foot_content)

        return jsonify({'success': success})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400