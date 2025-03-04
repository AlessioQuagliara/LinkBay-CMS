from models.database import db
import logging
from datetime import datetime

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

# 🔍 **Recupera tutti i domini di un negozio**
def get_all_domains(shop_id):
    try:
        domains = Domain.query.filter_by(shop_id=shop_id).all()
        return [domain_to_dict(domain) for domain in domains]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei domini per Shop ID {shop_id}: {e}")
        return []

# 🔎 **Recupera un dominio specifico per ID**
def get_domain_by_id(domain_id):
    try:
        domain = Domain.query.get(domain_id)
        return domain_to_dict(domain) if domain else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del dominio ID {domain_id}: {e}")
        return None

# ✅ **Crea un nuovo dominio**
def create_domain(data):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione del dominio: {e}")
        return None

# 🔄 **Aggiorna i record DNS di un dominio**
def update_domain_records(domain_id, data):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento dei record DNS per dominio ID {domain_id}: {e}")
        return False

# ❌ **Elimina un dominio**
def delete_domain(domain_id):
    try:
        domain = Domain.query.get(domain_id)
        if not domain:
            return False

        db.session.delete(domain)
        db.session.commit()
        logging.info(f"✅ Dominio {domain.domain} eliminato con successo")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione del dominio ID {domain_id}: {e}")
        return False

# 🔎 **Recupera un dominio per nome**
def get_domain_by_name(domain_name):
    try:
        domain = Domain.query.filter_by(domain=domain_name).first()
        return domain_to_dict(domain) if domain else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero del dominio {domain_name}: {e}")
        return None

# 🔄 **Aggiorna lo stato di un dominio**
def update_domain_status(domain_id, status):
    try:
        domain = Domain.query.get(domain_id)
        if not domain:
            return False

        domain.status = status
        db.session.commit()
        logging.info(f"✅ Stato del dominio {domain.domain} aggiornato a {status}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento dello stato del dominio ID {domain_id}: {e}")
        return False

# 📌 **Helper per convertire un dominio in dizionario**
def domain_to_dict(domain):
    return {
        "id": domain.id,
        "shop_id": domain.shop_id,
        "domain": domain.domain,
        "dns_provider": domain.dns_provider,
        "record_a": domain.record_a,
        "record_cname": domain.record_cname,
        "record_mx": domain.record_mx,
        "record_txt": domain.record_txt,
        "record_ns": domain.record_ns,
        "record_aaaa": domain.record_aaaa,
        "record_srv": domain.record_srv,
        "status": domain.status,
        "created_at": domain.created_at,
        "updated_at": domain.updated_at,
    }