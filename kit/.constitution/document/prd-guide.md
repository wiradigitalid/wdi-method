---
status: Accepted
---

# PRD Guide

**Loaded when:** writing, updating, or validating a PRD

A PRD states what the product promises a user for one functional area. It does not describe how the
system behaves — that is `SRS-<pc>.md` — and it does not describe how it is built — that is
`SDD-<pc>.md`. When a sentence here could only be checked by reading code, it is in the wrong file.

## Home and life cycle

- One PRD per **initiative / functional area**. It MUST live at `.what/_prd/<initiative>/prd.md`,
  with `addendum.md` beside it. Set through `prd_output_path` and `run_folder_pattern` in
  `_bmad/custom/bmad-prd.toml`.
- A PRD is a **living document**. It MUST NOT be frozen, archived, or superseded when a release
  ships.
- Memlog MUST go to `.control/memlog/prd-<slug>.md` via `--path`, with the slug matching the folder.
  `--workspace` MUST NOT be used; it would leave a `.memlog.md` inside `.what/`.
- `run_folder_pattern` ships as `ISI-slug-inisiatif`, which is deliberately unusable. A PRD found in
  a folder by that name means the override was never pointed at a real initiative slug; `wdi-product`
  check 1 catches it, and it MUST be moved before G2.

## Update, or a new PRD

This is the decision the guide exists for, and the default is **Update**.

| Situation | What to do |
|---|---|
| Behaviour of an existing promise changes | Update |
| A promise turns out to be wrong and must be withdrawn | Update — and the withdrawal MUST be visible in Revision History, not silently deleted |
| A new feature that a reader would expect to find in this PRD | Update |
| The next release extends what this PRD already promises | Update. A release is never a reason on its own |
| A functional area a reader would not think to look for here | New PRD |

The test is the reader, not the calendar: **would someone looking for this promise open this
document?** If yes, it belongs here however large the change. A PRD MUST NOT be split because it
grew long — length is what `addendum.md` and feature grouping are for. It is split only when the two
areas have different readers, different stakeholders, or no shared vocabulary.

When a split is genuinely right, the existing PRD MUST keep its own IDs. `FR-N` never moves between
PRDs; the sequence is global to the product.

## One home, and what `.what/<pc>/` may take from it

A PRD is the **reference** the blueprint and each component work from, not a quarry. `.what/<pc>/` is distilled from it — the
same promise restated as behaviour, at the altitude a builder needs — and the PRD stays the one place
that promise lives.

- One PRD per initiative. Its content MUST NOT be split into pieces spread across `.what/<pc>/`, and
  a fragment MUST NOT be moved out of it. A promise with two homes drifts, and the copy people read
  is whichever they open first.
- `.what/<pc>/` MUST cite the `FR`/`NFR` it realises by ID rather than restating its text. A use case
  saying what the system does is derivation; a use case reproducing the PRD's paragraph is a second
  copy.
- One initiative MAY span several Product Components, and one component MAY serve several PRDs. That
  is why neither can absorb the other — `corpus-guide.md` owns the two-axis rule.
- When the distillation proves a promise cannot be behaved into, the PRD changes first, through
  `wdi-product` intent `update`. The SRS MUST NOT narrow it quietly.

## Revision History

- Every `update` run MUST add **exactly one row**, appended at the bottom — one row per **pass**, never
  one per correction.
- Rows MUST be written for someone who was not in the room — a client, a sponsor, an auditor. State
  what the promise now is, not which section was edited. "Payment retries now cap at three attempts,
  down from unlimited, because support could not explain the charges" is a row. "Updated §4.2" is
  not.
- The `Releases affected` column names the releases whose promise changed. It MUST match
  `target_release` on the affected `CAP` entries.
- A row MUST NOT be edited after the run that wrote it. A correction is a new row.

The boundary against the memlog matters and MUST NOT be collapsed:

| | Memlog | Revision History |
|---|---|---|
| Records | Every decision, change, override, assumption inside a run | What changed for the reader |
| Written | Continuously, by `memlog.py`, append-only | Once per run, by hand |
| Read by | The next run, and audits | Anyone opening the PRD |
| Lives in | `.control/memlog/` | The PRD itself |

Neither MUST be written in place of the other. A PRD whose only change record is the memlog is
unreadable to the people it was written for.

## Release lives in the registry

Release MUST NOT be expressed through this document's folder name, title, or frontmatter. It is
carried by:

| Field | Answers |
|---|---|
| `CAP.target_release` | Which release this capability is planned for. **The only place a promise's release is written** |
| `waves.yaml` `release` | Which release a wave of work belongs to — the execution side |

An `FR` MUST NOT carry a release of its own. It inherits one from its `CAP`, the same way it reaches
its `BG`: each child names only its parent. A capability whose requirements genuinely land in
different releases is two capabilities, and MUST be split rather than annotated.

Naming a release in prose as context MAY happen; the registry is what binds.

## Numbering

`BG-N`, `CAP-N`, `FR-N`, `NFR-N`, and `UJ-N` MUST be allocated from `.control/registry/requirements.yaml`
and MUST NOT restart at 1. The chain runs `BG → CAP → FR/NFR → UC → DEC → Story → Test`, and each
child names only its parent:

- Each feature in §4 MUST declare its `CAP-N` and the `BG-N` it serves.
- Each `FR` MUST declare its `capability`. Its goal is reached *through* the capability and MUST NOT
  be restated on the FR.
- Each `NFR` attaches to `BG` directly — it does not pass through `CAP`.

V15 checks both links. An FR with no capability is a promise nobody asked for.

## Proof of done — one, in business language

Every `FR` MUST carry **exactly one** proof of done: a sentence a Product Owner can check without opening
the code. It is what lets one `FR` become one testable unit of work, and it is why a wave is ideally one
`FR`.

**The double proof of done is repealed.** Requiring a business sentence *and* a technical restatement
naming status codes, limits, and payloads meant writing the same acceptance twice, in two vocabularies that
then drifted. The technical form is represented by the **test name** recorded in `waves.yaml`, where it is
checked mechanically (V4) instead of read.

A technical detail that genuinely has to be written down belongs in `addendum.md` or in the SDD, not in a
second proof of done.

## Wording versus promise — two different journeys

The distinction this guide exists to protect, and the one that produced three corrections that ended
"reported but not fixed":

| What changes | Route |
|---|---|
| The **wording** of an `FR` — a wrong cross-reference, a retired term, a word no longer consistent with an `applied` decision, while **the promise is the same** | The skill already at work fixes it directly. Recorded in the memlog, and **one** Revision History row per pass, not per correction |
| The **promise** of an `FR` — scope changes, the proof of done changes, an `FR` is retired or born | `wdi-product` intent `update`, and the change-control matrix in `delivery-flow-guide.md` says which gates reopen |

The guard against abuse is already in the Revision History rule: a row is written for someone who was not in
the room. A wording correction produces no row a client would find interesting, and that is precisely the
evidence it was not a change of promise.

Treating a wording fix as a promise change is not caution — it is what made three corrections queue behind a
gate and then get dropped.

## `owns:` — one entity, one writer

A domain entity MUST have exactly one owner authorised to write it. Usually that is a Product Component,
declared as `owns:` on its row in `components.yaml`; an `FR` from another PRD that needs to change the entity
MUST point at the owner's `FR` through `defers_to`, rather than promising to write it itself. V21 checks this.

**A few entities belong to no Product Component at all** — a product-wide setting, the trace of one shared
outbound channel. Those are owned by `_platform` through `platform_owns`, and the test for when that is
legitimate lives in `corpus-guide.md`. `_platform` has no `FR`, so an `FR` writing a platform-owned entity is
**not** asked for a `defers_to`; what binds instead is the shape documented in `cross-cutting.md`. Reaching
for `_platform` because the owner is hard to decide is the one use of it that the test refuses.

This is not theoretical: two PRDs have already collided semantically over one shared numbering series. Two
`FR` claiming write authority over the same entity, with neither pointing at the other, is a defect at the
moment it is written — not at the moment the code disagrees.

## Sections that stop being optional

BMad's Adapt-In Menu is conditional by design. Two clusters MUST always be present here:

| Cluster | Why it is required |
|---|---|
| **Cross-Cutting NFRs** | G2 passes on numbered FR **and NFR**. Each NFR MUST name `enforced_by` — an `AD-N`, a `DEC-`, or a test name. An NFR nothing enforces is decoration (V5) |
| **Constraints and Guardrails** | A constraint found at G4 costs a decision that one sentence here would have prevented |

Constraints MUST state only the delta beyond `.what/_product-brief/brief.md`, and MUST say "none
beyond the brief" when there is nothing. An absent section reads as "not checked".

Prerequisites MUST NOT be written as prose. An initiative blocked on another is a `depends_on`
between `CAP` entries.

## What goes to `addendum.md`

`addendum.md` is **not** a change log — Revision History is. It holds depth that belongs downstream
or earned its place but does not fit the narrative: rejected-alternative rationale, options matrices,
mechanism and transport decisions, technical how, in-depth personas, sizing data.

Content MUST be captured there *during* the conversation when the user volunteers it, not swept
there at Finalize. What in the addendum turns out to bind a later document MUST be written into that
document by the skill owning its layer, rather than cited from the addendum forever.

Audit and override information MUST NOT go to the addendum; it belongs in the memlog.

## Passing G2

- Every `[ASSUMPTION]` still unresolved at Finalize MUST be filed through `wdi-question` before the gate
  opens — into `assumptions.md` by default, and into `blocking.md` only through the three tests that file
  states. Filing one as blocking "to be safe" is the habit that produced 146 ids.
- `bmad-review` runs automatically through `doc_standards` on `prd.md` and `addendum.md`. It MUST
  have run before the gate — a Product Owner's 45 minutes are for deciding, not proofreading.
- The gate reads `prd.md` and `EXPERIENCE.md` together. A PRD that passes while the experience side
  is missing has answered only half of what G2 decides.
- Solution shape MUST NOT appear. If a sentence names a framework, a table, or a transport, it belongs in
  `addendum.md` or in the spine.
- Invoke through `wdi-product`, never `bmad-prd` directly — the wrapper is what checks the rules on this
  page and lands the memlog.
