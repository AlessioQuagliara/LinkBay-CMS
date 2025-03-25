from flask import Blueprint

landing_bp = Blueprint('landing', __name__, template_folder='templates', static_folder='static')

from . import routes, auth, superadmin  # importa i file dentro landing