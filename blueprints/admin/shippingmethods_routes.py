from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from models.shippingmethods import ShippingMethods  # importo la classe database
from db_helpers import DatabaseHelper
db_helper = DatabaseHelper()
from db_helpers import DatabaseHelper
from helpers import check_user_authentication

# Blueprint
shipping_methods_bp = Blueprint('shipping_methods', __name__)

# Rotte per la gestione

@shipping_methods_bp.route('/admin/cms/pages/shipping-methods')
def shipping_methods():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]  # Ottieni il nome del negozio dal sottodominio
        with db_helper.get_db_connection() as db_conn:
            shipping_methods_model = ShippingMethods(db_conn)
            methods_list = shipping_methods_model.get_all_shipping_methods(shop_name)
        return render_template(
            'admin/cms/pages/shipping.html',
            title='Shipping Methods',
            username=username,
            methods=methods_list
        )
    return username


@shipping_methods_bp.route('/admin/cms/create_shipping_method', methods=['POST'])
def create_shipping_method():
    try:
        data = request.get_json()
        shop_name = request.host.split('.')[0]
        default_values = {
            "shop_name": shop_name,
            "name": data.get("name", "Standard Shipping"),
            "description": data.get("description", "Default shipping method"),
            "country": data.get("country", "Worldwide"),
            "region": data.get("region"),
            "cost": data.get("cost", 0.0),
            "estimated_delivery_time": data.get("estimated_delivery_time", "5-7 business days"),
            "is_active": data.get("is_active", True)
        }
        with db_helper.get_db_connection() as db_conn:
            shipping_methods_model = ShippingMethods(db_conn)
            new_method_id = shipping_methods_model.create_shipping_method(default_values)
        if new_method_id:
            return jsonify({'success': True, 'message': 'Shipping method created successfully.', 'method_id': new_method_id})
        else:
            return jsonify({'success': False, 'message': 'Failed to create shipping method.'})
    except Exception as e:
        print(f"Error creating shipping method: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500
    
@shipping_methods_bp.route('/admin/cms/delete_shippings', methods=['POST'])
def delete_shippings():
    try:
        data = request.get_json()
        shipping_ids = data.get('shipping_ids')

        if not shipping_ids or not isinstance(shipping_ids, list):
            return jsonify({'success': False, 'message': 'No shipping IDs provided or invalid format.'}), 400

        with db_helper.get_db_connection() as db_conn:
            shipping_methods_model = ShippingMethods(db_conn)
            for shipping_id in shipping_ids:
                success = shipping_methods_model.delete_shipping_method(shipping_id)
                if not success:
                    return jsonify({
                        'success': False,
                        'message': f'Failed to delete shipping method with ID {shipping_id}.'
                    }), 500

        return jsonify({'success': True, 'message': 'Selected shipping methods deleted successfully.'})
    except Exception as e:
        print(f"Error deleting shipping methods: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500
    
@shipping_methods_bp.route('/admin/cms/pages/shipping-method/<int:method_id>', methods=['GET', 'POST'])
@shipping_methods_bp.route('/admin/cms/pages/shipping-method', methods=['GET', 'POST'])
def manage_shipping_method(method_id=None):
    username = check_user_authentication()
    if isinstance(username, str):
        with db_helper.get_db_connection() as db_conn:
            shipping_model = ShippingMethods(db_conn)

            shop_subdomain = request.host.split('.')[0]  # Ottieni il nome del negozio dal sottodominio

            if request.method == 'POST':
                data = request.get_json()  
                try:
                    if method_id:  # Modifica
                        success = shipping_model.update_shipping_method(method_id, data)
                    else:  # Creazione
                        success = shipping_model.create_shipping_method(data)

                    if success:
                        return jsonify({'status': 'success', 'message': 'Shipping method saved successfully.'})
                    else:
                        return jsonify({'status': 'error', 'message': 'Failed to save the shipping method.'})
                except Exception as e:
                    print(f"Error managing shipping method: {e}")
                    return jsonify({'status': 'error', 'message': 'An error occurred.'})

            # Per GET: Ottieni i dettagli del metodo di spedizione (se esiste)
            shipping_method = shipping_model.get_shipping_method_by_id(method_id, shop_subdomain) if method_id else {}

            # Log di debug per verificare i dati passati
            print(f"Shipping Method: {shipping_method}")
            print(f"Shop Subdomain: {shop_subdomain}")

            return render_template(
                'admin/cms/pages/manage_shipping.html',
                title='Manage Shipping Method',
                username=username,
                method=shipping_method,
                shop_subdomain=shop_subdomain  # Passa il sottodominio al template
            )
    return username

@shipping_methods_bp.route('/admin/cms/update_shipping_method', methods=['POST'])
def update_shipping_method():
    username = check_user_authentication()
    if isinstance(username, str):
        try:
            # Ottieni i dati inviati dal form
            form_data = request.form
            shipping_id = form_data.get('id')

            if not shipping_id:
                return jsonify({'success': False, 'message': 'Shipping ID is required.'}), 400

            # Costruisci i dati aggiornati
            updated_data = {
                'name': form_data.get('name'),
                'description': form_data.get('description'),
                'country': form_data.get('country'),
                'region': form_data.get('region'),
                'cost': float(form_data.get('cost', 0)),
                'estimated_delivery_time': form_data.get('estimated_delivery_time'),
                'is_active': form_data.get('is_active') == '1',  # Converti a boolean
            }

            with db_helper.get_db_connection() as db_conn:
                shipping_model = ShippingMethods(db_conn)
                success = shipping_model.update_shipping_method(shipping_id, updated_data)

            if success:
                return jsonify({'success': True, 'message': 'Shipping method updated successfully.'})
            else:
                return jsonify({'success': False, 'message': 'Failed to update the shipping method.'}), 500
        except Exception as e:
            print(f"Error updating shipping method: {e}")
            return jsonify({'success': False, 'message': 'An error occurred.'}), 500
    return username

