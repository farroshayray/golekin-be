from .. import db
from datetime import datetime
from models.users import User
from models.products import Product

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
