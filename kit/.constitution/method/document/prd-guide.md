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
| A promise turns out to be wrong and must be withdrawn | Update — and the withdrawal MUST be visible in Revision History, not silently deleted. This is the one mandated history line in the method, and it survives because it is **business** history read by someone outside the room, not a record that a document changed |
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
| `specs.yaml` `release` | Which release a spec of work belongs to — the execution side |

An `FR` MUST NOT carry a release of its own. It inherits one from its `CAP`, the same way it reaches
its `BG`: each child names only its parent. A capability whose requirements genuinely land in
different releases is two capabilities, and MUST be split rather than annotated.

Naming a release in prose as context MAY happen; the registry is what binds.

## Numbering

`BG-N` is allocated from `.control/registry/goals.yaml`; `CAP-N`, `FR-N`, `NFR-N`, and `UJ-N` from this initiative's own `.control/registry/requirements-<slug>.yaml` — one file, one writer, one gate
and MUST NOT restart at 1. The chain runs `BG → CAP → FR/NFR → UC → DEC → Ticket → Test`, and each
child names only its parent:

- Each feature in §3 MUST declare its `CAP-N` and the `BG-N` it serves.
- Each `FR` MUST declare its `capability`. Its goal is reached *through* the capability and MUST NOT
  be restated on the FR.
- Each `NFR` attaches to `BG` directly — it does not pass through `CAP`.

`chain-links` checks both links. An FR with no capability is a promise nobody asked for.

## `FR`/`NFR` text lives in the registry, not in this document

The PRD cites `FR-N`/`NFR-N` under each feature's **Realizes:** line. It MUST NOT also write the
statement, the proof of done, or the enforcer in prose — those fields live on the id's own row in
`requirements-<slug>.yaml`, and landing them there is part of `wdi-product` producing this PRD, not a
follow-up. A promise written in both places is one fact with two homes, and the copy a reader trusts
is whichever they open first.

Every `FR` MUST carry **exactly one** proof of done: a sentence a Product Owner can check without opening
the code. It is what lets one `FR` become one testable unit of work, and it is why a spec is ideally one
`FR`.

**The double proof of done stays repealed.** A business sentence *and* a technical restatement naming
status codes, limits, and payloads meant writing the same acceptance twice, in two vocabularies that
then drifted. The technical form is represented by the **test name** recorded in `specs.yaml`, where it
is checked mechanically (`ticket-has-test`) instead of read.

A technical detail that genuinely has to be written down belongs in `addendum.md` or in the SDD, not in
a second proof of done — and not in this document's prose either.

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
MUST point at the owner's `FR` through `defers_to`, rather than promising to write it itself. `entity-one-writer` checks this.

**A few entities belong to no Product Component at all** — a product-wide setting, the trace of one shared
outbound channel. Those are owned by `_platform` through `platform_owns`, and the test for when that is
legitimate lives in `corpus-guide.md`. `_platform` has no `FR`, so an `FR` writing a platform-owned entity is
**not** asked for a `defers_to`; what binds instead is the shape documented in `cross-cutting.md`. Reaching
for `_platform` because the owner is hard to decide is the one use of it that the test refuses.

This is not theoretical: two PRDs have already collided semantically over one shared numbering series. Two
`FR` claiming write authority over the same entity, with neither pointing at the other, is a defect at the
moment it is written — not at the moment the code disagrees.

## Sections that stop being optional

BMad's Adapt-In Menu is conditional by design. Two clusters MUST always be present here, and are in
the Essential Spine rather than the Adapt-In menu for exactly that reason:

| Cluster | Section | Why it is required |
|---|---|---|
| **Cross-Cutting NFRs** | §6 | G2 passes on numbered FR **and NFR**. Each NFR MUST name `enforced_by` — an `AD-N`, a `DEC-`, or a test name. An NFR nothing enforces is decoration (`nfr-has-enforcer`) |
| **Constraints and Guardrails** | §7 | A constraint found at G4 costs a decision that one sentence here would have prevented |

Constraints MUST state only the delta beyond `.what/_product-brief/brief.md`, and MUST say "none
beyond the brief" when there is nothing. An absent section reads as "not checked".

Prerequisites MUST NOT be written as prose. An initiative blocked on another is a `depends_on`
between `CAP` entries.

## §1 Why This Initiative is a delta

BMad's default §1 Vision writes the product's vision from scratch, in the same 2-3 paragraph shape as
the brief's own narrative. On the first PRD a product ever gets, that duplicates `Why` in
`.what/_product-brief/brief.md` almost sentence for sentence — the same defect Executive Summary and
Vision had against each other inside the brief before they were merged.

§1 states only what THIS initiative changes, adds, or unlocks beyond what the brief's `Why` already
says. A product with a single initiative MAY reduce this to one sentence pointing back to the brief.
The full narrative is never written twice.

## Sections dropped from BMad's default, and where each fact actually lives

Four of BMad's default sections carry no content specific to this PRD, or duplicate a fact this method
already gives a home. Each is dropped rather than left conditional:

| Dropped section | Where the fact lives instead |
|---|---|
| Document Purpose | Nowhere — it explained what a PRD is in general, true of every PRD, so it held no information specific to this one |
| Glossary | `.control/product-glossary.md`. A term this PRD needs that is not there yet goes through `wdi-question` in the same pass — it is never added to a document-local glossary `wdi-blueprint` will not read at G3 |
| Non-Goals | The product's own Scope Out (`.what/_product-brief/brief.md`), for what the product never does, and §4.2 Out of Scope for MVP, for what this release defers. A third list restating both is the same fact twice |
| Open Questions | `.control/questions/`, the moment the question is found — not batched into a section read once at Finalize |
| Assumptions Index | `.control/questions/assumptions.md`, through `wdi-question`, before G2. The inline `[ASSUMPTION]` tag stays as a marker for the conversation that produced it; it is not also an index entry |

A reader who wants all of these assembled with the PRD's own content reads the generated deliverable —
see below — rather than a hand-maintained index inside this document.

## The generated deliverable

A complete, self-contained copy for a reader who should not need to open the registry or
`.control/questions/` lives at `.what-rendered/_prd/<slug>/prd.md` — written by `/wdi-report render prd`,
which runs `validate.py --generate`. It assembles this PRD's own prose verbatim, the
Vision from the brief's `Why` plus §1's delta, the `FR`/`NFR` rows from `requirements-<slug>.yaml`, the
Glossary terms this PRD actually uses, Non-Goals from the brief's Scope Out and §4.2, and the open
rows from `.control/questions/` that cite one of this PRD's ids. Nobody writes to it by hand.

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
