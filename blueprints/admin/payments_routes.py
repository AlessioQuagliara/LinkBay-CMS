from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models.database import db
from models.payments import Payment
from models.payment_methods import PaymentMethod
from helpers import check_user_authentication
import logging
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO)

payments_bp = Blueprint('payments', __name__)
