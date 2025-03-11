from models.database import db
import logging
from functools import wraps
from datetime import datetime

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# ✅ **Crea un nuovo metodo di pagamento**
@handle_db_errors
def create_payment_method(data):
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

# 🔄 **Aggiorna un metodo di pagamento**
@handle_db_errors
def update_payment_method(method_id, shop_name, data):
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

# 🔍 **Recupera tutti i metodi di pagamento per un negozio**
@handle_db_errors
def get_all_payment_methods(shop_name):
    methods = PaymentMethod.query.filter_by(shop_name=shop_name).order_by(PaymentMethod.created_at.desc()).all()
    return [model_to_dict(m) for m in methods]

# ❌ **Elimina un metodo di pagamento**
@handle_db_errors
def delete_payment_method(method_id, shop_name):
    method = PaymentMethod.query.filter_by(id=method_id, shop_name=shop_name).first()
    if not method:
        return False

    db.session.delete(method)
    db.session.commit()
    logging.info(f"✅ Metodo di pagamento {method_id} eliminato con successo")
    return True

# 🔍 **Recupera un metodo di pagamento per ID**
@handle_db_errors
def get_payment_method_by_id(method_id, shop_name):
    method = PaymentMethod.query.filter_by(id=method_id, shop_name=shop_name).first()
    return model_to_dict(method) if method else None

# 🔍 **Recupera un metodo di pagamento per nome e negozio**
@handle_db_errors
def get_payment_method(shop_name, method_name):
    method = PaymentMethod.query.filter_by(shop_name=shop_name, method_name=method_name).first()
    return model_to_dict(method) if method else None