"""Gestione errori centralizzata.

Un solo handler cattura TUTTI gli HTTPException (404, 403, 405, 500, …): non
serve una funzione per codice. Renderizza sempre lo stesso template
`errors/error.html`, passando codice/nome/messaggio, così la pagina cambia in
base all'errore ma la logica resta una sola.
"""
from werkzeug.exceptions import HTTPException

from flask import render_template
from flask_babel import lazy_gettext as _l

# Messaggi più umani per i casi comuni; per tutto il resto si usa la
# descrizione standard di Werkzeug. lazy_gettext perché il dict è valutato a
# import-time, prima che la lingua della richiesta sia nota.
FRIENDLY = {
    400: _l("The request couldn't be understood. Check the address and try again."),
    401: _l("You need to sign in to view this page."),
    403: _l("You don't have access to this page."),
    404: _l("The page you're looking for doesn't exist or has moved."),
    405: _l("That action isn't allowed on this page."),
    429: _l("Too many requests. Please slow down and try again shortly."),
    500: _l("Something went wrong on our side. We've been notified — please try again."),
    502: _l("An upstream service didn't respond. Please try again in a moment."),
    503: _l("The service is temporarily unavailable. Please try again shortly."),
}


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        code = e.code or 500
        if code >= 500:
            app.logger.error("HTTP %s at %s", code, getattr(e, "description", ""))
        message = FRIENDLY.get(code, e.description)
        return render_template("errors/error.html", code=code, name=e.name, message=message), code
