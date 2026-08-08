from app.extensions import db


class GscSiteDaily(db.Model):
    """Metriche giornaliere a livello di sito, salvate dallo storico Search
    Console. Serve a due cose: disegnare l'andamento nel tempo e calcolare i
    totali/delta di un periodo in modo preciso e ripetibile (senza rifare la
    query live ogni volta), e a conservare lo storico oltre i 16 mesi di GSC.

    Una riga per (utente, sito, giorno). L'ingest è idempotente: rifare il sync
    di un giorno già presente lo aggiorna, non lo duplica (vincolo unique).
    """

    __tablename__ = "gsc_site_daily"
    __table_args__ = (
        db.UniqueConstraint("user_id", "site_url", "date", name="uq_site_daily"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    site_url = db.Column(db.String(500), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)

    clicks = db.Column(db.Integer, nullable=False, default=0)
    impressions = db.Column(db.Integer, nullable=False, default=0)
    ctr = db.Column(db.Float, nullable=False, default=0.0)
    position = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f"<GscSiteDaily {self.site_url} {self.date} clicks={self.clicks}>"
