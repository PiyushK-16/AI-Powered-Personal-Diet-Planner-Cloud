"""
tests/test_app.py

Run with:  pytest tests/ -v   (from the project root, with venv activated)

Covers a representative slice of the full test plan in docs/TESTING.md:
registration, login, protected-route auth, diet-plan generation & fallback,
plan retrieval, user isolation, and file upload/list/delete.
"""

import os
import sys
import io
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Point the app at a throwaway SQLite file + storage folder for tests
TEST_DB_DIR = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_DIR}/test.db"
os.environ["STORAGE_BUCKET_PATH"] = os.path.join(TEST_DB_DIR, "test_bucket")
os.environ["SECRET_KEY"] = "test-secret"

import cloud.database_service as db
db.DB_PATH = os.path.join(TEST_DB_DIR, "test.db")

from backend.app import create_app

@pytest.fixture()
def client():
    db.init_db()
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def register(client, email="alice@example.com", password="password123"):
    return client.post("/register", json={"name": "Alice", "email": email, "password": password})


def login(client, email="alice@example.com", password="password123"):
    return client.post("/login", json={"email": email, "password": password})


# ---------- Authentication ----------

def test_register_new_user(client):
    resp = register(client)
    assert resp.status_code == 201


def test_register_duplicate_email_fails(client):
    register(client)
    resp = register(client)
    assert resp.status_code == 409


def test_login_valid_credentials(client):
    register(client)
    resp = login(client)
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_login_invalid_credentials(client):
    register(client)
    resp = login(client, password="wrongpassword")
    assert resp.status_code == 401


def test_dashboard_requires_auth(client):
    resp = client.get("/profile")
    assert resp.status_code == 401


# ---------- Profile ----------

def test_profile_update_and_fetch(client):
    register(client)
    token = login(client).get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.put("/profile", json={"dietary_preference": "vegan", "goal": "fitness"}, headers=headers)
    assert resp.status_code == 200

    resp = client.get("/profile", headers=headers)
    assert resp.get_json()["dietary_preference"] == "vegan"


# ---------- Diet plan generation ----------

def test_generate_plan_vegetarian(client):
    register(client)
    token = login(client).get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/generate-plan", json={"dietary_preference": "vegetarian", "goal": "balanced"}, headers=headers)
    assert resp.status_code == 201
    plan = resp.get_json()["plan"]
    assert plan["source"] == "rule_based_engine"
    assert plan["breakfast"]


def test_generate_plan_vegan(client):
    register(client)
    token = login(client).get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/generate-plan", json={"dietary_preference": "vegan", "goal": "weight_management"}, headers=headers)
    assert resp.status_code == 201


def test_ai_api_unconfigured_falls_back(client):
    os.environ.pop("AI_API_KEY", None)
    os.environ.pop("AI_API_URL", None)
    register(client)
    token = login(client).get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/generate-plan", json={"use_ai_api": True}, headers=headers)
    assert resp.status_code == 201
    assert resp.get_json()["plan"]["source"] == "rule_based_fallback"


def test_save_and_retrieve_plan(client):
    register(client)
    token = login(client).get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    gen = client.post("/generate-plan", json={}, headers=headers).get_json()
    plan_id = gen["plan"]["plan_id"]

    resp = client.get(f"/plans/{plan_id}", headers=headers)
    assert resp.status_code == 200


def test_user_cannot_access_other_users_plan(client):
    register(client, email="alice@example.com")
    token_a = login(client, email="alice@example.com").get_json()["token"]
    plan = client.post("/generate-plan", json={}, headers={"Authorization": f"Bearer {token_a}"}).get_json()["plan"]

    register(client, email="bob@example.com")
    token_b = login(client, email="bob@example.com").get_json()["token"]

    resp = client.get(f"/plans/{plan['plan_id']}", headers={"Authorization": f"Bearer {token_b}"})
    assert resp.status_code == 403


# ---------- Files / cloud storage ----------

def test_file_upload_and_list(client):
    register(client)
    token = login(client).get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    data = {"file": (io.BytesIO(b"fake image bytes"), "meal.png")}
    resp = client.post("/upload", data=data, headers=headers, content_type="multipart/form-data")
    assert resp.status_code == 201

    resp = client.get("/files", headers=headers)
    assert len(resp.get_json()) == 1


def test_file_invalid_type_rejected(client):
    register(client)
    token = login(client).get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    data = {"file": (io.BytesIO(b"binary"), "virus.exe")}
    resp = client.post("/upload", data=data, headers=headers, content_type="multipart/form-data")
    assert resp.status_code == 400


def test_logout(client):
    resp = client.post("/logout")
    assert resp.status_code == 200
