"""Gestione errori centralizzata.

Un solo handler cattura TUTTI gli HTTPException (404, 403, 405, 500, …): non
serve una funzione per codice. Renderizza sempre lo stesso template
`errors/error.html`, passando codice/nome/messaggio, così la pagina cambia in
base all'errore ma la logica resta una sola.
"""
from werkzeug.exceptions import HTTPException

from flask import render_template

# Messaggi più umani per i casi comuni; per tutto il resto si usa la
# descrizione standard di Werkzeug.
FRIENDLY = {
    400: "The request couldn't be understood. Check the address and try again.",
    401: "You need to sign in to view this page.",
    403: "You don't have access to this page.",
    404: "The page you're looking for doesn't exist or has moved.",
    405: "That action isn't allowed on this page.",
    429: "Too many requests. Please slow down and try again shortly.",
    500: "Something went wrong on our side. We've been notified — please try again.",
    502: "An upstream service didn't respond. Please try again in a moment.",
    503: "The service is temporarily unavailable. Please try again shortly.",
}


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        code = e.code or 500
        if code >= 500:
            app.logger.error("HTTP %s at %s", code, getattr(e, "description", ""))
        message = FRIENDLY.get(code, e.description)
        return render_template("errors/error.html", code=code, name=e.name, message=message), code
