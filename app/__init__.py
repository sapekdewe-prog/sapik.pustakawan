import os
import re
from flask import Flask
from config import Config
from app.extensions import db, login_manager
from app.models.user import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- CUSTOM JINJA FILTERS (PRODUCTION UTILS) ---
    @app.template_filter("rupiah")
    def format_rupiah(value):
        try:
            return f"Rp {int(value):,}".replace(",", ".")
        except (ValueError, TypeError):
            return "Rp 0"

    @app.template_filter("wa_link")
    def format_wa_link(phone, text=""):
        if not phone:
            return "#"
        # Bersihkan format nomor ke format internasional (62)
        cleaned = re.sub(r"\D", "", phone)
        if cleaned.startswith("0"):
            cleaned = "62" + cleaned[1:]
        elif not cleaned.startswith("62"):
            cleaned = "62" + cleaned
        return f"https://wa.me/{cleaned}?text={text}"

    # 1. Blueprint Otentikasi
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # 2. Blueprint Seller
    from app.routes.seller import seller_bp
    app.register_blueprint(seller_bp, url_prefix="/seller")

    # 3. Blueprint Marketplace
    from app.routes.marketplace import marketplace_bp
    app.register_blueprint(marketplace_bp)

    # 4. Blueprint Order & Jasa Antar
    from app.routes.order import order_bp
    app.register_blueprint(order_bp, url_prefix="/order")

    return app