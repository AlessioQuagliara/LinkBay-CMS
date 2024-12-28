from flask import Blueprint, request, jsonify
from models.categories import Categories  # importo la classe database
from db_helpers import DatabaseHelper
from helpers import check_user_authentication

db_helper = DatabaseHelper()

# Blueprint
categories_bp = Blueprint('categories', __name__)

# Rotte per la gestione
@categories_bp.route('/admin/cms/create_category', methods=['POST'])
def create_category():
    try:
        data = request.json
        name = data.get('name')
        shop_name = request.host.split('.')[0]
        if not name:
            return jsonify({'success': False, 'message': 'Category name is required.'}), 400

        with db_helper.get_db_connection() as db_conn:
            categories_model = Categories(db_conn)
            category_id = categories_model.create_category(shop_name, name)
            if category_id:
                return jsonify({'success': True, 'category_id': category_id})
            else:
                return jsonify({'success': False, 'message': 'Failed to create category.'}), 500
    except Exception as e:
        print(f"Error creating category: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500
