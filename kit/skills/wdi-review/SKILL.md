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

| `risk_accepted` | Lenses | And on the code |
|---|---|---|
| `low` | structure · prose · **edge-case-hunter** | a two-reviewer panel is required |
| `medium` | structure · prose · **edge-case-hunter** | — |
| `high` | structure · prose | — |

`SPEC.md` always carries `edge-case-hunter`: it is the contract a builder works from, and a branch missed
there surfaces as a bug at G5 instead.

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
- When the artifact changed after the review, the trace is stale by definition. You MUST re-run
  rather than bump the date.
- When findings reveal the requirement itself is wrong rather than the writing, this stops being a
  review. Route to `wdi-decision`, and let the `DEC-` change the artifact.

## Output

One short report: artifact, lenses run, findings by severity, what was resolved, what was deferred
and where it landed, and whether the trace was written — with the reason when it was not.
