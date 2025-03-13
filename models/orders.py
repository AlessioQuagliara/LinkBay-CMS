from models.database import db
from models.customers import Customer
from datetime import datetime
import logging
from functools import wraps

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per gli Ordini**
class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Nome del negozio
    order_number = db.Column(db.String(255), unique=True, nullable=False)  # 📌 Numero dell'ordine
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)  # 👤 Cliente che ha effettuato l'ordine
    total_amount = db.Column(db.Float, nullable=False, default=0.0)  # 💰 Totale dell'ordine
    status = db.Column(db.String(50), nullable=False, default="Draft")  # 🔄 Stato dell'ordine
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    # Relazione con gli articoli dell'ordine
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    @property
    def total_amount(self):
        """Calcola il totale dell'ordine sommando i subtotali degli OrderItems."""
        return sum(item.subtotal for item in self.order_items)

    def __repr__(self):
        return f"<Order {self.order_number} - {self.status}>"

# 🔹 **Modello per gli Articoli dell'Ordine**
class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)  # 🛒 Ordine associato
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)  # 🏷️ Prodotto
    quantity = db.Column(db.Integer, nullable=False, default=1)  # 🔢 Quantità acquistata
    price = db.Column(db.Float, nullable=False)  # 💰 Prezzo unitario
    subtotal = db.Column(db.Float, nullable=False)  # 💰 Totale parziale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di aggiunta

    # Relazione con il prodotto
    product = db.relationship('Product', backref='order_items', lazy=True)

    def __repr__(self):
        return f"<OrderItem {self.order_id} - {self.product_id}>"
    
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

# 🔍 **Recupera un ordine per ID**
@handle_db_errors
def get_order_by_id(order_id):
    orders = Order.query.get(order_id)
    return model_to_dict(orders) if orders else None

# ✅ **Crea un nuovo ordine**
@handle_db_errors
def create_order(data):
    new_order = Order(
        shop_name=data["shop_name"],
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
    orders = Order.query.get(order_id)
    if not orders:
        return False

    orders.status = status
    orders.total_amount = total_amount
    orders.updated_at = datetime.utcnow()
    db.session.commit()
    logging.info(f"✅ Stato ordine {order_id} aggiornato a {status}")
    return True

# ❌ **Elimina un ordine**
@handle_db_errors
def delete_order(order_id):
    orders = Order.query.get(order_id)
    if not orders:
        return False

    db.session.delete(orders)
    db.session.commit()
    logging.info(f"✅ Ordine {order_id} eliminato con successo")
    return True

# 📦 **Recupera tutti gli ordini per uno shop**
@handle_db_errors
def get_all_orders(shop_name):
    orders = Order.query.filter_by(shop_name=shop_name).order_by(Order.created_at.desc()).all()
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

@staticmethod
@handle_db_errors
def add_multiple_products_to_order(order_id, products):
        existing_items = OrderItem.query.filter(OrderItem.order_id == order_id).all()
        existing_items_dict = {item.product_id: item for item in existing_items}

        for product in products:
            product_id = product.get("product_id")
            quantity = product.get("quantity", 1)
            price = product.get("price", 0.0)

            if product_id in existing_items_dict:
                existing_items_dict[product_id].quantity += quantity
                existing_items_dict[product_id].subtotal = existing_items_dict[product_id].quantity * existing_items_dict[product_id].price
            else:
                new_item = OrderItem(
                    order_id=order_id,
                    product_id=product_id,
                    quantity=quantity,
                    price=price,
                    subtotal=quantity * price
                )
                db.session.add(new_item)

        db.session.commit()
        logging.info(f"✅ {len(products)} prodotti aggiunti/modificati per l'ordine {order_id}")
        return {'success': True, 'message': 'Products added/updated in order successfully.'}

# ❌ **Rimuove prodotti da un ordine**
@handle_db_errors
def remove_order_items(order_id, product_ids):
    OrderItem.query.filter(OrderItem.order_id == order_id, OrderItem.product_id.in_(product_ids)).delete()
    db.session.commit()
    logging.info(f"✅ Prodotti {product_ids} rimossi dall'ordine {order_id}")
    return True

# 🔄 **Aggiorna le quantità degli articoli in un ordine**
@handle_db_errors
def update_order_items_quantities(order_id, items):
    product_ids = [item["product_id"] for item in items]
    order_items = OrderItem.query.filter(
        OrderItem.order_id == order_id,
        OrderItem.product_id.in_(product_ids)
    ).all()

    for order_item in order_items:
        item_data = next((item for item in items if item["product_id"] == order_item.product_id), None)
        if item_data:
            order_item.quantity = item_data["quantity"]
            order_item.subtotal = item_data["quantity"] * order_item.price

    db.session.commit()
    logging.info(f"✅ Quantità aggiornate per l'ordine {order_id}")
    return True

# 📌 **Recupera i dati ordini con join ottimizzato**
@handle_db_errors
def get_orders_by_shop(shop_name):
    """
    Recupera gli ordini di un negozio con dettagli sul cliente e statistiche sui prodotti ordinati.
    """
    orders = (
        db.session.query(
            Order,
            Customer.first_name.label("customer_name"),
            Customer.last_name.label("customer_surname"),
            Customer.email.label("customer_email"),
            db.func.count(OrderItem.id).label("total_items"),
            db.func.coalesce(db.func.sum(OrderItem.quantity), 0).label("total_quantity")
        )
        .outerjoin(Customer, Order.customer_id == Customer.id)
        .outerjoin(OrderItem, Order.id == OrderItem.order_id)
        .filter(Order.shop_name == shop_name)
        .group_by(Order.id, Customer.first_name, Customer.last_name, Customer.email)
        .order_by(Order.created_at.desc())
        .all()
    )

    detailed_orders = [
        {
            "id": order.id,
            "order_number": order.order_number,
            "customer_name": customer_name or "Guest",
            "customer_surname": customer_surname or "Unknown",
            "customer_email": customer_email or "No Email",
            "status": order.status,
            "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "total_amount": round(order.total_amount, 2),
            "total_items": total_items or 0,
            "total_quantity": total_quantity or 0,
        }
        for order, customer_name, customer_surname, customer_email, total_items, total_quantity in orders
    ]

    return detailed_orders