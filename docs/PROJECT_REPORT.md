# Project Report: AI-Powered Personal Diet Planner with Cloud Storage

## Abstract
This project implements a cloud-oriented, full-stack web application
that generates general, educational diet-plan examples from synthetic
user profiles, storing structured data in a cloud-style database and
files in simulated cloud object storage. It demonstrates core cloud
computing concepts — authentication, REST APIs, database vs. object
storage, fallback-safe AI integration, and deployment — at zero cost.

## Introduction
Cloud computing coursework benefits from a hands-on project that touches
every layer of a real cloud application. This project was built to do
exactly that, using free-tier and local/simulated services so it is
fully runnable without any paid account.

## Problem Statement
Users seeking general meal-planning ideas lack a centralized, portable
place to store their preferences and generated plans. This project
provides an authenticated, cloud-style application where that data
persists centrally rather than only in one browser session.

## Objectives
1. Implement secure user authentication and per-user data isolation.
2. Demonstrate the distinction between a cloud database and cloud
   object storage with real, separate code paths.
3. Build an AI-assisted recommendation engine with automatic fallback.
4. Provide a complete, tested, documented, deployable REST API + frontend.

## Existing System
Most simple diet-tracking demos either hardcode data client-side (no
persistence, no multi-device access) or require a paid AI/cloud
subscription to run at all, which makes them unsuitable as a runnable
student portfolio piece.

## Proposed System
A three-tier application (frontend, Flask REST API, cloud data layer)
where the data layer is written behind an abstraction
(`cloud/database_service.py`, `cloud/storage_service.py`) so it can run
on free/local infrastructure now and be swapped for managed cloud
services later without touching business logic.

## Cloud Computing Concepts
See `docs/CLOUD_CONCEPTS.md` for the full concept-to-code mapping.

## Technology Stack
Python Flask, SQLite (simulating a cloud database), a local folder
(simulating cloud object storage), PyJWT for authentication, and vanilla
HTML/CSS/JavaScript for the frontend. See `docs/ARCHITECTURE.md` for the
Option A/B/C comparison.

## System Architecture
See the architecture diagram and data-flow walkthrough in `README.md`
and `docs/ARCHITECTURE.md`.

## Data Flow
User → Frontend → Authentication → REST API → AI Engine / Cloud
Database / Cloud Storage → Dashboard. Full sequence in
`docs/ARCHITECTURE.md#complete-data-flow`.

## Database Design
Three tables — `users`, `diet_plans`, `user_files` — with one-to-many
relationships from `users`. Full schema in `backend/models/schema.py`.

## Cloud Storage Design
Files are namespaced by `user_{id}` folders inside the storage bucket
path, mirroring how a real object-storage bucket would prefix keys per
user, with metadata (filename, path, timestamp) tracked separately in
the database.

## AI Recommendation Logic
A rule-based engine filters a demo food dataset by dietary preference,
goal, and allergies (Version A). An optional external AI API path
(Version B) is implemented with structured prompt construction and
response validation, and automatically falls back to Version A on any
failure, error, or missing configuration.

## Authentication
JWT-based stateless authentication with hashed passwords. Every
data-owning endpoint independently re-verifies that the requester owns
the record being accessed or modified.

## API Design
12 REST endpoints across auth, profile, plan, and file resources — full
table in `README.md#rest-api-reference`.

## Implementation
Implemented in Python (Flask) with a clean separation between routes,
authentication utilities, the AI engine, and the cloud data-access layer,
enabling each concern to be tested, replaced, or scaled independently.

## Testing
Automated pytest suite (`tests/test_app.py`) plus a 20-case manual test
plan (`docs/TESTING.md`) covering functional correctness, AI-fallback
behavior, and the user-isolation security rule.

## Cloud Deployment
Two deployment paths documented: a free-tier path (Render/Netlify) and
an enterprise-cloud path (AWS/Azure/GCP) — see `docs/DEPLOYMENT.md`.

## Security
Password hashing, JWT auth, environment-variable-based secrets, upload
validation, and per-user authorization — full checklist in
`docs/CLOUD_CONCEPTS.md#security-checklist`.

## Scalability
Discussed at 10 / 1,000 / 100,000-user scale with concrete architectural
changes at each tier — `docs/ARCHITECTURE.md#scalability`.

## Results
A fully functional, automatically-tested application demonstrating every
required cloud concept, runnable with zero cost and zero external
accounts.

## Advantages
Zero cost to run and evaluate; clean separation of concerns that
directly maps to how the system would be migrated to a real managed
cloud; automatic AI fallback means the demo never fails due to a missing
paid API key.

## Limitations
SQLite and local-folder storage do not provide the durability,
concurrency, or encryption-at-rest guarantees of a managed cloud
database/bucket; the AI engine is rule-based by default rather than a
full LLM integration.

## Future Scope
Migrate the two cloud abstraction modules to Firestore/Supabase and
S3/Firebase Storage; add refresh tokens; add calorie/macro trend
tracking over time.

## Conclusion
This project meets the stated goals of a Cloud Computing course
project: it is cloud-oriented in design, fully working, tested,
documented, and deployable, while remaining free and beginner-friendly
to build and run.
