from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models.database import db
from models.domain import Domain  # Importa il modello SQLAlchemy per i domini
from models.shoplist import ShopList  # Importa il modello SQLAlchemy per i negozi
from config import Config
from datetime import datetime
from public.godaddy_api import GoDaddyAPI
from helpers import check_user_authentication
import logging
import re

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione dei domini
domain_bp = Blueprint('domain', __name__)

# 📌 Route per visualizzare la pagina di gestione domini
@domain_bp.route('/admin/cms/pages/domain')
def domain():
    """
    Mostra la pagina di gestione dei domini per il negozio attuale.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, reindirizza alla login
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_name = request.host.split('.')[0]  # ✅ Recupera il nome del negozio solo se autenticato

    # Recupera i dati del negozio dal database
    shop = ShopList.query.filter_by(shop_name=shop_name).first()

    return render_template(
        'admin/cms/pages/domain.html',
        title='Domain',
        username=username,
        shop=shop
    )

# 📌 Route per cercare un dominio disponibile tramite GoDaddy API
@domain_bp.route('/api/domains/search', methods=['POST'])
def search_domain():
    """
    Cerca un dominio disponibile tramite GoDaddy API.
    """
    try:
        data = request.json
        domain_name = data.get('domain_name')

        if not domain_name:
            return jsonify({'success': False, 'message': 'Domain name is required.'}), 400

        godaddy = GoDaddyAPI()
        result = godaddy.search_domain(domain_name)

        logging.info(f"Search result: {result}")  # Log del risultato

        if result.get('available'):
            return jsonify({
                'success': True,
                'domains': [{'name': result['domain'], 'price': result['price']}]
            })
        else:
            return jsonify({'success': True, 'domains': []})  # Nessun dominio disponibile

    except Exception as e:
        logging.error(f"Error in search_domain: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while searching for the domain.'}), 500

# 📌 Route per acquistare un dominio tramite GoDaddy API
@domain_bp.route('/api/domains/purchase', methods=['POST'])
def purchase_domain():
    """
    Acquista un dominio tramite GoDaddy API e aggiorna il database.
    """
    try:
        data = request.form.to_dict()
        domain_name = data.get('domain_name')

        if not domain_name:
            return jsonify({'success': False, 'message': 'Domain name is required.'}), 400

        shop_name = request.host.split('.')[0]

        # Validazione del numero di telefono
        phone = data.get('admin_phone', "+1.1234567890")
        phone_pattern = re.compile(r"^\+([0-9]){1,3}\.([0-9]\ ?){5,14}$")
        if not phone_pattern.match(phone):
            return jsonify({'success': False, 'message': 'Invalid phone number format.'}), 400

        # Paesi e stati validi
        valid_countries = {
            "US": ["NY", "CA", "TX", "FL", "IL"],
            "IT": ["RM", "MI", "NA", "TO", "FI"],
            "GB": ["ENG", "SCT", "WLS", "NIR"],
        }

        country = data.get('admin_country', "US")
        if country not in valid_countries:
            return jsonify({'success': False, 'message': f'Invalid country code. Supported codes: {", ".join(valid_countries.keys())}'}), 400

        state = data.get('admin_state')
        if not state or state not in valid_countries[country]:
            return jsonify({'success': False, 'message': f'Invalid state for country {country}. Supported states: {", ".join(valid_countries[country])}'}), 400

        # Dati per il contatto amministrativo
        contact_admin = {
            "nameFirst": data.get('admin_first_name', "DefaultFirstName"),
            "nameLast": data.get('admin_last_name', "DefaultLastName"),
            "email": data.get('admin_email', "default@example.com"),
            "phone": phone,
            "addressMailing": {
                "address1": data.get('admin_address', "123 Example St"),
                "city": data.get('admin_city', "Cityville"),
                "state": state,
                "postalCode": data.get('admin_postal_code', "12345"),
                "country": country
            }
        }

        # Dati del cliente per GoDaddy API
        customer_data = {
            "consent": {
                "agreedAt": datetime.utcnow().isoformat() + "Z",
                "agreedBy": request.remote_addr,
                "agreementKeys": ["DNRA"]
            },
            "contactAdmin": contact_admin,
            "contactRegistrant": contact_admin,
            "contactTech": contact_admin,
            "contactBilling": contact_admin
        }

        # Acquisto del dominio tramite GoDaddy API
        godaddy = GoDaddyAPI()
        result = godaddy.purchase_domain(domain_name, customer_data)

        if result.get('orderId'):
            try:
                # Aggiorna il dominio nel database
                shop = ShopList.query.filter_by(shop_name=shop_name).first()

                if shop:
                    shop.domain = domain_name
                    db.session.commit()

                    return jsonify({
                        'success': True,
                        'message': f'Domain {domain_name} purchased and updated successfully.',
                        'orderId': result['orderId'],
                        'total': result['total'],
                        'currency': result['currency']
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Shop not found, domain purchase was successful but not linked.'
                    }), 500

            except Exception as e:
                db.session.rollback()
                logging.error(f"Database update error: {e}")
                return jsonify({'success': False, 'message': 'Failed to update database after domain purchase.'}), 500
        else:
            return jsonify({'success': False, 'message': 'Failed to confirm domain purchase.'}), 500

    except Exception as e:
        import traceback
        logging.error(f"Error purchasing domain: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': 'Internal server error.'}), 500