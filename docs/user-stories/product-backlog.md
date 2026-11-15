# CivicWatch — Product Backlog

## 1. Project Overview

CivicWatch is a civic complaint management platform. Citizens can report public issues, while authorities can review, assign, track, and resolve complaints.

## 2. Epics

| Epic | Name | Description |
|---|---|---|
| E1 | Auth and Roles | Citizen, officer and admin authentication and access |
| E2 | Complaint Reporting | Creating and submitting civic complaints |
| E3 | Complaint Tracking | Reviewing, assigning and tracking complaint status |
| E4 | Authority Management | Department and officer management |
| E5 | Geospatial Map | Location-based complaint visualization |
| E6 | Analytics and Reports | Complaint statistics, hotspots and reports |
| E7 | Quality and DevOps | Testing, CI/CD, documentation and release quality |

## 3. Complaint Status Workflow

`Submitted → Under Review → Assigned → In Progress → Resolved`

A complaint may also move to `Rejected` after review.

## 4. Product Backlog and User Stories

Each story includes two acceptance criteria in Given/When/Then format.

### Sprint 1 — Citizen Reporting Foundation

#### CW-103 — Create Complaint API
- **Epic:** E2 — Complaint Reporting
- **User Story:** As a citizen, I want to submit a complaint through an API so that my civic issue can be recorded.
- **Priority:** Must
- **Story Points:** 2
- **Sprint:** 1
- **Acceptance Criteria:**
  1. Given an authenticated citizen and valid complaint details, when the citizen submits the complaint, then the API creates it with status `Submitted` and priority `Medium`.
  2. Given invalid or missing complaint details, when the citizen submits the request, then the API returns a validation error.

#### CW-104 — Complaint Form
- **Epic:** E2 — Complaint Reporting
- **User Story:** As a citizen, I want a complaint submission form so that I can report a civic issue through the application.
- **Priority:** Must
- **Story Points:** 3
- **Sprint:** 1
- **Acceptance Criteria:**
  1. Given the complaint form is open, when the citizen enters valid title, description, category and location details, then the form allows submission.
  2. Given a complaint is submitted successfully, when the API responds successfully, then the application displays a confirmation message.

#### CW-204 — Base Database Migration
- **Epic:** E7 — Quality and DevOps
- **User Story:** As a developer, I want a base database migration so that the application's core entities can be created consistently.
- **Priority:** Must
- **Story Points:** 2
- **Sprint:** 1
- **Acceptance Criteria:**
  1. Given a fresh database, when the base migration runs, then the users, categories, departments and complaints tables are created.
  2. Given the migration has completed, when the database schema is inspected, then the expected tables and relationships exist.

#### CW-205 — JWT Authentication API
- **Epic:** E1 — Auth and Roles
- **User Story:** As a user, I want to register and log in securely so that I can access the platform using my account.
- **Priority:** Must
- **Story Points:** 2
- **Sprint:** 1
- **Acceptance Criteria:**
  1. Given valid registration details, when a user registers, then the API creates the account with a securely hashed password.
  2. Given valid login credentials, when the user logs in, then the API returns a JWT token; invalid credentials must be rejected.

#### CW-206 — Login and Register UI
- **Epic:** E1 — Auth and Roles
- **User Story:** As a user, I want login and registration screens so that I can access CivicWatch using the frontend.
- **Priority:** Must
- **Story Points:** 1
- **Sprint:** 1
- **Acceptance Criteria:**
  1. Given an unauthenticated user, when the user opens the authentication screen, then login and registration options are displayed.
  2. Given valid credentials, when the user submits the form, then the frontend communicates with the authentication API and handles the response.

#### CW-301 — Complaint Status State Machine
- **Epic:** E3 — Complaint Tracking
- **User Story:** As an authority officer, I want complaints to follow valid status transitions so that complaint progress remains consistent.
- **Priority:** Must
- **Story Points:** 3
- **Sprint:** 1
- **Acceptance Criteria:**
  1. Given a complaint in a valid current state, when an authorized transition is requested, then the complaint status changes to the permitted next state.
  2. Given an invalid status transition, when the transition is requested, then the system rejects it without changing the complaint.

#### CW-302 — Authority Module Scaffold
- **Epic:** E4 — Authority Management
- **User Story:** As a developer, I want an authority module scaffold so that authority-related functionality can be developed separately.
- **Priority:** Must
- **Story Points:** 2
- **Sprint:** 1
- **Acceptance Criteria:**
  1. Given the backend application starts, when the authority module is loaded, then its basic structure is available without breaking the application.
  2. Given an authority endpoint is registered, when it is requested, then the application returns the expected response.

#### CW-401 — Geo Utilities
- **Epic:** E5 — Geospatial Map
- **User Story:** As a developer, I want reusable geographic utilities so that location data can be validated and processed consistently.
- **Priority:** Must
- **Story Points:** 1
- **Sprint:** 1
- **Acceptance Criteria:**
  1. Given valid latitude and longitude values, when the geographic utility validates them, then the coordinates are accepted.
  2. Given coordinates outside valid geographic ranges, when validation runs, then the utility rejects them.

#### CW-402 — Hotspot Algorithm
- **Epic:** E6 — Analytics and Reports
- **User Story:** As an administrator, I want complaint hotspots to be identified so that areas with repeated civic issues can be prioritized.
- **Priority:** Should
- **Story Points:** 3
- **Sprint:** 1
- **Acceptance Criteria:**
  1. Given a collection of complaints with valid coordinates, when hotspot analysis runs, then nearby complaint concentrations are identified.
  2. Given there are no eligible complaints, when hotspot analysis runs, then the system returns an empty result without failing.

#### CW-403 — Leaflet Map Scaffold
- **Epic:** E5 — Geospatial Map
- **User Story:** As a citizen, I want a basic map interface so that complaint locations can be visualized in the application.
- **Priority:** Should
- **Story Points:** 1
- **Sprint:** 1
- **Acceptance Criteria:**
  1. Given the map page is opened, when the map component loads, then a Leaflet map is displayed.
  2. Given the map component receives valid location data, when it renders, then it can display the supplied location.

### Sprint 2 — Tracking and Authority Features

#### CW-105 — Photo Upload
- **Epic:** E2 — Complaint Reporting
- **User Story:** As a citizen, I want to attach a photo to my complaint so that I can provide visual evidence of the issue.
- **Priority:** Should
- **Story Points:** 2
- **Sprint:** 2
- **Acceptance Criteria:**
  1. Given a supported image file, when the citizen uploads it with a complaint, then the image is stored and associated with the complaint.
  2. Given an unsupported or oversized file, when the citizen uploads it, then the system rejects the file with an appropriate error.

#### CW-106 — Location Pin-Drop
- **Epic:** E2 — Complaint Reporting
- **User Story:** As a citizen, I want to select a complaint location on a map so that authorities can identify the issue's position.
- **Priority:** Should
- **Story Points:** 1
- **Sprint:** 2
- **Acceptance Criteria:**
  1. Given the location picker is open, when the citizen selects a point on the map, then its coordinates are captured.
  2. Given the citizen confirms the selected location, when the complaint is submitted, then the selected coordinates are included.

#### CW-107 — Tracking API and UI
- **Epic:** E3 — Complaint Tracking
- **User Story:** As a citizen, I want to track my complaint so that I can see its current progress.
- **Priority:** Must
- **Story Points:** 2
- **Sprint:** 2
- **Acceptance Criteria:**
  1. Given a citizen owns a complaint, when the citizen requests its tracking details, then the system returns its current status.
  2. Given a citizen requests another user's complaint, when access is checked, then the system denies unauthorized access.

#### CW-208 — RBAC and Route Guards
- **Epic:** E1 — Auth and Roles
- **User Story:** As an administrator, I want role-based access control so that users can access only the features permitted for their roles.
- **Priority:** Must
- **Story Points:** 2
- **Sprint:** 2
- **Acceptance Criteria:**
  1. Given a user has a defined role, when the user accesses a protected route, then access is allowed only if the role is authorized.
  2. Given an unauthenticated or unauthorized user, when the user accesses a protected route, then access is denied or redirected.

#### CW-209 — Admin API for Departments and Officers
- **Epic:** E4 — Authority Management
- **User Story:** As an administrator, I want to manage departments and officers through an API so that complaints can be handled by the appropriate teams.
- **Priority:** Must
- **Story Points:** 2
- **Sprint:** 2
- **Acceptance Criteria:**
  1. Given an authorized administrator, when a valid department or officer is created, then the API stores the record.
  2. Given a user without administrator permission, when a management request is made, then the API rejects it.

#### CW-303 — Complaint Review API
- **Epic:** E3 — Complaint Tracking
- **User Story:** As an authority officer, I want to review submitted complaints so that valid complaints can proceed for action.
- **Priority:** Must
- **Story Points:** 2
- **Sprint:** 2
- **Acceptance Criteria:**
  1. Given a complaint is submitted, when an authorized officer reviews it, then its review decision is recorded.
  2. Given a complaint does not exist, when a review is requested, then the API returns a not-found response.

#### CW-304 — Assign Complaint and Set Priority
- **Epic:** E3 — Complaint Tracking
- **User Story:** As an authority officer, I want to assign complaints and set their priority so that work can be distributed effectively.
- **Priority:** Must
- **Story Points:** 2
- **Sprint:** 2
- **Acceptance Criteria:**
  1. Given a valid complaint and department, when an authorized officer assigns the complaint, then the department assignment is saved.
  2. Given an authorized officer changes complaint priority, when the update succeeds, then the new priority is stored and returned.

#### CW-305 — Authority Dashboard
- **Epic:** E4 — Authority Management
- **User Story:** As an authority officer, I want a dashboard of assigned complaints so that I can manage my department's workload.
- **Priority:** Should
- **Story Points:** 1
- **Sprint:** 2
- **Acceptance Criteria:**
  1. Given an authenticated officer, when the dashboard loads, then complaints assigned to the officer's department are displayed.
  2. Given there are no assigned complaints, when the dashboard loads, then an appropriate empty state is displayed.

#### CW-404 — PostGIS Migration
- **Epic:** E5 — Geospatial Map
- **User Story:** As a developer, I want geospatial database support so that location-based queries can be performed efficiently.
- **Priority:** Should
- **Story Points:** 1
- **Sprint:** 2
- **Acceptance Criteria:**
  1. Given a supported PostgreSQL database, when the geospatial migration runs, then the required PostGIS support is enabled.
  2. Given the migration has already run, when migrations are checked again, then the database remains consistent.

#### CW-405 — Nearby and Bounding-Box APIs
- **Epic:** E5 — Geospatial Map
- **User Story:** As a citizen, I want to find complaints near a location or within a map area so that I can understand nearby civic issues.
- **Priority:** Should
- **Story Points:** 2
- **Sprint:** 2
- **Acceptance Criteria:**
  1. Given valid coordinates and a search radius, when the nearby API is requested, then complaints within the radius are returned.
  2. Given valid bounding-box coordinates, when the bounding-box API is requested, then only complaints inside that area are returned.

#### CW-406 — Real Markers on Map
- **Epic:** E5 — Geospatial Map
- **User Story:** As a citizen, I want real complaint markers on the map so that I can see reported issues geographically.
- **Priority:** Should
- **Story Points:** 1
- **Sprint:** 2
- **Acceptance Criteria:**
  1. Given the map receives complaint records with coordinates, when it renders, then a marker is displayed for each valid location.
  2. Given a complaint has missing or invalid coordinates, when markers are rendered, then that complaint does not create an invalid marker.

### Sprint 3 — Citizen Experience and Insights

#### CW-108 — Feedback and Reopen Complaint
- **Epic:** E3 — Complaint Tracking
- **User Story:** As a citizen, I want to provide feedback and reopen an unresolved complaint so that the authority can address incomplete work.
- **Priority:** Could
- **Story Points:** 3
- **Sprint:** 3
- **Acceptance Criteria:**
  1. Given a complaint is resolved, when its owner submits feedback, then the feedback is associated with the complaint.
  2. Given a complaint meets the reopening rules, when its owner requests reopening, then the complaint returns to the permitted review state.

#### CW-109 — My Complaints Filters
- **Epic:** E3 — Complaint Tracking
- **User Story:** As a citizen, I want to filter my complaints so that I can quickly find a particular report.
- **Priority:** Should
- **Story Points:** 2
- **Sprint:** 3
- **Acceptance Criteria:**
  1. Given a citizen has multiple complaints, when a status filter is selected, then only complaints matching that status are displayed.
  2. Given a citizen changes or clears the filter, when the list refreshes, then the displayed complaints reflect the selected filter.

#### CW-215 — Admin UI
- **Epic:** E1 — Auth and Roles
- **User Story:** As an administrator, I want an administration interface so that I can manage platform users and settings.
- **Priority:** Should
- **Story Points:** 2
- **Sprint:** 3
- **Acceptance Criteria:**
  1. Given an authenticated administrator, when the admin interface opens, then the available administration options are displayed.
  2. Given a non-admin user, when the user attempts to access the admin interface, then access is blocked.

#### CW-210 — Pagination and Indexes
- **Epic:** E7 — Quality and DevOps
- **User Story:** As a developer, I want pagination and database indexes so that complaint queries remain efficient as data grows.
- **Priority:** Should
- **Story Points:** 2
- **Sprint:** 3
- **Acceptance Criteria:**
  1. Given a large complaint collection, when the API is requested with page and page-size parameters, then only the requested page is returned.
  2. Given the required indexes are applied, when common complaint queries execute, then the database can use those indexes.

#### CW-306 — Complaint Escalation
- **Epic:** E3 — Complaint Tracking
- **User Story:** As an administrator, I want overdue complaints to be escalated so that delayed issues receive attention.
- **Priority:** Should
- **Story Points:** 2
- **Sprint:** 3
- **Acceptance Criteria:**
  1. Given a complaint exceeds its configured resolution threshold, when escalation runs, then the complaint is marked for escalation.
  2. Given a complaint is not overdue, when escalation runs, then its escalation state remains unchanged.

#### CW-307 — Notifications (Optional)
- **Epic:** E3 — Complaint Tracking
- **User Story:** As a citizen, I want notifications about complaint updates so that I remain informed about progress.
- **Priority:** Could
- **Story Points:** 2
- **Sprint:** 3
- **Acceptance Criteria:**
  1. Given a complaint status changes, when notification processing runs, then the complaint owner receives an update.
  2. Given notification delivery fails, when the system handles the failure, then the complaint update itself remains saved.

#### CW-308 — Dashboard Sorting
- **Epic:** E4 — Authority Management
- **User Story:** As an authority officer, I want to sort dashboard complaints so that I can prioritize the work that needs attention.
- **Priority:** Should
- **Story Points:** 1
- **Sprint:** 3
- **Acceptance Criteria:**
  1. Given the dashboard displays complaints, when the officer selects a sorting option, then the list is ordered accordingly.
  2. Given the officer changes the sorting direction, when the list refreshes, then the order is reversed.

#### CW-407 — Marker Clustering
- **Epic:** E5 — Geospatial Map
- **User Story:** As a citizen, I want nearby map markers grouped together so that dense areas remain easy to explore.
- **Priority:** Should
- **Story Points:** 1
- **Sprint:** 3
- **Acceptance Criteria:**
  1. Given many complaint markers are close together, when the map zooms out, then nearby markers are grouped into clusters.
  2. Given the user zooms into a cluster, when the map updates, then individual markers become visible.

#### CW-408 — Map Filters
- **Epic:** E5 — Geospatial Map
- **User Story:** As a citizen, I want to filter map complaints so that I can focus on relevant issues.
- **Priority:** Should
- **Story Points:** 1
- **Sprint:** 3
- **Acceptance Criteria:**
  1. Given complaint markers are displayed, when a category or status filter is selected, then only matching markers remain visible.
  2. Given the user clears the filters, when the map refreshes, then all eligible markers are displayed again.

#### CW-409 — Heatmap
- **Epic:** E6 — Analytics and Reports
- **User Story:** As an administrator, I want a complaint heatmap so that high-density problem areas can be identified.
- **Priority:** Should
- **Story Points:** 2
- **Sprint:** 3
- **Acceptance Criteria:**
  1. Given complaint locations are available, when the heatmap loads, then areas with higher complaint density are visually emphasized.
  2. Given no valid complaint locations are available, when the heatmap loads, then the map displays an appropriate empty state.

### Sprint 4 — Quality, Release and Reporting

#### CW-110 — Citizen End-to-End Tests
- **Epic:** E7 — Quality and DevOps
- **User Story:** As a developer, I want end-to-end tests for citizen workflows so that critical user journeys are verified.
- **Priority:** Must
- **Story Points:** 2
- **Sprint:** 4
- **Acceptance Criteria:**
  1. Given a citizen uses the application, when the registration, login and complaint submission journey is executed, then the expected workflow completes.
  2. Given an invalid citizen workflow input, when the end-to-end test runs, then the expected validation or error behavior is verified.

#### CW-111 — Citizen Workflow Refactor
- **Epic:** E7 — Quality and DevOps
- **User Story:** As a developer, I want citizen workflow code refactored so that it remains maintainable and understandable.
- **Priority:** Should
- **Story Points:** 1
- **Sprint:** 4
- **Acceptance Criteria:**
  1. Given existing citizen workflow code, when refactoring is completed, then behavior remains unchanged.
  2. Given the refactored code, when the relevant test suite runs, then all tests pass.

#### CW-112 — Product Owner Report
- **Epic:** E6 — Analytics and Reports
- **User Story:** As a product owner, I want a project report so that I can understand delivered functionality and remaining work.
- **Priority:** Should
- **Story Points:** 1
- **Sprint:** 4
- **Acceptance Criteria:**
  1. Given sprint results are available, when the report is prepared, then completed and pending work is summarized.
  2. Given the report is reviewed, when the product owner checks it, then key progress and outstanding risks are visible.

#### CW-211 — Security Hardening
- **Epic:** E1 — Auth and Roles
- **User Story:** As an administrator, I want the platform security hardened so that accounts and complaint data are protected.
- **Priority:** Must
- **Story Points:** 2
- **Sprint:** 4
- **Acceptance Criteria:**
  1. Given authentication and authorization endpoints are used, when security checks run, then unauthorized access is prevented.
  2. Given user input is submitted, when validation and security checks run, then unsafe input is handled safely.

#### CW-213 — README and OpenAPI Documentation
- **Epic:** E7 — Quality and DevOps
- **User Story:** As a developer, I want project and API documentation so that contributors can set up and use the application.
- **Priority:** Should
- **Story Points:** 1
- **Sprint:** 4
- **Acceptance Criteria:**
  1. Given a new contributor opens the README, when they follow the setup instructions, then they can configure and run the project.
  2. Given API endpoints are available, when the OpenAPI documentation is opened, then endpoint details and schemas are visible.

#### CW-214 — Release v1.0.0
- **Epic:** E7 — Quality and DevOps
- **User Story:** As a product owner, I want a versioned release so that the first stable platform version can be distributed.
- **Priority:** Must
- **Story Points:** 1
- **Sprint:** 4
- **Acceptance Criteria:**
  1. Given all release checks pass, when version 1.0.0 is prepared, then the release is tagged with the correct version.
  2. Given the release is published, when users view release notes, then the included features and known limitations are documented.

#### CW-310 — Authority End-to-End Tests
- **Epic:** E7 — Quality and DevOps
- **User Story:** As a developer, I want end-to-end tests for authority workflows so that complaint review and assignment are verified.
- **Priority:** Must
- **Story Points:** 1
- **Sprint:** 4
- **Acceptance Criteria:**
  1. Given an authorized officer, when the review and assignment workflow is executed, then the complaint is processed successfully.
  2. Given an unauthorized user, when an authority workflow is attempted, then access is denied.

#### CW-311 — Authority Module Refactor
- **Epic:** E7 — Quality and DevOps
- **User Story:** As a developer, I want authority module code refactored so that it remains maintainable.
- **Priority:** Should
- **Story Points:** 2
- **Sprint:** 4
- **Acceptance Criteria:**
  1. Given existing authority functionality, when refactoring is completed, then existing behavior is preserved.
  2. Given the refactored authority module, when its tests run, then all relevant tests pass.

#### CW-312 — Code-Smell Log
- **Epic:** E7 — Quality and DevOps
- **User Story:** As a developer, I want code smells documented so that technical debt can be tracked and addressed.
- **Priority:** Could
- **Story Points:** 1
- **Sprint:** 4
- **Acceptance Criteria:**
  1. Given a code quality review is performed, when code smells are identified, then each finding is documented with its location and impact.
  2. Given the code-smell log is updated, when the team reviews it, then findings can be prioritized for future work.

#### CW-411 — Hotspot API and Map Zones
- **Epic:** E6 — Analytics and Reports
- **User Story:** As an administrator, I want hotspot API results and map zones so that high-complaint areas can be acted upon.
- **Priority:** Should
- **Story Points:** 2
- **Sprint:** 4
- **Acceptance Criteria:**
  1. Given sufficient complaint location data, when the hotspot API is requested, then hotspot areas are returned.
  2. Given hotspot areas are returned, when the map displays them, then the relevant zones are visually distinguishable.

#### CW-412 — Reports and Charts
- **Epic:** E6 — Analytics and Reports
- **User Story:** As an administrator, I want complaint reports and charts so that I can understand platform performance and trends.
- **Priority:** Should
- **Story Points:** 2
- **Sprint:** 4
- **Acceptance Criteria:**
  1. Given complaint records are available, when a report is generated, then complaint totals and status summaries are included.
  2. Given report data is available, when charts are displayed, then the charts represent the underlying complaint statistics.

## 5. Scope and Prioritization

- Must: Essential functionality required for a usable and secure platform.
- Should: Important functionality that improves the platform but can be scheduled after Must items.
- Could: Useful enhancements that may be deferred if time is limited.

If the project falls behind schedule, cut scope in this order:
1. Notifications (CW-307).
2. Report charts UI (CW-412).
3. Feedback and reopen (CW-108).

Hotspot analysis and heatmap functionality remain in scope.

## 6. Sprint Summary

| Sprint | Focus | Story Count |
|---|---|---:|
| Sprint 1 | Citizen Reporting Foundation | 10 |
| Sprint 2 | Tracking and Authority Features | 11 |
| Sprint 3 | Citizen Experience and Insights | 10 |
| Sprint 4 | Quality, Release and Reporting | 11 |
| **Total** | **All Epics** | **42** |

## 7. Definition of Done

A user story is considered Done when:
- The implementation meets its acceptance criteria.
- Relevant automated tests pass.
- Code follows the project's agreed style and structure.
- No unrelated or out-of-scope files are modified.
- The work is committed to its assigned feature branch.
