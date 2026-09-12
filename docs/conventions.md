# Conventions

## Language & framework versions
Python 3.12+, FastAPI, Pydantic v2. Lint: ruff. Types: mypy (strict). Tests: pytest.

## Naming
- Files/functions/variables: `snake_case`. Classes and Pydantic models: `PascalCase`.
- Tests mirror the module they cover: `tests/unit/test_<module>.py`, `tests/api/test_<router>.py`.
- Branch names and commits follow `docs/git.md`.

## Error handling
Domain errors are typed exceptions raised in `service/` (e.g. `BookingConflictError`,
`InvalidTimeSlotError`). `api/` maps them to HTTP status: conflict → 409, invalid input/validation
→ 422 (Pydantic-driven where possible), not found → 404. No raw stack traces or internal details
ever appear in a response body.

## Data rules
- Timestamps: UTC, timezone-aware `datetime`, ISO-8601 on the wire.
- IDs: UUID4 strings, generated server-side.
- Time ranges: `end` is exclusive of the next Booking's `start` (touching slots don't conflict —
  see BR-1).

## Enforced by tooling
- ruff: style and common bugs (wired into `scripts/check.conf`).
- mypy: type correctness (wired into `scripts/check.conf`).
- pytest: behavior (wired into `scripts/check.conf`).
