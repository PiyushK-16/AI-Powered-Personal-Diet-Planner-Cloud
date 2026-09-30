# Interview Preparation

## Q1. Explain your project.
I built an AI-Powered Personal Diet Planner as a cloud computing course
project. Users register and log in with JWT-based authentication, fill
in a demo profile, and generate a general educational diet plan through
an AI recommendation engine. Plans are saved to a cloud database and
users can upload related files to a cloud object storage layer. I built
it with a beginner-friendly, zero-cost stack — Flask, SQLite, and a
local storage folder standing in for a real cloud bucket — but I wrote
the data-access code behind two abstraction modules specifically so it
could be swapped for Firebase or AWS later without touching the rest of
the app.

## Q2. What cloud computing concepts does this project actually demonstrate?
Client-server architecture, REST APIs, authentication and authorization,
the difference between a cloud database and cloud object storage,
environment-variable-based secrets management, and fallback-safe
external API integration. I also documented — though didn't build —
how the same architecture maps onto autoscaling, load balancing, and
serverless deployment at higher scale.

## Q3. Why did you separate cloud storage from the cloud database?
They solve different problems. The database stores structured,
queryable data — user rows, plan rows. Object storage stores raw file
bytes addressed by a key/path. I implemented them as two separate
service modules (`database_service.py`, `storage_service.py`) so that
distinction is enforced in code, not just described in a diagram.

## Q4. How does your authentication work?
On registration, the password is hashed with Werkzeug's
`generate_password_hash` — never stored in plain text. On login, if the
hash matches, I issue a JWT signed with a server-side secret key, which
the client sends back as a Bearer token on every subsequent request. A
decorator on protected routes decodes and validates that token before
the route runs.

## Q5. How do you make sure one user can't see another user's data?
Every route that reads or deletes a plan or file first fetches the
record, then explicitly checks that `record.user_id` matches the
`user_id` decoded from the caller's JWT. If it doesn't match, I return
403 Forbidden rather than the data. I have an automated test
specifically for this (`test_user_cannot_access_other_users_plan`).

## Q6. Walk me through your REST API design.
It's resource-oriented: `/register`, `/login`, `/profile`,
`/generate-plan`, `/plans`, `/plans/<id>`, `/upload`, `/files`,
`/files/<id>`, using standard HTTP verbs — GET to read, POST to create,
PUT to update, DELETE to remove — and standard status codes: 201 for
created, 401 for auth failures, 403 for authorization failures, 404 for
missing resources, 409 for duplicate registration.

## Q7. How did you integrate AI, and what happens if the AI service is down?
I built two paths: a local rule-based engine that filters a small food
dataset by dietary preference, goal, and allergies, and an optional
external AI API path that constructs a structured prompt and validates
the response. If the API key isn't configured, the request fails, or the
response is malformed, the code catches that and transparently falls
back to the rule-based engine, so plan generation never actually fails
for the user.

## Q8. How would this scale to real production traffic?
At small scale, this exact setup is fine. Past a few hundred concurrent
users, I'd move off SQLite and local file storage to a managed database
and S3-style object storage, run multiple backend instances behind a
load balancer, add caching for the food dataset, and put a CDN in front
of the static frontend. None of the route code would need to change
because the database/storage access is already isolated behind those
two service modules.

## Q9. How is security handled, and what would you add for production?
Passwords are hashed, tokens are signed and expire, secrets come from
environment variables (never hardcoded), and uploads are restricted by
type and size. For a real production deployment I'd add HTTPS
termination (handled automatically by most cloud hosts), rate limiting
on auth endpoints, and encryption at rest via a managed database/bucket
instead of a local file.

## Q10. How did you test this, and what happens if the backend or database is unreachable?
I have an automated pytest suite covering registration, login,
protected routes, plan generation (including the AI-fallback path),
ownership enforcement, and file upload validation, plus a manual
20-case test table for scenarios like invalid files and duplicate
emails. On the frontend, every API call is wrapped in try/catch, so if
the backend is down, the user sees a readable error message on the page
instead of the app silently failing.
