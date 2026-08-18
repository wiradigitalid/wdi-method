---
type: flow
component: '{pc}'
realizes: []                 # UC ids this flow implements
risky: false                 # true when money, irreversible state, or a third party is involved
created: '{YYYY-MM-DD}'
---

# Flow — {name}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     Lives in .how/<pc>/06-flows/. This is the TECHNICAL path — components calling components. The
     behavioural path the user experiences belongs to the UC in .what/<pc>/04-usecases/, and the two
     MUST NOT be merged: one is reviewed by the Product Owner, the other is not.

     A sequence diagram is written ONLY when `risky: true`. Drawing one for every flow costs more
     than it returns and buries the ones that matter. -->

## Realizes

<!-- The UC ids, and one line on which part of them this covers. -->

## Participants

<!-- The LC ids involved, in the order they enter. -->

## Happy path

<!-- Numbered, one hop per line: who calls whom, carrying what. -->

1.

## Sequence diagram

<!-- ONLY when risky: true. Author as valid mermaid — never an empty graph. Cut this section
     entirely otherwise. -->

## Failure modes

<!-- Per hop: what failure looks like, what the system does, and whether the operation can be
     retried safely. The retry column is the one that gets skipped and the one that causes double
     charges. -->

| Hop | Failure | System does | Safe to retry |
| --- | --- | --- | --- |

## Guarantees

<!-- Idempotency, ordering, at-least-once versus exactly-once, timeout budget. State what actually
     holds, not what would be nice. -->
