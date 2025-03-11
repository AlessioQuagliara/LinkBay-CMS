from flask import Blueprint, jsonify, request, session
from models.database import db
from models.products import Product, ProductImage, create_new_product
from models.orders import Order, OrderItem, add_product_to_order
import logging
import os
import uuid
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO)

order_list_bp = Blueprint('orderlistApi', __name__, url_prefix='/api/')

# 📌 API per rimuovere prodotti da un ordine
@order_list_bp.route('/remove_products_from_order', methods=['POST'])
def remove_products_from_order():
    """ API per rimuovere più prodotti da un ordine """
    data = request.get_json()
    order_id = data.get('order_id')
    product_ids = data.get('product_ids', [])

    if not order_id or not product_ids:
        return jsonify({'success': False, 'message': 'Order ID or Product IDs missing.'}), 400

    # Recupera l'ordine
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'message': 'Order not found.'}), 404

    try:
        # Rimuove i prodotti specificati dall'ordine
        db.session.query(OrderItem).filter(
            OrderItem.order_id == order_id,
            OrderItem.product_id.in_(product_ids)
        ).delete(synchronize_session=False)

        db.session.commit()
        logging.info(f"✅ Prodotti {product_ids} rimossi dall'ordine {order_id}")

        return jsonify({'success': True, 'message': 'Products removed successfully!'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore durante la rimozione dei prodotti dall'ordine {order_id}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while removing products.'}), 500



# 📌 API per aggiornare le quantità dei prodotti di un ordine
@order_list_bp.route('/update_order_quantities', methods=['POST'])
def update_order_quantities():
    try:
        data = request.get_json()
        logging.info(f"📌 Dati ricevuti: {data}")  # Log dei dati ricevuti

        order_id = data.get('order_id')
        items = data.get('items', [])

        # 🚨 Verifica se i dati sono validi
        if not order_id or not items:
            logging.warning("⚠️ Order ID o items non validi o mancanti.")
            return jsonify({'success': False, 'message': 'Order ID or items missing.'}), 400

        # 🔍 Recupera l'ordine
        order = Order.query.get(order_id)
        if not order:
            logging.warning(f"⚠️ Ordine {order_id} non trovato.")
            return jsonify({'success': False, 'message': 'Order not found.'}), 404

        # 🔄 Prepara gli aggiornamenti
        product_ids = [item['product_id'] for item in items if 'product_id' in item and 'quantity' in item]
        logging.info(f"🔍 Prodotti da aggiornare: {product_ids}")

        order_items = OrderItem.query.filter(
            OrderItem.order_id == order_id,
            OrderItem.product_id.in_(product_ids)
        ).all()

        if not order_items:
            logging.warning(f"⚠️ Nessun prodotto corrispondente trovato nell'ordine {order_id}.")
            return jsonify({'success': False, 'message': 'No matching products found in order.'}), 404

        updated_count = 0  # Contatore aggiornamenti

        for order_item in order_items:
            new_quantity = next((item['quantity'] for item in items if item['product_id'] == order_item.product_id), None)
            
            if isinstance(new_quantity, int) and new_quantity > 0:
                logging.info(f"🔄 Aggiornamento prodotto {order_item.product_id}: {order_item.quantity} → {new_quantity}")
                order_item.quantity = new_quantity
                order_item.subtotal = new_quantity * order_item.price  # Aggiorna il totale
                updated_count += 1
            else:
                logging.warning(f"⚠️ Quantità non valida per il prodotto {order_item.product_id}: {new_quantity}")
                return jsonify({'success': False, 'message': f'Invalid quantity for product {order_item.product_id}'}), 400

        db.session.commit()  # 💾 Salva le modifiche nel database
        logging.info(f"✅ {updated_count} quantità aggiornate per l'ordine {order_id}")

        return jsonify({'success': True, 'message': f'{updated_count} quantities updated successfully!'})

    except Exception as e:
        db.session.rollback()  # Annulla le modifiche in caso di errore
        logging.error(f"❌ Errore durante l'aggiornamento delle quantità per l'ordine {order_id}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while updating quantities.'}), 500
    
# 📌 API per aggiungere un singolo prodotto a un ordine dalla tabella
@order_list_bp.route('/add_product_to_order_from_table', methods=['POST'])
def add_product_to_order_from_table():
    data = request.get_json()
    order_id = data.get('order_id')
    product_id = data.get('product_id')

    if not order_id or not product_id:
        return jsonify({'success': False, 'message': 'Order ID or Product ID is missing.'}), 400

    # Recupera l'ordine
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'message': 'Order not found.'}), 404

    # Recupera il prodotto
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found.'}), 404

    try:
        # Controlla se il prodotto è già nell'ordine
        order_item = OrderItem.query.filter_by(order_id=order_id, product_id=product_id).first()

        if order_item:
            # Se il prodotto esiste già, incrementa la quantità
            order_item.quantity += 1
            order_item.subtotal = order_item.quantity * order_item.price
        else:
            # Se non esiste, crea una nuova riga
            new_item = OrderItem(
                order_id=order_id,
                product_id=product_id,
                quantity=1,
                price=product.price,
                subtotal=product.price
            )
            db.session.add(new_item)

        db.session.commit()
        logging.info(f"✅ Prodotto {product_id} aggiunto/modificato nell'ordine {order_id}")

        return jsonify({'success': True, 'message': 'Product added to order successfully!'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore durante l'aggiunta del prodotto {product_id} all'ordine {order_id}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while adding the product.'}), 500
    
# 📌 API per aggiungere più prodotti a un ordine
@order_list_bp.route('/add_products_to_order', methods=['POST'])
def add_products_to_order():
    """ API per aggiungere più prodotti a un ordine in un'unica chiamata """
    data = request.get_json()
    order_id = data.get('order_id')

    # Recupera gli ID dei prodotti dalla sessione Flask
    product_ids = session.get('copied_product_ids', [])

    # Verifica se i dati sono validi
    if not order_id or not product_ids:
        return jsonify({'success': False, 'message': 'Order ID or no products copied.'}), 400

    # Recupera l'ordine
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'message': 'Order not found.'}), 404

    try:
        # Recupera i prodotti in un'unica query
        products = Product.query.filter(Product.id.in_(product_ids)).all()

        if not products:
            return jsonify({'success': False, 'message': 'No valid products found.'}), 400

        new_items = [
            OrderItem(
                order_id=order_id,
                product_id=product.id,
                quantity=1,  # Quantità predefinita, modificabile
                price=product.price,
                subtotal=product.price
            ) for product in products
        ]

        # Se non ci sono prodotti validi, annulla l'operazione
        if not new_items:
            return jsonify({'success': False, 'message': 'No valid products to add.'}), 400

        # Aggiunge tutti gli oggetti in una singola operazione
        db.session.bulk_save_objects(new_items)
        db.session.commit()
        logging.info(f"✅ {len(new_items)} prodotti aggiunti all'ordine {order_id}")

        # Pulisce gli ID prodotti copiati dalla sessione dopo l'inserimento
        session.pop('copied_product_ids', None)

        return jsonify({'success': True, 'message': f'{len(new_items)} products added successfully!'})

    except Exception as e:
        db.session.rollback()  # Annulla eventuali modifiche in caso di errore
        logging.error(f"❌ Errore durante l'aggiunta dei prodotti all'ordine {order_id}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while adding products.'}), 500