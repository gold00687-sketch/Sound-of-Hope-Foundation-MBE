# Architecture Overview

## Pattern

Modular monolith. Business domains are grouped into modules under `app/modules/`.
Each module owns its models, repository, service, schemas and router.
Modules do not directly import each other's repositories — cross-module
interactions happen through service interfaces.

## Layers

```
HTTP Request
    │
    ▼
FastAPI Router (app/modules/*/router.py)
    │  validates input via Pydantic schemas
    ▼
Service (app/modules/*/service.py)
    │  owns business logic, orchestrates transactions
    ▼
Repository (app/modules/*/repository.py)
    │  owns SQL queries, returns ORM objects
    ▼
SQLAlchemy Models (app/modules/*/models.py)
    │
    ▼
PostgreSQL
```

## Infrastructure

| Concern | Technology | Location |
|---------|-----------|----------|
| Primary database | PostgreSQL 16 | `infrastructure/database/` |
| Session caching / blacklist | Redis 7 | `infrastructure/cache/` |
| Background jobs | Celery + Redis | `workers/` |
| File storage | Local (dev) / S3 (prod) | `infrastructure/storage/` |
| Email delivery | SMTP / SendGrid | `integrations/email/` |
| SMS delivery | Twilio | `integrations/sms/` |
| Payment processing | Pluggable provider | `integrations/payment_providers/` |
| Internal events | In-process event bus | `infrastructure/messaging/` |
| Full-text search | PostgreSQL tsvector | `infrastructure/search/` |

## Authentication

JWT-based. Access tokens (short-lived) carry user ID, email and permissions.
Refresh tokens are stored hashed in PostgreSQL and rotated on every use.
Revoked access tokens are tracked in Redis by JTI for the remainder of their TTL.

## Permissions

Role-based at the database level. Permissions are strings (`resource:action`).
Every API endpoint that modifies state or accesses restricted data enforces
at least one permission via the `require_permission()` dependency.
Safeguarding records enforce `safeguarding:read` — a permission not assigned
to instructors, programme managers or general staff by default.

## Module Extraction Path

Each module follows the same interface contract (repository / service / router).
To extract a module as a microservice:
1. Move its `models/`, `repository/`, `service/`, `router/` to a new service.
2. Replace direct service calls from other modules with HTTP or message-based calls.
3. Run migrations independently.

No module shares a database table with another module directly.
