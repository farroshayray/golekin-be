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
    
    reviews = db.relationship('ProductReview', backref='product', lazy=True)  # Relasi ke ulasan
    
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
        
class ProductReview(db.Model):
    __tablename__ = 'product_reviews'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # Relasi ke produk
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Relasi ke pengguna
    review_text = db.Column(db.Text, nullable=True)  # Teks ulasan
    star_rating = db.Column(db.Integer, nullable=True)  # Penilaian bintang (1-5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Waktu ulasan dibuat
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)  # Waktu ulasan diubah

    def to_dict(self):
        """Convert the ProductReview instance into a dictionary."""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "review_text": self.review_text,
            "star_rating": self.star_rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    category_name = db.Column(db.String(255), nullable=False, unique=True)  # Nama kategori
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)

    # Relationship to Product
    products = db.relationship('Product', backref='category', lazy=True)
    
class Promotion(db.Model):
    __tablename__ = 'promotions'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=True)
    scheme = db.Column(db.Enum('discount', 'cashback', 'nominal'), nullable=True)
    scheme_percentage = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "transaction_id": self.transaction_id,
            "scheme": self.scheme,
            "scheme_percentage": self.scheme_percentage,
            "description": self.description,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }