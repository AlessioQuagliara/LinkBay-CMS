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

    # Quando l'app è servita in HTTPS (produzione dietro Traefik) rendiamo i
    # cookie di sessione sicuri e coerenti con lo schema. SameSite=Lax è
    # necessario: il callback OAuth di Google è una navigazione GET top-level e
    # con Lax il cookie di stato viene comunque inviato al ritorno.
    _IS_HTTPS = APP_BASE_URL.startswith("https://")
    PREFERRED_URL_SCHEME = "https" if _IS_HTTPS else "http"
    SESSION_COOKIE_SECURE = _IS_HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

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

    # DeepSeek — AI Analyzer (endpoint OpenAI-compatibile). Se la chiave manca,
    # lo switch AI resta disattivabile ma l'analisi risponde "non configurata".
    DEEPSEEK_API = os.environ.get("DEEPSEEK_API")
    DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
