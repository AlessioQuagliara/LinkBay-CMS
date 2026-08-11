import os

from app import _ensure_tables, create_app

app = create_app()

if __name__ == "__main__":
    # Dev server (processo singolo): creiamo le tabelle mancanti qui, dato che
    # create_app() non lo fa più. In prod ci pensa l'hook on_starting di
    # gunicorn.conf.py, una volta sola nel master.
    _ensure_tables(app)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)), debug=True)
