"""
cloud/storage_service.py

CLOUD CONCEPT: Cloud Object Storage (vs. Cloud Database)
----------------------------------------------------------
A cloud DATABASE (see database_service.py) stores structured rows/fields
(users, plans). Cloud OBJECT STORAGE stores raw files/blobs (images,
PDFs, exports) addressed by a path/key, not by SQL columns. Real
examples: AWS S3, Firebase Storage, Supabase Storage, Azure Blob Storage.

This module simulates an object storage BUCKET using a local folder
(STORAGE_BUCKET_PATH). The function names and behaviour (upload_file,
get_file_path, delete_file, list of "keys") intentionally mirror a real
cloud SDK such as boto3's S3 client, so swapping this file for real S3
calls later requires no changes anywhere else in the app.
"""

import os
import uuid

BUCKET_PATH = os.environ.get("STORAGE_BUCKET_PATH", "cloud_storage_bucket")


def _ensure_bucket_exists():
    os.makedirs(BUCKET_PATH, exist_ok=True)


def _user_prefix(user_id):
    """Objects are namespaced by user_id, like a folder/prefix in S3.
    This is what enforces user-specific storage isolation."""
    return os.path.join(BUCKET_PATH, f"user_{user_id}")


def upload_file(user_id, filename, file_bytes):
    """
    Simulates: s3_client.put_object(Bucket=..., Key=..., Body=file_bytes)
    Returns the storage_path (the 'object key') to save in the database.
    """
    _ensure_bucket_exists()
    user_dir = _user_prefix(user_id)
    os.makedirs(user_dir, exist_ok=True)

    # Avoid filename collisions -- similar to how cloud storage often
    # requires unique object keys.
    safe_name = f"{uuid.uuid4().hex}_{filename}"
    storage_path = os.path.join(user_dir, safe_name)

    with open(storage_path, "wb") as f:
        f.write(file_bytes)

    return storage_path


def read_file(storage_path):
    """Simulates: s3_client.get_object(...)['Body'].read()"""
    with open(storage_path, "rb") as f:
        return f.read()


def delete_file(storage_path):
    """Simulates: s3_client.delete_object(Bucket=..., Key=...)"""
    if os.path.exists(storage_path):
        os.remove(storage_path)


def file_exists(storage_path):
    return os.path.exists(storage_path)
