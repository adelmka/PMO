# Test Scenarios

| ID | Scenario | Expected result |
| --- | --- | --- |
| T01 | Submit a complete request | Unique reference, Under Review/PMO Review, history record |
| T02 | Omit a required intake field | Validation error; no project saved |
| T03 | Reject at PMO review | Reason and history persist |
| T04 | Assign team and leads | Assignments persist |
| T05 | Progress lifecycle | Current phase/status and history agree |
| T06 | Mark Delivered | Completion timestamp and dashboard completion count update |
| T07 | Add configuration item | Available in the appropriate selectable list |
| T08 | Switch month/quarter/year | KPI boundary changes correctly |
| T09 | Restart pilot | SQLite projects and histories persist |
| T10 | Run pytest | Dashboard and reference-generation tests pass |

Manual UAT should validate actual role permissions, email, SSO, document-link access, backup/restore and reconciliation against the PMO register.
