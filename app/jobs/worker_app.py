"""App Flask minima per i processi worker RQ.

Stesso motivo di app/__init__.py::init_db_schema(): un job gira in un
processo separato da "web" (il worker RQ, avviato con `rq worker`, mai
attraverso create_app()) e deve costruirsi da solo un app-context per usare
current_app.config/db.session — ma senza registrare Flask-Admin/blueprint,
che non servono a un job e complicherebbero inutilmente l'import. Un solo
processo worker esegue molti job in sequenza: l'app va creata una volta sola
per processo, non ad ogni job (da cui la cache a livello di modulo).
"""
from flask import Flask

from config import Config

_worker_app: Flask | None = None


def get_worker_app() -> Flask:
    global _worker_app
    if _worker_app is None:
        import app.models  # noqa: F401 — popola db.metadata prima di init_app
        from app.extensions import db

        application = Flask("worker")
        application.config.from_object(Config)
        db.init_app(application)
        _worker_app = application
    return _worker_app
