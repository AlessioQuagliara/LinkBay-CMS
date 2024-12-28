from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from models.user import User # importo la classe database
from models.userstoreaccess import UserStoreAccess
from models.shoplist import ShopList
from app import get_db_connection, get_auth_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

# Blueprint
user_bp = Blueprint('user', __name__)

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
    db_conn = get_db_connection()  
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
    print(f"Request path: {request.path}")
    print(f"Session data: {session}")
    print(f"Cookies: {request.cookies}")

# Funzione di login -------------------------------------------------
@user_bp.route('/admin/', methods=['GET', 'POST'])
@user_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    auth_db_conn = get_auth_db_connection()  
    user_model = User(auth_db_conn)  
    access_model = UserStoreAccess(auth_db_conn)  
    shop_list_model = ShopList(auth_db_conn)  # Modello per ottenere i dettagli dello store

    # Rileva il sottodominio o il dominio principale
    domain_parts = request.host.split('.')
    subdomain_or_domain = domain_parts[0] if len(domain_parts) > 1 else request.host

    # Ottieni lo shop basato su `shop_name` o `domain`
    shop = shop_list_model.get_shop_by_name_or_domain(subdomain_or_domain)

    if not shop:
        flash('Store not found for this domain or subdomain.', 'danger')
        return redirect(url_for('login'))

    shop_id = shop['id']  # Identifica lo store attuale per l'accesso
    shop_name = shop['shop_name']  # Per visualizzazione nel template

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = user_model.get_user_by_email(email)

        if user and check_password_hash(user['password'], password):
            # Verifica se l'utente ha accesso a questo specifico store
            if access_model.has_access(user['id'], shop_id):
                # Se ha accesso, imposta la sessione
                session['user_id'] = user['id']
                session['username'] = user['nome']
                session['surname'] = user['cognome']
                session['email'] = user['email']
                session['phone'] = user['telefono']
                session['profile_photo'] = user['profilo_foto']
                session['shop_id'] = shop_id  # Salva lo shop_id nella sessione

                print(f"Session after login: {session}")

                # Controllo per 2FA
                if user['is_2fa_enabled']:
                    session['otp_secret'] = user['otp_secret']
                    return redirect(url_for('verify_otp'))
                else:
                    return redirect(url_for('homepage'))
            else:
                # Se l'utente non ha accesso a questo store
                flash('Access denied for this store.', 'danger')
                return redirect(url_for('login'))
        else:
            # Se email o password non sono corretti
            flash('Login failed. Please check your email and password.', 'danger')
            return redirect(url_for('login'))

    # Passa shop_name al template per mostrare il nome dello store
    return render_template('admin/login.html', title='Login', shop_name=shop_name)

@user_bp.route('/admin/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return render_template('admin/logout.html', title='Logout')

@user_bp.route('/admin/restore')
def restore():
    return render_template('/admin/restore.html', title='LinkBay - Restore')


