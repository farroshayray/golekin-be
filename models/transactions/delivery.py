from .. import db
from datetime import datetime

class Delivery(db.Model):
    __tablename__ = 'deliveries'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'in_progress', 'delivered', 'failed'), nullable=False)
    pickup_location = db.Column(db.String(255), nullable=False)
    delivery_location = db.Column(db.String(255), nullable=False)
    estimated_time = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime, nullable=True)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
