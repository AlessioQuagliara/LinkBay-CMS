from models.database import db
import logging
from functools import wraps
from datetime import datetime

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# ✅ **Crea un nuovo contatto**
@handle_db_errors
def create_contact(name, email, message):
    new_contact = Contact(name=name, email=email, message=message)
    db.session.add(new_contact)
    db.session.commit()
    logging.info(f"✅ Contatto '{name}' creato con successo")
    return new_contact.id

# 🔍 **Recupera tutti i contatti**
@handle_db_errors
def get_all_contacts():
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    return [model_to_dict(c) for c in contacts]

# 🔍 **Recupera un contatto per ID**
@handle_db_errors
def get_contact_by_id(contact_id):
    contact = Contact.query.get(contact_id)
    return model_to_dict(contact) if contact else None

# ❌ **Elimina un contatto**
@handle_db_errors
def delete_contact(contact_id):
    contact = Contact.query.get(contact_id)
    if not contact:
        return False

    db.session.delete(contact)
    db.session.commit()
    logging.info(f"🗑️ Contatto ID {contact_id} eliminato con successo")
    return True