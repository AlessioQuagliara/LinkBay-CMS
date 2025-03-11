from models.database import db
import logging
from functools import wraps

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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


# 🔍 **Recupera un negozio per nome**
@handle_db_errors
def get_shop_by_name(shop_name):
    shop = ShopList.query.filter_by(shop_name=shop_name).first()
    return shop_to_dict(shop) if shop else None


# 🔍 **Recupera un negozio per nome o dominio**
@handle_db_errors
def get_shop_by_name_or_domain(value):
    shop = ShopList.query.filter((ShopList.shop_name == value) | (ShopList.domain == value)).first()
    return shop_to_dict(shop) if shop else None


# 🔄 **Aggiorna il dominio di un negozio**
@handle_db_errors
def update_shop_domain(shop_name, domain):
    shop = ShopList.query.filter_by(shop_name=shop_name).first()
    if not shop:
        return False

    shop.domain = domain
    db.session.commit()
    logging.info(f"🔄 Dominio aggiornato per '{shop_name}': {domain}")
    return True


# 📌 **Helper per convertire un negozio in dizionario**
def shop_to_dict(shop):
    return {col.name: getattr(shop, col.name) for col in ShopList.__table__.columns} if shop else None