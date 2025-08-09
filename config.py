import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

class Config:
    """
    Configurazione generale dell'applicazione.
    """
    LANGUAGES = ['en', 'it', 'es', 'fr', 'de']
    DEFAULT_LANGUAGE = 'en'
    
    # Chiave segreta per la sicurezza dell'app
    SECRET_KEY = os.getenv("SECRET_KEY", "SpotexSrl@2024")

    # Configurazione database PostgreSQL per CMS_DEF
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql+psycopg2://root:root@localhost/cms_def')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # configurazione per Google AUTH
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "365461856822-j2egbbab7fihijb8vsg4h3298dge1shp.apps.googleusercontent.com")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "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")
    FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID", "474199322354663")
    FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET", "1618a8b7fa1b59c01f1920b2d9de55dd")
    APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID", "365461856822-j2egbbab7fihijb8vsg4h3298dge1shp.apps.googleusercontent.com")
    APPLE_CLIENT_SECRET = os.getenv("APPLE_CLIENT_SECRET", "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")

    # DeepSeek API Key
    DEEPSEEK_API_KEY = 'sk-82c79d72f35b402fb2f85a81bfe2d245'

    # Configurazione per l'invio di email
    MAIL_SERVER = 'smtps.aruba.it'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'noreply@linkbay-cms-support.com'
    MAIL_PASSWORD = 'WtQ5i8h20@'
    MAIL_DEFAULT_SENDER = 'noreply@linkbay-cms-support.com'
    
    if os.getenv('ENVIRONMENT') == 'development':
        # Altre configurazioni 
        SESSION_COOKIE_SECURE = False  # PER CHI MODIFICA = Sicuro solo su HTTPS, disabilitato in locale
        SESSION_PERMANENT = False  # PER CHI MODIFICA = Non mantenere la sessione dopo la chiusura del browser
        # Configurazioni GoDaddy API TEST
        GODADDY_API_URL = 'https://api.ote-godaddy.com/v1'
        GODADDY_API_KEY = '3mM44WkB29Cg9H_GRJds69oVsyQQrUYFoeTyh'
        GODADDY_API_SECRET = '42FBcBbn8SZFWuGGsetaDF'
        # Configurazioni Stripe interne
        STRIPE_WEBHOOK_SECRET = 'whsec_9e89f572077eefee590c317bafbb534224b3d64c9c5cbdc4cfebb625a5c80589'
        STRIPE_SECRET_KEY='sk_test_51R8r8BPteJOX9ukri0MrftLIDZoumDLgnKQz4upe7kHyhuxD3EpG44LAtz6jBdDhUr6iQAbvx9a0oIKfpfNClNCU00zCFovMAA'
        STRIPE_PUBLISHABLE_KEY='pk_test_51R8r8BPteJOX9ukruE1O5G1S8VqbgKzlHmhTPAqQQdWSibh9fkctSH6zobztupPgnrQiGfDZ7C9En96mSMxyO1Yz00R0EdgIUd'
    else:
        SESSION_COOKIE_SECURE = True  # PER CHI MODIFICA = Sicuro solo su HTTPS, disabilitato in locale
        SESSION_PERMANENT = True  # PER CHI MODIFICA = Non mantenere la sessione dopo la chiusura del browser
        # Configurazioni GoDaddy API PRODUZIONE
        GODADDY_API_URL = 'https://api.godaddy.com/v1'
        GODADDY_API_KEY = 'h1p3oVvDvVzt_4bcJJnnHMd3naQ74EaWzzS'  
        GODADDY_API_SECRET = 'NeLezhbgDrRdE56raE5KmY'  
        # Configurazioni Stripe interne
        STRIPE_WEBHOOK_SECRET = 'whsec_xEE4UjbnBuwf9HehsVfL7p4OeuSFaequ'
        STRIPE_SECRET_KEY='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'
        STRIPE_PUBLISHABLE_KEY='pk_live_51R8r84LbvfE9v2XljJqWpMiNMskDZi4rmfy00FsWVYgxReVXyctlCWUexNxhzq64jlLy7TYwEQ3xiBi8BwVtDMUw00DslS3PLB'
