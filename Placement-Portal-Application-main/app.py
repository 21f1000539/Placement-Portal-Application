from flask import Flask, render_template
from config import Config
from db import db   # 👈 import db from db.py

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from auth import auth_bp
    app.register_blueprint(auth_bp)

    from decorators import login_required

    from models import Company, Student, JobPosition, Application, Placement
    from flask import request, redirect, url_for, flash, session



    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/admin/dashboard")
    @login_required("admin")
    def admin_dashboard():
        # Stats
        stats = {
            "companies": Company.query.count(),
            "students": Student.query.count(),
            "jobs": JobPosition.query.count(),
            "applications": Application.query.count()
        }
        pending_companies = Company.query.filter_by(is_approved=False).all()
        return render_template("dashboards/admin.html", companies=pending_companies, stats=stats)

    # --- Company Management ---
    @app.route("/admin/manage/companies")
    @login_required("admin")
    def manage_companies():
        search = request.args.get("search", "")
        if search:
            companies = Company.query.filter(Company.name.ilike(f"%{search}%")).all()
        else:
            companies = Company.query.all()
        return render_template("admin/manage_companies.html", companies=companies)

    @app.route("/admin/approve_company_action/<int:company_id>/<action>")
    @login_required("admin")
    def approve_company_action(company_id, action):
        company = Company.query.get_or_404(company_id)
        if action == "approve":
            company.is_approved = True
            flash(f"{company.name} approved.")
        elif action == "reject":
            # Rejecting usually means deleting the registration request or keeping it unapproved?
            # Prompt says "Approve and Reject... registration". Rejection often implies deletion of the request.
            db.session.delete(company)
            flash(f"{company.name} rejected and removed.")
        elif action == "blacklist":
            company.is_blacklisted = True
            flash(f"{company.name} blacklisted.")
        elif action == "whitelist":
            company.is_blacklisted = False
            flash(f"{company.name} removed from blacklist.")
        
        db.session.commit()
        return redirect(request.referrer or url_for("manage_companies"))

    # Only keeping this for backward compatibility if needed, but redundant with above
    @app.route("/admin/approve/<int:company_id>")
    @login_required("admin")
    def approve_company(company_id):
        return approve_company_action(company_id, "approve")


    # --- Student Management ---
    @app.route("/admin/manage/students")
    @login_required("admin")
    def manage_students():
        search = request.args.get("search", "")
        if search:
            # Search by name or email
            students = Student.query.filter(
                (Student.name.ilike(f"%{search}%")) | (Student.email.ilike(f"%{search}%"))
            ).all()
        else:
            students = Student.query.all()
        return render_template("admin/manage_students.html", students=students)

    @app.route("/admin/student_action/<int:student_id>/<action>")
    @login_required("admin")
    def student_action(student_id, action):
        student = Student.query.get_or_404(student_id)
        if action == "deactivate":
            student.is_active = False
            flash(f"{student.name} deactivated.")
        elif action == "activate":
            student.is_active = True
            flash(f"{student.name} activated.")
        db.session.commit()
        return redirect(url_for("manage_students"))


    # --- Job Management ---
    @app.route("/admin/manage/jobs")
    @login_required("admin")
    def manage_jobs():
        jobs = JobPosition.query.all()
        return render_template("admin/manage_jobs.html", jobs=jobs)

    @app.route("/admin/job_action/<int:job_id>/<action>")
    @login_required("admin")
    def job_action(job_id, action):
        job = JobPosition.query.get_or_404(job_id)
        if action == "approve":
            job.status = "Approved"
        elif action == "reject":
            job.status = "Rejected"
        db.session.commit()
        return redirect(url_for("manage_jobs"))


    # --- Application View ---
    @app.route("/admin/view/applications")
    @login_required("admin")
    def view_applications():
        applications = Application.query.all()
        return render_template("admin/view_applications.html", applications=applications)


    @app.route("/student/dashboard")
    @login_required("student")
    def student_dashboard():
        return render_template("dashboards/student.html")

    @app.route("/company/dashboard")
    @login_required("company")
    def company_dashboard():
        company_id = session.get("user_id")
        company = Company.query.get(company_id)
        if not company.is_approved:
             return render_template("unauthorized.html", message="Your account is awaiting admin approval.")
        
        jobs = JobPosition.query.filter_by(company_id=company_id).all()
        # Count total applications received
        total_applications = 0
        for job in jobs:
            total_applications += len(job.applications)
            
        return render_template("dashboards/company.html", company=company, jobs=jobs, total_applications=total_applications)

    @app.route("/company/post_job", methods=["GET", "POST"])
    @login_required("company")
    def post_job():
        if request.method == "POST":
            company_id = session.get("user_id")
            title = request.form["title"]
            description = request.form["description"]
            eligibility = request.form["eligibility"]
            deadline_str = request.form["deadline"]
            skills = request.form["skills"]
            experience = request.form["experience"]
            salary = request.form["salary"]
            
            from datetime import datetime
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            
            job = JobPosition(
                company_id=company_id,
                title=title,
                description=description,
                eligibility=eligibility,
                deadline=deadline,
                skills=skills,
                experience=experience,
                salary=salary,
                status="Pending" 
                # Let's verify status default in model. Model default is 'Pending'. 
                # Does admin need to approve jobs? "Approve and Reject job postings... created by companies." -> YES.
                # So default should be 'Pending' or 'Active'? 
                # If Admin has to approve, it should probably be 'Pending'. 
                # But User Prompt also says "Update job posting status (Active/Closed)".
                # Let's keep default as 'Pending' (from model) for Admin workflow, but allow Company to close it later?
                # Actually, "Approve and Reject job postings" implies Admin control.
                # So newly created job is 'Pending'.
                # Once approved, it becomes 'Approved' (or 'Active'?). 
                # Model default is 'Pending'.
                # I will let it be 'Pending'.
            )
            db.session.add(job)
            db.session.commit()
            flash("Job posted successfully! Waiting for Admin approval.")
            return redirect(url_for("company_dashboard"))
            
        return render_template("company/post_job.html")

    @app.route("/company/update_job_status/<int:job_id>/<status>")
    @login_required("company")
    def update_job_status(job_id, status):
        job = JobPosition.query.get_or_404(job_id)
        # Ensure company owns this job
        if job.company_id != session.get("user_id"):
             flash("Unauthorized action.")
             return redirect(url_for("company_dashboard"))
        
        # Valid statuses for company to toggle? Active/Closed.
        # But system uses Pending/Approved/Rejected.
        # Maybe 'Closed' is a state company can set.
        if status in ["Closed", "Active"]: # If approved, they can close/re-open? Or just Close?
             # Assuming 'Approved' acts as 'Active'. 
             # Let's just update based on request if valid
             job.status = status
             db.session.commit()
             flash(f"Job status updated to {status}.")
        
        return redirect(url_for("company_dashboard"))

    @app.route("/company/applications")
    @login_required("company")
    def company_applications():
        company_id = session.get("user_id")
        jobs = JobPosition.query.filter_by(company_id=company_id).all()
        return render_template("company/view_applications.html", jobs=jobs)

    @app.route("/application/<int:app_id>/update_status/<status>")
    @login_required("company")
    def update_application_status(app_id, status):
        application = Application.query.get_or_404(app_id)
        # Verify ownership
        if application.job_position.company_id != session.get("user_id"):
            flash("Unauthorized.")
            return redirect(url_for("company_dashboard"))

        if status in ["Shortlisted", "Selected", "Rejected"]:
            application.status = status
            db.session.commit()
            flash(f"Application status updated to {status}")
        
        # Determine redirect back
        return redirect(request.referrer or url_for("company_applications"))

    @app.route("/student/profile/<int:student_id>")
    @login_required("company")
    def student_profile(student_id):
        student = Student.query.get_or_404(student_id)
        return render_template("company/student_profile.html", student=student)


    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
