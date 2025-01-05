from flask import Blueprint, request, jsonify, render_template, url_for
from models.domain import Domain  # importo la classe database
from config import Config
from db_helpers import DatabaseHelper
db_helper = DatabaseHelper()
from db_helpers import DatabaseHelper
from helpers import check_user_authentication

# Blueprint
domain_bp = Blueprint('domain', __name__)

# Rotte per la gestione

@domain_bp.route('/admin/cms/pages/domain')
def domain():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/domain.html', title='Domain', username=username)
    return username

