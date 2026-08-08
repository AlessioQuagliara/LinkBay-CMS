from datetime import datetime, timezone

from app.extensions import db


class AiAnalyzerConfig(db.Model):
    """Stato dell'AI Analyzer per (utente, sito). L'analisi AI parte solo se
    `enabled` è True (switch in UI). `last_run_at` serve a rispettare la cadenza
    settimanale ed evitare chiamate DeepSeek inutili (costo)."""

    __tablename__ = "ai_analyzer_config"
    __table_args__ = (
        db.UniqueConstraint("user_id", "site_url", name="uq_ai_config"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    site_url = db.Column(db.String(500), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    last_run_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<AiAnalyzerConfig {self.site_url} enabled={self.enabled}>"


class AiPageAnalysis(db.Model):
    """Risultato AI per singola pagina: uno score 0-100 (usato dalla
    radial-progress) e fino a 5 suggerimenti concreti (mostrati nello stack).
    Una riga per (utente, sito, pagina), aggiornata a ogni run settimanale."""

    __tablename__ = "ai_page_analysis"
    __table_args__ = (
        db.UniqueConstraint("user_id", "site_url", "page_url", name="uq_ai_page"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    site_url = db.Column(db.String(500), nullable=False)
    page_url = db.Column(db.String(2048), nullable=False)

    score = db.Column(db.Integer, nullable=False, default=0)
    suggestions = db.Column(db.JSON, nullable=False, default=list)
    week_start = db.Column(db.Date, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<AiPageAnalysis {self.page_url} score={self.score}>"
