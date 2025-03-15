from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for, flash
from public.pdf_printer import generate_order_pdf, generate_invoice_pdf
from models.database import db
from models.orders import Order, OrderItem, get_orders_by_shop
from models.products import Product
from models.customers import Customer
from models.payments import Payment
from models.shipping import Shipping
from datetime import datetime
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
    """
    Mostra la lista degli ordini per il negozio corrente con paginazione e filtri.
    """
    username = check_user_authentication()

    if not username:
        flash("Session expired. Please log in again.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]  # Nome del negozio

    # Recupera i parametri di filtro
    status_filter = request.args.get('status', type=str)
    amount_filter = request.args.get('amount', type=float)
    created_at_filter = request.args.get('created_at', type=str)

    # Recupera il numero della pagina
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Numero di ordini per pagina

    try:
        # ✅ Conta il totale PRIMA di chiamare .all()
        total_orders_query = db.session.query(db.func.count(Order.id)).filter(Order.shop_name == shop_subdomain)
        
        if status_filter:
            total_orders_query = total_orders_query.filter(Order.status == status_filter)

        if amount_filter:
            total_orders_query = total_orders_query.filter(Order.total_amount >= amount_filter)

        if created_at_filter:
            created_at_date = datetime.strptime(created_at_filter, "%Y-%m-%d")
            total_orders_query = total_orders_query.filter(db.func.date(Order.created_at) == created_at_date)

        total_orders = total_orders_query.scalar()

        # Costruisce la query con i filtri e la JOIN con Customers
        query = db.session.query(
            Order,
            Customer.first_name.label("customer_name"),
            Customer.last_name.label("customer_surname"),
            Customer.email.label("customer_email")
        ).join(Customer, Order.customer_id == Customer.id, isouter=True).filter(Order.shop_name == shop_subdomain)

        if status_filter:
            query = query.filter(Order.status == status_filter)

        if amount_filter:
            query = query.filter(Order.total_amount >= amount_filter)

        if created_at_filter:
            created_at_date = datetime.strptime(created_at_filter, "%Y-%m-%d")
            query = query.filter(db.func.date(Order.created_at) == created_at_date)

        # Applica la paginazione
        orders_paginated = query.order_by(Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

        # Convertiamo i risultati in un formato più facile da usare nel template
        orders_data = []
        for order, customer_name, customer_surname, customer_email in orders_paginated:
            orders_data.append({
                "id": order.id,
                "order_number": order.order_number,
                "customer_name": customer_name or "N/A",
                "customer_surname": customer_surname or "N/A",
                "customer_email": customer_email or "N/A",
                "total_items": len(order.order_items),  # Contiamo gli item in modo sicuro
                "total_quantity": sum(item.quantity for item in order.order_items),
                "total_amount": order.total_amount,
                "status": order.status,
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": order.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        # Creiamo un oggetto per la paginazione
        class Pagination:
            def __init__(self, total, per_page, page):
                self.total = total
                self.per_page = per_page
                self.page = page
                self.pages = (total + per_page - 1) // per_page
                self.has_prev = page > 1
                self.has_next = page < self.pages
                self.prev_num = page - 1 if self.has_prev else None
                self.next_num = page + 1 if self.has_next else None

            def iter_pages(self):
                return range(1, self.pages + 1)

        pagination = Pagination(total_orders, per_page, page)

        return render_template(
            'admin/cms/pages/orders.html',
            title='Orders',
            username=username,
            orders=orders_data,
            pagination=pagination,
            shop_subdomain=shop_subdomain
        )

    except Exception as e:
        logging.error(f"❌ Errore nel caricamento degli ordini: {str(e)}")
        flash("Si è verificato un errore nel caricamento degli ordini.", "danger")
        return render_template(
            'admin/cms/pages/error.html',
            title="Errore",
            message="Non è stato possibile caricare gli ordini."
        ), 500

# 📌 Route per creare/modificare un ordine
@orders_bp.route('/admin/cms/pages/order/<int:order_id>', methods=['GET', 'POST'])
@orders_bp.route('/admin/cms/pages/order', defaults={'order_id': None}, methods=['GET', 'POST'])
@handle_request_errors
def manage_order(order_id=None):
    """
    Visualizza, modifica o crea un ordine.
    """
    username = check_user_authentication()

    if not username:
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]  # Nome del negozio

    if request.method == 'POST':
        try:
            data = request.get_json()

            if not data:
                return jsonify({'status': 'error', 'message': 'Invalid JSON data.'}), 400

            if order_id:
                # Modifica ordine esistente
                order = Order.query.filter_by(id=order_id, shop_name=shop_subdomain).first()
                if not order:
                    return jsonify({'status': 'error', 'message': 'Order not found.'}), 404

                # Aggiorna lo stato e il cliente
                order.status = data.get('status', order.status)
                order.customer_id = data.get('customer_id', order.customer_id)

                # ✅ Ricalcola il totale dell'ordine
                order.total_amount = db.session.query(
                    db.func.sum(OrderItem.quantity * OrderItem.price)
                ).filter(OrderItem.order_id == order.id).scalar() or 0.0

                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Order updated successfully!', 'total_amount': order.total_amount})

            else:
                # Creazione nuovo ordine
                new_order = Order(
                    shop_name=shop_subdomain,
                    customer_id=data.get('customer_id'),
                    total_amount=0.0,  # 🛑 Il totale sarà aggiornato quando vengono aggiunti articoli
                    status=data.get('status', 'Draft')
                )
                db.session.add(new_order)
                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Order created successfully!', 'order_id': new_order.id})

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error managing order: {e}")
            return jsonify({'status': 'error', 'message': 'An error occurred while processing the order.'}), 500

    # Recupera i dettagli dell'ordine e ricalcola il totale
    order_details = get_order_details(order_id, shop_subdomain) if order_id else None

    # ✅ Calcola il `total_amount` solo se l'ordine esiste
    total_amount = 0.0
    if order_id:
        total_amount = db.session.query(
            db.func.sum(OrderItem.quantity * OrderItem.price)
        ).filter(OrderItem.order_id == order_id).scalar() or 0.0

    products = Product.query.filter_by(shop_name=shop_subdomain).all()

    return render_template(
        'admin/cms/pages/manage_order.html',
        title='Manage Order',
        username=username,
        products=products,
        shop_subdomain=shop_subdomain,
        total_amount=total_amount,  # ✅ Passiamo `total_amount` al template
        **(order_details if order_details else {})
    )

# 📌 Route per ottenere i dettagli di un ordine e i suoi prodotti
@orders_bp.route('/admin/cms/pages/order-list/<int:order_id>', methods=['GET'])
@orders_bp.route('/admin/cms/pages/order-list/', defaults={'order_id': None}, methods=['GET'])
@handle_request_errors
def manage_order_list(order_id=None):
    """
    Visualizza la lista degli ordini o i dettagli di un ordine specifico.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, lo reindirizziamo correttamente
        flash("Session expired. Please log in again.", "warning")
        return redirect(url_for('user.login'))

    shop_subdomain = request.host.split('.')[0]

    # Se viene fornito un order_id, otteniamo i dettagli dell'ordine e i prodotti associati
    order = None
    order_items = []

    if order_id:
        order = Order.query.filter_by(id=order_id, shop_name=shop_subdomain).first()
        if order:
            order_items = order.order_items  # ✅ Ottimizzato con la relazione tra Order e OrderItem

    return render_template(
        'admin/cms/pages/manage_order_list.html',
        title='Manage Order Items',
        username=username,
        shop_subdomain=shop_subdomain,
        order=order,
        order_items=order_items  # ✅ Passiamo gli articoli dell'ordine al template
    )


@orders_bp.route('/admin/cms/pages/order/<int:order_id>/pdf', methods=['GET'])
def download_order_pdf(order_id):
    """ Route per scaricare il PDF dell'ordine """
    pdf_buffer = generate_order_pdf(order_id)
    if not pdf_buffer:
        return jsonify({'success': False, 'message': 'Order not found.'}), 404

    return send_file(pdf_buffer, as_attachment=True, download_name=f"order_{order_id}.pdf", mimetype="application/pdf")

@orders_bp.route('/admin/cms/pages/order/<int:order_id>/pdf', methods=['GET'])
def generate_invoice_pdf(order_id):
    """ Route per scaricare il PDF dell'ordine """
    pdf_buffer = generate_invoice_pdf(order_id)
    if not pdf_buffer:
        return jsonify({'success': False, 'message': 'Order not found.'}), 404

    return send_file(pdf_buffer, as_attachment=True, download_name=f"InvoiceN00{order_id}.pdf", mimetype="application/pdf")