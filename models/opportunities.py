from models.database import db
import logging
from functools import wraps
from datetime import datetime

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per le Opportunità**
class Opportunity(db.Model):
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), db.ForeignKey("ShopList.shop_name"), nullable=False)  # 🏪 Relazione con il negozio
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # 👤 Utente che ha pubblicato
    title = db.Column(db.String(255), nullable=False)  # 📌 Titolo dell'opportunità
    category = db.Column(db.String(100), nullable=False)  # 📂 Categoria (SEO, Web Design, ecc.)
    description = db.Column(db.Text, nullable=False)  # 📝 Descrizione dettagliata
    budget = db.Column(db.Numeric(10, 2), nullable=True)  # 💰 Budget stimato
    status = db.Column(db.String(50), nullable=False, default="open")  # 🔄 Stato (open, taken, completed, closed)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    def __repr__(self):
        return f"<Opportunity {self.id} - {self.title}>"

# 🔹 **Modello per le Offerte delle Agenzie**
class AgencyOpportunity(db.Model):
    __tablename__ = "agency_opportunities"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id"), nullable=False)  # 🎯 Opportunità selezionata
    agency_id = db.Column(db.Integer, db.ForeignKey("agency.id"), nullable=False)  # 🏢 Agenzia che ha preso l'opportunità
    proposed_price = db.Column(db.Numeric(10, 2), nullable=False)  # 💰 Prezzo proposto
    deadline = db.Column(db.DateTime, nullable=False)  # 📅 Scadenza proposta
    status = db.Column(db.String(50), nullable=False, default="pending")  # 🔄 Stato della proposta (pending, accepted, rejected)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    def __repr__(self):
        return f"<AgencyOpportunity {self.id} - {self.status}>"

# 🔹 **Modello per i Messaggi delle Opportunità**
class OpportunityMessage(db.Model):
    __tablename__ = "opportunity_messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id"), nullable=False)  # 🎯 Opportunità associata
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # ✉️ Mittente
    sender_role = db.Column(db.String(50), nullable=False, default="user")  # 🔖 Ruolo del mittente (user, agency)
    message = db.Column(db.Text, nullable=False)  # 📝 Contenuto del messaggio
    is_read = db.Column(db.Boolean, default=False)  # 👀 Messaggio letto?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione

    def __repr__(self):
        return f"<OpportunityMessage {self.id} - {self.sender_role}>"
    
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

# 🔍 **Recupera tutte le opportunità per uno shop**
@handle_db_errors
def get_opportunities(shop_name):
    opportunities = Opportunity.query.filter_by(shop_name=shop_name).order_by(Opportunity.created_at.desc()).all()
    return [model_to_dict(o) for o in opportunities]

# ✅ **Crea una nuova opportunità**
@handle_db_errors
def create_opportunity(shop_name, user_id, title, category, description, budget):
    new_opportunity = Opportunity(
        shop_name=shop_name,
        user_id=user_id,
        title=title,
        category=category,
        description=description,
        budget=budget,
    )
    db.session.add(new_opportunity)
    db.session.commit()
    logging.info(f"✅ Opportunità '{title}' creata con successo per {shop_name}")
    return new_opportunity.id

# 🔄 **Aggiorna lo stato di un'opportunità**
@handle_db_errors
def update_opportunity_status(opportunity_id, status):
    opportunity = Opportunity.query.get(opportunity_id)
    if not opportunity:
        return False

    opportunity.status = status
    opportunity.updated_at = datetime.utcnow()
    db.session.commit()
    logging.info(f"✅ Stato opportunità {opportunity_id} aggiornato a {status}")
    return True

# ❌ **Elimina un'opportunità**
@handle_db_errors
def delete_opportunity(opportunity_id):
    opportunity = Opportunity.query.get(opportunity_id)
    if not opportunity:
        return False

    db.session.delete(opportunity)
    db.session.commit()
    logging.info(f"✅ Opportunità {opportunity_id} eliminata con successo")
    return True

# 📩 **Invia un messaggio per un'opportunità**
@handle_db_errors
def send_opportunity_message(opportunity_id, sender_id, sender_role, message):
    new_message = OpportunityMessage(
        opportunity_id=opportunity_id,
        sender_id=sender_id,
        sender_role=sender_role,
        message=message,
    )
    db.session.add(new_message)
    db.session.commit()
    logging.info(f"✅ Messaggio inviato per opportunità {opportunity_id} da {sender_role}")
    return new_message.id

# 🔍 **Recupera i messaggi di un'opportunità**
@handle_db_errors
def get_opportunity_messages(opportunity_id):
    messages = OpportunityMessage.query.filter_by(opportunity_id=opportunity_id).order_by(OpportunityMessage.created_at.asc()).all()
    return [model_to_dict(m) for m in messages]