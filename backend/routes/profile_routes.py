"""
backend/routes/profile_routes.py
REST endpoints: GET /profile, PUT /profile
"""

from flask import Blueprint, request, jsonify
from cloud import database_service as db
from backend.utils.auth_utils import token_required

profile_bp = Blueprint("profile", __name__)

ALLOWED_FIELDS = {
    "age", "height_cm", "weight_kg", "activity_level",
    "dietary_preference", "goal", "allergies",
}


@profile_bp.route("/profile", methods=["GET"])
@token_required
def get_profile():
    user = db.get_user_by_id(request.user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    user.pop("password_hash", None)  # never return the hash
    return jsonify(user), 200


@profile_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile():
    data = request.get_json(silent=True) or {}
    fields = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}

    if not fields:
        return jsonify({"error": "No valid profile fields provided."}), 400

    db.update_user_profile(request.user_id, fields)
    user = db.get_user_by_id(request.user_id)
    user.pop("password_hash", None)
    return jsonify({"message": "Profile updated.", "profile": user}), 200
