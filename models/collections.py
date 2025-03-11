from models.database import db
import logging
from functools import wraps
from datetime import datetime

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per le Collezioni**
class Collection(db.Model):
    __tablename__ = "collections"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco della collezione
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Nome dello shop
    name = db.Column(db.String(255), nullable=False)  # 📛 Nome della collezione
    slug = db.Column(db.String(255), unique=True, nullable=False)  # 🔗 Slug URL
    description = db.Column(db.String(1024), nullable=True)  # 📜 Descrizione
    image_url = db.Column(db.String(512), nullable=True)  # 🖼️ URL immagine
    is_active = db.Column(db.Boolean, default=True)  # ✅ Stato della collezione
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    images = db.relationship("CollectionImage", backref="collection", cascade="all, delete-orphan")
    products = db.relationship("CollectionProduct", backref="collection", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Collection {self.name} (ID: {self.id})>"

# 📸 **Modello per le Immagini delle Collezioni**
class CollectionImage(db.Model):
    __tablename__ = "collection_images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco immagine
    collection_id = db.Column(db.Integer, db.ForeignKey("collections.id"), nullable=False)  # 🔗 Collegamento a Collection
    image_url = db.Column(db.String(512), nullable=False)  # 🖼️ URL immagine
    is_main = db.Column(db.Boolean, default=False)  # ⭐ Immagine principale

    def __repr__(self):
        return f"<CollectionImage {self.image_url} (Collection ID: {self.collection_id})>"

# 🛒 **Modello per i Prodotti nelle Collezioni**
class CollectionProduct(db.Model):
    __tablename__ = "collection_products"

    collection_id = db.Column(db.Integer, db.ForeignKey("collections.id"), primary_key=True)  # 🔗 Collezione
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), primary_key=True)  # 🔗 Prodotto

    def __repr__(self):
        return f"<CollectionProduct Collection ID: {self.collection_id}, Product ID: {self.product_id}>"

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

# 🔄 **Helper per convertire un modello in dizionario**
def model_to_dict(model):
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}

# ✅ **Crea una nuova collezione**
@handle_db_errors
def create_collection(shop_name, name, slug, description=None, image_url=None, is_active=True):
    new_collection = Collection(
        shop_name=shop_name,
        name=name,
        slug=slug,
        description=description,
        image_url=image_url,
        is_active=is_active
    )
    db.session.add(new_collection)
    db.session.commit()
    logging.info(f"✅ Collezione '{name}' creata con successo")
    return new_collection.id

# 🔍 **Recupera tutte le collezioni per uno shop**
@handle_db_errors
def get_all_collections(shop_name):
    collections = Collection.query.filter_by(shop_name=shop_name).all()
    return [model_to_dict(col) for col in collections]

# 🔄 **Aggiorna una collezione**
@handle_db_errors
def update_collection(collection_id, data):
    collection = Collection.query.get(collection_id)
    if not collection:
        return False

    for key, value in data.items():
        setattr(collection, key, value)

    db.session.commit()
    logging.info(f"✅ Collezione {collection_id} aggiornata con successo")
    return True

# ❌ **Elimina una collezione**
@handle_db_errors
def delete_collection(collection_id):
    collection = Collection.query.get(collection_id)
    if not collection:
        return False

    db.session.delete(collection)
    db.session.commit()
    logging.info(f"🗑️ Collezione {collection_id} eliminata con successo")
    return True

# 📸 **Aggiunge un'immagine a una collezione**
@handle_db_errors
def add_collection_image(collection_id, image_url, is_main=False):
    new_image = CollectionImage(collection_id=collection_id, image_url=image_url, is_main=is_main)
    db.session.add(new_image)
    db.session.commit()
    logging.info(f"✅ Immagine aggiunta alla collezione {collection_id}")
    return new_image.id

# 📸 **Recupera tutte le immagini di una collezione**
@handle_db_errors
def get_collection_images(collection_id):
    images = CollectionImage.query.filter_by(collection_id=collection_id).all()
    return [model_to_dict(img) for img in images]

# 🛒 **Aggiunge un prodotto a una collezione**
@handle_db_errors
def add_product_to_collection(collection_id, product_id):
    new_relation = CollectionProduct(collection_id=collection_id, product_id=product_id)
    db.session.add(new_relation)
    db.session.commit()
    logging.info(f"✅ Prodotto {product_id} aggiunto alla collezione {collection_id}")
    return True

# ❌ **Rimuove un prodotto da una collezione**
@handle_db_errors
def remove_product_from_collection(collection_id, product_id):
    CollectionProduct.query.filter_by(collection_id=collection_id, product_id=product_id).delete()
    db.session.commit()
    logging.info(f"✅ Prodotto {product_id} rimosso dalla collezione {collection_id}")
    return True

# 🔍 **Recupera i prodotti di una collezione**
@handle_db_errors
def get_products_in_collection(collection_id):
    products = db.session.query(CollectionProduct.product_id).filter_by(collection_id=collection_id).all()
    return [p.product_id for p in products]

# 🔍 **Recupera tutte le collezioni attive per uno shop**
@handle_db_errors
def get_collections_by_shop(shop_name):
    collections = Collection.query.filter_by(shop_name=shop_name, is_active=True).order_by(Collection.name).all()
    return [model_to_dict(col) for col in collections]