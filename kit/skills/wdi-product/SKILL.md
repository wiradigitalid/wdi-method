---
name: wdi-product
description: Use at G2 Product — when a PRD is created or an existing promise changes. Two intents, prd and update. Checks position, dispatches bmad-prd, verifies the result against prd-guide.md, and lands the memlog. Never writes the PRD itself.
---

# WDI Product

G2 decides **what is built, and how it feels to use.** `bmad-prd` writes the PRD.

This wrapper exists because `bmad-prd` was the only writer of a primary artifact in this method with no WDI
wrapper at all — so nothing checked its position, nothing verified its result against the guide, and nothing
landed its memlog where the next run would read it. Those three gaps were paid for at G2 every time.

You MUST NOT write or edit `prd.md` yourself. If a check fails, name what is missing and re-dispatch.

| Intent | When |
|---|---|
| `prd` | A functional area a reader would not think to look for in an existing PRD |
| `update` | Anything else — the default, and by a wide margin |

## Inputs

| Source | What it answers |
|---|---|
| `.what/_product-brief/brief.md` | The problem, the primary user, the boundary the PRD MUST respect |
| `.what/_prd/*/prd.md` | Which initiatives already have a PRD, and what each already promises |
| `.control/registry/goals.yaml` | The `BG` this initiative serves |
| `.control/registry/requirements-*.yaml` | Every initiative's `FR`/`NFR`/`UJ`, so the next id continues the product's sequence |
| `.control/decisions/` | `applied` decisions the PRD MUST already reflect |
| `.constitution/method/document/prd-guide.md` | The rules the result is checked against |
| `.control/product-glossary.md` | Terms already fixed |

## Step 1 — Position, and `update` is the default

The decision this skill exists for. The test is the **reader**, not the calendar:

> Would someone looking for this promise open an existing document?

Yes → `update`, however large the change. No → `prd`. A PRD MUST NOT be split because it grew long, and a
release is never a reason on its own. `prd-guide.md` owns the full table.

Three asks that are not this skill:

| Ask | Route |
|---|---|
| The problem itself has changed | `wdi-problem` — a re-cut plan under a wrong problem is wasted work |
| Only the **wording** of an `FR` is wrong, while the promise is the same | The skill already at work fixes it directly. See below |
| A planning assumption turned out to be void | `wdi-decision`, which wraps `bmad-correct-course` |

## Step 2 — Wording is not a promise

The split that ended three corrections in "reported but not fixed". `prd-guide.md` owns it; what this skill
owns is refusing to run for the wrong half.

| What changed | Who does it |
|---|---|
| A wrong cross-reference, a retired term, a word inconsistent with an `applied` decision — **the promise is the same** | Whichever skill is already at work. Memlog records it; **one** Revision History row per pass, never one per correction |
| Scope, the proof of done, an `FR` retired or born | This skill, intent `update` |

You MUST NOT accept a wording correction as an `update` run. Doing so puts a trivial fix behind a gate, and
that is exactly how the three earlier ones were dropped.

## Step 3 — Dispatch

Invoke `bmad-prd` with the detected intent, scoped to **one initiative**. Do not restate the rules to it —
they arrive through `persistent_facts` and `doc_standards` in `_bmad/custom/bmad-prd.toml`.

Name the brief and, for `update`, the existing PRD and every `applied` decision that reaches it. The skill
globs its own default locations, which this project redirects.

## Step 4 — Land the requirements

Each feature's **Realizes:** line cites `FR-N`/`NFR-N` ids. The template gives the statement, the proof
of done, and the enforcer no home inside `prd.md` any more — write them straight into
`.control/registry/requirements-<slug>.yaml` — the slug being this PRD's own folder name — on the id's own row, as part of producing this PRD. The `CAP` row goes in the same file: one feature is one capability, and a feature lives in exactly one PRD. This is
landing, not editing `prd.md`: the same duty `wdi-problem` Step 4 carries for `BG-N`.

An `update` run that adds or changes a promise lands the same way — the registry row changes, the PRD
keeps citing the id, and Revision History (Step 6 below) records what changed for a reader.

## Step 5 — Verify

| # | Check | Fails when |
|---|---|---|
| 1 | Home | Anything outside `.what/_prd/<initiative>/`, or a folder still named `ISI-slug-inisiatif` |
| 2 | Ids allocated from the registry | `FR-1` restarted, or an id invented in prose |
| 3 | Every `FR` names its `capability`; every `NFR` names its `goal` | `chain-links` has nothing to check |
| 4 | Every `FR`'s statement and proof of done, every `NFR`'s statement and `enforced_by`, live only in `requirements-<slug>.yaml` | Full prose written in `prd.md` instead of, or as well as, the registry row from Step 4 |
| 5 | Cross-Cutting NFRs (§6) and Constraints and Guardrails (§7) both present | An absent section reads as "not checked" |
| 6 | No solution shape | A framework, a table, or a transport named in `prd.md` rather than in `addendum.md` |
| 7 | §1 Why This Initiative states a delta against the brief's `Why`, not a restatement of it | The product's own vision written out again on the first PRD |
| 8 | No Document Purpose, Glossary, Non-Goals, Open Questions, or Assumptions Index section | Any of the five appeared instead of being routed to its real home — see `prd-guide.md` |
| 9 | One Revision History row for this run, written for someone not in the room | Zero rows, several rows, or a row that says "Updated §4.2" |
| 10 | Memlog at `.control/memlog/prd-<slug>.md`, slug matching the folder | A `.memlog.md` appeared inside `.what/` — `--workspace` was used |
| 11 | `bmad-review` ran through `doc_standards` on `prd.md` and `addendum.md` | It did not fire |

Check 10 MUST be fixed immediately rather than reported. `memlog-home` rejects a memlog inside the corpus.

## Step 6 — `owns:`, and the collision it prevents

A new or changed `FR` that claims write authority over a domain entity MUST be checked against `owns:` in
`components.yaml`. An entity has exactly one owning Product Component; an `FR` from another PRD that needs to
change it MUST point at the owner's `FR` rather than promising to write it itself. `entity-one-writer` checks this, and the
collision has already happened once for real.

Report a collision. You MUST NOT resolve it by widening one PRD's claim.

## Step 7 — Impact

A changed promise changes what other documents can still claim. Check, and **report** — never edit.

| Found | Where it goes |
|---|---|
| A `UC` realising an `FR` whose promise moved | `wdi-component` intent `behaviour`, or `wdi-blueprint` when the catalogue line itself changes |
| A blueprint inventory row with nothing promising it any more | `wdi-blueprint` |
| A contradiction with an `applied` decision | `wdi-decision` — a new `DEC-`, never an edit to one already applied |
| A component born by this initiative | `wdi-init` intent `component` |

Then run the change-control matrix in `delivery-flow-guide.md` and **report** which gates reopen. You MUST
NOT reopen one yourself.

## Rules

- You MUST NOT write a second PRD for an area that already has one. The reader test decides, and its answer
  is `update` far more often than it feels.
- You MUST NOT open G2 on a PRD that has not been through check 11. Gate time is for deciding, not
  proofreading.
- The gate reads `prd.md` and `EXPERIENCE.md` together. A PRD that passes while the experience side is
  missing has answered half of what G2 decides.
- Every unresolved `[ASSUMPTION]` MUST be filed through `wdi-question` before the gate opens.
- You MUST NOT raise `status:`. Status is a stage; the `reviewed:` block is an event, and `wdi-review` writes
  it.
- When the PRD cannot promise what was asked, say so and stop. Route to `wdi-problem`; do not quietly narrow
  the ask.

## Output

Intent dispatched · what the promise now is in one line · the requirements landed in Step 4 · the result of
all eleven checks naming the failures · the `owns:` check · impact found and where it was routed · the gates
the matrix names · open questions filed.
