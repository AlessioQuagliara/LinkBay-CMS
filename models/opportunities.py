from models.database import db
from datetime import datetime
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

# 🔍 **Recupera tutte le opportunità per uno shop**
def get_opportunities(shop_name):
    try:
        opportunities = Opportunity.query.filter_by(shop_name=shop_name).order_by(Opportunity.created_at.desc()).all()
        return [opportunity_to_dict(o) for o in opportunities]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero delle opportunità per {shop_name}: {e}")
        return []

# ✅ **Crea una nuova opportunità**
def create_opportunity(shop_name, user_id, title, category, description, budget):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione dell'opportunità '{title}' per {shop_name}: {e}")
        return None

# 🔄 **Aggiorna lo stato di un'opportunità**
def update_opportunity_status(opportunity_id, status):
    try:
        opportunity = Opportunity.query.get(opportunity_id)
        if not opportunity:
            return False

        opportunity.status = status
        opportunity.updated_at = datetime.utcnow()
        db.session.commit()
        logging.info(f"✅ Stato opportunità {opportunity_id} aggiornato a {status}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento dello stato dell'opportunità {opportunity_id}: {e}")
        return False

# ❌ **Elimina un'opportunità**
def delete_opportunity(opportunity_id):
    try:
        opportunity = Opportunity.query.get(opportunity_id)
        if not opportunity:
            return False

        db.session.delete(opportunity)
        db.session.commit()
        logging.info(f"✅ Opportunità {opportunity_id} eliminata con successo")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione dell'opportunità {opportunity_id}: {e}")
        return False

# 📩 **Invia un messaggio per un'opportunità**
def send_opportunity_message(opportunity_id, sender_id, sender_role, message):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'invio del messaggio per opportunità {opportunity_id}: {e}")
        return None

# 🔍 **Recupera i messaggi di un'opportunità**
def get_opportunity_messages(opportunity_id):
    try:
        messages = OpportunityMessage.query.filter_by(opportunity_id=opportunity_id).order_by(OpportunityMessage.created_at.asc()).all()
        return [message_to_dict(m) for m in messages]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei messaggi per opportunità {opportunity_id}: {e}")
        return []

# 📌 **Helper per convertire un'opportunità in dizionario**
def opportunity_to_dict(opportunity):
    return {
        "id": opportunity.id,
        "shop_name": opportunity.shop_name,
        "user_id": opportunity.user_id,
        "title": opportunity.title,
        "category": opportunity.category,
        "description": opportunity.description,
        "budget": opportunity.budget,
        "status": opportunity.status,
        "created_at": opportunity.created_at,
        "updated_at": opportunity.updated_at,
    }

# 📌 **Helper per convertire un messaggio in dizionario**
def message_to_dict(message):
    return {
        "id": message.id,
        "opportunity_id": message.opportunity_id,
        "sender_id": message.sender_id,
        "sender_role": message.sender_role,
        "message": message.message,
        "is_read": message.is_read,
        "created_at": message.created_at,
    }