# Authority Code Smell & Refactoring Log (CW-311, CW-312)

**Author:** Udit (M3, Authority Management)  
**Date:** November 2026  
**Module:** `backend/app/authority/`, `frontend/src/features/authority/`

---

## 1. Code Smells Identified & Refactorings Applied

| Code Smell | Location | Description | Refactoring Action Taken |
|---|---|---|---|
| **Duplicate Transition Logic** | `backend/app/authority/router.py` | Repeated status validation, update, and history recording across `/review` and `/status` endpoints | Extracted reusable `change_status(db, complaint, new_status, user, note)` helper function |
| **Repeated 404 Checks** | `backend/app/authority/router.py` | Redundant DB query and 404 raise pattern in every complaint-specific endpoint | Extracted `get_complaint_or_404(complaint_id, db)` helper function |
| **Large Monolithic Component** | `frontend/src/features/authority/AuthorityDashboard.jsx` | Dashboard mixed filter state, data fetching, table rendering, and detail controls in a single 210-line component | Split out custom hook `useComplaints.js` for data/filters and `ComplaintsTable.jsx` for presentation |
| **Magic Numbers & Strings** | `backend/app/authority/escalation.py`, `backend/app/authority/router.py` | Hardcoded overdue time window (`48`) and priority literals | Named constant `OVERDUE_HOURS = 48` and tuple `VALID_PRIORITIES = ("Low", "Medium", "High", "Critical")` |
| **Unused Imports** | `backend/app/authority/router.py`, `backend/tests/authority/test_escalation.py` | Unused `fastapi.status` and `pytest` imports causing lint noise | Cleaned up unused imports to keep flake8 completely zero-warning |

---

## 2. Test Execution Summary

Real test run results verified after refactoring:

### Backend Test Results (pytest)
- **Total Backend Tests:** 123 passed
- **Authority Unit & Integration Tests:** 32 passed
  - `backend/tests/authority/test_workflow.py` (Sprint 1)
  - `backend/tests/authority/test_review_api.py` (Sprint 2 - CW-303)
  - `backend/tests/authority/test_assign_api.py` (Sprint 2 - CW-304)
  - `backend/tests/authority/test_status_api.py` (Sprint 2 - CW-305)
  - `backend/tests/authority/test_escalation.py` (Sprint 3 - CW-306)
  - `backend/tests/authority/test_sorting.py` (Sprint 3 - CW-308)
  - `backend/tests/authority/test_e2e_authority_flow.py` (Sprint 4 - CW-310)
- **Platform, Citizen, & Geo Tests:** 91 passed
- **Flake8 Lint:** Clean (0 errors, 0 warnings)

### Frontend Test Results (Jest)
- **Total Frontend Tests:** 37 passed
- **Authority Frontend Tests:** 8 passed
  - `frontend/src/__tests__/authority/assignForm.test.jsx` (2 tests)
  - `frontend/src/__tests__/authority/dashboard.test.jsx` (5 tests)
  - `frontend/src/__tests__/authority/authorityFlow.test.jsx` (1 test)
- **Citizen & Geo Tests:** 29 passed
- **Oxlint / Build:** 0 errors, production build succeeds in ~1.0s
