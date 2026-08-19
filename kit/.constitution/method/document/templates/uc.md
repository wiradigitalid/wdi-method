---
type: uc
id: UC-{NN}                  # allocated from .control/registry/usecases.yaml
component: '{pc}'
satisfies: []                # FR ids — V2 checks every FR has at least one UC
critical: false              # true ONLY when it touches money, personal data, or an irreversible
                             # action. Nothing else — the two elastic criteria are repealed
created: '{YYYY-MM-DD}'
---

# UC-{NN} — {a sentence the user would say}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     THE TITLE RULE, and G3 asks it as a starred question: the title MUST be a sentence a user would
     actually say — "Sign up through an invitation link" — and MUST NOT be a system term —
     "Invitation attribution handler". A system-shaped title means the functional analysis has already leaked
     into design.

     WHICH USE CASES GET ONE OF THESE FILES IS DECIDED BY `mode`, NOT BY `critical`:
       catalog            none. The catalogue line in the SRS is the whole record
       outline · guarded  the use cases the component exists for, AT MOST 3
       deep               every UC marked `critical`
     `critical` therefore decides something only at `deep`. Everywhere else it is a label the estimate
     and the review read, and it MUST NOT be used to justify writing a file the mode does not ask for.

     At most EIGHT steps in the Basic Flow. A flow needing more is either two use cases, or it has
     started describing implementation. -->

## Trigger

<!-- What starts this. An actor doing something, a schedule, or an external event. -->

## Precondition

<!-- What MUST already be true. Authentication state, prior data, prior status. -->

## Main Flow

<!-- Numbered, one step per line, alternating actor and system. Keep to the happy path — branches
     go below or, if long, into a SCN- file in 05-scenarios/. No screen names, no endpoints, no
     table names: this is behaviour, not design. -->

1.
2.

## Alternate Flows

<!-- Branches that still end in success. Reference the main-flow step they leave from. -->

| From step | Condition | What happens |
| --- | --- | --- |

## Failure Flows

<!-- Branches that end without the goal. For a `critical` UC this section MUST answer "what happens
     if it fails halfway" — the paired SDD carries the technical side of the same question. -->

| From step | Failure | What the system does | What the user is left with |
| --- | --- | --- | --- |

## Outcome

<!-- The state the system and the user are left in when the main flow completes. -->

## Business Rules

<!-- BR ids that govern this use case, referenced not restated. The rules themselves live in
     02-rules/. -->
