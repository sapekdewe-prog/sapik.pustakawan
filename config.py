import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "prod-secret-key-change-me-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL") or f"sqlite:///{os.path.join(BASE_DIR, 'thrift_market.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Konfigurasi upload gambar produk
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Maksimal 5 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}