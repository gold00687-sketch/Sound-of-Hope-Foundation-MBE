# Database Schema

## Conventions

- All primary keys are UUID v4.
- All timestamps stored in UTC with timezone (`TIMESTAMPTZ`).
- Soft deletion is used only where the business genuinely needs it (e.g. certificates have `is_revoked`, not a deleted_at column).
- Financial records (`financial_transactions`) are append-only — never updated.
- Audit logs (`audit_logs`) are append-only — never updated.

## Key Tables

| Table | Purpose |
|-------|---------|
| `users` | Authentication accounts |
| `user_profiles` | Display names, avatars, bios |
| `roles` | Named roles (system-seeded + custom) |
| `permissions` | Granular permission strings |
| `role_permissions` | M2M: roles ↔ permissions |
| `user_roles` | M2M: users ↔ roles |
| `refresh_tokens` | Hashed refresh tokens with expiry |
| `auth_events` | Immutable auth audit trail |
| `organisation` | Single organisation profile row |
| `departments` | Hierarchical department tree |
| `staff_members` | Staff employment records |
| `participants` | Programme participants (may or may not have user accounts) |
| `guardians` | Parents/guardians of minor participants |
| `participant_guardians` | M2M: participants ↔ guardians |
| `programmes` | Programme definitions |
| `programme_categories` | Programme classification |
| `programme_cohorts` | Specific intakes within a programme |
| `projects` | Organisational projects |
| `applications` | Programme applications with workflow |
| `enrolments` | Active enrolments (unique constraint prevents duplicates) |
| `courses` | Course definitions |
| `course_modules` | Ordered modules within a course |
| `lessons` | Ordered lessons within a module |
| `classes` | Running instance of a course |
| `class_sessions` | Scheduled sessions for a class |
| `attendance_records` | Per-participant per-session attendance |
| `assessments` | Assessment definitions |
| `assessment_submissions` | Participant submissions + grades |
| `certificates` | Issued certificates (unique per participant/programme/course) |
| `events` | Organisational events |
| `event_registrations` | Event sign-ups |
| `safeguarding_cases` | Restricted psychosocial support records |
| `consent_records` | Informed consent tracking |
| `referrals` | External referrals for participants |
| `financial_transactions` | Immutable financial ledger |
| `donations` | Donation records |
| `payments` | Payment records with idempotency keys |
| `expenses` | Staff expense submissions |
| `notifications` | In-app notification inbox |
| `audit_logs` | Full system audit trail with JSONB change diffs |

## Generating Migrations

```bash
# After editing any model file
alembic revision --autogenerate -m "short description"
alembic upgrade head
```

Always review the generated migration before applying — Alembic may not detect
all changes (e.g. check constraints, custom indexes) automatically.
