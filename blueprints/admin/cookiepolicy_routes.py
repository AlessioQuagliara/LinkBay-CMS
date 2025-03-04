from flask import Blueprint, render_template, request, jsonify
from models.database import db
from models.cookiepolicy import CookiePolicy
from helpers import check_user_authentication
import logging

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione delle cookie policy
cookiepolicy_bp = Blueprint('cookiepolicy' , __name__)

# 📌 Route per gestire la cookie policy interna
@cookiepolicy_bp.route('/admin/cms/function/cookie-policy', methods=['GET', 'POST'])
def cookie_setting():
    """
    Gestisce la configurazione della barra cookie del negozio.
    """
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_name = request.host.split('.')[0]

    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400

            # Recupera o crea la configurazione della cookie policy per il negozio
            cookie_settings = CookiePolicy.query.filter_by(shop_name=shop_name).first()

            if not cookie_settings:
                cookie_settings = CookiePolicy(shop_name=shop_name)

            # Aggiorna i valori della policy
            cookie_settings.title = data.get('title', 'Cookie Policy')
            cookie_settings.text_content = data.get('text_content', 'This site uses cookies.')
            cookie_settings.button_text = data.get('button_text', 'Accept')
            cookie_settings.background_color = data.get('background_color', '#ffffff')
            cookie_settings.button_color = data.get('button_color', '#28a745')
            cookie_settings.button_text_color = data.get('button_text_color', '#ffffff')
            cookie_settings.text_color = data.get('text_color', '#000000')
            cookie_settings.animation = data.get('animation', 'fade')

            # Salva nel database
            db.session.add(cookie_settings)
            db.session.commit()

            return jsonify({'success': True, 'message': 'Cookie settings updated successfully'})

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating cookie policy: {e}")
            return jsonify({'success': False, 'message': 'An error occurred'}), 500

    # Recupera le impostazioni attuali
    cookie_settings = CookiePolicy.query.filter_by(shop_name=shop_name).first()

    return render_template(
        'admin/cms/function/cookie-policy.html',
        title='Cookie Bar Settings',
        username=username,
        cookie_settings=cookie_settings
    )

# 📌 Route per gestire la cookie policy di terze parti
@cookiepolicy_bp.route('/admin/cms/function/cookie-policy-third-party', methods=['GET', 'POST'])
def cookie_setting_third_party():
    """
    Gestisce le impostazioni della cookie policy di terze parti per il negozio.
    """
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_name = request.host.split('.')[0]

    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'Invalid JSON data.'}), 400

            # Recupera o crea la configurazione della cookie policy per il negozio
            cookie_settings = CookiePolicy.query.filter_by(shop_name=shop_name).first()

            if not cookie_settings:
                cookie_settings = CookiePolicy(shop_name=shop_name)

            # Aggiorna i valori per i cookie di terze parti
            cookie_settings.use_third_party = data.get('use_third_party', False)
            cookie_settings.third_party_cookie = data.get('third_party_cookie', '')
            cookie_settings.third_party_privacy = data.get('third_party_privacy', '')
            cookie_settings.third_party_terms = data.get('third_party_terms', '')
            cookie_settings.third_party_consent = data.get('third_party_consent', '')

            # Salva nel database
            db.session.add(cookie_settings)
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Third-party cookie settings updated successfully!'})

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating third-party cookie policy: {e}")
            return jsonify({'status': 'error', 'message': 'An error occurred'}), 500

    # Recupera le impostazioni attuali
    cookie_settings = CookiePolicy.query.filter_by(shop_name=shop_name).first()

    return render_template(
        'admin/cms/function/cookie-policy-third-party.html',
        title='Third-Party Cookie Settings',
        username=username,
        cookie_settings=cookie_settings
    )