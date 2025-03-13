from flask import Blueprint, jsonify, request, send_file
from models.database import db
from models.orders import Order
import logging
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO)

ordersapi_bp = Blueprint('ordersApi', __name__, url_prefix='/api/')

@ordersapi_bp.route('/order/<int:order_id>', methods=['GET'])
def get_order_details_api(order_id):
    try:
        shop_subdomain = request.host.split('.')[0]
        order = Order.query.filter_by(id=order_id, shop_name=shop_subdomain).first()

        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404

        return jsonify({'success': True, 'order': order.to_dict()})
    except Exception as error:
        logging.error(f"Errore nel recupero ordine: {error}")
        return jsonify({'success': False, 'message': str(error)}), 500
    
# 📌 API per creare un nuovo ordine
@ordersapi_bp.route('/create_order', methods=['POST'])
def create_order():
        data = request.get_json()
        shop_name = request.host.split('.')[0]

        required_fields = ['order_number', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        new_order = Order(
            shop_name=shop_name,
            order_number=data['order_number'],
            status=data['status'],
            customer_id=data.get('customer_id')
        )

        db.session.add(new_order)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Order created successfully.', 'order_id': new_order.id})

# 📌 API per eliminare uno o più ordini
@ordersapi_bp.route('/delete_orders', methods=['POST'])
def delete_order():
    data = request.get_json()
    order_ids = data.get('order_ids')

    if not order_ids or not isinstance(order_ids, list):
        return jsonify({'success': False, 'message': 'No valid order IDs provided.'}), 400

    deleted_orders = Order.query.filter(Order.id.in_(order_ids)).delete(synchronize_session=False)
    db.session.commit()

    if deleted_orders > 0:
        return jsonify({'success': True, 'message': f'{deleted_orders} orders deleted successfully.'})
    else:
        return jsonify({'success': False, 'message': 'No orders found to delete.'}), 404

# 📌 API per ottenere i campi della tabella Order
@ordersapi_bp.route('/get_order_fields', methods=['GET'])
def get_order_fields():
    fields = [column.name for column in Order.__table__.columns]
    return jsonify({'success': True, 'fields': fields})

# 📌 API per ottenere i dettagli di un ordine
@ordersapi_bp.route('/get_order/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'message': 'Order not found.'}), 404

    order_data = {column.name: getattr(order, column.name) for column in Order.__table__.columns}
    return jsonify({'success': True, 'order': order_data})
    

# 📌 API per aggiornare un ordine
@ordersapi_bp.route('/update_order', methods=['POST'])
def update_order():
    data = request.get_json()
    order_id = data.pop('order_id', None)

    if not order_id:
        return jsonify({'success': False, 'message': 'Order ID is missing.'}), 400

    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'message': 'Order not found.'}), 404

    # Filtra i campi validi per evitare errori
    for key, value in data.items():
        if hasattr(order, key):
            setattr(order, key, value)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Order updated successfully.'})

