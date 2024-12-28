from flask import render_template
from app import app, get_db_connection, get_auth_db_connection, check_user_authentication


# Gestione errore 404 - Pagina non trovata
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

# Gestione errore 500 - Errore del server
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# Gestione errore 403 - Accesso negato
@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

