from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="buyer", nullable=False)  # 'buyer', 'seller', 'admin'
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi
    products = db.relationship("Product", backref="seller", lazy="dynamic", cascade="all, delete-orphan")
    orders_placed = db.relationship("Order", foreign_keys="Order.buyer_id", backref="buyer", lazy="dynamic")
    orders_received = db.relationship("Order", foreign_keys="Order.seller_id", backref="seller", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_seller(self):
        return self.role in ["seller", "admin"]