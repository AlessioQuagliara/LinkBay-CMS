"""Gate di accesso centralizzato: un solo before_request per tutta l'app,
invece di un decoratore su ogni singola route. Blocca chi ha finito il trial
di 13 giorni e non ha un piano Pro attivo (Paddle, Revolut manuale, o legacy
Lemon Squeezy — vedi app/entitlements/service.py::has_active_entitlement),
reindirizzandolo alla pagina di upgrade."""
from flask import redirect, request, url_for
from flask_limiter.util import get_remote_address
from flask_login import current_user

from app.extensions import limiter

# Blueprint che richiedono un accesso pagante. Tutto il resto (main, auth,
# billing, Flask-Admin, static) resta raggiungibile anche a trial scaduto.
# Sono anche i blueprint con rate limit per piano (vedi init_rate_limits):
# stessa superficie, stessa filosofia "solo le feature a pagamento".
GATED_BLUEPRINTS = {"dashboard", "gsc", "ai", "alerts", "exports", "audits"}


def init_access_gate(app):
    @app.before_request
    def enforce_subscription_access():
        if not current_user.is_authenticated or current_user.is_admin:
            return None
        if request.blueprint not in GATED_BLUEPRINTS:
            return None
        from app.entitlements.service import has_active_entitlement

        if has_active_entitlement(current_user):
            return None
        return redirect(url_for("billing.upgrade"))


# Limite conservativo per chi arriva senza sessione (nessun current_user —
# non dovrebbe succedere sui blueprint gated, protetti da @login_required,
# ma il rate limit va comunque a monte di quella verifica).
_ANONYMOUS_RATE = "30 per minute"
_ADMIN_RATE = "100000 per minute"  # di fatto illimitato: il team non ha un plan_type


def _rate_limit_key():
    if current_user.is_authenticated:
        return f"user:{current_user.id}"
    return get_remote_address()


def _rate_limit_value():
    if not current_user.is_authenticated:
        return _ANONYMOUS_RATE
    if current_user.is_admin:
        return _ADMIN_RATE
    from app.entitlements.service import get_plan_limits

    return f"{get_plan_limits(current_user).api_rate_per_min} per minute"


def init_rate_limits(blueprints):
    """Applica un rate limit per-utente (chiave: user id, non IP) e dinamico
    per piano (PlanLimits.api_rate_per_min) a ciascun blueprint gated. Va
    chiamato prima di app.register_blueprint(bp) — stesso ordine dell'idioma
    standard di Flask-Limiter per i limiti a livello di blueprint."""
    for bp in blueprints:
        limiter.limit(_rate_limit_value, key_func=_rate_limit_key)(bp)
