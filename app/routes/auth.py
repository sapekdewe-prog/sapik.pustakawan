from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("marketplace.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        role = request.form.get("role", "buyer")
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not email or not password:
            flash("Nama, email, dan password wajib diisi.", "danger")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Email sudah terdaftar. Gunakan email lain.", "danger")
            return render_template("auth/register.html")

        # Buat user baru
        new_user = User(
            name=name,
            email=email,
            role=role if role in ["buyer", "seller"] else "buyer",
            phone=phone,
            address=address
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Pendaftaran berhasil! Silakan masuk ke akun Anda.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("marketplace.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Selamat datang kembali, {user.name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("marketplace.index"))
        else:
            flash("Email atau kata sandi tidak valid.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Anda telah berhasil keluar.", "info")
    return redirect(url_for("auth.login"))
# Halaman Lihat & Edit Profil
@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not name:
            flash("Nama lengkap tidak boleh kosong.", "danger")
            return render_template("auth/profile.html")

        current_user.name = name
        current_user.phone = phone
        current_user.address = address
        db.session.commit()

        flash("Profil Anda berhasil diperbarui!", "success")
        return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html")