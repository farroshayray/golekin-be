from datetime import datetime
from . import db
from models.users import User

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)  
    product_name = db.Column(db.String(255), nullable=False)   
    description = db.Column(db.Text, nullable=True)  
    price = db.Column(db.Float, nullable=False)  
    stock = db.Column(db.Integer, nullable=False, default=0)  
    image_url = db.Column(db.String(500), nullable=True)
    ordered_times = db.Column(db.Integer, nullable=True, default=0)
    rated_times = db.Column(db.Integer, nullable=True, default=0)
    sum_rated = db.Column(db.Integer, nullable=True, default=0)  
    is_active = db.Column(db.Integer, nullable=False, default=1)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow) 

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    category_name = db.Column(db.String(255), nullable=False, unique=True)  # Nama kategori
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)

    # Relationship to Product
    products = db.relationship('Product', backref='category', lazy=True)