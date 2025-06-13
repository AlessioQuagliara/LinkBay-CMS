from models.database import db
from datetime import datetime
import logging
from .warehouse import Inventory
from functools import wraps
from sqlalchemy import UniqueConstraint, Index

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


# 🔹 **Modello per i Prodotti**
class Product(db.Model):
    __tablename__ = "products"

    id                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shop_id           = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)
    name              = db.Column(db.String(255), nullable=False)
    description       = db.Column(db.Text, nullable=True)
    sku               = db.Column(db.String(255), nullable=True)
    ean_code          = db.Column(db.String(255), nullable=True)
    short_description = db.Column(db.Text, nullable=True)
    price             = db.Column(db.Numeric(10,2), nullable=False)
    discount_price    = db.Column(db.Numeric(10,2), nullable=True)


    @property
    def total_stock(self):
        return db.session.query(
            db.func.sum(Inventory.quantity)
        ).filter_by(product_id=self.id).scalar() or 0
    slug              = db.Column(db.String(255), nullable=False)
    is_active         = db.Column(db.Boolean, default=True)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at        = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id       = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    is_digital        = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint('shop_id', 'slug', name='ux_products_shop_slug'),
        Index('ix_products_shop_name', 'shop_id', 'name'),
        db.Index('ix_products_sku', 'sku'),
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
    inventories = db.relationship("Inventory", backref="product", cascade="all, delete-orphan")

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

    def __repr__(self):
        return f"<Variant {self.id} of Product {self.product_id}: SKU={self.sku}>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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
    
# 🔄 **CRUD Functions for Category**
@handle_db_errors
def create_category(shop_id, name, parent_id=None):
    cat = Category(shop_id=shop_id, name=name, parent_id=parent_id)
    db.session.add(cat)
    db.session.commit()
    logging.info(f"✅ Categoria '{name}' creata per Shop ID {shop_id}")
    return cat.id

@handle_db_errors
def get_all_categories(shop_id):
    return Category.query.filter_by(shop_id=shop_id).all()

@handle_db_errors
def get_category_by_id(category_id):
    return Category.query.get(category_id)

@handle_db_errors
def update_category(category_id, **kwargs):
    cat = Category.query.get(category_id)
    if not cat:
        return None
    for key, value in kwargs.items():
        if hasattr(cat, key) and value is not None:
            setattr(cat, key, value)
    db.session.commit()
    logging.info(f"✅ Categoria ID {category_id} aggiornata")
    return cat

@handle_db_errors
def delete_category(category_id):
    cat = Category.query.get(category_id)
    if not cat:
        return False
    db.session.delete(cat)
    db.session.commit()
    logging.info(f"🗑️ Categoria ID {category_id} eliminata")
    return True

@handle_db_errors
def get_subcategories(parent_id):
    return Category.query.filter_by(parent_id=parent_id).all()


# 🔄 **CRUD Functions for Collection**
@handle_db_errors
def create_collection(shop_id, name, slug, description=None, image_url=None, is_active=True):
    col = Collection(
        shop_id=shop_id, name=name, slug=slug,
        description=description, image_url=image_url, is_active=is_active
    )
    db.session.add(col)
    db.session.commit()
    logging.info(f"✅ Collezione '{name}' creata per Shop ID {shop_id}")
    return col.id

@handle_db_errors
def get_all_collections(shop_id):
    return Collection.query.filter_by(shop_id=shop_id).all()

@handle_db_errors
def get_collection_by_slug(shop_id, slug):
    return Collection.query.filter_by(shop_id=shop_id, slug=slug).first()

@handle_db_errors
def update_collection(collection_id, **kwargs):
    col = Collection.query.get(collection_id)
    if not col:
        return None
    for key, value in kwargs.items():
        if hasattr(col, key) and value is not None:
            setattr(col, key, value)
    db.session.commit()
    logging.info(f"✅ Collezione ID {collection_id} aggiornata")
    return col

@handle_db_errors
def delete_collection(collection_id):
    col = Collection.query.get(collection_id)
    if not col:
        return False
    db.session.delete(col)
    db.session.commit()
    logging.info(f"🗑️ Collezione ID {collection_id} eliminata")
    return True


# 🔄 **CRUD Functions for CollectionImage**
@handle_db_errors
def create_collection_image(collection_id, url, is_main=False):
    img = CollectionImage(collection_id=collection_id, url=url, is_main=is_main)
    db.session.add(img)
    db.session.commit()
    logging.info(f"✅ Immagine aggiunta a Collezione ID {collection_id}")
    return img.id

@handle_db_errors
def get_collection_images(collection_id):
    return CollectionImage.query.filter_by(collection_id=collection_id).all()

@handle_db_errors
def delete_collection_image(image_id):
    img = CollectionImage.query.get(image_id)
    if not img:
        return False
    db.session.delete(img)
    db.session.commit()
    logging.info(f"🗑️ Immagine ID {image_id} eliminata")
    return True


# 🔄 **CRUD Functions for CollectionProduct**
@handle_db_errors
def add_product_to_collection(collection_id, product_id):
    rel = CollectionProduct(collection_id=collection_id, product_id=product_id)
    db.session.add(rel)
    db.session.commit()
    logging.info(f"✅ Prodotto {product_id} aggiunto a Collezione ID {collection_id}")
    return True

@handle_db_errors
def remove_product_from_collection(collection_id, product_id):
    CollectionProduct.query.filter_by(collection_id=collection_id, product_id=product_id).delete()
    db.session.commit()
    logging.info(f"🗑️ Prodotto {product_id} rimosso da Collezione ID {collection_id}")
    return True

@handle_db_errors
def get_products_in_collection(collection_id):
    rels = CollectionProduct.query.filter_by(collection_id=collection_id).all()
    return [r.product_id for r in rels]


# 🔄 **CRUD Functions for Product**
@handle_db_errors
def create_product(shop_id, name, price, sku, slug, **kwargs):
    prod = Product(
        shop_id=shop_id, name=name, price=price, sku=sku, slug=slug,
        **{k: kwargs.get(k) for k in [
            'description', 'short_description', 'discount_price',
            'stock_quantity', 'ean_code', 'category_id', 'brand_id',
            'weight', 'dimensions', 'color', 'material', 'is_active'
        ] if kwargs.get(k) is not None}
    )
    db.session.add(prod)
    db.session.commit()
    logging.info(f"✅ Prodotto '{name}' creato per Shop ID {shop_id}")
    return prod.id

@handle_db_errors
def get_all_products(shop_id):
    return Product.query.filter_by(shop_id=shop_id).all()

@handle_db_errors
def get_product_by_slug(shop_id, slug):
    return Product.query.filter_by(shop_id=shop_id, slug=slug).first()

@handle_db_errors
def update_product(product_id, **kwargs):
    prod = Product.query.get(product_id)
    if not prod:
        return None
    for key, value in kwargs.items():
        if hasattr(prod, key) and value is not None:
            setattr(prod, key, value)
    db.session.commit()
    logging.info(f"✅ Prodotto ID {product_id} aggiornato")
    return prod

@handle_db_errors
def delete_product(product_id):
    prod = Product.query.get(product_id)
    if not prod:
        return False
    db.session.delete(prod)
    db.session.commit()
    logging.info(f"🗑️ Prodotto ID {product_id} eliminato")
    return True

@handle_db_errors
def get_products_by_category(shop_id, category_id):
    return Product.query.filter_by(shop_id=shop_id, category_id=category_id).all()

@handle_db_errors
def get_products_by_brand(shop_id, brand_id):
    return Product.query.filter_by(shop_id=shop_id, brand_id=brand_id).all()

@handle_db_errors
def search_products(shop_id, query_text):
    return Product.query.filter(
        Product.shop_id == shop_id,
        Product.name.ilike(f"%{query_text}%")
    ).all()

@handle_db_errors
def get_products_by_ids(product_ids):
    return Product.query.filter(Product.id.in_(product_ids)).all()

@handle_db_errors
def get_first_product_by_shop(shop_id):
    return Product.query.filter_by(shop_id=shop_id).order_by(Product.id.asc()).first()


# 🔄 **CRUD Functions for ProductVariant**
@handle_db_errors
def create_variant(product_id, sku, **kwargs):
    var = ProductVariant(product_id=product_id, sku=sku, **{
        k: kwargs.get(k) for k in ['ean_code','price_modifier','stock_quantity','is_default']
        if kwargs.get(k) is not None
    })
    db.session.add(var)
    db.session.commit()
    logging.info(f"✅ Variante SKU '{sku}' creata per Prodotto ID {product_id}")
    return var.id

@handle_db_errors
def get_variants_by_product(product_id):
    return ProductVariant.query.filter_by(product_id=product_id).all()

@handle_db_errors
def update_variant(variant_id, **kwargs):
    var = ProductVariant.query.get(variant_id)
    if not var:
        return None
    for key, value in kwargs.items():
        if hasattr(var, key) and value is not None:
            setattr(var, key, value)
    db.session.commit()
    logging.info(f"✅ Variante ID {variant_id} aggiornata")
    return var

@handle_db_errors
def delete_variant(variant_id):
    var = ProductVariant.query.get(variant_id)
    if not var:
        return False
    db.session.delete(var)
    db.session.commit()
    logging.info(f"🗑️ Variante ID {variant_id} eliminata")
    return True


# 🔄 **CRUD Functions for ProductImage**
@handle_db_errors
def create_product_image(product_id, url, is_main=False):
    img = ProductImage(product_id=product_id, url=url, is_main=is_main)
    db.session.add(img)
    db.session.commit()
    logging.info(f"✅ Immagine '{url}' aggiunta a Prodotto ID {product_id}")
    return img.id

@handle_db_errors
def get_images_by_product(product_id):
    return ProductImage.query.filter_by(product_id=product_id).all()

@handle_db_errors
def update_product_image(image_id, **kwargs):
    img = ProductImage.query.get(image_id)
    if not img:
        return None
    for key, value in kwargs.items():
        if hasattr(img, key) and value is not None:
            setattr(img, key, value)
    db.session.commit()
    logging.info(f"✅ Immagine ID {image_id} aggiornata")
    return img

@handle_db_errors
def delete_product_image(image_id):
    img = ProductImage.query.get(image_id)
    if not img:
        return False
    db.session.delete(img)
    db.session.commit()
    logging.info(f"🗑️ Immagine ID {image_id} eliminata")
    return True
    inventories = db.relationship("Inventory", backref="variant", cascade="all, delete-orphan")

    @property
    def total_stock(self):
        return db.session.query(
            db.func.sum(Inventory.quantity)
        ).filter_by(variant_id=self.id).scalar() or 0