"""
backend/utils/auth_utils.py

CLOUD CONCEPT: Authentication vs Authorization
------------------------------------------------
Authentication = proving WHO you are (login with email/password).
Authorization   = controlling WHAT you're allowed to access
                   (e.g. only your own diet plans and files).

This module implements both:
  - Password hashing (never store plain-text passwords).
  - JWT (JSON Web Token) issuing/verification for stateless auth,
    similar to how Firebase Auth / AWS Cognito issue tokens.
  - A @token_required decorator that acts as the "authorization gate"
    on every protected route, injecting the authenticated user_id.
"""

import os
import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-secret-change-me")
JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))


def hash_password(plain_password: str) -> str:
    return generate_password_hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, plain_password)


def generate_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


def token_required(f):
    """Protects a route: requires 'Authorization: Bearer <token>' header."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header."}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired. Please log in again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token."}), 401

        request.user_id = payload["user_id"]
        return f(*args, **kwargs)
    return wrapper
