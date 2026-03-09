from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from db import db
from models import Company, Student, JobPosition, Application, Placement
from decorators import login_required
import os
from datetime import datetime, date


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads/resumes')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    from auth import auth_bp
    app.register_blueprint(auth_bp)

    # ---------------- HOME ----------------

    @app.route("/")
    def index():
        return render_template("index.html")

    # ---------------- ADMIN ----------------

    @app.route("/admin/dashboard")
    @login_required("admin")
    def admin_dashboard():

        stats = {
            "companies": Company.query.count(),
            "students": Student.query.count(),
            "jobs": JobPosition.query.count(),
            "applications": Application.query.count()
        }

        pending_companies = Company.query.filter_by(is_approved=False).all()
        jobs = JobPosition.query.order_by(JobPosition.posted_date.desc()).limit(5).all()

        return render_template(
            "dashboards/admin.html",
            companies=pending_companies,
            stats=stats,
            jobs=jobs
        )

    # ---------------- COMPANY MANAGEMENT ----------------

    @app.route("/admin/manage/companies")
    @login_required("admin")
    def manage_companies():

        search = request.args.get("search", "")

        if search:
            companies = Company.query.filter(
                Company.name.ilike(f"%{search}%")
            ).all()
        else:
            companies = Company.query.all()

        return render_template(
            "admin/manage_companies.html",
            companies=companies
        )

    @app.route("/admin/approve_company_action/<int:company_id>/<action>")
    @login_required("admin")
    def approve_company_action(company_id, action):

        company = Company.query.get_or_404(company_id)

        if action == "approve":
            company.is_approved = True

        elif action == "reject":
            db.session.delete(company)

        elif action == "blacklist":
            company.is_blacklisted = True

        elif action == "whitelist":
            company.is_blacklisted = False

        db.session.commit()

        return redirect(request.referrer or url_for("manage_companies"))

    @app.route("/admin/approve/<int:company_id>")
    @login_required("admin")
    def approve_company(company_id):
        return approve_company_action(company_id, "approve")

    # ---------------- STUDENT MANAGEMENT ----------------

    @app.route("/admin/manage/students")
    @login_required("admin")
    def manage_students():

        search = request.args.get("search", "")

        if search:
            students = Student.query.filter(
                (Student.name.ilike(f"%{search}%")) |
                (Student.email.ilike(f"%{search}%"))
            ).all()
        else:
            students = Student.query.all()

        return render_template(
            "admin/manage_students.html",
            students=students
        )

    @app.route("/admin/student_action/<int:student_id>/<action>")
    @login_required("admin")
    def student_action(student_id, action):

        student = Student.query.get_or_404(student_id)

        if action == "deactivate":
            student.is_active = False

        elif action == "activate":
            student.is_active = True

        db.session.commit()

        return redirect(url_for("manage_students"))

    # ---------------- JOB MANAGEMENT ----------------

    @app.route("/admin/manage/jobs")
    @login_required("admin")
    def manage_jobs():

        jobs = JobPosition.query.all()

        return render_template(
            "admin/manage_jobs.html",
            jobs=jobs
        )

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

    # ---------------- APPLICATIONS ----------------

    @app.route("/admin/view/applications")
    @login_required("admin")
    def view_applications():

        applications = Application.query.all()

        return render_template(
            "admin/view_applications.html",
            applications=applications
        )

    @app.route("/admin/job/<int:job_id>")
    @login_required("admin")
    def view_job_details(job_id):

        job = JobPosition.query.get_or_404(job_id)
        applications = Application.query.filter_by(job_position_id=job_id).all()

        return render_template(
            "admin/job_details.html",
            job=job,
            applications=applications
        )

    # ---------------- STUDENT ----------------

    @app.route("/student/dashboard")
    @login_required("student")
    def student_dashboard():

        active_drives = JobPosition.query.filter(
            JobPosition.status == "Approved",
            JobPosition.deadline >= date.today()
        ).order_by(JobPosition.posted_date.desc()).limit(5).all()

        return render_template(
            "dashboards/student.html",
            drives=active_drives
        )

    @app.route("/student/jobs")
    @login_required("student")
    def student_jobs():

        search = request.args.get("search", "")

        query = JobPosition.query.filter_by(status="Approved")

        if search:
            query = query.join(Company).filter(
                (JobPosition.title.ilike(f"%{search}%")) |
                (Company.name.ilike(f"%{search}%")) |
                (JobPosition.skills.ilike(f"%{search}%"))
            )

        jobs = query.all()

        return render_template(
            "student/jobs.html",
            jobs=jobs
        )

    @app.route("/student/apply/<int:job_id>")
    @login_required("student")
    def apply_job(job_id):

        student_id = session.get("user_id")

        existing = Application.query.filter_by(
            student_id=student_id,
            job_position_id=job_id
        ).first()

        if existing:
            flash("Already applied.")
            return redirect(url_for("student_jobs"))

        new_app = Application(
            student_id=student_id,
            job_position_id=job_id,
            status="Applied"
        )

        db.session.add(new_app)
        db.session.commit()

        return redirect(url_for("student_my_applications"))

    @app.route("/student/my_applications")
    @login_required("student")
    def student_my_applications():

        student_id = session.get("user_id")

        applications = Application.query.filter_by(
            student_id=student_id
        ).all()

        return render_template(
            "student/my_applications.html",
            applications=applications
        )
    @app.route("/student/profile", methods=["GET", "POST"])
    @login_required("student")

    def student_profile():

        student_id = session.get("user_id")
        student = Student.query.get_or_404(student_id)

        if request.method == "POST":

            student.name = request.form["name"]
            student.department = request.form["department"]

            cgpa = request.form.get("cgpa")

            if cgpa:
                try:
                    student.cgpa = float(cgpa)
                except:
                    flash("Invalid CGPA")

            # Resume upload
            if "resume" in request.files:
                file = request.files["resume"]

                if file.filename != "":
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(file.filename)

                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    student.resume = filename

            db.session.commit()

            flash("Profile updated successfully")
            return redirect(url_for("student_profile"))

        return render_template(
            "student/profile.html",
            student=student
        )

    # ---------------- COMPANY ----------------

    @app.route("/company/dashboard")
    @login_required("company")
    def company_dashboard():

        company_id = session.get("user_id")

        company = Company.query.get_or_404(company_id)

        jobs = JobPosition.query.filter_by(
            company_id=company_id
        ).all()

        total_applications = sum(len(job.applications) for job in jobs)

        return render_template(
            "dashboards/company.html",
            company=company,
            jobs=jobs,
            total_applications=total_applications
        )

    @app.route("/company/post_job", methods=["GET", "POST"])
    @login_required("company")
    def post_job():

        company_id = session.get("user_id")

        if request.method == "POST":

            deadline = datetime.strptime(
                request.form["deadline"],
                "%Y-%m-%d"
            ).date()

            job = JobPosition(
                company_id=company_id,
                title=request.form["title"],
                description=request.form["description"],
                eligibility=request.form["eligibility"],
                deadline=deadline,
                skills=request.form["skills"],
                experience=request.form["experience"],
                salary=request.form["salary"],
                status="Pending"
            )

            db.session.add(job)
            db.session.commit()

            return redirect(url_for("company_dashboard"))

        return render_template("company/post_job.html")

    

    @app.route("/company/applications")
    @login_required("company")
    def company_applications():

        company_id = session.get("user_id")

        jobs = JobPosition.query.filter_by(
            company_id=company_id
        ).all()

        return render_template(
            "company/view_applications.html",
            jobs=jobs
    )


    @app.route("/application/<int:app_id>/update_status/<status>")
    @login_required("company")
    def update_application_status(app_id, status):

        application = Application.query.get_or_404(app_id)

        if application.job_position.company_id != session.get("user_id"):
            flash("Unauthorized action")
            return redirect(url_for("company_dashboard"))

        if status in ["Shortlisted", "Interview", "Selected", "Placed", "Rejected"]:
            application.status = status
            db.session.commit()

        return redirect(request.referrer or url_for("company_applications"))
    
    @app.route("/student/profile/<int:student_id>")
    @login_required("company")
    def view_student_profile(student_id):

        student = Student.query.get_or_404(student_id)

        return render_template(
            "company/student_profile.html",
            student=student
        )
    
    
    @app.route("/company/update_job_status/<int:job_id>/<status>")
    @login_required("company")
    def update_job_status(job_id, status):

        job = JobPosition.query.get_or_404(job_id)

        # ensure company owns the job
        if job.company_id != session.get("user_id"):
            flash("Unauthorized action")
            return redirect(url_for("company_dashboard"))

        if status in ["Closed", "Active"]:
            job.status = status
            db.session.commit()
            flash(f"Job status updated to {status}")

        return redirect(url_for("company_dashboard"))
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)