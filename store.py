from models import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}')"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Order('{self.id}', '{self.user_id}', '{self.total_price}', '{self.status}')"

class StoreManager:
    @staticmethod
    def add_product(name, description, price, stock):
        product = Product(name=name, description=description, price=price, stock=stock)
        db.session.add(product)
        db.session.commit()

    @staticmethod
    def get_product(product_id):
        return Product.query.get(product_id)

    @staticmethod
    def update_product(product_id, **kwargs):
        product = Product.query.get(product_id)
        for key, value in kwargs.items():
            setattr(product, key, value)
        db.session.commit()

    @staticmethod
    def delete_product(product_id):
        product = Product.query.get(product_id)
        db.session.delete(product)
        db.session.commit()

    @staticmethod
    def create_order(user_id, total_price, status='pending'):
        order = Order(user_id=user_id, total_price=total_price, status=status)
        db.session.add(order)
        db.session.commit()