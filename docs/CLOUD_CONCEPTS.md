# Cloud Computing Concepts → Where They Appear In This Project

For every concept below: a plain-English definition, then exactly where
it shows up in this codebase.

## Cloud Computing
Delivering computing resources (compute, storage, databases) over a
network instead of running everything on one personal machine. Here:
the backend, database, and file storage are all separate services the
frontend talks to over HTTP — the same shape as a real cloud app.

## SaaS / PaaS / IaaS
- **SaaS** (Software as a Service): the finished diet-planner web app
  itself, as the end user experiences it.
- **PaaS** (Platform as a Service): the free-tier hosting platforms
  suggested in `docs/DEPLOYMENT.md` (Render/Railway/PythonAnywhere) — you
  deploy code, the platform manages the OS/runtime.
- **IaaS** (Infrastructure as a Service): the Option C (AWS/Azure/GCP)
  deployment in `docs/DEPLOYMENT.md`, where you provision raw compute
  (EC2/VMs) and wire it up yourself.

## Cloud Storage vs. Cloud Database
- **Cloud Database**: structured rows/columns — `cloud/database_service.py`
  (users, diet_plans, user_files *metadata*).
- **Cloud Object Storage**: raw files/blobs — `cloud/storage_service.py`
  (the actual uploaded file bytes, addressed by a path/key like an S3
  object key).

## Authentication / Authorization
`backend/utils/auth_utils.py` (JWT issuing/verification, password
hashing) and the `@token_required` decorator used on every protected
route. Authorization (user isolation) is the `record.user_id ==
request.user_id` checks in `plan_routes.py` / `file_routes.py`.

## REST API
`backend/routes/*.py` — resource-oriented endpoints (`/plans`,
`/files`, `/profile`) using standard HTTP verbs and status codes.

## Client-Server Architecture
`frontend/` (client) never touches the database or storage directly —
it only calls the Flask REST API (server), exactly as described in
`backend/app.py`'s module docstring.

## Serverless Computing
Not implemented directly (this build uses an always-on Flask process),
but discussed as an Option C upgrade in `docs/ARCHITECTURE.md` — e.g.
converting `/generate-plan` into an AWS Lambda / Cloud Function that
only runs (and only costs money) when invoked.

## Scalability / Availability / Elasticity
Discussed in `docs/ARCHITECTURE.md#scalability` with concrete 10 / 1,000
/ 100,000-user scenarios. This build is a single process (fine for a
student demo); a scaled version would run multiple backend instances
behind a load balancer with a managed, shared database.

## Load Balancing / API Gateway
Not present in the local build (a single Flask process doesn't need
one), but both are described in `docs/ARCHITECTURE.md` as what sits in
front of the backend once there is more than one instance (a load
balancer distributes requests; an API Gateway would additionally handle
routing, rate limiting, and auth at the edge in Option C).

## Environment Variables & Secrets Management
`.env.example` lists every configurable value (`SECRET_KEY`,
`DATABASE_URL`, `AI_API_KEY`, etc.). `backend/app.py` loads them via
`python-dotenv`; nothing sensitive is hardcoded anywhere in the source
(`.env` itself is git-ignored — see `.gitignore`).

## Cloud Security
Password hashing (`werkzeug.security`), JWT-based stateless auth,
per-user authorization checks, upload file-type/size validation, and
CORS configuration (`backend/app.py`). Full checklist below.

## Logging / Monitoring
The `/health` endpoint in `backend/app.py` is what a monitoring service
or load balancer would poll. Flask's built-in request logging is active
in debug mode; `docs/DEPLOYMENT.md` explains how a real cloud host
(Render/AWS CloudWatch) surfaces these logs centrally.

## Deployment / CI/CD
`docs/DEPLOYMENT.md` covers manual deployment steps for two approaches.
A GitHub Actions CI workflow suggestion (run `pytest` on every push) is
included there as the CI/CD demonstration.

---

## Security Checklist

| Area | Status in this project |
|---|---|
| Password security | ✅ Hashed with Werkzeug's `generate_password_hash` |
| Authentication tokens | ✅ JWT, expires after `JWT_EXPIRY_HOURS` |
| Secrets management | ✅ All secrets via environment variables, never hardcoded |
| Input validation | ✅ Email format, password length, file type/size checks |
| User isolation (authorization) | ✅ Every plan/file route checks ownership |
| CORS | ✅ Configured, restrict `FRONTEND_ORIGIN` in production |
| HTTPS | ⚠️ Not applicable locally; **required** in real deployment (free-tier hosts provide it automatically) |
| Encryption in transit | ⚠️ Provided by HTTPS at the hosting layer in production |
| Encryption at rest | ⚠️ Managed cloud databases/buckets provide this; local SQLite/folder do not — documented limitation |
| Rate limiting | ❌ Not implemented (documented as a future improvement) |
| Backups | ⚠️ Managed cloud DBs provide automatic backups; local SQLite file should be backed up manually during a demo |

**Common student mistakes to avoid:** committing a real `.env` file to
GitHub, hardcoding an API key in source code "just for testing", storing
passwords in plain text, and skipping the ownership check on a
`GET/DELETE` route (which is what causes User A to read User B's data).
