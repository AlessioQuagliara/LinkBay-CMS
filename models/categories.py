from models.database import db
import logging
from functools import wraps
from datetime import datetime

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per le Categorie**
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco della categoria
    shop_name = db.Column(db.String(255), nullable=False)  # 🏪 Nome dello shop
    name = db.Column(db.String(255), nullable=False)  # 🏷️ Nome della categoria
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)  # 🔗 ID della categoria padre

    # Relazione per le sotto-categorie
    subcategories = db.relationship("Category", backref=db.backref("parent", remote_side=[id]), lazy=True)

    def __repr__(self):
        return f"<Category {self.name} (ID: {self.id})>"
    
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

# ✅ **Crea una nuova categoria**
@handle_db_errors
def create_category(shop_name, name, parent_id=None):
    new_category = Category(shop_name=shop_name, name=name, parent_id=parent_id)
    db.session.add(new_category)
    db.session.commit()
    logging.info(f"✅ Categoria '{name}' creata con successo per lo shop '{shop_name}'")
    return new_category.id

# 🔍 **Recupera tutte le categorie di uno shop**
@handle_db_errors
def get_all_categories(shop_name):
    categories = Category.query.filter_by(shop_name=shop_name).all()
    return [model_to_dict(cat) for cat in categories]

# 🔍 **Recupera una categoria tramite ID**
@handle_db_errors
def get_category_by_id(category_id):
    category = Category.query.get(category_id)
    return model_to_dict(category) if category else None

# 🔄 **Aggiorna una categoria esistente**
@handle_db_errors
def update_category(category_id, name=None, parent_id=None):
    category = Category.query.get(category_id)
    if not category:
        return False

    if name:
        category.name = name
    if parent_id is not None:
        category.parent_id = parent_id

    db.session.commit()
    logging.info(f"✅ Categoria con ID {category_id} aggiornata con successo")
    return True

# 🗑️ **Elimina una categoria**
@handle_db_errors
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return False

    db.session.delete(category)
    db.session.commit()
    logging.info(f"🗑️ Categoria con ID {category_id} eliminata con successo")
    return True

# 🔍 **Recupera tutte le sotto-categorie di una categoria padre**
@handle_db_errors
def get_subcategories(parent_id):
    subcategories = Category.query.filter_by(parent_id=parent_id).all()
    return [model_to_dict(cat) for cat in subcategories]