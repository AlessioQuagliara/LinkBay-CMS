from flask import Blueprint, request, jsonify, render_template, url_for
from models.domain import Domain  # importo la classe database
from models.shoplist import ShopList  # importo la classe database
from config import Config
from datetime import datetime
from public.godaddy_api import GoDaddyAPI
from db_helpers import DatabaseHelper
db_helper = DatabaseHelper()
from db_helpers import DatabaseHelper
from helpers import check_user_authentication
import logging, re
logging.basicConfig(level=logging.INFO)

# Blueprint
domain_bp = Blueprint('domain', __name__)

# Rotte per la gestione

@domain_bp.route('/admin/cms/pages/domain')
def domain():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/domain.html', title='Domain', username=username)
    return username

@domain_bp.route('/api/domains/search', methods=['POST'])
def search_domain():
    try:
        data = request.json
        domain_name = data.get('domain_name')

        if not domain_name:
            return jsonify({'success': False, 'message': 'Domain name is required.'}), 400

        godaddy = GoDaddyAPI()
        result = godaddy.search_domain(domain_name)

        # Debug: stampa il risultato
        logging.info(f"Search result: {result}")

        if result.get('available'):
            return jsonify({
                'success': True,
                'domains': [
                    {
                        'name': result['domain'],
                        'price': f"${result['price'] / 1000000:.2f}"
                    }
                ]
            })
        else:
            return jsonify({'success': True, 'domains': []})  # Nessun dominio disponibile
    except Exception as e:
        logging.info(f"Error in search_domain: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while searching for the domain.'}), 500
    
@domain_bp.route('/api/domains/purchase', methods=['POST'])
def purchase_domain():
    try:
        import re
        data = request.form.to_dict()

        # Nome del dominio
        domain_name = data.get('domain_name')
        if not domain_name:
            return jsonify({'success': False, 'message': 'Domain name is required.'}), 400

        # Ottieni il nome del negozio
        shop_name = request.host.split('.')[0]

        # Validazione del telefono
        phone = data.get('admin_phone', "+1.1234567890")
        phone_pattern = re.compile(r"^\+([0-9]){1,3}\.([0-9]\ ?){5,14}$")
        if not phone_pattern.match(phone):
            return jsonify({'success': False, 'message': 'Invalid phone number format.'}), 400

        # Paese e stati validi
        valid_countries = {
            "US": ["NY", "CA", "TX", "FL", "IL"],  # Stati validi per gli USA (esempio)
            "IT": ["RM", "MI", "NA", "TO", "FI"],  # Province italiane
            "GB": ["ENG", "SCT", "WLS", "NIR"],    # Regioni nel Regno Unito
            # Aggiungi altri paesi e stati/province se necessario
        }

        country = data.get('admin_country', "US")
        if country not in valid_countries:
            return jsonify({'success': False, 'message': f'Invalid country code. Supported codes: {", ".join(valid_countries.keys())}'}), 400

        state = data.get('admin_state', None)
        if not state or state not in valid_countries[country]:
            return jsonify({'success': False, 'message': f'Invalid state for country {country}. Supported states: {", ".join(valid_countries[country])}'}), 400

        # Contatto amministrativo
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

        # Dati del cliente
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

        # GoDaddy API: Acquisto del dominio
        godaddy = GoDaddyAPI()
        result = godaddy.purchase_domain(domain_name, customer_data)

        if result.get('orderId'):
            with db_helper.get_auth_db_connection() as auth_conn:
                shop_list = ShopList(auth_conn)
                if shop_list.update_shop_domain(shop_name, domain_name):
                    return jsonify({
                        'success': True,
                        'message': f'Domain {domain_name} purchased and updated successfully.',
                        'orderId': result['orderId'],
                        'total': result['total'],
                        'currency': result['currency']
                    })
                else:
                    return jsonify({
                        'success': True,
                        'message': f'Domain {domain_name} purchased, but failed to update the database.',
                        'orderId': result['orderId'],
                        'total': result['total'],
                        'currency': result['currency']
                    }), 500
        else:
            return jsonify({'success': False, 'message': 'Failed to confirm domain purchase.'}), 500

    except Exception as e:
        import traceback
        logging.info(f"Error purchasing domain: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': 'Internal server error.'}), 500
    
