from datetime import datetime, timezone

from app.extensions import db


class ResourceUsageLog(db.Model):
    """Log di ogni azione che consuma risorse a pagamento: scan GSC, run AI,
    export. Base sia per l'enforcement dei limiti mensili (export/mese,
    "heavy user" tagging) sia per l'audit trail richiesto ("cosa ha fatto
    l'utente X e quando"). Tabella nuova — non esisteva nessun log di audit
    equivalente prima di questa fase (verificato via grep sull'intero repo).
    """

    __tablename__ = "resource_usage_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    site_url = db.Column(db.String(500), nullable=True)

    # "gsc_scan" | "ai_analysis" | "export_csv" | "export_pdf" | "site_added"
    action = db.Column(db.String(30), nullable=False)

    # Se False, l'azione è stata registrata ma non contava ai fini di un
    # limite (es. retry interno, azione admin) — tenuto per completezza
    # dell'audit senza sporcare i conteggi di enforcement.
    counted_against_limit = db.Column(db.Boolean, nullable=False, default=True)

    credits_consumed = db.Column(db.Integer, nullable=True)
    meta = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    user = db.relationship("User")

    __table_args__ = (
        db.Index("ix_resource_usage_user_action_created", "user_id", "action", "created_at"),
    )

    def __repr__(self):
        return f"<ResourceUsageLog user_id={self.user_id} action={self.action!r}>"
