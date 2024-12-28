from flask import Blueprint, render_template, request, session, jsonify
from models.payments import Payments  # importo la classe database
from models.products import Products  # importo la classe database

# Blueprint
checkout_bp = Blueprint('checkout', __name__)

# Rotte per la gestione

@checkout_bp.route('/checkout')
def checkout():
    return render_template('checkout/checkout.html', title='Checkout')

@checkout_bp.route('/cart_contents', methods=['GET'])
def cart_contents():
    """Ritorna i contenuti del carrello in formato JSON."""
    cart = session.get('cart', [])
    return jsonify({'cart': cart})


@checkout_bp.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    """Rimuove un prodotto dal carrello."""
    data = request.get_json()
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'success': False, 'error': 'Product ID is required'}), 400

    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart})