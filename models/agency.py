from models.database import db
import logging
from functools import wraps
from datetime import datetime

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per le Agenzie**
class Agency(db.Model):
    __tablename__ = "agency"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco dell'agenzia
    agency_name = db.Column(db.String(255), unique=True, nullable=False)  # 🏢 Nome dell'agenzia
    email = db.Column(db.String(255), unique=True, nullable=False)  # 📧 Email dell'agenzia
    phone = db.Column(db.String(20), nullable=True)  # 📞 Numero di telefono
    address = db.Column(db.String(255), nullable=True)  # 🏠 Indirizzo
    website = db.Column(db.String(255), nullable=True)  # 🌍 Sito web
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🕒 Ultimo aggiornamento

    def __repr__(self):
        return f"<Agency {self.agency_name}>"

# 🔹 **Modello per i Dipendenti delle Agenzie**
class AgencyEmployee(db.Model):
    __tablename__ = "agency_employees"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco del dipendente
    agency_id = db.Column(db.Integer, db.ForeignKey("agency.id"), nullable=False)  # 🔗 ID Agenzia
    email = db.Column(db.String(255), unique=True, nullable=False)  # 📧 Email del dipendente
    password = db.Column(db.String(255), nullable=False)  # 🔒 Password hashata
    name = db.Column(db.String(100), nullable=False)  # 🏷️ Nome
    surname = db.Column(db.String(100), nullable=False)  # 🏷️ Cognome
    phone = db.Column(db.String(20), nullable=True)  # 📞 Numero di telefono
    role = db.Column(db.String(50), nullable=False)  # 🎭 Ruolo (admin, sales, marketing, support, developer)
    is_active = db.Column(db.Boolean, default=True)  # ✅ Stato attivo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🕒 Ultimo aggiornamento

    def __repr__(self):
        return f"<AgencyEmployee {self.email}>"

# 🔹 **Modello per l'Accesso delle Agenzie ai Negozi**
class AgencyStoreAccess(db.Model):
    __tablename__ = "agency_store_access"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    agency_id = db.Column(db.Integer, db.ForeignKey("agency.id"), nullable=False)  # 🔗 ID Agenzia
    shop_id = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)  # 🔗 ID Negozio
    access_level = db.Column(db.String(50), nullable=False, default="partner")  # 🔑 Ruolo (partner, reseller, manager)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🕒 Ultimo aggiornamento

    def __repr__(self):
        return f"<AgencyStoreAccess {self.agency_id} -> {self.shop_id}>"
    
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

# ✅ **Crea una nuova agenzia**
@handle_db_errors
def create_agency(agency_name, email, phone=None, address=None, website=None):
    new_agency = Agency(
        agency_name=agency_name,
        email=email,
        phone=phone,
        address=address,
        website=website,
    )
    db.session.add(new_agency)
    db.session.commit()
    logging.info(f"✅ Agenzia '{agency_name}' creata con successo")
    return new_agency.id

# ✅ **Crea un nuovo dipendente dell'agenzia**
@handle_db_errors
def create_agency_employee(agency_id, email, password, name, surname, role, phone=None):
    new_employee = AgencyEmployee(
        agency_id=agency_id,
        email=email,
        password=password,  # 🔐 Hash della password in produzione
        name=name,
        surname=surname,
        phone=phone,
        role=role,
    )
    db.session.add(new_employee)
    db.session.commit()
    logging.info(f"✅ Dipendente '{email}' creato con successo")
    return new_employee.id

# ✅ **Concedi accesso a un'agenzia per un negozio**
@handle_db_errors
def grant_agency_access(agency_id, shop_id, access_level="partner"):
    new_access = AgencyStoreAccess(
        agency_id=agency_id,
        shop_id=shop_id,
        access_level=access_level,
    )
    db.session.add(new_access)
    db.session.commit()
    logging.info(f"✅ Accesso concesso all'agenzia {agency_id} per il negozio {shop_id}")
    return new_access.id

# 🔍 **Recupera tutte le agenzie**
@handle_db_errors
def get_all_agencies():
    return db.session.query(Agency).all()

# 🔍 **Recupera i dipendenti di un'agenzia**
@handle_db_errors
def get_agency_employees(agency_id):
    return db.session.query(AgencyEmployee).filter_by(agency_id=agency_id).all()

# 🔍 **Verifica se un'agenzia ha accesso a un negozio**
@handle_db_errors
def has_agency_access(agency_id, shop_id):
    access = db.session.query(AgencyStoreAccess).filter_by(agency_id=agency_id, shop_id=shop_id).first()
    return access is not None

# 🗑️ **Elimina un dipendente dell'agenzia**
@handle_db_errors
def delete_agency_employee(employee_id):
    employee = db.session.get(AgencyEmployee, employee_id)
    if not employee:
        return False
    db.session.delete(employee)
    db.session.commit()
    logging.info(f"✅ Dipendente {employee_id} eliminato con successo")
    return True

# 🗑️ **Elimina un'agenzia e tutti i suoi dipendenti**
@handle_db_errors
def delete_agency(agency_id):
    AgencyEmployee.query.filter_by(agency_id=agency_id).delete()
    agency = db.session.get(Agency, agency_id)
    if not agency:
        return False
    db.session.delete(agency)
    db.session.commit()
    logging.info(f"✅ Agenzia {agency_id} eliminata con successo")
    return True