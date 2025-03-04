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

    # OpenAI API Key
    OPENAI_API_KEY = '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'
    
    if os.getenv('ENVIRONMENT') == 'development':
        # Altre configurazioni 
        SESSION_COOKIE_SECURE = False  # PER CHI MODIFICA = Sicuro solo su HTTPS, disabilitato in locale
        SESSION_PERMANENT = False  # PER CHI MODIFICA = Non mantenere la sessione dopo la chiusura del browser
        # Configurazioni GoDaddy API TEST
        GODADDY_API_URL = 'https://api.ote-godaddy.com/v1/'
        GODADDY_API_KEY = '3mM44WkB29Cg9H_GRJds69oVsyQQrUYFoeTyh'
        GODADDY_API_SECRET = '42FBcBbn8SZFWuGGsetaDF'
        # Configurazioni Stripe interne
        STRIPE_SECRET_KEY='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'
        STRIPE_PUBLISHABLE_KEY='pk_live_51MijPqDLzaeBHrX0rui4jtJnGx1kTSKVNbVy6hbQQYUfoMhVTMVEFoN6U7jfYh2tyRgLhvSgOSM5wpSmi55nS3PH00XUmvoSY0'
    else:
        SESSION_COOKIE_SECURE = True  # PER CHI MODIFICA = Sicuro solo su HTTPS, disabilitato in locale
        SESSION_PERMANENT = True  # PER CHI MODIFICA = Non mantenere la sessione dopo la chiusura del browser
        # Configurazioni GoDaddy API PRODUZIONE
        GODADDY_API_URL = 'https://api.godaddy.com/v1'
        GODADDY_API_KEY = 'h1p3oVvDvVzt_4bcJJnnHMd3naQ74EaWzzS'  
        GODADDY_API_SECRET = 'NeLezhbgDrRdE56raE5KmY'  
        # Configurazioni Stripe interne
        STRIPE_SECRET_KEY='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'
        STRIPE_PUBLISHABLE_KEY='pk_live_51MijPqDLzaeBHrX0rui4jtJnGx1kTSKVNbVy6hbQQYUfoMhVTMVEFoN6U7jfYh2tyRgLhvSgOSM5wpSmi55nS3PH00XUmvoSY0'