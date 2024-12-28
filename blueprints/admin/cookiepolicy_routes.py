from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from models.cookiepolicy import CookiePolicy  # importo la classe database
from db_helpers import DatabaseHelper
from db_helpers import DatabaseHelper
from helpers import check_user_authentication

db_helper = DatabaseHelper()

# Blueprint
cookiepolicy_bp = Blueprint('cookiepolicy', __name__)

# Rotte per la gestione

@cookiepolicy_bp.route('/admin/cms/function/cookie-policy', methods=['GET', 'POST'])
def cookie_setting():
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_name = request.host.split('.')[0]

    with db_helper.get_db_connection() as db_conn:
        cookie_model = CookiePolicy(db_conn)

        if request.method == 'POST':
            # Verifica se la richiesta è di tipo JSON
            if request.is_json:
                # Ottieni i dati dalla richiesta JSON
                data = request.json
                title = data.get('title')
                text_content = data.get('text_content')
                button_text = data.get('button_text')
                background_color = data.get('background_color')
                button_color = data.get('button_color')
                button_text_color = data.get('button_text_color')
                text_color = data.get('text_color')
                entry_animation = data.get('animation')

                # Controlla se esiste già una configurazione per questo negozio
                existing_setting = cookie_model.get_policy_by_shop(shop_name)

                # Aggiorna o crea la configurazione interna
                if existing_setting:
                    success = cookie_model.update_internal_policy(
                        shop_name, title, text_content, button_text,
                        background_color, button_color, button_text_color,
                        text_color, entry_animation
                    )
                else:
                    success = cookie_model.create_internal_policy(
                        shop_name, title, text_content, button_text,
                        background_color, button_color, button_text_color,
                        text_color, entry_animation
                    )

                # Ritorna il risultato come JSON per il feedback AJAX
                return jsonify({'success': success})

            # Ritorna errore se la richiesta non è JSON
            return jsonify({'success': False, 'error': 'Invalid request format'})

        else:
            # Recupera le impostazioni esistenti, se presenti
            cookie_settings = cookie_model.get_policy_by_shop(shop_name)

            return render_template(
                'admin/cms/function/cookie-policy.html',
                title='Cookie Bar Settings',
                username=username,
                cookie_settings=cookie_settings
            )


@cookiepolicy_bp.route('/admin/cms/function/cookie-policy-third-party', methods=['GET', 'POST'])
def cookie_setting_third_party():
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_name = request.host.split('.')[0]

    with db_helper.get_db_connection() as db_conn:
        cookie_model = CookiePolicy(db_conn)

        if request.method == 'POST':
            data = request.get_json()  # Modifica per accettare JSON
            if not data:
                return jsonify({'status': 'error', 'message': 'Invalid JSON data.'}), 400

            # Dati dal JSON per la configurazione di terze parti
            use_third_party = data.get('use_third_party', False)
            third_party_cookie = data.get('third_party_cookie', '')
            third_party_privacy = data.get('third_party_privacy', '')
            third_party_terms = data.get('third_party_terms', '')
            third_party_consent = data.get('third_party_consent', '')

            # Aggiorna o crea la configurazione di terze parti
            existing_setting = cookie_model.get_policy_by_shop(shop_name)
            if existing_setting:
                success = cookie_model.update_third_party_policy(
                    shop_name, use_third_party, third_party_cookie, 
                    third_party_privacy, third_party_terms, third_party_consent
                )
            else:
                success = cookie_model.create_third_party_policy(
                    shop_name, use_third_party, third_party_cookie, 
                    third_party_privacy, third_party_terms, third_party_consent
                )

            # Risposte JSON per richiesta AJAX
            if success:
                return jsonify({'status': 'success', 'message': 'Third-party cookie settings updated successfully!'})
            else:
                return jsonify({'status': 'error', 'message': 'Error updating third-party cookie settings.'}), 500

        # Recupera le impostazioni esistenti, se presenti
        cookie_settings = cookie_model.get_policy_by_shop(shop_name)

        return render_template(
            'admin/cms/function/cookie-policy-third-party.html',
            title='Third-Party Cookie Settings',
            username=username,
            cookie_settings=cookie_settings
        )
    