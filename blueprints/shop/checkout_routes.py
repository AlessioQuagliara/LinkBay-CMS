from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for

from models.payments import Payments  # Importa la classe Payments
from models.products import Products  # Importa la classe Products

# Blueprint
checkout_bp = Blueprint('checkout', __name__)

# Rotta per la pagina di checkout
@checkout_bp.route('/checkout')
def checkout():
    """
    Mostra la pagina di checkout con i prodotti in sessione.
    """
    # Recupera i prodotti salvati in sessione
    cart = session.get('cart', [])
    
    # Calcola il totale del carrello
    subtotal = sum(float(item['price']) * int(item['quantity']) for item in cart)
    shipping_cost = 5.00  # Costo fisso della spedizione (puoi renderlo dinamico)
    total = subtotal + shipping_cost

    return render_template('checkout/checkout.html', 
                           title='Checkout', 
                           cart=cart, 
                           subtotal=subtotal, 
                           shipping_cost=shipping_cost, 
                           total=total)

# Rotta per completare il checkout
@checkout_bp.route('/checkout/complete', methods=['POST'])
def complete_checkout():
    """
    Finalizza il checkout e mostra la conferma dell'ordine.
    """
    # Recupera i dati del carrello
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('checkout.checkout'))  # Se il carrello è vuoto, torna al checkout

    # Recupera i dati del cliente dal form
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

    # Esegui la logica per salvare l'ordine (opzionale)

    # Svuota il carrello
    session['cart'] = []

    # Mostra la pagina di conferma
    return render_template('checkout/confirmation.html', 
                           title='Ordine Confermato', 
                           customer_data=customer_data, 
                           cart=cart)