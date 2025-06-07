from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from models.database import db
from models.user import User
from models.userstoreaccess import UserStoreAccess
from models.shoplist import ShopList
from werkzeug.security import generate_password_hash, check_password_hash
import logging, jwt
from config import Config

SECRET_KEY = Config.SECRET_KEY  # Segreto JWT per l'autenticazione sicura

# 📌 Blueprint per la gestione degli utenti
user_bp = Blueprint('user', __name__)

logging.basicConfig(level=logging.INFO)

# 🔹 **Middleware per controllare se l'utente è autenticato**
def check_user_authentication():
    if 'user_id' not in session:
        return None 
    return session.get('username')

# 🔹 **Rotta per la registrazione di un nuovo utente**
@user_bp.route('/admin/sign-in', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            surname = request.form.get('surname')
            email = request.form.get('email')
            password = request.form.get('password')

            # Verifica se l'utente esiste già
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already exists', 'danger')
                return redirect(url_for('user.signin'))

            # Creazione nuovo utente
            new_user = User(
                nome=name,
                cognome=surname,
                email=email,
                password=generate_password_hash(password, method='pbkdf2:sha256')
            )

            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('user.login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"❌ Error signing up user: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')

    return render_template('/admin/sign-in.html', title='LinkBayCMS - Sign-in')

# 🔹 **Middleware per il debug delle sessioni**
@user_bp.before_request
def log_session_info():
    try:
        logging.info(f"📌 Request path: {request.path}, Session: {session}")
    except Exception as e:
        logging.error(f"❌ Error logging session info: {e}")

# 🔹 **Rotta per il login**
@user_bp.route('/admin/', methods=['GET', 'POST'])
@user_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    token = request.args.get('token')

    if token:
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')

            if user_id:
                user = User.query.get(user_id)

                if user:
                    shop_name = request.host.split('.')[0]
                    shop = ShopList.query.filter_by(shop_name=shop_name).first()

                    if shop and UserStoreAccess.query.filter_by(user_id=user_id, shop_id=shop.id).first():
                        session.update({
                            'user_id': user.id,
                            'username': user.nome,
                            'surname': user.cognome,
                            'email': user.email,
                            'phone': user.telefono,
                            'profile_photo': user.profilo_foto,
                            'shop_id': shop.id
                        })
                        return redirect(url_for('ui.homepage'))
                    else:
                        flash('Access denied for this store.', 'danger')
                        return redirect(url_for('user.login'))

        except jwt.ExpiredSignatureError:
            flash('Session expired. Please log in again.', 'danger')
        except jwt.InvalidTokenError:
            flash('Invalid token.', 'danger')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            shop_name = request.host.split('.')[0]
            shop = ShopList.query.filter_by(shop_name=shop_name).first()

            if shop and UserStoreAccess.query.filter_by(user_id=user.id, shop_id=shop.id).first():
                session.update({
                    'user_id': user.id,
                    'username': user.nome,
                    'surname': user.cognome,
                    'email': user.email,
                    'phone': user.telefono,
                    'profile_photo': user.profilo_foto,
                    'shop_id': shop.id
                })
                return redirect(url_for('ui.homepage'))
            else:
                flash('Access denied for this store.', 'danger')
                return redirect(url_for('user.login'))
        else:
            flash('Invalid credentials.', 'danger')

    return render_template('admin/login.html', title='Login')

# 🔹 **Rotta per il logout**
@user_bp.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))

# 🔹 **Rotta per il ripristino della password**
@user_bp.route('/admin/restore')
def restore():
    return render_template('/admin/restore.html', title='LinkBayCMS - Restore')