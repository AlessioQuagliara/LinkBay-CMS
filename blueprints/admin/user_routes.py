from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from models.user import User # importo la classe database
from models.userstoreaccess import UserStoreAccess
from models.shoplist import ShopList
from werkzeug.security import generate_password_hash, check_password_hash
from db_helpers import DatabaseHelper
from helpers import check_user_authentication
import logging, jwt
from config import Config

SECRET_KEY = Config.SECRET_KEY  # Ora funziona correttamente

db_helper = DatabaseHelper()

# Blueprint
user_bp = Blueprint('user', __name__)

logging.basicConfig(level=logging.INFO)

# Rotte per la gestione

# Funzione per controllare se l'utente è autenticato -----------------------------------
def check_user_authentication():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    return session['username']

# Admin Routes -------------------------------------------------------------------------
@user_bp.route('/admin/sign-in', methods=['GET', 'POST'])
def signin():
    db_conn = db_helper.get_db_connection()  
    user_model = User(db_conn)  

    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        store_name = request.form.get('store_name')
        email = request.form.get('email')
        password = request.form.get('password')


        existing_user = user_model.get_user_by_email(email)
        if existing_user:
            flash('Email address already exists')
            return redirect(url_for('signin'))

        user_model.create_user(name, surname, email, password)
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('/admin/sign-in.html', title='LinkBay - Sign-in')

# Middleware per il debug delle sessioni
@user_bp.before_request
def log_session_info():
    try:
        logging.info(f"Request path: {request.path}")
    except Exception as e:
        logging.error(f"Errore durante il log: {e}")

# Funzione di login -------------------------------------------------
@user_bp.route('/admin/', methods=['GET', 'POST'])
@user_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    auth_db_conn = db_helper.get_auth_db_connection()  
    user_model = User(auth_db_conn)  
    access_model = UserStoreAccess(auth_db_conn)  
    shop_list_model = ShopList(auth_db_conn)

    # **1️⃣ Controlla se il Token è presente nella richiesta**
    token = request.args.get('token')

    if token:
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')

            if user_id:
                user = user_model.get_user_by_id(user_id)

                if user:
                    # **Verifica accesso allo store**
                    domain_parts = request.host.split('.')
                    subdomain_or_domain = domain_parts[0] if len(domain_parts) > 1 else request.host
                    shop = shop_list_model.get_shop_by_name_or_domain(subdomain_or_domain)

                    if shop and access_model.has_access(user_id, shop['id']):
                        session['user_id'] = user['id']
                        session['username'] = user['nome']
                        session['surname'] = user['cognome']
                        session['email'] = user['email']
                        session['phone'] = user['telefono']
                        session['profile_photo'] = user['profilo_foto']
                        session['shop_id'] = shop['id']

                        return redirect(url_for('ui.homepage'))
                    else:
                        flash('Accesso negato a questo store.', 'danger')
                        return redirect(url_for('user.login'))
        except jwt.ExpiredSignatureError:
            flash('Sessione scaduta. Effettua nuovamente il login.', 'danger')
        except jwt.InvalidTokenError:
            flash('Token non valido.', 'danger')

    # **2️⃣ Se non c'è token, gestisce il login classico con email e password**
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = user_model.get_user_by_email(email)

        if user and check_password_hash(user['password'], password):
            # **Verifica accesso allo store**
            domain_parts = request.host.split('.')
            subdomain_or_domain = domain_parts[0] if len(domain_parts) > 1 else request.host
            shop = shop_list_model.get_shop_by_name_or_domain(subdomain_or_domain)

            if shop and access_model.has_access(user['id'], shop['id']):
                session['user_id'] = user['id']
                session['username'] = user['nome']
                session['surname'] = user['cognome']
                session['email'] = user['email']
                session['phone'] = user['telefono']
                session['profile_photo'] = user['profilo_foto']
                session['shop_id'] = shop['id']

                return redirect(url_for('ui.homepage'))
            else:
                flash('Accesso negato a questo store.', 'danger')
                return redirect(url_for('user.login'))
        else:
            flash('Credenziali non valide.', 'danger')
            return redirect(url_for('user.login'))

    # **3️⃣ Se è solo GET, mostra la pagina di login**
    return render_template('admin/login.html', title='Login')

@user_bp.route('/admin/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return render_template('admin/logout.html', title='Logout')

@user_bp.route('/admin/restore')
def restore():
    return render_template('/admin/restore.html', title='LinkBay - Restore')


