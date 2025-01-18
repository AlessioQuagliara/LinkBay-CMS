from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect
from models.orders import Orders  # importo la classe database
from models.products import Products 
from models.customers import Customers 
from models.payments import Payments 
from models.shipping import Shipping
from db_helpers import DatabaseHelper
from db_helpers import DatabaseHelper
from helpers import check_user_authentication
import logging
logging.basicConfig(level=logging.INFO)

db_helper = DatabaseHelper()

# Blueprint
orders_bp = Blueprint('orders', __name__)

# Rotte per la gestione

@orders_bp.route('/admin/cms/pages/orders', methods=['GET'])
def orders():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_subdomain = request.host.split('.')[0]  # Identifica il negozio dal sottodominio

        with db_helper.get_db_connection() as db_conn:
            orders_model = Orders(db_conn)
            customers_model = Customers(db_conn)

            # Fetch all orders for the shop
            orders_list = orders_model.get_all_orders(shop_subdomain)

            # Prepare detailed orders
            detailed_orders = []
            for order in orders_list:
                # Fetch customer details if customer_id exists
                customer_details = None
                if order.get('customer_id'):  # Verifica che l'ID del cliente esista
                    customer_details = customers_model.get_customer_by_id(order['customer_id'])

                # Fetch total items and total quantity for the order
                order_items = orders_model.get_order_items(order['id'])
                total_items = len(order_items)  # Numero totale di articoli
                total_quantity = sum(item['quantity'] for item in order_items)  # Quantità totale

                # orders_bpend all details
                detailed_orders.append({
                    **order,  # Include tutti i campi dell'ordine
                    "customer_email": customer_details['email'] if customer_details else None,
                    "total_items": total_items,
                    "total_quantity": total_quantity,
                })

        # Renderizza il template con i dati dettagliati
        return render_template(
            'admin/cms/pages/orders.html',
            title='Orders',
            username=username,
            orders=detailed_orders,  # Pass detailed orders to the template
            shop_subdomain=shop_subdomain
        )
    return username

@orders_bp.route('/admin/cms/pages/order/<int:order_id>', methods=['GET', 'POST'])
@orders_bp.route('/admin/cms/pages/order', defaults={'order_id': None}, methods=['GET', 'POST'])
def manage_order(order_id):
    username = check_user_authentication()
    if isinstance(username, str):
        with db_helper.get_db_connection() as db_conn:
            order_model = Orders(db_conn)
            customer_model = Customers(db_conn)
            product_model = Products(db_conn)
            payment_model = Payments(db_conn)
            shipping_model = Shipping(db_conn)

            shop_subdomain = request.host.split('.')[0]  

            if request.method == 'POST':
                data = request.get_json()  
                try:
                    if order_id:
                        success = order_model.update_order(order_id, data)
                    else:
                        success = order_model.create_order(data)

                    if success:
                        return jsonify({'status': 'success', 'message': 'Order saved successfully!'})
                    else:
                        return jsonify({'status': 'error', 'message': 'Failed to save the order.'})
                except Exception as e:
                    logging.info(f"Error managing order: {e}")
                    return jsonify({'status': 'error', 'message': 'An error occurred.'})

            order = order_model.get_order_by_id(shop_subdomain, order_id) if order_id else {}
            order_items = order_model.get_order_items(order_id) if order_id else []
            payments = payment_model.get_payments_by_order_id(order_id) if order_id else []
            shipping = shipping_model.get_shipping_by_order_id(order_id) if order_id else {}

            # Modifica qui il recupero del cliente
            customer = customer_model.get_customer_by_id(order['customer_id']) if order and 'customer_id' in order else None

            # Elenco prodotti per il negozio
            products = product_model.get_all_products(shop_subdomain)

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
    return username

@orders_bp.route('/admin/cms/pages/order-list/<int:order_id>', methods=['GET', 'POST'])
@orders_bp.route('/admin/cms/pages/order-list/', methods=['GET', 'POST'])
def manage_order_list(order_id=None):
    username = check_user_authentication()
    if isinstance(username, str):
        with db_helper.get_db_connection() as db_conn:
            # Inizializza i modelli
            order_model = Orders(db_conn)
            customer_model = Customers(db_conn)
            payment_model = Payments(db_conn)
            shipping_model = Shipping(db_conn)
            product_model = Products(db_conn)

            shop_subdomain = request.host.split('.')[0]

            if request.method == 'POST':
                data = request.get_json()
                try:
                    if order_id:
                        success = order_model.update_order(order_id, data)
                    else:
                        success = order_model.create_order(data)

                    if success:
                        return jsonify({'status': 'success', 'message': 'Order saved successfully!'})
                    else:
                        return jsonify({'status': 'error', 'message': 'Failed to save the order.'})
                except Exception as e:
                    logging.info(f"Error managing order: {e}")
                    return jsonify({'status': 'error', 'message': 'An error occurred.'})

            # Dati ordine
            order = order_model.get_order_by_id(shop_subdomain, order_id) if order_id else {}
            orders = order_model.get_all_orders(shop_subdomain) if not order_id else []

            # Dettagli aggiuntivi per ordine specifico
            order_items = order_model.get_order_items(order_id) if order_id else []
            payments = payment_model.get_payments_by_order_id(order_id) if order_id else []
            shipping = shipping_model.get_shipping_by_order_id(order_id) if order_id else {}

            # Cliente
            customer = customer_model.get_customer_by_id(order['customer_id']) if order and 'customer_id' in order else None

            # Prodotti disponibili
            products = product_model.get_all_products(shop_subdomain)

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
    return username

@orders_bp.route('/admin/cms/create_order', methods=['POST'])
def create_order():
    try:
        data = request.get_json() 
        shop_name = request.host.split('.')[0]  

        print("Incoming data:", data)  
        print("Shop name:", shop_name)  

        required_fields = ['order_number', 'total_amount', 'status']
        for field in required_fields:
            if field not in data:
                error_message = f"Missing required field: {field}"
                print(error_message)  
                return jsonify({'success': False, 'message': error_message}), 400

        data['shop_name'] = shop_name
        print("Final data to be sent to the model:", data)  

        with db_helper.get_db_connection() as db_conn:
            orders_model = Orders(db_conn)
            order_id = orders_model.create_order(data)
            print("Order created with ID:", order_id)  

        if order_id:
            return jsonify({'success': True, 'message': 'Order created successfully.', 'order_id': order_id})
        else:
            print("Failed to create order.")  
            return jsonify({'success': False, 'message': 'Failed to create order.'}), 500
    except Exception as e:
        import traceback
        logging.info(f"Error creating order: {e}")
        print(traceback.format_exc())  
        return jsonify({'success': False, 'message': f'An error occurred: {e}'}), 500
    
@orders_bp.route('/admin/cms/delete_orders', methods=['POST'])
def delete_order():
    try:
        data = request.get_json()  # Ottieni i dati dalla richiesta
        order_ids = data.get('order_ids')  # Array di ID dei prodotti da eliminare

        if not order_ids:
            return jsonify({'success': False, 'message': 'No orders IDs provided.'}), 400

        with db_helper.get_db_connection() as db_conn:
            order_model = Orders(db_conn)
            for order_id in order_ids:
                success = order_model.delete_order(order_id)
                if not success:
                    return jsonify({'success': False, 'message': f'Failed to delete order with ID {order_id}.'}), 500

        return jsonify({'success': True, 'message': 'Selected orders deleted successfully.'})
    except Exception as e:
        logging.info(f"Error deleting orders: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500
    
@orders_bp.route('/admin/cms/update_order', methods=['POST'])
def update_order():
    try:
        data = request.get_json()  # Ottieni i dati dal client
        shop_name = request.host.split('.')[0]  # Recupera il nome del negozio

        if not data.get('order_id'):
            return jsonify({'success': False, 'message': 'Order ID is missing.'}), 400

        # Inizializza la connessione al database
        with db_helper.get_db_connection() as db_conn:
            orders_model = Orders(db_conn)

            # Aggiorna l'ordine
            success = orders_model.update_order(
                shop_name=shop_name,
                order_id=data.get('order_id'),
                customer_id=data.get('customer_id'),
                status=data.get('status'),
                total_amount=data.get('total_amount')
            )

            if success:
                return jsonify({'success': True, 'message': 'Order updated successfully.'})
            else:
                return jsonify({'success': False, 'message': 'Failed to update the order.'}), 500

    except Exception as e:
        logging.info(f"Error updating order: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while updating the order.'}), 500
    
@orders_bp.route('/admin/cms/customers', methods=['GET'])
def get_customers():
    try:
        shop_name = request.host.split('.')[0]  # Ottieni il nome del negozio
        with db_helper.get_db_connection() as db_conn:
            customer_model = Customers(db_conn)
            customers = customer_model.get_all_customers(shop_name)
        
        return jsonify({'success': True, 'customers': customers})
    except Exception as e:
        logging.info(f"Error fetching customers: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch customers.'}), 500
    

@orders_bp.route('/admin/cms/customer/<int:customer_id>', methods=['GET'])
def get_customer_details(customer_id):
    try:
        with db_helper.get_db_connection() as db_conn:
            customer_model = Customers(db_conn)
            customer = customer_model.get_customer_by_id(customer_id)
            if customer:
                return jsonify({'success': True, 'customer': customer})
            else:
                return jsonify({'success': False, 'message': 'Customer not found.'}), 404
    except Exception as e:
        logging.info(f"Error fetching customer details: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while fetching customer details.'}), 500

@orders_bp.route('/admin/cms/add_product_to_order', methods=['POST'])
def add_product_to_order():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        if not order_id or not product_id:
            return jsonify({'success': False, 'message': 'Order ID or Product ID is missing.'}), 400

        with db_helper.get_db_connection() as db_conn:
            orders_model = Orders(db_conn)
            result = orders_model.add_product_to_order(order_id, product_id, quantity)

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    except Exception as e:
        logging.info(f"Error in add_product_to_order route: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
    
@orders_bp.route('/admin/cms/remove_products_from_order', methods=['POST'])
def remove_products_from_order():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        product_ids = data.get('product_ids')

        if not order_id or not product_ids:
            return jsonify({'success': False, 'message': 'Order ID or Product IDs missing.'}), 400

        with db_helper.get_db_connection() as db_conn:
            orders_model = Orders(db_conn)
            success = orders_model.remove_order_items(order_id, product_ids)

            if success:
                return jsonify({'success': True, 'message': 'Products removed successfully.'})
            else:
                return jsonify({'success': False, 'message': 'Failed to remove products.'})
    except Exception as e:
        logging.info(f"Error removing products from order: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500
    
@orders_bp.route('/admin/cms/get_products_by_ids', methods=['POST'])
def get_products_by_ids():
    try:
        data = request.get_json()
        product_ids = data.get('product_ids', [])

        if not product_ids:
            return jsonify({'success': False, 'message': 'No product IDs provided.'}), 400

        with db_helper.get_db_connection() as db_conn:
            products_model = Products(db_conn)
            products = products_model.get_products_by_ids(product_ids)

        if products:
            return jsonify({'success': True, 'products': products})
        else:
            return jsonify({'success': False, 'message': 'No products found.'}), 404
    except Exception as e:
        logging.info(f"Error retrieving products by IDs: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while fetching products.'}), 500
    
@orders_bp.route('/admin/cms/add_products_to_order', methods=['POST'])
def add_products_to_order():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        products = data.get('products', [])

        if not order_id or not products:
            return jsonify({'success': False, 'message': 'Order ID or Products data missing.'}), 400

        with db_helper.get_db_connection() as db_conn:
            orders_model = Orders(db_conn)
            success = orders_model.add_multiple_order_items(order_id, products)

            if success:
                return jsonify({'success': True, 'message': 'Products added successfully.'})
            else:
                return jsonify({'success': False, 'message': 'Failed to add products to order.'})
    except Exception as e:
        logging.info(f"Error adding products to order: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500
    
@orders_bp.route('/admin/cms/update_order_quantities', methods=['POST'])
def update_order_quantities():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        items = data.get('items', [])

        if not order_id or not items:
            return jsonify({'success': False, 'message': 'Order ID or items missing.'}), 400

        with db_helper.get_db_connection() as db_conn:
            orders_model = Orders(db_conn)
            success = orders_model.update_order_items_quantities(order_id, items)

        if success:
            return jsonify({'success': True, 'message': 'Quantities updated successfully.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update quantities.'})
    except Exception as e:
        logging.info(f"Error updating order quantities: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500
    

