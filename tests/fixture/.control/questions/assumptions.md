# Assumptions

**Loaded when:** swept once per gate; MAY be skipped.

The **default** class for a question. The agent takes the answer itself and records it here, one
row: the assumption, plus the cost if it turns out wrong. This file **holds nothing**.

A row here MUST move up to `blocking.md` the moment it passes one of the three tests that file
states. A row whose reversal costs less than the conversation about it MUST NOT be here at all —
the shipping default is the record.

The four rows below exist so the `open_by_whose` split in the generated status board is actually
exercised: one `owner`, one `run:`, one `frozen:`, and one with `Whose` left unset, which is the
state the report has to surface rather than swallow.

## Open

| id | Assumption | Cost if wrong | Whose | Taken | By |
|---|---|---|---|---|---|
| OQ-2 | An order code is eight characters | one value changes; nothing is built on the length | owner | 2026-01-10 | agent |
| OQ-3 | SQLite holds at this write volume | a store swap, so it MUST be measured before deep | run: load 10k orders, measure p95 write | 2026-01-10 | agent |
| OQ-4 | The order page needs no login at all | a promise change, and DEC-001 froze this area | frozen: DEC-001 | 2026-01-10 | agent |
| OQ-5 | The code is shown once and not emailed | a second delivery path, additive | — | 2026-01-10 | agent |
