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
subscriptions_bp = Blueprint('subscriptionsApi', __name__, url_prefix='/api/')

@subscriptions_bp.route('/get-subscription-status', methods=['GET'])
def get_subscription_status():
    try:
        # Controllo autenticazione e recupero username
        username = check_user_authentication()
        if not username:
            return jsonify({"success": False, "error": "User not authenticated"}), 401

        # Recupera l'utente dal database
        user = User.query.filter_by(email=username).first()
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        # Recupera la sottoscrizione attiva
        subscription = Subscription.query.filter_by(user_id=user.id, status="active").first()
        if not subscription:
            return jsonify({"success": False, "error": "No active subscription found"}), 404

        # Determina lo stato dell'abbonamento
        now = datetime.datetime.utcnow()
        days_left = (subscription.renewal_date - now).days
        status = "active"

        if days_left <= 5:
            status = "expiring"
        elif subscription.status == "canceled":
            status = "canceled"

        return jsonify({
            "success": True,
            "plan_name": subscription.plan_name,
            "renewal_date": subscription.renewal_date.strftime("%Y-%m-%d"),
            "status": status
        }), 200

    except Exception as e:
        logging.error(f"Error in get_subscription_status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500