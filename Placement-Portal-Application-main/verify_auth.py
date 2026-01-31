import unittest
from app import create_app, db
from models import Student, Company, Admin
from werkzeug.security import generate_password_hash

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create Admin
            admin = Admin(username="admin", password="admin123")
            db.session.add(admin)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_student_register_login(self):
        try:
            # Register
            response = self.client.post("/register/student", data={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password",
                "department": "CS",
                "cgpa": "9.0",
                "resume": "link"
            }, follow_redirects=True)
            if b"Registration successful" not in response.data:
                print("Student Register Failed Response:", response.data)
            self.assertIn(b"Registration successful", response.data)

            # Login
            response = self.client.post("/login/student", data={
                "email": "john@example.com",
                "password": "password"
            }, follow_redirects=True)
            if b"Student Dashboard" not in response.data:
                print("Student Login Failed Response:", response.data)
            self.assertIn(b"Student Dashboard", response.data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e

    def test_company_register_approve_login(self):
        try:
            # Register
            response = self.client.post("/register/company", data={
                "name": "Tech Corp",
                "email": "hr@tech.com",
                "password": "password",
                "website": "tech.com",
                "hr_contact": "1234567890"
            }, follow_redirects=True)
            self.assertIn(b"Registration submitted", response.data)

            # Login before approval (Should fail/redirect)
            response = self.client.post("/login/company", data={
                "email": "hr@tech.com",
                "password": "password"
            }, follow_redirects=True)
            self.assertIn(b"Company not approved", response.data)

            # Admin Login
            response = self.client.post("/login/admin", data={
                "username": "admin",
                "password": "admin123"
            }, follow_redirects=True)
            self.assertIn(b"Admin Dashboard", response.data)
            self.assertIn(b"Tech Corp", response.data) # Should see pending company

            # Approve Company (Fetch company ID first)
            with self.app.app_context():
                company = Company.query.filter_by(email="hr@tech.com").first()
                if not company:
                    print("Company not found in DB")
                company_id = company.id
            
            response = self.client.get(f"/admin/approve/{company_id}", follow_redirects=True)
            self.assertIn(b"approved!", response.data)

            # Company Login after approval
            response = self.client.post("/login/company", data={
                "email": "hr@tech.com",
                "password": "password"
            }, follow_redirects=True)
            self.assertIn(b"Company Dashboard", response.data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e

if __name__ == "__main__":
    unittest.main()
