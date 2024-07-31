from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db, User, Role
from creators import RoleCreator, UserCreator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/CMS_DEF'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inizializza SQLAlchemy con l'app
db.init_app(app)

# Configura Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Includi le rotte
from routes import *

# Crea il database e i ruoli/utenti iniziali
with app.app_context():
    db.create_all()
    RoleCreator.create_roles()
    UserCreator.create_users()

if __name__ == '__main__':
    app.run(debug=True)