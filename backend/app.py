"""
backend/app.py

Application entry point. Run with:  python backend/app.py
(run this command from the project ROOT folder, not from inside backend/)

CLOUD CONCEPT: REST API / Client-Server Architecture
------------------------------------------------------
This Flask app is the "server" half of the client-server model. The
frontend (browser) never talks to the database or storage directly --
it only calls these HTTP/JSON endpoints. That boundary is what lets you
swap the frontend (React, mobile app, etc.) or scale the backend
independently later, which is central to cloud application design.
"""

import os
import sys

# Allow `from cloud import ...` / `from ai_engine import ...` when running
# this file directly from the project root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

from cloud.database_service import init_db
from backend.routes.auth_routes import auth_bp
from backend.routes.profile_routes import profile_bp
from backend.routes.plan_routes import plan_bp
from backend.routes.file_routes import file_bp


def create_app():
    app = Flask(__name__)

    # CLOUD CONCEPT: CORS -- required because the frontend (served from a
    # different origin/port) and backend are separate applications, exactly
    # like in a real cloud deployment (e.g. frontend on Vercel, backend on
    # Render). Implemented manually here to keep the dependency list tiny.
    frontend_origin = os.environ.get("FRONTEND_ORIGIN", "*")

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = frontend_origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    @app.route("/<path:_any>", methods=["OPTIONS"])
    def cors_preflight(_any):
        return "", 204

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(file_bp)

    @app.route("/health", methods=["GET"])
    def health_check():
        # CLOUD CONCEPT: health checks are what load balancers / uptime
        # monitors poll to decide if an instance is healthy (Availability).
        return jsonify({"status": "ok", "service": "ai-diet-planner-backend"}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
