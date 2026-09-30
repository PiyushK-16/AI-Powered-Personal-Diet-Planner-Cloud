"""
ai_engine/diet_engine.py

IMPORTANT DISCLAIMER
---------------------
This engine produces GENERAL, EDUCATIONAL wellness examples using
synthetic/demo logic. It is NOT medical or clinical nutrition advice
and must never be presented as such to real users.

VERSION A: generate_plan_rule_based()
    A deterministic, explainable recommendation engine driven by
    predefined rules over a small food dataset (food_data.json).
    This always works, needs no external service, and needs no API key.

VERSION B: generate_plan_ai_api()
    Demonstrates how a real AI/LLM API call would be structured
    (prompt construction -> request -> response validation).
    If AI_API_KEY / AI_API_URL are not configured, or the call fails
    for any reason, it automatically falls back to Version A.

generate_diet_plan() is the single entry point the backend calls.
It implements the FALLBACK LOGIC described in the project spec.
"""

import json
import os
import random
import requests

DATA_PATH = os.path.join(os.path.dirname(__file__), "food_data.json")

with open(DATA_PATH, "r") as f:
    FOOD_DATA = json.load(f)


def _normalize_preference(pref: str) -> str:
    pref = (pref or "").strip().lower().replace(" ", "_")
    mapping = {
        "veg": "vegetarian",
        "vegetarian": "vegetarian",
        "vegan": "vegan",
        "non_veg": "non_vegetarian",
        "non_vegetarian": "non_vegetarian",
        "nonvegetarian": "non_vegetarian",
    }
    return mapping.get(pref, "vegetarian")


def _normalize_goal(goal: str) -> str:
    goal = (goal or "").strip().lower().replace(" ", "_")
    if goal in ("weight_management", "weight_loss", "weight_gain"):
        return "weight_management"
    if goal in ("fitness", "fitness_oriented", "muscle_gain"):
        return "fitness"
    return "balanced"


def _pick_item(meal_list, diet, goal, allergies):
    allergies = [a.strip().lower() for a in (allergies or []) if a.strip()]
    candidates = [
        item for item in meal_list
        if diet in item["diet"]
        and goal in item["goal"]
        and not any(allergen in item["name"].lower() for allergen in allergies)
    ]
    if not candidates:
        # Relax the goal filter first, then relax allergy filter as a last resort,
        # so the demo always returns something rather than failing.
        candidates = [item for item in meal_list if diet in item["diet"]]
    if not candidates:
        candidates = meal_list
    return random.choice(candidates)


def generate_plan_rule_based(dietary_preference, activity_level, goal, allergies=None):
    """VERSION A: pure rule-based / local simulation. Always available offline."""
    diet = _normalize_preference(dietary_preference)
    norm_goal = _normalize_goal(goal)

    breakfast = _pick_item(FOOD_DATA["breakfast"], diet, norm_goal, allergies)
    lunch = _pick_item(FOOD_DATA["lunch"], diet, norm_goal, allergies)
    snack = _pick_item(FOOD_DATA["snack"], diet, norm_goal, allergies)
    dinner = _pick_item(FOOD_DATA["dinner"], diet, norm_goal, allergies)

    total_calories = breakfast["calories"] + lunch["calories"] + snack["calories"] + dinner["calories"]

    activity_note = {
        "low": "Your activity level is low, so portions lean lighter.",
        "moderate": "Your activity level is moderate, giving a balanced calorie spread.",
        "high": "Your activity level is high, so slightly larger, protein-forward portions are suggested.",
    }.get((activity_level or "").strip().lower(), "Portions are set at a general, balanced level.")

    nutrition_summary = (
        f"Approximate total: {total_calories} kcal for the day. {activity_note} "
        "This is a general educational estimate, not a medical calculation."
    )
    hydration_reminder = "Reminder: aim for roughly 6-8 glasses of water throughout the day (general wellness guideline, adjust for your own needs)."

    return {
        "breakfast": breakfast["name"],
        "lunch": lunch["name"],
        "snack": snack["name"],
        "dinner": dinner["name"],
        "nutrition_summary": nutrition_summary,
        "hydration_reminder": hydration_reminder,
        "source": "rule_based_engine",
    }


def _build_ai_prompt(dietary_preference, activity_level, goal, allergies):
    """Constructs a structured prompt for an external AI API (Version B)."""
    return (
        "You are a general wellness assistant generating an EDUCATIONAL, "
        "non-medical example daily meal plan. Respond ONLY as JSON with keys: "
        "breakfast, lunch, snack, dinner, nutrition_summary. "
        f"User preferences -> dietary_preference: {dietary_preference}, "
        f"activity_level: {activity_level}, goal: {goal}, "
        f"allergies_or_dislikes: {allergies or 'none'}."
    )


def generate_plan_ai_api(dietary_preference, activity_level, goal, allergies=None):
    """
    VERSION B: Optional external AI API call.

    Demonstrates: prompt construction -> API request -> response validation.
    Raises an exception on any failure so the caller (generate_diet_plan)
    can apply the fallback logic. No API key is ever hardcoded here --
    it is read from an environment variable.
    """
    api_key = os.environ.get("AI_API_KEY")
    api_url = os.environ.get("AI_API_URL")

    if not api_key or not api_url:
        raise RuntimeError("AI API not configured (AI_API_KEY/AI_API_URL missing).")

    prompt = _build_ai_prompt(dietary_preference, activity_level, goal, allergies)

    response = requests.post(
        api_url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"prompt": prompt, "max_tokens": 300},
        timeout=8,
    )
    response.raise_for_status()
    data = response.json()

    # --- Response validation ---
    required_keys = {"breakfast", "lunch", "snack", "dinner", "nutrition_summary"}
    if not required_keys.issubset(data.keys()):
        raise ValueError("AI API response missing required fields.")

    data["hydration_reminder"] = (
        "Reminder: aim for roughly 6-8 glasses of water throughout the day."
    )
    data["source"] = "ai_api"
    return data


def generate_diet_plan(dietary_preference, activity_level, goal, allergies=None, use_ai_api=False):
    """
    Single entry point used by the backend routes.

    FALLBACK LOGIC:
        IF use_ai_api is True AND the AI API call succeeds -> use its result.
        IF the AI API is not configured, unreachable, or returns something
        invalid -> silently fall back to the local rule-based engine so the
        project remains fully functional without any paid service.
    """
    if use_ai_api:
        try:
            return generate_plan_ai_api(dietary_preference, activity_level, goal, allergies)
        except Exception:
            # Fallback triggered -- rule-based engine guarantees a result.
            plan = generate_plan_rule_based(dietary_preference, activity_level, goal, allergies)
            plan["source"] = "rule_based_fallback"
            return plan

    return generate_plan_rule_based(dietary_preference, activity_level, goal, allergies)
