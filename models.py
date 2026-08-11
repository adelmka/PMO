from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class ConfigurationItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(30), nullable=False, index=True)
    label = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    __table_args__ = (db.UniqueConstraint("kind", "label", name="uq_configuration_kind_label"),)
    @classmethod
    def active(cls, kind):
        return cls.query.filter_by(kind=kind, active=True).order_by(cls.label).all()

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_number = db.Column(db.String(50), nullable=False, unique=True)
    organization_title = db.Column(db.String(150), nullable=False)
    contact_name = db.Column(db.String(120))
    contact_email = db.Column(db.String(150))
    projects = db.relationship("Project", back_populates="customer")

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True)
    team = db.Column(db.String(100))
    expertise = db.Column(db.String(250))
    active = db.Column(db.Boolean, default=True, nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference_number = db.Column(db.String(30), nullable=False, unique=True, index=True)
    title = db.Column(db.String(200), nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    requester_name = db.Column(db.String(120), nullable=False)
    requester_email = db.Column(db.String(150), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    customer = db.relationship("Customer", back_populates="projects")
    category = db.Column(db.String(100), nullable=False)
    project_type = db.Column(db.String(100), nullable=False)
    construction_agency = db.Column(db.String(50), nullable=False)
    impacted_systems = db.Column(db.String(500), default="")
    phase = db.Column(db.String(80), default="PMO Review", nullable=False)
    status = db.Column(db.String(40), default="Under Review", nullable=False)
    assigned_team = db.Column(db.String(100))
    pmo_analyst_id = db.Column(db.Integer, db.ForeignKey("resource.id"))
    group_lead_id = db.Column(db.Integer, db.ForeignKey("resource.id"))
    project_lead_id = db.Column(db.Integer, db.ForeignKey("resource.id"))
    pmo_analyst = db.relationship("Resource", foreign_keys=[pmo_analyst_id])
    group_lead = db.relationship("Resource", foreign_keys=[group_lead_id])
    project_lead = db.relationship("Resource", foreign_keys=[project_lead_id])
    decision_reason = db.Column(db.Text)
    it_demand_number = db.Column(db.String(80))
    estimated_cost = db.Column(db.Numeric(14, 2))
    estimated_duration_weeks = db.Column(db.Integer)
    document_links = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    histories = db.relationship("StatusHistory", back_populates="project", cascade="all, delete-orphan", order_by="StatusHistory.created_at.desc()")

class StatusHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    project = db.relationship("Project", back_populates="histories")
    phase = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(40), nullable=False)
    note = db.Column(db.Text)
    changed_by = db.Column(db.String(120), default="System")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
