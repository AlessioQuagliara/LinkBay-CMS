from flask import Blueprint, request, session, jsonify

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Aggiunge un prodotto al carrello nella sessione."""
    data = request.get_json()
    product_id = data.get('product_id')
    product_name = data.get('name')
    product_image = data.get('image')
    product_price = data.get('price')
    product_quantity = data.get('quantity')  

    if not product_id or not product_name or not product_price:
        return jsonify({'success': False, 'error': 'Dati mancanti per aggiungere il prodotto'}), 400

    # Recupera o crea il carrello nella sessione
    cart = session.get('cart', [])

    # Controlla se il prodotto esiste già nel carrello
    found = False
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += product_quantity
            found = True
            break

    # Se non trovato, aggiungi il prodotto come nuovo
    if not found:
        cart.append({
            'id': product_id,
            'name': product_name,
            'image': product_image,
            'price': product_price,
            'quantity': product_quantity,
        })

    # Logga il contenuto della sessione
    print("Contenuto della sessione:", session)

    # Salva il carrello aggiornato nella sessione
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart})

@cart_bp.route('/cart_contents', methods=['GET'])
def cart_contents():
    """Restituisce il contenuto del carrello."""
    cart = session.get('cart', [])
    return jsonify({'cart': cart})

@cart_bp.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    """Rimuove un prodotto dal carrello."""
    data = request.get_json()
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'success': False, 'error': 'Product ID non fornito'}), 400

    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart})