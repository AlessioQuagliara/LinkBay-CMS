from flask import Blueprint, render_template, request, jsonify, redirect
from models.payments import Payments # importo la classe database
from models.payment_methods import PaymentMethods
from db_helpers import DatabaseHelper
from helpers import check_user_authentication

db_helper = DatabaseHelper()

# Blueprint
payments_bp = Blueprint('payments', __name__)

# Rotte per la gestione

@payments_bp.route('/admin/cms/pages/payments', methods=['GET'])
def payments():
    """
    Renderizza la pagina dei metodi di pagamento.
    """
    shop_name = request.host.split('.')[0]

    try:
        with db_helper.get_db_connection() as conn:
            payment_methods_model = PaymentMethods(conn)
            active_methods = payment_methods_model.get_all_payment_methods(shop_name)

        # Lista dei metodi attivi
        active_methods_dict = {method['method_name']: method for method in active_methods}

        return render_template(
            'admin/cms/pages/payments.html',
            active_methods=active_methods_dict,  # Passa i metodi attivi come dizionario
            shop_name=shop_name,
            title='Payments'
        )

    except Exception as e:
        print(f"Error rendering payments page: {e}")
        return render_template('admin/cms/pages/error.html', title='Error 500' ,message="Unable to load payment methods"), 500

@payments_bp.route('/admin/cms/pages/manage_payments/<method_name>', methods=['GET'])
def configure_payment_method(method_name):
    """
    Renderizza la pagina di configurazione per un metodo di pagamento specifico.
    """
    shop_name = request.host.split('.')[0]

    try:
        with db_helper.get_db_connection() as conn:
            payment_methods_model = PaymentMethods(conn)
            method = payment_methods_model.get_payment_method(shop_name, method_name)

        return render_template(
            'admin/cms/pages/manage_payments.html',
            shop_name=shop_name,
            method=method if method else {"method_name": method_name},
            title="Manage Payment"
        )

    except Exception as e:
        print(f"Error loading payment method configuration: {e}")
        return render_template('admin/cms/pages/error.html', message="Unable to load payment method configuration"), 500

@payments_bp.route('/admin/cms/pages/update_payment_method', methods=['POST'])
def update_payment_method():
    try:
        # Ottieni i dati dal form
        data = request.form.to_dict()
        method_name = data.get('method_name')

        if not method_name:
            return jsonify({'success': False, 'message': 'Invalid or missing method_name.'}), 400

        shop_name = request.host.split('.')[0]  # Ottieni il nome del negozio dal sottodominio

        with db_helper.get_db_connection() as db_conn:
            payment_methods_model = PaymentMethods(db_conn)

            # Controlla se il metodo esiste
            existing_method = payment_methods_model.get_payment_method(shop_name, method_name)
            if not existing_method:
                return jsonify({'success': False, 'message': f'Payment method "{method_name}" not found.'}), 404

            # Aggiorna il metodo di pagamento
            success = payment_methods_model.update_payment_method(
                method_id=existing_method['id'],
                data={
                    'api_key': data.get('api_key'),
                    'api_secret': data.get('api_secret'),
                    'extra_info': data.get('extra_info'),
                },
                shop_name=shop_name
            )

        if success:
            return jsonify({'success': True, 'message': f'Payment method "{method_name}" updated successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update payment method.'}), 500
    except Exception as e:
        import traceback
        print(f"Error updating payment method: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
    

@payments_bp.route('/payment-methods/<shop_name>', methods=['GET'])
def get_payment_methods(shop_name):
    """
    Restituisce i metodi di pagamento configurati per un negozio.
    """
    with db_helper.get_db_connection() as conn:
        payment_methods_model = PaymentMethods(conn)
        methods = payment_methods_model.get_all_payment_methods(shop_name)
    return jsonify({'methods': [method['method_name'] for method in methods]})

@payments_bp.route('/admin/cms/pages/payments/get_active_methods', methods=['GET'])
def get_active_payment_methods():
    """
    Endpoint per ottenere i metodi di pagamento attivi per lo shop.
    """
    shop_name = request.host.split('.')[0]

    try:
        with db_helper.get_db_connection() as conn:
            payment_methods_model = PaymentMethods(conn)
            active_methods = payment_methods_model.get_all_payment_methods(shop_name)

        # Costruisci una lista con informazioni sui metodi
        methods_info = [
            {
                'method_name': method['method_name'],
                'is_active': True,
                'api_key': method['api_key'],
                'api_secret': method['api_secret'],
                'extra_info': method['extra_info'],
            }
            for method in active_methods
        ]

        return jsonify({'success': True, 'methods': methods_info}), 200

    except Exception as e:
        print(f"Error fetching active payment methods: {e}")
        return jsonify({'success': False, 'error': 'Errore interno del server'}), 500
    
@payments_bp.route('/admin/cms/pages/add_payment_method', methods=['POST'])
def add_payment_method():
    try:
        data = request.json
        method_name = data.get('method_name')
        shop_name = data.get('shop_name')

        if not method_name or not shop_name:
            return jsonify({'success': False, 'message': 'Invalid or missing data.'}), 400

        with db_helper.get_db_connection() as db_conn:
            payment_methods_model = PaymentMethods(db_conn)

            # Verifica se il metodo esiste già
            existing_method = payment_methods_model.get_payment_method(shop_name, method_name)
            if existing_method:
                return jsonify({'success': False, 'message': f'{method_name} is already configured.'}), 400

            # Inserisci il nuovo metodo
            payment_methods_model.create_payment_method({
                'shop_name': shop_name,
                'method_name': method_name,
                'api_key': '',  # Campi vuoti, da aggiornare successivamente
                'api_secret': '',
                'extra_info': ''
            })

        return jsonify({'success': True, 'message': f'{method_name} configured successfully.'})
    except Exception as e:
        import traceback
        print(f"Error adding payment method: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500