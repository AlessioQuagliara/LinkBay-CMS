from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for, flash
from public.pdf_printer import generate_order_pdf, generate_invoice_pdf
from models.database import db
from models.orders import Order, OrderItem
from models.products import Product
from models.customers import Customer
from models.payments import Payment
from models.shipping import Shipping
from datetime import datetime
from functools import wraps
from helpers import check_user_authentication
import logging

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione degli ordini
orders_bp = Blueprint('orders', __name__)
