---
status: Accepted
---

# Brief Guide

**Loaded when:** writing, updating, or validating the product brief

The brief is the G1 artifact. It answers WHY — what problem exists, whose it is, and why it is worth
building. Its shape lives in `templates/brief.md`; the rules that shape MUST obey live here.

## Home and life cycle

- The brief MUST live at `.what/_product-brief/brief.md`, with `addendum.md` beside it. Both
  filenames are fixed by `bmad-product-brief` and MUST NOT be expected to change; only the folder is
  configurable.
- One brief per product, spanning every release. A second product MUST get its own repository — the
  singleton is what makes "what did we set out to solve" answerable at all.
- The brief is amended, never re-run into a second folder. `run_folder_pattern` is a constant for
  exactly this reason.
- The memlog MUST be written to `.control/memlog/brief.md` via `memlog.py --path`. `--workspace`
  MUST NOT be used — it would drop a `.memlog.md` inside `.what/`, and no memlog belongs in the
  corpus.

## Required sections

`templates/brief.md` carries the shape. Its preamble invites dropping sections that do not earn
their place; that invitation MUST NOT be applied to the eight below. Everything else in the template
MAY be dropped.

| Section | Why it cannot be dropped |
|---|---|
| Why | The narrative the gate is read against. Without it there is nothing to approve |
| The Problem | The gate decides on this |
| Who This Serves | Names who the problem belongs to |
| Goals | `BG-N` is the first link of the traceability chain; without it the chain has no root |
| Success Criteria | The measure that makes "done" checkable |
| Scope In / Scope Out | The boundary the PRD is later held against |
| Constraints | What design MUST NOT trade away |

`The Solution` and `What Makes This Different` stay optional — G1's seven questions never ask what is
being built, only whether the problem is real and worth the cost.

## Decision rules

- The brief MUST name exactly one problem, one **primary** user, and one measure of success. Other
  users and stakeholders are listed as secondary, not ranked away. If the primary cannot be chosen,
  discovery is not finished and the gate MUST NOT open.
- Every user and stakeholder who touches the product MUST appear in the table, including those who
  never open it — whoever pays for it, approves it, or is accountable for it.
- **Success Criteria MUST name exactly one measurable figure**, with a timeframe. This is a ★
  question at G1 and the section most often left as a mission statement instead — check 5 in
  `wdi-problem` exists because nothing else caught this.
- Goals MUST be numbered `BG-1`, `BG-2`, … and MUST NOT be numbered `G1`, `G2` — `G1`–`G5` name the
  five gates. `BG` IDs are cited downstream and MUST stay stable once written.
- **Goals is a pointer, not a list.** The section states `Goals — see goals.yaml → goals:` and
  nothing more. The statement for each `BG-N`, and an optional `why:` when a goal needs a reason
  beyond its statement, are authored straight into `.control/registry/goals.yaml` — landing
  that row is part of producing the brief, done by `wdi-problem` in the same pass, not a follow-up.
  A goal's text written in this section as well as in the registry is the same fact with two homes,
  and the copy people read is whichever they open first.
- Scope Out MUST be written as items. Leaving it to be inferred from absence defeats its only
  purpose, which is naming what someone will otherwise assume is coming.
- Per-release MVP scope belongs to the PRD, not here. This section states the product boundary — what
  belongs to the product at all, ever, not what ships first.

## Constraints — the one product-level section still authored here

BMad has no home for a product-wide constraint; this section exists because of that gap.

| Section | Boundary | When it moves |
|---|---|---|
| Constraints | What is fixed before design starts. Technical constraints that only shape implementation belong in `addendum.md` | A constraint that emerges from a design decision becomes `AD-N` in the spine and MUST NOT be appended here later |

## No Assumptions or Prerequisites section

Both are dropped from the brief entirely — they were the two sections with no home anywhere else in
the corpus, and now they do:

- An assumption goes through `wdi-question` into `.control/questions/assumptions.md`. State it so it
  could be proven false; one that starts to wobble MUST become a row in
  `.control/registry/risks.yaml` with an owner. An assumption nobody would act differently about is
  not worth listing.
- A prerequisite goes through `wdi-question` into `.control/questions/external.md`, naming who is
  being waited on and by when.

Neither is restated in the brief itself — the brief citing a row it does not own is exactly the second
copy this section used to be. A reader who wants both assembled with everything else reads the
generated deliverable, `.what-rendered/_product-brief/brief.md`, which renders the open rows from both files.

## No Product Component list

The brief MUST NOT carry one, and MUST NOT fill `product_components`. The slicing is born at the
**tail of G2** through `wdi-init` intent `component`, which reads the brief and every PRD and
registers what the owner accepts. A list written at G1 is guessed before there is anything to guess
from, and every later gate inherits the guess.

## Raw material

- Research, brainstorming, forge, and PRFAQ output MUST stay in `_bmad-output/`. It MUST NOT be
  folded into the brief, and MUST NOT be promoted into `.what/`.
- A `DEC-` or the PRD cites it by path instead. `_bmad-output/` is committed, so the path is stable.
- Those run folders MUST NOT be deleted **while an `update` intent still needs them** — it re-reads the
  original inputs. Once what they were read for is written down, they are retired under the three conditions
  in `corpus-guide.md`, and that retirement is a `DEC-`. "Never deleted" was never the rule; needing them
  was.

## Passing G1

- Dying cheap is a pass. A brief concluding the idea is not worth building is a valid G1 outcome,
  and the most profitable one.
- The brief MUST have been through `bmad-review` lenses structure + prose before it reaches the
  gate. Gate time is for deciding, not for catching mistakes. This one fires on its own — it is the
  *Polish* step of `bmad-product-brief`, driven by `doc_standards`, and nobody invokes it. Verifying
  that it actually ran is check 11 in `wdi-problem`.
- Invoke through `wdi-problem`, not `bmad-product-brief` directly — the wrapper is what checks the
  rules on this page.

## The generated deliverable

A complete, self-contained copy for a reader who should not need to open the registry lives at
`.what-rendered/_product-brief/brief.md` — written by `/wdi-report render brief`, which runs
`validate.py --generate`. It assembles this document's own sections verbatim, the goals rendered from
`goals.yaml`, and the open rows from `assumptions.md` and `external.md`. Nobody writes to it by
hand — it is regenerated, never hand-patched, the same as `blueprint.md` and `decisions.md`.
