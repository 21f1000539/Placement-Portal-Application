import unittest
from app import create_app, db
from models import Company, JobPosition, Application, Student, Admin
from datetime import date

class CompanyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            
            # Setup Data
            self.admin = Admin(username="admin", password="123")
            db.session.add(self.admin)
            
            self.company = Company(name="TechCorp", email="hr@tech.com", password="123", is_approved=True)
            db.session.add(self.company)
            
            self.student = Student(name="John", email="john@doe.com", password="123", department="CS")
            db.session.add(self.student)
            
            db.session.commit()

    def test_post_job(self):
        with self.client:
            # Login
            self.client.post("/login/company", data={"email": "hr@tech.com", "password": "123"})
            
            # Post Job
            resp = self.client.post("/company/post_job", data={
                "title": "SDE",
                "description": "Code",
                "eligibility": "B.Tech",
                "deadline": "2025-12-31",
                "skills": "Python",
                "experience": "Fresher",
                "salary": "10 LPA"
            }, follow_redirects=True)
            
            self.assertIn(b"Job posted successfully", resp.data)
            
            with self.app.app_context():
                job = JobPosition.query.first()
                self.assertIsNotNone(job)
                self.assertEqual(job.title, "SDE")
                self.assertEqual(job.status, "Pending")
                self.assertEqual(job.skills, "Python")

    def test_application_workflow(self):
        # 1. Post Job (Company)
        with self.client:
            self.client.post("/login/company", data={"email": "hr@tech.com", "password": "123"})
            self.client.post("/company/post_job", data={
                "title": "SDE", "description": "Code", "eligibility": "B.Tech", 
                "deadline": "2025-12-31", "skills": "Python", "experience": "0", "salary": "10"
            })
        
        # 2. Approve Job (Admin) - Need to approve for Student to apply? 
        # Student sees active jobs? 
        # (Assuming Student Apply logic lists 'Approved' jobs - logic unimplemented in Student milestone yet, but let's assume we test direct application creation or just logic we built now)
        # Actually, Student milestone is NEXT.
        # But we need to test COMPANY managing applications.
        # So we can manually create an application in DB.
        
        with self.app.app_context():
            job = JobPosition.query.first()
            job.status = "Approved" # Admin approves
            
            student = Student.query.first()
            app = Application(student_id=student.id, job_position_id=job.id)
            db.session.add(app)
            db.session.commit()
            app_id = app.id
            
        # 3. Company Views Application
        with self.client:
            self.client.post("/login/company", data={"email": "hr@tech.com", "password": "123"})
            resp = self.client.get("/company/applications")
            self.assertIn(b"John", resp.data) # Student Name
            
            # 4. Shortlist
            self.client.get(f"/application/{app_id}/update_status/Shortlisted", follow_redirects=True)
            
            with self.app.app_context():
                 a = Application.query.get(app_id)
                 self.assertEqual(a.status, "Shortlisted")

if __name__ == "__main__":
    unittest.main()
