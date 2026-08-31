---
name: wdi-review
description: Use to review any corpus document at any time, and always before a gate on the four artifacts no doc_standards covers — the architecture spine, SRS, SDD, and SPEC. Reads the lens set from the component's risk_accepted, dispatches bmad-review, and stamps the V13 trace on those four only. Not for code review.
---

# WDI Review

Five BMad skills review their own output through `doc_standards`. Four artifacts have no such trigger,
and they are the most binding ones in the corpus. This skill covers exactly those four.

It exists for two reasons `bmad-review` cannot serve on its own: the lens set is not a property of the
artifact but of the component's `risk_accepted`, and defaulting to structure + prose silently drops the
one lens that matters for behaviour; and `bmad-review` is class D — it writes nothing, so nothing proves
it ran.

You MUST NOT use this for code or diffs. That is `bmad-code-review` and the Review Panel.

## What it covers

| Artifact | Trace lands in |
|---|---|
| `.how/_platform/ARCHITECTURE-SPINE.md` | `reviewed:` in its frontmatter |
| `SRS-<pc>.md` + slots `02`–`05` | `reviewed:` in the SRS frontmatter |
| `SDD-<pc>.md` + slots `01`–`06` | `reviewed:` in the SDD frontmatter |
| `SPEC.md` | `spec_reviewed:` on the wave in `waves.yaml` |

**The lens set comes from the component's `risk_accepted`, never from `mode` and never from the artifact
type.** `delivery-flow-guide.md` owns the mapping and it MUST NOT be restated as a second copy here; what
this skill owns is reading it and refusing to run a lighter set than it names.

| `risk_accepted` | First review, and the review before a gate | Every re-review after that | On the code |
|---|---|---|---|
| `low` | structure · prose · **edge-case-hunter** | structure · prose | a two-reviewer panel is required |
| `medium` | structure · prose · **edge-case-hunter** | structure · prose | — |
| `high` | structure · prose | structure · prose | — |

**`edge-case-hunter` is bought once, at the moment it pays for itself** — the first review of an artifact,
and the review that opens a gate. Running it again over a paragraph that changed is what made review feel
like a tax. A re-review MUST put it back when the delta touches money, personal data, an irreversible
action, or a third party; there the branch it hunts is the whole point.

`SPEC.md` always carries `edge-case-hunter`, first run and re-run alike: it is the contract a builder works
from, and a branch missed there surfaces as a bug at G5 instead.

## When a review has to run again — and when it does not

Four rules, and together they are what keeps this skill from becoming a treadmill. Every one of them has a
precedent elsewhere in the method; none of them lowers what a review looks for.

- **The trace has to be fresh at a gate and at wave close. Between those points a stale trace is
  advisory.** V13 reports it and does not fail, the same way V19 is advisory on wave `S`/`M`. What catches a
  gate opening on a stale review is G4's ★ question — *validators green **and** the review leaving no open
  finding* — not a validator firing on every commit.
- **A wording-only change MUST NOT trigger a re-run.** This is the split `prd-guide.md` already owns:
  changing an `FR`'s **promise** reopens gates, changing its **wording** costs one Revision History row and
  nothing else. Re-stamping `date` and `sha` without re-running is allowed **here and nowhere else**, and
  the Revision History row is what makes it checkable. Anything touching behaviour, a rule, a boundary, a
  contract, or a use case flow is material, and material changes re-run.
- **A re-review covers the delta, not the artifact.** Read what changed since the reviewed `sha`, review
  that and whatever it reaches. Re-reading four hundred lines of SRS to check one changed paragraph is the
  ceremony this rule exists to stop — and the same principle already governs G3, which reopens over the
  delta when a new PRD arrives.
- **One apply, one review.** A `DEC-` or an answered `OQ-` applied across several artifacts is **one**
  review of the delta across all of them, never one review per artifact. The trace lands on each artifact
  touched, naming the same `sha`.

## Findings have a budget, and it is not a new one

A review with no upper bound is what produced two hundred findings from one pass and ids reaching `OQ-146`;
`rationale.md` records it. The budget is the one `wdi-question` already carries, so nothing new is invented:

| Class | Where it goes | Target |
|---|---|---|
| Holds the gate | `.control/questions/blocking.md` | **≤3 per Product Component** |
| Does not hold anything | `.control/questions/assumptions.md`, one line each | **≤15** |

**A review that exceeds both MUST stop and say so.** What it reports is not a finding list but a verdict:
this artifact needs rewriting, not reviewing. Handing an owner sixty findings is not thoroughness — it is a
review that failed to reach a conclusion, and the owner pays for it twice.

You MUST NOT register a finding as blocking to be safe. That habit is what produced the flood.

**V13 stamps only components at `risk_accepted` `low` or `medium`.** At `high` the owner has already said
they accept the risk, and demanding the trace there is bookkeeping with no buyer.

SPEC keeps its trace in the registry because `bmad-spec` is its sole author and overwrites hand
edits. A trace written into `SPEC.md` disappears on the next run.

**Anything in the corpus MAY be reviewed here, at any time** — a `DEC-`, minutes, an `OQ-`, a guide, a
brief, a PRD, a `DESIGN.md`. What is restricted is the **stamp**, not the reading: only the four rows
above have a trace V13 reads, and only they MAY be stamped.

The five artifacts carrying `doc_standards` review themselves at finalize, so a review here is never
required for them. Asking for one anyway is legitimate — after hand edits, before a gate, when a
finding is suspected — and it MUST NOT leave a `reviewed:` block behind. A second trace on an
artifact whose first review is automatic implies that first one was optional.

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
worse than no trace: V13 goes green and the gate opens on a review nobody acted on.

## Step 4 — Stamp

Write the trace, and nothing else:

```yaml
reviewed:
  date: '<YYYY-MM-DD>'
  sha: '<commit sha at review time>'
  lenses: [structure, prose, edge-case-hunter]
```

- `sha` MUST be the commit the artifact was reviewed at. Without it staleness cannot be measured, only
  felt — the same reason a structure map requires one. V13 no longer reads the stamping commit itself as
  a change, so a fresh stamp does not make its own review look stale.
- You MUST NOT write the trace unless `bmad-review` actually ran in this session. Filling it as a
  formality turns V13 into a rubber stamp, which is worse than having no validator.
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
