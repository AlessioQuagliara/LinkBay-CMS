from models.database import db
from datetime import datetime
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

# ✅ **Crea un nuovo pagamento**
def create_payment(shop_name, payment_type, amount, stripe_payment_id, status="pending",
                   integration_name=None, subscription_id=None, currency="EUR"):
    try:
        payment = StorePayment(
            shop_name=shop_name,
            payment_type=payment_type,
            amount=amount,
            stripe_payment_id=stripe_payment_id,
            status=status,
            integration_name=integration_name,
            subscription_id=subscription_id,
            currency=currency,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(payment)
        db.session.commit()
        logging.info(f"✅ Pagamento creato: {shop_name} - {amount} {currency} - {status}")
        return payment.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione del pagamento: {e}")
        return None

# 🔄 **Aggiorna lo stato di un pagamento**
def update_payment_status(stripe_payment_id, status):
    try:
        payment = StorePayment.query.filter_by(stripe_payment_id=stripe_payment_id).first()
        if payment:
            payment.status = status
            payment.updated_at = datetime.utcnow()
            db.session.commit()
            logging.info(f"🔄 Stato del pagamento aggiornato: {stripe_payment_id} -> {status}")
            return True
        return False
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento dello stato del pagamento: {e}")
        return False

# 🔍 **Recupera tutti i pagamenti di uno shop**
def get_payments_by_shop(shop_name):
    try:
        payments = StorePayment.query.filter_by(shop_name=shop_name).order_by(StorePayment.created_at.desc()).all()
        return [payment_to_dict(payment) for payment in payments]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei pagamenti per {shop_name}: {e}")
        return []

# 🔍 **Recupera un pagamento specifico tramite Stripe ID**
def get_payment_by_stripe_id(stripe_payment_id):
    try:
        payment = StorePayment.query.filter_by(stripe_payment_id=stripe_payment_id).first()
        return payment_to_dict(payment) if payment else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del pagamento {stripe_payment_id}: {e}")
        return None

# 🔍 **Recupera i pagamenti di tipo abbonamento**
def get_subscription_payments(shop_name):
    try:
        payments = StorePayment.query.filter_by(shop_name=shop_name, payment_type="subscription")\
            .order_by(StorePayment.created_at.desc()).all()
        return [payment_to_dict(payment) for payment in payments]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei pagamenti in abbonamento per {shop_name}: {e}")
        return []

# 📌 **Helper per convertire un pagamento in dizionario**
def payment_to_dict(payment):
    return {col.name: getattr(payment, col.name) for col in StorePayment.__table__.columns} if payment else None