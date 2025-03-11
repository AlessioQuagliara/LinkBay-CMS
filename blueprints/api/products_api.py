from flask import Blueprint, jsonify, request, session
from models.database import db
from models.products import Product, ProductImage, create_new_product
import logging
import os
import uuid
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO)

productsapi_bp = Blueprint('productsApi', __name__, url_prefix='/api/')

# 📌 CREA UN NUOVO PRODOTTO
@productsapi_bp.route('/create_product', methods=['POST'])
def create_product():
    try:
        shop_subdomain = request.host.split('.')[0]  # Ottieni il sottodominio dello shop
        result = create_new_product(shop_subdomain)
        return jsonify(result), (200 if result['success'] else 500)
    except Exception as e:
        logging.error(f"❌ Error creating product: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while creating the product.'}), 500

# 📌 ELIMINA PRODOTTI MULTIPLI
@productsapi_bp.route('/delete_products', methods=['POST'])
def delete_products():
    try:
        data = request.get_json()
        product_ids = data.get('product_ids')

        if not product_ids:
            return jsonify({'success': False, 'message': 'No product IDs provided.'}), 400

        db.session.query(Product).filter(Product.id.in_(product_ids)).delete(synchronize_session=False)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Selected products deleted successfully.'})
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Error deleting products: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500

# 📌 AGGIORNA UN PRODOTTO
@productsapi_bp.route('/update_product', methods=['POST'])
def update_product():
    try:
        data = request.form.to_dict()
        product_id = data.get('id')

        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID is required.'}), 400

        product = db.session.query(Product).filter_by(id=product_id).first()
        if not product:
            return jsonify({'success': False, 'message': 'Product not found.'}), 404

        for key, value in data.items():
            if hasattr(product, key):
                attr_type = type(getattr(product, key))  
                
                # ✅ Converti i tipi di dato
                if attr_type == bool:
                    setattr(product, key, value.lower() in ['true', '1', 'yes'])  
                elif attr_type == int:
                    setattr(product, key, int(value) if value.isdigit() else None)  
                elif attr_type == float:
                    setattr(product, key, float(value) if value.replace('.', '', 1).isdigit() else None)  
                else:
                    setattr(product, key, value if value.lower() != "none" else None)  

        db.session.commit()
        return jsonify({'success': True, 'message': 'Product updated successfully!'})

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Error updating product: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

# 📌 CARICA UN'IMMAGINE PER UN PRODOTTO
@productsapi_bp.route('/upload_image_product', methods=['POST'])
def upload_image_product():
    try:
        product_id = request.form.get('product_id')
        image = request.files.get('image')

        if not product_id or not image:
            return jsonify({'success': False, 'message': 'Product ID or image is missing.'}), 400

        product = db.session.query(Product).filter_by(id=product_id).first()
        if not product:
            return jsonify({'success': False, 'message': 'Product not found.'}), 404

        unique_filename = f"{uuid.uuid4().hex}_{image.filename}"
        upload_folder = os.path.join('static', 'uploads', 'products')
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, unique_filename)

        image.save(image_path)

        new_image = ProductImage(product_id=product_id, image_url=f"/{image_path}")
        db.session.add(new_image)
        db.session.commit()

        return jsonify({'success': True, 'image_url': f"/{image_path}", 'image_id': new_image.id})
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Error uploading image: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred during upload.'}), 500

# 📌 ELIMINA UN'IMMAGINE DI UN PRODOTTO
@productsapi_bp.route('/delete_image_product', methods=['POST'])
def delete_image_product():
    try:
        data = request.get_json()
        image_id = data.get('image_id')

        if not image_id:
            return jsonify({'success': False, 'message': 'Image ID is missing.'}), 400

        image = db.session.query(ProductImage).filter_by(id=image_id).first()
        if not image:
            return jsonify({'success': False, 'message': 'Image not found.'}), 404

        image_path = image.image_url.lstrip('/')
        if os.path.exists(image_path):
            os.remove(image_path)

        db.session.delete(image)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Image deleted successfully.'})
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"❌ Error deleting image: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred during deletion.'}), 500
    
# 📌 API per salvare gli ID dei prodotti copiati nella sessione
@productsapi_bp.route('/set_copied_products', methods=['POST'])
def set_copied_products():
    """ Salva gli ID dei prodotti copiati nella sessione Flask """
    data = request.get_json()
    product_ids = data.get('product_ids', [])

    if not product_ids:
        return jsonify({'success': False, 'message': 'No product IDs provided'}), 400

    session['copied_product_ids'] = product_ids
    logging.info(f"✅ Copied product IDs saved in session: {product_ids}")

    return jsonify({'success': True, 'message': 'Product IDs saved successfully'})

# 📌 API per recuperare gli ID dei prodotti copiati dalla sessione
@productsapi_bp.route('/get_copied_products', methods=['GET'])
def get_copied_products():
    """ Recupera gli ID dei prodotti copiati dalla sessione Flask """
    product_ids = session.get('copied_product_ids', [])
    return jsonify({'success': True, 'product_ids': product_ids})

# 📌 API per ottenere prodotti tramite ID
@productsapi_bp.route('/get_products_by_ids', methods=['POST'])
def get_products_by_ids():
    data = request.get_json()
    product_ids = data.get('product_ids', [])

    if not product_ids:
        return jsonify({'success': False, 'message': 'No product IDs provided.'}), 400

    products = Product.query.filter(Product.id.in_(product_ids)).all()

    if products:
        return jsonify({'success': True, 'products': [product.to_dict() for product in products]})
    return jsonify({'success': False, 'message': 'No products found.'}), 404
