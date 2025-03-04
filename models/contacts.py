from models.database import db
import logging
from datetime import datetime

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

# 🔹 **Modello per i Contatti**
class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco del contatto
    name = db.Column(db.String(255), nullable=False)  # 🏷️ Nome del contatto
    email = db.Column(db.String(255), nullable=False)  # 📧 Email del contatto
    message = db.Column(db.Text, nullable=False)  # 💬 Messaggio del contatto
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione

    def __repr__(self):
        return f"<Contact {self.name} ({self.email})>"

# ✅ **Crea un nuovo contatto**
def create_contact(name, email, message):
    try:
        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()
        logging.info(f"✅ Contatto '{name}' creato con successo")
        return new_contact.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione del contatto '{name}': {e}")
        return None

# 🔍 **Recupera tutti i contatti**
def get_all_contacts():
    try:
        contacts = Contact.query.order_by(Contact.created_at.desc()).all()
        return [contact_to_dict(c) for c in contacts]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei contatti: {e}")
        return []

# 🔍 **Recupera un contatto per ID**
def get_contact_by_id(contact_id):
    try:
        contact = Contact.query.get(contact_id)
        return contact_to_dict(contact) if contact else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del contatto ID {contact_id}: {e}")
        return None

# ❌ **Elimina un contatto**
def delete_contact(contact_id):
    try:
        contact = Contact.query.get(contact_id)
        if not contact:
            return False

        db.session.delete(contact)
        db.session.commit()
        logging.info(f"🗑️ Contatto ID {contact_id} eliminato con successo")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione del contatto ID {contact_id}: {e}")
        return False

# 📌 **Helper per convertire un contatto in dizionario**
def contact_to_dict(contact):
    return {
        "id": contact.id,
        "name": contact.name,
        "email": contact.email,
        "message": contact.message,
        "created_at": contact.created_at,
    }