---
status: Accepted
---

# SDD Guide

**Loaded when:** writing, changing, or validating the SDD of a Product Component

An SDD states how one Product Component is **built**. `SRS-<pc>.md` fixed the behaviour; this decides the
shape that delivers it, and MUST NOT introduce behaviour — a promise appearing here first is a promise
nobody agreed to.

## Which sections exist, and when

Every section names the **minimum `mode` that demands it**. Below that minimum it MUST NOT be written to
fill a slot; above it, it is required.

| Section | Minimum `mode` |
|---|---|
| § Decision Summary — what this component is built as, and the one or two most expensive choices reversed | `outline` |
| § Structure — the `LC` list and the direction of their dependencies | `outline` |
| § Inherited Constraints — every `AD-N` binding this component, **quoted** | `guarded` |
| § Failure Behaviour — per boundary | `guarded` |
| `03-integrations/<name>.md` | `guarded`, when the component has one |
| § Robustness Analysis — ABCE | `deep` |
| `02-contracts/` · `04-components/` · `05-model/data-model.md` · `06-flows/` | `deep` |
| `01-ux/<screen>.md` | `deep`, or earlier through `wdi-ux` |

At `mode: catalog` the SDD is a **skeleton** — frontmatter and headings, born from `templates/sdd.md` by
`wdi-init` intent `component`. That is a finished state, not an unfinished one: G4 is skipped there, and the
code is written from the blueprint.

Review lenses are read from `risk_accepted`, never from `mode`. Both fields are defined in
`delivery-flow-guide.md`.

## No BMad skill writes this either

The same three consequences as the SRS apply — no `doc_standards` fires, no memlog is created, no template
enforces itself — and they are stated in `srs-guide.md` rather than repeated. `bmad-architecture` writes the
**spine**, not this.

## Home and life cycle

- `.how/<pc>/SDD-<pc>.md`, with slots `01-ux/` … `06-flows/`.
- Living and amended, exactly like its SRS. It MUST NOT be versioned or frozen.
- The slot numbers are an **ABCE classification**, not a reading order — `corpus-guide.md` owns that rule.
- `supplements/` is **repealed** along with the `ANX-` concept it existed for.

## Inherited constraints

From `guarded` up, every `AD-N` in `ARCHITECTURE-SPINE.md` that reaches this component MUST be listed under
**Inherited Constraints**, quoted rather than paraphrased — a paraphrase drifts, and the drift is invisible
because both texts read reasonably.

A design that must deviate does not argue here. It goes through `wdi-decision`, and either the spine changes
or the design does. An SDD contradicting an `AD-N` in prose is the failure the spine exists to prevent.

## Failure Behaviour — it stands on its own

**`Failure Behaviour` does not need ABCE**, and this is the change that makes `guarded` worth having. The
boundary list already exists: `.how/_platform/inventory-api.md` names the endpoints and
`inventory-screen.md` names the screens, each with an owning-component column. Nothing has to be derived
again.

For each boundary, state what happens when the thing on the other side is slow, absent, or lying: timeout,
retry policy, what the user sees, what gets logged. "Returns an error" is not an answer.

When a failure mode turns out to be a promise — a refund path, a partial save — it becomes a scenario on the
`.what` side, and it MUST go to the SRS first.

## Object identification — the ABCE pass, at `deep` only

This is the Robustness Analysis. It MUST NOT have appeared in the SRS, and at `outline` and `guarded` it MUST
NOT be written at all.

| Class | What it is | Slot |
|---|---|---|
| **Boundary** | Where the component meets something outside it — screens, endpoints, adapters, file drops | `01-ux/` · `02-contracts/` · `03-integrations/` |
| **Control** | What coordinates a use case from start to finish | `04-components/` |
| **Entity** | The things that persist, and their shape | `05-model/` |
| Behaviour | How the three move together, per use case | `06-flows/` |

From `guarded` up, every Boundary object MUST correspond to an `LC` in `.control/registry/components.yaml`;
at `deep`, Control objects too. Registration is checked **when the spec closes** — `lc-registered` — not before a ticket
is picked up.

Flows **into and out of** each boundary MUST be stated, not just the boundary. A boundary listed without its
direction of call is a name, not a design.

Flow diagrams in `06-flows/` are written only for a flow touching money, irreversible state, or a third
party. The lane order is the project's to fix, once, in `../../project/codebase-conventions-guide.md`. **The `No-op` lane
rule is repealed** — it was a heavy convention for a folder that had never carried a file, and it belongs to
how a diagram is drawn rather than to what binds.

## The three inventories are derived, not authored

`.how/_platform/inventory-db.md`, `inventory-api.md`, and `inventory-screen.md` belong to `wdi-blueprint`,
and they are born at G3. This document MUST NOT keep a second copy of any of them.

| State | How the inventory comes to exist |
|---|---|
| No code yet | Written as a **plan** by `wdi-blueprint` intent `platform`. Nothing can be derived, because there is no source |
| Code exists | **Derived** from the code first — migrations for tables, route registration for endpoints, pages for screens — then compared with the plan. The difference is a finding, not hand work |

`.control/generated/` and `inventory.py` own the refresh. A discrepancy between plan and reality surfaces as
a validator finding; it MUST NOT become hand work that someone can forget.

`02-contracts/00-inventory.md` at `deep` is a different thing: the endpoints **this component** owns, with
numbers stable enough to carry into filenames. A new endpoint takes the next number, never a renumber —
renumbering renames every file after it and breaks every link.

## Contracts and data model — `deep` only

| Artifact | Where | Rule |
|---|---|---|
| API contract per endpoint | `02-contracts/` | One file per endpoint or per resource, never one for the whole surface |
| External integration | `03-integrations/` | MUST name the owner outside the team, and what happens when they change it. Required from `guarded` |
| Data model | `05-model/` | Diagram **and** a data dictionary — a diagram alone does not say what a column means |

### The five lanes every contract answers

Each contract spec MUST answer all five, and MUST say so explicitly when one does not apply:

| Lane | States |
|---|---|
| Authentication | Who may call it, and what happens when they may not |
| Validation | What is rejected before any work happens |
| Error handling | Which failures are expected and which are exceptional |
| **Rate limiting** | The limit, or `none` with a reason |
| **Idempotency** | Whether a repeated call is safe, and what makes it so |

The last two are the ones always skipped, and the two that hurt in production. `none` is an acceptable
answer; silence is not — silence reads as "not considered".

**One error envelope, referenced not repeated.** Its shape is defined once in
`.how/_platform/cross-cutting.md`. Every contract MUST reference it rather than restate it, and MUST
document 4xx and 5xx in that envelope — that is how a system ends up with four different error formats, each
of which looked reasonable on its own page.

## Evidence discipline

Every technical claim about code that already exists MUST be traceable to something in the repository — a
source file, a config, a schema, a manifest. Naming the file is the trace; "the service handles retries"
without one is not design, it is rumour.

This is not only a brownfield rule. **Raising a component's `mode` after its code runs** produces an
as-built record, and the labels are mandatory there for the same reason.

| Label | Meaning |
|---|---|
| `[ASSUMED]` | We decided to believe it; nothing was read that confirms it |
| `[PARTIAL]` | Verified for part of the surface, not all of it |
| `[NEEDS CONFIRMATION]` | A question with an owner, filed through `wdi-question` |
| `[MISSING]` | **Checked, and the thing described is not there** |

An unlabelled claim is read as verified. That is why the labels are mandatory and not a courtesy.

### Status is raised, never assumed

- A claim is raised to verified only after the evidence it names has actually been read. Reading the
  controller does not verify the repository.
- The raise MUST record **what was read**. "Verified against `<the file that was read>` and its
  integration test" is a raise; "verified" is not. There is no example path here on purpose: a guide
  is portable, and naming a tree — or even a file extension — teaches one product's stack, not the rule.
- `[PARTIAL]` MUST state what is **not** covered. A partial that only says "partial" is an unlabelled claim
  wearing a label.
- A claim MUST NOT be raised because it has survived several readings. Familiarity is not evidence.

### `[MISSING]` — negative knowledge, and why it MUST NOT be deleted

The first three labels state a degree of **not knowing**; this one states the opposite — it was checked, and
it is not there. `[ASSUMED]` means nobody looked.

The instinct is to delete the sentence, and that MUST NOT be done. Deleting it throws away the fact that
somebody once believed the thing existed, and that belief came from somewhere: a cancelled plan, a rename
the document never followed, a feature removed without a trace.

Each MUST be resolved into exactly one of three, with the disposition recorded beside it:

| If | Then |
|---|---|
| The code should have it | A `BUG-` in `defects.yaml`, with `root_cause` set and `violates` naming what it breaks |
| The document was wrong | Correct the claim, and say in the same pass what it used to assert |
| It is real but not built yet | A planned line with an owner — a `CAP` or an `FR`, never a bare note |

An unresolved `[MISSING]` MUST NOT pass G4.

## The boundary against promising

If a sentence here would surprise the Product Owner who approved the PRD, it is a promise and MUST travel
back — PRD or SRS first, this document second. A technology choice a second component will have to follow
belongs to the spine, as an `AD-N` through `wdi-decision`.

## Passing G4

Only what this component's `mode` demands, and nothing beyond it:

- From `outline`: Decision Summary and the `LC` list present.
- From `guarded`: Inherited Constraints complete, quoted, and contradicted nowhere in the document; Failure
  Behaviour present for **every** boundary named in the API and screen inventories.
- At `deep`: Robustness Analysis done; every `critical` use case mirrored at the technical altitude under
  the same ids; contract specs answering all five lanes; the data dictionary present.
- Always: unresolved `[NEEDS CONFIRMATION]` filed through `wdi-question`, no unresolved `[MISSING]`, and
  `wdi-review` run with the lens set `risk_accepted` names for a gate-opening review — a re-review after
  the gate runs the lighter set, and `wdi-review` owns which.

The spine comes first and the spec's contract comes last. An SDD written before the spine will be rewritten; a SPEC
written before the SDD has nothing to project.
