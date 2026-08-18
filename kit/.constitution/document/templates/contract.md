---
type: contract
component: '{pc}'
lc: LC-{NNN}                 # the gateway this contract belongs to
direction: exposed           # exposed (we serve it) · consumed (a third party serves it)
created: '{YYYY-MM-DD}'
updated: '{YYYY-MM-DD}'
---

# Contract — {name}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     Lives in .how/<pc>/02-contracts/ when we expose it, .how/<pc>/03-integrations/ when we consume
     someone else's.

     Where a machine-readable spec exists — OpenAPI, protobuf, a schema file — THAT is the source of
     truth and this document MUST point at it rather than restate it. A restated schema drifts from
     the generated one within a wave. Write here only what the machine spec cannot carry. -->

## Source of truth

<!-- Path or URL to the machine-readable spec, or `none` if this contract is prose-only. -->

## Purpose

<!-- Which UC this serves, and what the caller is trying to achieve. -->

## Operations

<!-- One row per operation. Keep it thin — detail belongs to the machine spec. -->

| Operation | Purpose | Realizes |
| --- | --- | --- |

## Error behaviour

<!-- What the caller sees when things go wrong, and which of those are expected rather than
     exceptional. This is the part a generated spec carries worst and a caller needs most. -->

| Condition | Response | Caller should |
| --- | --- | --- |

## Compatibility

<!-- What counts as a breaking change here, and how it is announced. A contract with no stated
     breaking-change policy will be broken by someone acting in good faith. -->

## Constraints

<!-- Rate limits, size limits, timeouts, idempotency, ordering guarantees. Anything the caller MUST
     honour that the schema does not express. -->
