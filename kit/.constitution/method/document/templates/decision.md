---
type: decision
id: DEC-{NNN}                # allocated from .control/registry/decisions.yaml, globally
status: draft                # draft · accepted · applied · superseded · rejected
touches: []                  # empty until applied; then the files this decision actually changed
supersedes: null
superseded_by: null
created: '{YYYY-MM-DD}'
---

# DEC-{NNN} — {the decision, stated as what now holds}

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     Three sections are required: Decision, Why, Cost. The three below them are required only when
     this decision reaches a Product Component whose `risk_accepted` is `low`. Anywhere else, drop
     the ones you have nothing to put under — a heading with nothing beneath it reads as an omission.

     A `DEC-` records ONE event. It freezes when its status reaches `applied`, not when it is
     accepted. A changed mind after that produces a new `DEC-`, and this one becomes `superseded`
     with a pointer forward.

     Do not confuse this with AD-N in the architecture spine, which is a living rule edited in place.

     Add `type:` to the frontmatter when it is useful — `risk-acceptance`, `course-correction`. -->

## Decision

<!-- One sentence, present tense, quotable into a rule. Not "we will". -->

## Why

<!-- The context that forced it. A few lines, written so a reader in a year needs no other document.
     The memlog is where the reasoning lives, and the memlog MUST NOT be quoted into the corpus.
     If this came out of a third failed fix attempt, say so — that is the signal
     wdi-systematic-debugging exists to raise. -->

## Cost

<!-- What becomes harder. A decision with only benefits was not thought through. -->

## Alternatives

<!-- Required only at `risk_accepted: low`. What else was considered, and why each lost.
     "We considered X" with no reason is not an alternative. -->

| Option | Why not |
| --- | --- |

## Reversal trigger

<!-- Required only at `risk_accepted: low`. The observable condition that makes revisiting this
     correct. A decision with no reversal condition is a belief. -->

## Trace

<!-- Required only at `risk_accepted: low`. Where this came from. What it landed in belongs in
     `touches:` above, not here — one fact, one home. -->

| | |
| --- | --- |
| Meeting note | `.control/meetings/{YYYY-MM-DD-slug}.md` — or `—` |
| Open question | `OQ-{n}` — or `—` |
| Source material | path, or `—` |
