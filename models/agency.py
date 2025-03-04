from models.database import db
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

# 🔹 **Modello per le Agenzie**
class Agency(db.Model):
    """
    Modello ORM per le Agenzie nel CMS.
    """
    __tablename__ = "agency"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco dell'agenzia
    agency_name = db.Column(db.String(255), unique=True, nullable=False)  # 🏢 Nome dell'agenzia
    email = db.Column(db.String(255), unique=True, nullable=False)  # 📧 Email dell'agenzia
    phone = db.Column(db.String(20), nullable=True)  # 📞 Numero di telefono
    address = db.Column(db.String(255), nullable=True)  # 🏠 Indirizzo
    website = db.Column(db.String(255), nullable=True)  # 🌍 Sito web
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 🕒 Ultimo aggiornamento


# 🔹 **Modello per i Dipendenti delle Agenzie**
class AgencyEmployee(db.Model):
    """
    Modello ORM per i Dipendenti delle Agenzie.
    """
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
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 🕒 Ultimo aggiornamento


# 🔹 **Modello per l'Accesso delle Agenzie ai Negozi**
class AgencyStoreAccess(db.Model):
    """
    Modello ORM per la gestione dell'accesso delle agenzie ai negozi.
    """
    __tablename__ = "agency_store_access"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    agency_id = db.Column(db.Integer, db.ForeignKey("agency.id"), nullable=False)  # 🔗 ID Agenzia
    shop_id = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)  # 🔗 ID Negozio
    access_level = db.Column(db.String(50), nullable=False, default="partner")  # 🔑 Ruolo (partner, reseller, manager)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 🕒 Ultimo aggiornamento


# ✅ **Crea una nuova agenzia**
def create_agency(agency_name, email, phone=None, address=None, website=None):
    """
    Crea una nuova agenzia e la salva nel database.
    """
    try:
        new_agency = Agency(
            agency_name=agency_name,
            email=email,
            phone=phone,
            address=address,
            website=website,
        )
        db.session.add(new_agency)
        db.session.commit()
        return new_agency.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione dell'agenzia {agency_name}: {e}")
        return None


# ✅ **Crea un nuovo dipendente dell'agenzia**
def create_agency_employee(agency_id, email, password, name, surname, role, phone=None):
    """
    Crea un nuovo dipendente per un'agenzia.
    """
    try:
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
        return new_employee.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione del dipendente {email}: {e}")
        return None


# ✅ **Concedi accesso a un'agenzia per un negozio**
def grant_agency_access(agency_id, shop_id, access_level="partner"):
    """
    Concede accesso a un negozio per un'agenzia con un determinato livello di accesso.
    """
    try:
        new_access = AgencyStoreAccess(
            agency_id=agency_id,
            shop_id=shop_id,
            access_level=access_level,
        )
        db.session.add(new_access)
        db.session.commit()
        return new_access.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella concessione dell'accesso all'agenzia: {e}")
        return None


# 🔍 **Recupera tutte le agenzie**
def get_all_agencies():
    """
    Recupera tutte le agenzie registrate nel database.
    """
    try:
        return db.session.query(Agency).all()
    except Exception as e:
        logging.error(f"❌ Errore nel recupero di tutte le agenzie: {e}")
        return []


# 🔍 **Recupera i dipendenti di un'agenzia**
def get_agency_employees(agency_id):
    """
    Recupera tutti i dipendenti di una specifica agenzia.
    """
    try:
        return db.session.query(AgencyEmployee).filter_by(agency_id=agency_id).all()
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei dipendenti dell'agenzia {agency_id}: {e}")
        return []


# 🔍 **Verifica se un'agenzia ha accesso a un negozio**
def has_agency_access(agency_id, shop_id):
    """
    Verifica se un'agenzia ha accesso a un negozio specifico.
    """
    try:
        access = db.session.query(AgencyStoreAccess).filter_by(agency_id=agency_id, shop_id=shop_id).first()
        return access is not None
    except Exception as e:
        logging.error(f"❌ Errore nel controllo dell'accesso dell'agenzia: {e}")
        return False


# 🗑️ **Elimina un dipendente dell'agenzia**
def delete_agency_employee(employee_id):
    """
    Elimina un dipendente specifico di un'agenzia.
    """
    try:
        employee = db.session.get(AgencyEmployee, employee_id)
        if not employee:
            return False
        db.session.delete(employee)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione del dipendente {employee_id}: {e}")
        return False


# 🗑️ **Elimina un'agenzia e tutti i suoi dipendenti**
def delete_agency(agency_id):
    """
    Elimina un'agenzia e tutti i suoi dipendenti associati.
    """
    try:
        AgencyEmployee.query.filter_by(agency_id=agency_id).delete()
        agency = db.session.get(Agency, agency_id)
        if not agency:
            return False
        db.session.delete(agency)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione dell'agenzia {agency_id}: {e}")
        return False