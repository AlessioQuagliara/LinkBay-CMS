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

        # 👉 GESTIONE DOMINIO ACQUISTATO (senza toccare le subscription)
        domain = metadata.get('domain')
        if domain:
            from models.user import User
            from models.shoplist import ShopList
            from models.domain import Domain
            from public.godaddy_api import GoDaddyAPI  # Adattato secondo struttura indicata

            try:
                user = User.query.get(user_id)
                shop = ShopList.query.filter_by(shop_name=shop_name).first()

                if not (user and shop and shop.user_id == user.id):
                    webhook_logger.warning(f"❌ Dati non validi per salvataggio dominio: user={user}, shop={shop}")
                else:
                    contact = {
                        "nameFirst": user.nome or "Utente",
                        "nameLast": user.cognome or "",
                        "email": user.email,
                        "phone": "+39.3333333333",
                        "addressMailing": {
                            "address1": "Via Generica 123",
                            "city": "Roma",
                            "state": "RM",
                            "postalCode": "00100",
                            "country": "IT"
                        }
                    }

                    api = GoDaddyAPI()
                    result = api.purchase_domain(domain, {
                        "domain": domain,
                        "consent": {
                            "agreementKeys": ["DNRA"],
                            "agreedBy": request.remote_addr or "127.0.0.1",
                            "agreedAt": datetime.utcnow().isoformat() + "Z"
                        },
                        "contactAdmin": contact,
                        "contactRegistrant": contact,
                        "contactTech": contact,
                        "contactBilling": contact
                    })

                    if "error" in result:
                        webhook_logger.error(f"❌ Errore durante l'acquisto dominio: {result['error']}")
                    else:
                        webhook_logger.info(f"📥 Salvataggio dominio nel database: {domain}")
                        new_domain = Domain(
                            shop_id=shop.id,
                            domain=domain,
                            dns_provider="GoDaddy",
                            status="active",
                            renewal_enabled=True,
                            renewal_date=datetime.utcnow() + timedelta(days=365)
                        )
                        db.session.add(new_domain)
                        db.session.commit()

                        # Aggiunta record DNS per puntare all'IP del server
                        try:
                            api.set_dns_records(domain, [
                                {
                                    "type": "A",
                                    "name": "@",
                                    "data": "103.240.147.13",
                                    "ttl": 600
                                }
                            ])
                            webhook_logger.info(f"🌍 DNS A record aggiunto per {domain} -> 103.240.147.13")
                        except Exception as dns_err:
                            webhook_logger.error(f"⚠️ Errore durante la configurazione DNS per {domain}: {dns_err}")

                        # 🔧 Esegui configurazione Nginx + Certbot per dominio acquistato
                        try:
                            import subprocess
                            subprocess.run(["python3", "/var/www/CMS_DEF/scripts/setup_custom_domain.py", domain], check=True)
                            webhook_logger.info(f"🛠️ Script setup_custom_domain.py eseguito per: {domain}")
                        except Exception as e:
                            webhook_logger.error(f"⚠️ Errore durante l'esecuzione dello script setup_custom_domain.py: {e}")

                        webhook_logger.info(f"✅ Dominio '{domain}' registrato nel database con shop_id={shop.id}")
            except Exception as e:
                db.session.rollback()
                webhook_logger.error(f"🔥 Errore durante gestione dominio via webhook: {e}")

    if event['type'] == 'checkout.session.completed':
        webhook_logger.info(f"✅ Webhook completato per session ID: {session.get('id')}")
    else:
        webhook_logger.info(f"✅ Webhook completato per evento: {event['type']}")
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
