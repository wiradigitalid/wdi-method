---
type: scn
id: SCN-{NN}
component: '{pc}'
attaches_to: UC-{NN}         # exactly one UC — a scenario that fits two is two scenarios
created: '{YYYY-MM-DD}'
---

# SCN-{NN} — {what this branch is}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     A scenario exists so a Use Case does not get fat. It is a long branch lifted out of one UC, and
     it MUST attach to exactly one. If it seems to belong to two, the UC boundary is wrong — fix that
     instead of duplicating the scenario.

     WRITTEN AT `mode: deep` ONLY. Below deep, a branch that will not fit stays inside its UC file or
     is not written; a scenario file MUST NOT be created to fill the slot. -->

## Where it branches

<!-- The UC and the numbered step this leaves from. -->

## Condition

<!-- What makes this branch taken rather than the main flow. -->

## Flow

<!-- Numbered, same discipline as the UC: behaviour only, no design shape. -->

1.

## Outcome

<!-- Where the user and the system end up, and whether they can rejoin the main flow. -->

## Why it is not in the UC

<!-- One line. If the honest answer is "it just felt long", it probably belongs back in the UC. -->
