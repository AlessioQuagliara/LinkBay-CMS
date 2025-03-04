from flask import Blueprint, render_template, request, jsonify, Response
from models.database import db
from models.products import Product, ProductImage
from models.categories import Category
import os, uuid, csv, io, base64, logging
from helpers import check_user_authentication
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO)

# Blueprint
products_bp = Blueprint('products', __name__)

# 🔹 **Pagina di gestione prodotti**
@products_bp.route('/admin/cms/pages/products')
def products():
    username = check_user_authentication()
    if isinstance(username, str):
        shop_subdomain = request.host.split('.')[0]
        
        products_list = Product.query.filter_by(shop_name=shop_subdomain).all()
        categories = Category.query.filter_by(shop_name=shop_subdomain).all()

        return render_template(
            'admin/cms/pages/products.html', 
            title='Products', 
            username=username, 
            categories=categories,
            products=products_list
        )
    return username

# 🔹 **Gestione singolo prodotto (GET per visualizzare, POST per modificare)**
@products_bp.route('/admin/cms/pages/product/<int:product_id>', methods=['GET', 'POST'])
@products_bp.route('/admin/cms/pages/product', methods=['GET', 'POST'])
def manage_product(product_id=None):
    username = check_user_authentication()
    if isinstance(username, str):
        shop_subdomain = request.host.split('.')[0]

        if request.method == 'POST':
            try:
                data = request.form.to_dict()
                if product_id:
                    product = Product.query.filter_by(id=product_id, shop_name=shop_subdomain).first()
                    if not product:
                        return jsonify({'status': 'error', 'message': 'Product not found'}), 404
                    for key, value in data.items():
                        setattr(product, key, value)
                else:
                    new_product = Product(shop_name=shop_subdomain, **data)
                    db.session.add(new_product)

                db.session.commit()
                return jsonify({'status': 'success', 'message': 'Product saved successfully'})
            except SQLAlchemyError as e:
                db.session.rollback()
                logging.error(f"❌ Error managing product: {str(e)}")
                return jsonify({'status': 'error', 'message': 'An error occurred'}), 500

        product = Product.query.filter_by(id=product_id, shop_name=shop_subdomain).first() if product_id else None
        images = product.images if product else []
        categories = Category.query.filter_by(shop_name=shop_subdomain).all()

        return render_template(
            'admin/cms/pages/manage_product.html',
            title='Manage Product',
            username=username,
            product=product,
            images=images,
            categories=categories,
            shop_subdomain=shop_subdomain
        )
    return username


@products_bp.route('/admin/cms/create_product', methods=['POST'])
def create_product():
    try:
        shop_subdomain = request.host.split('.')[0]  # Ottieni il sottodominio dello shop

        # Creazione del nuovo prodotto con valori predefiniti
        new_product = Product(
            name="New Product",
            short_description="Short description",
            description="Detailed description",
            price=0.0,
            discount_price=0.0,
            stock_quantity=0,
            sku=f"SKU-{uuid.uuid4().hex[:8]}",  # SKU univoco generato
            category_id=None,  
            brand_id=None,
            weight=0.0,
            dimensions="0x0x0",
            color="Default color",
            material="Default material",
            image_url="/static/images/default.png",
            slug=f"new-product-{uuid.uuid4().hex[:8]}",  # Slug univoco generato
            is_active=False,
            shop_name=shop_subdomain
        )

        db.session.add(new_product)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Product created successfully.',
            'product_id': new_product.id
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Error creating product: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to create product.'}), 500
    
@products_bp.route('/admin/cms/delete_products', methods=['POST'])
def delete_products():
    try:
        data = request.get_json()
        product_ids = data.get('product_ids')

        if not product_ids:
            return jsonify({'success': False, 'message': 'No product IDs provided.'}), 400

        # Eliminazione multipla usando SQLAlchemy ORM
        db.session.query(Product).filter(Product.id.in_(product_ids)).delete(synchronize_session=False)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Selected products deleted successfully.'})
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Error deleting products: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500

@products_bp.route('/admin/cms/update_product', methods=['POST'])
def update_product():
    try:
        data = request.form.to_dict()
        product_id = data.get('id')

        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID is required.'}), 400

        # Verifica se il prodotto esiste
        product = db.session.query(Product).filter_by(id=product_id).first()
        if not product:
            return jsonify({'success': False, 'message': 'Product not found.'}), 404

        # Aggiorna il prodotto con i nuovi dati
        for key, value in data.items():
            if hasattr(product, key):
                setattr(product, key, value)

        db.session.commit()

        return jsonify({'success': True, 'message': 'Product updated successfully!'})
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Error updating product: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
    
@products_bp.route('/admin/cms/upload_image_product', methods=['POST'])
def upload_image_product():
    try:
        product_id = request.form.get('product_id')
        image = request.files.get('image')

        if not product_id or not image:
            return jsonify({'success': False, 'message': 'Product ID or image is missing.'}), 400

        # Verifica se il prodotto esiste
        product = db.session.query(Product).filter_by(id=product_id).first()
        if not product:
            return jsonify({'success': False, 'message': 'Product not found.'}), 404

        # Genera un nome univoco per il file
        unique_filename = f"{uuid.uuid4().hex}_{image.filename}"
        upload_folder = os.path.join('static', 'uploads', 'products')
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, unique_filename)

        # Salva il file
        image.save(image_path)

        # Aggiungi l'immagine al database
        new_image = ProductImage(product_id=product_id, image_url=f"/{image_path}")
        db.session.add(new_image)
        db.session.commit()

        return jsonify({'success': True, 'image_url': f"/{image_path}", 'image_id': new_image.id})
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Error uploading image: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred during upload.'}), 500
    
@products_bp.route('/admin/cms/delete_image_product', methods=['POST'])
def delete_image_product():
    try:
        data = request.get_json()
        image_id = data.get('image_id')

        if not image_id:
            return jsonify({'success': False, 'message': 'Image ID is missing.'}), 400

        # Recupera l'immagine dal database
        image = db.session.query(ProductImage).filter_by(id=image_id).first()

        if not image:
            return jsonify({'success': False, 'message': 'Image not found.'}), 404

        # Rimuove il file dal filesystem se esiste
        image_path = image.image_url.lstrip('/')
        if os.path.exists(image_path):
            os.remove(image_path)

        # Elimina il record dal database
        db.session.delete(image)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Image deleted successfully.'})
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Error deleting image: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500
    
@products_bp.route('/admin/cms/export_products', methods=['GET'])
def export_products():
    shop_name = request.host.split('.')[0]  # Sottodominio per identificare il negozio

    try:
        # Recupera tutti i prodotti per il negozio specifico
        products = db.session.query(Product).filter_by(shop_name=shop_name).all()

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
                product.id,
                product.name,
                product.description,
                product.short_description,
                product.price,
                product.discount_price,
                product.stock_quantity,
                product.sku,
                product.category_id or '',
                product.brand_id or '',
                product.weight,
                product.dimensions,
                product.color,
                product.material,
                product.image_url,
                product.slug,
                'Yes' if product.is_active else 'No',
                product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                product.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        # Generazione del file CSV
        output.seek(0)
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=products.csv"}
        )

    except SQLAlchemyError as e:
        logging.error(f"❌ Database error: {str(e)}")
        return jsonify({'success': False, 'message': 'Database error occurred.'}), 500
    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}")
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