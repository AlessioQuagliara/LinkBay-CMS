from models.database import db
import logging
from functools import wraps
from datetime import datetime

# Configurazione del logging (da spostare nel file principale dell'app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 **Modello per le Suggestioni di Miglioramento**
class ImprovementSuggestion(db.Model):
    __tablename__ = "improvement_suggestion"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 🔑 ID univoco
    shop_name = db.Column(db.String(255), db.ForeignKey("ShopList.shop_name"), nullable=False)  # 🏪 Relazione con ShopList
    suggestion_text = db.Column(db.Text, nullable=False)  # ✏️ Testo della suggestion
    category = db.Column(db.String(100), nullable=False)  # 🏷️ Categoria (UI, Performance, Feature Request, Bug)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 🕒 Data di creazione

    def __repr__(self):
        return f"<ImprovementSuggestion {self.id} - {self.category}>"
    
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

# ✅ **Crea una nuova suggestione di miglioramento**
@handle_db_errors
def create_suggestion(shop_name, suggestion_text, category):
    new_suggestion = ImprovementSuggestion(
        shop_name=shop_name,
        suggestion_text=suggestion_text,
        category=category,
    )
    db.session.add(new_suggestion)
    db.session.commit()
    logging.info(f"✅ Suggestione creata con successo per {shop_name}")
    return new_suggestion.id

# 🔍 **Ottieni tutte le suggestioni per uno shop**
@handle_db_errors
def get_suggestions_by_shop(shop_name):
    suggestions = ImprovementSuggestion.query.filter_by(shop_name=shop_name).all()
    return [model_to_dict(s) for s in suggestions]

# ❌ **Elimina una suggestione specifica**
@handle_db_errors
def delete_suggestion(suggestion_id):
    suggestion = ImprovementSuggestion.query.get(suggestion_id)
    if not suggestion:
        return False

    db.session.delete(suggestion)
    db.session.commit()
    logging.info(f"✅ Suggestione {suggestion_id} eliminata con successo")
    return True