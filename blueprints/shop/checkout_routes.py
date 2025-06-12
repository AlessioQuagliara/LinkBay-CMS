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
