class Config:
    LANGUAGES = ['en', 'it', 'es', 'fr', 'de']  
    DEFAULT_LANGUAGE = 'en'  
    SECRET_KEY = 'cxzw5H23390@sall13&'  
    
    # Configurazioni del Database
    DB_HOST = '127.0.0.1'
    DB_USER = 'root'
    DB_PASSWORD = 'root'
    DB_NAME = 'CMS_DEF'
    DB_PORT = 8889
    
    # Altre configurazioni 
    SESSION_COOKIE_SECURE = True  # Sessione sicura (HTTPS)
    SESSION_PERMANENT = False  # Chido la sessione dopo che il browser è chiuso dall'utente