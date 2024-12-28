
# Importa i blueprint definiti nei vari file
from .checkout_routes import checkout_bp
from .cart_routes import cart_bp



# Funzione per registrare tutti i blueprint della sezione admin

def register_user_blueprints(app):
    """
    Registra tutti i blueprint della sezione user nell'app Flask.
    """
    app.register_blueprint(checkout_bp)
    app.register_blueprint(cart_bp)