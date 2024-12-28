from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect
#from models.domain import Domain   importo la classe 
from db_helpers import DatabaseHelper
from db_helpers import DatabaseHelper
from helpers import check_user_authentication

db_helper = DatabaseHelper()

# Blueprint
domain_bp = Blueprint('domain', __name__)

# Rotte per la gestione

@domain_bp.route('/admin/cms/pages/domain')
def domain():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/pages/domain.html', title='Domain', username=username)
    return username