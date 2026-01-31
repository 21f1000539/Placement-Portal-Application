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
    from flask import request, redirect, url_for, flash
    from db import db


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
        return render_template("dashboards/company.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
