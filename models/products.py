from models.database import db
from datetime import datetime
import logging
from functools import wraps
from sqlalchemy import UniqueConstraint, Index


# Evita import circolari per Inventory
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.warehouse import Inventory

# Ensure mappers are configured after all classes are defined
from sqlalchemy.orm import configure_mappers
configure_mappers()

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔄 Decoratore per la gestione degli errori del database
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


# 🔹 **Modello per le Categorie**
class Category(db.Model):
    __tablename__ = "categories"

    id       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name     = db.Column(db.String(255), nullable=False)
    shop_id  = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)
    parent_id= db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    __table_args__ = (
        UniqueConstraint('shop_id', 'name', name='ux_categories_shop_name'),
    )

    subcategories = db.relationship(
        "Category",
        backref=db.backref("parent", remote_side=[id]),
        lazy=True
    )

    def __repr__(self):
        return f"<Category {self.name} (ID: {self.id})>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# 🔹 **Modello per le Collezioni**
class Collection(db.Model):
    __tablename__ = "collections"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    shop_id    = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)  
    name       = db.Column(db.String(255), nullable=False)  
    slug       = db.Column(db.String(255), nullable=False)  
    description= db.Column(db.String(1024), nullable=True)  
    image_url  = db.Column(db.String(512), nullable=True)  
    is_active  = db.Column(db.Boolean, default=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  

    __table_args__ = (
        UniqueConstraint('shop_id', 'slug', name='ux_collections_shop_slug'),
    )

    images   = db.relationship("CollectionImage",   backref="collection", cascade="all, delete-orphan")
    products = db.relationship(
        "Product",
        secondary="collection_products",
        back_populates="collections",
        lazy="dynamic"
    )

    def __repr__(self):
        return f"<Collection {self.name} (ID: {self.id})>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# 📸 **Modello per le Immagini delle Collezioni**
class CollectionImage(db.Model):
    __tablename__ = "collection_images"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    collection_id = db.Column(db.Integer, db.ForeignKey("collections.id"), nullable=False)  
    url           = db.Column(db.String(512), nullable=False)  
    is_main       = db.Column(db.Boolean, default=False)  
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)  
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  

    __table_args__ = (
        UniqueConstraint('collection_id', 'url', name='ux_coll_images_coll_url'),
        Index('ix_coll_images_coll', 'collection_id'),
    )

    def __repr__(self):
        return f"<CollectionImage {self.id} for Collection {self.collection_id}>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# 🛒 **Tabella di associazione Collezione–Prodotto**
class CollectionProduct(db.Model):
    __tablename__ = "collection_products"

    collection_id = db.Column(db.Integer, db.ForeignKey("collections.id"), primary_key=True)
    product_id    = db.Column(db.Integer, db.ForeignKey("products.id"),    primary_key=True)

    def __repr__(self):
        return f"<CollectionProduct C:{self.collection_id} P:{self.product_id}>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


#
# 🔹 **Modello per le Immagini dei Prodotti**
class ProductImage(db.Model):
    __tablename__ = "product_images"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    url        = db.Column(db.String(512), nullable=False)
    is_main    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('product_id', 'url', name='ux_product_images_prod_url'),
        Index('ix_product_images_prod', 'product_id'),
    )

    product = db.relationship("Product", back_populates="images")

    def __repr__(self):
        return f"<ProductImage {self.id} for Product {self.product_id}>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# 🔹 **Modello per i Prodotti**
class Product(db.Model):
    __tablename__ = "products"

    id                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shop_id           = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)
    name              = db.Column(db.String(255), nullable=False)
    description       = db.Column(db.Text, nullable=True)
    short_description = db.Column(db.Text, nullable=True)
    price             = db.Column(db.Numeric(10,2), nullable=False)
    discount_price    = db.Column(db.Numeric(10,2), nullable=True)

    slug              = db.Column(db.String(255), nullable=False)
    is_active         = db.Column(db.Boolean, default=True)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at        = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id       = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    is_digital        = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint('shop_id', 'slug', name='ux_products_shop_slug'),
        Index('ix_products_shop_name', 'shop_id', 'name'),
    )

    variants    = db.relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    images      = db.relationship("ProductImage",   back_populates="product", cascade="all, delete-orphan")
    collections = db.relationship(
        "Collection",
        secondary="collection_products",
        back_populates="products",
        lazy="dynamic"
    )
    category    = db.relationship("Category", backref="products")

    def __repr__(self):
        return f"<Product {self.id} – {self.name}>"

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data['collections'] = [col.to_dict() for col in self.collections]
        data['variants']    = [v.to_dict()   for v in self.variants]
        return data


# 🔹 **Modello per le Varianti di Prodotto**
class ProductVariant(db.Model):
    __tablename__ = "product_variants"

    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id     = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    name           = db.Column(db.String(255), nullable=False)
    sku            = db.Column(db.String(255), nullable=False)
    ean_code       = db.Column(db.String(255), nullable=True)
    price_modifier = db.Column(db.Numeric(10,2), default=0)
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    is_default     = db.Column(db.Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('product_id', 'sku', name='ux_variants_prod_sku'),
        Index('ix_variants_product', 'product_id'),
    )

    product = db.relationship("Product", back_populates="variants")

    inventories = db.relationship("Inventory", back_populates="variant", cascade="all, delete-orphan")

    @property
    def total_stock(self):
        return db.session.query(
            db.func.sum(Inventory.quantity)
        ).filter_by(variant_id=self.id).scalar() or 0

    def __repr__(self):
        return f"<Variant {self.id} of Product {self.product_id}: SKU={self.sku}>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    
    

# ✅ Funzioni CRUD per Category
@handle_db_errors
def create_category(name, shop_id, parent_id=None):
    category = Category(name=name, shop_id=shop_id, parent_id=parent_id)
    db.session.add(category)
    db.session.commit()
    return category

def get_category_by_id(category_id):
    return Category.query.get(category_id)

@handle_db_errors
def update_category(category, name=None, parent_id=None):
    if name: category.name = name
    if parent_id is not None: category.parent_id = parent_id
    db.session.commit()
    return category

@handle_db_errors
def delete_category(category):
    db.session.delete(category)
    db.session.commit()


# ✅ Funzioni CRUD per Collection
@handle_db_errors
def create_collection(shop_id, name, slug, description=None, image_url=None):
    collection = Collection(
        shop_id=shop_id, name=name, slug=slug,
        description=description, image_url=image_url
    )
    db.session.add(collection)
    db.session.commit()
    return collection

def get_collection_by_id(collection_id):
    return Collection.query.get(collection_id)

@handle_db_errors
def update_collection(collection, name=None, slug=None, description=None, image_url=None, is_active=None):
    if name: collection.name = name
    if slug: collection.slug = slug
    if description is not None: collection.description = description
    if image_url is not None: collection.image_url = image_url
    if is_active is not None: collection.is_active = is_active
    db.session.commit()
    return collection

@handle_db_errors
def delete_collection(collection):
    db.session.delete(collection)
    db.session.commit()


# ✅ Funzioni CRUD per CollectionImage
@handle_db_errors
def create_collection_image(collection_id, url, is_main=False):
    image = CollectionImage(collection_id=collection_id, url=url, is_main=is_main)
    db.session.add(image)
    db.session.commit()
    return image

@handle_db_errors
def delete_collection_image(image):
    db.session.delete(image)
    db.session.commit()


# ✅ Funzioni CRUD per CollectionProduct
@handle_db_errors
def link_product_to_collection(product_id, collection_id):
    link = CollectionProduct(product_id=product_id, collection_id=collection_id)
    db.session.add(link)
    db.session.commit()
    return link

@handle_db_errors
def unlink_product_from_collection(product_id, collection_id):
    link = CollectionProduct.query.filter_by(product_id=product_id, collection_id=collection_id).first()
    if link:
        db.session.delete(link)
        db.session.commit()


# ✅ Funzioni CRUD per ProductImage
@handle_db_errors
def create_product_image(product_id, url, is_main=False):
    image = ProductImage(product_id=product_id, url=url, is_main=is_main)
    db.session.add(image)
    db.session.commit()
    return image

@handle_db_errors
def delete_product_image(image):
    db.session.delete(image)
    db.session.commit()


# ✅ Funzioni CRUD per Product
@handle_db_errors
def create_product(shop_id, name, price, slug, description=None, short_description=None, discount_price=None, category_id=None, is_digital=False):
    product = Product(
        shop_id=shop_id, name=name, price=price, slug=slug,
        description=description, short_description=short_description,
        discount_price=discount_price, category_id=category_id, is_digital=is_digital
    )
    db.session.add(product)
    db.session.commit()
    return product

def get_product_by_id(product_id):
    return Product.query.get(product_id)

@handle_db_errors
def update_product(product, **kwargs):
    for key, value in kwargs.items():
        if hasattr(product, key) and value is not None:
            setattr(product, key, value)
    db.session.commit()
    return product

@handle_db_errors
def delete_product(product):
    db.session.delete(product)
    db.session.commit()


# ✅ Funzioni CRUD per ProductVariant
@handle_db_errors
def create_variant(product_id, name, sku, price_modifier=0, ean_code=None, stock_quantity=0, is_default=False):
    variant = ProductVariant(
        product_id=product_id, name=name, sku=sku,
        price_modifier=price_modifier, ean_code=ean_code,
        stock_quantity=stock_quantity, is_default=is_default
    )
    db.session.add(variant)
    db.session.commit()
    return variant

def get_variant_by_id(variant_id):
    return ProductVariant.query.get(variant_id)

@handle_db_errors
def update_variant(variant, **kwargs):
    for key, value in kwargs.items():
        if hasattr(variant, key) and value is not None:
            setattr(variant, key, value)
    db.session.commit()
    return variant

@handle_db_errors
def delete_variant(variant):
    db.session.delete(variant)
    db.session.commit()
