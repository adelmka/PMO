import pytest
from app import create_app
from models import db

@pytest.fixture()
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app.test_client()

def test_dashboard_loads(client):
    assert client.get("/").status_code == 200

def test_intake_generates_reference(client):
    response = client.post("/requests/new", data={
        "requester_name": "Amina", "requester_email": "amina@example.com",
        "organization_number": "HR-01", "organization_title": "Human Resources",
        "title": "Leave dashboard", "short_description": "Reporting dashboard",
        "category": "Dashboard & Reporting", "project_type": "Web/Portal Application",
        "construction_agency": "IT"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"PMO-" in response.data
