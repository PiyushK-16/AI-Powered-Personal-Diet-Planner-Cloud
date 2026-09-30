# Architecture & Technology Stack Options

## Technology Stack Options

### Option A — Beginner (this repository implements this)
- Frontend: HTML / CSS / JavaScript
- Backend: Python Flask
- Database: SQLite (local file, simulating a cloud database)
- AI: Rule-based recommendation engine, with optional AI-API path + fallback
- Storage: Local folder simulating cloud object storage
- Deployment: Any free-tier host that runs Python (Render, PythonAnywhere)

**Difficulty:** Low. **Cost:** $0. **Concepts demonstrated:** REST API,
auth, DB design, storage abstraction, fallback logic, testing. **Output:**
A fully working, demoable app with zero external accounts required.

### Option B — Recommended (documented upgrade path, not built here)
- Frontend: React
- Backend: FastAPI or Flask
- Auth: Firebase Authentication / Supabase Auth
- Database: Firestore / Supabase (Postgres)
- Storage: Firebase Storage / Supabase Storage
- AI: Real AI API with local rule-based fallback (same fallback pattern
  already implemented in `ai_engine/diet_engine.py`)
- Deployment: Vercel (frontend) + Render/Railway (backend) free tiers

**Difficulty:** Medium. **Cost:** $0 on free tiers, small cost at scale.
**Concepts demonstrated:** everything in Option A, plus a real managed
cloud database and real managed object storage, and a proper build step.
**Migration path:** because `cloud/database_service.py` and
`cloud/storage_service.py` are the *only* files that touch SQLite/local
folders, swapping to Firestore/Supabase means rewriting those two files
only — no route or frontend code changes.

### Option C — Advanced (documented, for reference)
- Frontend: React / Next.js
- Backend: FastAPI
- Cloud: AWS or Azure or GCP
- Services: managed compute (EC2/App Runner/Cloud Run), S3/Blob Storage,
  RDS/Cosmos DB, Cognito/Azure AD B2C, Lambda/Cloud Functions, API
  Gateway, CloudWatch/Monitor
- AI: LLM/API integration with the same safe fallback pattern

**Difficulty:** High. **Cost:** Free-tier eligible for ~12 months on new
AWS/GCP accounts, then usage-based. **Concepts demonstrated:** the full
enterprise cloud stack — IaaS, serverless, API gateway, managed DB,
autoscaling, centralized logging/monitoring.

**Recommendation for a student portfolio project:** build and fully
demo Option A first (as this repo does) so the whole system is provably
working end-to-end at zero cost and zero setup friction, then describe
Options B/C in the README/report as the deployment roadmap. That's a
stronger interview story than a half-finished AWS setup.

---

## Complete Data Flow

1. Browser loads a static page from `frontend/`.
2. User submits a form → `frontend/js/api.js` sends a `fetch()` call to
   the Flask REST API.
3. Flask (`backend/app.py`) routes the request to the right blueprint
   (`routes/auth_routes.py`, `profile_routes.py`, `plan_routes.py`,
   `file_routes.py`).
4. Protected routes run `@token_required` (`backend/utils/auth_utils.py`)
   to decode the JWT and authorize the caller.
5. Business logic calls `ai_engine/diet_engine.py` (for plan generation)
   and/or `cloud/database_service.py` / `cloud/storage_service.py` for
   persistence.
6. The database/storage layer returns data; the route formats a JSON
   response with an appropriate HTTP status code.
7. The frontend renders the JSON response into the dashboard, plan
   result, saved-plans, or files page.

## Scalability

| Users | What happens | How the architecture would adapt |
|---|---|---|
| **10** | This exact build (single Flask process + SQLite) handles it comfortably. | No changes needed. |
| **1,000** | SQLite's single-writer model and local file storage start to bottleneck; one server may saturate CPU during traffic spikes. | Move to a managed database (Postgres/Firestore), move file storage to S3/Firebase Storage, add a second backend instance behind a load balancer. |
| **100,000** | A single server and single DB instance cannot keep up; global users need low latency. | Autoscaling groups of backend instances behind a load balancer; managed database with read replicas; CDN for static frontend assets; caching layer (Redis) for frequent reads (e.g. food dataset); message queue for slow tasks (e.g. AI-API calls) so requests don't block; object storage (S3) already scales natively. |

Key scaling concepts for interviews: **autoscaling** (add/remove server
instances based on load), **load balancers** (spread requests across
instances), **serverless functions** (pay only per invocation, scale to
zero), **managed databases** (handle replication/failover for you),
**CDN** (serve static assets from edge locations near the user),
**caching** (avoid recomputing/refetching the same data), **queues**
(decouple slow work from the request/response cycle).
