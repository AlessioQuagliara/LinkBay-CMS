from app import app, db
from models import SuperAdmin
from werkzeug.security import generate_password_hash
import logging

# 📌 Configura il logging
logging.basicConfig(level=logging.INFO)

with app.app_context():
    try:
        superadmins = [
            {
                "email": "quagliara.alessio@outlook.com",
                "full_name": "Alessio Quagliara",
                "password": "WtQ5i8h20@",
                "role": "superadmin"
            },
            {
                "email": "junior.campos@spotexsrl.com",
                "full_name": "Junior Campos",
                "password": "LinkBay2024",
                "role": "editor"
            },
            {
                "email": "juan.romero@spotexsrl.com",
                "full_name": "Juan Romero",
                "password": "LinkBay2024",
                "role": "editor"
            },
            {
                "email": "nicola.pavan@spotexsrl.com",
                "full_name": "Nicola Pavan",
                "password": "LinkBay2024",
                "role": "editor"
            },
        ]

        for sa in superadmins:
            hashed_pw = generate_password_hash(sa["password"])
            new_admin = SuperAdmin(
                email=sa["email"],
                password_hash=hashed_pw,
                full_name=sa["full_name"],
                role=sa["role"]
            )
            db.session.add(new_admin)
            logging.info(f"✅ SuperAdmin creato: {sa['email']} ({sa['role']})")

        db.session.commit()
        logging.info("✅ Tutti i SuperAdmin sono stati creati correttamente.")

    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore durante la creazione dei SuperAdmin: {str(e)}")