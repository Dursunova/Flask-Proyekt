from extensions import *
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    parent = db.relationship('Category', remote_side=[id], backref=db.backref('children', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return f'Category {self.title}'

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    discounted_price = db.Column(db.Float)
    category_id = db.Column(db.Integer,db.ForeignKey('category.id'),nullable=False)
    category = db.relationship("Category", backref="products")
    
    favorites = db.relationship('Favorite', back_populates='product')
    reviews = db.relationship('Review', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product{self.name}>'
    
    
class User(db.Model,UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    favorites = db.relationship('Favorite', back_populates='user')
    
    def __repr__(self):
        return f'<User {self.name}>' 
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    # # Şifrənin hash edilməsi üçün funksiya
    # def set_password(self, password):
    #     self.password = generate_password_hash(password)

    # # Şifrəni yoxlamaq üçün funksiya
    # def check_password(self, password):
    #     return check_password_hash(self.password, password)
    
    # Şifrəni təyin edən funksiya
    def set_password(self, password):
        self.password = password 
    # Şifrəni yoxlayan funksiya
    def check_password(self, password):
        return self.password == password  
        
    
    
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref='reviews', lazy=True)

    def __repr__(self):
        return f'<Review {self.content[:20]}...>'
    
    
class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    # Define relationships
    user = db.relationship('User', back_populates='favorites')
    product = db.relationship('Product', back_populates='favorites')

    # def __repr__(self):
    #     return f'<Favorite User: {self.user.name}, Product: {self.product.name}>'
    
    
    


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)