from models.database import db
from datetime import datetime
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per i Messaggi Diretti tra Utenti**
class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # 👤 Mittente
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # 👥 Destinatario
    message = db.Column(db.Text, nullable=False)  # 💬 Testo del messaggio
    attachment_url = db.Column(db.String(500), nullable=True)  # 📎 Allegato (link al file se presente)
    is_read = db.Column(db.Boolean, default=False)  # 👀 Stato lettura
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Timestamp creazione

    def __repr__(self):
        return f"<ChatMessage {self.id} from {self.sender_id} to {self.receiver_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message": self.message,
            "attachment_url": self.attachment_url,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat()
        }

# 🔄 Decoratore per gestire gli errori del DB
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

# ✅ Crea un nuovo messaggio
@handle_db_errors
def send_message(sender_id, receiver_id, message, attachment_url=None):
    msg = ChatMessage(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message,
        attachment_url=attachment_url
    )
    db.session.add(msg)
    db.session.commit()
    logging.info(f"📩 Messaggio inviato da {sender_id} a {receiver_id}")
    return msg.to_dict()

# 🔍 Recupera conversazione tra due utenti
@handle_db_errors
def get_conversation(user1_id, user2_id):
    messages = ChatMessage.query.filter(
        ((ChatMessage.sender_id == user1_id) & (ChatMessage.receiver_id == user2_id)) |
        ((ChatMessage.sender_id == user2_id) & (ChatMessage.receiver_id == user1_id))
    ).order_by(ChatMessage.created_at.asc()).all()
    return [msg.to_dict() for msg in messages]

# 🔄 Segna un messaggio come letto
@handle_db_errors
def mark_chat_message_as_read(message_id):
    msg = ChatMessage.query.get(message_id)
    if msg:
        msg.is_read = True
        db.session.commit()
        logging.info(f"👁️‍🗨️ Messaggio {message_id} segnato come letto")
        return True
    return False

# ❌ Elimina un messaggio
@handle_db_errors
def delete_chat_message(message_id):
    msg = ChatMessage.query.get(message_id)
    if msg:
        db.session.delete(msg)
        db.session.commit()
        logging.info(f"🗑️ Messaggio {message_id} eliminato")
        return True
    return False