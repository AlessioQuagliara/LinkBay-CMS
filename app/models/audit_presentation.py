from datetime import datetime, timezone

from app.extensions import db


class AuditPresentation(db.Model):
    """Presentazione reveal.js delle criticità di un sito, generata dall'AI a
    partire dai dati già raccolti (page_alerts) e salvata come artefatto
    datato. Il markdown è la fonte di verità: la vista/il download la
    renderizzano al volo in HTML reveal.js (app/audits/render.py), non c'è
    nessun HTML pre-renderizzato da tenere in sync."""

    __tablename__ = "audit_presentations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    site_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    markdown = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    user = db.relationship("User")

    def __repr__(self):
        return f"<AuditPresentation {self.site_url} {self.created_at}>"
