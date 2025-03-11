from models.database import db
import logging
from functools import wraps
from datetime import datetime

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per i Domini**
class Domain(db.Model):
    __tablename__ = "domains"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_id = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)  # 🏪 Collegamento con ShopList
    domain = db.Column(db.String(255), unique=True, nullable=False)  # 🌍 Nome del dominio
    dns_provider = db.Column(db.String(255), nullable=True)  # 🖥️ Provider DNS (Cloudflare, GoDaddy, ecc.)
    record_a = db.Column(db.String(255), nullable=True)  # 🔧 Record A (IP principale)
    record_cname = db.Column(db.String(255), nullable=True)  # 🔗 CNAME (Alias)
    record_mx = db.Column(db.String(255), nullable=True)  # 📬 Record MX (Mail Exchange)
    record_txt = db.Column(db.String(255), nullable=True)  # 🔍 Record TXT (Verifica, SPF, DKIM)
    record_ns = db.Column(db.String(255), nullable=True)  # 🏷️ Record NS (Nameserver)
    record_aaaa = db.Column(db.String(255), nullable=True)  # 🌐 Record AAAA (IPv6)
    record_srv = db.Column(db.String(255), nullable=True)  # 🔄 Record SRV (Servizi speciali)
    status = db.Column(db.String(50), nullable=False, default="pending")  # ⏳ Stato (active, pending, disabled)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Data di aggiornamento

    def __repr__(self):
        return f"<Domain {self.domain} (Status: {self.status})>"

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

# 🔍 **Recupera tutti i domini di un negozio**
@handle_db_errors
def get_all_domains(shop_id):
    domains = Domain.query.filter_by(shop_id=shop_id).all()
    return [model_to_dict(domain) for domain in domains]

# 🔎 **Recupera un dominio specifico per ID**
@handle_db_errors
def get_domain_by_id(domain_id):
    domain = Domain.query.get(domain_id)
    return model_to_dict(domain) if domain else None

# ✅ **Crea un nuovo dominio**
@handle_db_errors
def create_domain(data):
    new_domain = Domain(
        shop_id=data["shop_id"],
        domain=data["domain"],
        dns_provider=data.get("dns_provider"),
        record_a=data.get("record_a"),
        record_cname=data.get("record_cname"),
        record_mx=data.get("record_mx"),
        record_txt=data.get("record_txt"),
        record_ns=data.get("record_ns"),
        record_aaaa=data.get("record_aaaa"),
        record_srv=data.get("record_srv"),
        status=data.get("status", "pending"),
    )
    db.session.add(new_domain)
    db.session.commit()
    logging.info(f"✅ Dominio {data['domain']} creato con successo")
    return new_domain.id

# 🔄 **Aggiorna i record DNS di un dominio**
@handle_db_errors
def update_domain_records(domain_id, data):
    domain = Domain.query.get(domain_id)
    if not domain:
        return False

    domain.record_a = data.get("record_a", domain.record_a)
    domain.record_cname = data.get("record_cname", domain.record_cname)
    domain.record_mx = data.get("record_mx", domain.record_mx)
    domain.record_txt = data.get("record_txt", domain.record_txt)
    domain.record_ns = data.get("record_ns", domain.record_ns)
    domain.record_aaaa = data.get("record_aaaa", domain.record_aaaa)
    domain.record_srv = data.get("record_srv", domain.record_srv)

    db.session.commit()
    logging.info(f"✅ Record DNS aggiornati per il dominio {domain.domain}")
    return True

# ❌ **Elimina un dominio**
@handle_db_errors
def delete_domain(domain_id):
    domain = Domain.query.get(domain_id)
    if not domain:
        return False

    db.session.delete(domain)
    db.session.commit()
    logging.info(f"✅ Dominio {domain.domain} eliminato con successo")
    return True

# 🔎 **Recupera un dominio per nome**
@handle_db_errors
def get_domain_by_name(domain_name):
    domain = Domain.query.filter_by(domain=domain_name).first()
    return model_to_dict(domain) if domain else None

# 🔄 **Aggiorna lo stato di un dominio**
@handle_db_errors
def update_domain_status(domain_id, status):
    domain = Domain.query.get(domain_id)
    if not domain:
        return False

    domain.status = status
    db.session.commit()
    logging.info(f"✅ Stato del dominio {domain.domain} aggiornato a {status}")
    return True