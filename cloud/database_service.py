"""
cloud/database_service.py

CLOUD CONCEPT: Cloud Database
------------------------------
In production (Option B/C in the README), this module would talk to a
managed cloud database such as Firebase Firestore, Supabase (Postgres),
or AWS RDS, instead of a local SQLite file. The rest of the application
(routes, ai_engine) never touches SQL directly -- it only calls the
functions in this file. That separation is exactly how real cloud apps
are built: swap this one file for a cloud SDK and nothing else changes.

For this beginner-friendly, free-tier version, SQLite simulates the
"managed database" so the whole project is runnable with zero paid
services and zero external accounts.
"""

import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "diet_planner.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Creates the USERS, DIET_PLANS and USER_FILES tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            age INTEGER,
            height_cm REAL,
            weight_kg REAL,
            activity_level TEXT,
            dietary_preference TEXT,
            goal TEXT,
            allergies TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS diet_plans (
            plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            breakfast TEXT,
            lunch TEXT,
            snack TEXT,
            dinner TEXT,
            nutrition_summary TEXT,
            hydration_reminder TEXT,
            source TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_files (
            file_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            storage_path TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def now():
    return datetime.now(timezone.utc).isoformat()


# ---------------- USERS ----------------

def create_user(name, email, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, now()),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_user_by_email(email):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_profile(user_id, fields: dict):
    if not fields:
        return
    columns = ", ".join(f"{key} = ?" for key in fields.keys())
    values = list(fields.values()) + [user_id]
    conn = get_connection()
    conn.execute(f"UPDATE users SET {columns} WHERE user_id = ?", values)
    conn.commit()
    conn.close()


# ---------------- DIET PLANS ----------------

def create_diet_plan(user_id, breakfast, lunch, snack, dinner, nutrition_summary,
                      hydration_reminder, source):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO diet_plans
        (user_id, breakfast, lunch, snack, dinner, nutrition_summary, hydration_reminder, source, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, breakfast, lunch, snack, dinner, nutrition_summary, hydration_reminder, source, now()))
    conn.commit()
    plan_id = cur.lastrowid
    conn.close()
    return plan_id


def get_plans_for_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM diet_plans WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_plan_by_id(plan_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM diet_plans WHERE plan_id = ?", (plan_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_plan(plan_id):
    conn = get_connection()
    conn.execute("DELETE FROM diet_plans WHERE plan_id = ?", (plan_id,))
    conn.commit()
    conn.close()


# ---------------- FILES (metadata only -- actual bytes live in cloud storage) ----------------

def create_file_record(user_id, filename, storage_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_files (user_id, filename, storage_path, uploaded_at) VALUES (?, ?, ?, ?)",
        (user_id, filename, storage_path, now()),
    )
    conn.commit()
    file_id = cur.lastrowid
    conn.close()
    return file_id


def get_files_for_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM user_files WHERE user_id = ? ORDER BY uploaded_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_file_by_id(file_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM user_files WHERE file_id = ?", (file_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_file_record(file_id):
    conn = get_connection()
    conn.execute("DELETE FROM user_files WHERE file_id = ?", (file_id,))
    conn.commit()
    conn.close()
