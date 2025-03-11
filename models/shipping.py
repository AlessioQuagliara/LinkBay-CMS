from models.database import db
from datetime import datetime
import logging
from functools import wraps

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per le Spedizioni**
class Shipping(db.Model):
    __tablename__ = "shipping"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Nome dello shop
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)  # 🛒 ID dell'ordine
    shipping_method = db.Column(db.String(255), nullable=False)  # 🚚 Metodo di spedizione
    tracking_number = db.Column(db.String(255), nullable=True)  # 🔍 Numero di tracking
    carrier_name = db.Column(db.String(255), nullable=True)  # 📦 Nome del corriere
    estimated_delivery_date = db.Column(db.DateTime, nullable=True)  # 📅 Data di consegna stimata
    delivery_status = db.Column(db.String(50), nullable=False, default="pending")  # ✅ Stato della spedizione
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Aggiornamento

    def __repr__(self):
        return f"<Shipping {self.id} - {self.order_id} - {self.delivery_status}>"

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


# 🔍 **Recupera i dettagli di spedizione per un ordine**
@handle_db_errors
def get_shipping_by_order_id(order_id):
    shipping = Shipping.query.filter_by(order_id=order_id).first()
    return shipping_to_dict(shipping) if shipping else None


# 🔍 **Recupera tutte le spedizioni per un negozio**
@handle_db_errors
def get_all_shippings(shop_name):
    shippings = Shipping.query.filter_by(shop_name=shop_name).order_by(Shipping.created_at.desc()).all()
    return [shipping_to_dict(s) for s in shippings]


# ✅ **Aggiunge o aggiorna una spedizione**
@handle_db_errors
def upsert_shipping(data):
    shipping = Shipping.query.filter_by(order_id=data["order_id"]).first()

    if shipping:
        # Aggiorna la spedizione esistente
        for key, value in data.items():
            if hasattr(shipping, key) and value is not None:
                setattr(shipping, key, value)

        shipping.updated_at = datetime.utcnow()
        logging.info(f"🔄 Spedizione per ordine {data['order_id']} aggiornata.")
    else:
        # Crea una nuova spedizione
        shipping = Shipping(
            shop_name=data["shop_name"],
            order_id=data["order_id"],
            shipping_method=data["shipping_method"],
            tracking_number=data.get("tracking_number"),
            carrier_name=data.get("carrier_name"),
            estimated_delivery_date=data.get("estimated_delivery_date"),
            delivery_status=data.get("delivery_status", "pending"),
        )
        db.session.add(shipping)
        logging.info(f"✅ Nuova spedizione per ordine {data['order_id']} creata.")

    db.session.commit()
    return shipping.id


# 🔄 **Aggiorna lo stato della spedizione**
@handle_db_errors
def update_shipping_status(order_id, status):
    shipping = Shipping.query.filter_by(order_id=order_id).first()
    if not shipping:
        return False

    shipping.delivery_status = status
    shipping.updated_at = datetime.utcnow()
    db.session.commit()
    logging.info(f"✅ Stato della spedizione per ordine {order_id} aggiornato a '{status}'.")
    return True


# 📌 **Helper per convertire una spedizione in dizionario**
def shipping_to_dict(shipping):
    return {col.name: getattr(shipping, col.name) for col in Shipping.__table__.columns} if shipping else None