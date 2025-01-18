from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect, Response
from models.products import Products  # importo la classe database
from models.categories import Categories
import os, uuid, csv, io, mysql.connector, base64
from db_helpers import DatabaseHelper
db_helper = DatabaseHelper()
from db_helpers import DatabaseHelper
from helpers import check_user_authentication
import logging
logging.basicConfig(level=logging.INFO)

# Blueprint
products_bp = Blueprint('products', __name__)

# Rotte per la gestione

@products_bp.route('/admin/cms/pages/products')
def products():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_subdomain = request.host.split('.')[0]  # Ottieni il nome del negozio dal sottodominio
        with db_helper.get_db_connection() as db_conn:
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

@products_bp.route('/admin/cms/pages/product/<int:product_id>', methods=['GET', 'POST'])
@products_bp.route('/admin/cms/pages/product', methods=['GET', 'POST'])
def manage_product(product_id=None):
    username = check_user_authentication()
    if isinstance(username, str):
        with db_helper.get_db_connection() as db_conn:
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
                    logging.info(f"Error managing product: {e}")
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


@products_bp.route('/admin/cms/create_product', methods=['POST'])
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

        with db_helper.get_db_connection() as db_conn:
            product_model = Products(db_conn)
            new_product_id = product_model.create_product(default_values)

        return jsonify({
            'success': True,
            'message': 'Product created successfully.',
            'product_id': new_product_id
        })
    except Exception as e:
        logging.info(f"Error creating product: {e}")
        return jsonify({'success': False, 'message': 'Failed to create product.'}), 500
    
@products_bp.route('/admin/cms/delete_products', methods=['POST'])
def delete_products():
    try:
        data = request.get_json()  # Ottieni i dati dalla richiesta
        product_ids = data.get('product_ids')  # Array di ID dei prodotti da eliminare

        if not product_ids:
            return jsonify({'success': False, 'message': 'No product IDs provided.'}), 400

        with db_helper.get_db_connection() as db_conn:
            product_model = Products(db_conn)
            for product_id in product_ids:
                success = product_model.delete_product(product_id)
                if not success:
                    return jsonify({'success': False, 'message': f'Failed to delete product with ID {product_id}.'}), 500

        return jsonify({'success': True, 'message': 'Selected products deleted successfully.'})
    except Exception as e:
        logging.info(f"Error deleting products: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500

@products_bp.route('/admin/cms/update_product', methods=['POST'])
def update_product():
    try:
        data = request.form.to_dict()  # Usa request.form per raccogliere i dati del FormData
        product_id = data.get('id')

        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID is required.'}), 400

        # Connetti al database
        with db_helper.get_db_connection() as db_conn:
            product_model = Products(db_conn)
            success = product_model.update_product(product_id, data)

        if success:
            return jsonify({'success': True, 'message': 'Product updated successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update the product.'}), 500
    except Exception as e:
        logging.info(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
    
@products_bp.route('/admin/cms/upload_image_product', methods=['POST'])
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
        db_conn = db_helper.get_db_connection()
        products_model = Products(db_conn)
        image_id = products_model.add_product_image(product_id, f"/{image_path}")

        if image_id:
            return jsonify({'success': True, 'image_url': f"/{image_path}", 'image_id': image_id})
        else:
            return jsonify({'success': False, 'message': 'Failed to save image to database.'}), 500
    except Exception as e:
        logging.info(f"Error uploading image: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during upload.'}), 500
    
@products_bp.route('/admin/cms/delete_image_product', methods=['POST'])
def delete_image_product():
    try:
        data = request.get_json()
        image_id = data.get('image_id')

        if not image_id:
            return jsonify({'success': False, 'message': 'Image ID is missing.'}), 400

        db_conn = db_helper.get_db_connection()
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
        logging.info(f"Error deleting image: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500
    
@products_bp.route('/admin/cms/export_products', methods=['GET'])
def export_products():
    shop_name = request.host.split('.')[0]  # Sottodominio per identificare il negozio

    try:
        # Connessione al database
        with db_helper.get_db_connection() as db_conn:
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
        logging.info(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Database error occurred.'}), 500
    except Exception as e:
        logging.info(f"Unexpected error: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
    
# Funzione per salvare un'immagine base64 generica ---------------------------------------------------------------
def save_base64_image(base64_image, upload_folder):
    try:
        header, encoded = base64_image.split(",", 1)
        binary_data = base64.b64decode(encoded)

        # Genera un nome file unico usando UUID
        unique_filename = f"{uuid.uuid4().hex}.png"
        file_path = os.path.join(upload_folder, unique_filename)

        # Salva il file sul server
        with open(file_path, "wb") as f:
            f.write(binary_data)

        return f"/static/uploads/{unique_filename}"
    except Exception as e:
        logging.info(f"Errore durante il salvataggio dell'immagine: {str(e)}")
        return None