
# Importa i blueprint definiti nei vari file
from .cmsaddon_routes import cmsaddon_bp
from .products_routes import products_bp
from .page_routes import page_bp
from .websettings_routes import websettings_bp
from .user_routes import user_bp
from .orders_routes import orders_bp
from .payments_routes import payments_bp
from .shippingmethods_routes import shipping_methods_bp
from .customers_routes import customers_bp
from .ui_routes import ui_bp
from .cookiepolicy_routes import cookiepolicy_bp
from .domain_routes import domain_bp
from .ai_routes import ai_bp
from .analytics_routes import analytics_bp



# Funzione per registrare tutti i blueprint della sezione admin
def register_admin_blueprints(app):
    """
    Registra tutti i blueprint della sezione admin nell'app Flask.
    """
    app.register_blueprint(cmsaddon_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(page_bp)
    app.register_blueprint(websettings_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(shipping_methods_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(ui_bp)
    app.register_blueprint(cookiepolicy_bp)
    app.register_blueprint(domain_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(analytics_bp)