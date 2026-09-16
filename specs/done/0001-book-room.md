# Spec 0001 — Book a room with conflict rejection and free-slot suggestions

- Status: Shipped
- Mode: strict (from AGENTS.md at creation time)
- Plan: `specs/plans/0001-plan.md`

## Intent

Office staff need to book a meeting Room for a specific time window so the room is reliably
theirs and double-bookings don't happen. Success looks like: a valid request creates a Booking; a
request that overlaps an existing Booking for that Room is rejected with enough detail to see why
(the conflicting booking's time range and title) plus a short list of the nearest free
alternatives for that same room, so the requester can immediately retry instead of guessing. This
spec covers only booking creation and its conflict/suggestion behavior — it does not cover
editing/cancelling bookings, room management, recurring bookings, notifications, or any UI. Rooms
are assumed to already exist (provisioned via seed/fixture data); Room management is deliberately
out of scope and left to a future spec.

## Requirements

- A requester can submit a request to book a Room for a time window, giving an organizer and a
  title for the booking.
- A booking succeeds when the requested Room exists, the requested time window is valid (end
  strictly after start, start not strictly before the current time — BR-2, BR-3; a start exactly
  equal to the current time is NOT considered past), and the window does not overlap any existing
  Booking for that Room (BR-1; touching/adjacent slots are allowed, not a conflict).
- Submitted start/end times must be UTC-aware timestamps (an explicit UTC offset or equivalent).
  A naive timestamp with no timezone information is rejected as invalid input.
- The organizer is a free-text, non-empty string (e.g. a name); no further format is required.
- A booking that would overlap one or more existing Bookings for the same Room is rejected. The
  rejection identifies every existing Booking it overlaps with, in ascending order of start time,
  showing each one's time range and title (not who organized it).
- When a booking is rejected for overlapping, the response also suggests up to 3 alternative free
  time windows for the same Room. Each suggested window:
  - has the same duration as the originally requested booking,
  - starts at or after the originally requested start time (never earlier),
  - is free of any existing Booking for that Room,
  - falls within 7 days of the originally requested start time.
  If fewer than 3 such windows exist in that horizon, fewer are returned; if none exist, an empty
  list is returned alongside the rejection.
- A request for a Room that does not exist is rejected, distinguishably from both an overlap
  rejection and an invalid-time-window rejection (no free-slot suggestions are computed in this
  case, since there is no room to search).
- A request with an invalid time window (end not strictly after start, start strictly in the
  past, or a non-UTC-aware timestamp) is rejected, distinguishably from both an overlap rejection
  and a room-not-found rejection, and no free-slot suggestions are computed.
- A successfully created Booking can be distinguished from a rejected one by the caller without
  ambiguity.

## Constraints & out of scope

- Rooms are pre-existing (seed/fixture data). Creating, listing, updating, or deleting Rooms is
  OUT OF SCOPE for this spec.
- Editing or cancelling an existing Booking is OUT OF SCOPE.
- Recurring bookings are OUT OF SCOPE.
- Notifications (email, calendar invite, etc.) are OUT OF SCOPE.
- Multi-room suggestions (suggesting a different Room than the one requested) are OUT OF SCOPE —
  suggestions only ever concern the originally requested Room.
- Suggestions never look further than 7 days past the originally requested start time, and never
  suggest a window starting before the originally requested start time.
- No authentication/authorization (V1 assumes a trusted, single-office network — `docs/security.md`).
- No persistence across restarts (in-memory storage — `docs/architecture.md`).
- Concurrent booking requests racing against the same Room's conflict check are OUT OF SCOPE for
  this spec (V1 is a single in-memory process); this is an assumption, not a guarantee to test.

## Acceptance criteria

- [x] AC-1 — Booking a Room with a valid, non-overlapping time window, organizer, and title
      succeeds.
- [x] AC-2 — Booking a Room with a time window that exactly matches an existing Booking's window is
      rejected as a conflict.
- [x] AC-3 — Booking a Room with a time window that partially overlaps an existing Booking (new
      start falls inside the existing booking) is rejected as a conflict.
- [x] AC-4 — Booking a Room with a time window that partially overlaps an existing Booking (new end
      falls inside the existing booking) is rejected as a conflict.
- [x] AC-5 — Booking a Room with a time window that fully contains an existing Booking's window is
      rejected as a conflict.
- [x] AC-6 — Booking a Room with a time window that touches an existing Booking (new start equals
      existing end, or new end equals existing start) is NOT a conflict and succeeds.
- [x] AC-7 — A conflict rejection identifies every existing Booking it overlaps with (time range and
      title of each), not just the first one found, ordered ascending by start time.
- [x] AC-8 — A conflict rejection includes up to 3 suggested free time windows for the same Room,
      each with the same duration as requested, starting at or after the requested start, free of
      conflicts, within 7 days of the requested start.
- [x] AC-9 — When there are no existing Bookings for the Room at all, a valid request succeeds
      (no conflict to check against).
- [x] AC-10 — When the requested Room's remaining free capacity within the 7-day horizon cannot
      fit even one window of the requested duration, the conflict rejection's suggestion list is
      empty (not an error).
- [x] AC-11 — Booking a non-existent Room is rejected distinguishably from both a conflict
      rejection and an invalid-time-window rejection, with no suggestions computed.
- [x] AC-12 — Booking with an end time not strictly after the start time is rejected
      distinguishably from both a conflict rejection and a room-not-found rejection, with no
      suggestions computed.
- [x] AC-13 — Booking with a start time strictly before the current time is rejected
      distinguishably from both a conflict rejection and a room-not-found rejection, with no
      suggestions computed; a start time exactly equal to the current time is NOT rejected on
      this basis.
- [x] AC-14 — Booking with a missing or empty organizer or title is rejected as invalid input.
- [x] AC-15 — Booking with a start or end timestamp that lacks UTC/timezone information (a naive
      timestamp) is rejected as invalid input, distinguishably from a conflict rejection.

## Definition of Done

- [x] Every acceptance criterion mapped to proof (test or reproducible observation) — see
      criterion↔evidence table in the QA verification (2026-09-12); 26 tests green.
- [x] `scripts/check` green
- [x] Independent review done; real findings fixed, noise rejected with written rationale (5 real
      findings fixed across 4 commits; 1 low-severity finding rejected as noise — undocumented but
      functionally-correct plan deviation, no behavior change needed)
- [x] Docs / ADRs updated if behavior or architecture changed — no update needed; the one
      maintainability fix (composition-root wiring in `service/wiring.py`) reinforces the
      already-documented `docs/architecture.md` forbidden-dependency rule rather than changing it.
- [x] Spec moved to `specs/done/` (it becomes immutable there) — merged via
      [PR #1](https://github.com/oguzdgd/roombook/pull/1).

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | 0 (post-approval) |
| Fix rounds | 1 |
| Review findings: real / noise | 5 / 1 |
| Regressions introduced | 0 |
| Bugs escaped to production | N/A (not yet shipped) |
