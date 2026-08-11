"""Rule engine del prodotto: decide quali pagine sono in "vera discesa" e con
quale priorità.

Vincolo deliberato (ARCHITECTURE.md §4): questo package non importa nulla di
Flask né di SQLAlchemy. Riceve dataclass, restituisce dataclass. È l'unico modo
per testarlo sul serio e per tarare le soglie senza avviare l'applicazione.
"""
