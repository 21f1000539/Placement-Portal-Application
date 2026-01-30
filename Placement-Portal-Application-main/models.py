from app import db
from datetime import datetime

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    website = db.Column(db.String(200))
    hr_contact = db.Column(db.String(20))

    is_approved = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    job_drives = db.relationship("JobDrive", backref="company", lazy=True)



class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    department = db.Column(db.String(50))
    cgpa = db.Column(db.Float)
    resume = db.Column(db.String(200))

    is_active = db.Column(db.Boolean, default=True)

    applications = db.relationship("Application", backref="student", lazy=True)



class JobDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    eligibility = db.Column(db.String(200))
    deadline = db.Column(db.Date)

    status = db.Column(db.String(20), default="Pending")
    # Pending / Approved / Closed

    applications = db.relationship("Application", backref="job_drive", lazy=True)




class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    job_drive_id = db.Column(db.Integer, db.ForeignKey("job_drive.id"), nullable=False)

    status = db.Column(db.String(20), default="Applied")
    # Applied / Shortlisted / Selected / Rejected

    applied_on = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("student_id", "job_drive_id", name="unique_application"),
    )



class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    job_title = db.Column(db.String(100))

    placed_on = db.Column(db.DateTime, default=datetime.utcnow)


