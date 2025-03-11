from models.database import db
import logging
from functools import wraps
from datetime import datetime
import uuid

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    category = db.relationship("Category", backref="products", lazy=True)


    def __repr__(self):
        return f"<Product {self.id} - {self.name}>"
# DIZIONARIO ---------------------------------------------------- 
    def to_dict(self):
        return {
            "id": self.id,
            "shop_name": self.shop_name,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "discount_price": self.discount_price,
            "stock_quantity": self.stock_quantity,
            "sku": self.sku,
            "ean_code": self.ean_code,
            "category_id": self.category_id,
            "brand_id": self.brand_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

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


# ✅ **Crea un nuovo prodotto**
@handle_db_errors
def create_new_product(shop_subdomain):
    new_product = Product(
        name="New Product",
        short_description="Short description",
        description="Detailed description",
        price=0.0,
        discount_price=0.0,
        stock_quantity=0,
        sku=f"SKU-{uuid.uuid4().hex[:8]}",  # SKU univoco generato
        category_id=None,  
        brand_id=None,
        weight=0.0,
        dimensions="0x0x0",
        color="Default color",
        material="Default material",
        slug=f"new-product-{uuid.uuid4().hex[:8]}",  # Slug univoco generato
        is_active=False,
        shop_name=shop_subdomain
    )

    db.session.add(new_product)
    db.session.commit()

    return {
        'success': True,
        'message': 'Product created successfully.',
        'product_id': new_product.id
    }


# 🔍 **Recupera tutti i prodotti per un negozio**
@handle_db_errors
def get_all_products(shop_name):
    products = Product.query.filter_by(shop_name=shop_name).all()
    return [product_to_dict(p) for p in products]


# 🔍 **Recupera un prodotto per slug**
@handle_db_errors
def get_product_by_slug(slug, shop_name):
    product = Product.query.filter_by(slug=slug, shop_name=shop_name).first()
    return product_to_dict(product) if product else None


# 🔄 **Aggiorna un prodotto**
@handle_db_errors
def update_product(product_id, data):
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


# ❌ **Elimina un prodotto**
@handle_db_errors
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return False

    db.session.delete(product)
    db.session.commit()
    logging.info(f"🗑️ Prodotto '{product_id}' eliminato con successo.")
    return True


# 🔍 **Recupera prodotti per categoria**
@handle_db_errors
def get_products_by_category(category_id):
    products = Product.query.filter_by(category_id=category_id).all()
    return [product_to_dict(p) for p in products]


# 🔍 **Recupera prodotti per brand**
@handle_db_errors
def get_products_by_brand(brand_id):
    products = Product.query.filter_by(brand_id=brand_id).all()
    return [product_to_dict(p) for p in products]


# 🔍 **Cerca prodotti per nome**
@handle_db_errors
def search_products(query_text, shop_name):
    products = Product.query.filter(Product.name.ilike(f"%{query_text}%"), Product.shop_name == shop_name).all()
    return [product_to_dict(p) for p in products]


# 🔍 **Recupera prodotti per ID multipli**
@handle_db_errors
def get_products_by_ids(product_ids):
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    return [product_to_dict(p) for p in products]


# 🔍 **Recupera il primo prodotto di un negozio**
@handle_db_errors
def get_first_product_by_shop(shop_name):
    product = Product.query.filter_by(shop_name=shop_name).order_by(Product.id.asc()).first()
    return product_to_dict(product) if product else None


# 📌 **Helper per convertire un prodotto in dizionario**
def product_to_dict(product):
    return {col.name: getattr(product, col.name) for col in Product.__table__.columns} if product else None