from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect
from models.collections import Collections  # importo la classe database
from models.products import Products 
from app import app  # connessione al database
import os, uuid, re, base64
from db_helpers import DatabaseHelper
from db_helpers import DatabaseHelper
from helpers import check_user_authentication

db_helper = DatabaseHelper()

# Blueprint
collections_bp = Blueprint('collections', __name__)

# Rotte per la gestione

@collections_bp.route('/admin/cms/pages/collections')
def collections():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_subdomain = request.host.split('.')[0]  # Ottieni il nome del negozio dal sottodominio
        with db_helper.get_db_connection() as db_conn:
            collections_model = Collections(db_conn)
            collections_list = collections_model.get_all_collections(shop_subdomain)  # Passa shop_subdomain come parametro
        return render_template(
            'admin/cms/pages/collections.html', 
            title='Collections', 
            username=username, 
            collections=collections_list
        )
    return username

@collections_bp.route('/admin/cms/create_collection', methods=['POST'])
def create_collection():
    try:
        # Ottieni i valori predefiniti o forniti
        shop_subdomain = request.host.split('.')[0]  # Sottodominio per identificare il negozio
        name = request.form.get('name', 'New Collection')  # Ottieni il nome della collezione
        slug = f"{re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '-').lower()}-{uuid.uuid4().hex[:8]}"  # Genera slug univoco

        default_values = {
            "name": name,
            "slug": slug,
            "description": request.form.get('description', 'Detailed description'),
            "image_url": request.form.get('image_url', '/static/images/default.png'),
            "is_active": False,
            "shop_name": shop_subdomain,
        }

        with db_helper.get_db_connection() as db_conn:
            collection_model = Collections(db_conn)
            new_collection_id = collection_model.create_collection(default_values)

        return jsonify({
            'success': True,
            'message': 'Collection created successfully.',
            'collection_id': new_collection_id
        })
    except Exception as e:
        print(f"Error creating collection: {e}")
        return jsonify({'success': False, 'message': 'Failed to create Collection.'}), 500
    
@collections_bp.route('/admin/cms/pages/collection/<int:collection_id>', methods=['GET', 'POST'])
@collections_bp.route('/admin/cms/pages/collection', methods=['GET', 'POST'])
def manage_collection(collection_id=None):
    username = check_user_authentication()
    if isinstance(username, str):
        with db_helper.get_db_connection() as db_conn:
            collection_model = Collections(db_conn)

            if request.method == 'POST':
                data = request.get_json()  
                try:
                    if collection_id:  # Modifica
                        success = collection_model.update_collection(collection_id, data)
                    else:  # Creazione
                        success = collection_model.create_collection(data)

                    if success:
                        return jsonify({'status': 'success', 'message': 'Collection saved successfully.'})
                    else:
                        return jsonify({'status': 'error', 'message': 'Failed to save the collection.'})
                except Exception as e:
                    print(f"Error managing collection: {e}")
                    return jsonify({'status': 'error', 'message': 'An error occurred.'})

            # Per GET: Ottieni i dettagli del prodotto (se esiste)
            collection = collection_model.get_collection_by_id(collection_id) if collection_id else {}

            # Ottieni le immagini associate al prodotto, se esiste
            images = collection_model.get_collection_images(collection_id) if collection_id else []

            shop_subdomain = request.host.split('.')[0]  

            # Log di debug per verificare i dati passati
            print(f"Collection: {collection}")
            print(f"Shop Subdomain: {shop_subdomain}")

            return render_template(
                'admin/cms/pages/manage_collection.html',
                title='Manage Collection',
                username=username,
                collection=collection,
                images=images,
                shop_subdomain=shop_subdomain  # Passa il sottodominio al template
            )
    return username

# GESTIONE DELLA LISTA DELLE COLLEZIONI

@collections_bp.route('/admin/cms/pages/collection-list/<int:collection_id>', methods=['GET', 'POST'])
@collections_bp.route('/admin/cms/pages/collection-list/', methods=['GET', 'POST'])
def manage_collection_list(collection_id=None):
    username = check_user_authentication()
    if isinstance(username, str):
        with db_helper.get_db_connection() as db_conn:
            # Inizializza i modelli
            collection_model = Collections(db_conn)
            product_model = Products(db_conn)

            # Ottieni i dettagli della collezione
            collection = collection_model.get_collection_by_id(collection_id) if collection_id else {}

            # Ottieni i prodotti associati alla collezione
            products_in_collection = collection_model.get_products_in_collection(collection_id) if collection_id else []

            # Recupera i dettagli completi per ogni prodotto
            detailed_products = []
            for product in products_in_collection:
                product_details = product_model.get_product_by_id(product['id'])  # Assicurati che esista un metodo `get_product_by_id`
                if product_details:
                    detailed_products.collections_bpend(product_details)

            # Ottieni il nome del negozio dal sottodominio
            shop_subdomain = request.host.split('.')[0]

            return render_template(
                'admin/cms/pages/manage_collection_list.html',
                title='Manage Collection List',
                username=username,
                collection=collection,
                products=detailed_products,  # Passa i dettagli completi dei prodotti al template
                shop_subdomain=shop_subdomain
            )
    return username

@collections_bp.route('/admin/cms/delete_products_from_collection', methods=['POST'])
def delete_products_from_collection():
    try:
        data = request.get_json()
        collection_id = data.get('collection_id')
        product_ids = data.get('product_ids', [])

        if not collection_id or not product_ids:
            return jsonify({'success': False, 'message': 'Missing collection ID or product IDs.'}), 400

        with db_helper.get_db_connection() as db_conn:
            collection_model = Collections(db_conn)
            success = collection_model.remove_products_from_collection(collection_id, product_ids)

        if success:
            return jsonify({'success': True, 'message': 'Products removed successfully.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to remove products.'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
    
@collections_bp.route('/admin/cms/add_products_to_collection', methods=['POST'])
def add_products_to_collection():
    try:
        data = request.get_json()
        collection_id = data.get('collection_id')
        product_ids = data.get('product_ids', [])

        if not collection_id or not product_ids:
            return jsonify({'success': False, 'message': 'Missing collection ID or product IDs.'}), 400

        with db_helper.get_db_connection() as db_conn:
            collection_model = Collections(db_conn)
            success = collection_model.add_products_to_collection(collection_id, product_ids)

        if success:
            return jsonify({'success': True, 'message': 'Products added successfully.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add products.'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

@collections_bp.route('/admin/cms/search_products', methods=['GET'])
def search_products():
    query = request.args.get('query', '').strip()
    shop_subdomain = request.host.split('.')[0]

    print(f"Search query: {query}")
    print(f"Shop subdomain: {shop_subdomain}")

    if not query:
        return jsonify({'success': False, 'message': 'No search term provided.'}), 400

    with db_helper.get_db_connection() as db_conn:
        product_model = Products(db_conn)
        products = product_model.search_products(query, shop_subdomain)
    
    print(f"Found products: {products}")
    return jsonify({'success': True, 'products': products})

@collections_bp.route('/admin/cms/add_product_to_collection', methods=['POST'])
def add_product_to_collection():
    try:
        data = request.get_json()
        collection_id = data.get('collection_id')
        product_id = data.get('product_id')

        if not collection_id or not product_id:
            return jsonify({'success': False, 'message': 'Missing collection ID or product ID.'}), 400

        with db_helper.get_db_connection() as db_conn:
            collection_model = Collections(db_conn)
            success = collection_model.add_product_to_collection(collection_id, product_id)

        if success:
            return jsonify({'success': True, 'message': 'Product added successfully.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add product.'})
    except Exception as e:
        print(f"Error adding product to collection: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500


@collections_bp.route('/admin/cms/delete_collections', methods=['POST'])
def delete_collection():
    try:
        data = request.get_json()  # Ottieni i dati dalla richiesta
        collection_ids = data.get('collection_ids')  # Array di ID dei prodotti da eliminare

        if not collection_ids:
            return jsonify({'success': False, 'message': 'No collection IDs provided.'}), 400

        with db_helper.get_db_connection() as db_conn:
            collection_model = Collections(db_conn)
            for collection_id in collection_ids:
                success = collection_model.delete_collection(collection_id)
                if not success:
                    return jsonify({'success': False, 'message': f'Failed to delete collection with ID {collection_id}.'}), 500

        return jsonify({'success': True, 'message': 'Selected collections deleted successfully.'})
    except Exception as e:
        print(f"Error deleting collections: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500

@collections_bp.route('/admin/cms/update_collection', methods=['POST'])
def update_collection():
    try:
        data = request.form.to_dict()  # Usa request.form per raccogliere i dati del FormData
        collection_id = data.get('id')

        if not collection_id:
            return jsonify({'success': False, 'message': 'Collection ID is required.'}), 400

        shop_subdomain = request.host.split('.')[0]  # Ottieni il nome del negozio

        # Rigenera lo slug solo se il nome è stato modificato
        if 'name' in data:
            new_name = data['name']
            new_slug = f"{re.sub(r'[^\w\s-]', '', new_name).strip().replace(' ', '-').lower()}-{uuid.uuid4().hex[:4]}"
            data['slug'] = new_slug

        # Connetti al database
        with db_helper.get_db_connection() as db_conn:
            collection_model = Collections(db_conn)
            success = collection_model.update_collection(collection_id, data)

        if success:
            return jsonify({'success': True, 'message': 'Collection updated successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update the collection.'}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

@collections_bp.route('/admin/cms/upload_image_collection', methods=['POST'])
def upload_image_collection():
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

        # Aggiungi l'immagine al database
        db_conn = db_helper.get_db_connection()
        collections_model = Collections(db_conn)
        image_id = collections_model.add_collection_image(collection_id, f"/{image_path}")

        if image_id:
            return jsonify({'success': True, 'image_url': f"/{image_path}", 'image_id': image_id})
        else:
            return jsonify({'success': False, 'message': 'Failed to save image to database.'}), 500
    except Exception as e:
        print(f"Error uploading image: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during upload.'}), 500

@collections_bp.route('/admin/cms/delete_image_collection', methods=['POST'])
def delete_image_collection():
    try:
        data = request.get_json()
        image_id = data.get('image_id')

        if not image_id:
            return jsonify({'success': False, 'message': 'Image ID is missing.'}), 400

        db_conn = db_helper.get_db_connection()
        collections_model = Collections(db_conn)
        image = collections_model.get_collection_image_by_id(image_id)  # Usa il nuovo metodo

        if image and os.path.exists(image['image_url'][1:]):  # Rimuove '/' iniziale
            os.remove(image['image_url'][1:])

        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM collection_images WHERE id = %s", (image_id,))
        db_conn.commit()
        cursor.close()

        return jsonify({'success': True, 'message': 'Image deleted successfully.'})
    except Exception as e:
        print(f"Error deleting image: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500
    
@collections_bp.route('/api/collections', methods=['GET'])
def get_collections():
    shop_name = request.host.split('.')[0]
    if not shop_name:
        return jsonify({'success': False, 'message': 'Shop name is required'}), 400

    conn = db_helper.get_db_connection()
    collection_model = Collections(conn)

    try:
        collections = collection_model.get_collections_by_shop(shop_name)
        return jsonify({'success': True, 'collections': collections})
    except Exception as e:
        print(f"Error fetching collections: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500
    
def save_base64_image(base64_image):
    try:
        header, encoded = base64_image.split(",", 1)
        binary_data = base64.b64decode(encoded)

        # Genera un nome file unico usando UUID
        unique_filename = f"{uuid.uuid4().hex}.png"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        # Salva il file sul server
        with open(file_path, "wb") as f:
            f.write(binary_data)

        return f"/static/uploads/{unique_filename}"
    except Exception as e:
        print(f"Errore durante il salvataggio dell'immagine: {str(e)}")
        return None