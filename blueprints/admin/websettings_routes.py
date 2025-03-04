from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from models.database import db
from models.websettings import WebSettings  # Importiamo la classe del database
from helpers import check_user_authentication
import logging

# 📌 Configurazione del logger
logging.basicConfig(level=logging.INFO)

# 📌 Blueprint per la gestione delle impostazioni web
websettings_bp = Blueprint('websettings', __name__)

# 🔹 **Rotta per la modifica delle impostazioni web**
@websettings_bp.route('/admin/web_settings/edit')
def edit_web_settings():
    username = check_user_authentication()

    if isinstance(username, str):
        try:
            shop_subdomain = request.host.split('.')[0]
            web_settings = WebSettings.query.filter_by(shop_name=shop_subdomain).first()

            if web_settings:
                return render_template(
                    'admin/cms/store_editor/script_editor.html',
                    title='Edit Web Settings',
                    username=username,
                    web_settings=web_settings
                )
            else:
                flash('Web settings not found for this shop.', 'danger')
                return redirect(url_for('ui.homepage'))

        except Exception as e:
            logging.error(f"❌ Error loading web settings: {str(e)}")
            flash('An error occurred while retrieving web settings.', 'danger')
            return redirect(url_for('ui.homepage'))

    return redirect(url_for('user.login'))

# 🔹 **Rotta per aggiornare le impostazioni web**
@websettings_bp.route('/admin/web_settings/update', methods=['POST'])
def update_web_settings():
    try:
        data = request.get_json()
        head_content = data.get('head')
        script_content = data.get('script')
        foot_content = data.get('foot')

        if not head_content or not script_content or not foot_content:
            return jsonify({'success': False, 'error': 'Missing content'}), 400

        shop_subdomain = request.host.split('.')[0]
        web_settings = WebSettings.query.filter_by(shop_name=shop_subdomain).first()

        if web_settings:
            web_settings.head_content = head_content
            web_settings.script_content = script_content
            web_settings.foot_content = foot_content
        else:
            web_settings = WebSettings(
                shop_name=shop_subdomain,
                head_content=head_content,
                script_content=script_content,
                foot_content=foot_content
            )
            db.session.add(web_settings)

        db.session.commit()

        logging.info(f"✅ Web settings updated for {shop_subdomain}")
        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Error updating web settings: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400