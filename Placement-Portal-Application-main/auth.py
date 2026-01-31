from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from models import Student, Company, Admin

auth_bp = Blueprint("auth", __name__)


from flask import request, redirect, render_template, url_for, flash
from werkzeug.security import generate_password_hash
from models import Student
from app import db


@auth_bp.route("/register/student", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        email = request.form["email"]

        existing = Student.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered")
            return redirect(url_for("auth.student_register"))

        student = Student(
            name=request.form["name"],
            email=email,
            password=generate_password_hash(request.form["password"]),
        )

        db.session.add(student)
        db.session.commit()

        flash("Registration successful. Please login.")
        return redirect(url_for("student_login"))

    return render_template("student_register.html")



from werkzeug.security import check_password_hash
from flask import session

@auth_bp.route("/login/student", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        student = Student.query.filter_by(
            email=request.form["email"]
        ).first()

        if student and check_password_hash(student.password, request.form["password"]):
            session["user_id"] = student.id
            session["role"] = "student"
            return redirect(url_for("student_dashboard"))

        flash("Invalid credentials")
    return render_template("student_login.html")

@auth_bp.route("/register/company", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        company = Company(
            name=request.form["name"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"]),
            is_approved=False
        )
        db.session.add(company)
        db.session.commit()

        flash("Registration submitted. Await admin approval.")
        return redirect(url_for("auth.company_login"))

    return render_template("company_register.html")

@auth_bp.route("/login/company", methods=["GET", "POST"])
def company_login():
    if request.method == "POST":
        company = Company.query.filter_by(
            email=request.form["email"]
        ).first()

        if not company:
            flash("Invalid credentials")
            return redirect(url_for("company_login"))

        if not company.is_approved:
            flash("Company not approved by admin yet")
            return redirect(url_for("company_login"))

        if check_password_hash(company.password, request.form["password"]):
            session["user_id"] = company.id
            session["role"] = "company"
            return redirect(url_for("company_dashboard"))

        flash("Invalid credentials")

    return render_template("company_login.html")


from models import Admin

@auth_bp.route("/login/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin = Admin.query.filter_by(
            username=request.form["username"]
        ).first()

        if admin and admin.password == request.form["password"]:
            session["user_id"] = admin.id
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin credentials")

    return render_template("admin_login.html")


from functools import wraps
from flask import session, redirect, url_for

def login_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if "role" not in session or session["role"] != role:
                return redirect(url_for("index"))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


@auth_bp.route("/admin/dashboard")
@login_required("admin")
def admin_dashboard():
    return "Admin Dashboard"

@auth_bp.route("/student/dashboard")
@login_required("student")
def student_dashboard():
    return "Student Dashboard"

@auth_bp.route("/company/dashboard")
@login_required("company")
def company_dashboard():
    return "Company Dashboard"

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

