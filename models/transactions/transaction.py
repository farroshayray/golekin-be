from .. import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
