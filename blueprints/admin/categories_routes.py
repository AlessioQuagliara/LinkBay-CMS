from flask import Blueprint, request, jsonify
from models.database import db  # Importiamo il database SQLAlchemy
from models.categories import Category  # Importiamo il modello Category
import logging

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione delle categorie
categories_bp = Blueprint('categories' , __name__)

@categories_bp.route('/api/create_category', methods=['POST'])
def create_category():
    """
    API per creare una nuova categoria associata a uno shop.
    """
    try:
        # 📌 Recupera i dati dalla richiesta JSON
        data = request.json
        name = data.get('name', '').strip()  # Nome della categoria
        shop_name = request.host.split('.')[0]  # Ottiene il nome del negozio dal sottodominio

        # 📌 Validazione: il nome della categoria è obbligatorio
        if not name:
            return jsonify({'success': False, 'message': 'Category name is required.'}), 400

        # 📌 Verifica se la categoria esiste già
        existing_category = Category.query.filter_by(shop_name=shop_name, name=name).first()
        if existing_category:
            return jsonify({'success': False, 'message': 'Category already exists.'}), 409

        # 📌 Crea una nuova categoria
        new_category = Category(shop_name=shop_name, name=name)
        db.session.add(new_category)
        db.session.commit()  # Conferma la transazione

        return jsonify({'success': True, 'category_id': new_category.id}), 201

    except Exception as e:
        logging.error(f"Errore durante la creazione della categoria: {e}")
        db.session.rollback()  # Annulla la transazione in caso di errore
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500