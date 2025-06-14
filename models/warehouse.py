from models.database import db
from datetime import datetime
import logging
from functools import wraps
from sqlalchemy import UniqueConstraint, Index

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass  # Evita import diretto per circolarità


# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔄 Decoratore per la gestione degli errori del database
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

# 🔹 **Modello per i Magazzini**
class Warehouse(db.Model):
    __tablename__ = "warehouses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco del magazzino
    shop_id = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)  # 🔗 ID dello shop
    name = db.Column(db.String(255), nullable=False)  # 📛 Nome del magazzino
    address = db.Column(db.String(255), nullable=True)  # 🏠 Indirizzo del magazzino
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento
    inventories = db.relationship("Inventory", backref="warehouse", lazy="dynamic")
    locations = db.relationship(
        "Location",
        back_populates="warehouse",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Warehouse {self.name} (Shop ID: {self.shop_id})>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    

# 🔄 **CRUD Functions for Warehouse**

@handle_db_errors
def create_warehouse(shop_id, name, address=None):
    """Crea un nuovo magazzino per lo shop specificato."""
    warehouse = Warehouse(shop_id=shop_id, name=name, address=address)
    db.session.add(warehouse)
    db.session.commit()
    logging.info(f"✅ Magazzino '{name}' creato per Shop ID {shop_id}")
    return warehouse.id

@handle_db_errors
def get_all_warehouses(shop_id):
    """Recupera tutti i magazzini di uno shop."""
    return Warehouse.query.filter_by(shop_id=shop_id).all()

@handle_db_errors
def get_warehouse_by_id(warehouse_id):
    """Recupera un magazzino per ID."""
    return Warehouse.query.get(warehouse_id)

@handle_db_errors
def update_warehouse(warehouse_id, **kwargs):
    """Aggiorna i campi di un magazzino."""
    warehouse = Warehouse.query.get(warehouse_id)
    if not warehouse:
        return None
    for key, value in kwargs.items():
        if hasattr(warehouse, key):
            setattr(warehouse, key, value)
    db.session.commit()
    logging.info(f"✅ Magazzino ID {warehouse_id} aggiornato")
    return warehouse

@handle_db_errors
def delete_warehouse(warehouse_id):
    """Elimina un magazzino."""
    warehouse = Warehouse.query.get(warehouse_id)
    if not warehouse:
        return False
    db.session.delete(warehouse)
    db.session.commit()
    logging.info(f"✅ Magazzino ID {warehouse_id} eliminato")
    return True

# 🔹 **Modello per le Ubicazioni**
class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco dell'ubicazione
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=False)  # 🔗 ID del magazzino
    code = db.Column(db.String(100), nullable=False)  # 🏷️ Codice dell'ubicazione interna
    description = db.Column(db.String(255), nullable=True)  # 📝 Descrizione dell'ubicazione
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento
    warehouse = db.relationship("Warehouse", back_populates="locations", lazy=True)

    __table_args__ = (
        UniqueConstraint('warehouse_id', 'code', name='ux_locations_warehouse_code'),
    )

    def __repr__(self):
        return f"<Location {self.code} (Warehouse ID: {self.warehouse_id})>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# 🔹 **Modello per le Giacenze (Inventory)**
class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco della giacenza
    shop_id = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)  # 🔗 ID dello shop
    variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id"), nullable=False)  # 🔗 ID della variante prodotto
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=False)  # 🔗 ID del magazzino
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=True)  # 🔗 ID dell'ubicazione
    quantity = db.Column(db.Integer, nullable=False, default=0)  # 📦 Quantità disponibile
    reserved = db.Column(db.Integer, nullable=False, default=0)  # 🔒 Quantità riservata
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 🔄 Ultimo aggiornamento

    supplier_cost = db.Column(db.Numeric(10,2), nullable=True)
    min_stock     = db.Column(db.Integer, nullable=True)
    reorder_point = db.Column(db.Integer, nullable=True)

    # Relazione verso ProductVariant (evita import diretto per circolarità)
    variant = db.relationship("ProductVariant", back_populates="inventories")

    __table_args__ = (
        UniqueConstraint('shop_id', 'variant_id', 'warehouse_id', 'location_id', name='ux_inventory_shop_variant_wh_loc'),
    )

    def __repr__(self):
        return f"<Inventory Shop {self.shop_id} - Variant {self.variant_id} @ Warehouse {self.warehouse_id} Location {self.location_id}>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    

# 🔄 **CRUD Functions for Location**

@handle_db_errors
def create_location(warehouse_id, code, description=None):
    """Crea una nuova ubicazione in un magazzino."""
    loc = Location(warehouse_id=warehouse_id, code=code, description=description)
    db.session.add(loc)
    db.session.commit()
    logging.info(f"✅ Ubicazione '{code}' creata per Warehouse ID {warehouse_id}")
    return loc.id

@handle_db_errors
def get_all_locations(warehouse_id):
    """Recupera tutte le ubicazioni di un magazzino."""
    return Location.query.filter_by(warehouse_id=warehouse_id).all()

@handle_db_errors
def get_location_by_id(location_id):
    """Recupera un'ubicazione per ID."""
    return Location.query.get(location_id)

@handle_db_errors
def update_location(location_id, **kwargs):
    """Aggiorna i campi di un'ubicazione."""
    loc = Location.query.get(location_id)
    if not loc:
        return None
    for key, value in kwargs.items():
        if hasattr(loc, key):
            setattr(loc, key, value)
    db.session.commit()
    logging.info(f"✅ Ubicazione ID {location_id} aggiornata")
    return loc

@handle_db_errors
def delete_location(location_id):
    """Elimina un'ubicazione."""
    loc = Location.query.get(location_id)
    if not loc:
        return False
    db.session.delete(loc)
    db.session.commit()
    logging.info(f"✅ Ubicazione ID {location_id} eliminata")
    return True

# 🔄 **CRUD Functions for Inventory**

@handle_db_errors
def create_inventory(shop_id, variant_id, warehouse_id, location_id=None, quantity=0, reserved=0):
    """Crea una nuova giacenza."""
    inv = Inventory(
        shop_id=shop_id,
        variant_id=variant_id,
        warehouse_id=warehouse_id,
        location_id=location_id,
        quantity=quantity,
        reserved=reserved
    )
    db.session.add(inv)
    db.session.commit()
    logging.info(f"✅ Inventory creato per Shop ID {shop_id}, Variant ID {variant_id}")
    return inv.id

@handle_db_errors
def get_inventory_by_shop(shop_id):
    """Recupera tutte le giacenze di uno shop."""
    return Inventory.query.filter_by(shop_id=shop_id).all()

@handle_db_errors
def get_inventory_by_variant(shop_id, variant_id):
    """Recupera le giacenze di una variante in uno shop."""
    return Inventory.query.filter_by(shop_id=shop_id, variant_id=variant_id).all()

@handle_db_errors
def update_inventory(inventory_id, **kwargs):
    """Aggiorna i campi di una giacenza."""
    inv = Inventory.query.get(inventory_id)
    if not inv:
        return None
    for key, value in kwargs.items():
        if hasattr(inv, key):
            setattr(inv, key, value)
    db.session.commit()
    logging.info(f"✅ Inventory ID {inventory_id} aggiornato")
    return inv

@handle_db_errors
def delete_inventory(inventory_id):
    """Elimina una giacenza."""
    inv = Inventory.query.get(inventory_id)
    if not inv:
        return False
    db.session.delete(inv)
    db.session.commit()
    logging.info(f"✅ Inventory ID {inventory_id} eliminato")
    return True


# 📦 **Movimenti di Magazzino**
from sqlalchemy import Index

class InventoryMovement(db.Model):
    __tablename__ = "inventory_movements"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shop_id       = db.Column(db.Integer, db.ForeignKey("ShopList.id"), nullable=False)
    inventory_id  = db.Column(db.Integer, db.ForeignKey("inventory.id"), nullable=False)
    variant_id    = db.Column(db.Integer, db.ForeignKey("product_variants.id"), nullable=True)
    movement_type = db.Column(db.String(50), nullable=False)  # es. 'ingresso', 'uscita', 'rettifica'
    quantity      = db.Column(db.Integer, nullable=False)
    reason        = db.Column(db.String(255), nullable=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    source        = db.Column(db.String(100), nullable=True)
    document_ref  = db.Column(db.String(100), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('ix_movements_shop_inventory', 'shop_id', 'inventory_id'),
    )

    def __repr__(self):
        return f"<InventoryMovement {self.id} – Inventory {self.inventory_id} – Type {self.movement_type}>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

@handle_db_errors
def create_inventory_movement(shop_id, inventory_id, variant_id=None, movement_type='ingresso', quantity=0, reason=None, user_id=None, source='manual', document_ref=None):
    movement = InventoryMovement(
        shop_id=shop_id,
        inventory_id=inventory_id,
        variant_id=variant_id,
        movement_type=movement_type,
        quantity=quantity,
        reason=reason,
        user_id=user_id,
        source=source,
        document_ref=document_ref
    )
    db.session.add(movement)

    # Aggiorna giacenza
    inv = Inventory.query.get(inventory_id)
    if not inv:
        inv = Inventory(shop_id=shop_id, variant_id=variant_id, warehouse_id=1, quantity=0)
        db.session.add(inv)

    if movement_type == 'ingresso':
        inv.quantity += quantity
    elif movement_type == 'uscita':
        inv.quantity -= quantity
    elif movement_type == 'rettifica':
        inv.quantity = quantity

    db.session.commit()
    logging.info(f"📦 Movimento '{movement_type}' registrato per Variante {variant_id} (Inventory ID: {inventory_id})")
    return movement.id