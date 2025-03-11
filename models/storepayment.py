from models.database import db
from datetime import datetime
import logging
from functools import wraps

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per i Pagamenti dello Store**
class StorePayment(db.Model):
    __tablename__ = "store_payments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Nome dello shop
    payment_type = db.Column(db.String(50), nullable=False)  # 💳 'one-time' | 'subscription'
    integration_name = db.Column(db.String(255), nullable=True)  # 🛠️ Metodo di pagamento (es. Stripe, PayPal)
    amount = db.Column(db.Float, nullable=False)  # 💰 Importo pagato
    currency = db.Column(db.String(10), nullable=False, default="EUR")  # 💱 Valuta
    stripe_payment_id = db.Column(db.String(255), unique=True, nullable=False)  # 🆔 ID Stripe
    status = db.Column(db.String(50), nullable=False, default="pending")  # ⏳ Stato (pending, completed, failed)
    subscription_id = db.Column(db.String(255), nullable=True)  # 🔁 ID Abbonamento Stripe
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    def __repr__(self):
        return f"<StorePayment {self.id} - {self.shop_name} - {self.status}>"
    
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


# ✅ **Crea un nuovo pagamento**
@handle_db_errors
def create_payment(shop_name, payment_type, amount, stripe_payment_id, status="pending",
                   integration_name=None, subscription_id=None, currency="EUR"):
    payment = StorePayment(
        shop_name=shop_name,
        payment_type=payment_type,
        amount=amount,
        stripe_payment_id=stripe_payment_id,
        status=status,
        integration_name=integration_name,
        subscription_id=subscription_id,
        currency=currency,
    )
    db.session.add(payment)
    db.session.commit()
    logging.info(f"✅ Pagamento creato: {shop_name} - {amount} {currency} - {status}")
    return payment.id


# 🔄 **Aggiorna lo stato di un pagamento**
@handle_db_errors
def update_payment_status(stripe_payment_id, status):
    payment = StorePayment.query.filter_by(stripe_payment_id=stripe_payment_id).first()
    if not payment:
        return False

    payment.status = status
    payment.updated_at = datetime.utcnow()
    db.session.commit()
    logging.info(f"🔄 Stato del pagamento aggiornato: {stripe_payment_id} -> {status}")
    return True


# 🔍 **Recupera tutti i pagamenti di uno shop**
@handle_db_errors
def get_payments_by_shop(shop_name):
    payments = StorePayment.query.filter_by(shop_name=shop_name).order_by(StorePayment.created_at.desc()).all()
    return [payment_to_dict(payment) for payment in payments]


# 🔍 **Recupera un pagamento specifico tramite Stripe ID**
@handle_db_errors
def get_payment_by_stripe_id(stripe_payment_id):
    payment = StorePayment.query.filter_by(stripe_payment_id=stripe_payment_id).first()
    return payment_to_dict(payment) if payment else None


# 🔍 **Recupera i pagamenti di tipo abbonamento**
@handle_db_errors
def get_subscription_payments(shop_name):
    payments = StorePayment.query.filter_by(shop_name=shop_name, payment_type="subscription")\
        .order_by(StorePayment.created_at.desc()).all()
    return [payment_to_dict(payment) for payment in payments]


# 📌 **Helper per convertire un pagamento in dizionario**
def payment_to_dict(payment):
    return {col.name: getattr(payment, col.name) for col in StorePayment.__table__.columns} if payment else None