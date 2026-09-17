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

    # Revolut Business — link di pagamento manuali per i pacchetti crediti AI
    # (vendita una tantum, riservata ai piani AppSumo — vedi
    # app/entitlements/service.py::get_plan_limits().ai_credit_topups_allowed).
    # Nome della env var = numero di crediti del pacchetto (vedi
    # app/billing/revolut_products.py::AI_TOPUP_CATALOG), non l'etichetta
    # commerciale — resta stabile anche se cambia il naming marketing.
    REVOLUT_AI_TOPUP_LINK_50 = os.environ.get("REVOLUT_AI_TOPUP_LINK_50")
    REVOLUT_AI_TOPUP_LINK_150 = os.environ.get("REVOLUT_AI_TOPUP_LINK_150")
    REVOLUT_AI_TOPUP_LINK_500 = os.environ.get("REVOLUT_AI_TOPUP_LINK_500")

    # Paddle Billing — provider principale per abbonamenti Pro (checkout
    # server-driven, webhook firmati) e pacchetti crediti AI one-time. Vedi
    # app/billing/paddle_client.py per la scelta sandbox/production e
    # docs/paddle-billing.md per l'architettura completa. Revolut/AppSumo
    # restano attivi come canali legacy/manuali (vedi sopra), non sostituiti.
    #
    # "sandbox" (default) o "production" — l'UNICA leva che decide sia il
    # base URL API (sandbox-api.paddle.com vs api.paddle.com) sia quale set
    # di price ID viene risolto (_SANDBOX_* vs _PRODUCTION_* sotto). Nessuna
    # altra condizione nel codice (host, DEBUG, ecc.) deve mai influenzare
    # questa scelta.
    PADDLE_ENVIRONMENT = os.environ.get("PADDLE_ENVIRONMENT", "sandbox")
    # API key server-side (Paddle Dashboard > Developer Tools > Authentication).
    # MAI esposta al frontend, nei template, nei log o nei messaggi di errore
    # — solo letta da app/billing/paddle_client.py per l'header Authorization.
    PADDLE_API_KEY = os.environ.get("PADDLE_API_KEY")
    # Secret del webhook Paddle (Dashboard > Developer Tools > Notifications >
    # endpoint > "Signing secret"), usato SOLO per verificare l'header
    # Paddle-Signature sul raw body — mai per autenticare richieste in uscita.
    PADDLE_WEBHOOK_SECRET = os.environ.get("PADDLE_WEBHOOK_SECRET")
    # Client-side token (Dashboard > Developer Tools > Authentication > Client-
    # side tokens) — l'unico valore Paddle sicuro da esporre nel browser. Non
    # usato dal flusso di checkout attuale (hosted checkout: il backend crea
    # la transazione e reindirizza a transaction.checkout.url, niente
    # Paddle.js/overlay) — riservato per un futuro overlay checkout, vedi
    # docs/paddle-billing.md.
    PADDLE_CLIENT_TOKEN = os.environ.get("PADDLE_CLIENT_TOKEN")
    # URL di ritorno dopo il pagamento. Se non impostata, si usa la pagina
    # interna billing.paddle_pending (polling su /billing/status finché il
    # webhook non conferma) — vedi app/billing/paddle_routes.py.
    PADDLE_SUCCESS_URL = os.environ.get("PADDLE_SUCCESS_URL")
    PADDLE_DEFAULT_CURRENCY = os.environ.get("PADDLE_DEFAULT_CURRENCY", "EUR")

    # Price ID Paddle per i tre piani Pro (stessa durata/prezzo di
    # REVOLUT_PLAN_PRICES in app/entitlements/limits.py — vedi
    # app/billing/paddle_products.py) e per i tre pacchetti crediti AI
    # (stessi numeri di AI_CREDIT_PACKS). Due set separati, MAI mescolati:
    # quale set viene letto dipende solo da PADDLE_ENVIRONMENT sopra.
    PADDLE_SANDBOX_PRICE_ID_1M = os.environ.get("PADDLE_SANDBOX_PRICE_ID_1M")
    PADDLE_SANDBOX_PRICE_ID_3M = os.environ.get("PADDLE_SANDBOX_PRICE_ID_3M")
    PADDLE_SANDBOX_PRICE_ID_12M = os.environ.get("PADDLE_SANDBOX_PRICE_ID_12M")
    PADDLE_SANDBOX_PRICE_ID_AI_TOPUP_STARTER = os.environ.get("PADDLE_SANDBOX_PRICE_ID_AI_TOPUP_STARTER")
    PADDLE_SANDBOX_PRICE_ID_AI_TOPUP_GROWTH = os.environ.get("PADDLE_SANDBOX_PRICE_ID_AI_TOPUP_GROWTH")
    PADDLE_SANDBOX_PRICE_ID_AI_TOPUP_SCALE = os.environ.get("PADDLE_SANDBOX_PRICE_ID_AI_TOPUP_SCALE")

    PADDLE_PRODUCTION_PRICE_ID_1M = os.environ.get("PADDLE_PRODUCTION_PRICE_ID_1M")
    PADDLE_PRODUCTION_PRICE_ID_3M = os.environ.get("PADDLE_PRODUCTION_PRICE_ID_3M")
    PADDLE_PRODUCTION_PRICE_ID_12M = os.environ.get("PADDLE_PRODUCTION_PRICE_ID_12M")
    PADDLE_PRODUCTION_PRICE_ID_AI_TOPUP_STARTER = os.environ.get("PADDLE_PRODUCTION_PRICE_ID_AI_TOPUP_STARTER")
    PADDLE_PRODUCTION_PRICE_ID_AI_TOPUP_GROWTH = os.environ.get("PADDLE_PRODUCTION_PRICE_ID_AI_TOPUP_GROWTH")
    PADDLE_PRODUCTION_PRICE_ID_AI_TOPUP_SCALE = os.environ.get("PADDLE_PRODUCTION_PRICE_ID_AI_TOPUP_SCALE")
