from flask import Blueprint, jsonify, request
from models.database import db
from models.customers import Customer
import uuid
import logging

logging.basicConfig(level=logging.INFO)

customersapi_bp = Blueprint('customersApi', __name__, url_prefix='/api/')

@customersapi_bp.route('/get-customers', methods=['GET'])
def get_customers():
    try:
        customers = Customer.query.all()
        customers_list = [customer.to_dict() for customer in customers]
        return jsonify({'success': True, 'customers': customers_list})
    except Exception as error:
        logging.error(f"Errore nel recupero clienti: {error}")
        return jsonify({'success': False, 'error': str(error)}), 500

@customersapi_bp.route('/customer/<int:customer_id>', methods=['GET'])
def customer(customer_id):
    try:
        customer = Customer.query.filter_by(id=customer_id).first_or_404()
        return jsonify({'success': True, 'customer': customer.to_dict()})
    except Exception as error:
        logging.error(f"Errore nel recupero del cliente {customer_id}: {error}")
        return jsonify({'success': False, 'error': str(error)}), 500
    
# 📌 Route per creare un nuovo cliente
@customersapi_bp.route('/create_customer', methods=['POST'])
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
    
@customersapi_bp.route('/customers/search', methods=['GET'])
def search_customers():
    """
    API per cercare i clienti con query dinamica.
    """
    try:
        query = request.args.get('query', type=str)

        if not query:
            return jsonify({"success": False, "error": "Nessuna query di ricerca"}), 400

        # Filtra i clienti per nome o email
        customers = Customer.query.filter(
            (Customer.first_name.ilike(f"%{query}%")) | 
            (Customer.email.ilike(f"%{query}%"))
        ).limit(10).all()  # Limitiamo a 10 risultati per evitare sovraccarico

        results = [{
            "id": customer.id,
            "first_name": customer.first_name,
            "email": customer.email
        } for customer in customers]

        return jsonify({"success": True, "customers": results}), 200

    except Exception as e:
        logging.error(f"❌ Errore nella ricerca clienti: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
    
@customersapi_bp.route('/recent-customers', methods=['GET'])
def get_recent_customers():
    try:
        recent_customers = (
            db.session.query(Customer)
            .order_by(Customer.created_at.desc())
            .limit(5)
            .all()
        )

        customers_data = [
            {
                "id": customer.id,
                "name": f"{customer.first_name} {customer.last_name}",
                "email": customer.email,
                "phone": customer.phone or "N/A",
                "created_at": customer.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for customer in recent_customers
        ]

        return jsonify({"success": True, "customers": customers_data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500