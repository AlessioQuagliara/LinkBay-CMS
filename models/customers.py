from models.database import db
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

# 🔍 **Recupera un cliente per ID**
def get_customer_by_id(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        return customer_to_dict(customer) if customer else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del cliente ID {customer_id}: {e}")
        return None

# ✅ **Crea un nuovo cliente**
def create_customer(data):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione del cliente: {e}")
        return None

# 🔄 **Recupera tutti i clienti di un negozio**
def get_all_customers(shop_name):
    try:
        customers = Customer.query.filter_by(shop_name=shop_name).all()
        return [customer_to_dict(customer) for customer in customers]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei clienti per {shop_name}: {e}")
        return []

# ✏️ **Aggiorna un cliente**
def update_customer(customer_id, shop_name, data):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento del cliente: {e}")
        return False

# ❌ **Elimina un cliente**
def delete_customer(customer_id, shop_name):
    try:
        customer = Customer.query.filter_by(id=customer_id, shop_name=shop_name).first()
        if not customer:
            return False

        db.session.delete(customer)
        db.session.commit()
        logging.info(f"✅ Cliente {customer.first_name} {customer.last_name} eliminato con successo")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione del cliente: {e}")
        return False

# 🔒 **Verifica la password di un cliente**
def verify_customer_password(customer_id, provided_password):
    try:
        customer = Customer.query.get(customer_id)
        if customer and check_password_hash(customer.password, provided_password):
            return True
        return False
    except Exception as e:
        logging.error(f"❌ Errore nella verifica della password per il cliente ID {customer_id}: {e}")
        return False

# 📌 **Helper per convertire un cliente in dizionario**
def customer_to_dict(customer):
    return {
        "id": customer.id,
        "shop_name": customer.shop_name,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "city": customer.city,
        "state": customer.state,
        "postal_code": customer.postal_code,
        "country": customer.country,
        "codice_fiscale": customer.codice_fiscale,
        "partita_iva": customer.partita_iva,
        "pec": customer.pec,
        "codice_destinatario": customer.codice_destinatario,
        "created_at": customer.created_at,
        "updated_at": customer.updated_at,
    }