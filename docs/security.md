# Security

## Secrets
- Secrets never enter the repo, specs, prompts, or chat. `.env` is gitignored; provide `.env.example`.
- Agents never print secret values, even when debugging.

## Input & output
All request bodies validated via Pydantic models (reject malformed/oversized/wrong-typed payloads
with 422). Error responses never leak internals: no stack traces, no storage/module details, no
raw exception messages — only a safe, generic message plus the domain error code.

## AuthN / AuthZ
None in V1 — explicit non-goal, valid only under the assumption of a trusted, single-office
network with no public exposure. Adding auth/authz is a required prerequisite before any
multi-tenant, public, or internet-facing deployment (track as an ADR when that changes).

## Dependencies
New dependencies require review before adding: check maintenance status and known CVEs; pin
versions in `pyproject.toml`/lockfile. Prefer the standard library over a new dependency when
reasonable.

## Review lens
Security is a mandatory dimension of every independent review (see `prompts/review.md`), not a
separate afterthought phase.
