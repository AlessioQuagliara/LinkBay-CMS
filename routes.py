from flask import render_template, redirect, url_for, request, flash, session, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import User, ShopList, Page, WebSettings, CookiePolicy, CMSAddon, UserStoreAccess, Products, Collections, Categories
from app import app, get_db_connection, get_auth_db_connection
from datetime import datetime
from creators import capture_screenshot
import base64, os, uuid, re, mysql.connector, stripe, csv, io
from config import Config

stripe.api_key = Config.STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY = Config.STRIPE_PUBLISHABLE_KEY

# Se non trova la pagina va in 404 ------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Funzione per controllare se l'utente è autenticato -----------------------------------
def check_user_authentication():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    return session['username']

# Admin Routes -------------------------------------------------------------------------
@app.route('/admin/sign-in', methods=['GET', 'POST'])
def signin():
    db_conn = get_db_connection()  
    user_model = User(db_conn)  

    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        store_name = request.form.get('store_name')
        email = request.form.get('email')
        password = request.form.get('password')


        existing_user = user_model.get_user_by_email(email)
        if existing_user:
            flash('Email address already exists')
            return redirect(url_for('signin'))

        user_model.create_user(name, surname, email, password)
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('/admin/sign-in.html', title='LinkBay - Sign-in')

# Middleware per il debug delle sessioni
@app.before_request
def log_session_info():
    print(f"Request path: {request.path}")
    print(f"Session data: {session}")
    print(f"Cookies: {request.cookies}")

# Funzione di login -------------------------------------------------
@app.route('/admin/', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    auth_db_conn = get_auth_db_connection()  
    user_model = User(auth_db_conn)  
    access_model = UserStoreAccess(auth_db_conn)  
    shop_list_model = ShopList(auth_db_conn)  # Modello per ottenere i dettagli dello store

    # Rileva il sottodominio o il dominio principale
    domain_parts = request.host.split('.')
    subdomain_or_domain = domain_parts[0] if len(domain_parts) > 1 else request.host

    # Ottieni lo shop basato su `shop_name` o `domain`
    shop = shop_list_model.get_shop_by_name_or_domain(subdomain_or_domain)

    if not shop:
        flash('Store not found for this domain or subdomain.', 'danger')
        return redirect(url_for('login'))

    shop_id = shop['id']  # Identifica lo store attuale per l'accesso
    shop_name = shop['shop_name']  # Per visualizzazione nel template

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = user_model.get_user_by_email(email)

        if user and check_password_hash(user['password'], password):
            # Verifica se l'utente ha accesso a questo specifico store
            if access_model.has_access(user['id'], shop_id):
                # Se ha accesso, imposta la sessione
                session['user_id'] = user['id']
                session['username'] = user['nome']
                session['surname'] = user['cognome']
                session['email'] = user['email']
                session['phone'] = user['telefono']
                session['profile_photo'] = user['profilo_foto']
                session['shop_id'] = shop_id  # Salva lo shop_id nella sessione

                print(f"Session after login: {session}")

                # Controllo per 2FA
                if user['is_2fa_enabled']:
                    session['otp_secret'] = user['otp_secret']
                    return redirect(url_for('verify_otp'))
                else:
                    return redirect(url_for('homepage'))
            else:
                # Se l'utente non ha accesso a questo store
                flash('Access denied for this store.', 'danger')
                return redirect(url_for('login'))
        else:
            # Se email o password non sono corretti
            flash('Login failed. Please check your email and password.', 'danger')
            return redirect(url_for('login'))

    # Passa shop_name al template per mostrare il nome dello store
    return render_template('admin/login.html', title='Login', shop_name=shop_name)

@app.route('/admin/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return render_template('admin/logout.html', title='Logout')

@app.route('/admin/restore')
def restore():
    return render_template('/admin/restore.html', title='LinkBay - Restore')


# Verifica autenticazione utente -----------------------------------
def check_user_authentication():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    
    print(f"User authenticated: {session.get('username')}")
    return session['username']

# CMS Routes -------------------------------------------------------------------------
@app.route('/admin/cms/interface/')
@app.route('/admin/cms/interface/render')
def render_interface():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/interface/render.html', title='CMS Interface', username=username)
    return username  

# Rotta per la homepage del CMS
@app.route('/admin/cms/pages/homepage')
def homepage():
    username = check_user_authentication()
    print(f"Session in homepage: {session}")
    if isinstance(username, str):
        return render_template('admin/cms/pages/home.html', title='HomePage', username=username)
    return username

@app.route('/admin/cms/pages/orders')
def orders():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/orders.html', title='Orders', username=username)
    return username

# PRODOTTI, COLLEZIONI, CATEGORIE, GESTIONE E ROTTE ---------------------------------------------------------------------------------------

# COLLEZIONI -------------------------------- >

@app.route('/admin/cms/pages/collections')
def collections():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_subdomain = request.host.split('.')[0]  # Ottieni il nome del negozio dal sottodominio
        with get_db_connection() as db_conn:
            collections_model = Collections(db_conn)
            collections_list = collections_model.get_all_collections(shop_subdomain)  # Passa shop_subdomain come parametro
        return render_template(
            'admin/cms/pages/collections.html', 
            title='Collections', 
            username=username, 
            collections=collections_list
        )
    return username

@app.route('/admin/cms/create_collection', methods=['POST'])
def create_collection():
    try:
        # Ottieni i valori predefiniti o forniti
        shop_subdomain = request.host.split('.')[0]  # Sottodominio per identificare il negozio
        default_values = {
            "name": "New Collection",
            "slug": "new-collection",
            "description": "Detailed description",
            "image_url": "/static/images/default.png",
            "is_active": False,
            "shop_name": shop_subdomain,
        }

        with get_db_connection() as db_conn:
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
    
@app.route('/admin/cms/pages/collection/<int:collection_id>', methods=['GET', 'POST'])
@app.route('/admin/cms/pages/collection', methods=['GET', 'POST'])
def manage_collection(collection_id=None):
    username = check_user_authentication()
    if isinstance(username, str):
        with get_db_connection() as db_conn:
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

@app.route('/admin/cms/pages/collection-list/<int:collection_id>', methods=['GET', 'POST'])
@app.route('/admin/cms/pages/collection-list/', methods=['GET', 'POST'])
def manage_collection_list(collection_id=None):
    username = check_user_authentication()
    if isinstance(username, str):
        with get_db_connection() as db_conn:
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
                    detailed_products.append(product_details)

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

@app.route('/admin/cms/delete_products_from_collection', methods=['POST'])
def delete_products_from_collection():
    try:
        data = request.get_json()
        collection_id = data.get('collection_id')
        product_ids = data.get('product_ids', [])

        if not collection_id or not product_ids:
            return jsonify({'success': False, 'message': 'Missing collection ID or product IDs.'}), 400

        with get_db_connection() as db_conn:
            collection_model = Collections(db_conn)
            success = collection_model.remove_products_from_collection(collection_id, product_ids)

        if success:
            return jsonify({'success': True, 'message': 'Products removed successfully.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to remove products.'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
    
@app.route('/admin/cms/add_products_to_collection', methods=['POST'])
def add_products_to_collection():
    try:
        data = request.get_json()
        collection_id = data.get('collection_id')
        product_ids = data.get('product_ids', [])

        if not collection_id or not product_ids:
            return jsonify({'success': False, 'message': 'Missing collection ID or product IDs.'}), 400

        with get_db_connection() as db_conn:
            collection_model = Collections(db_conn)
            success = collection_model.add_products_to_collection(collection_id, product_ids)

        if success:
            return jsonify({'success': True, 'message': 'Products added successfully.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add products.'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

@app.route('/admin/cms/search_products', methods=['GET'])
def search_products():
    query = request.args.get('query', '').strip()
    shop_subdomain = request.host.split('.')[0]

    print(f"Search query: {query}")
    print(f"Shop subdomain: {shop_subdomain}")

    if not query:
        return jsonify({'success': False, 'message': 'No search term provided.'}), 400

    with get_db_connection() as db_conn:
        product_model = Products(db_conn)
        products = product_model.search_products(query, shop_subdomain)
    
    print(f"Found products: {products}")
    return jsonify({'success': True, 'products': products})

@app.route('/admin/cms/add_product_to_collection', methods=['POST'])
def add_product_to_collection():
    try:
        data = request.get_json()
        collection_id = data.get('collection_id')
        product_id = data.get('product_id')

        if not collection_id or not product_id:
            return jsonify({'success': False, 'message': 'Missing collection ID or product ID.'}), 400

        with get_db_connection() as db_conn:
            collection_model = Collections(db_conn)
            success = collection_model.add_product_to_collection(collection_id, product_id)

        if success:
            return jsonify({'success': True, 'message': 'Product added successfully.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add product.'})
    except Exception as e:
        print(f"Error adding product to collection: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

# GESTIONE DELLA COLLEZIONE

@app.route('/admin/cms/delete_collections', methods=['POST'])
def delete_collection():
    try:
        data = request.get_json()  # Ottieni i dati dalla richiesta
        collection_ids = data.get('collection_ids')  # Array di ID dei prodotti da eliminare

        if not collection_ids:
            return jsonify({'success': False, 'message': 'No collection IDs provided.'}), 400

        with get_db_connection() as db_conn:
            collection_model = Collections(db_conn)
            for collection_id in collection_ids:
                success = collection_model.delete_collection(collection_id)
                if not success:
                    return jsonify({'success': False, 'message': f'Failed to delete collection with ID {collection_id}.'}), 500

        return jsonify({'success': True, 'message': 'Selected collections deleted successfully.'})
    except Exception as e:
        print(f"Error deleting collections: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500

@app.route('/admin/cms/update_collection', methods=['POST'])
def update_collection():
    try:
        data = request.form.to_dict()  # Usa request.form per raccogliere i dati del FormData
        collection_id = data.get('id')

        if not collection_id:
            return jsonify({'success': False, 'message': 'Collection ID is required.'}), 400

        # Connetti al database
        with get_db_connection() as db_conn:
            collection_model = Collections(db_conn)
            success = collection_model.update_collection(collection_id, data)

        if success:
            return jsonify({'success': True, 'message': 'Collection updated successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update the collection.'}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

@app.route('/admin/cms/upload_image_collection', methods=['POST'])
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
        db_conn = get_db_connection()
        collections_model = Collections(db_conn)
        image_id = collections_model.add_collection_image(collection_id, f"/{image_path}")

        if image_id:
            return jsonify({'success': True, 'image_url': f"/{image_path}", 'image_id': image_id})
        else:
            return jsonify({'success': False, 'message': 'Failed to save image to database.'}), 500
    except Exception as e:
        print(f"Error uploading image: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during upload.'}), 500

@app.route('/admin/cms/delete_image_collection', methods=['POST'])
def delete_image_collection():
    try:
        data = request.get_json()
        image_id = data.get('image_id')

        if not image_id:
            return jsonify({'success': False, 'message': 'Image ID is missing.'}), 400

        db_conn = get_db_connection()
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

# PRODOTTI -------------------------------- >

@app.route('/admin/cms/pages/products')
def products():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_subdomain = request.host.split('.')[0]  # Ottieni il nome del negozio dal sottodominio
        with get_db_connection() as db_conn:
            products_model = Products(db_conn)
            category_model = Categories(db_conn)
            products_list = products_model.get_all_products(shop_subdomain)  # Passa shop_subdomain come parametro
            categories = category_model.get_all_categories(shop_subdomain)
        return render_template(
            'admin/cms/pages/products.html', 
            title='Products', 
            username=username, 
            categories=categories,
            products=products_list
        )
    return username

@app.route('/admin/cms/pages/product/<int:product_id>', methods=['GET', 'POST'])
@app.route('/admin/cms/pages/product', methods=['GET', 'POST'])
def manage_product(product_id=None):
    username = check_user_authentication()
    if isinstance(username, str):
        with get_db_connection() as db_conn:
            product_model = Products(db_conn)
            category_model = Categories(db_conn)

            if request.method == 'POST':
                # Ottieni i dati del prodotto
                data = request.form.to_dict()  # Usa request.form se i dati sono inviati come FormData
                try:
                    if product_id:  # Modifica
                        success = product_model.update_product(product_id, data)
                    else:  # Creazione
                        success = product_model.create_product(data)

                    if success:
                        return jsonify({'status': 'success', 'message': 'Product saved successfully.'})
                    else:
                        return jsonify({'status': 'error', 'message': 'Failed to save the product.'})
                except Exception as e:
                    print(f"Error managing product: {e}")
                    return jsonify({'status': 'error', 'message': 'An error occurred.'})

            # Per GET: Ottieni i dettagli del prodotto (se esiste)
            product = product_model.get_product_by_id(product_id) if product_id else {}

            # Ottieni le immagini associate al prodotto, se esiste
            images = product_model.get_product_images(product_id) if product_id else []

            # Ottieni tutte le categorie per lo shop corrente
            shop_subdomain = request.host.split('.')[0]  
            categories = category_model.get_all_categories(shop_subdomain)

            return render_template(
                'admin/cms/pages/manage_product.html',
                title='Manage Product',
                username=username,
                product=product,
                images=images,
                categories=categories,
                shop_subdomain=shop_subdomain  # Passa il sottodominio al template
            )
    return username

@app.route('/admin/cms/create_category', methods=['POST'])
def create_category():
    try:
        data = request.json
        name = data.get('name')
        shop_name = request.host.split('.')[0]
        if not name:
            return jsonify({'success': False, 'message': 'Category name is required.'}), 400

        with get_db_connection() as db_conn:
            categories_model = Categories(db_conn)
            category_id = categories_model.create_category(shop_name, name)
            if category_id:
                return jsonify({'success': True, 'category_id': category_id})
            else:
                return jsonify({'success': False, 'message': 'Failed to create category.'}), 500
    except Exception as e:
        print(f"Error creating category: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

@app.route('/admin/cms/create_product', methods=['POST'])
def create_product():
    try:
        # Ottieni i valori predefiniti o forniti
        shop_subdomain = request.host.split('.')[0]  # Sottodominio per identificare il negozio
        default_values = {
            "name": "New Product",
            "short_description": "Short description",
            "description": "Detailed description",
            "price": 0.0,
            "discount_price": 0.0,
            "stock_quantity": 0,
            "sku": "NEW_SKU",
            "category_id": None,  # Assicurati che queste categorie esistano
            "brand_id": None,
            "weight": 0.0,
            "dimensions": "0x0x0",
            "color": "Default color",
            "material": "Default material",
            "image_url": "/static/images/default.png",
            "slug": f"new-product-{uuid.uuid4().hex[:8]}",
            "is_active": False,
            "shop_name": shop_subdomain,
        }

        with get_db_connection() as db_conn:
            product_model = Products(db_conn)
            new_product_id = product_model.create_product(default_values)

        return jsonify({
            'success': True,
            'message': 'Product created successfully.',
            'product_id': new_product_id
        })
    except Exception as e:
        print(f"Error creating product: {e}")
        return jsonify({'success': False, 'message': 'Failed to create product.'}), 500
    
@app.route('/admin/cms/delete_products', methods=['POST'])
def delete_products():
    try:
        data = request.get_json()  # Ottieni i dati dalla richiesta
        product_ids = data.get('product_ids')  # Array di ID dei prodotti da eliminare

        if not product_ids:
            return jsonify({'success': False, 'message': 'No product IDs provided.'}), 400

        with get_db_connection() as db_conn:
            product_model = Products(db_conn)
            for product_id in product_ids:
                success = product_model.delete_product(product_id)
                if not success:
                    return jsonify({'success': False, 'message': f'Failed to delete product with ID {product_id}.'}), 500

        return jsonify({'success': True, 'message': 'Selected products deleted successfully.'})
    except Exception as e:
        print(f"Error deleting products: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500

@app.route('/admin/cms/update_product', methods=['POST'])
def update_product():
    try:
        data = request.form.to_dict()  # Usa request.form per raccogliere i dati del FormData
        product_id = data.get('id')

        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID is required.'}), 400

        # Connetti al database
        with get_db_connection() as db_conn:
            product_model = Products(db_conn)
            success = product_model.update_product(product_id, data)

        if success:
            return jsonify({'success': True, 'message': 'Product updated successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update the product.'}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
    
@app.route('/admin/cms/upload_image_product', methods=['POST'])
def upload_image_product():
    try:
        product_id = request.form.get('product_id')
        image = request.files.get('image')

        if not product_id or not image:
            return jsonify({'success': False, 'message': 'Product ID or image is missing.'}), 400

        # Genera un nome univoco per il file
        unique_filename = f"{uuid.uuid4().hex}_{image.filename}"
        upload_folder = os.path.join('static', 'uploads', 'products')
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, unique_filename)

        # Salva il file
        image.save(image_path)

        # Aggiungi l'immagine al database
        db_conn = get_db_connection()
        products_model = Products(db_conn)
        image_id = products_model.add_product_image(product_id, f"/{image_path}")

        if image_id:
            return jsonify({'success': True, 'image_url': f"/{image_path}", 'image_id': image_id})
        else:
            return jsonify({'success': False, 'message': 'Failed to save image to database.'}), 500
    except Exception as e:
        print(f"Error uploading image: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during upload.'}), 500
    
@app.route('/admin/cms/delete_image_product', methods=['POST'])
def delete_image_product():
    try:
        data = request.get_json()
        image_id = data.get('image_id')

        if not image_id:
            return jsonify({'success': False, 'message': 'Image ID is missing.'}), 400

        db_conn = get_db_connection()
        products_model = Products(db_conn)
        image = products_model.get_product_images(image_id)

        if image and os.path.exists(image[0]['image_url'][1:]):  # Rimuove '/' iniziale
            os.remove(image[0]['image_url'][1:])

        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM product_images WHERE id = %s", (image_id,))
        db_conn.commit()
        cursor.close()

        return jsonify({'success': True, 'message': 'Image deleted successfully.'})
    except Exception as e:
        print(f"Error deleting image: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500
    
@app.route('/admin/cms/export_products', methods=['GET'])
def export_products():
    shop_name = request.host.split('.')[0]  # Sottodominio per identificare il negozio

    try:
        # Connessione al database
        with get_db_connection() as db_conn:
            product_model = Products(db_conn)

            # Assicurati che il metodo supporti il filtraggio per `shop_name`
            products = product_model.get_all_products(shop_name)

            if not products:
                return jsonify({'success': False, 'message': 'No products found for this shop.'}), 404

        # Creazione del file CSV in memoria
        output = io.StringIO()
        writer = csv.writer(output)

        # Intestazioni
        headers = [
            "ID", "Name", "Description", "Short Description", "Price", "Discount Price",
            "Stock", "SKU", "Category", "Brand", "Weight", "Dimensions", "Color",
            "Material", "Image URL", "Slug", "Is Active", "Created At", "Updated At"
        ]
        writer.writerow(headers)

        # Righe dei dati
        for product in products:
            writer.writerow([
                product.get('id', ''),
                product.get('name', ''),
                product.get('description', ''),
                product.get('short_description', ''),
                product.get('price', 0.0),
                product.get('discount_price', 0.0),
                product.get('stock_quantity', 0),
                product.get('sku', ''),
                product.get('category_id', ''),
                product.get('brand_id', ''),
                product.get('weight', 0.0),
                product.get('dimensions', ''),
                product.get('color', ''),
                product.get('material', ''),
                product.get('image_url', ''),
                product.get('slug', ''),
                'Yes' if product.get('is_active') else 'No',
                product.get('created_at', ''),
                product.get('updated_at', '')
            ])

        # Generazione del file CSV
        output.seek(0)
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=products.csv"}
        )
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Database error occurred.'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

@app.route('/admin/cms/pages/customers')
def customers():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/customers.html', title='Customers', username=username)
    return username

@app.route('/admin/cms/pages/marketing')
def marketing():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/marketing.html', title='Marketing', username=username)
    return username

@app.route('/admin/cms/pages/online-content')
def online_content():
    username = check_user_authentication()
    
    if isinstance(username, str):
        shop_subdomain = request.host.split('.')[0]  
        print(f"Subdomain: {shop_subdomain}")  # Log del subdominio

        try:
            with get_auth_db_connection() as auth_db_conn:
                shoplist_model = ShopList(auth_db_conn)
                shop = shoplist_model.get_shop_by_name(shop_subdomain)

            if shop:
                print(f"Shop trovato: {shop}")  # Log per il negozio

                with get_db_connection() as db_conn:
                    page_model = Page(db_conn)
                    page_slug = 'home'
                    # Esegui la query e leggi il risultato
                    page = page_model.get_page_by_slug(page_slug, shop_subdomain)

                    if page:
                        updated_at = page['updated_at']
                        now = datetime.now()
                        minutes_ago = (now - updated_at).total_seconds() // 60  
                        return render_template(
                            'admin/cms/pages/content.html', 
                            title='Online Content', 
                            username=username, 
                            page=page,
                            shop=shop,
                            minutes_ago=int(minutes_ago)  
                        )
                    else:
                        flash('Contenuto della pagina non trovato.')
                        return redirect(url_for('homepage'))

            else:
                print("Nessun negozio trovato.")  # Log per negozio non trovato
                flash('Nessun negozio trovato per questo nome.')
                return redirect(url_for('homepage'))

        except mysql.connector.Error as e:
            print(f"Errore nel database: {str(e)}")  # Log del messaggio di errore
            flash('Errore durante l\'accesso ai dati del negozio o della pagina.')
            return redirect(url_for('homepage'))
    
    return username

@app.route('/admin/cms/pages/domain')
def domain():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/domain.html', title='Domain', username=username)
    return username

@app.route('/admin/cms/pages/shipping')
def shipping():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/shipping.html', title='Shipping', username=username)
    return username



# INTERN - Subscription Script Page ---------------------------------------------------------------------------------------------

@app.route('/admin/cms/pages/subscription')
def subscription():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template(
            'admin/cms/pages/subscription.html', 
            title='Subscription', 
            username=username, 
            stripe_publishable_key=STRIPE_PUBLISHABLE_KEY
        )
    return username

@app.route('/subscription/checkout', methods=['POST'])
def create_checkout_session():
    data = request.get_json()
    plan_id = data.get('plan_id')  

    if not plan_id:
        return jsonify(error="Invalid plan ID"), 400

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan_id, 
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('subscription_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('subscription_cancel', _external=True),
        )
        
        return jsonify({'sessionId': session.id})
    
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return jsonify(error=str(e)), 500
    
@app.route('/subscription/success')
def subscription_success():
    return render_template('admin/cms/pages/sub_success.html', title="Subscription Successful")

@app.route('/subscription/cancel')
def subscription_cancel():
    return render_template('admin/cms/pages/sub_cancel.html', title="Subscription Canceled")

# Editor Store Content ---------------------------------------------------------------------------------------------

# Editor code ----------------------------------------------------------------

@app.route('/admin/cms/function/edit-code/<slug>')
def edit_code_page(slug):
    username = check_user_authentication()
    
    if isinstance(username, str):
        db_conn = get_db_connection() 

        shop_subdomain = request.host.split('.')[0]  
        
        page_model = Page(db_conn)
        
        pages = page_model.get_all_pages(shop_subdomain)  
        page = page_model.get_page_by_slug(slug, shop_subdomain) 
        
        if page:
            content = page.get('content', '')  
            return render_template('admin/cms/store_editor/code_editor.html', 
                                   title=page['title'], 
                                   pages=pages, 
                                   page=page, 
                                   slug=slug,  
                                   content=content, 
                                   username=username)
    
    return username

# Funzione per salvare il codice modificato
@app.route('/admin/cms/function/save_code', methods=['POST'])
def save_code_page():
    try:
        data = request.get_json()  
        content = data.get('content')
        slug = data.get('slug')

        if not content or not slug:
            return jsonify({'success': False, 'error': 'Missing content or slug'}), 400

        db_conn = get_db_connection()
        
        shop_subdomain = request.host.split('.')[0]  
        
        page_model = Page(db_conn)

        success = page_model.update_page_content_by_slug(slug, content, shop_subdomain)

        return jsonify({'success': success})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    
# Editor Script ----------------------------------------------------------------

@app.route('/admin/web_settings/edit')
def edit_web_settings():
    username = check_user_authentication()

    if isinstance(username, str):
        db_conn = get_db_connection()
        shop_subdomain = request.host.split('.')[0]  
        web_settings_model = WebSettings(db_conn)
        web_settings = web_settings_model.get_web_settings(shop_subdomain)  

        if web_settings:
            return render_template(
                'admin/cms/store_editor/script_editor.html',
                title='Edit Web Settings',
                username=username,
                web_settings=web_settings 
            )
        else:
            flash('Web settings not found for this shop.', 'danger')
            return redirect(url_for('homepage'))
        
    return redirect(url_for('login'))  

# Funzione per aggiornare le impostazioni web
@app.route('/admin/web_settings/update', methods=['POST'])
def update_web_settings():
    try:
        data = request.get_json()
        head_content = data.get('head')
        script_content = data.get('script')
        foot_content = data.get('foot')

        if not head_content or not script_content or not foot_content:
            return jsonify({'success': False, 'error': 'Missing content'}), 400

        db_conn = get_db_connection()
        shop_subdomain = request.host.split('.')[0]  
        web_settings_model = WebSettings(db_conn)
        success = web_settings_model.update_web_settings(shop_subdomain, head_content, script_content, foot_content)

        return jsonify({'success': success})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Editor block -------------------------------------------------------------------------------------------------------------------

@app.route('/admin/cms/store_editor/editor_interface', defaults={'slug': None})
@app.route('/admin/cms/store_editor/editor_interface/<slug>')
def editor_interface(slug=None):
    username = check_user_authentication()
    
    if isinstance(username, str):
        db_conn = get_db_connection()  
        shop_subdomain = request.host.split('.')[0]

        with get_auth_db_connection() as auth_db_conn:
            shoplist_model = ShopList(auth_db_conn)
            shop = shoplist_model.get_shop_by_name(shop_subdomain)

        if not shop:
            flash('Nessun negozio selezionato o negozio non trovato.', 'danger')
            return redirect(url_for('homepage'))

        page_model = Page(db_conn)
        pages = page_model.get_all_pages(shop_name=shop_subdomain)
        page = None
        page_title = 'CMS Interface'
        
        if slug:
            page = page_model.get_page_by_slug(slug, shop_subdomain)
            if page:
                page_title = page['title']

        # Ottenere l'addon di tipo 'theme_ui' con status 'selected' per il negozio attuale
        addon_model = CMSAddon(db_conn)
        selected_theme_ui = addon_model.get_selected_addon_for_shop(shop_subdomain, 'theme_ui')

        current_url = request.path
        return render_template('admin/cms/store_editor/editor_interface.html', 
                               title=page_title, 
                               pages=pages, 
                               page=page, 
                               slug=slug,  
                               current_url=current_url, 
                               username=username,
                               selected_theme_ui=selected_theme_ui)
    return username  


@app.route('/admin/cms/function/edit/<slug>')
def edit_page(slug):
    username = check_user_authentication()
    
    if isinstance(username, str):
        db_conn = get_db_connection()  
        shop_subdomain = request.host.split('.')[0]  

        with get_auth_db_connection() as auth_db_conn:
            shoplist_model = ShopList(auth_db_conn)
            shop = shoplist_model.get_shop_by_name(shop_subdomain)

        if not shop:
            flash('Nessun negozio selezionato o negozio non trovato.', 'danger')
            return redirect(url_for('homepage'))

        # Recupera la lingua selezionata
        language = request.args.get('language', 'en')  # Default "en" se non è specificata

        page_model = Page(db_conn)
        page = page_model.get_page_by_slug_and_language(slug, language, shop_subdomain)  

        if not page:
            flash('Pagina non trovata.', 'danger')
            return redirect(url_for('homepage'))

        # Recupera il tema UI selezionato per lo shop
        addon_model = CMSAddon(db_conn)
        selected_theme_ui = addon_model.get_selected_addon_for_shop(shop_subdomain, 'theme_ui')

        # Recupera i dettagli del prodotto se la pagina contiene riferimenti a prodotti
        product_model = Products(db_conn)
        product_references = page_model.get_product_references(page['id'])  # Supponendo esista un metodo per i riferimenti ai prodotti
        products = []
        for product_id in product_references:
            product = product_model.get_product_by_id(product_id)
            if product:
                product['images'] = product_model.get_product_images(product['id'])
                products.append(product)

        return render_template(
            'admin/cms/function/edit.html', 
            title='Edit Page', 
            page=page, 
            username=username, 
            selected_theme_ui=selected_theme_ui,
            products=products  # Passa i dati del prodotto al template
        )
    
    return username

# SALVATAGGIO PAGINA CON CARICAMENTO IMMAGINI ----------------------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(base64_image, page_id, shop_subdomain):
    try:
        header, encoded = base64_image.split(",", 1)
        binary_data = base64.b64decode(encoded)

        # Creazione della cartella per il negozio specifico
        upload_folder = f"static/uploads/{shop_subdomain}"
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)  

        # Nome univoco per ogni immagine, ad esempio usando un UUID
        image_name = f"{page_id}_{uuid.uuid4().hex}.png"
        image_path = os.path.join(upload_folder, image_name)

        # Salva l'immagine
        with open(image_path, "wb") as f:
            f.write(binary_data)

        return f"/{upload_folder}/{image_name}"
    except Exception as e:
        print(f"Error saving image: {str(e)}")
        return None

# Funzione per salvare il contenuto della pagina con gestione delle immagini ---------------------------------
@app.route('/admin/cms/function/save', methods=['POST'])
def save_page():
    try:
        data = request.get_json()
        page_id = data.get('id')
        content = data.get('content')
        language = data.get('language')  # Aggiungiamo il parametro lingua
        shop_subdomain = request.host.split('.')[0]

        print(f"Salvataggio pagina con ID: {page_id}, lingua: {language} per il negozio: {shop_subdomain}")
        
        db_conn = get_db_connection()  
        page_model = Page(db_conn)  
        
        # Cerca immagini base64 nel contenuto
        img_tags = re.findall(r'<img.*?src=["\'](data:image/[^"\']+)["\']', content)
        for base64_img in img_tags:
            # Salva l'immagine base64
            image_url = save_image(base64_img, page_id, shop_subdomain)
            if image_url:
                # Sostituisci l'immagine base64 con l'URL dell'immagine salvata
                content = content.replace(base64_img, image_url)
        
        # Aggiorna il contenuto della pagina nel database con la lingua specifica
        success = page_model.update_or_create_page_content(page_id, content, language, shop_subdomain)
        return jsonify({'success': success})
    
    except Exception as e:
        print(f"Errore durante il salvataggio della pagina: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Funzione per salvare un'immagine base64 generica ---------------------------------------------------------------
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

# Endpoint Flask per gestire l'upload delle immagini generiche -------------------------------------------------------
@app.route('/upload-image', methods=['POST'])
def upload_image():
    data = request.get_json()
    base64_image = data.get('image')

    if not base64_image:
        return jsonify({'error': 'No image provided'}), 400

    image_url = save_base64_image(base64_image)
    
    if image_url:
        return jsonify({'url': image_url}), 200
    else:
        return jsonify({'error': 'Failed to upload image'}), 500
    
# Upload SEO -------------------------------------------------------

# Funzione per salvare i dati SEO della pagina
@app.route('/admin/cms/function/save-seo', methods=['POST'])
def save_seo_page():
    data = request.get_json()
    page_id = data.get('id')
    title = data.get('title')
    description = data.get('description')
    keywords = data.get('keywords')
    slug = data.get('slug')

    shop_subdomain = request.host.split('.')[0]  

    db_conn = get_db_connection()  
    page_model = Page(db_conn)  

    success = page_model.update_page_seo(page_id, title, description, keywords, slug, shop_name=shop_subdomain)

    return jsonify({'success': success})


# Funzione per creare una nuova pagina per un negozio specifico
@app.route('/admin/cms/function/create', methods=['POST'])
def create_page():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'You need to log in first.'})

    if request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        keywords = data.get('keywords')
        slug = data.get('slug')
        content = data.get('content')
        theme_name = data.get('theme_name')
        paid = data.get('paid')
        language = data.get('language')
        published = data.get('published')

        shop_subdomain = request.host.split('.')[0]  

        db_conn = get_db_connection()
        page_model = Page(db_conn)  

        success = page_model.create_page(title, description, keywords, slug, content, theme_name, paid, language, published, shop_name=shop_subdomain)

        return jsonify({'success': success})
    

# Funzione per eliminare una pagina di un negozio specifico
@app.route('/admin/cms/function/delete', methods=['POST'])
def delete_page():
    data = request.get_json()
    page_id = data.get('id')  

    if not page_id:
        return jsonify({'success': False, 'message': 'ID pagina mancante.'})
    shop_subdomain = request.host.split('.')[0]  

    page_model = Page(get_db_connection())  
    try:
        page_model.delete_page(page_id, shop_name=shop_subdomain)  
        return jsonify({'success': True, 'message': 'Pagina cancellata con successo.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f"Errore durante la cancellazione: {str(e)}"})

# SCRIPT PAGE --------------------------------------------------------------------------------------------------------

# STORE -----------------------------------------------------------------------------------------------------
@app.route('/capture-screenshot', methods=['POST'])
def capture_screenshot_route():
    try:
        capture_screenshot('http://127.0.0.1:5000/', 'static/images/screenshot_result.png')
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Addons e Componenti a pagamento aggiuntive -----------------------------------------------------------------------------

@app.route('/store-components/theme-ui')
def theme_ui():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]
        with get_db_connection() as db_conn:
            addon_model = CMSAddon(db_conn)
            theme_ui_addons = addon_model.get_addons_by_type('theme_ui')
            for addon in theme_ui_addons:
                status = addon_model.get_addon_status(shop_name, addon['id'])
                addon['status'] = status if status else 'select'
        return render_template(
            'admin/cms/store-components/theme-ui.html',
            title='Theme UI',
            username=username,
            addons=theme_ui_addons
        )
    return username


@app.route('/store-components/plugin')
def plugin():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]
        with get_db_connection() as db_conn:
            addon_model = CMSAddon(db_conn)
            plugin_addons = addon_model.get_addons_by_type('plugin')
            for addon in plugin_addons:
                status = addon_model.get_addon_status(shop_name, addon['id'])
                addon['status'] = status if status else 'select'
        return render_template(
            'admin/cms/store-components/plugin.html',
            title='Plugin',
            username=username,
            addons=plugin_addons
        )
    return username


@app.route('/store-components/services')
def services():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]
        with get_db_connection() as db_conn:
            addon_model = CMSAddon(db_conn)
            service_addons = addon_model.get_addons_by_type('service')
            
            for addon in service_addons:
                status = addon_model.get_addon_status(shop_name, addon['id'])
                
                # Se lo stato è 'purchased', assicuriamoci che non possa essere modificato
                if status == 'purchased':
                    addon['status'] = 'purchased'
                elif status == 'selected':
                    addon['status'] = 'selected'
                else:
                    addon['status'] = 'select'  # Default per add-ons non selezionati né acquistati

        return render_template(
            'admin/cms/store-components/services.html',
            title='Services',
            username=username,
            addons=service_addons
        )
    
    return username


@app.route('/store-components/themes')
def themes():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_name = request.host.split('.')[0]
        with get_db_connection() as db_conn:
            addon_model = CMSAddon(db_conn)
            theme_addons = addon_model.get_addons_by_type('theme')
            for addon in theme_addons:
                status = addon_model.get_addon_status(shop_name, addon['id'])
                addon['status'] = status if status else 'select'
        return render_template(
            'admin/cms/store-components/themes.html',
            title='Themes',
            username=username,
            addons=theme_addons
        )
    return username


# Route per selezionare un addon
@app.route('/api/select-addon', methods=['POST'])
def select_addon():
    data = request.get_json()
    shop_name = request.host.split('.')[0]
    addon_id = data.get('addon_id')
    addon_type = data.get('addon_type')
    with get_db_connection() as db_conn:
        addon_model = CMSAddon(db_conn)
        
        # Assicurati di impostare "selected" per l'addon attuale e "deselected" per tutti gli altri dello stesso tipo
        success = addon_model.update_shop_addon_status(shop_name, addon_id, addon_type, 'selected')
        if success:
            # Deseleziona altri addon dello stesso tipo per lo stesso negozio
            addon_model.deselect_other_addons(shop_name, addon_id, addon_type)

    if success:
        return jsonify({'status': 'success', 'message': 'Addon selected successfully'})
    return jsonify({'status': 'error', 'message': 'Failed to select addon'}), 500


# Route per acquistare un addon
@app.route('/api/purchase-addon', methods=['POST'])
def purchase_addon():
    data = request.get_json()
    shop_name = request.host.split('.')[0]
    addon_id = data.get('addon_id')
    addon_type = data.get('addon_type')
    with get_db_connection() as db_conn:
        addon_model = CMSAddon(db_conn)
        success = addon_model.update_shop_addon_status(shop_name, addon_id, addon_type, 'paid')
    if success:
        return jsonify({'status': 'success', 'message': 'Addon purchased successfully'})
    return jsonify({'status': 'error', 'message': 'Failed to purchase addon'}), 500

# ----------- Cookie e policy ----------------------------------------------------------------------------------------

@app.route('/admin/cms/function/cookie-policy', methods=['GET', 'POST'])
def cookie_setting():
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_name = request.host.split('.')[0]

    with get_db_connection() as db_conn:
        cookie_model = CookiePolicy(db_conn)

        if request.method == 'POST':
            # Verifica se la richiesta è di tipo JSON
            if request.is_json:
                # Ottieni i dati dalla richiesta JSON
                data = request.json
                title = data.get('title')
                text_content = data.get('text_content')
                button_text = data.get('button_text')
                background_color = data.get('background_color')
                button_color = data.get('button_color')
                button_text_color = data.get('button_text_color')
                text_color = data.get('text_color')
                entry_animation = data.get('animation')

                # Controlla se esiste già una configurazione per questo negozio
                existing_setting = cookie_model.get_policy_by_shop(shop_name)

                # Aggiorna o crea la configurazione interna
                if existing_setting:
                    success = cookie_model.update_internal_policy(
                        shop_name, title, text_content, button_text,
                        background_color, button_color, button_text_color,
                        text_color, entry_animation
                    )
                else:
                    success = cookie_model.create_internal_policy(
                        shop_name, title, text_content, button_text,
                        background_color, button_color, button_text_color,
                        text_color, entry_animation
                    )

                # Ritorna il risultato come JSON per il feedback AJAX
                return jsonify({'success': success})

            # Ritorna errore se la richiesta non è JSON
            return jsonify({'success': False, 'error': 'Invalid request format'})

        else:
            # Recupera le impostazioni esistenti, se presenti
            cookie_settings = cookie_model.get_policy_by_shop(shop_name)

            return render_template(
                'admin/cms/function/cookie-policy.html',
                title='Cookie Bar Settings',
                username=username,
                cookie_settings=cookie_settings
            )


@app.route('/admin/cms/function/cookie-policy-third-party', methods=['GET', 'POST'])
def cookie_setting_third_party():
    username = check_user_authentication()
    if not isinstance(username, str):
        return username

    shop_name = request.host.split('.')[0]

    with get_db_connection() as db_conn:
        cookie_model = CookiePolicy(db_conn)

        if request.method == 'POST':
            data = request.get_json()  # Modifica per accettare JSON
            if not data:
                return jsonify({'status': 'error', 'message': 'Invalid JSON data.'}), 400

            # Dati dal JSON per la configurazione di terze parti
            use_third_party = data.get('use_third_party', False)
            third_party_cookie = data.get('third_party_cookie', '')
            third_party_privacy = data.get('third_party_privacy', '')
            third_party_terms = data.get('third_party_terms', '')
            third_party_consent = data.get('third_party_consent', '')

            # Aggiorna o crea la configurazione di terze parti
            existing_setting = cookie_model.get_policy_by_shop(shop_name)
            if existing_setting:
                success = cookie_model.update_third_party_policy(
                    shop_name, use_third_party, third_party_cookie, 
                    third_party_privacy, third_party_terms, third_party_consent
                )
            else:
                success = cookie_model.create_third_party_policy(
                    shop_name, use_third_party, third_party_cookie, 
                    third_party_privacy, third_party_terms, third_party_consent
                )

            # Risposte JSON per richiesta AJAX
            if success:
                return jsonify({'status': 'success', 'message': 'Third-party cookie settings updated successfully!'})
            else:
                return jsonify({'status': 'error', 'message': 'Error updating third-party cookie settings.'}), 500

        # Recupera le impostazioni esistenti, se presenti
        cookie_settings = cookie_model.get_policy_by_shop(shop_name)

        return render_template(
            'admin/cms/function/cookie-policy-third-party.html',
            title='Third-Party Cookie Settings',
            username=username,
            cookie_settings=cookie_settings
        )
    
