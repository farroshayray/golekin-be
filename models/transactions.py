from . import db
from models.users import User
from models.products import Product
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    shipping_cost = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.Enum('withdrawal', 'transfer', 'deposit'), nullable=False)
    status = db.Column(db.Enum('cart', 'ordered', 'processed', 'completed'), nullable=False)
    description = db.Column(db.String(255))
    user_location = db.Column(db.String(255), nullable=True)
    driver_location = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    transaction_items = db.relationship('TransactionItems', backref='transaction', lazy=True)
    delivery = db.relationship('Delivery', backref='transaction', lazy=True)
    
    def to_dict(self):
        """Convert the Transaction instance into a dictionary."""
        # Fetch market/agent name
        market = User.query.filter_by(id=self.to_user_id, role="agen").first()
        market_name = market.fullname if market else "Unknown Market"

        # Fetch product details for each item
        items = []
        for item in self.transaction_items:
            product = Product.query.get(item.product_id)
            if product:
                items.append({
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": product.product_name,
                    "product_description": product.description,
                    "product_price": product.price,
                    "product_image_url": product.image_url,
                    "quantity": item.quantity,
                    "subtotal": item.subtotal,
                })

        return {
            "id": self.id,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "market_name": market_name,
            "total_amount": self.total_amount,
            "driver_id": self.driver_id,
            "type": self.type,
            "shipping_cost": self.shipping_cost,
            "status": self.status,
            "description": self.description,
            "user_location": self.user_location,
            "driver_location": self.driver_location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "items": items,
        }
    
    
class TransactionItems(db.Model):
    __tablename__ = 'transaction_items'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert the TransactionItems instance into a dictionary."""
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "subtotal": self.subtotal,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
class Delivery(db.Model):
    __tablename__ = 'deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'in_progress', 'delivered', 'failed'), nullable=False)
    pickup_location = db.Column(db.String(255), nullable=False)
    delivery_location = db.Column(db.String(255), nullable=False)
    estimated_time = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime, nullable=True)  # Waktu pengiriman selesai
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)