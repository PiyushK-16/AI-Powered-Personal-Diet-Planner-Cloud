"""
backend/routes/auth_routes.py
REST endpoints: POST /register, POST /login, POST /logout
"""

from flask import Blueprint, request, jsonify
import re

from cloud import database_service as db
from backend.utils.auth_utils import hash_password, verify_password, generate_token

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required."}), 400
    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "Invalid email format."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    if db.get_user_by_email(email):
        return jsonify({"error": "An account with this email already exists."}), 409

    password_hash = hash_password(password)
    user_id = db.create_user(name, email, password_hash)

    return jsonify({"message": "Registration successful.", "user_id": user_id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = db.get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid email or password."}), 401

    token = generate_token(user["user_id"])
    return jsonify({
        "message": "Login successful.",
        "token": token,
        "user": {"user_id": user["user_id"], "name": user["name"], "email": user["email"]},
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    # JWTs are stateless: "logout" simply means the client discards the
    # token. In a production system you might additionally maintain a
    # short-lived token blocklist -- noted in docs/CLOUD_CONCEPTS.md.
    return jsonify({"message": "Logged out. Please discard your token client-side."}), 200
