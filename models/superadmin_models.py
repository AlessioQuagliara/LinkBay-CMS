from models.database import db
import logging
from datetime import datetime
from functools import wraps

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Tabella per i SuperAdmin**
class SuperAdmin(db.Model):
    __tablename__ = "superadmin"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Hash della password
    full_name = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), nullable=False, default="superadmin")  # Esempio: superadmin, owner
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SuperAdmin email={self.email}, role={self.role}>"


# 🔹 **Tabella per le pagine del sito landing del CMS**
class SuperPages(db.Model):
    __tablename__ = "superpages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=True)
    seo_keywords = db.Column(db.String(255), nullable=True)
    seo_description = db.Column(db.Text, nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SuperPages title={self.title}, slug={self.slug}>"


# 🔹 **Tabella per i media caricati sul CMS**
class SuperMedia(db.Model):
    __tablename__ = "supermedia"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # Es. image, video, document
    uploaded_by = db.Column(db.Integer, db.ForeignKey("superadmin.id"), nullable=False)  # Associa il media a un SuperAdmin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SuperMedia file_name={self.file_name}, file_type={self.file_type}>"


# 🔹 **Tabella per le fatture emesse ai clienti**
class SuperInvoice(db.Model):
    __tablename__ = "superinvoice"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    shop_name = db.Column(db.String(255), nullable=False)
    invoice_number = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="EUR")
    status = db.Column(db.String(50), nullable=False, default="pending")  # pending, paid, failed
    pdf_url = db.Column(db.String(500), nullable=True)  # URL per scaricare la fattura
    issued_by = db.Column(db.Integer, db.ForeignKey("superadmin.id"), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SuperInvoice invoice_number={self.invoice_number}, status={self.status}>"


# 🔹 **Tabella per i messaggi di sistema (annunci, aggiornamenti)**
class SuperMessages(db.Model):
    __tablename__ = "supermessages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)  # Titolo del messaggio
    message = db.Column(db.Text, nullable=False)  # Testo del messaggio
    message_type = db.Column(db.String(50), nullable=False, default="info")  # info, warning, alert
    is_active = db.Column(db.Boolean, default=True)  # Se il messaggio è ancora valido
    show_until = db.Column(db.DateTime, nullable=True)  # Data di scadenza del messaggio
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SuperMessages title={self.title}, type={self.message_type}>"


# 🔹 **Tabella per i ticket complessi inviati dalle agenzie**
class SuperSupport(db.Model):
    __tablename__ = "supersupport"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    agency_id = db.Column(db.Integer, db.ForeignKey("agency.id"), nullable=False)  # Agenzia che invia il ticket
    shop_name = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)  # Oggetto del ticket
    description = db.Column(db.Text, nullable=False)  # Dettagli del problema
    priority = db.Column(db.String(50), nullable=False, default="normal")  # low, normal, high, critical
    status = db.Column(db.String(50), nullable=False, default="open")  # open, in_progress, closed
    assigned_to = db.Column(db.Integer, db.ForeignKey("superadmin.id"), nullable=True)  # SuperAdmin assegnato
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SuperSupport subject={self.subject}, priority={self.priority}>"
    
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


# 📌 **Helper per convertire un modello in dizionario**
def model_to_dict(model):
    return {col.name: getattr(model, col.name) for col in model.__table__.columns} if model else None