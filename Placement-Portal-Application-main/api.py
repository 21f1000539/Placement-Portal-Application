from flask import Blueprint, jsonify, request, session
from db import db
from models import JobPosition, Company, Student

api_bp = Blueprint("api", __name__)

# Helper to check authentication (simple session check for now)
def is_company():
    return session.get("role") == "company"

def is_admin():
    return session.get("role") == "admin"

# --- JOBS API ---

@api_bp.route("/jobs", methods=["GET"])
def get_jobs():
    jobs = JobPosition.query.filter_by(status="Approved").all()
    result = []
    for job in jobs:
        result.append({
            "id": job.id,
            "title": job.title,
            "company": job.company.name,
            "deadline": job.deadline.strftime("%Y-%m-%d") if job.deadline else None,
            "status": job.status
        })
    return jsonify(result), 200

@api_bp.route("/jobs/<int:job_id>", methods=["GET"])
def get_job_detail(job_id):
    job = JobPosition.query.get_or_404(job_id)
    return jsonify({
        "id": job.id,
        "title": job.title,
        "company": job.company.name,
        "description": job.description,
        "skills": job.skills,
        "salary": job.salary,
        "status": job.status
    }), 200

@api_bp.route("/jobs", methods=["POST"])
def create_job():
    if not is_company():
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    company_id = session.get("user_id")
    company = Company.query.get(company_id)
    if not company.is_approved:
        return jsonify({"error": "Company not approved"}), 403

    from datetime import datetime
    try:
        deadline = datetime.strptime(data.get("deadline"), "%Y-%m-%d").date()
    except:
        deadline = None

    new_job = JobPosition(
        company_id=company_id,
        title=data.get("title"),
        description=data.get("description"),
        eligibility=data.get("eligibility"),
        deadline=deadline,
        skills=data.get("skills"),
        experience=data.get("experience"),
        salary=data.get("salary"),
        status="Pending"
    )
    db.session.add(new_job)
    db.session.commit()
    
    return jsonify({"message": "Job created", "id": new_job.id}), 201

@api_bp.route("/jobs/<int:job_id>", methods=["PUT"])
def update_job(job_id):
    if not is_company():
        return jsonify({"error": "Unauthorized"}), 403
    
    job = JobPosition.query.get_or_404(job_id)
    if job.company_id != session.get("user_id"):
        return jsonify({"error": "Unauthorized access to this job"}), 403
        
    data = request.json
    if "title" in data: job.title = data["title"]
    if "description" in data: job.description = data["description"]
    if "salary" in data: job.salary = data["salary"]
    
    # We don't verify all fields for brevity, but enough to show method works
    
    db.session.commit()
    return jsonify({"message": "Job updated"}), 200

@api_bp.route("/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    if not is_company():
        return jsonify({"error": "Unauthorized"}), 403

    job = JobPosition.query.get_or_404(job_id)
    if job.company_id != session.get("user_id"):
        return jsonify({"error": "Unauthorized access to this job"}), 403
    
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted"}), 200


# --- COMPANIES API ---

@api_bp.route("/companies", methods=["GET"])
def get_companies():
    companies = Company.query.filter_by(is_approved=True).all()
    result = []
    for c in companies:
        result.append({
            "id": c.id,
            "name": c.name,
            "website": c.website
        })
    return jsonify(result), 200


# --- STUDENTS API ---

@api_bp.route("/students", methods=["GET"])
def get_students():
    if not (is_admin() or is_company()):
        return jsonify({"error": "Unauthorized"}), 403
        
    students = Student.query.filter_by(is_active=True).all()
    result = []
    for s in students:
        result.append({
            "id": s.id,
            "name": s.name,
            "department": s.department,
            "cgpa": s.cgpa
        })
    return jsonify(result), 200
