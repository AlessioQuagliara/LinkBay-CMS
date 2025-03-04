from models.database import db
import logging
from datetime import datetime

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

# 🔹 **Modello per gli Addon**
class CMSAddon(db.Model):
    __tablename__ = "cms_addons"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco dell'addon
    name = db.Column(db.String(255), nullable=False)  # 📛 Nome dell'addon
    description = db.Column(db.String(255), nullable=True)  # 📜 Descrizione
    price = db.Column(db.Float, nullable=False)  # 💰 Prezzo
    addon_type = db.Column(db.String(255), nullable=False)  # 📌 Tipo di addon
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    def __repr__(self):
        return f"<CMSAddon {self.name} (ID: {self.id})>"


# 🔹 **Modello per gli Addon associati ai negozi**
class ShopAddon(db.Model):
    __tablename__ = "shop_addons"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco della relazione
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Nome dello shop
    addon_id = db.Column(db.Integer, db.ForeignKey("cms_addons.id"), nullable=False)  # 🔗 Collegamento con CMSAddon
    addon_type = db.Column(db.String(255), nullable=False)  # 📌 Tipo di addon
    status = db.Column(db.String(50), nullable=False)  # 🟢 Stato dell'addon (selected, deselected, purchased)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    def __repr__(self):
        return f"<ShopAddon Shop: {self.shop_name}, Addon ID: {self.addon_id}, Status: {self.status}>"

# ✅ **Crea un nuovo addon**
def create_addon(name, description, price, addon_type):
    try:
        new_addon = CMSAddon(name=name, description=description, price=price, type=addon_type)
        db.session.add(new_addon)
        db.session.commit()
        logging.info(f"✅ Addon '{name}' creato con successo")
        return new_addon.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione dell'addon '{name}': {e}")
        return None

# 🔍 **Recupera tutti gli addon di un certo tipo**
def get_addons_by_type(addon_type):
    try:
        addons = CMSAddon.query.filter_by(type=addon_type).all()
        return [addon_to_dict(addon) for addon in addons]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero degli addon di tipo '{addon_type}': {e}")
        return []

# ✅ **Seleziona un addon per uno shop**
def select_addon(shop_name, addon_id, addon_type):
    try:
        # Controlla se l'addon è già acquistato
        existing_addon = ShopAddon.query.filter_by(shop_name=shop_name, addon_id=addon_id).first()

        if existing_addon and existing_addon.status == "purchased":
            return False  # 🛑 L'addon è già acquistato

        # Deseleziona altri addon dello stesso tipo per il negozio (eccetto quelli "purchased")
        ShopAddon.query.filter(
            ShopAddon.shop_name == shop_name,
            ShopAddon.addon_type == addon_type,
            ShopAddon.status == "selected"
        ).update({"status": "deselected", "updated_at": datetime.utcnow()})

        # Seleziona l'addon
        if existing_addon:
            existing_addon.status = "selected"
            existing_addon.updated_at = datetime.utcnow()
        else:
            new_selection = ShopAddon(
                shop_name=shop_name, addon_id=addon_id, addon_type=addon_type, status="selected"
            )
            db.session.add(new_selection)

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella selezione dell'addon {addon_id} per lo shop {shop_name}: {e}")
        return False

# 💳 **Acquista un addon per uno shop**
def purchase_addon(shop_name, addon_id, addon_type):
    try:
        existing_addon = ShopAddon.query.filter_by(shop_name=shop_name, addon_id=addon_id).first()

        if existing_addon:
            existing_addon.status = "purchased"
            existing_addon.updated_at = datetime.utcnow()
        else:
            new_purchase = ShopAddon(
                shop_name=shop_name, addon_id=addon_id, addon_type=addon_type, status="purchased"
            )
            db.session.add(new_purchase)

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'acquisto dell'addon {addon_id} per lo shop {shop_name}: {e}")
        return False

# 🔍 **Ottieni lo stato di un addon specifico per uno shop**
def get_addon_status(shop_name, addon_id):
    try:
        addon = ShopAddon.query.filter_by(shop_name=shop_name, addon_id=addon_id).first()
        return addon.status if addon else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dello stato dell'addon {addon_id} per lo shop {shop_name}: {e}")
        return None

# 🔄 **Aggiorna lo stato di un addon per uno shop**
def update_shop_addon_status(shop_name, addon_id, addon_type, status):
    try:
        existing_addon = ShopAddon.query.filter_by(shop_name=shop_name, addon_id=addon_id).first()

        if existing_addon:
            existing_addon.status = status
            existing_addon.updated_at = datetime.utcnow()
        else:
            new_status = ShopAddon(
                shop_name=shop_name, addon_id=addon_id, addon_type=addon_type, status=status
            )
            db.session.add(new_status)

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento dello stato dell'addon {addon_id} per lo shop {shop_name}: {e}")
        return False

# ❌ **Deseleziona altri addon dello stesso tipo (eccetto quelli "purchased")**
def deselect_other_addons(shop_name, addon_id, addon_type):
    try:
        ShopAddon.query.filter(
            ShopAddon.shop_name == shop_name,
            ShopAddon.addon_type == addon_type,
            ShopAddon.addon_id != addon_id,
            ShopAddon.status != "purchased"
        ).update({"status": "deselected", "updated_at": datetime.utcnow()})

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella deselezione degli altri addon per lo shop {shop_name}: {e}")

# 🔍 **Ottieni l'addon selezionato per uno shop**
def get_selected_addon_for_shop(shop_name, addon_type):
    try:
        addon = db.session.query(CMSAddon.name, CMSAddon.description, CMSAddon.price, CMSAddon.type).join(
            ShopAddon, ShopAddon.addon_id == CMSAddon.id
        ).filter(
            ShopAddon.shop_name == shop_name,
            ShopAddon.addon_type == addon_type,
            ShopAddon.status == "selected"
        ).first()

        return addon._asdict() if addon else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero dell'addon selezionato per lo shop {shop_name}: {e}")
        return None

# 📌 **Funzione per convertire un oggetto CMSAddon in un dizionario**
def addon_to_dict(addon):
    return {
        "id": addon.id,
        "name": addon.name,
        "description": addon.description,
        "price": addon.price,
        "type": addon.type,
        "created_at": addon.created_at,
        "updated_at": addon.updated_at,
    }