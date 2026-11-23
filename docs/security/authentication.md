# Authentication & Security

## Token Lifecycle

1. **Login** — POST `/api/v1/auth/login` returns an access token (JWT, 30 min) and a refresh token (opaque, 7 days).
2. **Access** — Include `Authorization: Bearer <access_token>` on every protected request.
3. **Refresh** — POST `/api/v1/auth/refresh` with the refresh token. Returns a new access token and rotates the refresh token. The old refresh token is immediately revoked.
4. **Logout** — POST `/api/v1/auth/logout` revokes the refresh token. The access token is blacklisted in Redis for its remaining TTL.
5. **Logout all** — POST `/api/v1/auth/logout-all` revokes all active refresh tokens for the user.

## Password Policy

- Minimum 8 characters, maximum 128.
- Must contain at least one uppercase letter, one lowercase letter, one digit.
- Hashed with Argon2id (time_cost=2, memory=64MB, parallelism=2).
- Automatically rehashed on login if the stored hash uses outdated parameters.

## Account Lockout

After `MAX_LOGIN_ATTEMPTS` (default 5) consecutive failures, the account is locked
for `LOCKOUT_DURATION_MINUTES` (default 30). The lockout timestamp is stored in the
`users` table so it survives process restarts.

## Sensitive Data

- Safeguarding cases require `safeguarding:read` permission — not assigned to instructors or general staff.
- Consent records require `consent:read`.
- Financial records are append-only via the `FinancialTransaction` ledger.
- Raw card numbers and CVV are never stored — the `payments` table holds only provider references.

## CORS

Configure `CORS_ORIGINS` in `.env` to the exact origins of your frontend applications.
Wildcard `*` is not permitted in production.

## Secrets

All credentials and keys are loaded from environment variables via `pydantic-settings`.
The `.env` file is listed in `.gitignore` and must never be committed.
Use `.env.example` as the reference template.
