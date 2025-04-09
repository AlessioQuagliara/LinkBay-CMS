import stripe
from flask import Blueprint, request, current_app
from models.database import db
from models import StorePayment, ShopAddon
from models.subscription import Subscription
from datetime import datetime, timedelta
import logging
import os

# Crea cartella log se non esiste
os.makedirs("logs", exist_ok=True)

# Configura il logger per il webhook Stripe
webhook_logger = logging.getLogger('stripe_webhook')
webhook_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/webhook_stripe.log')
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)
webhook_logger.addHandler(file_handler)

stripe_webhook_bp = Blueprint('stripe_webhook_bp', __name__)

@stripe_webhook_bp.route('/webhook/stripe', methods=['POST'])
def handle_stripe_webhook():
    ...
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config['STRIPE_WEBHOOK_SECRET']

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        current_app.logger.error(f"❌ Errore nella verifica del webhook Stripe: {e}")
        return 'Webhook Error', 400

    webhook_logger.info(f"📦 Ricevuto evento Stripe: {event['type']}")
    webhook_logger.info(f"📨 Payload ricevuto: {event}")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        
        webhook_logger.info(f"📋 Metadata presenti nella sessione: {metadata}")

        user_id = int(metadata.get('user_id', 0))
        shop_name = metadata.get('shop_name')
        plan_name = metadata.get('plan_name')

        webhook_logger.info(f"🧠 Metadata ricevuti: user_id={user_id}, shop_name={shop_name}, plan_name={plan_name}")

        try:
            subscription = Subscription.query.filter_by(shop_name=shop_name, user_id=user_id).first()
            if not subscription:
                current_app.logger.warning(f"❌ Nessuna subscription trovata con shop_name={shop_name} e user_id={user_id}")
            else:
                plan_map = {
                    "allisready": {
                        "label": "AllIsReady",
                        "price": 18,
                        "features": '{"max_products":600}',
                        "limits": '{"max_visits":999999}'
                    },
                    "professionaldesk": {
                        "label": "ProfessionalDesk",
                        "price": 36,
                        "features": '{"max_products":"unlimited"}',
                        "limits": '{"max_visits":"unlimited"}'
                    }
                }

                plan_data = plan_map.get(plan_name.lower())
                if not plan_data:
                    current_app.logger.warning(f"⚠️ Piano non riconosciuto: {plan_name}")
                else:
                    webhook_logger.info(f"🔁 Dati aggiornamento -> Piano: {plan_data['label']}, Prezzo: {plan_data['price']}, Shop: {shop_name}, User: {user_id}")
                    subscription.plan_name = plan_data["label"]
                    subscription.price = plan_data["price"]
                    subscription.features = plan_data["features"]
                    subscription.limits = plan_data["limits"]
                    subscription.status = 'active'
                    subscription.payment_gateway = 'stripe'
                    subscription.payment_reference = session['id']
                    subscription.renewal_date = datetime.utcnow() + timedelta(days=30)
                    db.session.commit()
                    webhook_logger.info(f"✅ Abbonamento aggiornato a {plan_data['label']} per {shop_name}.")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"🔥 Errore durante l'aggiornamento dell'abbonamento: {e}")

    webhook_logger.info(f"✅ Webhook completato per session ID: {session.get('id')}")
    return '', 200

@stripe_webhook_bp.route('/webhook/debug/subscriptions', methods=['GET'])
def debug_subscriptions():
    subscriptions = Subscription.query.all()
    result = []
    for sub in subscriptions:
        result.append({
            "shop_name": sub.shop_name,
            "user_id": sub.user_id,
            "plan_name": sub.plan_name,
            "price": sub.price,
            "status": sub.status,
            "renewal_date": sub.renewal_date.strftime('%Y-%m-%d') if sub.renewal_date else None
        })
    return {"subscriptions": result}

