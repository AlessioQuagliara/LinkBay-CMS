from models.database import db
from models.customers import Customer
from models.products import Product
from datetime import datetime
import logging
from functools import wraps
from sqlalchemy import UniqueConstraint

# Configurazione del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per gli Ordini**
class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)
    order_number = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(50), nullable=False, default="Draft")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('shop_id', 'order_number', name='ux_orders_shop_order_number'),
    )

    def __repr__(self):
        return f"<Order {self.order_number} - {self.status}>"

# 🔹 **Modello per gli Articoli dell'Ordine**
class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='order_items', lazy=True)

    def __repr__(self):
        return f"<OrderItem {self.order_id} - {self.product_id}>"

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

# 🔍 **Recupera un ordine per ID**
@handle_db_errors
def get_order_by_id(order_id):
    order = Order.query.get(order_id)
    return model_to_dict(order) if order else None

# ✅ **Crea un nuovo ordine**
@handle_db_errors
def create_order(data):
    new_order = Order(
        shop_id=data["shop_id"],
        order_number=data["order_number"],
        customer_id=data.get("customer_id"),
        total_amount=data.get("total_amount", 0.0),
        status=data.get("status", "Draft"),
    )
    db.session.add(new_order)
    db.session.commit()
    logging.info(f"✅ Ordine '{new_order.order_number}' creato con successo")
    return new_order.id

# 🔄 **Aggiorna lo stato di un ordine**
@handle_db_errors
def update_order(order_id, status, total_amount):
    order = Order.query.get(order_id)
    if not order:
        return False

    order.status = status
    order.total_amount = total_amount
    order.updated_at = datetime.utcnow()
    db.session.commit()
    logging.info(f"✅ Stato ordine {order_id} aggiornato a {status}")
    return True

# ❌ **Elimina un ordine**
@handle_db_errors
def delete_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return False

    db.session.delete(order)
    db.session.commit()
    logging.info(f"✅ Ordine {order_id} eliminato con successo")
    return True

# 📦 **Recupera tutti gli ordini per uno shop**
@handle_db_errors
def get_all_orders(shop_id):
    orders = Order.query.filter_by(shop_id=shop_id).order_by(Order.created_at.desc()).all()
    return [model_to_dict(o) for o in orders]

# 🛒 **Recupera i prodotti di un ordine**
@handle_db_errors
def get_order_items(order_id):
    items = OrderItem.query.filter_by(order_id=order_id).all()
    return [model_to_dict(i) for i in items]

# 🛍️ **Aggiungi un prodotto a un ordine**
@handle_db_errors
def add_product_to_order(order_id, product_id, quantity=1, price=0):
    subtotal = price * quantity
    new_item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        price=price,
        subtotal=subtotal,
    )
    db.session.add(new_item)
    db.session.commit()
    logging.info(f"✅ Prodotto {product_id} aggiunto all'ordine {order_id}")
    return True