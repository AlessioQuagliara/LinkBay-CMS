import stripe
from flask import current_app, jsonify

def create_connect_account(shop_name):
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']  # ✅ Spostato dentro la funzione

    account = stripe.Account.create(
        type="express",
        country="IT",
        capabilities={"transfers": {"requested": True}},
        business_type="individual"
    )

    account_link = stripe.AccountLink.create(
        account=account.id,
        refresh_url="https://linkbay-cms.com/dashboard/payments",
        return_url="https://linkbay-cms.com/dashboard/payments",
        type="account_onboarding"
    )

    return {
        "account_id": account.id,
        "onboarding_url": account_link.url
    }