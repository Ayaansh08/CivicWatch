# Changelog

All notable changes to CivicWatch are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-11-20

### E1 — Platform & Auth (Gaurav)

- `feat(auth)` JWT register, login, and `/auth/me` endpoints with bcrypt password hashing
- `feat(rbac)` Role-based `require_role` dependency and frontend `ProtectedRoute` and `NavBar`
- `feat(admin-api)` Admin endpoints for departments, officers, and user role management
- `feat(pagination)` Shared `paginate()` helper and performance indexes on the complaints table
- `feat(admin-ui)` Admin dashboard with paged departments and officers panels
- `feat(security)` Input validation, in-memory rate limiting, CORS config, and security headers
- `refactor(platform)` Config constants, `get_user_by_email` helper, and module docstrings
- `docs(api)` OpenAPI title, descriptions, and summaries on all platform endpoints
- `chore(release)` Version set to 1.0.0 in backend and frontend

### E2 — Citizen Reporting (Ayan)

- `feat(citizen)` Complaint filing form with photo upload, location pin-drop, and category selection
- `feat(tracking)` Complaint status history API and timeline UI
- `feat(feedback)` Feedback and reopen flow for resolved complaints
- `test(e2e)` End-to-end citizen flow tests

### E3 — Authority Management (Udit)

- `feat(review-api)` List and review complaints endpoints for authority officers
- `feat(assign-api)` Assign complaints to departments and set priority
- `feat(dashboard)` Authority dashboard with filters, sorting by priority and age
- `feat(escalation)` Auto-escalation for overdue unresolved complaints
- `test(e2e)` End-to-end authority flow acceptance tests
- `refactor(authority)` Simplified workflow helpers and split dashboard components

### E4 — Geospatial & Analytics (Ayaansh)

- `feat(geo-utils)` Distance and bounding-box helper functions
- `feat(hotspot)` Grid-based hotspot detection algorithm
- `feat(map)` Leaflet map with real markers, clustering, category and status filters
- `feat(heatmap)` Density API and leaflet.heat heatmap layer
- `feat(hotspots)` Hotspot API and repeat-issue zones layer on the map
- `feat(reports)` Analytics endpoints and bar chart reports page
- `refactor(geo)` Magic numbers extracted to constants module

### E5 — Infrastructure & CI (all)

- `chore(backend)` FastAPI scaffold with pytest and TestClient
- `chore(docker)` Docker Compose with PostgreSQL + PostGIS image
- `ci(actions)` GitHub Actions pipeline: lint, pytest with coverage, Jest, and build
- `feat(db)` Alembic base migration for users, categories, departments, and complaints

### E6 — QA & Documentation (all)

- `docs(agile)` Sprint 1–4 reports, burndown charts, and kanban metrics
- `docs(qa)` Exploratory testing notes, code-smell log, and QA checklist

---

> **To deploy v1.0.0:** merge all sprint branches into main via pull requests (in order: sprint2 → sprint3 → sprint4), then run:
>
> ```bash
> git tag v1.0.0 main
> git push origin v1.0.0
> ```
