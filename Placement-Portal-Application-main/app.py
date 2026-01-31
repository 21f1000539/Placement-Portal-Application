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

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/admin/dashboard")
    @login_required("admin")
    def admin_dashboard():
        return render_template("dashboards/admin.html")

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
