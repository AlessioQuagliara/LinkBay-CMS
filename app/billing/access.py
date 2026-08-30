"""Gate di accesso centralizzato: un solo before_request per tutta l'app,
invece di un decoratore su ogni singola route. Blocca chi ha finito il trial
di 14 giorni e non ha un abbonamento Stripe attivo (vedi User.has_active_access
in app/models/user.py), reindirizzandolo alla pagina di upgrade."""
from flask import redirect, request, url_for
from flask_login import current_user

# Blueprint che richiedono un accesso pagante. Tutto il resto (main, auth,
# billing, Flask-Admin, static) resta raggiungibile anche a trial scaduto.
GATED_BLUEPRINTS = {"dashboard", "gsc", "ai", "alerts"}


def init_access_gate(app):
    @app.before_request
    def enforce_subscription_access():
        if not current_user.is_authenticated or current_user.is_admin:
            return None
        if request.blueprint not in GATED_BLUEPRINTS:
            return None
        if current_user.has_active_access:
            return None
        return redirect(url_for("billing.upgrade"))
