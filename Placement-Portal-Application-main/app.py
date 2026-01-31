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

    from models import Company

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/admin/dashboard")
    @login_required("admin")
    def admin_dashboard():
        pending_companies = Company.query.filter_by(is_approved=False).all()
        return render_template("dashboards/admin.html", companies=pending_companies)

    @app.route("/admin/approve/<int:company_id>")
    @login_required("admin")
    def approve_company(company_id):
        company = Company.query.get_or_404(company_id)
        company.is_approved = True
        db.session.commit()
        from flask import flash, redirect, url_for
        flash(f"Company {company.name} approved!")
        return redirect(url_for("admin_dashboard"))

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
