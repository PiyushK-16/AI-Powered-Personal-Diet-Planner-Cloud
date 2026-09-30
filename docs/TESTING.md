# Testing Strategy

## Automated Tests

`tests/test_app.py` (pytest) covers registration, login, protected-route
auth, profile updates, plan generation (vegetarian/vegan), AI-API
fallback, plan retrieval/ownership, file upload/validation, and logout.

```bash
pip install pytest
pytest tests/ -v
```

## Manual Test Case Table

Fill in "Actual Result" and "Pass/Fail" as you run these by hand against
your running local instance — this table is what recruiters/instructors
expect to see as evidence of real testing, beyond the automated suite.

| Test ID | Scenario | Input | Expected Result | Actual Result | Pass/Fail |
|---|---|---|---|---|---|
| T01 | New user registration | Valid unique name/email/password | 201, account created | | |
| T02 | Existing email registration | Email already registered | 409, "already exists" error | | |
| T03 | Valid login | Correct email/password | 200, JWT token returned | | |
| T04 | Invalid login | Wrong password | 401, "Invalid email or password" | | |
| T05 | Unauthorized dashboard access | No/invalid token on `/profile` | 401, access denied | | |
| T06 | Profile creation | Valid profile fields via `PUT /profile` | 200, profile saved | | |
| T07 | Diet plan generation | Authenticated, valid preferences | 201, full plan returned | | |
| T08 | Vegetarian preference | `dietary_preference=vegetarian` | Plan contains only vegetarian-tagged items | | |
| T09 | Vegan preference | `dietary_preference=vegan` | Plan contains only vegan-tagged items | | |
| T10 | Different goal | `goal=fitness` vs `goal=weight_management` | Plan/portion notes reflect the goal | | |
| T11 | AI API failure | `use_ai_api=true`, no `AI_API_KEY` set | Falls back silently, `source=rule_based_fallback` | | |
| T12 | Rule-based fallback | Same as T11 | Response still 201 with a complete plan | | |
| T13 | Save diet plan | Any successful `/generate-plan` call | Row appears in `diet_plans` table | | |
| T14 | Retrieve plan | `GET /plans/<id>` for own plan | 200, correct plan data | | |
| T15 | Upload file | Valid image/PDF under 5 MB | 201, file stored + row created | | |
| T16 | Retrieve file | `GET /files` after upload | File appears in list | | |
| T17 | Invalid file | `.exe` file or file over 5 MB | 400, upload rejected | | |
| T18 | User A cannot retrieve User B's data | User B's token on User A's `plan_id`/`file_id` | 403, "Forbidden" | | |
| T19 | Logout | `POST /logout` | 200, confirmation message | | |
| T20 | Cloud/database failure handling | Stop backend, call from frontend | Frontend shows a readable error message, doesn't crash | | |

## Notes on Failure-Handling Tests (T11, T12, T20)

- T11/T12 are exercised automatically by
  `test_ai_api_unconfigured_falls_back` in `tests/test_app.py` — the
  fallback is deterministic and doesn't require a real API key to test.
- T20 is a manual test: stop `python backend/app.py`, then try to
  generate a plan from the browser. `frontend/js/api.js`'s `try/catch`
  around every `apiRequest()` call is what turns a network failure into
  a readable on-page message instead of a silent crash.
