from models.database import db
import logging
from datetime import datetime

# 📌 Inizializza il database SQLAlchemy
logging.basicConfig(level=logging.INFO)

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

# ✅ **Crea una nuova suggestione di miglioramento**
def create_suggestion(shop_name, suggestion_text, category):
    try:
        new_suggestion = ImprovementSuggestion(
            shop_name=shop_name,
            suggestion_text=suggestion_text,
            category=category,
        )
        db.session.add(new_suggestion)
        db.session.commit()
        logging.info(f"✅ Suggestione creata con successo per {shop_name}")
        return new_suggestion.id
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nella creazione della suggestione per {shop_name}: {e}")
        return None

# 🔍 **Ottieni tutte le suggestioni per uno shop**
def get_suggestions_by_shop(shop_name):
    try:
        suggestions = ImprovementSuggestion.query.filter_by(shop_name=shop_name).all()
        return [suggestion_to_dict(s) for s in suggestions]
    except Exception as e:
        logging.error(f"❌ Errore nel recupero delle suggestioni per {shop_name}: {e}")
        return []

# ❌ **Elimina una suggestione specifica**
def delete_suggestion(suggestion_id):
    try:
        suggestion = ImprovementSuggestion.query.get(suggestion_id)
        if not suggestion:
            return False

        db.session.delete(suggestion)
        db.session.commit()
        logging.info(f"✅ Suggestione {suggestion_id} eliminata con successo")
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore nell'eliminazione della suggestione {suggestion_id}: {e}")
        return False

# 📌 **Helper per convertire una suggestion in dizionario**
def suggestion_to_dict(suggestion):
    return {
        "id": suggestion.id,
        "shop_name": suggestion.shop_name,
        "suggestion_text": suggestion.suggestion_text,
        "category": suggestion.category,
        "created_at": suggestion.created_at,
    }