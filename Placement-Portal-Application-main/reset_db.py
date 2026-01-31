from app import create_app, db

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database reset successfully with new schema.")
    
    # Create Admin for testing
    from models import Admin
    db.session.add(Admin(username="admin", password="123"))
    db.session.commit()
    print("Admin created: admin/123")
