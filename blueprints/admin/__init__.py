
# Importa i blueprint definiti nei vari file
from .categories_routes import categories_bp
from .cmsaddon_routes import cmsaddon_bp
from .collections_routes import collections_bp
from .products_routes import products_bp
from .page_routes import page_bp
from .websettings_routes import websettings_bp
from .user_routes import user_bp
from .orders_routes import orders_bp
from .payments_routes import payments_bp
from .shipping_routes import shipping_bp
from .shippingmethods_routes import shipping_methods_bp
from .storepayments_routes import storepayments_bp
from .userstoreaccess_routes import userstoreaccess_bp
from .shoplist_routes import shoplist_bp
from .database_routes import database_bp
from .customers_routes import customers_bp





# Funzione per registrare tutti i blueprint della sezione admin
def register_admin_blueprints(app):
    """
    Registra tutti i blueprint della sezione admin nell'app Flask.
    """
    app.register_blueprint(categories_bp)
    app.register_blueprint(cmsaddon_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(page_bp)
    app.register_blueprint(websettings_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(shipping_bp)
    app.register_blueprint(shipping_methods_bp)
    app.register_blueprint(storepayments_bp)
    app.register_blueprint(userstoreaccess_bp)
    app.register_blueprint(shoplist_bp)
    app.register_blueprint(database_bp)
    app.register_blueprint(customers_bp)
