from models.database import db
import logging
from functools import wraps
from datetime import datetime

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per i Pagamenti**
class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)  # 🛒 ID dell'ordine associato
    payment_method = db.Column(db.String(255), nullable=False)  # 💳 Metodo di pagamento (Stripe, PayPal)
    payment_status = db.Column(db.String(50), nullable=False, default="pending")  # 📌 Stato del pagamento
    paid_amount = db.Column(db.Float, nullable=False, default=0.0)  # 💰 Importo pagato
    transaction_id = db.Column(db.String(255), nullable=True)  # 🔗 ID della transazione
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione

    def __repr__(self):
        return f"<Payment {self.id} - Order {self.order_id} ({self.payment_status})>"

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

# ✅ **Aggiunge un nuovo pagamento**
@handle_db_errors
def add_payment(data):
    # Validazione dei dati obbligatori
    required_fields = ["order_id", "payment_method", "payment_status", "paid_amount"]
    if not all(field in data for field in required_fields):
        logging.error("❌ Dati mancanti per la creazione del pagamento")
        return None

    new_payment = Payment(
        order_id=data["order_id"],
        payment_method=data["payment_method"],
        payment_status=data["payment_status"],
        paid_amount=data["paid_amount"],
        transaction_id=data.get("transaction_id"),
    )
    db.session.add(new_payment)
    db.session.commit()
    logging.info(f"✅ Pagamento aggiunto con successo per l'ordine {data['order_id']}")
    return new_payment.id

# 🔍 **Recupera tutti i pagamenti associati a un ordine**
@handle_db_errors
def get_payments_by_order_id(order_id):
    payments = Payment.query.filter_by(order_id=order_id).order_by(Payment.created_at.desc()).all()
    return [model_to_dict(p) for p in payments]

# 🔍 **Recupera un pagamento per ID**
@handle_db_errors
def get_payment_by_id(payment_id):
    payment = Payment.query.filter_by(id=payment_id).first()
    return model_to_dict(payment) if payment else None

# 🔄 **Aggiorna lo stato di un pagamento**
@handle_db_errors
def update_payment_status(payment_id, new_status):
    payment = Payment.query.filter_by(id=payment_id).first()
    if not payment:
        logging.error(f"❌ Pagamento {payment_id} non trovato")
        return False

    payment.payment_status = new_status
    payment.updated_at = datetime.utcnow()

    db.session.commit()
    logging.info(f"✅ Stato del pagamento {payment_id} aggiornato a {new_status}")
    return True