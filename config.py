import os
from environment import environment

class Config:
    LANGUAGES = ['en', 'it', 'es', 'fr', 'de']
    DEFAULT_LANGUAGE = 'en'
    SECRET_KEY = 'SpotexSrl@2024'
    
    # Configurazioni del Database dell'app (CMS_DEF)
    DB_HOST = '127.0.0.1'
    DB_USER = 'root'
    DB_PASSWORD = 'root'
    DB_NAME = 'CMS_DEF'
    DB_PORT = 8889

    #Configurazioni del database globale (CMS_INDEX)
    AUTH_DB_HOST = '127.0.0.1'
    AUTH_DB_USER = 'root'
    AUTH_DB_PASSWORD = 'root'
    AUTH_DB_NAME = 'CMS_INDEX'
    AUTH_DB_PORT = 8889

    # OpenAI API Key
    OPENAI_API_KEY = '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'
    
    if environment == 'development':
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