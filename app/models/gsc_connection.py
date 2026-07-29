from datetime import datetime, timezone

from app.extensions import db


class GscConnection(db.Model):
    """Collega un User al suo account Google Search Console (OAuth2).

    Un solo collegamento per utente (relazione 1:1). access_token e
    refresh_token sono cifrati con Fernet prima di essere salvati — vedi
    app/gsc/crypto.py — non sono mai leggibili in chiaro dal DB da soli.
    """

    __tablename__ = "gsc_connections"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    user = db.relationship("User", back_populates="gsc_connection")

    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    token_uri = db.Column(db.String(255), nullable=False)
    scopes = db.Column(db.String(500), nullable=False)
    expiry = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<GscConnection user_id={self.user_id}>"
