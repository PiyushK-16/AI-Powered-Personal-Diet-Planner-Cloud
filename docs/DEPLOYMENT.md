# Local Simulation & Cloud Deployment

## Local / Virtual Simulation

Exact commands to run and demo the entire project locally, end to end.

```bash
# Step 1-2: get the project and enter it
cd AI-Personal-Diet-Planner-Cloud

# Step 3: create a virtual environment
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate

# Step 4: install dependencies
pip install -r requirements.txt

# Step 5: configure environment variables
cp .env.example .env

# Step 6: start the backend
python backend/app.py
# -> Running on http://127.0.0.1:5000

# Step 7: start the frontend (new terminal, from project root)
cd frontend
python3 -m http.server 5500
# -> open http://127.0.0.1:5500
```

Then, in the browser:

- **Step 8:** Register a demo user on `register.html`.
- **Step 9:** Log in, then complete your profile on `profile.html`.
- **Step 10:** Go to `generate-plan.html` and generate a diet plan.
- **Step 11:** The plan is auto-saved; confirm it on `saved-plans.html`.
- **Step 12:** Upload a sample file on `files.html`.
- **Step 13:** Refresh `saved-plans.html` / `files.html` to confirm
  retrieval from the database/storage layer (not just browser memory).
- **Step 14:** Click Logout, then log back in — data should persist.
- **Step 15:** Inspect `backend/diet_planner.db` (e.g. with the
  `sqlite3` CLI or "DB Browser for SQLite") and the `cloud_storage_bucket/`
  folder to see the stored rows and files directly.

## Local Development vs. Cloud Deployment

| | Local Development | Cloud Deployment |
|---|---|---|
| Database | SQLite file on disk | Managed cloud database (Firestore/Supabase/RDS) |
| File storage | Local folder | Managed object storage (S3/Firebase Storage) |
| Access | Only from your machine | Reachable from any device via a public URL |
| Secrets | `.env` file (git-ignored) | Host's environment-variable / secrets manager UI |
| Availability | Only while your machine is running | Host keeps the app running (with sleep/wake on some free tiers) |

## Approach A — Student-Friendly / Free-Tier Deployment

1. Push this repository to GitHub (see `docs/GITHUB_STRATEGY.md`).
2. **Backend:** deploy `backend/` to a free-tier Python host (e.g. Render,
   Railway, or PythonAnywhere):
   - Set the start command to `python backend/app.py` (or a WSGI server
     such as `gunicorn backend.app:app` if the host requires one).
   - Add the environment variables from `.env.example` in the host's
     dashboard (never commit `.env`).
   - Because SQLite is a single file, use the host's persistent disk
     option if available, or switch `cloud/database_service.py` to a
     free-tier managed Postgres add-on for durability.
3. **Frontend:** deploy the static `frontend/` folder to a free static
   host (e.g. Netlify, Vercel, GitHub Pages).
   - Update `API_BASE_URL` in `frontend/js/api.js` to your deployed
     backend's URL.
4. **Environment variables:** set `FRONTEND_ORIGIN` on the backend host
   to your deployed frontend's URL (tightens CORS instead of using `*`).
5. **Logs/monitoring:** most free-tier hosts show live logs and a basic
   uptime/health dashboard in their web console — point it at `/health`.

## Approach B — AWS / Azure / GCP Architecture (Option C)

- **Frontend deployment:** static hosting (S3 + CloudFront, or Azure
  Static Web Apps, or GCP Cloud Storage + CDN).
- **Backend deployment:** containerize the Flask app and run it on
  AWS App Runner / ECS, Azure App Service, or GCP Cloud Run (all support
  scale-to-zero, which keeps cost near $0 for a low-traffic student demo).
- **Managed database:** AWS RDS (Postgres) / Azure SQL / GCP Cloud SQL,
  replacing `cloud/database_service.py`'s SQLite calls.
- **Object storage:** AWS S3 / Azure Blob Storage / GCP Cloud Storage,
  replacing `cloud/storage_service.py`'s local-folder calls.
- **Authentication:** AWS Cognito / Azure AD B2C / Firebase Auth can
  replace the custom JWT layer if desired.
- **Environment variables & secrets:** AWS Secrets Manager / Parameter
  Store, Azure Key Vault, or GCP Secret Manager.
- **Logs:** CloudWatch Logs / Azure Monitor / GCP Cloud Logging.
- **Monitoring:** CloudWatch Alarms / Azure Monitor Alerts / GCP Cloud
  Monitoring, watching the `/health` endpoint and error rates.

## CI/CD (suggested GitHub Actions workflow)

Add `.github/workflows/tests.yml` that runs on every push:

```yaml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt pytest
      - run: pytest tests/ -v
```

This gives the repository a visible, green "CI" badge and demonstrates
the CI/CD concept without needing any cloud deployment permissions.
