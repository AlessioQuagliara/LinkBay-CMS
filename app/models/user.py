from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model, UserMixin):
    """Un cliente che si registra dalla landing e usa il software.
    Tutto lo storico dell'app va agganciato a questo modello (via user_id)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Non è RBAC: un solo flag per distinguere il team (accesso a Flask-Admin)
    # dai clienti normali. Si imposta con `python3 -m flask make-admin <email>`.
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    gsc_connection = db.relationship(
        "GscConnection", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
