# Sound of Hope Foundation — Main Backend

The main backend API for the Sound of Hope Foundation organisation management and community empowerment platform.

## Technology Stack

- **Python 3.12** with FastAPI
- **PostgreSQL** via SQLAlchemy 2.x (async)
- **Alembic** for migrations
- **Redis** for caching and token blacklisting
- **Celery** for background tasks
- **Argon2** password hashing, **JWT** authentication
- **Docker & Docker Compose** for local development

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.12 (for local development without Docker)

### Environment configuration

```bash
cp .env.example .env
# Edit .env with your local values
```

### Run with Docker (recommended)

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`
Celery monitor: `http://localhost:5555`

### Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements/development.txt

# Start PostgreSQL and Redis (via Docker or locally)
docker compose up postgres redis -d

# Run migrations
alembic upgrade head

# Seed reference data (roles and permissions)
python -m scripts.seed_database

# Create initial admin
python -m scripts.create_initial_admin --email admin@example.com --password AdminPass1!

# Start the API
uvicorn app.main:app --reload
```

## Running Tests

```bash
pytest                        # All tests
pytest tests/unit/            # Unit tests only
pytest tests/api/             # API tests only
pytest tests/security/        # Security tests only
pytest --cov=app              # With coverage report
```

## Database Migrations

```bash
# After changing any model
alembic revision --autogenerate -m "describe the change"

# Apply all pending migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1
```

## Project Structure

```
app/
  core/           Config, security, exceptions, middleware, permissions, constants
  infrastructure/ Database, Redis, storage, messaging, search
  modules/        43 business domain modules
  workers/        Celery app and async task definitions
  integrations/   External service clients (email, SMS, payment providers)
  utils/          Pagination, date helpers, validators, slug/token generation
migrations/       Alembic async migrations
tests/            Unit, API, security, integration, performance
scripts/          Seed data, admin creation, health check
docs/             Architecture, database, API, security documentation
```

## API Versioning

All endpoints are under `/api/v1/`. Full route list at `http://localhost:8000/docs`.

## Security

- Argon2id password hashing with automatic rehash on login
- Short-lived JWT access tokens + rotating refresh tokens
- Refresh tokens stored hashed in PostgreSQL
- Revoked access tokens tracked in Redis by JTI
- Account lockout after configurable failed login attempts
- All secrets via environment variables — never committed to source control
- Safeguarding records isolated behind dedicated permission (`safeguarding:read`)
- Financial records append-only via `FinancialTransaction` ledger
- Payment idempotency keys prevent duplicate charges

## Implementation Status

| Module | Model | Service | Router | Tests |
|--------|-------|---------|--------|-------|
| Identity & Authentication | Complete | Complete | Complete | Complete |
| Roles & Permissions | Complete | Complete | Complete | Partial |
| Users | Complete | Complete | Complete | Partial |
| Organisation & Departments | Complete | Complete | Complete | Partial |
| Staff | Complete | Complete | Complete | Partial |
| Participants | Complete | Complete | Complete | Partial |
| Guardians | Complete | Complete | Complete | Partial |
| Programmes & Cohorts | Complete | Complete | Complete | Partial |
| Projects | Complete | Stub | Stub | Pending |
| Applications | Complete | Complete | Complete | Partial |
| Enrolments | Complete | Complete | Complete | Partial |
| Courses, Modules & Lessons | Complete | Complete | Complete | Pending |
| Classes | Complete | Complete | Complete | Pending |
| Schedules (Sessions) | Complete | Complete | Via classes | Pending |
| Attendance | Complete | Complete | Complete | Pending |
| Assessments | Complete | Complete | Complete | Pending |
| Certificates | Complete | Complete | Complete | Pending |
| Creative Arts | Complete | Stub | Stub | Pending |
| Vocational Training | Complete | Stub | Stub | Pending |
| Instruments | Complete | Stub | Stub | Pending |
| Events & Registration | Complete | Complete | Complete | Pending |
| Community Initiatives | Complete | Stub | Stub | Pending |
| Discussions & Comments | Complete | Stub | Stub | Pending |
| Moderation | Complete | Stub | Stub | Pending |
| Safeguarding Cases | Complete | Complete | Complete | Pending |
| Consent Records | Complete | Complete | Complete | Pending |
| Referrals | Complete | Stub | Stub | Pending |
| Research Projects | Complete | Stub | Stub | Pending |
| Library Resources | Complete | Stub | Stub | Pending |
| Publications | Complete | Stub | Stub | Pending |
| CMS Pages & Versions | Complete | Stub | Stub | Pending |
| Media Assets | Complete | Stub | Stub | Pending |
| Navigation Menus | Complete | Stub | Stub | Pending |
| Finance (Ledger) | Complete | Complete | Complete | Pending |
| Donations | Complete | Complete | Complete | Pending |
| Payments (Idempotent) | Complete | Complete | Complete | Pending |
| Expenses | Complete | Complete | Complete | Pending |
| Notifications | Complete | Complete | Complete | Pending |
| Messaging (Threads) | Complete | Stub | Stub | Pending |
| Reporting | Complete | Stub | Stub | Pending |
| Analytics Snapshots | Complete | Stub | Stub | Pending |
| Audit Log | Complete | Complete | Complete | Pending |

## Known Limitations / Next Steps

- Stub service modules (creative arts, instruments, vocational, CMS, etc.) need full CRUD implementation in the next phase
- Full-text search endpoints need integration once search indexes are created via migration
- Real payment provider (Flutterwave / MTN MoMo / Stripe) needs wiring into `integrations/payment_providers/`
- S3 storage backend needs enabling via `STORAGE_BACKEND=s3` and AWS credentials
- Integration and performance test suites need expanding
- Rate limiting middleware needs implementing (Redis-backed sliding window)
