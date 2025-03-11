from models.database import db
import logging
from functools import wraps

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per le impostazioni web di un negozio**
class WebSettings(db.Model):
    __tablename__ = "web_settings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shop_name = db.Column(db.String(255), db.ForeignKey("ShopList.shop_name"), unique=True, nullable=False)
    theme_name = db.Column(db.String(255), nullable=True)
    google_analytics = db.Column(db.Text, nullable=True)
    facebook_pixel = db.Column(db.Text, nullable=True)
    tiktok_pixel = db.Column(db.Text, nullable=True)
    head = db.Column(db.Text, nullable=True)
    favicon = db.Column(db.Text, nullable=True)
    foot = db.Column(db.Text, nullable=True)
    script = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<WebSettings shop_name={self.shop_name}, theme={self.theme_name}>"
    
# DIZIONARIO ---------------------------------------------------- 
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# 🔄 **Decoratore per la gestione degli errori del database**
def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            db.session.rollback()
            logging.error(f"❌ Errore in {func.__name__}: {e}")
            return None
    return wrapper


# ✅ **Recupera le impostazioni web di un negozio**
@handle_db_errors
def get_web_settings(shop_name):
    settings = WebSettings.query.filter_by(shop_name=shop_name).first()
    return settings if settings else None


# ✅ **Aggiorna head, foot e script per un negozio**
@handle_db_errors
def update_web_settings(shop_name, head_content=None, script_content=None, foot_content=None):
    settings = WebSettings.query.filter_by(shop_name=shop_name).first()
    if settings:
        settings.head = head_content if head_content is not None else settings.head
        settings.script = script_content if script_content is not None else settings.script
        settings.foot = foot_content if foot_content is not None else settings.foot
    else:
        settings = WebSettings(shop_name=shop_name, head=head_content, script=script_content, foot=foot_content)
        db.session.add(settings)

    db.session.commit()
    logging.info(f"✅ Impostazioni web aggiornate per '{shop_name}'")
    return True