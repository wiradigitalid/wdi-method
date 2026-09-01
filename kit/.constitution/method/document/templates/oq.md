---
type: oq
id: OQ-{n}
component: '{pc}'            # or `_platform`
blocks: []                   # gate, FR, UC, or ticket ids — empty means it blocks nothing
owner: '{who can answer}'
by_when: '{gate or date}'
status: open                 # open · answered
created: '{YYYY-MM-DD}'
---

# OQ-{n} — {the question, as one answerable sentence}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     Most open questions need only a line in one of the four lists in .control/questions/. This file
     exists for the
     few whose discussion outgrows one line; the list then keeps a one-line pointer here.

     The title MUST be answerable. "How should referrals work?" is a topic, not a question. -->

## Why it is open

<!-- What makes this undecidable right now — missing information, a stakeholder who has not
     answered, a dependency that has not landed. -->

## What it blocks

<!-- Concretely. If it blocks nothing, say so — a question that blocks nothing MAY still be
     registered, but mixing blockers with curiosities makes the list useless exactly when it
     matters. -->

## Options considered

<!-- Only if any exist. A proposed answer for the owner to confirm is useful; recording it as
     settled is not. -->

## Answer

<!-- Filled when it closes, WITH the date and who answered. The entry is closed in place and MUST
     NOT be deleted — the record of what was once uncertain is what stops it being reopened in three
     months.

     If the answer amounts to a decision that is expensive to reverse, closing here is not enough:
     route it to wdi-decision so a DEC- carries what was chosen and what it cost. -->
