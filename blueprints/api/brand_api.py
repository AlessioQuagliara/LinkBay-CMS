from flask import Blueprint, jsonify, request
from models.database import db
from models.products import Brand
import logging

logging.basicConfig(level=logging.INFO)

brands_bp = Blueprint('brandsApi', __name__, url_prefix='/api/')

@brands_bp.route('/create_brand', methods=['POST'])
def create_brand():
    """ API per creare un nuovo brand associato a uno shop. """
    try:
        data = request.json
        name = data.get('name', '').strip()  
        shop_name = request.host.split('.')[0]  

        if not name:
            return jsonify({'success': False, 'message': 'Brand name is required.'}), 400

        existing_brand = Brand.query.filter_by(name=name).first()
        if existing_brand:
            return jsonify({'success': False, 'message': 'Brand already exists.'}), 409

        new_brand = Brand(name=name)
        db.session.add(new_brand)
        db.session.commit()  

        return jsonify({'success': True, 'brand_id': new_brand.id}), 201

    except Exception as e:
        logging.error(f"Errore durante la creazione del brand: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500