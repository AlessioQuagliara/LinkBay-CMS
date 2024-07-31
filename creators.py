from models import db, Role, User

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