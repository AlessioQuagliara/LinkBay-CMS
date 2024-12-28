from flask import Blueprint, request, jsonify, session, render_template
from db_helpers import DatabaseHelper
db_helper = DatabaseHelper()
from db_helpers import DatabaseHelper
from helpers import check_user_authentication

# Blueprint
ui_bp = Blueprint('ui', __name__)

# Rotte per la gestione
@ui_bp.route('/admin/cms/interface/')
@ui_bp.route('/admin/cms/interface/render')
def render_interface():
    username = check_user_authentication()
    if isinstance(username, str):
        return render_template('admin/cms/interface/render.html', title='CMS Interface', username=username)
    return username  

# Rotta per la homepage del CMS
@ui_bp.route('/admin/cms/pages/homepage')
def homepage():
    username = check_user_authentication()
    print(f"Session in homepage: {session}")
    if isinstance(username, str):
        return render_template('admin/cms/pages/home.html', title='HomePage', username=username)
    return username