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

    # Redis — broker della coda RQ (app/jobs/): scan GSC on-demand e run AI
    # Analyzer eseguiti da un worker separato invece che dentro la request.
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    # Flask-Limiter: stesso Redis, non lo storage in-memory di default — con
    # gunicorn multi-worker un limite in-memory sarebbe per-processo, non
    # condiviso, quindi inaffidabile (vedi app/billing/access.py::init_rate_limits).
    RATELIMIT_STORAGE_URI = REDIS_URL

    # Chiave Fernet per cifrare access/refresh token in DB (obbligatoria per app/gsc).
    # Generane una con: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    TOKEN_ENCRYPTION_KEY = os.environ.get("TOKEN_ENCRYPTION_KEY")

    # DeepSeek — AI Analyzer (endpoint OpenAI-compatibile). Se la chiave manca,
    # lo switch AI resta disattivabile ma l'analisi risponde "non configurata".
    DEEPSEEK_API = os.environ.get("DEEPSEEK_API")
    DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

    # Resend — invio email transazionali (es. codici OTP). RESEND_API è la
    # API key (re_...). RESEND_FROM è il mittente: deve usare un dominio
    # verificato su Resend (qui linkbay-cms.com è già verificato).
    RESEND_API = os.environ.get("RESEND_API")
    RESEND_FROM = os.environ.get("RESEND_FROM", "LinkBayCMS <no-reply@linkbay-cms.com>")

    # OTP via email al login/registrazione. Codice numerico a 6 cifre, valido
    # OTP_TTL_SECONDS, max OTP_MAX_ATTEMPTS tentativi, e un nuovo invio non è
    # richiedibile prima di OTP_RESEND_COOLDOWN secondi.
    OTP_TTL_SECONDS = int(os.environ.get("OTP_TTL_SECONDS", "600"))
    OTP_MAX_ATTEMPTS = int(os.environ.get("OTP_MAX_ATTEMPTS", "5"))
    OTP_RESEND_COOLDOWN = int(os.environ.get("OTP_RESEND_COOLDOWN", "60"))

    # Recupero password via email (link, non codice). Valido
    # PASSWORD_RESET_TTL_SECONDS, un nuovo invio non è richiedibile prima di
    # PASSWORD_RESET_RESEND_COOLDOWN secondi (vedi app/auth/password_reset.py).
    PASSWORD_RESET_TTL_SECONDS = int(os.environ.get("PASSWORD_RESET_TTL_SECONDS", "3600"))
    PASSWORD_RESET_RESEND_COOLDOWN = int(os.environ.get("PASSWORD_RESET_RESEND_COOLDOWN", "60"))

    # Revolut Business — link di pagamento manuali per i piani Pro (1/3/12
    # mesi), dopo il trial di 13 giorni (vedi app/billing/). Nessuna API,
    # nessun webhook: il cliente paga su un link statico creato a mano nella
    # dashboard Revolut Business, Revolut notifica il pagamento via email e un
    # admin attiva/estende il piano da Flask-Admin (vedi
    # app/billing/revolut_manual_activation.py). Se un link non è
    # configurato, la relativa CTA in /billing/upgrade si disabilita da sola
    # invece di puntare a un placeholder.
    REVOLUT_PAYMENT_LINK_1M = os.environ.get("REVOLUT_PAYMENT_LINK_1M")
    REVOLUT_PAYMENT_LINK_3M = os.environ.get("REVOLUT_PAYMENT_LINK_3M")
    REVOLUT_PAYMENT_LINK_12M = os.environ.get("REVOLUT_PAYMENT_LINK_12M")
