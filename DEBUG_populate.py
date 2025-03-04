from app import app, db
from models.user import User
from models.shoplist import ShopList
from models.userstoreaccess import UserStoreAccess
from werkzeug.security import generate_password_hash
import logging

# 📌 Configura il logging
logging.basicConfig(level=logging.INFO)

with app.app_context():
    try:
        # ✅ Crea un nuovo utente SENZA controllare se esiste già
        user = User(
            email="quagliara.alessio@gmail.com",
            nome="Alessio",
            cognome="Quagliara",
            telefono="1234567890",
            profilo_foto=None,
            is_2fa_enabled=False,
            otp_secret=None
        )
        user.set_password("WtQ5i8h20@")  # Hash della password

        db.session.add(user)
        db.session.commit()
        logging.info(f"✅ Utente creato: {user.email}")

        # ✅ Crea un nuovo negozio SENZA controllare se esiste già
        shop = ShopList(
            shop_name="erboristeria",
            shop_type="ecommerce",
            domain="erboristeria.local",
            user_id=user.id,
            partner_id=None
        )

        db.session.add(shop)
        db.session.commit()
        logging.info(f"✅ Negozio creato: {shop.shop_name}")

        # ✅ Concede accesso all'utente SENZA controllare se ha già accesso
        access = UserStoreAccess(user_id=user.id, shop_id=shop.id, access_level="admin")
        db.session.add(access)
        db.session.commit()
        logging.info(f"✅ Accesso assegnato: {user.email} → {shop.shop_name} (admin)")

    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore durante l'inserimento dei dati: {str(e)}")