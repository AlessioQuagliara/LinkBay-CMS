from models.database import db
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

# 🔹 **Modello per la Lista Negozi**
class ShopList(db.Model):
    __tablename__ = "ShopList"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), nullable=False, unique=True)  # 🏪 Nome del negozio
    shop_type = db.Column(db.String(50), nullable=False)  # 🔧 Tipo di negozio (ex themeOptions)
    domain = db.Column(db.String(255), nullable=True, unique=True)  # 🌐 Dominio del negozio
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # 👤 Utente proprietario
    partner_id = db.Column(db.Integer, db.ForeignKey("agency.id"), nullable=True)  # 🤝 Partner opzionale

    def __repr__(self):
        return f"<ShopList {self.id} - {self.shop_name} ({self.shop_type})>"

# 🔍 **Recupera un negozio per nome**
def get_shop_by_name(shop_name):
    try:
        shop = ShopList.query.filter_by(shop_name=shop_name).first()
        return shop_to_dict(shop) if shop else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del negozio '{shop_name}': {e}")
        return None

# 🔍 **Recupera un negozio per nome o dominio**
def get_shop_by_name_or_domain(value):
    try:
        shop = ShopList.query.filter((ShopList.shop_name == value) | (ShopList.domain == value)).first()
        return shop_to_dict(shop) if shop else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del negozio con valore '{value}': {e}")
        return None

# 🔄 **Aggiorna il dominio di un negozio**
def update_shop_domain(shop_name, domain):
    try:
        shop = ShopList.query.filter_by(shop_name=shop_name).first()
        if not shop:
            return False

        shop.domain = domain
        db.session.commit()
        logging.info(f"🔄 Dominio aggiornato per '{shop_name}': {domain}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento del dominio per '{shop_name}': {e}")
        return False

# 📌 **Helper per convertire un negozio in dizionario**
def shop_to_dict(shop):
    return {col.name: getattr(shop, col.name) for col in ShopList.__table__.columns} if shop else None