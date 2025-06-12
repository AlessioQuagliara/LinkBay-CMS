from flask import Blueprint, request, jsonify, redirect, current_app, flash, url_for
from werkzeug.security import generate_password_hash
from models.database import db
from models.shoplist import ShopList
from models.user import User 
from models.stores_info import StoreInfo
from models.userstoreaccess import UserStoreAccess
from models.products import Product, ProductVariant, ProductImage, Category, Collection, CollectionImage, CollectionProduct
from models.database import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from flask import session
import stripe
import logging
import os
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_fields(*fields):
    return all(field for field in fields)

product_api = Blueprint('productApi', __name__, url_prefix='/api/')



# Route API per copiare i prodotti selezionati
@product_api.route('copy_products', methods=['POST'])
def copy_products():
    try:
        product_ids = request.json.get('product_ids', [])
        if not product_ids:
            return jsonify({'status': 'error', 'message': 'Nessun ID prodotto fornito.'}), 400

        copied_ids = []
        for product_id in product_ids:
            product = Product.query.get(product_id)
            if product:
                new_product = Product(
                    shop_id=product.shop_id,
                    name=f"{product.name} (Copia)",
                    description=product.description,
                    short_description=product.short_description,
                    price=product.price,
                    discount_price=product.discount_price,
                    stock_quantity=product.stock_quantity,
                    slug=f"{product.slug}-copy-{datetime.utcnow().timestamp()}",
                    is_active=False,
                    category_id=product.category_id,
                    is_digital=product.is_digital
                )
                db.session.add(new_product)
                db.session.flush()  # Ottieni l'ID
                copied_ids.append(new_product.id)

        db.session.commit()
        return jsonify({'status': 'success', 'copied_ids': copied_ids})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Errore durante la copia prodotti: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Errore durante la copia.'}), 500


# Route API per eliminare i prodotti selezionati
@product_api.route('delete_products', methods=['POST'])
def delete_products():
    try:
        product_ids = request.json.get('product_ids', [])
        if not product_ids:
            return jsonify({'status': 'error', 'message': 'Nessun ID prodotto fornito.'}), 400

        for product_id in product_ids:
            product = Product.query.get(product_id)
            if product:
                db.session.delete(product)

        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Prodotti eliminati con successo.'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Errore durante eliminazione prodotti: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Errore durante eliminazione.'}), 500
    

# Route API per eliminare una singola immagine di un prodotto
@product_api.route('delete_product_image/<int:image_id>', methods=['DELETE'])
def delete_product_image(image_id):
    try:
        image = ProductImage.query.get(image_id)
        if not image:
            return jsonify({'status': 'error', 'message': 'Immagine non trovata.'}), 404

        # Rimuove fisicamente il file se esiste
        image_path = os.path.join(current_app.root_path, 'static', image.url.lstrip('/'))
        if os.path.exists(image_path):
            os.remove(image_path)

        # Rimuove la riga dal DB
        db.session.delete(image)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Immagine eliminata con successo.'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Errore durante l'eliminazione immagine: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Errore durante l\'eliminazione dell\'immagine.'}), 500

@product_api.route("/product_images/<int:product_id>", methods=["GET"])
def api_get_product_images(product_id):
    shop_subdomain = request.host.split('.')[0]
    shop = db.session.query(ShopList).filter_by(shop_name=shop_subdomain).first()
    if not shop:
        return jsonify({"success": False, "error": "Negozio non trovato"}), 404

    product = db.session.query(Product).filter_by(id=product_id, shop_id=shop.id).first()
    if not product:
        return jsonify({"success": False, "error": "Prodotto non trovato"}), 404

    images = [
        {
            "id": img.id,
            "url": img.url,
            "is_main": img.is_main
        } for img in product.images
    ]

    return jsonify({"success": True, "images": images})

@product_api.route("/set_main_image/<int:image_id>", methods=["POST"])
def set_main_image(image_id):
    image = ProductImage.query.get(image_id)
    if not image:
        return jsonify({"success": False, "error": "Immagine non trovata"}), 404

    ProductImage.query.filter_by(product_id=image.product_id).update({'is_main': False})
    image.is_main = True
    db.session.commit()

    return jsonify({"success": True})

@product_api.route("/delete_image/<int:image_id>", methods=["POST"])
def delete_image(image_id):
    image = ProductImage.query.get(image_id)
    if not image:
        return jsonify({"success": False, "error": "Immagine non trovata"}), 404

    try:
        filepath = os.path.join("static", image.url.strip("/"))
        if os.path.exists(filepath):
            os.remove(filepath)
        db.session.delete(image)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        logging.error(f"Errore eliminazione immagine: {str(e)}")
        return jsonify({"success": False, "error": "Errore server"}), 500