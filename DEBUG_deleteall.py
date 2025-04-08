from app import app, db
from sqlalchemy import text
import logging

# Abilita il logging
logging.basicConfig(level=logging.INFO)

with app.app_context():
    try:
        logging.warning("⚠️ ATTENZIONE: Avvio svuotamento parziale del database...")

        # Elimina solo i primi 5 record da ciascuna tabella specificata
        tables = ["user_store_access", "web_settings", "stores_info", "shoplist", "user"]
        for table in tables:
            db.session.execute(text(f"DELETE FROM {table} WHERE id IN (SELECT id FROM {table} ORDER BY id ASC LIMIT 5);"))
        db.session.commit()

        logging.info("✅ I primi 5 record di ciascuna tabella sono stati eliminati correttamente.")
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore durante l'eliminazione dei record: {e}")