
# Importa i blueprint definiti nei vari file
from .subscriptions import subscriptions_bp
from .navbar_api import navbar_bp
from .landing_api import landing_api
from .product_api import product_api



# Funzione per registrare tutti i blueprint della sezione admin
def register_api_blueprints(app):
    """
    Registra tutti i blueprint della sezione API nell'app Flask.
    """
    app.register_blueprint(subscriptions_bp, url_prefix='/api')
    app.register_blueprint(navbar_bp)
    app.register_blueprint(landing_api)
    app.register_blueprint(product_api)