from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models.database import db
from models.customers import Customer  # Importa il modello SQLAlchemy
from helpers import check_user_authentication
import uuid
import logging

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione dei clienti
customers_bp = Blueprint('customers', __name__)
