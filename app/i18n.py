"""Selezione della lingua (EN/IT). Un solo punto di verità per capire quale
locale usare in ogni richiesta, usato da Babel per scegliere le traduzioni.

Priorità: preferenza salvata sull'utente loggato (Settings) > lingua scelta
in sessione (switcher per visitatori anonimi) > Accept-Language del browser >
inglese di default."""
from flask import request, session
from flask_login import current_user

SUPPORTED_LOCALES = ["en", "it"]
DEFAULT_LOCALE = "en"


def get_locale():
    if current_user.is_authenticated and current_user.locale in SUPPORTED_LOCALES:
        return current_user.locale
    if session.get("locale") in SUPPORTED_LOCALES:
        return session["locale"]
    return request.accept_languages.best_match(SUPPORTED_LOCALES) or DEFAULT_LOCALE


def init_babel(app):
    from app.extensions import babel

    babel.init_app(app, locale_selector=get_locale)

    @app.context_processor
    def inject_locale():
        return {"get_locale": get_locale, "supported_locales": SUPPORTED_LOCALES}
