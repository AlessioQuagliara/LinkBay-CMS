from models.database import db
import logging
from functools import wraps
from datetime import datetime

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# ✅ **Crea un nuovo addon**
@handle_db_errors
def create_addon(name, description, price, addon_type):
    new_addon = CMSAddon(name=name, description=description, price=price, addon_type=addon_type)
    db.session.add(new_addon)
    db.session.commit()
    logging.info(f"✅ Addon '{name}' creato con successo")
    return new_addon.id

# 🔍 **Recupera tutti gli addon di un certo tipo**
@handle_db_errors
def get_addons_by_type(addon_type):
    addons = CMSAddon.query.filter_by(addon_type=addon_type).all()
    return [model_to_dict(addon) for addon in addons]

# ✅ **Seleziona un addon per uno shop**
@handle_db_errors
def select_addon(shop_name, addon_id, addon_type):
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
    logging.info(f"✅ Addon {addon_id} selezionato per lo shop {shop_name}")
    return True

# 💳 **Acquista un addon per uno shop**
@handle_db_errors
def purchase_addon(shop_name, addon_id, addon_type):
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
    logging.info(f"✅ Addon {addon_id} acquistato per lo shop {shop_name}")
    return True

# 🔍 **Ottieni lo stato di un addon specifico per uno shop**
@handle_db_errors
def get_addon_status(shop_name, addon_id):
    addon = ShopAddon.query.filter_by(shop_name=shop_name, addon_id=addon_id).first()
    return addon.status if addon else None

# 🔄 **Aggiorna lo stato di un addon per uno shop**
@handle_db_errors
def update_shop_addon_status(shop_name, addon_id, addon_type, status):
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
    logging.info(f"✅ Stato dell'addon {addon_id} aggiornato a '{status}' per lo shop {shop_name}")
    return True

# ❌ **Deseleziona altri addon dello stesso tipo (eccetto quelli "purchased")**
@handle_db_errors
def deselect_other_addons(shop_name, addon_id, addon_type):
    ShopAddon.query.filter(
        ShopAddon.shop_name == shop_name,
        ShopAddon.addon_type == addon_type,
        ShopAddon.addon_id != addon_id,
        ShopAddon.status != "purchased"
    ).update({"status": "deselected", "updated_at": datetime.utcnow()})

    db.session.commit()
    logging.info(f"✅ Altri addon deselezionati per lo shop {shop_name}")

# 🔍 **Ottieni l'addon selezionato per uno shop**
@handle_db_errors
def get_selected_addon_for_shop(shop_name, addon_type):
    addon = db.session.query(CMSAddon.name, CMSAddon.description, CMSAddon.price, CMSAddon.addon_type).join(
        ShopAddon, ShopAddon.addon_id == CMSAddon.id
    ).filter(
        ShopAddon.shop_name == shop_name,
        ShopAddon.addon_type == addon_type,
        ShopAddon.status == "selected"
    ).first()

    return addon._asdict() if addon else None