from models.database import db
from datetime import datetime
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

# 🔹 **Modello per i Metodi di Spedizione**
class ShippingMethod(db.Model):
    __tablename__ = "shipping_methods"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Nome del negozio
    name = db.Column(db.String(255), nullable=False)  # 📦 Nome del metodo di spedizione
    description = db.Column(db.Text, nullable=True)  # ℹ️ Descrizione del metodo di spedizione
    country = db.Column(db.String(100), nullable=True)  # 🌍 Paese
    region = db.Column(db.String(100), nullable=True)  # 📍 Regione
    cost = db.Column(db.Float, nullable=False)  # 💰 Costo della spedizione
    estimated_delivery_time = db.Column(db.String(100), nullable=True)  # ⏳ Tempo di consegna stimato
    is_active = db.Column(db.Boolean, default=True)  # ✅ Stato attivo/inattivo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Data di aggiornamento

    def __repr__(self):
        return f"<ShippingMethod {self.id} - {self.name} ({self.shop_name})>"

# ✅ **Crea un nuovo metodo di spedizione**
def create_shipping_method(data):
    try:
        new_shipping = ShippingMethod(
            shop_name=data["shop_name"],
            name=data["name"],
            description=data.get("description"),
            country=data.get("country"),
            region=data.get("region"),
            cost=data["cost"],
            estimated_delivery_time=data.get("estimated_delivery_time"),
            is_active=data.get("is_active", True),
        )
        db.session.add(new_shipping)
        db.session.commit()
        logging.info(f"✅ Metodo di spedizione '{data['name']}' creato per '{data['shop_name']}'.")
        return new_shipping.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione del metodo di spedizione: {e}")
        return None

# 🔍 **Recupera tutti i metodi di spedizione attivi per un negozio**
def get_all_shipping_methods(shop_name):
    try:
        methods = ShippingMethod.query.filter_by(shop_name=shop_name, is_active=True).order_by(ShippingMethod.created_at.desc()).all()
        return [shipping_method_to_dict(m) for m in methods]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei metodi di spedizione per '{shop_name}': {e}")
        return []

# 🔄 **Aggiorna un metodo di spedizione**
def update_shipping_method(method_id, shop_name, data):
    try:
        shipping = ShippingMethod.query.filter_by(id=method_id, shop_name=shop_name).first()
        if not shipping:
            return False

        for key, value in data.items():
            if hasattr(shipping, key) and value is not None:
                setattr(shipping, key, value)

        shipping.updated_at = datetime.utcnow()
        db.session.commit()
        logging.info(f"🔄 Metodo di spedizione {method_id} aggiornato per '{shop_name}'.")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento del metodo di spedizione: {e}")
        return False

# ❌ **Elimina un metodo di spedizione**
def delete_shipping_method(shipping_id, shop_name):
    try:
        shipping = ShippingMethod.query.filter_by(id=shipping_id, shop_name=shop_name).first()
        if not shipping:
            return False

        db.session.delete(shipping)
        db.session.commit()
        logging.info(f"❌ Metodo di spedizione {shipping_id} eliminato per '{shop_name}'.")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione del metodo di spedizione: {e}")
        return False

# 🔍 **Recupera un metodo di spedizione per ID**
def get_shipping_method_by_id(shipping_id, shop_name):
    try:
        shipping = ShippingMethod.query.filter_by(id=shipping_id, shop_name=shop_name).first()
        return shipping_method_to_dict(shipping) if shipping else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del metodo di spedizione ID {shipping_id}: {e}")
        return None

# 📌 **Helper per convertire un metodo di spedizione in dizionario**
def shipping_method_to_dict(shipping):
    return {col.name: getattr(shipping, col.name) for col in ShippingMethod.__table__.columns} if shipping else None