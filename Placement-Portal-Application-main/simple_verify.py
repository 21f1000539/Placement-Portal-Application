from app import create_app
from db import db
from models import Admin

app = create_app()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

with app.app_context():
    try:
        db.create_all()
        print("DB Created successfully")
        
        admin = Admin(username="testadmin", password="123")
        db.session.add(admin)
        db.session.commit()
        print("Admin added successfully")
    except Exception as e:
        import traceback
        traceback.print_exc()
