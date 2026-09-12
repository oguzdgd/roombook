# Testing

## The contract
- Every acceptance criterion maps to at least one test (criterion ↔ test map lives in the plan).
- Tests assert **behavior**, not implementation details or mere status codes.
- The whole suite runs inside `scripts/check` — one command, everywhere.

## Frameworks & layout
- Framework: pytest.
- `tests/unit/` — `service/` business rules, no HTTP layer involved.
- `tests/api/` — FastAPI `TestClient` tests per router (happy path + conflict + validation error).
- Run via `pytest -q` (wired into `scripts/check.conf`).

## What must be tested
- Every business rule (BR-1, BR-2, BR-3), including overlap edge cases: exact match, partial
  overlap (start inside/end inside), one slot fully containing another, and adjacent/touching
  slots (must NOT be flagged as a conflict).
- Free-slot computation: no bookings (whole window free), fully booked window, gaps at the
  start/middle/end of the window.
- Every endpoint: happy path, conflict (409), validation error (422), not-found (404).

## Protected-tests rule
Weakening asserts, deleting, or skipping tests to reach green is forbidden. A red test triggers
`prompts/recovery/red-test.md` (R-02) — first decide what is wrong: code, test, or spec.

## Determinism
Flaky tests are fixed, not retried or skipped — see R-03. Evidence of a fix: 5 consecutive green runs.
