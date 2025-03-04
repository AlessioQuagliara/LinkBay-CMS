from models.database import db
from datetime import datetime
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

# ✅ **Aggiunge un nuovo pagamento**
def add_payment(data):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiunta del pagamento: {e}")
        return None

# 🔍 **Recupera tutti i pagamenti associati a un ordine**
def get_payments_by_order_id(order_id):
    try:
        payments = Payment.query.filter_by(order_id=order_id).order_by(Payment.created_at.desc()).all()
        return [payment_to_dict(p) for p in payments]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei pagamenti per l'ordine {order_id}: {e}")
        return []

# 🔍 **Recupera un pagamento per ID**
def get_payment_by_id(payment_id):
    try:
        payment = Payment.query.filter_by(id=payment_id).first()
        return payment_to_dict(payment) if payment else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del pagamento {payment_id}: {e}")
        return None

# 🔄 **Aggiorna lo stato di un pagamento**
def update_payment_status(payment_id, new_status):
    try:
        payment = Payment.query.filter_by(id=payment_id).first()
        if not payment:
            return False

        payment.payment_status = new_status
        payment.updated_at = datetime.utcnow()

        db.session.commit()
        logging.info(f"✅ Stato del pagamento {payment_id} aggiornato a {new_status}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento dello stato del pagamento {payment_id}: {e}")
        return False

# 📌 **Helper per convertire un pagamento in dizionario**
def payment_to_dict(payment):
    return {col.name: getattr(payment, col.name) for col in Payment.__table__.columns} if payment else None