from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from decimal import Decimal

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    fullname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    pin_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0.0)
    phone_number = db.Column(db.String(100), nullable=False)
    agen_id = db.Column(db.Integer, nullable=True)  # Agen ID di sini, bisa null jika tidak pedagang/driver
    location = db.Column(db.String(255), nullable=True)
    role = db.Column(db.Enum('konsumen', 'pedagang', 'agen', 'driver'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_pin(self, pin):
        self.pin_hash = generate_password_hash(pin)

    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, pin)

    # untuk cek role dn validasi agen_id
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.role in ['pedagang', 'driver'] and self.agen_id is None:
            raise ValueError("Agen ID must be provided for 'pedagang' or 'driver' roles.")
        elif self.role not in ['pedagang', 'driver'] and self.agen_id is not None:
            raise ValueError("Agen ID should not be provided for non 'pedagang' or 'driver' roles.")
