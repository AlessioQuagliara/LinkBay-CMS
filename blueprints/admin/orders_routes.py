from flask import Blueprint, render_template, request, jsonify
from models.database import db
from models.orders import Order, OrderItem
from models.products import Product
from models.customers import Customer
from models.payments import Payment
from models.shipping import Shipping
from helpers import check_user_authentication
import logging

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione degli ordini
orders_bp = Blueprint('orders', __name__)

# 📌 Route per visualizzare tutti gli ordini
@orders_bp.route('/admin/cms/pages/orders', methods=['GET']) 
def orders():
    """
    Mostra la lista di tutti gli ordini per il negozio attuale.
    """
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_subdomain = request.host.split('.')[0]  # Ottiene il nome del negozio dal sottodominio

    try:
        # Ottiene tutti gli ordini con i relativi clienti in una singola query ottimizzata
        orders_list = (
            db.session.query(Order, Customer.email)
            .join(Customer, Order.customer_id == Customer.id, isouter=True)  # Outer join per gestire ordini senza clienti
            .filter(Order.shop_name == shop_subdomain)
            .all()
        )

        # Prepara i dettagli degli ordini
        detailed_orders = []
        for order, customer_email in orders_list:
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            
            detailed_orders.append({
                "id": order.id,
                "customer_email": customer_email if customer_email else "Guest",  # Se non c'è email, mostra "Guest"
                "status": order.status,
                "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "total_price": order.total_price,
                "total_items": len(order_items),
                "total_quantity": sum(item.quantity for item in order_items),
            })

        return render_template(
            'admin/cms/pages/orders.html',
            title='Orders',
            username=username,
            orders=detailed_orders,
            shop_subdomain=shop_subdomain
        )
    except Exception as e:
        logging.error(f"Errore nel recupero degli ordini: {e}")
        return jsonify({'success': False, 'message': 'Errore nel recupero degli ordini.'}), 500

# 📌 Route per creare/modificare un ordine
@orders_bp.route('/admin/cms/pages/order/<int:order_id>', methods=['GET', 'POST'])
@orders_bp.route('/admin/cms/pages/order', defaults={'order_id': None}, methods=['GET', 'POST'])
def manage_order(order_id=None):
    """
    Gestisce la visualizzazione e modifica di un ordine.
    - Se viene fornito un ID ordine, recupera i dettagli dell'ordine esistente.
    - Se l'ID ordine è `None`, permette la creazione di un nuovo ordine.
    """
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_subdomain = request.host.split('.')[0]  # Ottiene il nome del negozio dal sottodominio

    try:
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
        order = Order.query.filter_by(id=order_id, shop_name=shop_subdomain).first() if order_id else None

        # Recupera gli elementi dell'ordine, pagamenti e spedizioni
        order_items = OrderItem.query.filter_by(order_id=order.id).all() if order else []
        payments = Payment.query.filter_by(order_id=order.id).all() if order else []
        shipping = Shipping.query.filter_by(order_id=order.id).first() if order else None

        # Recupera il cliente
        customer = Customer.query.get(order.customer_id) if order and order.customer_id else None

        # Recupera tutti i prodotti del negozio per la selezione
        products = Product.query.filter_by(shop_name=shop_subdomain).all()

        return render_template(
            'admin/cms/pages/manage_order.html',
            title='Manage Order',
            username=username,
            order=order,
            order_items=order_items,
            payments=payments,
            shipping=shipping,
            customer=customer,
            products=products,
            shop_subdomain=shop_subdomain
        )

    except Exception as e:
        logging.error(f"Errore nella gestione dell'ordine: {e}")
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'}), 500

# 📌 Route per gestire la lista ordini
@orders_bp.route('/admin/cms/pages/order-list/<int:order_id>', methods=['GET', 'POST'])
@orders_bp.route('/admin/cms/pages/order-list/', defaults={'order_id': None}, methods=['GET', 'POST'])
def manage_order_list(order_id=None):
    """
    Gestisce la lista degli ordini e i dettagli di un ordine specifico.
    - Se viene fornito un `order_id`, visualizza e modifica i dettagli di un ordine.
    - Se `order_id` è `None`, mostra la lista completa degli ordini.
    """
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_subdomain = request.host.split('.')[0]  # Identifica il negozio dal sottodominio

    try:
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

        # Recupera tutti gli ordini del negozio
        orders = Order.query.filter_by(shop_name=shop_subdomain).all() if not order_id else []

        # Recupera i dettagli dell'ordine se `order_id` è fornito
        order = Order.query.filter_by(id=order_id, shop_name=shop_subdomain).first() if order_id else None
        order_items = OrderItem.query.filter_by(order_id=order.id).all() if order else []
        payments = Payment.query.filter_by(order_id=order.id).all() if order else []
        shipping = Shipping.query.filter_by(order_id=order.id).first() if order else None

        # Recupera il cliente associato all'ordine
        customer = Customer.query.get(order.customer_id) if order and order.customer_id else None

        # Recupera tutti i prodotti disponibili nel negozio
        products = Product.query.filter_by(shop_name=shop_subdomain).all()

        return render_template(
            'admin/cms/pages/manage_order_list.html',
            title='Manage Order Items',
            username=username,
            order=order,
            orders=orders,
            order_items=order_items,
            payments=payments,
            shipping=shipping,
            customer=customer,
            products=products,
            shop_subdomain=shop_subdomain
        )

    except Exception as e:
        logging.error(f"Errore nella gestione della lista ordini: {e}")
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'}), 500

# 📌 API per creare un nuovo ordine
@orders_bp.route('/admin/cms/create_order', methods=['POST'])
def create_order():
    """
    API per creare un nuovo ordine.
    - Richiede `order_number`, `total_amount` e `status`.
    - Salva l'ordine nel database SQLAlchemy.
    """
    try:
        data = request.get_json()
        shop_name = request.host.split('.')[0]  # Identifica il negozio dal sottodominio

        # 🛑 Validazione campi obbligatori
        required_fields = ['order_number', 'total_amount', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        # ✅ Creazione nuovo ordine
        new_order = Order(
            shop_name=shop_name,
            order_number=data['order_number'],
            total_amount=data['total_amount'],
            status=data['status'],
            customer_id=data.get('customer_id')  # Opzionale
        )

        db.session.add(new_order)
        db.session.commit()  # 🔄 Commit transazionale

        return jsonify({'success': True, 'message': 'Order created successfully.', 'order_id': new_order.id})

    except Exception as e:
        db.session.rollback()  # 🛑 Annulla operazione in caso di errore
        logging.error(f"Error creating order: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while creating the order.'}), 500


# 📌 API per eliminare uno o più ordini
@orders_bp.route('/admin/cms/delete_orders', methods=['POST'])
def delete_order():
    """
    API per eliminare ordini.
    - Richiede una lista `order_ids`.
    - Cancella gli ordini se esistono.
    """
    try:
        data = request.get_json()
        order_ids = data.get('order_ids')

        # 🛑 Controlla se sono stati forniti ID validi
        if not order_ids or not isinstance(order_ids, list):
            return jsonify({'success': False, 'message': 'No valid order IDs provided.'}), 400

        # 🔄 Elimina gli ordini in blocco
        deleted_orders = Order.query.filter(Order.id.in_(order_ids)).delete(synchronize_session=False)
        db.session.commit()

        if deleted_orders > 0:
            return jsonify({'success': True, 'message': f'{deleted_orders} orders deleted successfully.'})
        else:
            return jsonify({'success': False, 'message': 'No orders found to delete.'}), 404

    except Exception as e:
        db.session.rollback()  # 🛑 Rollback in caso di errore
        logging.error(f"Error deleting orders: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500


# 📌 API per aggiornare un ordine
@orders_bp.route('/admin/cms/update_order', methods=['POST'])
def update_order():
    """
    API per aggiornare un ordine.
    - Richiede `order_id` e almeno un campo modificabile (`status`, `total_amount`, `customer_id`).
    """
    try:
        data = request.get_json()
        order_id = data.get('order_id')

        # 🛑 Controllo campo obbligatorio
        if not order_id:
            return jsonify({'success': False, 'message': 'Order ID is missing.'}), 400

        # 🔍 Recupera l'ordine da aggiornare
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Order not found.'}), 404

        # 🔄 Aggiorna i campi se forniti
        if 'status' in data:
            order.status = data['status']
        if 'total_amount' in data:
            order.total_amount = data['total_amount']
        if 'customer_id' in data:
            customer = Customer.query.get(data['customer_id'])
            if not customer:
                return jsonify({'success': False, 'message': 'Invalid customer ID provided.'}), 400
            order.customer_id = data['customer_id']

        db.session.commit()  # 🔄 Salva le modifiche

        return jsonify({'success': True, 'message': 'Order updated successfully.'})

    except Exception as e:
        db.session.rollback()  # 🛑 Rollback in caso di errore
        logging.error(f"Error updating order: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while updating the order.'}), 500

# 📌 API per ottenere tutti i clienti di un negozio
@orders_bp.route('/admin/cms/customers', methods=['GET'])
def get_customers():
    """
    Restituisce tutti i clienti di un negozio.
    """
    try:
        shop_name = request.host.split('.')[0]  # Nome del negozio

        customers = Customer.query.filter_by(shop_name=shop_name).all()

        return jsonify({
            'success': True,
            'customers': [customer.to_dict() for customer in customers]
        })
    except Exception as e:
        logging.error(f"Error fetching customers: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch customers.'}), 500


# 📌 API per ottenere i dettagli di un cliente specifico
@orders_bp.route('/admin/cms/customer/<int:customer_id>', methods=['GET'])
def get_customer_details(customer_id):
    """
    Restituisce i dettagli di un cliente specifico.
    """
    try:
        customer = Customer.query.get(customer_id)
        if customer:
            return jsonify({'success': True, 'customer': customer.to_dict()})
        return jsonify({'success': False, 'message': 'Customer not found.'}), 404
    except Exception as e:
        logging.error(f"Error fetching customer details: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500


# 📌 API per aggiungere un prodotto a un ordine
@orders_bp.route('/admin/cms/add_product_to_order', methods=['POST'])
def add_product_to_order():
    """
    Aggiunge un prodotto a un ordine esistente.
    """
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        if not order_id or not product_id:
            return jsonify({'success': False, 'message': 'Order ID or Product ID is missing.'}), 400

        order = Order.query.get(order_id)
        product = Product.query.get(product_id)

        if not order or not product:
            return jsonify({'success': False, 'message': 'Order or product not found.'}), 404

        # Aggiungi il prodotto all'ordine
        order.add_product(product, quantity)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Product added to order successfully.'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding product to order: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500


# 📌 API per rimuovere prodotti da un ordine
@orders_bp.route('/admin/cms/remove_products_from_order', methods=['POST'])
def remove_products_from_order():
    """
    Rimuove prodotti specifici da un ordine.
    """
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        product_ids = data.get('product_ids', [])

        if not order_id or not product_ids:
            return jsonify({'success': False, 'message': 'Order ID or Product IDs missing.'}), 400

        order = Order.query.get(order_id)

        if not order:
            return jsonify({'success': False, 'message': 'Order not found.'}), 404

        order.remove_products(product_ids)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Products removed successfully.'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error removing products from order: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500


# 📌 API per ottenere prodotti tramite ID
@orders_bp.route('/admin/cms/get_products_by_ids', methods=['POST'])
def get_products_by_ids():
    """
    Restituisce i dettagli dei prodotti specificati dagli ID.
    """
    try:
        data = request.get_json()
        product_ids = data.get('product_ids', [])

        if not product_ids:
            return jsonify({'success': False, 'message': 'No product IDs provided.'}), 400

        products = Product.query.filter(Product.id.in_(product_ids)).all()

        if products:
            return jsonify({'success': True, 'products': [product.to_dict() for product in products]})
        return jsonify({'success': False, 'message': 'No products found.'}), 404

    except Exception as e:
        logging.error(f"Error retrieving products by IDs: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500


# 📌 API per aggiungere più prodotti a un ordine
@orders_bp.route('/admin/cms/add_products_to_order', methods=['POST'])
def add_products_to_order():
    """
    Aggiunge più prodotti a un ordine.
    """
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        products = data.get('products', [])

        if not order_id or not products:
            return jsonify({'success': False, 'message': 'Order ID or Product data missing.'}), 400

        order = Order.query.get(order_id)

        if not order:
            return jsonify({'success': False, 'message': 'Order not found.'}), 404

        for product_data in products:
            product = Product.query.get(product_data['product_id'])
            if product:
                order.add_product(product, product_data.get('quantity', 1))

        db.session.commit()

        return jsonify({'success': True, 'message': 'Products added to order successfully.'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding products to order: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500


# 📌 API per aggiornare le quantità dei prodotti di un ordine
@orders_bp.route('/admin/cms/update_order_quantities', methods=['POST'])
def update_order_quantities():
    """
    Aggiorna le quantità dei prodotti in un ordine.
    """
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        items = data.get('items', [])

        if not order_id or not items:
            return jsonify({'success': False, 'message': 'Order ID or items missing.'}), 400

        # 🔍 Recupera l'ordine dal database
        order = Order.query.get(order_id)

        if not order:
            return jsonify({'success': False, 'message': 'Order not found.'}), 404

        # 🔄 Aggiorna la quantità per ogni prodotto
        for item in items:
            product_id = item.get('product_id')
            new_quantity = item.get('quantity')

            if not product_id or not isinstance(new_quantity, int) or new_quantity <= 0:
                return jsonify({'success': False, 'message': f'Invalid product ID or quantity for product {product_id}'}), 400

            # 🔍 Trova il prodotto nell'ordine
            order_item = next((i for i in order.items if i.product_id == product_id), None)

            if order_item:
                order_item.quantity = new_quantity  # 📌 Aggiorna la quantità
            else:
                return jsonify({'success': False, 'message': f'Product {product_id} not found in the order.'}), 404

        db.session.commit()  # 💾 Salva le modifiche nel database

        return jsonify({'success': True, 'message': 'Quantities updated successfully.'})

    except Exception as e:
        db.session.rollback()  # 🔄 Annulla le modifiche in caso di errore
        logging.error(f"Error updating order quantities: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while updating order quantities.'}), 500