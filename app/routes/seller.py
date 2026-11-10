import os
import io
import csv
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, Response, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.product import Product
from app.models.order import Order

seller_bp = Blueprint("seller", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Dashboard Etalase Barang Penjual
@seller_bp.route("/dashboard")
@login_required
def dashboard():
    if not current_user.is_seller:
        flash("Akses hanya untuk akun penjual.", "danger")
        return redirect(url_for("marketplace.index"))

    products = Product.query.filter_by(seller_id=current_user.id).order_by(Product.created_at.desc()).all()
    return render_template("seller/dashboard.html", products=products)


# Tambah Barang Bekas Baru
@seller_bp.route("/product/create", methods=["GET", "POST"])
@login_required
def create_product():
    if not current_user.is_seller:
        flash("Akses hanya untuk akun penjual.", "danger")
        return redirect(url_for("marketplace.index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        condition = request.form.get("condition", "").strip()
        price = request.form.get("price", type=int)
        description = request.form.get("description", "").strip()

        offers_delivery = "offers_delivery" in request.form
        delivery_fee = request.form.get("delivery_fee", 0, type=int) if offers_delivery else 0

        file = request.files.get("image")
        filename = "default.png"

        if file and file.filename != "" and allowed_file(file.filename):
            sec_filename = secure_filename(file.filename)
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{sec_filename}"
            upload_dir = current_app.config.get("UPLOAD_FOLDER", os.path.join("app", "static", "uploads"))
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, unique_filename))
            filename = unique_filename

        new_product = Product(
            seller_id=current_user.id,
            title=title,
            category=category,
            condition=condition,
            price=price,
            description=description,
            image_filename=filename,
            offers_delivery=offers_delivery,
            delivery_fee=delivery_fee
        )

        db.session.add(new_product)
        db.session.commit()

        flash("Barang bekas berhasil diposting ke etalase!", "success")
        return redirect(url_for("seller.dashboard"))

    return render_template("seller/product_form.html", action="Tambah", product=None)


# Hapus Barang
@seller_bp.route("/product/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.seller_id != current_user.id:
        abort(403)

    db.session.delete(product)
    db.session.commit()
    flash("Barang berhasil dihapus dari etalase.", "success")
    return redirect(url_for("seller.dashboard"))


# Halaman Ringkasan Laporan Penjualan & Jasa Antar
@seller_bp.route("/reports")
@login_required
def reports():
    if not current_user.is_seller:
        flash("Akses hanya untuk akun penjual.", "danger")
        return redirect(url_for("marketplace.index"))

    completed_orders = Order.query.filter_by(seller_id=current_user.id, status="completed").all()

    total_product_income = sum(o.item_price for o in completed_orders)
    total_delivery_income = sum(o.delivery_fee for o in completed_orders)
    grand_total = total_product_income + total_delivery_income

    return render_template(
        "seller/reports.html",
        orders=completed_orders,
        total_product_income=total_product_income,
        total_delivery_income=total_delivery_income,
        grand_total=grand_total
    )


# Ekspor Data Transaksi Selesai ke Format CSV (Excel)
@seller_bp.route("/reports/export-csv")
@login_required
def export_csv():
    if not current_user.is_seller:
        abort(403)

    completed_orders = Order.query.filter_by(seller_id=current_user.id, status="completed").order_by(
        Order.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header kolom CSV
    writer.writerow([
        "ID Pesanan",
        "Tanggal",
        "Nama Pembeli",
        "Nomor HP",
        "Nama Barang",
        "Metode Pengiriman",
        "Harga Barang (Rp)",
        "Ongkir Jasa Antar (Rp)",
        "Total Tagihan (Rp)",
        "Alamat Tujuan"
    ])

    for o in completed_orders:
        writer.writerow([
            f"#{o.id}",
            o.created_at.strftime("%d/%m/%Y %H:%M"),
            o.buyer.name,
            o.buyer.phone or "-",
            o.product.title,
            "Jasa Antar" if o.delivery_method == "seller_delivery" else "Ambil Sendiri",
            o.item_price,
            o.delivery_fee,
            o.total_price,
            o.shipping_address
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=Laporan_Penjualan_ThriftMarket.csv"}
    )