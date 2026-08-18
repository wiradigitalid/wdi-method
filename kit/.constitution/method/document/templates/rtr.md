---
type: rtr
id: RTR-{wave}
wave: '{W<N>}'
size: L                  # the wave size that made this required
status: draft            # draft · reviewed · locked · superseded
created: '{YYYY-MM-DD}'
---

# RTR-{wave} — Retrospective, wave {W<N>}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     Home: .control/reports/RTR-<wave>.md, landed by wdi-build at wave close. Its old home
     .control/supplements/ is gone.

     REQUIRED on wave `L`. Advisory on `S` and `M`, and skipping it MUST be stated rather than left
     silent — V19 is advisory for exactly that reason. It is tied to wave SIZE, never to `mode`: depth
     of documents and volume of work are different things.

     THE SPEC FOLDER IS EPHEMERAL AND THIS IS NOT. bmad-retrospective writes RETROSPECTIVE.md inside
     the run folder; this is the archived form, and it is the only part that survives the wave.

     WRITE WHAT WAS LEARNED, NOT WHAT HAPPENED. A wave-by-wave narrative is recoverable from git; what
     is not recoverable is what somebody now knows and would otherwise forget. Every section below is
     one question, and a section with nothing under it MUST be cut. -->

## What this wave shipped

<!-- One line. Which FR, and whether the RTM rows for them are green. Not a story list. -->

## What took longer than expected, and why

<!-- G5's question 5. One cause, named concretely. "Underestimated" is not a cause. -->

## What the corpus got wrong

<!-- The section this method exists to feed. Every defect whose root_cause was `requirement` or
     `architecture` rather than code, by BUG- id — and what in .what/ or .how/ was wrong.

     This ratio is a fact about the METHOD, not about the team, and it is the only place it is
     recorded per wave. -->

| BUG- | Root cause | What was wrong upstream | Fixed where |
| --- | --- | --- | --- |

## What we would do differently

<!-- Only items with an owner and a next action. An observation nobody owns is not a finding; it is a
     feeling, and it MUST be cut rather than carried forward into the next wave's reading. -->

| Change | Owner | Where it lands |
| --- | --- | --- |

<!-- `Where it lands` MUST name a file or a skill. A retrospective item that lands nowhere is why
     retrospectives get a reputation for being theatre — and it is what makes the next one skippable. -->

## What is deliberately carried forward

<!-- Follow-ups accepted rather than fixed, each pointing at its OQ- or DEC-. Anything here that has
     no id is being lost right now. -->
