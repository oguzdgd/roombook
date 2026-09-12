# Domain

## Ubiquitous language

| Term | Meaning | Notes / not to be confused with |
|---|---|---|
| Room | A bookable physical space with a capacity | Not a "location" or "building" |
| Booking | A reservation of one Room for one TimeSlot, with an organizer and title | Not "reservation" — use "Booking" everywhere (code, API, specs) |
| TimeSlot | A start/end pair, UTC, non-zero duration | Always tz-aware; never a naive datetime |
| Free slot | A gap between existing Bookings for a Room within a queried window | Computed, not stored |

## Business rules
- BR-1: No two Bookings for the same Room may overlap in time (touching/adjacent slots, where one
  ends exactly when the other starts, are NOT an overlap and are allowed).
- BR-2: A Booking's end must be strictly after its start.
- BR-3: A Booking cannot be created with a start time in the past.

## Key domain invariants
- A Room's Bookings, at any point in time, never contain two overlapping TimeSlots (BR-1 must hold
  after every write — this is the core invariant the conflict-detection logic protects).
- All stored timestamps are UTC; conversion to local time is a presentation concern, never a
  storage concern.
