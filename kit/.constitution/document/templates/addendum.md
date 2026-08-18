---
type: addendum
parent: '{brief | prd}'  # which document this sits beside
initiative: '{slug}'     # omit when parent: brief
status: draft            # draft · reviewed · locked · superseded
created: '{YYYY-MM-DD}'
updated: '{YYYY-MM-DD}'
---

# Addendum — {product brief | PRD: initiative}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     Two homes, one shape:
       .what/_product-brief/addendum.md          beside the brief, born at G1
       .what/_prd/<initiative>/addendum.md       beside a PRD, born at G2

     Both already existed in this corpus and both were born without a template, which is why the one
     rule that governs them lived only in prd-guide.md prose.

     THAT RULE, STATED WHERE IT BELONGS: an addendum is NOT a change log. Revision History in the
     parent document is the change log. This holds depth that earned its place but does not fit the
     narrative — and putting a change record here means the client-facing document stops carrying its
     own history.

     WHAT GOES HERE: rejected-alternative rationale · options matrices · mechanism and transport
     thinking · technical how · in-depth personas · sizing data · anything the owner volunteered that
     would derail the narrative.

     WHAT MUST NOT: audit and override information — that is the memlog. A commercial fact — that is
     refused outright, per repo-guide.md. A promise — a promise stated only here is a promise nobody
     approved, because the gate reads the parent document.

     CAPTURED DURING THE CONVERSATION, not swept here at Finalize. Content moved here at the end is
     content nobody will find, because the reader was already told the parent was complete.

     WHAT BINDS LATER MOVES OUT. Something in here that turns out to bind a downstream document MUST
     be written into that document by the skill owning its layer, rather than cited from here forever.
     A citation into an addendum is a dependency on a file that was explicitly not gated. -->

## Rejected alternatives

<!-- One per subsection or one row each, and each MUST say why it lost. "We considered X" with no
     reason preserves nothing — the reason is the part memory loses first, and it is why the same
     option gets proposed again next quarter.

     A rejection that is expensive to revisit is a DEC-, not a row here. -->

| Option | Why it lost |
| --- | --- |

## Options weighed

<!-- Matrices, comparisons, and scoring that would swamp the parent document. State the criteria
     before the scores; a matrix whose criteria appeared after the winner is a justification. -->

## Mechanism and transport

<!-- Technical thinking that surfaced while deciding a promise. It is not a design — the SDD owns
     that — and it MUST NOT be cited as one. If a builder would be right to follow it, it belongs in
     .how/ and it has to get there through the skill that owns the layer. -->

## Sizing

<!-- Numbers behind an estimate: counts, throughput assumptions, mandays reasoning. Each MUST name
     where the figure came from. An unsourced number here reappears as a commitment somewhere else. -->

## Personas and research detail

<!-- Depth beyond what the parent needs. Raw research output MUST NOT be folded in — it stays in
     _bmad-output/ and is cited by path, which is stable because that folder is committed. -->
