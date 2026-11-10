import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager
from app.models.user import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Pastikan folder uploads tersedia
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Inisialisasi Ekstensi
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Placeholder registrasi blueprint (akan diisi di tahap selanjutnya)
    # from app.routes.auth import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')

    return app