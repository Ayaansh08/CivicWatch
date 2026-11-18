# Authority Module Exploratory Testing Notes (CW-309)

**Tester:** Udit (M3, Authority Management)  
**Date:** November 2026  
**Target:** CivicWatch Authority Management Feature (Sprint 2 - Sprint 4)

---

## Charter 1: Complaint Review & Assignment Workflow

**Objective:** Verify that an officer can review submitted complaints and assign them to departments with proper priority levels.

| Test Scenario | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| Review submitted complaint | Open submitted complaint, click Review | Status transitions to 'Under Review'; history logged | TODO | TODO |
| Assign department and priority | Select department and priority level, submit assignment | Status transitions to 'Assigned'; department and priority saved | TODO | TODO |
| Invalid department ID | Attempt assignment with non-existent department ID | Returns HTTP 404 with error message | TODO | TODO |
| Citizen access blocked | Attempt review/assign using citizen JWT credentials | Returns HTTP 403 Forbidden | TODO | TODO |

---

## Charter 2: Status Lifecycle Transitions

**Objective:** Validate that status transitions strictly follow the allowable workflow paths defined in CW-301.

| Test Scenario | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| Assigned to In Progress | Submit status change to 'In Progress' | Transitions to 'In Progress'; timestamp updated | TODO | TODO |
| In Progress to Resolved | Submit status change to 'Resolved' with note | Transitions to 'Resolved'; final status reached | TODO | TODO |
| Illegal direct skip | Attempt jumping directly from 'Submitted' to 'Resolved' | Returns HTTP 400 Invalid transition | TODO | TODO |
| Status change after Resolved | Attempt modifying complaint after 'Resolved' status | Returns HTTP 400 Invalid transition | TODO | TODO |

---

## Charter 3: Dashboard Filtering & Auto-Escalation

**Objective:** Verify filtering, sorting, and overdue auto-escalation functionality on the authority dashboard.

| Test Scenario | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| Filter by status | Select 'Under Review' in status dropdown | Only complaints with 'Under Review' status are displayed | TODO | TODO |
| Sort by priority | Select 'By priority' in sort dropdown | High/Critical complaints appear before Medium/Low | TODO | TODO |
| Sort by age | Select 'Oldest first' in sort dropdown | Oldest complaints appear first | TODO | TODO |
| Auto-escalate overdue | Click 'Escalate overdue' button | Overdue unresolved complaints (>48h) escalated one priority level | TODO | TODO |
