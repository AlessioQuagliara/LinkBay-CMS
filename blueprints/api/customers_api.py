from flask import Blueprint, jsonify
from models.customers import Customer
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
    