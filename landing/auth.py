from flask import Blueprint, request, session, jsonify, redirect, url_for
from werkzeug.security import check_password_hash
from models.database import db
from models.user import User
import logging
from flask import current_app
from authlib.integrations.flask_client import OAuth
from config import Config
import os
import jwt
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    oauth.register(
        name='facebook',
        client_id=app.config['FACEBOOK_CLIENT_ID'],
        client_secret=app.config['FACEBOOK_CLIENT_SECRET'],
        access_token_url='https://graph.facebook.com/v10.0/oauth/access_token',
        authorize_url='https://www.facebook.com/v10.0/dialog/oauth',
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'email'}
    )
    oauth.register(
        name='apple',
        client_id=app.config['APPLE_CLIENT_ID'],
        client_secret=app.config['APPLE_CLIENT_SECRET'],
        access_token_url='https://appleid.apple.com/auth/token',
        authorize_url='https://appleid.apple.com/auth/authorize',
        api_base_url='https://appleid.apple.com/',
        client_kwargs={'scope': 'name email'}
    )

@auth_bp.route('/login', methods=['POST'])
def login():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return jsonify(success=False, message="Email e password obbligatorie."), 400

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.nome
            session['user_avatar'] = user.profilo_foto
            logging.info(f"✅ Login effettuato per {user.email}")
            return jsonify(success=True, message="Login effettuato!", redirect='/dashboard')
        else:
            logging.warning(f"❌ Tentativo di login fallito per {email}")
            return jsonify(success=False, message="Email o password non validi."), 401
    else:
        return redirect(url_for('landing.home'))

@auth_bp.route('/login/google')
def login_google():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/login/google/callback')
def google_callback():
    token = oauth.google.authorize_access_token()
    resp = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo')
    user_info = resp.json()

    if not user_info or 'email' not in user_info:
        return jsonify(success=False, message="Errore durante il login con Google"), 400

    user = User.query.filter_by(email=user_info['email']).first()

    if not user:
        user = User(
            email=user_info['email'],
            password='',
            nome=user_info.get('given_name', 'GoogleUser'),
            cognome=user_info.get('family_name', ''),
            telefono=None,
            profilo_foto=user_info.get('picture', None),
            is_2fa_enabled=False,
            otp_secret=None
        )
        db.session.add(user)
        db.session.commit()

    session['user_id'] = user.id
    session['user_email'] = user.email
    session['user_name'] = user.nome
    session['user_avatar'] = user.profilo_foto 

    return redirect('/dashboard')

@auth_bp.route('/login/facebook')
def login_facebook():
    redirect_uri = url_for('auth.facebook_callback', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)

@auth_bp.route('/login/facebook/callback')
def facebook_callback():
    token = oauth.facebook.authorize_access_token()
    resp = oauth.facebook.get('https://graph.facebook.com/me?fields=id,name,email,picture')
    user_info = resp.json()

    if not user_info or 'email' not in user_info:
        return jsonify(success=False, message="Errore durante il login con Facebook"), 400

    user = User.query.filter_by(email=user_info['email']).first()

    if not user:
        nome, *cognome = user_info.get('name', 'FacebookUser').split(' ')
        user = User(
            email=user_info['email'],
            password='',
            nome=nome,
            cognome=' '.join(cognome),
            telefono=None,
            profilo_foto=user_info.get('picture', {}).get('data', {}).get('url'),
            is_2fa_enabled=False,
            otp_secret=None
        )
        db.session.add(user)
        db.session.commit()

    session['user_id'] = user.id
    session['user_email'] = user.email
    session['user_name'] = user.nome
    session['user_avatar'] = user.profilo_foto

    return redirect('/dashboard')

@auth_bp.route('/login/apple')
def login_apple():
    redirect_uri = url_for('auth.apple_callback', _external=True)
    return oauth.apple.authorize_redirect(redirect_uri)

@auth_bp.route('/login/apple/callback')
def apple_callback():
    token = oauth.apple.authorize_access_token()
    resp = oauth.apple.get('https://appleid.apple.com/auth/userinfo')
    user_info = resp.json()

    if not user_info or 'email' not in user_info:
        return jsonify(success=False, message="Errore durante il login con Apple"), 400

    user = User.query.filter_by(email=user_info['email']).first()

    if not user:
        user = User(
            email=user_info['email'],
            password='',
            nome=user_info.get('name', 'AppleUser'),
            cognome='',
            telefono=None,
            profilo_foto=None,
            is_2fa_enabled=False,
            otp_secret=None
        )
        db.session.add(user)
        db.session.commit()

    session['user_id'] = user.id
    session['user_email'] = user.email
    session['user_name'] = user.nome
    session['user_avatar'] = user.profilo_foto

    return redirect('/dashboard')

@auth_bp.route('/generate_token/<shop_name>')
def generate_token(shop_name):
    if 'user_id' not in session:
        return redirect(url_for('landing.login'))

    token = jwt.encode({
        'user_id': session['user_id'],
        'exp': datetime.utcnow() + timedelta(minutes=15)  # oppure ore/giorni
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    # ✅ Metodo consigliato
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == 'development':
        return redirect(f"http://{shop_name}.localhost:8080/admin/login?token={token}")
    else:
        return redirect(f"https://{shop_name}.yoursite-linkbay-cms.com/admin/login?token={token}")