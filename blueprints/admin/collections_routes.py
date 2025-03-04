from flask import Blueprint, render_template, request, jsonify
from models.database import db  # Database SQLAlchemy
from models.collections import Collection, CollectionProduct, CollectionImage  # Modello delle collezioni
from models.products import Product  # Modello dei prodotti
from helpers import check_user_authentication
import os, logging, uuid, re

logging.basicConfig(level=logging.INFO)

# Creazione del Blueprint per la gestione delle collezioni
collections_bp = Blueprint('collections' , __name__)

# 📌 Route per visualizzare la pagina delle collezioni
@collections_bp.route('/admin/cms/pages/collections')
def collections():
    """
    Visualizza tutte le collezioni di un negozio.
    """
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]  # Ottieni il nome del negozio dal sottodominio
        collections_list = Collection.query.filter_by(shop_name=shop_name).all()  # Query con SQLAlchemy

        return render_template(
            'admin/cms/pages/collections.html', 
            title='Collections', 
            username=username, 
            collections=collections_list
        )
    return username

# 📌 Route per creare una nuova collezione
@collections_bp.route('/admin/cms/create_collection', methods=['POST'])
def create_collection():
    """
    API per creare una nuova collezione nel CMS.
    """
    try:
        shop_name = request.host.split('.')[0]  # Sottodominio per identificare il negozio
        data = request.form

        # Generazione slug univoco basato sul nome
        name = data.get('name', 'New Collection').strip()
        slug = f"{re.sub(r'[^\w\s-]', '', name).replace(' ', '-').lower()}-{uuid.uuid4().hex[:8]}"

        # Creazione della nuova collezione
        new_collection = Collection(
            name=name,
            slug=slug,
            description=data.get('description', 'Detailed description'),
            image_url=data.get('image_url', '/static/images/default.png'),
            is_active=False,
            shop_name=shop_name,
        )

        db.session.add(new_collection)
        db.session.commit()  # Conferma la transazione

        return jsonify({
            'success': True,
            'message': 'Collection created successfully.',
            'collection_id': new_collection.id
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating collection: {e}")
        return jsonify({'success': False, 'message': 'Failed to create Collection.'}), 500

# 📌 Route per visualizzare/modificare una collezione specifica
@collections_bp.route('/admin/cms/pages/collection/<int:collection_id>', methods=['GET', 'POST'])
@collections_bp.route('/admin/cms/pages/collection', methods=['GET', 'POST'])
def manage_collection(collection_id=None):
    """
    API per gestire (visualizzare/modificare) una collezione specifica.
    """
    username = check_user_authentication()
    if isinstance(username, str):
        try:
            if request.method == 'POST':
                data = request.get_json()
                if collection_id:  # Se la collezione esiste, la aggiorniamo
                    collection = Collection.query.get(collection_id)
                    if not collection:
                        return jsonify({'status': 'error', 'message': 'Collection not found'}), 404

                    # Aggiorna solo i campi forniti nel request
                    collection.name = data.get('name', collection.name)
                    collection.description = data.get('description', collection.description)
                    collection.image_url = data.get('image_url', collection.image_url)
                    collection.is_active = data.get('is_active', collection.is_active)

                    db.session.commit()
                    return jsonify({'status': 'success', 'message': 'Collection updated successfully.'})
                else:  # Creazione nuova collezione
                    new_collection = Collection(
                        name=data.get('name', 'New Collection'),
                        slug=f"{re.sub(r'[^\w\s-]', '', data.get('name', 'New Collection')).replace(' ', '-').lower()}-{uuid.uuid4().hex[:8]}",
                        description=data.get('description', 'Detailed description'),
                        image_url=data.get('image_url', '/static/images/default.png'),
                        is_active=data.get('is_active', False),
                        shop_name=request.host.split('.')[0]
                    )

                    db.session.add(new_collection)
                    db.session.commit()

                    return jsonify({'status': 'success', 'message': 'Collection created successfully.', 'collection_id': new_collection.id})

            # Se GET, restituiamo i dettagli della collezione
            collection = Collection.query.get(collection_id) if collection_id else None

            return render_template(
                'admin/cms/pages/manage_collection.html',
                title='Manage Collection',
                username=username,
                collection=collection,
                shop_subdomain=request.host.split('.')[0]  # Passa il sottodominio al template
            )

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error managing collection: {e}")
            return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'}), 500

# 📌 Route per la gestione della lista delle collezioni
@collections_bp.route('/admin/cms/pages/collection-list/<int:collection_id>', methods=['GET', 'POST'])
@collections_bp.route('/admin/cms/pages/collection-list/', methods=['GET', 'POST'])
def manage_collection_list(collection_id=None):
    """
    Visualizza e gestisce una lista di collezioni con i prodotti associati.
    """
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]  # Ottieni il nome del negozio dal sottodominio

        try:
            collection = Collection.query.filter_by(id=collection_id, shop_name=shop_name).first() if collection_id else None

            # Recupera tutti i prodotti associati alla collezione
            products_in_collection = (
                db.session.query(Product)
                .join(CollectionProduct, CollectionProduct.product_id == Product.id)
                .filter(CollectionProduct.collection_id == collection_id)
                .all()
                if collection_id
                else []
            )

            return render_template(
                'admin/cms/pages/manage_collection_list.html',
                title='Manage Collection List',
                username=username,
                collection=collection,
                products=products_in_collection,  # Passa i dettagli completi dei prodotti al template
                shop_subdomain=shop_name
            )

        except Exception as e:
            logging.error(f"Error retrieving collection list: {e}")
            return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'}), 500

    return username

# 📌 Route per rimuovere prodotti da una collezione
@collections_bp.route('/admin/cms/delete_products_from_collection', methods=['POST'])
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
@collections_bp.route('/admin/cms/add_products_to_collection', methods=['POST'])
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

# 📌 Route per cercare prodotti
@collections_bp.route('/admin/cms/search_products', methods=['GET'])
def search_products():
    """
    Cerca prodotti nel database in base alla query fornita.
    """
    query = request.args.get('query', '').strip()
    shop_name = request.host.split('.')[0]

    if not query:
        return jsonify({'success': False, 'message': 'No search term provided.'}), 400

    try:
        products = Product.query.filter(
            Product.shop_name == shop_name,
            Product.name.ilike(f"%{query}%")
        ).all()

        products_data = [{'id': p.id, 'name': p.name, 'price': p.price} for p in products]

        return jsonify({'success': True, 'products': products_data})

    except Exception as e:
        logging.error(f"Error searching products: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

# 📌 Route per aggiungere un prodotto a una collezione
@collections_bp.route('/admin/cms/add_product_to_collection', methods=['POST'])
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
@collections_bp.route('/admin/cms/delete_collections', methods=['POST'])
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
@collections_bp.route('/admin/cms/update_collection', methods=['POST'])
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
@collections_bp.route('/admin/cms/upload_image_collection', methods=['POST'])
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
@collections_bp.route('/admin/cms/delete_image_collection', methods=['POST'])
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
@collections_bp.route('/api/collections', methods=['GET'])
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