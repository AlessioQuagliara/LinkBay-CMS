from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect
from models.payments import Payments  # importo la classe database
from app import get_db_connection, check_user_authentication  # connessione al database

# Blueprint
checkout_bp = Blueprint('checkout', __name__)

# Rotte per la gestione

@checkout_bp.route('/checkout')
def checkout():
    return render_template('checkout/checkout.html', title='Checkout')
