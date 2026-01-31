from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from models import Student, Company, Admin

auth_bp = Blueprint("auth", __name__)

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
            department=request.form.get("department"),
            cgpa=request.form.get("cgpa"),
            resume=request.form.get("resume")
        )

        db.session.add(student)
        db.session.commit()

        flash("Registration successful. Please login.")
        return redirect(url_for("auth.student_login"))

    return render_template("student_register.html")


@auth_bp.route("/login/student", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        student = Student.query.filter_by(email=request.form["email"]).first()

        if student and check_password_hash(student.password, request.form["password"]):
            if not student.is_active:
                flash("Account deactivated by admin.")
                return redirect(url_for("auth.student_login"))
            
            session["user_id"] = student.id
            session["role"] = "student"
            return redirect(url_for("student_dashboard"))

        flash("Invalid credentials")
    return render_template("student_login.html")


@auth_bp.route("/register/company", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        existing = Company.query.filter_by(email=request.form["email"]).first()
        if existing:
             flash("Email already registered")
             return redirect(url_for("auth.company_register"))

        company = Company(
            name=request.form["name"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"]),
            website=request.form.get("website"),
            hr_contact=request.form.get("hr_contact"),
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
        company = Company.query.filter_by(email=request.form["email"]).first()

        if not company:
            flash("Invalid credentials")
            return redirect(url_for("auth.company_login"))

        if not company.is_approved:
            flash("Company not approved by admin yet")
            return redirect(url_for("auth.company_login"))

        if check_password_hash(company.password, request.form["password"]):
            session["user_id"] = company.id
            session["role"] = "company"
            return redirect(url_for("company_dashboard"))

        flash("Invalid credentials")

    return render_template("company_login.html")


@auth_bp.route("/login/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin = Admin.query.filter_by(username=request.form["username"]).first()

        if admin and check_password_hash(admin.password, request.form["password"]):
            session["user_id"] = admin.id
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin credentials")

    return render_template("admin_login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


