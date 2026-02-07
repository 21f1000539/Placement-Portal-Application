# Placement Portal Application

A comprehensive placement portal for managing students, companies, and job/internship applications.

## Features
- **Admin Dashboard**: Manage students, companies, and jobs.
- **Student Dashboard**: Apply for jobs, manage profile, view status.
- **Company Dashboard**: Post jobs, view applications, shortlist candidates.

## Installation

1.  **Clone the repository**.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Database Initialization
The project uses SQLite. To initialize the database:

```bash
python init_db.py
```

This will create `instance/placement.db` and a default admin user.

- **Admin Username**: `admin`
- **Admin Password**: `admin123`

## Running the Application

```bash
python app.py
```

Access the application at `http://127.0.0.1:5000/`.

## Login Credentials (Default)

- **Admin**: `admin` / `admin123`
- **Companies/Students**: Register via the "Register" links on the home page.