---
type: cross-cutting
scope: _platform
status: draft            # draft · reviewed · locked · superseded
created: '{YYYY-MM-DD}'
updated: '{YYYY-MM-DD}'
---

# Cross-Cutting — {product}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     Home: .how/_platform/cross-cutting.md. Blueprint output, born at G3 by wdi-blueprint intent
     `platform`. It exists at every `mode`.

     WHAT THIS FILE IS FOR: the things defined ONCE for the whole product and referenced everywhere
     else. Without a fixed shape they grow into four error formats, each of which looked reasonable
     on its own page — and that is not a hypothetical failure, it is the standard one.

     WHAT IT IS NOT: a place for rules. A statement that FORBIDS something across components is an
     AD-N and belongs in the spine. This file DESCRIBES what is shared. One fact, one home — a rule
     written here as well as in the spine gives the reader two versions to choose between. -->

## Error envelope

<!-- The shape of an error response, defined once. Every contract in .how/<pc>/02-contracts/
     REFERENCES this rather than restating it, and documents its 4xx and 5xx IN this envelope — never
     as an ad-hoc { "message": "..." }.

     Field names are English: they are machine-facing keys, and language-guide.md governs that. What
     the user reads is not a field name. -->

```json
```

| Field | Type | Means | Always present |
| --- | --- | --- | --- |

## Error catalogue

<!-- The codes this envelope may carry, and what each means to the caller. A code with no row here is
     a code nobody can handle. -->

| Code | HTTP | Means | Caller should |
| --- | --- | --- | --- |

## Platform-owned

<!-- REQUIRED as soon as anything is owned by `_platform` — a `platform_owns` entity, an inventory row,
     an LC. V21 checks it.

     Something lands here only when NO Product Component's promise is the reason it exists AND more than
     one component depends on it. corpus-guide.md owns that test, and it refuses the one use people
     reach for: "the owner is hard to decide".

     `Kind` is data · endpoint · job · screen, and the list is open. What is not open is the test.

     `_platform` has no `FR`, so there is no owner-FR for another component to point at. What replaces
     "one writer" is ONE DOCUMENTED SHAPE — stated here, once. A component that wants it different is
     proposing a change to this file, not making a local choice. -->

| What | Kind | Why no component explains it | Who touches it | The shape every toucher obeys |
| --- | --- | --- | --- | --- |

<!-- `Who touches it` names components, and naming more than one is a NORMAL state — that is half the
     reason the row is here. A single toucher is a signal it belongs to that component instead. -->

## Other product-level agreements

<!-- One subsection each, only for what genuinely crosses components. Candidates that earn a place:
     identity and session shape · timestamp and timezone convention · pagination shape ·
     idempotency key convention · logging fields · rate-limit response shape.

     Each MUST state where it is enforced. An agreement nothing enforces is a preference, and
     preferences belong in ../../../project/codebase-conventions-guide.md where nothing has to justify itself. -->

### {agreement}

**Applies to:** {which components or containers — `all` is a valid answer and MUST be written}
**Enforced by:** {a middleware, a shared helper, a test name — not "convention"}
