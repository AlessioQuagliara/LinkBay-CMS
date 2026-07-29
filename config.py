"""Configurazione dell'app, letta da variabili d'ambiente (.env)."""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://linkbay:linkbay@localhost:5432/linkbay_cms"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:3000")

    # Google Search Console (OAuth2) — vedi app/gsc/.
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    # Opzionale: se non impostata, viene derivata con url_for(..., _external=True).
    # Impostala esplicitamente dietro proxy/load balancer, dove schema/host
    # dedotti dalla request in arrivo non sono affidabili.
    GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")
    GSC_SCOPES = [
        s.strip() for s in os.environ.get(
            "GSC_SCOPES", "https://www.googleapis.com/auth/webmasters.readonly"
        ).split(",") if s.strip()
    ]

    # Chiave Fernet per cifrare access/refresh token in DB (obbligatoria per app/gsc).
    # Generane una con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    TOKEN_ENCRYPTION_KEY = os.environ.get("TOKEN_ENCRYPTION_KEY")
