from models.database import db
from datetime import datetime
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

# 🔹 **Modello per la gestione degli accessi utente ai negozi**
class UserStoreAccess(db.Model):
    __tablename__ = "user_store_access"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)
    access_level = db.Column(db.String(20), nullable=False, default="viewer")  # viewer, editor, admin

    __table_args__ = (db.UniqueConstraint("user_id", "shop_id", name="uq_user_store"),)  # Impedisce accessi duplicati

    def __repr__(self):
        return f"<UserStoreAccess user_id={self.user_id}, shop_id={self.shop_id}, access_level={self.access_level}>"

# ✅ **Concedi accesso a un utente per uno store**
def grant_access(user_id, shop_id, access_level="viewer"):
    try:
        access = UserStoreAccess.query.filter_by(user_id=user_id, shop_id=shop_id).first()
        if access:
            access.access_level = access_level  # Aggiorna se già esistente
        else:
            access = UserStoreAccess(user_id=user_id, shop_id=shop_id, access_level=access_level)
            db.session.add(access)
        db.session.commit()
        logging.info(f"✅ Accesso concesso: user {user_id} → shop {shop_id} ({access_level})")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella concessione dell'accesso: {e}")
        return False

# ❌ **Revoca accesso a un utente per uno store**
def revoke_access(user_id, shop_id):
    try:
        result = UserStoreAccess.query.filter_by(user_id=user_id, shop_id=shop_id).delete()
        db.session.commit()
        if result:
            logging.info(f"❌ Accesso revocato: user {user_id} → shop {shop_id}")
            return True
        return False
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella revoca dell'accesso: {e}")
        return False

# 🔍 **Controlla se un utente ha accesso a uno store**
def has_access(user_id, shop_id):
    return UserStoreAccess.query.filter_by(user_id=user_id, shop_id=shop_id).first() is not None

# 🔍 **Recupera il livello di accesso di un utente per uno store**
def get_access_level(user_id, shop_id):
    access = UserStoreAccess.query.filter_by(user_id=user_id, shop_id=shop_id).first()
    return access.access_level if access else None

# 🔍 **Recupera tutti gli store a cui un utente ha accesso**
def get_user_stores(user_id):
    return [
        {"shop_id": access.shop_id, "access_level": access.access_level}
        for access in UserStoreAccess.query.filter_by(user_id=user_id).all()
    ]