"""
backend/routes/plan_routes.py
REST endpoints: POST /generate-plan, GET /plans, GET /plans/<id>, DELETE /plans/<id>
"""

from flask import Blueprint, request, jsonify
from cloud import database_service as db
from backend.utils.auth_utils import token_required
from ai_engine.diet_engine import generate_diet_plan

plan_bp = Blueprint("plan", __name__)


@plan_bp.route("/generate-plan", methods=["POST"])
@token_required
def generate_plan():
    data = request.get_json(silent=True) or {}
    user = db.get_user_by_id(request.user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    dietary_preference = data.get("dietary_preference") or user.get("dietary_preference") or "vegetarian"
    activity_level = data.get("activity_level") or user.get("activity_level") or "moderate"
    goal = data.get("goal") or user.get("goal") or "balanced"
    allergies_raw = data.get("allergies", user.get("allergies") or "")
    allergies = [a.strip() for a in str(allergies_raw).split(",") if a.strip()]
    use_ai_api = bool(data.get("use_ai_api", False))

    plan = generate_diet_plan(dietary_preference, activity_level, goal, allergies, use_ai_api)

    plan_id = db.create_diet_plan(
        request.user_id,
        plan["breakfast"], plan["lunch"], plan["snack"], plan["dinner"],
        plan["nutrition_summary"], plan["hydration_reminder"], plan["source"],
    )
    plan["plan_id"] = plan_id

    return jsonify({
        "message": "Diet plan generated. This is a general educational wellness "
                    "example, not medical or clinical nutrition advice.",
        "plan": plan,
    }), 201


@plan_bp.route("/plans", methods=["GET"])
@token_required
def list_plans():
    plans = db.get_plans_for_user(request.user_id)
    return jsonify(plans), 200


@plan_bp.route("/plans/<int:plan_id>", methods=["GET"])
@token_required
def get_plan(plan_id):
    plan = db.get_plan_by_id(plan_id)
    if not plan:
        return jsonify({"error": "Plan not found."}), 404
    # AUTHORIZATION CHECK: user isolation -- users can only read their own data.
    if plan["user_id"] != request.user_id:
        return jsonify({"error": "Forbidden."}), 403
    return jsonify(plan), 200


@plan_bp.route("/plans/<int:plan_id>", methods=["DELETE"])
@token_required
def remove_plan(plan_id):
    plan = db.get_plan_by_id(plan_id)
    if not plan:
        return jsonify({"error": "Plan not found."}), 404
    if plan["user_id"] != request.user_id:
        return jsonify({"error": "Forbidden."}), 403

    db.delete_plan(plan_id)
    return jsonify({"message": "Plan deleted."}), 200
