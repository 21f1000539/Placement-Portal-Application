from app import create_app
from db import db
from models import Admin

app = create_app()

with app.app_context():
    db.create_all()

    admin = Admin.query.filter_by(username="admin").first()
    from werkzeug.security import generate_password_hash
    if not admin:
        admin = Admin(
            username="admin",
            password=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()

    print("Database initialized successfully.")
