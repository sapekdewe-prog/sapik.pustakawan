from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.product import Product
from app.models.order import Order

order_bp = Blueprint("order", __name__)

# Halaman Checkout & Pemesanan Barang
@order_bp.route("/checkout/<int:product_id>", methods=["GET", "POST"])
@login_required
def checkout(product_id):
    product = Product.query.get_or_404(product_id)

    # Validasi: Tidak boleh membeli barang sendiri atau barang yang sudah laku
    if product.seller_id == current_user.id:
        flash("Anda tidak dapat membeli barang milik sendiri.", "danger")
        return redirect(url_for("marketplace.product_detail", product_id=product.id))

    if product.is_sold:
        flash("Maaf, barang ini sudah terjual.", "danger")
        return redirect(url_for("marketplace.index"))

    if request.method == "POST":
        delivery_method = request.form.get("delivery_method", "seller_delivery")
        shipping_address = request.form.get("shipping_address", "").strip()
        notes = request.form.get("notes", "").strip()

        # Hitung ongkir dan total biaya
        delivery_fee = product.delivery_fee if (delivery_method == "seller_delivery" and product.offers_delivery) else 0
        total_price = product.price + delivery_fee

        if delivery_method == "seller_delivery" and not shipping_address:
            flash("Alamat tujuan wajib diisi jika memilih opsi Jasa Antar.", "danger")
            return render_template("order/checkout.html", product=product)

        # Buat pesanan baru
        order = Order(
            buyer_id=current_user.id,
            seller_id=product.seller_id,
            product_id=product.id,
            item_price=product.price,
            delivery_fee=delivery_fee,
            total_price=total_price,
            delivery_method=delivery_method,
            shipping_address=shipping_address if delivery_method == "seller_delivery" else "Ambil Sendiri di Tempat Penjual",
            notes=notes,
            status="pending"
        )

        # Tandai barang sudah dibeli/dipesan
        product.is_sold = True

        db.session.add(order)
        db.session.commit()

        flash("Pesanan berhasil dibuat! Penjual akan segera memproses pengantaran.", "success")
        return redirect(url_for("order.my_orders"))

    return render_template("order/checkout.html", product=product)


# Riwayat Pesanan Pembeli
@order_bp.route("/my-orders")
@login_required
def my_orders():
    orders = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("order/my_orders.html", orders=orders)


# Daftar Pesanan Masuk untuk Penjual (Jasa Antar)
@order_bp.route("/seller-orders")
@login_required
def seller_orders():
    if not current_user.is_seller:
        flash("Akses ditolak.", "danger")
        return redirect(url_for("marketplace.index"))

    orders = Order.query.filter_by(seller_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("order/seller_orders.html", orders=orders)


# Update Status Pesanan & Kurir oleh Penjual
@order_bp.route("/order/<int:order_id>/update-status", methods=["POST"])
@login_required
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    if order.seller_id != current_user.id:
        abort(403)

    new_status = request.form.get("status")
    if new_status in ["confirmed", "in_delivery", "completed", "cancelled"]:
        order.status = new_status
        db.session.commit()
        flash("Status pesanan dan pengantaran berhasil diperbarui.", "success")

    return redirect(url_for("order.seller_orders"))
from app.models.review import Review  # Pastikan di-import di bagian atas file

@order_bp.route("/order/<int:order_id>/review", methods=["POST"])
@login_required
def submit_review(order_id):
    order = Order.query.get_or_404(order_id)

    # Validasi: Hanya pembeli yang boleh memberi ulasan & pesanan harus sudah 'completed'
    if order.buyer_id != current_user.id:
        abort(403)

    if order.status != "completed":
        flash("Ulasan hanya dapat diberikan setelah pesanan berstatus Selesai.", "danger")
        return redirect(url_for("order.my_orders"))

    if order.review:
        flash("Anda sudah memberikan ulasan untuk pesanan ini.", "info")
        return redirect(url_for("order.my_orders"))

    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment", "").strip()

    if not rating or rating < 1 or rating > 5:
        flash("Rating wajib diisi antara bintang 1 sampai 5.", "danger")
        return redirect(url_for("order.my_orders"))

    new_review = Review(
        order_id=order.id,
        product_id=order.product_id,
        buyer_id=current_user.id,
        seller_id=order.seller_id,
        rating=rating,
        comment=comment
    )

    db.session.add(new_review)
    db.session.commit()

    flash("Terima kasih! Ulasan Anda berhasil disimpan.", "success")
    return redirect(url_for("order.my_orders"))