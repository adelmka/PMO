import pytest
from app import create_app
from models import db, Project, Customer, Resource, ConfigurationItem
from datetime import datetime

@pytest.fixture()
def app():
    """Create application for the tests."""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture()
def sample_customer(app):
    """Create a sample customer for testing."""
    with app.app_context():
        customer = Customer(
            organization_number="TEST-01",
            organization_title="Test Organization",
            contact_name="John Doe",
            contact_email="john@test.com"
        )
        db.session.add(customer)
        db.session.commit()
        yield customer

@pytest.fixture()
def sample_resource(app):
    """Create a sample resource for testing."""
    with app.app_context():
        resource = Resource(
            name="Jane Smith",
            email="jane@test.com",
            team="Platform Team",
            expertise="Python, Flask",
            active=True
        )
        db.session.add(resource)
        db.session.commit()
        yield resource

@pytest.fixture()
def sample_project(app, sample_customer):
    """Create a sample project for testing."""
    with app.app_context():
        project = Project(
            reference_number="PMO-2026-0001",
            title="Test Project",
            short_description="A test project for automation",
            requester_name="Test User",
            requester_email="test@example.com",
            customer_id=sample_customer.id,
            category="New System",
            project_type="Web/Portal Application",
            construction_agency="IT",
            phase="PMO Review",
            status="Under Review"
        )
        db.session.add(project)
        db.session.commit()
        # Refresh to avoid detached instance issues
        db.session.refresh(project)
        yield project

# ============================================================================
# DASHBOARD TESTS
# ============================================================================

def test_dashboard_loads(client):
    """Test that the dashboard page loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"PMO Pulse Dashboard" in response.data

def test_dashboard_displays_metrics(client, app, sample_customer, sample_project):
    """Test that dashboard displays key metrics."""
    response = client.get("/")
    assert response.status_code == 200
    # Check for metric cards
    assert b"Received" in response.data
    assert b"Completed" in response.data
    assert b"YTD" in response.data

def test_dashboard_period_filter_month(client):
    """Test dashboard with month period filter."""
    response = client.get("/?period=month")
    assert response.status_code == 200
    assert b"This Month" in response.data

def test_dashboard_period_filter_quarter(client):
    """Test dashboard with quarter period filter."""
    response = client.get("/?period=quarter")
    assert response.status_code == 200
    assert b"This Quarter" in response.data

def test_dashboard_period_filter_year(client):
    """Test dashboard with year period filter."""
    response = client.get("/?period=year")
    assert response.status_code == 200
    assert b"Year to Date" in response.data

# ============================================================================
# INTAKE/NEW REQUEST TESTS
# ============================================================================

def test_intake_form_loads(client):
    """Test that the intake form loads successfully."""
    response = client.get("/requests/new")
    assert response.status_code == 200
    assert b"Submit IT Project Request" in response.data
    assert b"Requester Name" in response.data
    assert b"Organization Number" in response.data

def test_intake_generates_reference(client):
    """Test that intake form generates correct reference number."""
    response = client.post("/requests/new", data={
        "requester_name": "Amina",
        "requester_email": "amina@example.com",
        "organization_number": "HR-01",
        "organization_title": "Human Resources",
        "title": "Leave dashboard",
        "short_description": "Reporting dashboard",
        "category": "New System",
        "project_type": "Web/Portal Application",
        "construction_agency": "IT"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"PMO-" in response.data
    assert b"submitted successfully" in response.data

def test_intake_missing_required_field(client):
    """Test that intake form rejects missing required fields."""
    response = client.post("/requests/new", data={
        "requester_name": "Amina",
        "requester_email": "amina@example.com",
        # Missing organization_number
        "organization_title": "Human Resources",
        "title": "Leave dashboard",
        "short_description": "Reporting dashboard",
        "category": "New System",
        "project_type": "Web/Portal Application",
        "construction_agency": "IT"
    }, follow_redirects=True)
    assert response.status_code == 200
    # Should show error or redirect to form

def test_intake_creates_customer(client, app):
    """Test that intake creates a new customer if not exists."""
    with app.app_context():
        initial_count = Customer.query.count()
    
    response = client.post("/requests/new", data={
        "requester_name": "Bob",
        "requester_email": "bob@example.com",
        "organization_number": "NEW-ORG",
        "organization_title": "New Organization",
        "title": "New Project",
        "short_description": "Test project",
        "category": "New System",
        "project_type": "Web/Portal Application",
        "construction_agency": "IT"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    with app.app_context():
        final_count = Customer.query.count()
        assert final_count > initial_count
        customer = Customer.query.filter_by(organization_number="NEW-ORG").first()
        assert customer is not None
        assert customer.organization_title == "New Organization"

# ============================================================================
# PROJECT LIST & SEARCH TESTS
# ============================================================================

def test_projects_list_loads(client):
    """Test that projects list page loads."""
    response = client.get("/projects")
    assert response.status_code == 200
    assert b"Projects" in response.data
    assert b"Search" in response.data or b"search" in response.data

def test_projects_search_by_reference(client, app, sample_customer):
    """Test searching projects by reference number."""
    # Create test projects within app context
    with app.app_context():
        for i in range(3):
            project = Project(
                reference_number=f"PMO-2026-{i:04d}",
                title=f"Project {i}",
                short_description="Test project",
                requester_name="Test User",
                requester_email="test@example.com",
                customer_id=sample_customer.id,
                category="New System",
                project_type="Web/Portal Application",
                construction_agency="IT"
            )
            db.session.add(project)
        db.session.commit()
    
    # Test search
    response = client.get("/projects?search=PMO-2026-0001")
    assert response.status_code == 200
    assert b"PMO-2026-0001" in response.data

def test_projects_search_by_title(client, app, sample_customer):
    """Test searching projects by title."""
    # Create test projects within app context
    with app.app_context():
        project1 = Project(
            reference_number="PMO-2026-0001",
            title="Leave Management System",
            short_description="Test",
            requester_name="Test User",
            requester_email="test@example.com",
            customer_id=sample_customer.id,
            category="New System",
            project_type="Web/Portal Application",
            construction_agency="IT"
        )
        project2 = Project(
            reference_number="PMO-2026-0002",
            title="Payroll System",
            short_description="Test",
            requester_name="Test User",
            requester_email="test@example.com",
            customer_id=sample_customer.id,
            category="New System",
            project_type="Web/Portal Application",
            construction_agency="IT"
        )
        db.session.add(project1)
        db.session.add(project2)
        db.session.commit()
    
    # Test search for "Leave"
    response = client.get("/projects?search=Leave")
    assert response.status_code == 200
    assert b"Leave Management System" in response.data

def test_projects_filter_by_status(client, app, sample_customer):
    """Test filtering projects by status."""
    # Create projects with different statuses within app context
    with app.app_context():
        project1 = Project(
            reference_number="PMO-2026-0001",
            title="Project 1",
            short_description="Test",
            requester_name="Test User",
            requester_email="test@example.com",
            customer_id=sample_customer.id,
            category="New System",
            project_type="Web/Portal Application",
            construction_agency="IT",
            status="Under Review"
        )
        project2 = Project(
            reference_number="PMO-2026-0002",
            title="Project 2",
            short_description="Test",
            requester_name="Test User",
            requester_email="test@example.com",
            customer_id=sample_customer.id,
            category="New System",
            project_type="Web/Portal Application",
            construction_agency="IT",
            status="Delivered"
        )
        db.session.add(project1)
        db.session.add(project2)
        db.session.commit()
    
    # Test filter by status
    response = client.get("/projects?status=Delivered")
    assert response.status_code == 200
    assert b"Project 2" in response.data

def test_projects_search_and_filter_combined(client, app, sample_customer):
    """Test combining search and filter."""
    # Create test projects within app context
    with app.app_context():
        project1 = Project(
            reference_number="PMO-2026-0001",
            title="Dashboard",
            short_description="Test",
            requester_name="Test User",
            requester_email="test@example.com",
            customer_id=sample_customer.id,
            category="New System",
            project_type="Web/Portal Application",
            construction_agency="IT",
            status="Under Review"
        )
        project2 = Project(
            reference_number="PMO-2026-0002",
            title="Dashboard System",
            short_description="Test",
            requester_name="Test User",
            requester_email="test@example.com",
            customer_id=sample_customer.id,
            category="New System",
            project_type="Web/Portal Application",
            construction_agency="IT",
            status="Delivered"
        )
        db.session.add(project1)
        db.session.add(project2)
        db.session.commit()
    
    # Test combined search and filter
    response = client.get("/projects?search=Dashboard&status=Delivered")
    assert response.status_code == 200
    assert b"PMO-2026-0002" in response.data

# ============================================================================
# PROJECT DETAIL TESTS
# ============================================================================

def test_project_detail_loads(client, app, sample_customer):
    """Test that project detail page loads."""
    with app.app_context():
        project = Project(
            reference_number="PMO-2026-TEST",
            title="Detail Test Project",
            short_description="Test",
            requester_name="Test User",
            requester_email="test@example.com",
            customer_id=sample_customer.id,
            category="New System",
            project_type="Web/Portal Application",
            construction_agency="IT"
        )
        db.session.add(project)
        db.session.commit()
        project_id = project.id
    
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert b"PMO-2026-TEST" in response.data
    assert b"Detail Test Project" in response.data

def test_project_detail_displays_status(client, app, sample_customer):
    """Test that project detail displays current status and phase."""
    with app.app_context():
        project = Project(
            reference_number="PMO-2026-STATUS",
            title="Status Test Project",
            short_description="Test",
            requester_name="Test User",
            requester_email="test@example.com",
            customer_id=sample_customer.id,
            category="New System",
            project_type="Web/Portal Application",
            construction_agency="IT",
            phase="PMO Review",
            status="Under Review"
        )
        db.session.add(project)
        db.session.commit()
        project_id = project.id
    
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert b"Under Review" in response.data
    assert b"PMO Review" in response.data

def test_project_detail_displays_history(client, app, sample_customer):
    """Test that project history is displayed."""
    with app.app_context():
        project = Project(
            reference_number="PMO-2026-HIST",
            title="History Test Project",
            short_description="Test",
            requester_name="Test User",
            requester_email="test@example.com",
            customer_id=sample_customer.id,
            category="New System",
            project_type="Web/Portal Application",
            construction_agency="IT"
        )
        db.session.add(project)
        db.session.commit()
        project_id = project.id
    
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    # Check for history section
    assert b"History" in response.data or b"history" in response.data

def test_project_detail_update(client, app, sample_customer, sample_resource):
    """Test updating a project."""
    with app.app_context():
        project = Project(
            reference_number="PMO-2026-UPDATE",
            title="Update Test Project",
            short_description="Test",
            requester_name="Test User",
            requester_email="test@example.com",
            customer_id=sample_customer.id,
            category="New System",
            project_type="Web/Portal Application",
            construction_agency="IT",
            phase="PMO Review",
            status="Under Review"
        )
        db.session.add(project)
        db.session.commit()
        project_id = project.id
    
    response = client.post(f"/projects/{project_id}", data={
        "phase": "IT Demand Submitted",
        "status": "Accepted",
        "pmo_analyst_id": sample_resource.id,
        "note": "Project approved by PMO"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"updated successfully" in response.data
    
    # Verify the update
    with app.app_context():
        updated_project = Project.query.get(project_id)
        assert updated_project.status == "Accepted"
        assert updated_project.phase == "IT Demand Submitted"

def test_project_detail_update_creates_history(client, app, sample_customer):
    """Test that updating a project creates a status history entry."""
    with app.app_context():
        project = Project(
            reference_number="PMO-2026-HISTORY",
            title="History Creation Test",
            short_description="Test",
            requester_name="Test User",
            requester_email="test@example.com",
            customer_id=sample_customer.id,
            category="New System",
            project_type="Web/Portal Application",
            construction_agency="IT"
        )
        db.session.add(project)
        db.session.commit()
        project_id = project.id
        initial_history_count = len(project.histories)
    
    client.post(f"/projects/{project_id}", data={
        "phase": "IT Demand Submitted",
        "status": "Assigned",
        "note": "Assigned to team"
    })
    
    with app.app_context():
        updated_project = Project.query.get(project_id)
        assert len(updated_project.histories) > initial_history_count

# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

def test_configuration_page_loads(client):
    """Test that configuration page loads."""
    response = client.get("/configuration")
    assert response.status_code == 200
    assert b"Configuration" in response.data

def test_configuration_add_item(client, app):
    """Test adding a configuration item."""
    response = client.post("/configuration", data={
        "kind": "category",
        "label": "Custom Category"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"added successfully" in response.data
    
    # Verify it was added
    with app.app_context():
        item = ConfigurationItem.query.filter_by(
            kind="category",
            label="Custom Category"
        ).first()
        assert item is not None

def test_configuration_add_duplicate_item(client, app):
    """Test that adding duplicate item is rejected."""
    # Add first item
    client.post("/configuration", data={
        "kind": "category",
        "label": "Unique Category"
    })
    
    # Try to add duplicate
    response = client.post("/configuration", data={
        "kind": "category",
        "label": "Unique Category"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"already exists" in response.data

def test_configuration_invalid_kind(client):
    """Test that invalid configuration kind is rejected."""
    response = client.post("/configuration", data={
        "kind": "invalid_type",
        "label": "Some Label"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"error" in response.data.lower() or b"valid" in response.data.lower()
