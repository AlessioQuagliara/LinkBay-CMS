"""Config gunicorn per la produzione (usata da Dockerfile: `gunicorn -c gunicorn.conf.py run:app`).

I flag rispecchiano quelli che prima erano nel CMD del Dockerfile.

Perché questo file esiste: le tabelle mancanti vanno create UNA sola volta, nel
processo master PRIMA del fork dei worker (hook `on_starting`). Quando invece
ogni worker chiamava `db.create_all()` all'avvio (era in create_app), i 3 worker
correvano a creare le stesse tabelle e Postgres crashava con una UniqueViolation
su `pg_type_typname_nsp_index` — il boot falliva e gunicorn si riavviava. Farlo
una volta sola nel master elimina la race alla radice.
"""

bind = "0.0.0.0:3000"
workers = 3
# L'analisi AI fa una chiamata sincrona a DeepSeek che può superare i 30s di default.
timeout = 120
accesslog = "-"
errorlog = "-"


def on_starting(server):
    """Eseguito nel master, prima del fork dei worker: crea le tabelle mancanti
    una volta sola, così nessun worker tocca lo schema (niente race)."""
    from app import _ensure_tables, create_app
    from app.extensions import db

    app = create_app()
    _ensure_tables(app)
    # App usa e getta: chiudiamo il pool del master così i worker (che
    # reimportano run:app dopo il fork) partono con connessioni proprie.
    with app.app_context():
        db.engine.dispose()
