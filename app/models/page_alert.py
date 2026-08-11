from datetime import datetime, timezone

from app.extensions import db


class PageAlert(db.Model):
    """Una pagina in "vera discesa" prodotta dal rule engine (app/rules/), con il
    suo punteggio di priorità e la spiegazione in italiano già pronta per la
    lista utente. È l'output persistito del job settimanale.

    Una riga per (utente, sito, pagina, finestra): `window_end` è l'ultimo mese
    chiuso considerato in quel run. L'ingest è idempotente sullo stesso
    window_end (vincolo unique): rilanciare il job aggiorna la riga, non la
    duplica. Gli alert di finestre precedenti restano come storico — non si
    buttano mai (BUSINESS_PLAN.md §13).
    """

    __tablename__ = "page_alerts"
    __table_args__ = (
        db.UniqueConstraint("user_id", "site_url", "url", "window_end", name="uq_page_alert"),
        # Query principale della schermata unica: "alert di questo sito, ultimo
        # periodo, ordinati per priorità" (ARCHITECTURE.md §6, indici indispensabili).
        db.Index("ix_page_alerts_site_window_priority", "site_url", "window_end", "priority_score"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    site_url = db.Column(db.String(500), nullable=False, index=True)
    url = db.Column(db.String(2048), nullable=False, index=True)
    window_end = db.Column(db.Date, nullable=False)  # ultimo mese chiuso considerato

    best_month_clicks = db.Column(db.Integer, nullable=True)
    click_loss_abs = db.Column(db.Integer, nullable=True)
    click_loss_pct = db.Column(db.Float, nullable=True)
    position_before = db.Column(db.Float, nullable=True)
    position_after = db.Column(db.Float, nullable=True)
    impressions_trend_pct = db.Column(db.Float, nullable=True)
    site_relative_drop_pct = db.Column(db.Float, nullable=True)
    yoy_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    priority_score = db.Column(db.Float, nullable=True, index=True)
    reason_text = db.Column(db.Text, nullable=True)

    # new -> acknowledged -> done -> recovered. Per ora solo il campo: la UI per
    # cambiarlo arriva nel Prompt 5 (vedi ciclo di vita in ARCHITECTURE.md §11).
    status = db.Column(db.String(20), nullable=False, default="new")

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<PageAlert {self.site_url} {self.url} {self.window_end} prio={self.priority_score}>"
