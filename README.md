# PMO Pulse

PMO Pulse is a project-intake and portfolio-monitoring tool for HR Information Systems teams. It tracks work at the project phase level—from intake and PMO review through DSD, IT demand, build, UAT, deployment, and closure.

## Features
- Intake with generated request references
- PMO decision, assignment and phase/status history
- Configurable categories, types, agencies and impacted systems
- Resource assignment; IT demand, estimates and document-link fields
- Dashboard: portfolio by customer/status, category/status mix, YTD totals, and received-versus-completed counts by period
- SQLite default with MySQL configuration through `DATABASE_URL`

## Run
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app app run --debug
```

Open http://127.0.0.1:5000. Run `pytest` for tests.

## Documentation
- [Requirements specification](docs/requirements-specification.md)
- [Development plan](docs/development-plan.md)
- [Architecture and data model](docs/architecture-and-data-model.md)
- [User guide](docs/user-guide.md)
- [Test scenarios](docs/test-scenarios.md)

Before production, add enterprise SSO/RBAC, SMTP notifications, managed document storage, database migrations, backups and monitoring.
