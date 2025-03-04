from models.database import db
from datetime import datetime
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

# ✅ **Crea un nuovo store**
def create_store(shop_name, owner_name, email, phone=None, industry=None, description=None, website_url=None, revenue=0.0):
    try:
        store = StoreInfo(
            shop_name=shop_name,
            owner_name=owner_name,
            email=email,
            phone=phone,
            industry=industry,
            description=description,
            website_url=website_url,
            revenue=revenue,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(store)
        db.session.commit()
        logging.info(f"✅ Store creato: {shop_name} - Proprietario: {owner_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione dello store '{shop_name}': {e}")
        return False

# 🔍 **Recupera le informazioni di uno store**
def get_store_by_name(shop_name):
    try:
        store = StoreInfo.query.filter_by(shop_name=shop_name).first()
        return store_to_dict(store) if store else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dello store '{shop_name}': {e}")
        return None

# 🔄 **Aggiorna le informazioni di uno store**
def update_store(shop_name, **kwargs):
    try:
        store = StoreInfo.query.filter_by(shop_name=shop_name).first()
        if not store:
            return False
        for key, value in kwargs.items():
            setattr(store, key, value)
        store.updated_at = datetime.utcnow()
        db.session.commit()
        logging.info(f"🔄 Store aggiornato: {shop_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento dello store '{shop_name}': {e}")
        return False

# ❌ **Elimina uno store**
def delete_store(shop_name):
    try:
        store = StoreInfo.query.filter_by(shop_name=shop_name).first()
        if not store:
            return False
        db.session.delete(store)
        db.session.commit()
        logging.info(f"❌ Store eliminato: {shop_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella cancellazione dello store '{shop_name}': {e}")
        return False

# 🔍 **Recupera tutti gli store**
def get_all_stores():
    try:
        stores = StoreInfo.query.all()
        return [store_to_dict(store) for store in stores]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero di tutti gli store: {e}")
        return []

# 🔍 **Verifica se uno store esiste**
def store_exists(shop_name):
    try:
        return db.session.query(StoreInfo.shop_name).filter_by(shop_name=shop_name).first() is not None
    except Exception as e:
        logging.error(f"❌ Errore nel controllo dell'esistenza dello store '{shop_name}': {e}")
        return False

# 📌 **Helper per convertire uno store in dizionario**
def store_to_dict(store):
    return {col.name: getattr(store, col.name) for col in StoreInfo.__table__.columns} if store else None