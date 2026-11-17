# Product Owner Sprint Report — Citizen Reporting

## 1. Overview and Sprint Goals
This report documents the verification, test evidence, and acceptance criteria review for all Citizen Reporting user stories (CW-103 through CW-111) developed by Ayan (M1, Citizen Reporting).

### Sprint Goal Status
- **Sprint 1 (Foundation):** Completed. Citizen complaint API and submission form created.
- **Sprint 2 (Tracking & Evidence):** Completed. Photo upload, Leaflet location pin-drop, status history logging, and My Complaints timeline tracking delivered.
- **Sprint 3 (Experience & Insights):** Completed. Citizen 1-5 star resolution feedback, complaint reopening, and status/category filters delivered.
- **Sprint 4 (Quality & Review):** Completed. End-to-end integration tests written, component refactoring applied, and this report compiled.

---

## 2. User Stories and Acceptance Review

| Story ID | Description | Acceptance Criteria | Test Evidence | PO Decision |
|---|---|---|---|---|
| **CW-103** | Create Complaint API | 1. Given authenticated citizen, when valid complaint submitted, then status `Submitted` and priority `Medium`.<br>2. Given invalid/missing details, returns validation error (422/400). | `backend/tests/citizen/test_complaints_api.py` (8 tests passed) | TODO: Product Owner decides at sprint review |
| **CW-104** | Complaint Form | 1. Given form open, allows input for title, description, category, location.<br>2. On valid submission with API success, displays confirmation message. | `frontend/src/__tests__/citizen/complaintForm.test.jsx` (5 tests passed) | TODO: Product Owner decides at sprint review |
| **CW-105** | Photo Upload | 1. Given valid image (.jpg, .jpeg, .png <= 2 MB), saves to uploads and links to complaint.<br>2. Unsupported type or oversized file rejected with 400. | `backend/tests/citizen/test_photo_upload.py` (5 tests passed)<br>`frontend/src/__tests__/citizen/photoPicker.test.jsx` (3 tests passed) | TODO: Product Owner decides at sprint review |
| **CW-106** | Location Pin-Drop | 1. Given location picker, citizen can drop pin on map or use browser geolocation.<br>2. Captured coordinates included upon complaint submission. | `frontend/src/__tests__/citizen/locationPicker.test.jsx` (4 tests passed) | TODO: Product Owner decides at sprint review |
| **CW-107** | Tracking & History | 1. Given citizen owns complaints, /mine returns their reports and status history chronological timeline.<br>2. Unauthorized user cannot access other's complaint history (403). | `backend/tests/citizen/test_tracking.py` (6 tests passed)<br>`frontend/src/__tests__/citizen/myComplaints.test.jsx` (4 tests passed) | TODO: Product Owner decides at sprint review |
| **CW-108** | Feedback and Reopen | 1. Given resolved complaint, owner can submit 1-5 rating and comment.<br>2. Given resolved complaint, owner can reopen with reason, resetting status to `Under Review`. | `backend/tests/citizen/test_feedback_reopen.py` (6 tests passed)<br>`frontend/src/__tests__/citizen/feedbackPanel.test.jsx` (3 tests passed) | TODO: Product Owner decides at sprint review |
| **CW-109** | My Complaints Filters | 1. Given citizen has multiple complaints, filtering by status or category narrows list.<br>2. Citizen can clear filters or see empty filter message. | `backend/tests/citizen/test_filters.py` (3 tests passed)<br>`frontend/src/__tests__/citizen/complaintFilters.test.jsx` (1 test passed) | TODO: Product Owner decides at sprint review |
| **CW-110** | Citizen End-to-End | 1. Full citizen flow: register, login, report complaint, upload photo, view in mine, rate, and reopen.<br>2. Verified cross-user isolation and access controls. | `backend/tests/citizen/test_e2e_citizen_flow.py` (2 tests passed)<br>`frontend/src/__tests__/citizen/citizenFlow.test.jsx` (1 test passed) | TODO: Product Owner decides at sprint review |
| **CW-111** | Citizen Refactor | 1. Extracted shared FormField, StatusBadge, unified request helper in api.js.<br>2. Backend extracted get_owned_complaint_or_error helper; 0 regressions. | Backend suite (30 passed), Frontend suite (29 passed) | TODO: Product Owner decides at sprint review |

---

## 3. Scope-Cut Status
- All committed stories CW-103 through CW-111 were delivered in full.
- No citizen scope items were cut or deferred.

---

## 4. Identified Technical Debt & Risks
1. **JWT Expiration & Refresh Flow:** Frontend stores token in `localStorage`; if expired, token refresh mechanism will be required in upcoming milestones.
2. **PostgreSQL/PostGIS Deployment:** In-memory SQLite and local SQLite environments tested thoroughly; staging migration to PostgreSQL requires live database credentials.
