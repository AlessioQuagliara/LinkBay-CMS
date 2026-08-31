from datetime import datetime, timezone

from app.extensions import db


class MonitoredSite(db.Model):
    """Un sito Search Console che un utente ha scelto di monitorare.

    Sostituisce il precedente `GscConnection.monitored_site_url` (singolare):
    un utente può ora avere più siti attivi in monitoraggio. L'OAuth resta
    1:1 su `GscConnection` (un solo login Google per utente) — questa tabella
    aggiunge solo la relazione 1:N sui siti scelti da quell'account.

    Le tabelle a valle (GscSiteDaily, GscPageMonthly, PageAlert,
    AiAnalyzerConfig, ...) chiavano già su stringhe (user_id, site_url), non
    su una FK verso questa tabella: rimuovere/riaggiungere un sito qui non
    tocca lo storico già raccolto.
    """

    __tablename__ = "monitored_sites"
    __table_args__ = (
        db.UniqueConstraint("user_id", "site_url", name="uq_monitored_site_user_url"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    site_url = db.Column(db.String(500), nullable=False)

    # Disattiva-non-cancella: "rimuovere" un sito lo disattiva soltanto, così
    # lo storico resta intatto e riaggiungerlo più tardi non crea un duplicato
    # (viola l'unique su user_id+site_url) ma riattiva la riga esistente.
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    added_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    deactivated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Ultimo sync GSC riuscito per questo sito — usato in Fase 2 per decidere
    # se i dati mostrati in Insights sono abbastanza freschi o vanno
    # rinfrescati in coda, secondo il refresh_interval del piano dell'utente.
    last_synced_at = db.Column(db.DateTime(timezone=True), nullable=True)

    user = db.relationship("User", backref=db.backref("monitored_sites", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<MonitoredSite user_id={self.user_id} site_url={self.site_url!r} active={self.is_active}>"
