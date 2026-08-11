# PMO Pulse Requirements Specification

## Scope
PMO Pulse is a portfolio register for HRIS IT project requests. It tracks the current phase and status of each project rather than detailed tasks or sprint deliverables.

## Roles
| Role | Responsibility |
| --- | --- |
| Requester | Submit request and receive decision |
| PMO analyst | Review, accept/reject, assign team, manage portfolio |
| Group lead | Assign project lead |
| Project lead | Manage requirements, IT demand, delivery/UAT/closure updates |
| Executive | Dashboard read-only view |
| Administrator | Manage lists and resources |

## Functional requirements
1. Capture requester, organization, title, description, attachment/document link, category, type, construction agency, and impacted systems.
2. Generate a unique reference and acknowledgement event.
3. Record PMO accept/reject decision and reason.
4. Assign PMO analyst, team, group lead, and project lead.
5. Track PMO Review, SME Review, DSD, IT Demand, Estimation, Build, UAT, Deployment plus the requested project statuses.
6. Persist IT Demand number, cost/duration estimates, notes, and document links.
7. Keep categories, types, agencies and impacted systems configurable—not hard-coded.
8. Dashboard projects by customer/status; totals received/completed by month, quarter, and year; YTD; category and status mix.
9. Store timestamped phase/status history.

## Non-functional requirements
Python OOP service/model separation; relational database; responsive browser GUI; SQLite pilot support and MySQL production configuration. A production release must add SSO/RBAC, email, document-storage integration, backups, encryption, data-retention, accessibility and operational monitoring.
