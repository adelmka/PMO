from datetime import datetime
from sqlalchemy import func
from models import db, ConfigurationItem, Customer, Project, StatusHistory

DEFAULTS = {
    "category": ["New System", "Systems Enhancement", "Policy Implementation", "Audit"],
    "type": ["SAP", "Web/Portal Application", "Dashboard & Reporting", "AI / GenAI / Data Science", "Mobile", "RPA", "e-Government Data Integration"],
    "agency": ["IT", "In-House", "Vendor"],
    "system": ["SAP HCM", "HR Portal", "Data Warehouse"],
}
def seed_configuration():
    for kind, labels in DEFAULTS.items():
        for label in labels:
            if not ConfigurationItem.query.filter_by(kind=kind, label=label).first():
                db.session.add(ConfigurationItem(kind=kind, label=label))
    db.session.commit()

class ProjectService:
    @staticmethod
    def create_request(form):
        required = ["requester_name", "requester_email", "organization_number", "organization_title", "title", "short_description", "category", "project_type", "construction_agency"]
        missing = [field.replace("_", " ") for field in required if not form.get(field, "").strip()]
        if missing:
            raise ValueError("Required: " + ", ".join(missing))
        customer = Customer.query.filter_by(organization_number=form["organization_number"].strip()).first()
        if not customer:
            customer = Customer(organization_number=form["organization_number"].strip(), organization_title=form["organization_title"].strip())
            db.session.add(customer)
            db.session.flush()
        customer.contact_name, customer.contact_email = form["requester_name"], form["requester_email"]
        year = datetime.utcnow().year
        sequence = Project.query.filter(Project.reference_number.like(f"PMO-{year}-%")).count() + 1
        project = Project(reference_number=f"PMO-{year}-{sequence:04d}", title=form["title"].strip(), short_description=form["short_description"].strip(), requester_name=form["requester_name"].strip(), requester_email=form["requester_email"].strip(), customer=customer, category=form["category"], project_type=form["project_type"], construction_agency=form["construction_agency"], impacted_systems=", ".join(form.getlist("impacted_systems")))
        db.session.add(project)
        db.session.flush()
        db.session.add(StatusHistory(project=project, phase=project.phase, status=project.status, note="Request submitted", changed_by=project.requester_name))
        db.session.commit()
        return project

    @staticmethod
    def update_project(project, form):
        old = (project.phase, project.status)
        for field in ["phase", "status", "assigned_team", "decision_reason", "it_demand_number", "document_links"]:
            if field in form:
                setattr(project, field, form.get(field) or None)
        for field in ["pmo_analyst_id", "group_lead_id", "project_lead_id", "estimated_duration_weeks"]:
            if field in form:
                setattr(project, field, int(form[field]) if form.get(field) else None)
        if form.get("estimated_cost"):
            project.estimated_cost = form["estimated_cost"]
        if project.status == "Delivered" and not project.completed_at:
            project.completed_at = datetime.utcnow()
        if old != (project.phase, project.status) or form.get("note"):
            db.session.add(StatusHistory(project=project, phase=project.phase, status=project.status, note=form.get("note"), changed_by=form.get("changed_by") or "PMO User"))
        db.session.commit()

class DashboardService:
    @staticmethod
    def summary(period):
        now = datetime.utcnow()
        start = datetime(now.year, 1, 1)
        if period == "month":
            start = datetime(now.year, now.month, 1)
        elif period == "quarter":
            start = datetime(now.year, ((now.month - 1) // 3) * 3 + 1, 1)
        return {"projects": Project.query.order_by(Project.updated_at.desc()).all(),
                "received": Project.query.filter(Project.created_at >= start).count(),
                "completed": Project.query.filter(Project.completed_at >= start).count(),
                "ytd_received": Project.query.filter(Project.created_at >= datetime(now.year, 1, 1)).count(),
                "ytd_completed": Project.query.filter(Project.completed_at >= datetime(now.year, 1, 1)).count(),
                "by_status": db.session.query(Project.status, func.count(Project.id)).group_by(Project.status).all(),
                "by_category": db.session.query(Project.category, func.count(Project.id)).group_by(Project.category).all(),
                "period_label": period.title()}
