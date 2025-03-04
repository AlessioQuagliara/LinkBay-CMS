from models.database import db
from datetime import datetime
import logging

# 📌 Inizializza il logger
logging.basicConfig(level=logging.INFO)


from models.database import db
from datetime import datetime
import logging

# 📌 Inizializza il logger
logging.basicConfig(level=logging.INFO)

# 🔹 **Modello per i Prodotti**
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Nome dello shop
    name = db.Column(db.String(255), nullable=False)  # 📌 Nome del prodotto
    description = db.Column(db.Text, nullable=True)  # 📝 Descrizione lunga
    short_description = db.Column(db.Text, nullable=True)  # 📝 Descrizione breve
    price = db.Column(db.Float, nullable=False)  # 💰 Prezzo
    discount_price = db.Column(db.Float, nullable=True)  # 🏷️ Prezzo scontato
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)  # 📦 Quantità disponibile
    sku = db.Column(db.String(255), unique=True, nullable=False)  # 🔖 Codice SKU
    ean_code = db.Column(db.String(255), unique=True, nullable=True)  # 🔍 Codice EAN (può essere NULL)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)  # 📂 Categoria
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id", ondelete="SET NULL"), nullable=True)  # 🏷️ Brand
    weight = db.Column(db.Float, nullable=True)  # ⚖️ Peso
    dimensions = db.Column(db.String(255), nullable=True)  # 📏 Dimensioni
    color = db.Column(db.String(255), nullable=True)  # 🎨 Colore
    material = db.Column(db.String(255), nullable=True)  # 🏗️ Materiale
    slug = db.Column(db.String(255), unique=True, nullable=False)  # 🔗 Slug URL
    is_active = db.Column(db.Boolean, default=True)  # ✅ Attivo o no
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Aggiornamento

    # 🔗 Relazioni con altre tabelle
    images = db.relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    attributes = db.relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.id} - {self.name}>"


# 🔹 **Modello per le Immagini dei Prodotti**
class ProductImage(db.Model):
    __tablename__ = "product_images"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    image_url = db.Column(db.String(512), nullable=False)  # 🖼️ URL dell'immagine
    is_main = db.Column(db.Boolean, default=False)  # ⭐ Indica se è l'immagine principale

    product = db.relationship("Product", back_populates="images")  # 🔄 Relazione con `Product`

    def __repr__(self):
        return f"<ProductImage {self.id} - Product {self.product_id}>"


# 🔹 **Modello per gli Attributi dei Prodotti (Varianti)**
class ProductAttribute(db.Model):
    __tablename__ = "product_attributes"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    attribute_name = db.Column(db.String(100), nullable=False)  # Es. "Size", "Color"
    attribute_value = db.Column(db.String(100), nullable=False)  # Es. "Red", "XL"
    price_modifier = db.Column(db.Float, default=0.0)  # 💰 Modifica del prezzo in base alla variante
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)  # 📦 Quantità disponibile della variante
    variant_image_url = db.Column(db.String(512), nullable=True)  # 🖼️ Immagine della variante
    ean_code = db.Column(db.String(255), unique=True, nullable=True)  # 🔍 Codice EAN della variante (può essere NULL)

    product = db.relationship("Product", back_populates="attributes")  # 🔄 Relazione con `Product`

    def __repr__(self):
        return f"<ProductAttribute {self.id} - Product {self.product_id} - {self.attribute_name}: {self.attribute_value}>"

# 🔹 **Modello per i Brands**    
class Brand(db.Model):
    __tablename__ = "brands"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ID univoco
    name = db.Column(db.String(255), nullable=False, unique=True)  # Nome univoco del brand

    # Relazione con prodotti (opzionale, se vuoi caricare i prodotti insieme ai brand)
    products = db.relationship("Product", backref="brand", lazy=True)

# ✅ **Crea un nuovo prodotto**
def create_product(data):
    try:
        new_product = Product(
            shop_name=data["shop_name"],
            name=data["name"],
            description=data.get("description"),
            short_description=data.get("short_description"),
            price=data["price"],
            discount_price=data.get("discount_price"),
            stock_quantity=data["stock_quantity"],
            sku=data["sku"],
            category_id=data.get("category_id"),
            brand_id=data.get("brand_id"),
            weight=data.get("weight"),
            dimensions=data.get("dimensions"),
            color=data.get("color"),
            material=data.get("material"),
            image_url=data.get("image_url"),
            slug=data["slug"],
            is_active=data.get("is_active", True),
        )
        db.session.add(new_product)
        db.session.commit()
        logging.info(f"✅ Prodotto '{data['name']}' aggiunto con successo.")
        return new_product.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione del prodotto: {e}")
        return None

# 🔍 **Recupera tutti i prodotti per un negozio**
def get_all_products(shop_name):
    try:
        products = Product.query.filter_by(shop_name=shop_name).all()
        return [product_to_dict(p) for p in products]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei prodotti per '{shop_name}': {e}")
        return []

# 🔍 **Recupera un prodotto per slug**
def get_product_by_slug(slug, shop_name):
    try:
        product = Product.query.filter_by(slug=slug, shop_name=shop_name).first()
        return product_to_dict(product) if product else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del prodotto '{slug}': {e}")
        return None

# 🔄 **Aggiorna un prodotto**
def update_product(product_id, data):
    try:
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return False

        for key, value in data.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)

        product.updated_at = datetime.utcnow()
        db.session.commit()
        logging.info(f"✅ Prodotto '{product_id}' aggiornato con successo.")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento del prodotto {product_id}: {e}")
        return False

# ❌ **Elimina un prodotto**
def delete_product(product_id):
    try:
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return False

        db.session.delete(product)
        db.session.commit()
        logging.info(f"🗑️ Prodotto '{product_id}' eliminato con successo.")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione del prodotto {product_id}: {e}")
        return False

# 🔍 **Recupera prodotti per categoria**
def get_products_by_category(category_id):
    try:
        products = Product.query.filter_by(category_id=category_id).all()
        return [product_to_dict(p) for p in products]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei prodotti per categoria {category_id}: {e}")
        return []

# 🔍 **Recupera prodotti per brand**
def get_products_by_brand(brand_id):
    try:
        products = Product.query.filter_by(brand_id=brand_id).all()
        return [product_to_dict(p) for p in products]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei prodotti per brand {brand_id}: {e}")
        return []

# 🔍 **Cerca prodotti per nome**
def search_products(query_text, shop_name):
    try:
        products = Product.query.filter(Product.name.ilike(f"%{query_text}%"), Product.shop_name == shop_name).all()
        return [product_to_dict(p) for p in products]
    except Exception as e:
        logging.error(f"❌ Errore nella ricerca prodotti: {e}")
        return []

# 🔍 **Recupera prodotti per ID multipli**
def get_products_by_ids(product_ids):
    try:
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        return [product_to_dict(p) for p in products]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero di prodotti multipli: {e}")
        return []

# 🔍 **Recupera il primo prodotto di un negozio**
def get_first_product_by_shop(shop_name):
    try:
        product = Product.query.filter_by(shop_name=shop_name).order_by(Product.id.asc()).first()
        return product_to_dict(product) if product else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del primo prodotto per '{shop_name}': {e}")
        return None

# 📌 **Helper per convertire un prodotto in dizionario**
def product_to_dict(product):
    return {col.name: getattr(product, col.name) for col in Product.__table__.columns} if product else None