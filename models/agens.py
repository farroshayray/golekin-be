from datetime import datetime
from . import db

class Agen(db.Model):
    __tablename__ = 'agens'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    is_open = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_open(self):
        self.is_open = True
        db.session.commit()

    def set_close(self):
        self.is_open = False
        db.session.commit()

