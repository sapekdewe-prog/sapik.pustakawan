from flask import Blueprint, render_template, request
from app.models.product import Product

marketplace_bp = Blueprint("marketplace", __name__)

@marketplace_bp.route("/")
def index():
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    delivery_only = request.args.get("delivery_only", "")

    # Ambil barang yang belum terjual
    products_query = Product.query.filter_by(is_sold=False)

    # Filter pencarian teks
    if query:
        products_query = products_query.filter(
            (Product.title.ilike(f"%{query}%")) | (Product.description.ilike(f"%{query}%"))
        )

    # Filter kategori
    if category:
        products_query = products_query.filter_by(category=category)

    # Filter barang yang menyediakan jasa antar
    if delivery_only == "1":
        products_query = products_query.filter_by(offers_delivery=True)

    products = products_query.order_by(Product.created_at.desc()).all()

    categories = ["Pakaian", "Elektronik", "Otomotif", "Hobi & Koleksi", "Furnitur", "Lainnya"]
    return render_template(
        "marketplace/index.html",
        products=products,
        categories=categories,
        current_category=category,
        query=query,
        delivery_only=delivery_only
    )

@marketplace_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("marketplace/detail.html", product=product)