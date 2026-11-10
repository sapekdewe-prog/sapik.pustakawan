from datetime import datetime
from app.extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)  # Disimpan dalam satuan Rupiah integer
    condition = db.Column(db.String(50), nullable=False)  # Contoh: "Seperti Baru (9.5/10)", "Bekas Normal (8/10)"
    category = db.Column(db.String(50), nullable=False, index=True)
    image_filename = db.Column(db.String(255), default="default_product.jpg")
    is_sold = db.Column(db.Boolean, default=False, nullable=False)

    # Fitur Pemasaran Jasa Antar
    offers_delivery = db.Column(db.Boolean, default=True, nullable=False)
    delivery_fee = db.Column(db.Integer, default=0, nullable=False)  # Ongkos kirim jika ditangani penjual

    created_at = db.Column(db.DateTime, default=datetime.utcnow)