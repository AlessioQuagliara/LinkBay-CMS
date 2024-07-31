from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/CMS_DEF'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role.name}')"

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    permissions = db.Column(db.String(200), nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f"Role('{self.name}', '{self.permissions}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RoleCreator:
    @staticmethod
    def create_roles():
        admin_role = Role(name='Admin', permissions='create,read,update,delete')
        user_role = Role(name='User', permissions='read')
        db.session.add(admin_role)
        db.session.add(user_role)
        db.session.commit()

class UserCreator:
    @staticmethod
    def create_users():
        admin = User(username='admin', email='admin@example.com', role_id=1)
        admin.set_password('admin_password')
        user = User(username='user', email='user@example.com', role_id=2)
        user.set_password('user_password')
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()

if __name__ == "__main__":
    db.create_all()
    RoleCreator.create_roles()
    UserCreator.create_users()
    app.run(debug=True)