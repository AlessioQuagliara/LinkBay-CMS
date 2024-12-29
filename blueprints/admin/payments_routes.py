from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect
from models.payments import Payments # importo la classe database
from db_helpers import DatabaseHelper
from helpers import check_user_authentication

db_helper = DatabaseHelper()

# Blueprint
payments_bp = Blueprint('payments', __name__)

# Rotte per la gestione

@payments_bp.route('/admin/cms/pages/payments', methods=['GET'])
def payments():
    """
    Mostra la lista dei metodi di pagmanto disponibili.
    """
    return render_template('admin/cms/pages/payments.html', title='Payments')