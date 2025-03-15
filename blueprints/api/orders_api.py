from flask import Blueprint, jsonify, request, send_file
from datetime import datetime, timedelta
from models.database import db
from models.customers import Customer
from models.orders import Order
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

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


@ordersapi_bp.route('/orders/search', methods=['GET'])
def search_orders():
    """
    API per cercare gli ordini con filtri personalizzati.
    Permette di filtrare per order_number, status, customer_id e date range.
    """
    try:
        # 🔹 Recupera i parametri della query string
        order_number = request.args.get('order_number', type=str)
        status = request.args.get('status', type=str)
        customer_id = request.args.get('customer_id', type=int)
        start_date = request.args.get('start_date', type=str)  # Formato: YYYY-MM-DD
        end_date = request.args.get('end_date', type=str)  # Formato: YYYY-MM-DD

        # 🔍 Costruzione della query dinamica
        query = Order.query

        if order_number:
            query = query.filter(Order.order_number.ilike(f"%{order_number}%"))  # 🔍 Cerca per numero d'ordine (parziale)

        if status:
            query = query.filter(Order.status == status)  # 🎯 Filtra per stato

        if customer_id:
            query = query.filter(Order.customer_id == customer_id)  # 👤 Filtra per ID cliente

        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Order.created_at >= start_datetime)  # 🗓️ Filtra per data inizio

        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Order.created_at <= end_datetime)  # 🗓️ Filtra per data fine

        # 📦 Esegui la query
        orders = query.order_by(Order.created_at.desc()).all()

        # 🔄 Converti i risultati in formato JSON
        results = [{
            "id": order.id,
            "shop_name": order.shop_name,
            "order_number": order.order_number,
            "customer_id": order.customer_id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": order.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        } for order in orders]

        return jsonify({"success": True, "orders": results}), 200

    except SQLAlchemyError as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@ordersapi_bp.route('/latest-orders', methods=['GET'])
def latest_orders():
    """
    API per recuperare gli ultimi ordini effettuati nel negozio corrente.
    """
    shop_subdomain = request.host.split('.')[0]  # Estrai il nome del negozio dal sottodominio
    limit = request.args.get('limit', 5, type=int)  # Permette di modificare il numero di risultati (default: 5)

    try:
        # Query per recuperare gli ultimi ordini con i dati del cliente
        latest_orders = (
            db.session.query(
                Order.id,
                Order.order_number,
                Order.total_amount,
                Order.status,
                Order.created_at,
                Customer.first_name.label("customer_name"),
                Customer.last_name.label("customer_surname"),
                Customer.email.label("customer_email")
            )
            .join(Customer, Order.customer_id == Customer.id, isouter=True)
            .filter(Order.shop_name == shop_subdomain)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .all()
        )

        # Convertiamo i dati in formato JSON-friendly
        orders_data = [
            {
                "id": order.id,
                "order_number": order.order_number,
                "customer_name": f"{order.customer_name or 'N/A'} {order.customer_surname or ''}".strip(),
                "customer_email": order.customer_email or 'N/A',
                "total_amount": order.total_amount,
                "status": order.status,
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for order in latest_orders
        ]

        return jsonify({"success": True, "orders": orders_data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@ordersapi_bp.route('/sales-data', methods=['GET'])
def get_sales_data():
    try:
        last_week = datetime.utcnow() - timedelta(days=7)

        sales_data = (
            db.session.query(
                func.date(Order.created_at).label("date"),
                func.sum(Order.total_amount).label("total_sales")
            )
            .filter(Order.created_at >= last_week)
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
            .all()
        )

        dates = [row.date.strftime("%Y-%m-%d") for row in sales_data]
        sales = [float(row.total_sales) for row in sales_data]

        return jsonify({"success": True, "dates": dates, "sales": sales}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500