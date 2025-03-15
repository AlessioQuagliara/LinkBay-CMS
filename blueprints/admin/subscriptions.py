from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.database import db  # Importa il database SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import datetime
from models.subscription import Subscription
from models.user import User  # Importa il modello della tabella
from helpers import check_user_authentication
import logging

logging.basicConfig(level=logging.INFO)

# 📌 Blueprint per la gestione dei metodi di spedizione
subscriptions_bp = Blueprint('subscription' , __name__)