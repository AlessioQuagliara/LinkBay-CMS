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
    
    # Altre configurazioni 
    SESSION_COOKIE_SECURE = True  # Sessione sicura (HTTPS)
    SESSION_PERMANENT = False  # Chido la sessione dopo che il browser è chiuso dall'utente