from models.database import db
from datetime import datetime
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

# 🔹 **Modello per i Metodi di Pagamento**
class PaymentMethod(db.Model):
    __tablename__ = "payment_methods"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Nome del negozio
    method_name = db.Column(db.String(255), nullable=False)  # 💳 Nome del metodo di pagamento
    api_key = db.Column(db.String(512), nullable=False)  # 🔑 API Key
    api_secret = db.Column(db.String(512), nullable=False)  # 🔒 API Secret
    extra_info = db.Column(db.Text, nullable=True)  # ℹ️ Informazioni extra
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    def __repr__(self):
        return f"<PaymentMethod {self.method_name} - {self.shop_name}>"

# ✅ **Crea un nuovo metodo di pagamento**
def create_payment_method(data):
    try:
        new_method = PaymentMethod(
            shop_name=data["shop_name"],
            method_name=data["method_name"],
            api_key=data["api_key"],
            api_secret=data["api_secret"],
            extra_info=data.get("extra_info"),
        )
        db.session.add(new_method)
        db.session.commit()
        logging.info(f"✅ Metodo di pagamento '{data['method_name']}' creato con successo")
        return new_method.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione del metodo di pagamento: {e}")
        return None

# 🔄 **Aggiorna un metodo di pagamento**
def update_payment_method(method_id, shop_name, data):
    try:
        method = PaymentMethod.query.filter_by(id=method_id, shop_name=shop_name).first()
        if not method:
            return False

        method.api_key = data.get("api_key", method.api_key)
        method.api_secret = data.get("api_secret", method.api_secret)
        method.extra_info = data.get("extra_info", method.extra_info)
        method.updated_at = datetime.utcnow()

        db.session.commit()
        logging.info(f"✅ Metodo di pagamento {method_id} aggiornato con successo")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento del metodo di pagamento {method_id}: {e}")
        return False

# 🔍 **Recupera tutti i metodi di pagamento per un negozio**
def get_all_payment_methods(shop_name):
    try:
        methods = PaymentMethod.query.filter_by(shop_name=shop_name).order_by(PaymentMethod.created_at.desc()).all()
        return [payment_method_to_dict(m) for m in methods]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei metodi di pagamento per {shop_name}: {e}")
        return []

# ❌ **Elimina un metodo di pagamento**
def delete_payment_method(method_id, shop_name):
    try:
        method = PaymentMethod.query.filter_by(id=method_id, shop_name=shop_name).first()
        if not method:
            return False

        db.session.delete(method)
        db.session.commit()
        logging.info(f"✅ Metodo di pagamento {method_id} eliminato con successo")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione del metodo di pagamento {method_id}: {e}")
        return False

# 🔍 **Recupera un metodo di pagamento per ID**
def get_payment_method_by_id(method_id, shop_name):
    try:
        method = PaymentMethod.query.filter_by(id=method_id, shop_name=shop_name).first()
        return payment_method_to_dict(method) if method else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del metodo di pagamento {method_id}: {e}")
        return None

# 🔍 **Recupera un metodo di pagamento per nome e negozio**
def get_payment_method(shop_name, method_name):
    try:
        method = PaymentMethod.query.filter_by(shop_name=shop_name, method_name=method_name).first()
        return payment_method_to_dict(method) if method else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del metodo di pagamento '{method_name}' per {shop_name}: {e}")
        return None

# 📌 **Helper per convertire un metodo di pagamento in dizionario**
def payment_method_to_dict(method):
    return {col.name: getattr(method, col.name) for col in PaymentMethod.__table__.columns} if method else None