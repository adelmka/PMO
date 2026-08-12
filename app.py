from __future__ import annotations

import os
from pathlib import Path
from flask import Flask, flash, redirect, render_template, request, url_for
from models import db, ConfigurationItem, Project, Resource
from services import DashboardService, ProjectService, seed_configuration

PHASES = ["PMO Review", "SME Review", "Functional Requirement (DSD)", "IT Demand Submitted", "IT Estimation", "IT Build", "UAT", "Deployment"]
STATUSES = ["Under Review", "Accepted", "Assigned", "Design", "Build", "UAT", "Deployment", "Delivered", "On Hold", "Cancelled"]

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "change-this-before-production"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///" + str(Path(app.instance_path) / "pmo_pulse.db")),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        seed_configuration()

    @app.get("/")
    def dashboard():
        period = request.args.get("period", "quarter")
        return render_template("dashboard.html", data=DashboardService.summary(period))

    @app.route("/requests/new", methods=["GET", "POST"])
    def intake():
        if request.method == "POST":
            try:
                project = ProjectService.create_request(request.form)
                flash(f"Request {project.reference_number} submitted successfully!", "success")
                return redirect(url_for("project_detail", project_id=project.id))
            except ValueError as error:
                flash(str(error), "error")
        return render_template("intake.html", **form_data())

    @app.get("/projects")
    def projects():
        query = Project.query
        
        # Search filter
        search = request.args.get("search", "").strip()
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Project.reference_number.ilike(search_term)) |
                (Project.title.ilike(search_term))
            )
        
        # Status filter
        status = request.args.get("status", "").strip()
        if status:
            query = query.filter_by(status=status)
        
        # Order by most recently updated
        query = query.order_by(Project.updated_at.desc())
        
        return render_template("projects.html", projects=query.all())

    @app.route("/projects/<int:project_id>", methods=["GET", "POST"])
    def project_detail(project_id):
        project = db.get_or_404(Project, project_id)
        if request.method == "POST":
            ProjectService.update_project(project, request.form)
            flash("Project updated successfully!", "success")
            return redirect(url_for("project_detail", project_id=project.id))
        return render_template("project_detail.html", project=project, histories=project.histories, **form_data())

    @app.route("/configuration", methods=["GET", "POST"])
    def configuration():
        if request.method == "POST":
            label, kind = request.form.get("label", "").strip(), request.form.get("kind")
            if kind in {"category", "type", "agency", "system"} and label:
                # Check if already exists
                existing = ConfigurationItem.query.filter_by(kind=kind, label=label).first()
                if existing:
                    flash(f"'{label}' already exists in {kind}.", "error")
                else:
                    db.session.add(ConfigurationItem(kind=kind, label=label))
                    db.session.commit()
                    flash(f"Configuration item '{label}' added successfully!", "success")
            else:
                flash("Please choose a valid configuration type and enter a value.", "error")
        return render_template("configuration.html", items=ConfigurationItem.query.order_by(ConfigurationItem.kind, ConfigurationItem.label).all())

    return app

def form_data():
    return {
        "categories": ConfigurationItem.active("category"),
        "types": ConfigurationItem.active("type"),
        "agencies": ConfigurationItem.active("agency"),
        "systems": ConfigurationItem.active("system"),
        "resources": Resource.query.order_by(Resource.name).all(),
        "phases": PHASES,
        "statuses": STATUSES
    }

app = create_app()
