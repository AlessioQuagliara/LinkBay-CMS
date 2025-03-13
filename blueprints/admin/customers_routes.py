from flask import Blueprint, render_template, request, jsonify
from models.database import db
from models.customers import Customer  # Importa il modello SQLAlchemy
from helpers import check_user_authentication
import uuid
import logging

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione dei clienti
customers_bp = Blueprint('customers', __name__)

# 📌 Route per visualizzare i clienti nel pannello admin
@customers_bp.route('/admin/cms/pages/customers')
def customers():
    """
    Mostra la lista dei clienti del negozio.
    """
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_name = request.host.split('.')[0]  # Identifica il negozio dal sottodominio

    # Recupera i clienti dal database
    customers_list = Customer.query.filter_by(shop_name=shop_name).all()

    return render_template(
        'admin/cms/pages/customers.html', 
        title='Customers', 
        username=username, 
        customers=customers_list  # Passa i clienti al template
    )

# 📌 Route per creare un nuovo cliente
@customers_bp.route('/admin/cms/create_customer', methods=['POST'])
def create_customer():
    """
    Crea un nuovo cliente nel database.
    """
    try:
        shop_name = request.host.split('.')[0]

        # Recupera i dati dal form o imposta valori predefiniti
        new_customer = Customer(
            first_name=request.form.get('first_name', 'New Customer'),
            last_name=request.form.get('last_name', 'Last Name'),
            password=request.form.get('password', 'default'),
            email=request.form.get('email', f"{uuid.uuid4().hex[:8]}@linkbay.it"),
            phone=request.form.get('phone', '0000000'),
            address=request.form.get('address', 'Customer address'),
            city=request.form.get('city', 'City'),
            state=request.form.get('state', 'State'),
            postal_code=request.form.get('postal_code', 'Postal Code'),
            country=request.form.get('country', 'Country'),
            shop_name=shop_name
        )

        # Salva il cliente nel database
        db.session.add(new_customer)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Customer created successfully.', 'customer_id': new_customer.id})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating customer: {e}")
        return jsonify({'success': False, 'message': 'Failed to create Customer.'}), 500

# 📌 Route per gestire un cliente (visualizzazione o modifica)
@customers_bp.route('/admin/cms/pages/customer/<int:customer_id>', methods=['GET', 'POST'])
def manage_customer(customer_id):
    """
    Modifica o visualizza i dettagli di un cliente.
    """
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_name = request.host.split('.')[0]
    
    # Recupera il cliente dal database
    customer = Customer.query.filter_by(id=customer_id, shop_name=shop_name).first()

    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404

    if request.method == 'POST':
        try:
            data = request.get_json()
            for key, value in data.items():
                setattr(customer, key, value)  # Aggiorna i campi dinamicamente

            db.session.commit()
            return jsonify({'success': True, 'message': 'Customer updated successfully'})

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating customer: {e}")
            return jsonify({'success': False, 'message': 'An error occurred'}), 500

    return render_template(
        'admin/cms/pages/manage_customer.html',
        title='Manage Customer',
        username=username,
        customer=customer
    )

# 📌 Route per aggiornare un cliente
@customers_bp.route('/api/update_customer', methods=['POST'])
def update_customer():
    """
    Aggiorna le informazioni di un cliente esistente.
    """
    try:
        data = request.form.to_dict()
        customer_id = data.get('id')

        if not customer_id or not customer_id.isdigit():
            return jsonify({'success': False, 'message': 'Invalid or missing Customer ID.'}), 400

        shop_name = request.host.split('.')[0]

        # Recupera il cliente
        customer = Customer.query.filter_by(id=int(customer_id), shop_name=shop_name).first()

        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'}), 404

        # Aggiorna i dati
        for key, value in data.items():
            setattr(customer, key, value)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Customer updated successfully'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating customer: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred'}), 500

# 📌 Route per eliminare più clienti
@customers_bp.route('/admin/cms/delete_customers', methods=['POST'])
def delete_customers():
    """
    Elimina uno o più clienti dal database.
    """
    try:
        data = request.get_json()
        customer_ids = data.get('customer_ids')

        if not customer_ids:
            return jsonify({'success': False, 'message': 'No customer IDs provided.'}), 400

        shop_name = request.host.split('.')[0]

        # Elimina i clienti specificati
        customers_deleted = Customer.query.filter(Customer.id.in_(customer_ids), Customer.shop_name == shop_name).delete(synchronize_session=False)
        db.session.commit()

        if customers_deleted > 0:
            return jsonify({'success': True, 'message': 'Selected customers deleted successfully.'})
        else:
            return jsonify({'success': False, 'message': 'No customers were deleted.'}), 500

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting customers: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500

# 📌 Route per visualizzare la pagina marketing
@customers_bp.route('/admin/cms/pages/marketing')
def marketing():
    """
    Visualizza la pagina di marketing nel pannello admin.
    """
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/marketing.html', title='Marketing', username=username)
    return username