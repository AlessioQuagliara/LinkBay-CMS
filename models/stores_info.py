from models.database import db
from datetime import datetime
import logging
from functools import wraps

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per le Informazioni degli Store**
class StoreInfo(db.Model):
    __tablename__ = "stores_info"

    shop_name = db.Column(db.String(255), primary_key=True)  # 🏪 Nome dello shop
    owner_name = db.Column(db.String(255), nullable=False)  # 👤 Proprietario
    email = db.Column(db.String(255), nullable=False, unique=True)  # 📧 Email
    phone = db.Column(db.String(20), nullable=True)  # 📞 Numero di telefono
    industry = db.Column(db.String(255), nullable=True)  # 🏭 Settore industriale
    description = db.Column(db.String(500), nullable=True)  # 📝 Descrizione dello store
    website_url = db.Column(db.String(255), nullable=True)  # 🌐 Sito web
    revenue = db.Column(db.Float, default=0.0)  # 💰 Fatturato totale
    total_orders = db.Column(db.Integer, default=0)  # 📦 Numero ordini
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    def __repr__(self):
        return f"<StoreInfo {self.shop_name} - {self.owner_name}>"
    
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


# ✅ **Crea un nuovo store**
@handle_db_errors
def create_store(shop_name, owner_name, email, phone=None, industry=None, description=None, website_url=None, revenue=0.0):
    store = StoreInfo(
        shop_name=shop_name,
        owner_name=owner_name,
        email=email,
        phone=phone,
        industry=industry,
        description=description,
        website_url=website_url,
        revenue=revenue,
    )
    db.session.add(store)
    db.session.commit()
    logging.info(f"✅ Store creato: {shop_name} - Proprietario: {owner_name}")
    return True


# 🔍 **Recupera le informazioni di uno store**
@handle_db_errors
def get_store_by_name(shop_name):
    store = StoreInfo.query.filter_by(shop_name=shop_name).first()
    return store_to_dict(store) if store else None


# 🔄 **Aggiorna le informazioni di uno store**
@handle_db_errors
def update_store(shop_name, **kwargs):
    store = StoreInfo.query.filter_by(shop_name=shop_name).first()
    if not store:
        return False

    for key, value in kwargs.items():
        setattr(store, key, value)

    store.updated_at = datetime.utcnow()
    db.session.commit()
    logging.info(f"🔄 Store aggiornato: {shop_name}")
    return True


# ❌ **Elimina uno store**
@handle_db_errors
def delete_store(shop_name):
    store = StoreInfo.query.filter_by(shop_name=shop_name).first()
    if not store:
        return False

    db.session.delete(store)
    db.session.commit()
    logging.info(f"❌ Store eliminato: {shop_name}")
    return True


# 🔍 **Recupera tutti gli store**
@handle_db_errors
def get_all_stores():
    stores = StoreInfo.query.all()
    return [store_to_dict(store) for store in stores]


# 🔍 **Verifica se uno store esiste**
@handle_db_errors
def store_exists(shop_name):
    return db.session.query(StoreInfo.shop_name).filter_by(shop_name=shop_name).first() is not None


# 📌 **Helper per convertire uno store in dizionario**
def store_to_dict(store):
    return {col.name: getattr(store, col.name) for col in StoreInfo.__table__.columns} if store else None