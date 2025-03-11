
# Importa i blueprint definiti nei vari file
from .customers_api import customersapi_bp
from .orders_api import ordersapi_bp
from .products_api import productsapi_bp
from .brand_api import brands_bp
from .collections_api import collections_bp



# Funzione per registrare tutti i blueprint della sezione admin
def register_api_blueprints(app):
    """
    Registra tutti i blueprint della sezione API nell'app Flask.
    """
    app.register_blueprint(customersapi_bp)
    app.register_blueprint(ordersapi_bp)
    app.register_blueprint(productsapi_bp)
    app.register_blueprint(brands_bp)
    app.register_blueprint(collections_bp)