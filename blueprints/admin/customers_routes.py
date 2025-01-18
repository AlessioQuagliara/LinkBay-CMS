from flask import Blueprint, request, jsonify, session, url_for, redirect, render_template
from models.customers import Customers  # importo la classe database
from db_helpers import DatabaseHelper
db_helper = DatabaseHelper()
import uuid
from db_helpers import DatabaseHelper
from helpers import check_user_authentication
import logging
logging.basicConfig(level=logging.INFO)

# Blueprint
customers_bp = Blueprint('customers', __name__)

# Rotte per la gestione

@customers_bp.route('/admin/cms/pages/customers')
def customers():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_subdomain = request.host.split('.')[0]  # Identifica il negozio dal sottodominio

        with db_helper.get_db_connection() as db_conn:
            customers_model = Customers(db_conn)
            customers_list = customers_model.get_all_customers(shop_subdomain)  # Ottieni tutti i clienti per il negozio

        return render_template(
            'admin/cms/pages/customers.html', 
            title='Customers', 
            username=username, 
            customers=customers_list  # Passa i clienti al template
        )
    return username

@customers_bp.route('/admin/cms/create_customer', methods=['POST'])
def create_customer():
    try:
        shop_subdomain = request.host.split('.')[0] 
        first_name = request.form.get('first_name','New Customer')
        last_name = request.form.get('last_name',' Last Name')
        password = request.form.get('password','default')
        email = request.form.get('email', f"{uuid.uuid4().hex[:8]}@linkbay.it")
        phone = request.form.get('phone','0000000')
        address = request.form.get('address','Customer address')
        city = request.form.get('city','City')
        state = request.form.get('state','State')
        postal_code = request.form.get('postal_code','Postal Code')
        country = request.form.get('country','Country')

        default_values = {
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state,
            "postal_code": postal_code,
            "country": country,
            "shop_name": shop_subdomain,
        }

        with db_helper.get_db_connection() as db_conn:
            customer_model = Customers(db_conn)
            new_customer_id = customer_model.create_customer(default_values)

        return jsonify({
            'success': True,
            'message': 'Customer created successfully.',
            'customer_id': new_customer_id
        })
    except Exception as e:
        logging.info(f"Error creating customer: {e}")
        return jsonify({'success': False, 'message': 'Failed to create Customer.'}), 500
    
@customers_bp.route('/admin/cms/pages/customer/<int:customer_id>', methods=['GET', 'POST'])
@customers_bp.route('/admin/cms/pages/customer', methods=['GET', 'POST'])
def manage_customer(customer_id=None):
    username = check_user_authentication()
    if isinstance(username, str):
        with db_helper.get_db_connection() as db_conn:
            customer_model = Customers(db_conn)

            if request.method == 'POST':
                data = request.get_json()  
                try:
                    if customer_id:  # Modifica
                        success = customer_model.update_customer(customer_id, data)
                    else:  # Creazione
                        success = customer_model.create_customer(data)

                    if success:
                        return jsonify({'status': 'success', 'message': 'Collection saved successfully.'})
                    else:
                        return jsonify({'status': 'error', 'message': 'Failed to save the customer.'})
                except Exception as e:
                    logging.info(f"Error managing customer: {e}")
                    return jsonify({'status': 'error', 'message': 'An error occurred.'})

            # Per GET: Ottieni i dettagli del prodotto (se esiste)
            customer = customer_model.get_customer_by_id(customer_id) if customer_id else {}

            shop_subdomain = request.host.split('.')[0]  

            # Log di debug per verificare i dati passati
            logging.info(f"Customer: {customer}")
            logging.info(f"Shop Subdomain: {shop_subdomain}")

            return render_template(
                'admin/cms/pages/manage_customer.html',
                title='Manage Customer',
                username=username,
                customer=customer,
                shop_subdomain=shop_subdomain 
            )
    return username

    
@customers_bp.route('/admin/cms/update_customer', methods=['POST'])
def update_customer():
    try:
        data = request.form.to_dict()
        customer_id = data.get('id')

        if not customer_id or not customer_id.isdigit():
            return jsonify({'success': False, 'message': 'Invalid or missing Customer ID.'}), 400

        shop_name = request.host.split('.')[0]  # Ottieni il nome del negozio dal sottodominio

        with db_helper.get_db_connection() as db_conn:
            customer_model = Customers(db_conn)
            success = customer_model.update_customer(int(customer_id), data, shop_name)

        if success:
            return jsonify({'success': True, 'message': 'Customer updated successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update customer.'}), 500
    except Exception as e:
        import traceback
        logging.info(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
    
@customers_bp.route('/admin/cms/delete_customers', methods=['POST'])
def delete_customers():
    try:
        data = request.get_json()  # Ottieni i dati dalla richiesta
        customer_ids = data.get('customer_ids')  # Array di ID dei clienti da eliminare

        if not customer_ids:
            return jsonify({'success': False, 'message': 'No customer IDs provided.'}), 400

        shop_subdomain = request.host.split('.')[0]  # Ottieni il nome del negozio

        with db_helper.get_db_connection() as db_conn:
            customer_model = Customers(db_conn)
            for customer_id in customer_ids:
                success = customer_model.delete_customer(customer_id, shop_subdomain)
                if not success:
                    return jsonify({'success': False, 'message': f'Failed to delete customer with ID {customer_id}.'}), 500

        return jsonify({'success': True, 'message': 'Selected customers deleted successfully.'})
    except Exception as e:
        logging.info(f"Error deleting customers: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500

@customers_bp.route('/admin/cms/pages/marketing')
def marketing():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/marketing.html', title='Marketing', username=username)
    return username

