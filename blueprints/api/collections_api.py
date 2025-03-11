from flask import Blueprint, jsonify, request
from models.database import db
from models.products import Product
from models.collections import Collection, CollectionImage, CollectionProduct
import uuid, re, os
import logging

logging.basicConfig(level=logging.INFO)

collections_bp = Blueprint('collectionsApi', __name__, url_prefix='/')

# 📌 Route per rimuovere prodotti da una collezione
@collections_bp.route('/delete_products_from_collection', methods=['POST'])
def delete_products_from_collection():
    """
    API per rimuovere prodotti da una collezione esistente.
    """
    try:
        data = request.get_json()
        collection_id = data.get('collection_id')
        product_ids = data.get('product_ids', [])

        if not collection_id or not product_ids:
            return jsonify({'success': False, 'message': 'Missing collection ID or product IDs.'}), 400

        # Rimuove le associazioni tra prodotti e collezione
        db.session.query(CollectionProduct).filter(
            CollectionProduct.collection_id == collection_id,
            CollectionProduct.product_id.in_(product_ids)
        ).delete(synchronize_session=False)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Products removed successfully.'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error removing products from collection: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

# 📌 Route per aggiungere prodotti a una collezione
@collections_bp.route('/add_products_to_collection', methods=['POST'])
def add_products_to_collection():
    """
    API per aggiungere prodotti a una collezione esistente.
    """
    try:
        data = request.get_json()
        collection_id = data.get('collection_id')
        product_ids = data.get('product_ids', [])

        if not collection_id or not product_ids:
            return jsonify({'success': False, 'message': 'Missing collection ID or product IDs.'}), 400

        # Verifica che i prodotti esistano prima di aggiungerli
        existing_products = Product.query.filter(Product.id.in_(product_ids)).all()
        existing_product_ids = {product.id for product in existing_products}

        new_associations = [
            CollectionProduct(collection_id=collection_id, product_id=product_id)
            for product_id in product_ids if product_id in existing_product_ids
        ]

        db.session.bulk_save_objects(new_associations)  # Ottimizza il salvataggio
        db.session.commit()
        return jsonify({'success': True, 'message': 'Products added successfully.'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding products to collection: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

# 📌 Route per aggiungere un prodotto a una collezione
@collections_bp.route('/add_product_to_collection', methods=['POST'])
def add_product_to_collection():
    """
    Aggiunge un prodotto a una collezione esistente.
    """
    try:
        data = request.get_json()
        collection_id = data.get('collection_id')
        product_id = data.get('product_id')

        if not collection_id or not product_id:
            return jsonify({'success': False, 'message': 'Missing collection ID or product ID.'}), 400

        new_association = CollectionProduct(collection_id=collection_id, product_id=product_id)
        db.session.add(new_association)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Product added successfully.'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding product to collection: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500

# 📌 Route per eliminare una collezione
@collections_bp.route('/delete_collections', methods=['POST'])
def delete_collection():
    """
    Elimina una o più collezioni dal database.
    """
    try:
        data = request.get_json()
        collection_ids = data.get('collection_ids')

        if not collection_ids:
            return jsonify({'success': False, 'message': 'No collection IDs provided.'}), 400

        # Eliminazione delle collezioni e delle associazioni con prodotti
        CollectionProduct.query.filter(CollectionProduct.collection_id.in_(collection_ids)).delete(synchronize_session=False)
        Collection.query.filter(Collection.id.in_(collection_ids)).delete(synchronize_session=False)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Selected collections deleted successfully.'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting collections: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500

# 📌 Route per aggiornare una collezione
@collections_bp.route('/update_collection', methods=['POST'])
def update_collection():
    """
    Aggiorna una collezione esistente nel database.
    """
    try:
        data = request.get_json()
        collection_id = data.get('id')

        if not collection_id:
            return jsonify({'success': False, 'message': 'Collection ID is required.'}), 400

        collection = Collection.query.get(collection_id)
        if not collection:
            return jsonify({'success': False, 'message': 'Collection not found.'}), 404

        # Rigenera lo slug solo se il nome è stato modificato
        if 'name' in data:
            new_name = data['name']
            new_slug = f"{re.sub(r'[^\w\s-]', '', new_name).strip().replace(' ', '-').lower()}-{uuid.uuid4().hex[:4]}"
            collection.slug = new_slug

        for key, value in data.items():
            setattr(collection, key, value)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Collection updated successfully!'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating collection: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

# 📌 Route per caricare un'immagine per una collezione
@collections_bp.route('/upload_image_collection', methods=['POST'])
def upload_image_collection():
    """
    Carica un'immagine per una collezione specifica e la salva nel database.
    """
    try:
        collection_id = request.form.get('collection_id')
        image = request.files.get('image')

        if not collection_id or not image:
            return jsonify({'success': False, 'message': 'Collection ID or image is missing.'}), 400

        # Genera un nome univoco per il file
        unique_filename = f"{uuid.uuid4().hex}_{image.filename}"
        upload_folder = os.path.join('static', 'uploads', 'collections')
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, unique_filename)

        # Salva il file
        image.save(image_path)

        # Salva il percorso dell'immagine nel database
        new_image = CollectionImage(collection_id=collection_id, image_url=f"/{image_path}")
        db.session.add(new_image)
        db.session.commit()

        return jsonify({'success': True, 'image_url': f"/{image_path}", 'image_id': new_image.id})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error uploading image: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500

# 📌 Route per eliminare un'immagine di una collezione
@collections_bp.route('/delete_image_collection', methods=['POST'])
def delete_image_collection():
    """
    Elimina un'immagine da una collezione.
    """
    try:
        data = request.get_json()
        image_id = data.get('image_id')

        if not image_id:
            return jsonify({'success': False, 'message': 'Image ID is missing.'}), 400

        image = CollectionImage.query.get(image_id)
        if not image:
            return jsonify({'success': False, 'message': 'Image not found.'}), 404

        # Elimina il file fisico se esiste
        image_path = image.image_url[1:]  # Rimuove lo '/' iniziale
        if os.path.exists(image_path):
            os.remove(image_path)

        db.session.delete(image)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Image deleted successfully.'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting image: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500

# 📌 Route per ottenere tutte le collezioni di un negozio
@collections_bp.route('/collections', methods=['GET'])
def get_collections():
    """
    Ottiene tutte le collezioni di un negozio specifico.
    """
    shop_name = request.host.split('.')[0]

    if not shop_name:
        return jsonify({'success': False, 'message': 'Shop name is required'}), 400

    try:
        collections = Collection.query.filter_by(shop_name=shop_name).all()
        collections_data = [{'id': c.id, 'name': c.name, 'slug': c.slug} for c in collections]

        return jsonify({'success': True, 'collections': collections_data})

    except Exception as e:
        logging.error(f"Error fetching collections: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500