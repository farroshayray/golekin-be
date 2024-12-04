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
    
    def to_dict(self):
        """Convert the Product instance into a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_name": self.product_name,
            "description": self.description,
            "price": float(self.price),  # Ensure floats are JSON serializable
            "stock": self.stock,
            "category_id": self.category_id,
            "image_url": self.image_url,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    category_name = db.Column(db.String(255), nullable=False, unique=True)  # Nama kategori
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)

    # Relationship to Product
    products = db.relationship('Product', backref='category', lazy=True)