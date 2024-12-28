from flask import Blueprint, render_template
from models.payments import Payments  # importo la classe database

# Blueprint
checkout_bp = Blueprint('checkout', __name__)

# Rotte per la gestione

@checkout_bp.route('/checkout')
def checkout():
    return render_template('checkout/checkout.html', title='Checkout')
