from .error_handlers import errors_bp

def register_error_handlers(app):
    app.register_blueprint(errors_bp)