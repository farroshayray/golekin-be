from datetime import datetime
from . import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)  
    product_name = db.Column(db.String(255), nullable=False)  
    qty = db.Column(db.Integer, nullable=False, default=0)  
    description = db.Column(db.Text, nullable=True)  
    price = db.Column(db.Float, nullable=False)  
    stock = db.Column(db.Integer, nullable=False, default=0)  
    category_id = db.Column(db.Integer, nullable=False)  
    image_url = db.Column(db.String(500), nullable=True)  
    is_active = db.Column(db.Integer, nullable=False, default=1)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow) 

