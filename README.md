# CivicWatch

CivicWatch is a city-complaint management platform that connects citizens with local government departments. Citizens file complaints about civic issues, authority officers review and resolve them, and platform admins manage departments and accounts. All data is tracked through a full audit trail with status history and citizen feedback.

---

## Tech Stack

| Layer    | Technology |
|----------|------------|
| Backend  | Python 3.10, FastAPI, SQLAlchemy, Alembic, bcrypt, PyJWT |
| Database | PostgreSQL 15 + PostGIS |
| Frontend | React 18, Vite, React Router v7, Leaflet |
| Testing  | pytest, pytest-cov (backend); Jest + React Testing Library (frontend) |
| CI/CD    | GitHub Actions |

---

## Team

| Member   | Role                              |
|----------|-----------------------------------|
| Gaurav   | Platform & Auth, Scrum Master     |
| Ayaansh  | Geospatial & Analytics            |
| Ayan     | Citizen Reporting, Product Owner  |
| Udit     | Authority Management              |

---

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Docker Desktop (for PostgreSQL + PostGIS)
- Git

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-org>/civicwatch.git
cd civicwatch
```

### 2. Start the database

```bash
docker compose up -d
```

This starts a PostgreSQL + PostGIS container on port 5432.

### 3. Set up the Python environment

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
cd ..
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY for production
```

### 5. Run database migrations

```bash
# From the civicwatch/ root directory
alembic -c backend/alembic.ini upgrade head
```

### 6. Create the first admin account

The public `/auth/register` endpoint only creates citizen accounts. Create the first admin like this:

```bash
python -m backend.app.platform.create_admin "Admin" admin@civicwatch.com secret123
```

### 7. Run the backend

```bash
uvicorn backend.app.main:app --reload
```

The API is now available at **http://localhost:8000**. Interactive docs are at **http://localhost:8000/docs**.

### 8. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend is now available at **http://localhost:5173**.

---

## Seed Demo Data

Load the pre-defined city departments:

```bash
python -m backend.app.authority.seed_departments
```

Load demo complaint data for the map:

```bash
python -m backend.app.geo.seed_demo_complaints
```

---

## Create an Officer

Log in to `/docs` as an admin and use `POST /admin/officers`:

```json
{
  "name": "Officer Name",
  "email": "officer@civicwatch.com",
  "password": "strongpassword"
}
```

---

## Running Tests

### Backend

```bash
# From the civicwatch/ root directory
pytest -q --cov=backend/app
```

### Frontend

```bash
cd frontend
npm test
```

---

## CI

GitHub Actions runs on every push and pull request. The pipeline:
1. Runs `flake8` for Python linting
2. Runs `pytest -q --cov=backend/app` and fails if coverage drops below 70 %
3. Runs `npm test` for all Jest tests
4. Runs `npm run build` to verify the production bundle compiles

Configuration: `.github/workflows/ci.yml`

---

## Branching and Commit Rules

- **Never commit to `main` directly** — open a pull request.
- Branch naming: `feature/<team>-<story>` (e.g., `feature/platform-sprint2`)
- Branches stack from each other: sprint3 from sprint2, sprint4 from sprint3.
- **Commit message format:** `type(scope): short summary [CW-XXX]`
  - Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`
  - Examples: `feat(auth): login endpoint [CW-205]`, `docs(agile): sprint 2 report [CW-207]`

---

## Roles

| Role    | What they can do |
|---------|-----------------|
| citizen | Register, file complaints, view own complaints, give feedback |
| officer | Everything a citizen can do, plus review/assign/resolve all complaints, view the map and reports |
| admin   | Everything an officer can do, plus manage departments and officer accounts |

---

## API Documentation

Interactive Swagger UI: **http://localhost:8000/docs**  
Raw OpenAPI schema: **http://localhost:8000/openapi.json**

---

## Project Structure

```
civicwatch/
├── backend/
│   ├── app/
│   │   ├── platform/      # Auth, JWT, RBAC, admin — Gaurav
│   │   ├── citizen/       # Complaint filing, history — Ayan
│   │   ├── authority/     # Dashboard, assignment, escalation — Udit
│   │   └── geo/           # Map, heatmap, hotspots, reports — Ayaansh
│   ├── alembic/           # Database migrations
│   └── tests/             # Pytest test suites per module
├── frontend/
│   └── src/
│       ├── features/      # React feature folders (auth, citizen, authority, geo, admin)
│       └── __tests__/     # Jest test suites per feature
├── docs/
│   ├── sprint-reports/    # Sprint goal, velocity, retro per sprint
│   └── kanban-metrics.md  # Weekly cycle-time and WIP log
├── .env.example           # Copy to .env — never commit .env
├── docker-compose.yml     # PostgreSQL + PostGIS
└── README.md
```
