---
name: wdi-decision
description: Use when a decision worth remembering has been made, when one has to be carried into the documents it governs, or when a planning assumption turns out to be void. Three intents — open, accept, apply. Wraps bmad-correct-course. Produces a globally numbered DEC-.
---

# WDI Decision

Free of stage and free of role: a decision MAY be made at any point by anyone. What is fixed is where its
output lives — `.control/decisions/DEC-NNN-<slug>.md`, numbered globally from `decisions.yaml`.

Three intents, because deciding, ratifying, and rewriting the documents are three different acts and merging
them means documents change before anyone approved the change.

| Intent | Does | Who |
|---|---|---|
| `open` | Writes a `DEC-` at `status: draft`. Also the entry point for a void planning assumption, which is where `bmad-correct-course` is dispatched | anyone |
| `accept` | Raises `draft` → `accepted` | **the Product Owner only** |
| `apply` | Dispatches the owner of every document the decision reaches, checks what came back, fills `touches`, raises `applied` | anyone |

Applying is what **freezes** a decision, not accepting. `decision-guide.md` owns the full ladder and this skill
MUST NOT restate it.

## The one test, before anything is written

> **If someone asks in three months why it is like this, is the answer readable from the code?**

Yes → it MUST NOT be recorded. No → record it.

**Recording is not mandatory**, and a decision nobody recorded is normal rather than negligence. You MUST NOT
log it as debt or backfill it later from memory. One case stays mandatory: a decision that **contradicts or
changes an `AD-N`**.

The old name ADR forced the wrong question — *"is this architectural?"* — and that question threw away exactly
the decisions most worth keeping, the ones that sound small.

## Intent `open`

### Inputs

Any of these, alone or together: minutes in `.control/meetings/`, an answered question in
`.control/questions/`, a review or debugging finding, a memlog in `.control/memlog/`, a `wdi-reconcile` conflict.

The memlog is the richest source and the most often forgotten. It is the record of *why* — read it before
writing the Why section rather than reconstructing the reasoning from the outcome.

### What it writes

Three sections, always: **Decision** (one sentence, present tense, quotable) · **Why** · **Cost** (what becomes
harder). Alternatives, a reversal trigger, and Trace are required only when the decision reaches a Product
Component whose `risk_accepted` is `low`; elsewhere an empty one MUST be dropped rather than left as a heading.

Frontmatter carries `touches: []` — empty until applied — and `type:` when it is useful. There is no `layer:`
and no `component:`; both were classifications demanded before anything was known.

A `DEC-` MUST NOT hold an open question. Those go to `wdi-question`.

### A void planning assumption

This is the same intent, with one extra step in front. The trigger is one thing: **a planning assumption turned
out to be void.** It usually surfaces while building, but its impact reaches back into G2, G3, and G4.

Three things it is **not**:

| Ask | Route |
|---|---|
| Something is broken and the cause is unknown | `wdi-systematic-debugging` **first**. A correction built on a guessed cause corrects the wrong thing |
| A decision exists and documents must follow | intent `apply`. There is no plan to re-cut |
| Scope grows without invalidating anything | `wdi-product` intent `update`, then the normal flow |

State the void assumption in **one line** before dispatching. A correction whose trigger cannot be stated in one
line is a re-plan, and it belongs upstream.

Then dispatch `bmad-correct-course`. Do not restate the rules to it — they arrive through `persistent_facts` in
`_bmad/custom/bmad-correct-course.toml`, including the ban on direct edits. Name the corpus files in scope
explicitly; it globs its own defaults, which this project does not use.

**Its impact analysis is incomplete by construction** — it knows a PRD, epics, and stories, and it cannot see
`.what/<pc>/`, `.how/`, `.control/`, or `.constitution/`. Every one of these MUST be checked here:

| Layer | What to look for |
|---|---|
| `.what/_prd/` | The `FR`/`NFR` that no longer holds, and every one depending on it |
| `.what/<pc>/` | Use cases realising those `FR`, business rules, state lifecycles that lose a state |
| `.how/_platform/` | An `AD-N` the correction breaks, a container the C4 set no longer describes, an inventory row with nothing behind it |
| `.how/<pc>/` | Contracts, flows, and Failure Behaviour written against the old promise |
| `SPEC.md` | What the wave projected — a SPEC MUST NOT be edited to match; it is re-derived |
| `waves.yaml` | The wave's size, and whether the correction changes it |
| Story files | Which stories are `in-progress`, and which are not yet started |

The result is a `DEC-` of **`type: course-correction`**. The `SCP-` code is retired — a course correction is a
decision, and no second code names the same thing.

A correction cancelling more than **30%** of a wave's stories MUST NOT be handled as a patch. Say so, and let
the wave be re-cut through `wdi-build`.

A story already `in-progress` MUST NOT have its contract changed. Report it; stopping it and returning it to
`ready-for-dev` is the coordinator's act.

## Intent `accept`

Only the Product Owner MAY raise a `DEC-` to `accepted`. **An agent MUST NOT accept its own.** When work is
blocked waiting on one, the block is reported, never resolved by self-approval.

An `accepted` `DEC-` that is still unapplied MAY be corrected in place, with the correction recorded in the
memlog. Nothing has been built on it, so there is no divergent record to preserve.

## Intent `apply`

**You apply nothing yourself.** Every artifact has an owner, and the owner writes it. A hand-edit here produces
a change with no author, no input trail, and nothing that verifies it.

Exactly one `DEC-`, at `status: accepted`. You MUST NOT apply one in any other status.

### Step 1 — List the targets before touching one

Name every document the decision reaches, and the skill that owns each, **before** anything is dispatched. A
list assembled while editing is a list that grows to fit what was already done.

| Target | Dispatch |
|---|---|
| `.what/_product-brief/` | `wdi-problem` |
| `.what/_prd/<initiative>/` | `wdi-product` intent `update` |
| `.what/<pc>/` § Actor Register · § UC Catalogue · `03-domain/domain-model.md` | `wdi-blueprint` intent `catalog` |
| `.what/business-rules.md` · `.control/product-glossary.md` | `wdi-blueprint` intent `catalog` |
| `.how/_platform/` — spine, C4, `cross-cutting.md`, the three inventories | `wdi-blueprint` intent `platform` |
| `.what/<pc>/` slots `02`–`05` — full flows, local rules, lifecycles, scenarios | `wdi-component` intent `behaviour` |
| `.how/<pc>/` minus `01-ux/` | `wdi-component` intent `design` |
| `EXPERIENCE.md` · `.how/<pc>/01-ux/` · `design-system.md` | `wdi-ux` |
| `components.yaml` — a PC born or changed · `mode` · `risk_accepted` · the two structure maps | `wdi-init`, by intent |
| `waves.yaml`, or anything inside an open wave | `wdi-build` |
| `.control/questions/` | `wdi-question` |
| `.control/project-non-technical-log.md` · `.control/meetings/` | `wdi-log` |

A target with **no row here** MUST be reported as a gap in the method, not given a plausible owner.

Apply in layer order — **`.what/` before `.how/`** — so the lower layer is written against the promise it is
supposed to serve, not against the one it is about to replace. The retired `layer:` field used to declare that
order in advance; it is now simply the order.

### Step 2 — Dispatch, one owner at a time

Hand each owner the `DEC-` id and the exact change its layer has to carry. You MUST NOT restate the decision in
your own words; **quote it.** A paraphrase drifts, and the drift is invisible because both texts read reasonably.

Each owner keeps its own rules — its review, its memlog, its registry entry. You MUST NOT ask an owner to skip
any of them because the change is small.

### Step 3 — Name the gates

Run the change-control matrix in `delivery-flow-guide.md` and **report** which gates it names. You MUST NOT
reopen a gate yourself, and you MUST NOT treat a green application as a gate that has already passed.

### Step 4 — Close the trail

- Fill `touches:` with the files that were **actually** changed, in the `DEC-` and in `decisions.yaml`. Raise
  `status: applied`. **From that point the file MUST NOT be edited** — not the Decision, not the Cost, not a
  typo in the Why. Documents cite it now.
- V8 checks that an `applied` decision names a non-empty `touches`.
- Regenerate `.control/generated/decisions.md` with `validate.py --generate`. That table is how a decision is
  found now; searching the memlog for decisions is retired, and the memlog is a run log again.
- Report what changed, and what the decision implied but was **not** changed.

## Rules

- You MUST NOT widen scope beyond the decision. A neighbouring paragraph that now looks wrong is a finding to
  report, not a change to make.
- You MUST NOT introduce a new domain noun. If the decision requires one, it goes through `wdi-blueprint` first.
- If applying would contradict another `applied` decision, you MUST stop and report the conflict. Two applied
  decisions that disagree is work for intent `open`, not something to resolve by preferring the newer one.
- If the decision is unapplicable as written — the document it names no longer exists, or the change was already
  made differently — you MUST report that instead of improvising.
- You MUST NOT apply into a wave that is already closed.
- `AD-N` is a different thing: a living rule with Binds · Prevents · Rule, edited in place. You MUST NOT convert
  one into the other.
- A decision that emerged from a failed third fix attempt MUST say so in Why. That is the signal
  `wdi-systematic-debugging` exists to raise, and burying it wastes the finding.

## Output

Intent taken. For `open`: the decision in one sentence, its three required sections, and — for a correction —
the void assumption in one line plus what the scan found that `bmad-correct-course` could not see. For `apply`:
every target with its owner, what each owner changed, what was reported instead of changed and why, the gates the
matrix names, and whether `touches` and `applied` were filled.
