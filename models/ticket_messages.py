from models.database import db
from datetime import datetime
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

# ✅ **Crea un nuovo messaggio in un ticket**
def create_ticket_message(ticket_id, sender_id, sender_role, message):
    try:
        msg = TicketMessage(
            ticket_id=ticket_id,
            sender_id=sender_id,
            sender_role=sender_role,
            message=message,
            created_at=datetime.utcnow(),
        )
        db.session.add(msg)
        db.session.commit()
        logging.info(f"✅ Messaggio aggiunto al ticket {ticket_id} da {sender_role}")
        return msg.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione del messaggio per ticket {ticket_id}: {e}")
        return None

# 🔍 **Recupera tutti i messaggi di un ticket**
def get_messages_by_ticket(ticket_id):
    try:
        messages = TicketMessage.query.filter_by(ticket_id=ticket_id).order_by(TicketMessage.created_at.asc()).all()
        return [message_to_dict(msg) for msg in messages]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei messaggi per ticket {ticket_id}: {e}")
        return []

# 🔄 **Segna un messaggio come letto**
def mark_message_as_read(message_id):
    try:
        msg = TicketMessage.query.get(message_id)
        if msg:
            msg.is_read = True
            db.session.commit()
            logging.info(f"👀 Messaggio {message_id} segnato come letto")
            return True
        return False
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nel segnalare come letto il messaggio {message_id}: {e}")
        return False

# ❌ **Elimina un messaggio**
def delete_ticket_message(message_id):
    try:
        msg = TicketMessage.query.get(message_id)
        if not msg:
            return False
        db.session.delete(msg)
        db.session.commit()
        logging.info(f"❌ Messaggio {message_id} eliminato")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione del messaggio {message_id}: {e}")
        return False

# 📌 **Helper per convertire un messaggio in dizionario**
def message_to_dict(msg):
    return {col.name: getattr(msg, col.name) for col in TicketMessage.__table__.columns} if msg else None