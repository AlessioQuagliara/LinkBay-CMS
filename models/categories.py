from models.database import db
import logging

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

# ✅ **Crea una nuova categoria**
def create_category(shop_name, name, parent_id=None):
    """
    Crea una nuova categoria per uno shop.
    """
    try:
        new_category = Category(shop_name=shop_name, name=name, parent_id=parent_id)
        db.session.add(new_category)
        db.session.commit()
        logging.info(f"✅ Categoria '{name}' creata con successo per lo shop '{shop_name}'")
        return new_category.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione della categoria '{name}': {e}")
        return None

# 🔍 **Recupera tutte le categorie di uno shop**
def get_all_categories(shop_name):
    """
    Restituisce tutte le categorie di un determinato shop.
    """
    try:
        categories = Category.query.filter_by(shop_name=shop_name).all()
        return [category_to_dict(cat) for cat in categories]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero delle categorie per lo shop '{shop_name}': {e}")
        return []

# 🔍 **Recupera una categoria tramite ID**
def get_category_by_id(category_id):
    """
    Restituisce una singola categoria tramite ID.
    """
    try:
        category = Category.query.get(category_id)
        return category_to_dict(category) if category else None
    except Exception as e:
        logging.error(f"❌ Errore nel recupero della categoria con ID {category_id}: {e}")
        return None

# 🔄 **Aggiorna una categoria esistente**
def update_category(category_id, name=None, parent_id=None):
    """
    Aggiorna una categoria esistente nel database.
    """
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'aggiornamento della categoria {category_id}: {e}")
        return False

# 🗑️ **Elimina una categoria**
def delete_category(category_id):
    """
    Elimina una categoria dal database.
    """
    try:
        category = Category.query.get(category_id)
        if not category:
            return False

        db.session.delete(category)
        db.session.commit()
        logging.info(f"🗑️ Categoria con ID {category_id} eliminata con successo")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione della categoria {category_id}: {e}")
        return False

# 🔍 **Recupera tutte le sotto-categorie di una categoria padre**
def get_subcategories(parent_id):
    """
    Restituisce tutte le sotto-categorie di una categoria padre.
    """
    try:
        subcategories = Category.query.filter_by(parent_id=parent_id).all()
        return [category_to_dict(cat) for cat in subcategories]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero delle sotto-categorie per la categoria padre {parent_id}: {e}")
        return []

# 📌 **Funzione per convertire un oggetto Category in un dizionario**
def category_to_dict(category):
    """
    Converte un oggetto Category in un dizionario.
    """
    return {
        "id": category.id,
        "shop_name": category.shop_name,
        "name": category.name,
        "parent_id": category.parent_id
    }