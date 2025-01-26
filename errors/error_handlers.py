from flask import Blueprint, render_template

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def handle_404_error(e):
    """
    Gestione errore 404 - Pagina non trovata.
    """
    return render_template('errors/404.html', title="Error 404"), 404

@errors_bp.app_errorhandler(500)
def handle_500_error(e):
    """
    Gestione errore 500 - Errore interno del server.
    """
    return render_template('errors/500.html', title="Error 500"), 500

@errors_bp.app_errorhandler(403)
def handle_403_error(e):
    """
    Gestione errore 403 - Accesso negato.
    """
    return render_template('errors/error.html', title="Error 403", message="Access Denied."), 403