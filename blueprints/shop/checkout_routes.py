from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from models.database import db
from models.payments import Payment  # Modello dei pagamenti
from models.products import Product  # Modello dei prodotti
from models.shippingmethods import ShippingMethod  # Modello dei metodi di spedizione
from helpers import check_user_authentication
import logging

# 📌 Configurazione del logger
logging.basicConfig(level=logging.INFO)

# 📌 Blueprint per la gestione del checkout
checkout_bp = Blueprint('checkout', __name__)

# 🔹 **Rotta per la pagina di checkout**
@checkout_bp.route('/checkout')
def checkout():
    """
    Mostra la pagina di checkout con i prodotti in sessione.
    """
    cart = session.get('cart', [])

    # **Calcola il totale del carrello**
    subtotal = sum(float(item['price']) * int(item['quantity']) for item in cart)

    # **Ottieni il costo della spedizione dinamicamente**
    shop_name = request.host.split('.')[0]
    shipping_method = ShippingMethod.query.filter_by(shop_name=shop_name, is_active=True).first()
    shipping_cost = shipping_method.cost if shipping_method else 5.00  # Default a 5.00€

    total = subtotal + shipping_cost

    return render_template(
        'checkout/checkout.html', 
        title='Checkout', 
        cart=cart, 
        subtotal=subtotal, 
        shipping_cost=shipping_cost, 
        total=total
    )

# 🔹 **Rotta per completare il checkout**
@checkout_bp.route('/checkout/complete', methods=['POST'])
def complete_checkout():
    """
    Finalizza il checkout e mostra la conferma dell'ordine.
    """
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('checkout.checkout'))  # Se il carrello è vuoto, torna al checkout

    # **Recupera i dati del cliente dal form**
    customer_data = {
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'address': request.form.get('address'),
        'city': request.form.get('city'),
        'state': request.form.get('state'),
        'postal_code': request.form.get('postal_code'),
        'country': request.form.get('country'),
        'shipping_method': request.form.get('shipping_method'),
        'payment_method': request.form.get('payment_method')
    }

    try:
        # **(Opzionale) Logica per salvare l'ordine nel database**
        # new_order = Order(...)
        # db.session.add(new_order)
        # db.session.commit()

        # **Svuota il carrello**
        session['cart'] = []

        return render_template(
            'checkout/confirmation.html', 
            title='Ordine Confermato', 
            customer_data=customer_data, 
            cart=cart
        )
    except Exception as e:
        logging.error(f"❌ Errore nel completamento del checkout: {str(e)}")
        return jsonify({'error': 'Errore durante il checkout'}), 500

# 🔹 **Rotta per ottenere i metodi di spedizione**
@checkout_bp.route('/checkout/get_shipping_methods', methods=['GET'])
def get_shipping_methods():
    """
    Ottiene i metodi di spedizione disponibili per il negozio.
    """
    shop_name = request.host.split('.')[0]

    try:
        # **Recupera i metodi di spedizione attivi per lo shop**
        shipping_methods = ShippingMethod.query.filter_by(shop_name=shop_name, is_active=True).all()

        # **Converti i risultati in un formato JSON-friendly**
        methods_list = [
            {
                'id': method.id,
                'name': method.name,
                'description': method.description,
                'cost': method.cost,
                'estimated_delivery_time': method.estimated_delivery_time
            }
            for method in shipping_methods
        ]

        return jsonify(methods_list), 200

    except Exception as e:
        logging.error(f"❌ Errore durante il recupero dei metodi di spedizione: {str(e)}")
        return jsonify({'error': 'Impossibile recuperare i metodi di spedizione'}), 500