from models.database import db
from datetime import datetime
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

# 🔹 **Modello per la gestione degli abbonamenti**
class Subscription(db.Model):
    __tablename__ = "subscription"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shop_name = db.Column(db.String(255), db.ForeignKey("ShopList.shop_name"), nullable=False)  # 🏪 Negozio
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # 👤 Utente associato
    plan_name = db.Column(db.String(100), nullable=False)  # 📜 Piano (Starter, Pro, Enterprise)
    price = db.Column(db.Float, nullable=False)  # 💰 Prezzo del piano
    currency = db.Column(db.String(10), nullable=False, default="EUR")  # 💱 Valuta (EUR, USD, ecc.)
    features = db.Column(db.String(500), nullable=True)  # ⭐ Funzionalità incluse
    limits = db.Column(db.String(500), nullable=True)  # 🚧 Limiti del piano
    status = db.Column(db.String(20), nullable=False, default="active")  # 🔄 Stato (active, canceled, expired, trial)
    payment_gateway = db.Column(db.String(50), nullable=False)  # 💳 Stripe, PayPal, Bonifico
    payment_reference = db.Column(db.String(255), nullable=True)  # 🏦 ID transazione Stripe/PayPal
    trial_end = db.Column(db.DateTime, nullable=True)  # 🆓 Fine periodo di prova
    renewal_date = db.Column(db.DateTime, nullable=False)  # 📆 Data di rinnovo o scadenza
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    def __repr__(self):
        return f"<Subscription {self.shop_name} - {self.plan_name} ({self.status})>"

# ✅ **Crea un nuovo abbonamento**
def create_subscription(shop_name, user_id, plan_name, price, currency, features, limits, payment_gateway, payment_reference, renewal_date, trial_end=None):
    try:
        subscription = Subscription(
            shop_name=shop_name,
            user_id=user_id,
            plan_name=plan_name,
            price=price,
            currency=currency,
            features=features,
            limits=limits,
            status="active",
            payment_gateway=payment_gateway,
            payment_reference=payment_reference,
            renewal_date=renewal_date,
            trial_end=trial_end,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(subscription)
        db.session.commit()
        logging.info(f"✅ Abbonamento creato per {shop_name} - Piano: {plan_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione dell'abbonamento per {shop_name}: {e}")
        return False

# 🔍 **Recupera l'abbonamento di uno shop**
def get_subscription_by_shop(shop_name):
    try:
        subscription = Subscription.query.filter_by(shop_name=shop_name).first()
        return subscription_to_dict(subscription) if subscription else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dell'abbonamento per {shop_name}: {e}")
        return None

# 🔄 **Aggiorna l'abbonamento di uno shop**
def update_subscription(shop_name, **kwargs):
    try:
        subscription = Subscription.query.filter_by(shop_name=shop_name).first()
        if not subscription:
            return False
        for key, value in kwargs.items():
            setattr(subscription, key, value)
        subscription.updated_at = datetime.utcnow()
        db.session.commit()
        logging.info(f"🔄 Abbonamento aggiornato per {shop_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento dell'abbonamento per {shop_name}: {e}")
        return False

# ❌ **Elimina un abbonamento**
def delete_subscription(shop_name):
    try:
        subscription = Subscription.query.filter_by(shop_name=shop_name).first()
        if not subscription:
            return False
        db.session.delete(subscription)
        db.session.commit()
        logging.info(f"❌ Abbonamento eliminato per {shop_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione dell'abbonamento per {shop_name}: {e}")
        return False

# 🔍 **Controlla se uno shop ha un abbonamento attivo**
def has_active_subscription(shop_name):
    try:
        return Subscription.query.filter_by(shop_name=shop_name, status="active").first() is not None
    except Exception as e:
        logging.error(f"❌ Errore nel controllo dello stato dell'abbonamento per {shop_name}: {e}")
        return False

# 📌 **Helper per convertire un abbonamento in dizionario**
def subscription_to_dict(subscription):
    return {col.name: getattr(subscription, col.name) for col in Subscription.__table__.columns} if subscription else None