from app.extensions import db


class GscPageMonthly(db.Model):
    """Metriche mensili per singola pagina, salvate dallo storico Search
    Console. È la base per il trend a più mesi di ogni pagina e per il rule
    engine che individua le pagine in calo, e conserva lo storico oltre i ~16
    mesi che GSC mette a disposizione.

    Una riga per (utente, sito, pagina, mese) — `month` è sempre il primo
    giorno del mese. L'ingest è idempotente: rifare il sync di un mese già
    presente lo aggiorna, non lo duplica (vincolo unique). Si interroga un mese
    per volta con dimensions=["page"] (vedi ARCHITECTURE.md §6-7), non per
    giorno, per non far esplodere numero di righe e consumo di RAM.
    """

    __tablename__ = "gsc_page_monthly"
    __table_args__ = (
        db.UniqueConstraint("user_id", "site_url", "page_url", "month", name="uq_page_monthly"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    site_url = db.Column(db.String(500), nullable=False, index=True)
    page_url = db.Column(db.String(2048), nullable=False, index=True)
    month = db.Column(db.Date, nullable=False, index=True)  # sempre il primo giorno del mese

    clicks = db.Column(db.Integer, nullable=False, default=0)
    impressions = db.Column(db.Integer, nullable=False, default=0)
    ctr = db.Column(db.Float, nullable=False, default=0.0)
    position = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f"<GscPageMonthly {self.site_url} {self.page_url} {self.month} clicks={self.clicks}>"
