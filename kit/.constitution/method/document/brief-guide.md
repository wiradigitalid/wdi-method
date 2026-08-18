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
| The Problem | The gate decides on this. Without it there is nothing to approve |
| Who This Serves | Names who the problem belongs to |
| Goals | `BG-N` is the first link of the traceability chain; without it the chain has no root |
| Success Criteria | The measure that makes "done" checkable |
| Scope In / Scope Out | The boundary the PRD is later held against |
| Constraints | What design MUST NOT trade away |
| Assumptions | What the brief would be wrong without |
| Prerequisites | What blocks work before it starts |

## Decision rules

- The brief MUST name exactly one problem, one **primary** user, and one measure of success. Other
  users and stakeholders are listed as secondary, not ranked away. If the primary cannot be chosen,
  discovery is not finished and the gate MUST NOT open.
- Every user and stakeholder who touches the product MUST appear in the table, including those who
  never open it — whoever pays for it, approves it, or is accountable for it.
- Goals MUST be numbered `BG-1`, `BG-2`, … and MUST NOT be numbered `G1`, `G2` — `G1`–`G5` name the
  five gates. `BG` IDs are cited downstream and MUST stay stable once written.
- Scope Out MUST be written as items. Leaving it to be inferred from absence defeats its only
  purpose, which is naming what someone will otherwise assume is coming.
- Per-release MVP scope belongs to the PRD, not here. This section states the product boundary.

## The three product-level sections

BMad has no home for these; they exist because of that gap, and each has a rule about where it goes
when it stops being a statement.

| Section | Boundary | When it moves |
|---|---|---|
| Constraints | What is fixed before design starts. Technical constraints that only shape implementation belong in `addendum.md` | A constraint that emerges from a design decision becomes `AD-N` in the spine and MUST NOT be appended here later |
| Assumptions | What is believed but unverified, stated so it could be proven false | An assumption that starts to wobble MUST become a row in `.control/registry/risks.yaml` with an owner |
| Prerequisites | What MUST exist or be granted before work can start | Any prerequisite not yet satisfied MUST have a row in `.control/questions/external.md` naming who is being waited on and by when |

An assumption nobody would act differently about is not worth listing.

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
  that it actually ran is check 9 in `wdi-problem`.
- Invoke through `wdi-problem`, not `bmad-product-brief` directly — the wrapper is what checks the
  rules on this page.
