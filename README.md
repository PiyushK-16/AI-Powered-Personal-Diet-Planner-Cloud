# AI-Powered Personal Diet Planner with Cloud Storage

A Cloud Computing course project: a full-stack web application that lets a
user register, build a demo profile, generate an AI-assisted daily meal
plan, save it to a cloud database, and upload related files to cloud
object storage — all runnable for free, locally or on a free-tier host.

> **Disclaimer:** This project uses only synthetic/demo data. Generated
> diet plans are general, educational wellness examples — **not** medical,
> clinical, or professional nutrition advice.

---

## Overview

| | |
|---|---|
| **Type** | Cloud Computing course project / GitHub portfolio piece |
| **Status** | Local development complete, deployable to free-tier cloud hosting |
| **Stack (this build)** | Flask (Python), SQLite, simulated cloud object storage, vanilla HTML/CSS/JS |
| **Cost** | $0 — everything runs on free-tier or local/simulated services |

## Problem Statement

People who want general, everyday meal-planning ideas often have no
central place to store their preferences and generated plans, and no way
to reach that history from another device. This project solves that with
a cloud-style client-server app: one account, one profile, plans and
files stored centrally and reachable from anywhere the app is deployed.

## Why Cloud Computing Here

- **Centralized data**: profile, plans, and files live on the server/cloud,
  not only in one browser — so a user can log in from a different device
  and see the same data.
- **Cloud database vs. cloud storage**: structured data (users, plans) is
  a database concern; raw files (images, exports) are an object-storage
  concern. This project deliberately implements both, through two
  separate service modules, so the distinction is concrete rather than
  theoretical.
- **Client-server / REST API**: the frontend and backend are independent
  applications that only talk over HTTP/JSON — the same shape as a
  production cloud app, just without the paid infrastructure.

## Simple Explanation

You make an account, tell the app a bit about yourself (like whether
you're vegetarian and how active you are), and it hands you a sample
day's meals. It remembers your past plans and files so you can find them
later, from any device, as long as you're logged in.

## Technical Explanation

The frontend (static HTML/JS) calls a Flask REST API. The API
authenticates requests with JWTs, reads/writes structured data through a
`cloud/database_service.py` abstraction (SQLite locally; a managed cloud
DB in production), generates a plan via `ai_engine/diet_engine.py`
(rule-based, with an AI-API path that falls back automatically), and
stores uploaded files through `cloud/storage_service.py` (a local folder
standing in for an object-storage bucket such as S3 or Firebase Storage).

### High-Level Workflow

```
User
  │
  ▼
Web Application (frontend/)
  │
  ▼
Authentication (JWT, backend/utils/auth_utils.py)
  │
  ▼
User Profile Input
  │
  ▼
Cloud Backend / REST API (backend/app.py + routes/)
  │
  ▼
AI Diet Planner (ai_engine/diet_engine.py)
  │
  ▼
Personalized Plan
  │
  ▼
Cloud Database (cloud/database_service.py)
  │
  ▼
Cloud Storage (cloud/storage_service.py)
  │
  ▼
User Dashboard
```

## System Architecture

```
                     CLIENT LAYER
                Web Browser (HTML/CSS/JS)
                          │
                          ▼
                 AUTHENTICATION (JWT)
                          │
                          ▼
                    REST API (Flask)
                          │
                          ▼
                APPLICATION LAYER (backend/)
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
   AI ENGINE          CLOUD DATABASE     CLOUD STORAGE
 (rule-based +      (users, plans,      (uploaded files,
  AI-API fallback)   file metadata)      bucket-style)
        │                 │                  │
        └─────────────────┼──────────────────┘
                          ▼
                    Diet Plan / Files
                          ▼
                    USER DASHBOARD
```

Full data-flow narrative and diagrams: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## Features

- Register / Login / Logout (JWT-based auth)
- Demo profile: age, height, weight, activity level, dietary preference,
  goal, optional allergies — synthetic data only, no medical use
- AI-assisted diet plan generation (breakfast/lunch/snack/dinner +
  nutrition summary + hydration reminder), for vegetarian, vegan, and
  non-vegetarian preferences and balanced/weight-management/fitness goals
- Automatic fallback: if an external AI API is unavailable, the app
  silently uses its local rule-based engine so the demo never breaks
- Save / list / delete generated plans (cloud database)
- Upload / list / delete files to simulated cloud object storage
- Dashboard summarizing profile, latest plan, and file count
- User isolation: one account can never read another account's data
- Automated tests (pytest) covering auth, plans, fallback, files, and
  cross-user access control

## Cloud Computing Concepts Demonstrated

See [`docs/CLOUD_CONCEPTS.md`](docs/CLOUD_CONCEPTS.md) for a full concept
→ code mapping (SaaS/PaaS/IaaS, object storage, REST API,
serverless, scalability, availability, elasticity, load balancing, API
gateway, environment variables, secrets management, security, logging,
monitoring, CI/CD, and more).

## Technology Stack Options

Three implementation tiers are documented and compared in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#technology-stack-options)
(Beginner / Recommended / Advanced). **This repository implements Option
A (Beginner)** — Flask + SQLite + simulated storage — because it is
100% free, has zero external accounts to configure, and still
demonstrates every required cloud concept. Option B (Firebase/Supabase)
and Option C (AWS/Azure/GCP) are documented as upgrade paths.

## Database Design

**USERS** — `user_id (PK)`, `name`, `email (unique)`, `password_hash`,
`age`, `height_cm`, `weight_kg`, `activity_level`, `dietary_preference`,
`goal`, `allergies`, `created_at`

**DIET_PLANS** — `plan_id (PK)`, `user_id (FK)`, `breakfast`, `lunch`,
`snack`, `dinner`, `nutrition_summary`, `hydration_reminder`, `source`,
`created_at`

**USER_FILES** — `file_id (PK)`, `user_id (FK)`, `filename`,
`storage_path`, `uploaded_at`

Relationships: one user → many plans, one user → many files. Every route
checks `record.user_id == request.user_id` (from the JWT) before
returning or deleting a row — full design notes in
[`backend/models/schema.py`](backend/models/schema.py).

## AI Diet Recommendation Engine

- **Version A (implemented, always on):** rule-based engine
  (`ai_engine/diet_engine.py` + `ai_engine/food_data.json`) filters a
  small food dataset by dietary preference, goal, and allergies.
- **Version B (optional):** if `AI_API_KEY`/`AI_API_URL` are set, the
  backend builds a structured prompt and calls an external AI API;
  the response is validated, and **any failure automatically falls back**
  to Version A — the project never breaks without a paid API key.

## REST API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register` | – | Create account |
| POST | `/login` | – | Get JWT token |
| POST | `/logout` | – | Client-side token discard |
| GET | `/profile` | ✅ | Get own profile |
| PUT | `/profile` | ✅ | Update own profile |
| POST | `/generate-plan` | ✅ | Generate + save a diet plan |
| GET | `/plans` | ✅ | List own saved plans |
| GET | `/plans/<id>` | ✅ | Get one plan (owner only) |
| DELETE | `/plans/<id>` | ✅ | Delete one plan (owner only) |
| POST | `/upload` | ✅ | Upload a file to cloud storage |
| GET | `/files` | ✅ | List own files |
| DELETE | `/files/<id>` | ✅ | Delete own file |
| GET | `/health` | – | Health check |

All authenticated routes require `Authorization: Bearer <token>`.
Standard status codes are used: `200/201` success, `400` bad input,
`401` auth failure, `403` forbidden (wrong owner), `404` not found,
`409` conflict (duplicate email), `500` server error.

## Folder Structure

```
AI-Personal-Diet-Planner-Cloud/
├── backend/
│   ├── app.py                 # Flask entry point
│   ├── routes/                # auth, profile, plan, file blueprints
│   ├── utils/auth_utils.py    # JWT + password hashing
│   └── models/schema.py       # schema documentation
├── ai_engine/
│   ├── diet_engine.py         # rule-based + AI-API fallback logic
│   └── food_data.json         # demo food dataset
├── cloud/
│   ├── database_service.py    # "cloud database" abstraction (SQLite locally)
│   └── storage_service.py     # "cloud object storage" abstraction (local folder)
├── frontend/                  # static HTML/CSS/JS pages
├── tests/test_app.py          # pytest automated tests
├── docs/                      # architecture, deployment, testing, interview prep, etc.
├── sample_data/               # example seed/demo data
├── screenshots/               # place your proof screenshots here
├── requirements.txt
├── .env.example
└── .gitignore
```

## Installation & Local Setup

```bash
# 1. Clone / unzip the project, then move into it
cd AI-Personal-Diet-Planner-Cloud

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env            # then edit .env if you want (defaults work locally)

# 5. Start the backend (runs on http://127.0.0.1:5000)
python backend/app.py

# 6. Serve the frontend (in a second terminal, from the project root)
cd frontend
python3 -m http.server 5500
# open http://127.0.0.1:5500 in your browser
```

Full step-by-step walkthrough (including how to demo every feature) is in
[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md#local--virtual-simulation).

## Cloud Deployment

Two deployment paths (free-tier and AWS/Azure/GCP) are documented in
[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## Testing

Run the automated suite:

```bash
pip install pytest   # if not already installed
pytest tests/ -v
```

Full manual test-case table (20 scenarios: registration, login, AI
fallback, file validation, user isolation, etc.) is in
[`docs/TESTING.md`](docs/TESTING.md).

## Security Notes

Passwords are hashed (never stored in plain text); JWTs are used for
stateless auth; secrets are read from environment variables, never
hardcoded; every data-owning route enforces per-user authorization;
uploads are restricted by extension and size. Full checklist —
including what a production deployment would add (HTTPS, encryption at
rest, rate limiting, CORS lockdown) — in
[`docs/CLOUD_CONCEPTS.md`](docs/CLOUD_CONCEPTS.md#security).

## Scalability

How this architecture would evolve at 10 / 1,000 / 100,000 users
(load balancers, managed databases, CDN, caching, queues) is discussed in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#scalability).

## Screenshots

See [`docs/SCREENSHOTS_CHECKLIST.md`](docs/SCREENSHOTS_CHECKLIST.md) for
the exact list of screenshots to capture and their suggested filenames.
Save them into `screenshots/`.

## Results

The application runs fully offline/locally at zero cost, demonstrates
authentication, a cloud database, cloud object storage, an AI engine
with automatic fallback, and a working dashboard — all backed by an
automated test suite covering the core flows and user-isolation
security rule.

## Limitations

- Uses SQLite and local-folder storage rather than a managed cloud DB/
  bucket (by design, for a $0 student build) — see `docs/ARCHITECTURE.md`
  for the drop-in upgrade path to Firebase/Supabase/AWS.
- Diet plans are generated from a small demo dataset and simple rules;
  they are not personalized medical/clinical recommendations.
- JWT is stored in `localStorage` on the frontend for simplicity, which
  is acceptable for a local demo but not ideal for production (see
  Security notes).

## Future Improvements

- Swap `cloud/database_service.py` for Firestore/Supabase/RDS and
  `cloud/storage_service.py` for S3/Firebase Storage without touching
  any route code (that's the point of the abstraction layer).
- Add refresh tokens and a token blocklist for real logout semantics.
- Add calorie/macro tracking over time and CSV export.

## Learning Outcomes

Hands-on practice with: REST API design, JWT authentication and
authorization, the cloud-database vs. cloud-storage distinction,
building a fallback-safe AI integration, writing automated tests for a
multi-user system, and structuring a project for cloud deployment.

## Author

Student project — Cloud Computing coursework. Built as GitHub portfolio
proof of work.

## Disclaimer

This project is for educational purposes only. It uses synthetic/demo
data, and generated diet plans are general wellness examples, not
medical or clinical nutrition advice. Do not use this application to
make real health decisions.
