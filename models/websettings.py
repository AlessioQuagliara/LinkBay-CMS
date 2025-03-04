from models.database import db
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

# ✅ **Recupera le impostazioni web di un negozio**
def get_web_settings(shop_name):
    try:
        settings = WebSettings.query.filter_by(shop_name=shop_name).first()
        return settings if settings else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero delle impostazioni web per '{shop_name}': {e}")
        return None

# ✅ **Aggiorna head, foot e script per un negozio**
def update_web_settings(shop_name, head_content=None, script_content=None, foot_content=None):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento delle impostazioni web per '{shop_name}': {e}")
        return False