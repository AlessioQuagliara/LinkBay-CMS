from models.database import db
from datetime import datetime
import logging
from functools import wraps

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per i Messaggi nei Ticket di Supporto**
class TicketMessage(db.Model):
    __tablename__ = "ticket_messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("support_tickets.id"), nullable=False)  # 🔗 Relazione con il ticket
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # 📩 Chi invia il messaggio
    sender_role = db.Column(db.String(50), nullable=False, default="user")  # 🏷️ Ruolo: user, agency, support_agent
    message = db.Column(db.Text, nullable=False)  # 💬 Contenuto del messaggio
    is_read = db.Column(db.Boolean, default=False)  # 👀 Se il messaggio è stato letto
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione

    def __repr__(self):
        return f"<TicketMessage {self.id} - Ticket {self.ticket_id} ({self.sender_role})>"
    
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


# ✅ **Crea un nuovo messaggio in un ticket**
@handle_db_errors
def create_ticket_message(ticket_id, sender_id, sender_role, message):
    msg = TicketMessage(
        ticket_id=ticket_id,
        sender_id=sender_id,
        sender_role=sender_role,
        message=message,
    )
    db.session.add(msg)
    db.session.commit()
    logging.info(f"✅ Messaggio aggiunto al ticket {ticket_id} da {sender_role}")
    return msg.id


# 🔍 **Recupera tutti i messaggi di un ticket**
@handle_db_errors
def get_messages_by_ticket(ticket_id):
    messages = TicketMessage.query.filter_by(ticket_id=ticket_id).order_by(TicketMessage.created_at.asc()).all()
    return [message_to_dict(msg) for msg in messages]


# 🔄 **Segna un messaggio come letto**
@handle_db_errors
def mark_message_as_read(message_id):
    msg = TicketMessage.query.get(message_id)
    if not msg:
        return False

    msg.is_read = True
    db.session.commit()
    logging.info(f"👀 Messaggio {message_id} segnato come letto")
    return True


# ❌ **Elimina un messaggio**
@handle_db_errors
def delete_ticket_message(message_id):
    msg = TicketMessage.query.get(message_id)
    if not msg:
        return False

    db.session.delete(msg)
    db.session.commit()
    logging.info(f"❌ Messaggio {message_id} eliminato")
    return True


# 📌 **Helper per convertire un messaggio in dizionario**
def message_to_dict(msg):
    return {col.name: getattr(msg, col.name) for col in TicketMessage.__table__.columns} if msg else None