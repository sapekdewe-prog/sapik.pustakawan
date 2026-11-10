from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.review import Review

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Inisialisasi tabel SQLite."""
    with app.app_context():
        db.create_all()
        print("-> Database SQLite berhasil diinisialisasi beserta tabel-tabelnya.")

if __name__ == "__main__":
    app.run(debug=True, port=5000)