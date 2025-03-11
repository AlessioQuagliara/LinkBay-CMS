from flask import Blueprint, render_template, request, jsonify
from models.database import db
from models.orders import Order, OrderItem, get_orders_by_shop
from models.products import Product
from models.customers import Customer
from models.payments import Payment
from models.shipping import Shipping
from functools import wraps
from helpers import check_user_authentication
import logging

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione degli ordini
orders_bp = Blueprint('orders', __name__)

# 🔄 Funzione Helper per gestire gli errori
def handle_request_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Errore in {func.__name__}: {e}")
            return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
    return wrapper

# 🔄 Funzione Helper per recuperare i dettagli dell'ordine
def get_order_details(order_id, shop_subdomain):
    order = Order.query.filter_by(id=order_id, shop_name=shop_subdomain).first()
    if not order:
        return None

    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    payments = Payment.query.filter_by(order_id=order.id).all()
    shipping = Shipping.query.filter_by(order_id=order.id).first()
    customer = Customer.query.get(order.customer_id) if order.customer_id else None

    return {
        'order': order,
        'order_items': order_items,
        'payments': payments,
        'shipping': shipping,
        'customer': customer
    }

# 📌 Route per la pagina degli ordini
@orders_bp.route('/admin/cms/pages/orders', methods=['GET'])
@handle_request_errors
def orders():
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_subdomain = request.host.split('.')[0]
    detailed_orders = get_orders_by_shop(shop_subdomain)

    return render_template(
        'admin/cms/pages/orders.html',
        title='Orders',
        username=username,
        orders=detailed_orders,
        shop_subdomain=shop_subdomain
    )

# 📌 Route per creare/modificare un ordine
@orders_bp.route('/admin/cms/pages/order/<int:order_id>', methods=['GET', 'POST'])
@orders_bp.route('/admin/cms/pages/order', defaults={'order_id': None}, methods=['GET', 'POST'])
@handle_request_errors
def manage_order(order_id=None):
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_subdomain = request.host.split('.')[0]

    if request.method == 'POST':
        data = request.get_json()

        if order_id:
            # Modifica ordine esistente
            order = Order.query.filter_by(id=order_id, shop_name=shop_subdomain).first()
            if not order:
                return jsonify({'status': 'error', 'message': 'Order not found.'}), 404

            order.status = data.get('status', order.status)
            order.total_price = data.get('total_price', order.total_price)
            order.customer_id = data.get('customer_id', order.customer_id)

            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Order updated successfully!'})

        else:
            # Creazione nuovo ordine
            new_order = Order(
                shop_name=shop_subdomain,
                customer_id=data.get('customer_id'),
                total_price=data.get('total_price', 0),
                status=data.get('status', 'pending')
            )
            db.session.add(new_order)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Order created successfully!', 'order_id': new_order.id})

    # Recupera i dettagli dell'ordine se esiste
    order_details = get_order_details(order_id, shop_subdomain) if order_id else None
    products = Product.query.filter_by(shop_name=shop_subdomain).all()

    return render_template(
        'admin/cms/pages/manage_order.html',
        title='Manage Order',
        username=username,
        products=products,
        shop_subdomain=shop_subdomain,
        **order_details if order_details else {}
    )

# 📌 Route per ottenere i dettagli di un ordine e i suoi prodotti
@orders_bp.route('/admin/cms/pages/order-list/<int:order_id>', methods=['GET'])
@orders_bp.route('/admin/cms/pages/order-list/', defaults={'order_id': None}, methods=['GET'])
@handle_request_errors
def manage_order_list(order_id=None):
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_subdomain = request.host.split('.')[0]

    # Se viene fornito un order_id, otteniamo i dettagli dell'ordine e i prodotti associati
    order = None
    order_items = []
    
    if order_id:
        order = Order.query.filter_by(id=order_id, shop_name=shop_subdomain).first()
        if order:
            order_items = OrderItem.query.filter_by(order_id=order_id).all()

    return render_template(
        'admin/cms/pages/manage_order_list.html',
        title='Manage Order Items',
        username=username,
        shop_subdomain=shop_subdomain,
        order=order
    )


