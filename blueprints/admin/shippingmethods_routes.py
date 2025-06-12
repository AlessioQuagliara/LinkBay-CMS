from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.database import db  # Importa il database SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from models.shippingmethods import ShippingMethod  # Importa il modello della tabella
from helpers import check_user_authentication
import logging

logging.basicConfig(level=logging.INFO)

# 📌 Blueprint per la gestione dei metodi di spedizione
shipping_methods_bp = Blueprint('shipping_methods' , __name__)
