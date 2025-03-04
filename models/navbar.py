from models.database import db
import logging
from datetime import datetime

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

# 🔍 **Recupera tutti i link della navbar per un negozio**
def get_navbar_links(shop_name):
    try:
        links = NavbarLink.query.filter_by(shop_name=shop_name).order_by(NavbarLink.position.asc()).all()
        return [link_to_dict(link) for link in links]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dei link per {shop_name}: {e}")
        return []

# ✅ **Crea un nuovo link nella navbar**
def create_navbar_link(shop_name, link_text, link_url, link_type, parent_id=None, position=None):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione del link '{link_text}' per {shop_name}: {e}")
        return None

# 🔄 **Aggiorna un link della navbar**
def update_navbar_link(link_id, shop_name, link_text, link_url, link_type, parent_id=None, position=None):
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento del link {link_id} per {shop_name}: {e}")
        return False

# ❌ **Elimina un link dalla navbar**
def delete_navbar_link(link_id, shop_name):
    try:
        link = NavbarLink.query.filter_by(id=link_id, shop_name=shop_name).first()
        if not link:
            return False

        db.session.delete(link)
        db.session.commit()
        logging.info(f"✅ Link {link_id} eliminato con successo per {shop_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione del link {link_id} per {shop_name}: {e}")
        return False

# ❌ **Elimina tutti i link della navbar per un determinato negozio**
def delete_all_navbar_links(shop_name):
    try:
        NavbarLink.query.filter_by(shop_name=shop_name).delete()
        db.session.commit()
        logging.info(f"✅ Tutti i link eliminati per {shop_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione di tutti i link per {shop_name}: {e}")
        return False

# 🔄 **Aggiorna la posizione dei link nella navbar**
def reorder_navbar_links(shop_name, order_list):
    try:
        for position, link_id in enumerate(order_list, start=1):
            link = NavbarLink.query.filter_by(id=link_id, shop_name=shop_name).first()
            if link:
                link.position = position
                link.updated_at = datetime.utcnow()

        db.session.commit()
        logging.info(f"✅ Navbar ordinata con successo per {shop_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nel riordinamento della navbar per {shop_name}: {e}")
        return False

# 📌 **Helper per convertire un link in dizionario**
def link_to_dict(link):
    return {
        "id": link.id,
        "shop_name": link.shop_name,
        "link_text": link.link_text,
        "link_url": link.link_url,
        "link_type": link.link_type,
        "parent_id": link.parent_id,
        "position": link.position,
        "created_at": link.created_at,
        "updated_at": link.updated_at,
    }