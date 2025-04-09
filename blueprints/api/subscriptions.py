from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from models.database import db  # Importa il database SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import datetime
from models.subscription import Subscription
from models.user import User  # Importa il modello della tabella
import logging

logging.basicConfig(level=logging.INFO)

# 📌 Blueprint per la gestione dei metodi di spedizione
subscriptions_bp = Blueprint('subscriptionsApi', __name__)

@subscriptions_bp.route('/get-subscription-status', methods=['GET'])
def get_subscription_status():
    try:
        # Controllo autenticazione e recupero user_id e shop_name dalla sessione
        user_id = session.get("user_id")
        shop_name = session.get("shop_name")
        if not user_id or not shop_name:
            return jsonify({"success": False, "error": "Missing user or shop context"}), 401

        # Recupera la sottoscrizione attiva
        subscription = Subscription.query.filter_by(user_id=user_id, shop_name=shop_name).first()
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
            "status": status,
            "price": subscription.price,
            "currency": subscription.currency,
            "limits": subscription.limits,
            "features": subscription.features,
            "payment_gateway": subscription.payment_gateway
        }), 200

    except Exception as e:
        logging.error(f"Error in get_subscription_status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500