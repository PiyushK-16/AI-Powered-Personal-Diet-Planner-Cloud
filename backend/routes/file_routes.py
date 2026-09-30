"""
backend/routes/file_routes.py
REST endpoints: POST /upload, GET /files, DELETE /files/<id>
"""

from flask import Blueprint, request, jsonify
from cloud import database_service as db
from cloud import storage_service as storage
from backend.utils.auth_utils import token_required

file_bp = Blueprint("file", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "txt", "csv"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB demo limit


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@file_bp.route("/upload", methods=["POST"])
@token_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request."}), 400

    uploaded = request.files["file"]
    if uploaded.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not _allowed_file(uploaded.filename):
        return jsonify({"error": "File type not allowed."}), 400

    file_bytes = uploaded.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return jsonify({"error": "File too large (max 5 MB in this demo)."}), 400

    storage_path = storage.upload_file(request.user_id, uploaded.filename, file_bytes)
    file_id = db.create_file_record(request.user_id, uploaded.filename, storage_path)

    return jsonify({"message": "File uploaded to cloud storage.", "file_id": file_id}), 201


@file_bp.route("/files", methods=["GET"])
@token_required
def list_files():
    files = db.get_files_for_user(request.user_id)
    return jsonify(files), 200


@file_bp.route("/files/<int:file_id>", methods=["DELETE"])
@token_required
def remove_file(file_id):
    record = db.get_file_by_id(file_id)
    if not record:
        return jsonify({"error": "File not found."}), 404
    if record["user_id"] != request.user_id:
        return jsonify({"error": "Forbidden."}), 403

    storage.delete_file(record["storage_path"])
    db.delete_file_record(file_id)
    return jsonify({"message": "File deleted."}), 200
