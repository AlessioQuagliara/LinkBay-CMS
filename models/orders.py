from models.database import db
from datetime import datetime
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

    def __repr__(self):
        return f"<OrderItem {self.order_id} - {self.product_id}>"

# 🔍 **Recupera un ordine per ID**
def get_order_by_id(order_id):
    try:
        order = Order.query.get(order_id)
        return order_to_dict(order) if order else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dell'ordine {order_id}: {e}")
        return None

# ✅ **Crea un nuovo ordine**
def create_order(data):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione dell'ordine: {e}")
        return None

# 🔄 **Aggiorna lo stato di un ordine**
def update_order(order_id, status, total_amount):
    try:
        order = Order.query.get(order_id)
        if not order:
            return False

        order.status = status
        order.total_amount = total_amount
        order.updated_at = datetime.utcnow()
        db.session.commit()
        logging.info(f"✅ Stato ordine {order_id} aggiornato a {status}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento dello stato dell'ordine {order_id}: {e}")
        return False

# ❌ **Elimina un ordine**
def delete_order(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return False

        db.session.delete(order)
        db.session.commit()
        logging.info(f"✅ Ordine {order_id} eliminato con successo")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione dell'ordine {order_id}: {e}")
        return False

# 📦 **Recupera tutti gli ordini per uno shop**
def get_all_orders(shop_name):
    try:
        orders = Order.query.filter_by(shop_name=shop_name).order_by(Order.created_at.desc()).all()
        return [order_to_dict(o) for o in orders]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero degli ordini per {shop_name}: {e}")
        return []

# 🛒 **Recupera i prodotti di un ordine**
def get_order_items(order_id):
    try:
        items = OrderItem.query.filter_by(order_id=order_id).all()
        return [order_item_to_dict(i) for i in items]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero degli articoli per l'ordine {order_id}: {e}")
        return []

# 🛍️ **Aggiungi un prodotto a un ordine**
def add_product_to_order(order_id, product_id, quantity=1, price=0):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiunta del prodotto {product_id} all'ordine {order_id}: {e}")
        return False

# ❌ **Rimuove prodotti da un ordine**
def remove_order_items(order_id, product_ids):
    try:
        OrderItem.query.filter(OrderItem.order_id == order_id, OrderItem.product_id.in_(product_ids)).delete()
        db.session.commit()
        logging.info(f"✅ Prodotti {product_ids} rimossi dall'ordine {order_id}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella rimozione dei prodotti da ordine {order_id}: {e}")
        return False

# 🔄 **Aggiorna le quantità degli articoli in un ordine**
def update_order_items_quantities(order_id, items):
    try:
        for item in items:
            order_item = OrderItem.query.filter_by(order_id=order_id, product_id=item["product_id"]).first()
            if order_item:
                order_item.quantity = item["quantity"]
                order_item.subtotal = item["quantity"] * order_item.price
        db.session.commit()
        logging.info(f"✅ Quantità aggiornate per l'ordine {order_id}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento delle quantità per l'ordine {order_id}: {e}")
        return False

# 📌 **Helper per convertire un ordine in dizionario**
def order_to_dict(order):
    return {
        "id": order.id,
        "shop_name": order.shop_name,
        "order_number": order.order_number,
        "customer_id": order.customer_id,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }

# 📌 **Helper per convertire un articolo dell'ordine in dizionario**
def order_item_to_dict(item):
    return {
        "id": item.id,
        "order_id": item.order_id,
        "product_id": item.product_id,
        "quantity": item.quantity,
        "price": item.price,
        "subtotal": item.subtotal,
        "created_at": item.created_at,
    }