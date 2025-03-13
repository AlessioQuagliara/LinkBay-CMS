from flask import Blueprint, request, jsonify, render_template, url_for, flash, redirect
from models.database import db  # Importa il database SQLAlchemy
from models.storepayment import StorePayment  # Modello per i pagamenti
from config import Config
import stripe
from helpers import check_user_authentication
import logging

logging.basicConfig(level=logging.INFO)

# 📌 Blueprint per la gestione dei pagamenti
storepayments_bp = Blueprint('storepayments' , __name__)

# 📌 Configurazione Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY = Config.STRIPE_PUBLISHABLE_KEY


# 🔹 **Pagina di gestione dell'abbonamento**
@storepayments_bp.route('/admin/cms/pages/subscription')
def subscription():
    """
    Visualizza la pagina delle sottoscrizioni per il negozio.
    """
    username = check_user_authentication()

    if not username:  # ✅ Se la sessione è scaduta, reindirizza alla login
        flash("Sessione scaduta. Effettua nuovamente il login.", "warning")
        return redirect(url_for('user.login'))

    if not STRIPE_PUBLISHABLE_KEY:
        logging.warning("⚠️ Stripe Publishable Key non configurata correttamente.")
        flash("Si è verificato un problema con la configurazione del pagamento. Contatta il supporto.", "danger")
        return redirect(url_for('admin.dashboard'))  # ✅ Redirect a una pagina sicura

    return render_template(
        'admin/cms/pages/subscription.html',
        title='Subscription',
        username=username,
        stripe_publishable_key=STRIPE_PUBLISHABLE_KEY
    )


# 🔹 **Creazione della sessione di checkout Stripe**
@storepayments_bp.route('/subscription/checkout', methods=['POST'])
def create_checkout_session():
    data = request.get_json()
    plan_id = data.get('plan_id')

    logging.info(f"📌 Received plan_id: {plan_id}")  # Log per il debug

    if not plan_id:
        return jsonify({'error': 'Invalid plan ID'}), 400

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('storepayments.subscription_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('storepayments.subscription_cancel', _external=True),
        )

        logging.info(f"✅ Checkout session created: {session.id}")
        return jsonify({'sessionId': session.id})

    except Exception as e:
        logging.error(f"❌ Error creating checkout session: {str(e)}")
        return jsonify({'error': str(e)}), 500


# 🔹 **Pagina di successo dell'abbonamento**
@storepayments_bp.route('/subscription/success')
def subscription_success():
    session_id = request.args.get('session_id')

    if not session_id:
        return render_template('admin/cms/pages/sub_success.html', title="Subscription Successful")

    try:
        # Recupera i dettagli della sessione di pagamento
        session = stripe.checkout.Session.retrieve(session_id)
        customer_id = session.customer
        subscription_id = session.subscription
        shop_name = request.host.split('.')[0]

        logging.info(f"✅ Subscription successful! Customer ID: {customer_id}, Subscription ID: {subscription_id}")

        # Verifica se l'abbonamento è già registrato
        existing_payment = StorePayment.query.filter_by(shop_name=shop_name, stripe_subscription_id=subscription_id).first()

        if not existing_payment:
            # Salva i dettagli nel database
            new_payment = StorePayment(
                shop_name=shop_name,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id,
                status="active"
            )

            db.session.add(new_payment)
            db.session.commit()
            logging.info("✅ Payment record saved successfully!")

        return render_template('admin/cms/pages/sub_success.html', title="Subscription Successful")

    except stripe.error.StripeError as e:
        logging.error(f"❌ Stripe error: {str(e)}")
        return render_template('admin/cms/pages/sub_success.html', title="Subscription Successful, but an error occurred"), 500
    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}")
        return render_template('admin/cms/pages/sub_success.html', title="Subscription Successful, but an error occurred"), 500


# 🔹 **Pagina di annullamento dell'abbonamento**
@storepayments_bp.route('/subscription/cancel')
def subscription_cancel():
    return render_template('admin/cms/pages/sub_cancel.html', title="Subscription Canceled")