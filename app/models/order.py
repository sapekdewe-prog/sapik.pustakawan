from datetime import datetime
from app.extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    # Rincian Biaya
    item_price = db.Column(db.Integer, nullable=False)
    delivery_fee = db.Column(db.Integer, default=0, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)

    # Logistik / Jasa Antar
    delivery_method = db.Column(db.String(50),
                                default="delivery")  # "pickup" (ambil sendiri) atau "seller_delivery" (jasa antar)
    shipping_address = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Status Pemesanan
    status = db.Column(db.String(30), default="pending", nullable=False)
    # Status flow: "pending" -> "confirmed" -> "in_delivery" -> "completed" / "cancelled"

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship("Product", backref="order_entries")