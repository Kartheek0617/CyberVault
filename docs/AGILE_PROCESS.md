# CyberVault Agile & Scrum Development Process

## 1. Overview
The CyberVault project integrates the Agile (Scrum) workflow directly within the Secure Software Development Lifecycle (SSDLC). Security checks (Threat Modeling, automated CI Security runs) are embedded aggressively within the Sprints.

## 2. Jira Artifacts Location
All detailed planning records, backlogs, and sprint metrics are maintained as Jira-ready project artifacts within the `docs/jira/` directory:
- `PRODUCT_BACKLOG.md`
- `EPICS.md`
- `USER_STORIES.md`
- `SPRINT_PLAN.md`
- `SPRINT_BACKLOG.md`
- `ACCEPTANCE_CRITERIA.md`
- `DEFINITION_OF_DONE.md`
- `SPRINT_REVIEW.md`
- `RETROSPECTIVE.md`
- `JIRA_SETUP_GUIDE.md`

*(Note: These represent reconstructive Jira-ready project artifacts for academic/compliance auditing).*

## 3. Agile Metrics Summary
- **Velocity:** Evaluated historically at an average of 11.75 Story Points per sprint.
- **Burndown Rate:** Consistent tracking against an initial 47-point project baseline.
- **Defects Carried Over:** Historical iterations demonstrated a carry-over of 3 IDOR and MIME-related defects resolved in a subsequent Sprint (documented in `RETROSPECTIVE.md`).

## 4. Kanban & WIP Control
- **Workflow Columns:** BACKLOG → READY → IN PROGRESS → CODE REVIEW → SECURITY TESTING → DONE
- **WIP Limit:** Enforced at **3** items in the `IN PROGRESS` column.
- **WIP Rationale:** Prevents unsafe context switching, minimizing exposed attack surfaces from partially implemented logic, ensuring security features are fully resolved before moving on.
