class Config:
    LANGUAGES = ['en', 'it', 'es', 'fr', 'de']
    DEFAULT_LANGUAGE = 'en'
    SECRET_KEY = 'cxzw5H23390@sall13&'
    
    # Configurazioni del Database dell'app
    DB_HOST = '127.0.0.1'
    DB_USER = 'root'
    DB_PASSWORD = 'root'
    DB_NAME = 'CMS_DEF'
    DB_PORT = 8889

    #Configurazioni del database globale
    AUTH_DB_HOST = '127.0.0.1'
    AUTH_DB_USER = 'root'
    AUTH_DB_PASSWORD = 'root'
    AUTH_DB_NAME = 'CMS_INDEX'
    AUTH_DB_PORT = 8889

    # Configurazioni Stripe interne
    
    
    # Altre configurazioni 
    SESSION_COOKIE_SECURE = False  # PER CHI MODIFICA = Sicuro solo su HTTPS, disabilitato in locale
    SESSION_PERMANENT = False  # PER CHI MODIFICA = Non mantenere la sessione dopo la chiusura del browser

    # SESSION_COOKIE_DOMAIN su test ho visto che provoca danno
    # SESSION_COOKIE_DOMAIN = '.local'