# Placement Portal Application

A comprehensive and robust placement portal designed to bridge the gap between students, hiring companies, and college placement cells. The system offers dedicated, role-based dashboards to streamline the entire placement workflow.

## 🚀 Features

### General System Operations
*   **Role-Based Access Control**: Secure, separate dashboards and interfaces for Admins, Companies, and Students.
*   **Session-based Authentication**: Secure login/registration flows with password hashing via `Werkzeug`.
*   **Approval Workflows**: Companies are vetted and actively approved by administrators before gaining the ability to post jobs.

### Admin Capabilities
*   Review and systematically approve or reject newly registered companies.
*   Activate, deactivate, or blacklist student and company accounts across the platform.
*   Monitor all platform activity, overseeing job postings and managing student access as needed.

### Company Capabilities
*   Register and create a rich company profile.
*   Publish multiple detailed job or internship postings (with requirements, salary, and deadlines).
*   Review student applications and securely download uploaded resumes.
*   Actively manage candidate application statuses (Shortlisted, Selected, Rejected).

### Student Capabilities
*   Manage a comprehensive academic profile, including CGPA and department details.
*   Upload and confidently manage resume documentation.
*   Browse, filter, and flexibly apply for actively approved job postings.
*   Track the real-time status of all submitted job applications via the personal dashboard.

## 🛠️ Architecture & Technologies Used

*   **Backend Strategy**: Flask 3.0 (Python) utilizing a modular structure for controllers, forms, and routes.
*   **Database Management**: SQLite managed seamlessly via SQLAlchemy ORM.
*   **Frontend Templating**: Jinja2 working in tandem with Bootstrap 5.3 + Icons for responsive, cleanly styled user interfaces.

### Core File Structure Highlights
-   `app.py`: Route controller and main Flask entry point.
-   `auth.py`: Centralized authentication and registration flows.
-   `models.py`: Declarative SQLAlchemy models.
-   `templates/`: HTML structures segmented by user role views.
-   `init_db.py`: Quick-start utility to rapidly create schemas and seed essential data.

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/21f1000539/Placement-Portal-Application.git
    cd Placement-Portal-Application-main
    ```

2.  **Set Up Virtual Environment** (Highly Recommended)
    ```bash
    python -m venv venv
    ```
    - Activate the environment (Windows): `venv\Scripts\activate`
    - Activate the environment (Mac/Linux): `source venv/bin/activate`

3.  **Install Required Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the Database**
    To construct the initial SQLite relations and seed a default admin user, strictly execute:
    ```bash
    python init_db.py
    ```
    *(Note: This creates `instance/placement.db`)*

5.  **Run the Application locally**
    ```bash
    python app.py
    ```
    Navigate to `http://127.0.0.1:5000/` in your preferred web browser.

## 🔐 Default Login Credentials
Upon initializing the database via `init_db.py`, a default administrator account will be immediately available.

**Admin Credentials:**
*   Username: `admin`
*   Password: `admin123`

*Students and Companies will actively register their distinct accounts via the "Register" links natively on the index page.*

---

*This application was developed as part of standard college coursework focusing on scalable system design, active automation, and solving real-world challenges using modern code practices.*