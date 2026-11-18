# Sprint 4 QA Checklist & Test Plan

**Module:** Geospatial & Analytics (M4 — Ayaansh)
**Sprint:** Sprint 4 (CW-411 to CW-414)
**Branch:** `feature/geo-sprint4`
**Date:** 2026-11-18
**Status:** Template — results to be filled in by QA reviewer before PR merge.

---

## 1. Environment Setup

| Item | Expected | Result |
|------|----------|--------|
| Backend server starts with `uvicorn backend.app.main:app --reload` | No startup errors | TODO |
| Frontend starts with `npm run dev` (inside `frontend/`) | Dev server on port 5173 | TODO |
| Demo data seeded: `python -m backend.app.geo.seed_demo_complaints` | "Inserted N demo complaints" or "Already seeded" | TODO |
| Logged in as an **officer** user | Bearer token stored in localStorage | TODO |
| Logged in as a **citizen** user (for access-control tests) | Bearer token stored in localStorage | TODO |

---

## 2. CW-411 — Hotspot API and Repeat-Issue Zones

### 2.1 Backend API (`GET /geo/hotspots`)

| # | Test Charter | Steps | Expected | Result |
|---|--------------|-------|----------|--------|
| H-01 | Hotspots appear for dense clusters | Seed demo data; call with default params | At least 3 hotspot cells returned | TODO |
| H-02 | `min_count` threshold respected | Call with `min_count=10` on sparse area | Fewer (or zero) hotspots returned | TODO |
| H-03 | `cell_size` parameter changes granularity | Call with `cell_size=0.001` vs `cell_size=0.05` | Smaller cell → more cells; larger cell → fewer, bigger cells | TODO |
| H-04 | `category` field populated correctly | Seed complaints of category "Pothole" in one cluster | That cluster's `category` = "Pothole" | TODO |
| H-05 | Citizen gets 403 | Log in as citizen; call `/geo/hotspots` | HTTP 403, body contains "You do not have permission" | TODO |
| H-06 | No token gets 401 | Call without Authorization header | HTTP 401 | TODO |
| H-07 | Invalid `cell_size` rejected | Call with `cell_size=0.0005` (below 0.001) | HTTP 422 | TODO |
| H-08 | Invalid `min_count` rejected | Call with `min_count=1` (below minimum 2) | HTTP 422 | TODO |
| H-09 | Category filter works | Call with `category_id` for "Garbage" only | All returned hotspots are in Garbage-majority cells | TODO |
| H-10 | Status filter works | Call with `status=Resolved` | Only resolved complaints counted in cells | TODO |

### 2.2 Frontend — HotspotLayer and HotspotList

| # | Test Charter | Steps | Expected | Result |
|---|--------------|-------|----------|--------|
| HF-01 | Hotspot checkbox appears on map page | Navigate to `/map` as officer | Checkbox labelled "Hotspots" is visible | TODO |
| HF-02 | Checking box fetches hotspots and renders circles | Tick "Hotspots" checkbox | Red semi-transparent circles appear on dense areas | TODO |
| HF-03 | Unchecking removes circles | Untick the checkbox | Circles disappear; map shows clean markers | TODO |
| HF-04 | Circle popup shows correct info | Click a circle | Popup shows "Hotspot: N complaints, mostly \<category\>" | TODO |
| HF-05 | HotspotList renders rank table | Import HotspotList with mock data in browser | Table shows rank, count, category, centre columns | TODO |
| HF-06 | HotspotList empty state | Pass empty array to HotspotList | Shows "No hotspots found" message | TODO |
| HF-07 | Citizen cannot see hotspot data | Log in as citizen; navigate to `/map` | Hotspot checkbox absent OR API returns 403 gracefully | TODO |

---

## 3. CW-412 — Reports and Charts

### 3.1 Backend API (`GET /geo/reports/summary`)

| # | Test Charter | Steps | Expected | Result |
|---|--------------|-------|----------|--------|
| R-01 | Summary returns correct total count | Seed N complaints; call `/geo/reports/summary` | `total` field equals N | TODO |
| R-02 | `by_status` breakdown matches seeded data | Seed 5 Submitted, 3 Resolved; call API | `by_status` list contains both entries with correct counts | TODO |
| R-03 | `by_category` sorted by count descending | Seed more Potholes than Garbage; call API | Potholes entry appears before Garbage | TODO |
| R-04 | `by_area` returns top geographic cells | Seed dense cluster at Noida; call API | First area entry has highest count | TODO |
| R-05 | `avg_resolution_hours` is None when no resolved | Seed only Submitted complaints | `avg_resolution_hours` is null | TODO |
| R-06 | `avg_resolution_hours` calculated correctly | Seed a Resolved complaint with 24 h between created/updated | `avg_resolution_hours` ≈ 24.0 | TODO |
| R-07 | Citizen gets 403 | Log in as citizen; call `/geo/reports/summary` | HTTP 403 | TODO |
| R-08 | No token gets 401 | Call without Authorization header | HTTP 401 | TODO |

### 3.2 Frontend — ReportsPage and BarChart

| # | Test Charter | Steps | Expected | Result |
|---|--------------|-------|----------|--------|
| RF-01 | Reports page accessible from map | On `/map` as officer; click "View Reports" link | Navigates to `/reports` | TODO |
| RF-02 | Total count displayed | Load `/reports` with real data | "Total complaints: N" text visible | TODO |
| RF-03 | Status chart renders bars | Load page with by_status data | Horizontal bar chart visible with labelled bars | TODO |
| RF-04 | Category chart renders bars | Load page with by_category data | Bars for each category with counts | TODO |
| RF-05 | Area table shows top areas | Load page with by_area data | Table rows with area coordinates and counts | TODO |
| RF-06 | Avg resolution time shown | Resolved complaints exist | "Average resolution time: X.X hours" displayed | TODO |
| RF-07 | Loading spinner during fetch | Throttle network to Slow 3G | Spinner visible before data arrives | TODO |
| RF-08 | Error state on API failure | Disconnect backend; load `/reports` | "Failed to load report" error message shown | TODO |
| RF-09 | Citizen cannot access reports | Log in as citizen; navigate to `/reports` | Redirected to login OR API returns 403 error message | TODO |

---

## 4. CW-413 — Refactor: Named Constants

| # | Test Charter | Steps | Expected | Result |
|---|--------------|-------|----------|--------|
| C-01 | No regression in heatmap | Run `/geo/heatmap` with same bbox before and after refactor | Identical cell count and values | TODO |
| C-02 | No regression in hotspots | Run `/geo/hotspots` before and after refactor | Identical hotspot list | TODO |
| C-03 | No regression in reports | Run `/geo/reports/summary` before and after refactor | Identical summary | TODO |
| C-04 | Constants file importable | `python -c "from backend.app.geo.constants import MAX_RESULTS; print(MAX_RESULTS)"` | Prints `5000` | TODO |

---

## 5. Cross-Feature Regression Tests

| # | Test Charter | Steps | Expected | Result |
|---|--------------|-------|----------|--------|
| X-01 | Existing `/geo/complaints/nearby` unaffected | Call with valid lat/lon/radius as any logged-in user | Returns complaint list as before | TODO |
| X-02 | Existing `/geo/complaints/bbox` with filters unaffected | Call with bbox + category_id + status | Filtered results returned correctly | TODO |
| X-03 | Map clustering still works after sprint 4 changes | Load `/map`; zoom out | Cluster circles appear; zoom in to see individual markers | TODO |
| X-04 | Filter + heatmap combination | Apply "Garbage" category filter; switch to heatmap view | Heatmap shows only Garbage complaint density | TODO |
| X-05 | Filter + hotspot combination | Apply "Submitted" status filter; enable Hotspots | Only Submitted complaints counted in hotspot cells | TODO |
| X-06 | Switching views (Markers → Heatmap → Markers) | Toggle view mode twice | No duplicate layers; map state consistent | TODO |

---

## 6. Performance & Load

| # | Test Charter | Steps | Expected | Result |
|---|--------------|-------|----------|--------|
| P-01 | Heatmap with 5000 complaints responds within 2 s | Seed 5000 complaints; time the `/geo/heatmap` call | Response time < 2 seconds | TODO |
| P-02 | Hotspot with 5000 complaints responds within 2 s | Same data set; time `/geo/hotspots` | Response time < 2 seconds | TODO |
| P-03 | Reports summary with 5000 complaints within 2 s | Same data set; time `/geo/reports/summary` | Response time < 2 seconds | TODO |

---

## 7. Accessibility & UX

| # | Test Charter | Steps | Expected | Result |
|---|--------------|-------|----------|--------|
| A-01 | Hotspot circles have descriptive popups | Tab to a hotspot circle on the map | Popup readable by screen reader (text content present) | TODO |
| A-02 | Charts have text labels (not just colour) | View ReportsPage | Each bar has a text count label; colour not the only indicator | TODO |
| A-03 | Filter dropdowns keyboard-accessible | Use Tab + Enter to change filters | Filters update without mouse | TODO |

---

## 8. Known Limitations (for viva discussion)

- `leaflet.heat` and `leaflet.markercluster` are not tested with real Leaflet in Jest — both are mocked. Visual correctness must be verified manually in the browser.
- The demo seeder (`seed_demo_complaints.py`) targets a PostgreSQL database with PostGIS. It will error on SQLite (dev/test environment) — this is expected.
- `avg_resolution_hours` only counts complaints with `status = "Resolved"` and both timestamps set. Complaints updated for other reasons do not count.
- The `HotspotList` component is exported for teammate Udit's authority dashboard but is not routed in this module.
- RBAC uses a local `require_officer` check in `permissions.py`. When teammate Gaurav's RBAC is merged, replace with `platform.require_role`.

---

## 9. Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | Ayaansh | 2026-11-18 | ✓ (automated tests passing) |
| QA Reviewer | ___ | ___ | ___ |
| Scrum Master | ___ | ___ | ___ |
