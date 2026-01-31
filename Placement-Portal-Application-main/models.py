from db import db
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

    job_positions = db.relationship("JobPosition", backref="company", lazy=True)



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



class JobPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    eligibility = db.Column(db.String(200))
    deadline = db.Column(db.Date)
    
    skills = db.Column(db.String(200))
    experience = db.Column(db.String(50))
    salary = db.Column(db.String(50))

    status = db.Column(db.String(20), default="Pending")
    # Pending / Approved / Closed

    applications = db.relationship("Application", backref="job_position", lazy=True)




class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    job_position_id = db.Column(db.Integer, db.ForeignKey("job_position.id"), nullable=False)

    status = db.Column(db.String(20), default="Applied")
    # Applied / Shortlisted / Selected / Rejected

    applied_on = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("student_id", "job_position_id", name="unique_application"),
    )
    
    placement = db.relationship("Placement", backref="application", uselist=False, lazy=True)



class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(db.Integer, db.ForeignKey("application.id"), nullable=False)
    
    # We can keep these for easy querying, but they are redundant if we have application_id
    # However, keeping them might be useful for analytics or simple joins. 
    # Let's keep them as per the user's implicit request for "Student-Application, Application-Placement" flow
    # but strictly speaking, application already links to student and job_position (which links to company).
    # To avoid data inconsistency, ideally we should just use application_id.
    # But the prompt asked for "Create models/tables... Define relationships".
    # I will rely on application_id for the core link.
    
    placed_on = db.Column(db.DateTime, default=datetime.utcnow)



