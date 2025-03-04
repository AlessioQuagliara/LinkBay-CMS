from models.database import db
import logging
from datetime import datetime

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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


# ✅ **Crea una nuova collezione**
def create_collection(shop_name, name, slug, description=None, image_url=None, is_active=True):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione della collezione '{name}': {e}")
        return None


# 🔍 **Recupera tutte le collezioni per uno shop**
def get_all_collections(shop_name):
    try:
        collections = Collection.query.filter_by(shop_name=shop_name).all()
        return [collection_to_dict(col) for col in collections]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero delle collezioni per lo shop '{shop_name}': {e}")
        return []


# 🔄 **Aggiorna una collezione**
def update_collection(collection_id, data):
    try:
        collection = Collection.query.get(collection_id)
        if not collection:
            return False

        for key, value in data.items():
            setattr(collection, key, value)

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento della collezione {collection_id}: {e}")
        return False


# ❌ **Elimina una collezione**
def delete_collection(collection_id):
    try:
        collection = Collection.query.get(collection_id)
        if not collection:
            return False

        db.session.delete(collection)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione della collezione {collection_id}: {e}")
        return False


# 📸 **Aggiunge un'immagine a una collezione**
def add_collection_image(collection_id, image_url, is_main=False):
    try:
        new_image = CollectionImage(collection_id=collection_id, image_url=image_url, is_main=is_main)
        db.session.add(new_image)
        db.session.commit()
        return new_image.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiunta dell'immagine alla collezione {collection_id}: {e}")
        return None


# 📸 **Recupera tutte le immagini di una collezione**
def get_collection_images(collection_id):
    try:
        images = CollectionImage.query.filter_by(collection_id=collection_id).all()
        return [image_to_dict(img) for img in images]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero delle immagini per la collezione {collection_id}: {e}")
        return []


# 🛒 **Aggiunge un prodotto a una collezione**
def add_product_to_collection(collection_id, product_id):
    try:
        new_relation = CollectionProduct(collection_id=collection_id, product_id=product_id)
        db.session.add(new_relation)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiunta del prodotto {product_id} alla collezione {collection_id}: {e}")
        return False


# ❌ **Rimuove un prodotto da una collezione**
def remove_product_from_collection(collection_id, product_id):
    try:
        CollectionProduct.query.filter_by(collection_id=collection_id, product_id=product_id).delete()
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella rimozione del prodotto {product_id} dalla collezione {collection_id}: {e}")
        return False


# 🔍 **Recupera i prodotti di una collezione**
def get_products_in_collection(collection_id):
    try:
        products = db.session.query(CollectionProduct.product_id).filter_by(collection_id=collection_id).all()
        return [p.product_id for p in products]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei prodotti della collezione {collection_id}: {e}")
        return []


# 🔍 **Recupera tutte le collezioni attive per uno shop**
def get_collections_by_shop(shop_name):
    try:
        collections = Collection.query.filter_by(shop_name=shop_name, is_active=True).order_by(Collection.name).all()
        return [collection_to_dict(col) for col in collections]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero delle collezioni attive per lo shop '{shop_name}': {e}")
        return []


# 📌 **Helper per convertire una collezione in dizionario**
def collection_to_dict(collection):
    return {
        "id": collection.id,
        "shop_name": collection.shop_name,
        "name": collection.name,
        "slug": collection.slug,
        "description": collection.description,
        "image_url": collection.image_url,
        "is_active": collection.is_active,
        "created_at": collection.created_at,
        "updated_at": collection.updated_at,
    }


# 📸 **Helper per convertire un'immagine in dizionario**
def image_to_dict(image):
    return {
        "id": image.id,
        "collection_id": image.collection_id,
        "image_url": image.image_url,
        "is_main": image.is_main,
    }