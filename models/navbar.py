from models.database import db
import logging
from functools import wraps
from datetime import datetime

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per i Link della Navbar**
class NavbarLink(db.Model):
    __tablename__ = "navbar_links"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Identificatore del negozio
    link_text = db.Column(db.String(255), nullable=False)  # 🔗 Testo del link
    link_url = db.Column(db.String(512), nullable=False)  # 🌍 URL di destinazione
    link_type = db.Column(db.String(100), nullable=False)  # 🔖 Tipo di link (interno, esterno, dropdown)
    parent_id = db.Column(db.Integer, db.ForeignKey("navbar_links.id"), nullable=True)  # 📌 Submenu
    position = db.Column(db.Integer, nullable=True)  # 📊 Posizione nella navbar
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    def __repr__(self):
        return f"<NavbarLink {self.id} - {self.link_text}>"
    
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

# 🔍 **Recupera tutti i link della navbar per un negozio**
@handle_db_errors
def get_navbar_links(shop_name):
    links = NavbarLink.query.filter_by(shop_name=shop_name).order_by(NavbarLink.position.asc()).all()
    return [model_to_dict(link) for link in links]

# ✅ **Crea un nuovo link nella navbar**
@handle_db_errors
def create_navbar_link(shop_name, link_text, link_url, link_type, parent_id=None, position=None):
    new_link = NavbarLink(
        shop_name=shop_name,
        link_text=link_text,
        link_url=link_url,
        link_type=link_type,
        parent_id=parent_id,
        position=position,
    )
    db.session.add(new_link)
    db.session.commit()
    logging.info(f"✅ Link '{link_text}' creato con successo per {shop_name}")
    return new_link.id

# 🔄 **Aggiorna un link della navbar**
@handle_db_errors
def update_navbar_link(link_id, shop_name, link_text, link_url, link_type, parent_id=None, position=None):
    link = NavbarLink.query.filter_by(id=link_id, shop_name=shop_name).first()
    if not link:
        return False

    link.link_text = link_text
    link.link_url = link_url
    link.link_type = link_type
    link.parent_id = parent_id
    link.position = position
    link.updated_at = datetime.utcnow()

    db.session.commit()
    logging.info(f"✅ Link '{link_text}' aggiornato con successo per {shop_name}")
    return True

# ❌ **Elimina un link dalla navbar**
@handle_db_errors
def delete_navbar_link(link_id, shop_name):
    link = NavbarLink.query.filter_by(id=link_id, shop_name=shop_name).first()
    if not link:
        return False

    db.session.delete(link)
    db.session.commit()
    logging.info(f"✅ Link {link_id} eliminato con successo per {shop_name}")
    return True

# ❌ **Elimina tutti i link della navbar per un determinato negozio**
@handle_db_errors
def delete_all_navbar_links(shop_name):
    NavbarLink.query.filter_by(shop_name=shop_name).delete()
    db.session.commit()
    logging.info(f"✅ Tutti i link eliminati per {shop_name}")
    return True

# 🔄 **Aggiorna la posizione dei link nella navbar**
@handle_db_errors
def reorder_navbar_links(shop_name, order_list):
    for position, link_id in enumerate(order_list, start=1):
        link = NavbarLink.query.filter_by(id=link_id, shop_name=shop_name).first()
        if link:
            link.position = position
            link.updated_at = datetime.utcnow()

    db.session.commit()
    logging.info(f"✅ Navbar ordinata con successo per {shop_name}")
    return True