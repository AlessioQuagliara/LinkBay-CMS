from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from models.storepayment import StorePayment  # importo la classe database
from db_helpers import DatabaseHelper
db_helper = DatabaseHelper()
from config import Config
import stripe
from db_helpers import DatabaseHelper
from helpers import check_user_authentication

# Blueprint
storepayments_bp = Blueprint('storepayments', __name__)

# STRIPE 

stripe.api_key = Config.STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY = Config.STRIPE_PUBLISHABLE_KEY

# Rotte per la gestione

@storepayments_bp.route('/admin/cms/pages/subscription')
def subscription():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template(
            'admin/cms/pages/subscription.html', 
            title='Subscription', 
            username=username, 
            stripe_publishable_key=STRIPE_PUBLISHABLE_KEY
        )
    return username

@storepayments_bp.route('/subscription/checkout', methods=['POST'])
def create_checkout_session():
    data = request.get_json()
    plan_id = data.get('plan_id')  

    if not plan_id:
        return jsonify(error="Invalid plan ID"), 400

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan_id, 
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('subscription_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('subscription_cancel', _external=True),
        )
        
        return jsonify({'sessionId': session.id})
    
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return jsonify(error=str(e)), 500
    
@storepayments_bp.route('/subscription/success')
def subscription_success():
    return render_template('admin/cms/pages/sub_success.html', title="Subscription Successful")

@storepayments_bp.route('/subscription/cancel')
def subscription_cancel():
    return render_template('admin/cms/pages/sub_cancel.html', title="Subscription Canceled")