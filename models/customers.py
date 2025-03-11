from models.database import db
import logging
from functools import wraps
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per i Clienti**
class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Nome del negozio
    first_name = db.Column(db.String(255), nullable=False)  # 🧑 Nome
    last_name = db.Column(db.String(255), nullable=False)  # 🧑 Cognome
    email = db.Column(db.String(255), unique=True, nullable=False)  # 📧 Email
    password = db.Column(db.String(255), nullable=False)  # 🔒 Password (hashed)
    phone = db.Column(db.String(50), nullable=True)  # 📞 Telefono
    address = db.Column(db.String(255), nullable=True)  # 🏠 Indirizzo
    city = db.Column(db.String(100), nullable=True)  # 🏙️ Città
    state = db.Column(db.String(100), nullable=True)  # 🌍 Stato/Regione
    postal_code = db.Column(db.String(20), nullable=True)  # 📮 CAP
    country = db.Column(db.String(100), nullable=True)  # 🌍 Paese
    codice_fiscale = db.Column(db.String(50), nullable=True)  # 🏛️ Codice Fiscale
    partita_iva = db.Column(db.String(50), nullable=True)  # 🏛️ Partita IVA
    pec = db.Column(db.String(255), nullable=True)  # 📧 PEC
    codice_destinatario = db.Column(db.String(50), nullable=True)  # 📩 Codice Destinatario
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Data di aggiornamento

    def __repr__(self):
        return f"<Customer {self.first_name} {self.last_name} ({self.email})>"
    
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

# 🔍 **Recupera un cliente per ID**
@handle_db_errors
def get_customer_by_id(customer_id):
    customer = Customer.query.get(customer_id)
    return model_to_dict(customer) if customer else None

# ✅ **Crea un nuovo cliente**
@handle_db_errors
def create_customer(data):
    new_customer = Customer(
        shop_name=data["shop_name"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        phone=data.get("phone"),
        address=data.get("address"),
        city=data.get("city"),
        state=data.get("state"),
        postal_code=data.get("postal_code"),
        country=data.get("country"),
        password=generate_password_hash(data["password"]),  # 🔒 Hash della password
        codice_fiscale=data.get("codice_fiscale"),
        partita_iva=data.get("partita_iva"),
        pec=data.get("pec"),
        codice_destinatario=data.get("codice_destinatario"),
    )
    db.session.add(new_customer)
    db.session.commit()
    logging.info(f"✅ Cliente {data['first_name']} {data['last_name']} creato con successo")
    return new_customer.id

# 🔄 **Recupera tutti i clienti di un negozio**
@handle_db_errors
def get_all_customers(shop_name):
    customers = Customer.query.filter_by(shop_name=shop_name).all()
    return [model_to_dict(customer) for customer in customers]

# ✏️ **Aggiorna un cliente**
@handle_db_errors
def update_customer(customer_id, shop_name, data):
    customer = Customer.query.filter_by(id=customer_id, shop_name=shop_name).first()
    if not customer:
        return False

    # Aggiorna i dati solo se forniti
    customer.first_name = data.get("first_name", customer.first_name)
    customer.last_name = data.get("last_name", customer.last_name)
    customer.email = data.get("email", customer.email)
    if "password" in data:
        customer.password = generate_password_hash(data["password"])  # 🔒 Hash della password aggiornata
    customer.phone = data.get("phone", customer.phone)
    customer.address = data.get("address", customer.address)
    customer.city = data.get("city", customer.city)
    customer.state = data.get("state", customer.state)
    customer.postal_code = data.get("postal_code", customer.postal_code)
    customer.country = data.get("country", customer.country)
    customer.codice_fiscale = data.get("codice_fiscale", customer.codice_fiscale)
    customer.partita_iva = data.get("partita_iva", customer.partita_iva)
    customer.pec = data.get("pec", customer.pec)
    customer.codice_destinatario = data.get("codice_destinatario", customer.codice_destinatario)

    db.session.commit()
    logging.info(f"✅ Cliente {customer.first_name} {customer.last_name} aggiornato con successo")
    return True

# ❌ **Elimina un cliente**
@handle_db_errors
def delete_customer(customer_id, shop_name):
    customer = Customer.query.filter_by(id=customer_id, shop_name=shop_name).first()
    if not customer:
        return False

    db.session.delete(customer)
    db.session.commit()
    logging.info(f"✅ Cliente {customer.first_name} {customer.last_name} eliminato con successo")
    return True

# 🔒 **Verifica la password di un cliente**
@handle_db_errors
def verify_customer_password(customer_id, provided_password):
    customer = Customer.query.get(customer_id)
    if customer and check_password_hash(customer.password, provided_password):
        return True
    return False