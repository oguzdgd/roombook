# Architecture

## System overview
RoomBook is a meeting-room booking API: clients create/query Bookings for Rooms, get conflict
errors on overlap, and can ask for free time slots. V1 is a single-process FastAPI service with
in-memory storage, no auth, single office. Modular monolith (layered), not services — the domain
is small and a single process is enough for V1.

## Modules / components and ownership

| Module | Single responsibility | Owns |
|---|---|---|
| `api/` | HTTP layer: FastAPI routers, request/response schemas, status-code mapping | Wire format only |
| `service/` | Business rules: conflict detection (BR-1..BR-3), free-slot computation | Domain logic, no storage details |
| `repository/` | Storage access behind an interface/protocol; in-memory impl for V1 | Room/Booking storage |

## Communication rules
`api/` calls `service/` only. `service/` calls `repository/` through its interface only — never
holds storage internals. No module reaches two layers down (e.g. a router never touches
`repository/` directly).

## Forbidden dependencies (make them testable)
- `api/` never imports from `repository/` directly — only through `service/`.
- `service/` never imports FastAPI or Pydantic — it must stay framework-agnostic and unit-testable
  without spinning up the HTTP layer.
- `repository/` is the only module holding storage state; it is accessed only through its
  interface/protocol, so swapping in-memory for a real DB later touches one module.

## Deliberately out of scope
- Authentication/authorization (V1 assumes a trusted, single-office network).
- Multi-tenant/multi-office support.
- Persistent storage (in-memory only; data does not survive a restart).
