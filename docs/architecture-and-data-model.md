# Architecture and Data Model

```
Browser → Flask routes/templates → ProjectService / DashboardService → SQLAlchemy → SQLite or MySQL
```

## Entities
- **Customer**: organization identifier, name and contact.
- **Project**: lifecycle record, classification, owner assignments, estimates, evidence links and dates.
- **Resource**: assignable PMO/group/project team member.
- **ConfigurationItem**: configurable category, type, agency or impacted system.
- **StatusHistory**: timestamped lifecycle audit entry.

```
Intake → PMO Review → SME Review → DSD → IT Demand → Estimation → Build → UAT → Deployment → Delivered
                         ↘ Rejected / On Hold / Cancelled
```

The Project table holds the current reporting state; StatusHistory preserves changes. Production architecture should terminate SSO before the web app, use managed MySQL, external document storage and SMTP/event integrations.
