"""
backend/models/schema.py

This project keeps all actual database calls inside cloud/database_service.py
(the "swap this file for a real cloud DB SDK" boundary described there).
This module simply documents the logical schema/design in one place for
readability and for the README's Database Design section.

USERS
  user_id (PK), name, email (unique), password_hash, age, height_cm,
  weight_kg, activity_level, dietary_preference, goal, allergies, created_at

DIET_PLANS
  plan_id (PK), user_id (FK -> users.user_id), breakfast, lunch, snack,
  dinner, nutrition_summary, hydration_reminder, source, created_at

USER_FILES
  file_id (PK), user_id (FK -> users.user_id), filename, storage_path,
  uploaded_at

Relationships:
  users (1) ---- (many) diet_plans
  users (1) ---- (many) user_files

User-specific access: every plan_routes.py / file_routes.py handler
checks that record.user_id == request.user_id (the id decoded from the
caller's JWT) before returning or deleting data -- this is what stops
User A from reading User B's rows through the API.
"""
