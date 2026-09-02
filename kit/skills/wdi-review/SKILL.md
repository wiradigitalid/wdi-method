---
name: wdi-review
description: Use to review any corpus document at any time, and always before a gate on the four artifacts no doc_standards covers — the architecture spine, SRS, SDD, and SPEC. Reads the lens set from the component's risk_accepted, dispatches bmad-review, and stamps the `review-trace` trace on those four only. Not for code review.
---

# WDI Review

Five BMad skills review their own output through `doc_standards`. Four artifacts have no such trigger,
and they are the most binding ones in the corpus. This skill covers exactly those four.

It exists for two reasons `bmad-review` cannot serve on its own: the lens set is not a property of the
artifact but of the component's `risk_accepted`, and defaulting to structure + prose silently drops the
one lens that matters for behaviour; and `bmad-review` is class D — it writes nothing, so nothing proves
it ran.

You MUST NOT use this for code or diffs. That is `code-review`, dispatched by `wdi-build` as Step 3 of its pipeline.

## What it covers

| Artifact | Trace lands in |
|---|---|
| `.how/_platform/ARCHITECTURE-SPINE.md` | `reviewed:` in its frontmatter |
| `SRS-<pc>.md` + slots `02`–`05` | `reviewed:` in the SRS frontmatter |
| `SDD-<pc>.md` + slots `01`–`06` | `reviewed:` in the SDD frontmatter |
| the contract — `SPEC.md`, or the ticket set as one artifact at size `S` | `spec_reviewed:` on the spec in `specs.yaml` |

**The lens set comes from the component's `risk_accepted`, never from `mode` and never from the artifact
type.** The mapping lives in `delivery-flow-guide.md` § Two fields, and it is **read from there, not copied
here** — this file carried a second copy of that table until it was noticed that the sentence forbidding
the copy sat directly above it.

What this skill owns is three things the mapping does not say:

- **Refusing a lighter set than it names.** The lens set is not negotiable down, whatever the artifact.
- **The contract is the exception:** it always carries `edge-case-hunter`, first run and re-run alike. It
  is what a builder works from, and a branch missed there surfaces as a bug at G5 instead.
- **Reading `risk_accepted` off the component, not off the artifact** — Step 1 below.

## When a review has to run again — and when it does not

Four rules, and together they are what keeps this skill from becoming a treadmill. Every one of them has a
precedent elsewhere in the method; none of them lowers what a review looks for.

- **The trace has to be fresh at a gate and at spec close. Between those points a stale trace is
  advisory.** `review-trace` reports it and does not fail; what catches a
  gate opening on a stale review is G4's ★ question — *validators green **and** the review leaving no open
  finding* — not a validator firing on every commit.
- **A wording-only change MUST NOT trigger a re-run.** The split is `prd-guide.md`'s: an `FR`'s
  **promise** reopens gates, its **wording** costs one Revision History row. Re-stamping `date` and `sha`
  without re-running is allowed **here and nowhere else**, and that row is what makes it checkable.
  Behaviour, a rule, a boundary, a contract, or a use case flow is material, and material changes re-run.
- **A re-review covers the delta, not the artifact.** Read what changed since the reviewed `sha`, and
  whatever it reaches. G3 already reopens over the delta when a new PRD arrives; same principle.
- **One apply, one review.** A `DEC-` or an answered `OQ-` applied across several artifacts is **one**
  review of the delta across all of them, never one review per artifact. The trace lands on each artifact
  touched, naming the same `sha`.

## Stale is not a finding. Load-bearing stale is.

**Triggers are a gate, a spec close, and an explicit ask — nothing else.** You MUST NOT offer a review
because a document was touched. An offer declined five times teaches the owner to decline the sixth,
which is the one that mattered.

Three things look like a review and are not: a document the owner has already **decided against** — an
edit, `delivery-flow-guide.md` owns it; a document **merely behind the code**, its expected state; and a
machine contract, which nobody reads.

**The test — one question, and it decides:**

> Would a reader who believes this sentence make the wrong repair?

| Load-bearing — repair NOW | Not load-bearing — leave it |
|---|---|
| A binding guide describing a stack the repo left — `npm` commands that all fail | A count, a date, a section that reads a little old |
| A guard that greps a language this repo no longer writes | Wording that is merely less good than it could be |
| A cite that resolves to nothing | A section whose file has moved but whose point still holds |
| A claim contradicting an `AD-N` or an `applied` `DEC-` | An artifact the next spec will rewrite anyway |

Everything in the right column is corrected **when someone next touches that section**, or it dies with
the document. It MUST NOT be raised as a finding, MUST NOT open an `OQ-`, and MUST NOT hold a stamp.

**A missing history line is never a finding.** Not a rationale, not a note saying why something changed,
not an account of a conflict already resolved. `corpus-guide.md` § The corpus is written in the present
tense says history is written when someone judges it worth writing, and that skipping it is not a gap —
a review that reports it as one turns a record into a ritual.

**Where substance actually is.** On the evidence of a real pass of twenty-one findings: a document checked
against **the code**, and against an **`AD-N`** or an `applied` `DEC-`. Those two found the only two that
changed what was true. Document-versus-document bookkeeping found thirteen and changed nothing. When the
budget is tight — it always is — spend it on the first two and skip the third.

## A restated derived fact is one finding, and its remedy is deletion

The cheapest class to produce is the one worth least: a document disagreeing with a registry it could
have read. It was **thirteen of the twenty-one** in the pass above — `mode` restated in prose, a slot
list denying files on disk, "no applied `DEC-` binds this component", a Gate Checklist counting four use
cases where the registry held six.

Handled as follows, and it is not a judgement call:

- **One finding, not one per site.** Report the class and list its locations. Thirteen rows for one
  cause spends the budget above on a single problem and buries whatever else the pass found.
- **The remedy is DELETION.** You MUST NOT correct the restated value. A corrected copy is a *second*
  stale fact on a slower clock — one real SRS carried three claims about its own `mode` on one page,
  one of them a correction block fixing an older value, and none of the three was right.
- **It is a `structure` finding**, never `edge-case-hunter`. It costs no thinking to find and MUST NOT
  consume the lens bought for reasoning about behaviour.
- If the document's **template** invited it, say so and route to the maintainer. `corpus-guide.md` §
  A derived fact has exactly one home is the list; the templates were cleaned once already, and an
  invitation still standing is a package defect, not a product one.

## Findings have a budget, and it is not a new one

A review with no upper bound produced two hundred findings from one pass. The budget is the one
`wdi-question` already carries, so nothing new is invented:

| Class | Where it goes | Target |
|---|---|---|
| Holds the gate | `.control/questions/blocking.md` | **≤3 per Product Component** |
| Does not hold anything | `.control/questions/assumptions.md`, one line each | **≤15** |

**A review that exceeds both MUST stop and say so.** What it reports is not a finding list but a verdict:
this artifact needs rewriting, not reviewing. Sixty findings is not thoroughness — it is a review that
failed to reach a conclusion, and the owner pays for it twice. You MUST NOT register a finding as
blocking to be safe.

**`review-trace` stamps only components at `risk_accepted` `low` or `medium`.** At `high` the owner has already
accepted the risk, and demanding the trace there is bookkeeping with no buyer. The contract keeps its
trace in the registry rather than in itself: `to-spec` and `to-tickets` overwrite hand edits.

**Anything in the corpus MAY be reviewed here when asked** — a `DEC-`, minutes, a guide, a brief, a PRD,
a `DESIGN.md`. What is restricted is the **stamp**, not the reading: only the four rows above carry a
trace `review-trace` reads. The five artifacts with `doc_standards` review themselves at finalize; a review here is
never required for them and MUST NOT leave a `reviewed:` block, because a second trace implies the first
was optional.

## Step 1 — Read the lens set off the component

Find the artifact's component, read its `risk_accepted` from `components.yaml`, and state the lens set in
one line before dispatching. Do not ask the user which lenses to run — the field decides, and it is the
owner's field.

For an artifact with no component — a guide, minutes, the spine — use structure · prose.

The adversarial lens is in no table. It MAY be added when the artifact touches money, personal data, or a
third-party integration. It demands at least ten concrete findings and treats an empty result as a signal
to re-check, so adding it to a routine review buys noise.

## Step 2 — Dispatch

Invoke `bmad-review` with the artifact path and the chosen lenses. Slots are part of the artifact:
reviewing `SRS-<pc>.md` without `04-usecases/` and `05-scenarios/` reviews the kernel and misses
where the branches live.

## Step 3 — Resolve before stamping

Findings MUST be resolved or explicitly deferred before the trace is written. A deferred finding
MUST be filed through `wdi-question`, or opened as a `DEC-` through `wdi-decision` — never a note in the
chat that dies with the session.

You MUST NOT stamp an artifact whose findings are still open. A trace on unresolved findings is
worse than no trace: `review-trace` goes green and the gate opens on a review nobody acted on.

## Step 4 — Stamp

Write the trace, and nothing else:

```yaml
reviewed:
  date: '<YYYY-MM-DD>'
  sha: '<commit sha at review time>'
  lenses: [structure, prose, edge-case-hunter]
```

- `sha` MUST be the commit the artifact was reviewed at. Without it staleness cannot be measured, only
  felt — the same reason a structure map requires one. `review-trace` no longer reads the stamping commit itself as
  a change, so a fresh stamp does not make its own review look stale.
- You MUST NOT write the trace unless `bmad-review` actually ran in this session. Filling it as a
  formality turns `review-trace` into a rubber stamp, which is worse than having no validator.
- You MUST NOT touch `status:` while stamping. `status: reviewed` states a **stage**; the `reviewed:`
  block states an **event**. Raising the status is a separate act.
- You MUST NOT edit the artifact's content. Fixing a finding is the author's act, not the
  reviewer's — say what is wrong and stop.

## Rules

- You MUST NOT stamp anything outside the four rows in the table. Brief, PRD, `DESIGN.md`,
  `EXPERIENCE.md`, and research MAY be reviewed on request; the finding report is the whole output,
  and no `reviewed:` block is written.
- You MUST NOT stamp on behalf of a review someone else ran earlier. Re-run it; the run is cheap and
  the claim is not.
- When the artifact changed **materially** after the review, the trace is stale and you MUST re-run
  rather than bump the date. A wording-only change is the one exception, and §*When a review has to run
  again* owns it.
- When findings reveal the requirement itself is wrong rather than the writing, this stops being a
  review. Route to `wdi-decision`, and let the `DEC-` change the artifact.

## Output

One short report: artifact, lenses run, findings by severity, what was resolved, what was deferred
and where it landed, and whether the trace was written — with the reason when it was not.
