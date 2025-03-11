from models.database import db
from datetime import datetime
import logging
from functools import wraps

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per la gestione dei Ticket di Supporto**
class SupportTicket(db.Model):
    __tablename__ = "support_tickets"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shop_name = db.Column(db.String(255), db.ForeignKey("ShopList.shop_name"), nullable=False)  # 🏪 Negozio
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)  # 👤 Utente che apre il ticket
    agency_id = db.Column(db.Integer, db.ForeignKey("agency.id"), nullable=True)  # 🏢 Agenzia (se il ticket è aperto da un'agenzia)
    title = db.Column(db.String(255), nullable=False)  # 📝 Oggetto del ticket
    category = db.Column(db.String(100), nullable=False)  # 📂 Categoria (tecnico, fatturazione, ecommerce)
    message = db.Column(db.Text, nullable=False)  # 💬 Primo messaggio del ticket
    priority = db.Column(db.String(50), nullable=False, default="normal")  # 🚨 Priorità (low, normal, high, critical)
    status = db.Column(db.String(50), nullable=False, default="open")  # 🔄 Stato (open, in_progress, closed)
    assigned_to = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)  # 👨‍💻 Operatore assegnato al ticket
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    def __repr__(self):
        return f"<SupportTicket {self.id} - {self.title} ({self.status})>"
    
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


# ✅ **Crea un nuovo ticket**
@handle_db_errors
def create_support_ticket(shop_name, user_id, title, category, message, priority="normal", agency_id=None, assigned_to=None):
    ticket = SupportTicket(
        shop_name=shop_name,
        user_id=user_id,
        agency_id=agency_id,
        title=title,
        category=category,
        message=message,
        priority=priority,
        status="open",
        assigned_to=assigned_to,
    )
    db.session.add(ticket)
    db.session.commit()
    logging.info(f"✅ Ticket creato: {title} per {shop_name}")
    return ticket.id


# 🔍 **Recupera tutti i ticket di uno shop**
@handle_db_errors
def get_tickets_by_shop(shop_name, status=None):
    query = SupportTicket.query.filter_by(shop_name=shop_name)
    if status:
        query = query.filter_by(status=status)
    tickets = query.order_by(SupportTicket.created_at.desc()).all()
    return [ticket_to_dict(ticket) for ticket in tickets]


# 🔍 **Recupera un ticket per ID**
@handle_db_errors
def get_ticket_by_id(ticket_id):
    ticket = SupportTicket.query.get(ticket_id)
    return ticket_to_dict(ticket) if ticket else None


# 🔄 **Aggiorna un ticket**
@handle_db_errors
def update_ticket(ticket_id, **kwargs):
    ticket = SupportTicket.query.get(ticket_id)
    if not ticket:
        return False

    for key, value in kwargs.items():
        setattr(ticket, key, value)

    ticket.updated_at = datetime.utcnow()
    db.session.commit()
    logging.info(f"🔄 Ticket {ticket_id} aggiornato")
    return True


# ❌ **Elimina un ticket**
@handle_db_errors
def delete_ticket(ticket_id):
    ticket = SupportTicket.query.get(ticket_id)
    if not ticket:
        return False

    db.session.delete(ticket)
    db.session.commit()
    logging.info(f"❌ Ticket {ticket_id} eliminato")
    return True


# 📌 **Helper per convertire un ticket in dizionario**
def ticket_to_dict(ticket):
    return {col.name: getattr(ticket, col.name) for col in SupportTicket.__table__.columns} if ticket else None