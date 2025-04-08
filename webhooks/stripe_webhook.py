from flask import Blueprint, request, jsonify
import stripe
from models.cmsaddon import purchase_addon
from models.database import db
import logging

stripe_webhook_bp = Blueprint('stripe_webhook', __name__)
endpoint_secret = "whsec_..."  # Prendi dal tuo dashboard Stripe

@stripe_webhook_bp.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except stripe.error.SignatureVerificationError as e:
        logging.warning("⚠️ Webhook signature verification failed.")
        return jsonify(success=False), 400

    # 💳 Quando il pagamento è confermato
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        
        shop_name = metadata.get("shop_name")
        addon_id = int(metadata.get("addon_id"))
        addon_type = metadata.get("addon_type")

        # Acquisto effettivo dell'addon
        if shop_name and addon_id and addon_type:
            success = purchase_addon(shop_name, addon_id, addon_type)
            if success:
                logging.info(f"✅ Acquisto completato per {shop_name} - addon {addon_id}")
            else:
                logging.warning(f"❌ Acquisto fallito per {shop_name} - addon {addon_id}")
        else:
            logging.warning("❌ Dati metadata mancanti nel webhook")

    return jsonify(success=True)