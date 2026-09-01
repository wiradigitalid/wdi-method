---
status: Accepted
---

# Decision Guide

**Loaded when:** opening, accepting, or applying a `DEC-`

A `DEC-` records a decision worth remembering. The old name was ADR — *Architecture Decision Record*
— and the word "Architecture" forced the wrong question at the moment of writing: *"is this
architectural?"*. That question throws away the decisions most worth keeping, the ones that sound
small: *"the filter works like this"*, *"this list is sorted that way"*.

## One test decides whether to record

> **If someone asks in three months why it is like this, is the answer readable from the code?**

Yes → it MUST NOT be recorded. No → it is recorded.

**A `DEC-` records a state, never an event.** It answers *why is it like this* for someone about to
change it — forward-looking, present tense. It is not a record that something changed, not a record that
a document used to say otherwise, and not a record that a review found a conflict. Those are document
history, and `corpus-guide.md` § The corpus is written in the present tense says they go nowhere.

The practical form of the test: **would this file save the next person from a mistake they were about to
make?** If the honest answer is *"no, but it explains what happened"*, there is no file.

**Recording is not mandatory, and a decision nobody recorded is normal rather than negligence.** It
MUST NOT be logged as debt, raised as a finding, or backfilled later from memory. Without this
sentence, "not mandatory" is read as "mandatory but allowed to be late".

One case remains mandatory: a decision that **contradicts or changes an `AD-N`** MUST be recorded
before the work that depends on it. That is the only one — and it is mandatory because an `AD-N` is what
the architecture rests on, not because a change is large or arrived late.

**Nothing else stops the work.** Where a change contradicts an `FR`, a `UC`, a business rule, or a
document's wording, the agent states the consequence once and the owner decides. If they proceed, the
documents are edited to match — `delivery-flow-guide.md` § When something settled has to change owns the
matrix, and the survey behind that warning is spent the moment the owner answers.

## `AD-N` and `DEC-NNN` are not the same thing

| | `AD-N` | `DEC-NNN` |
|---|---|---|
| Is | A **living rule** in `ARCHITECTURE-SPINE.md` | A **decision event** |
| Lives in | The spine | `.control/decisions/` |
| Changes by | Being edited in place | Never, once `applied` — a new `DEC-` supersedes it |
| Answers | What is forbidden from now on | What was chosen, and what it cost |

An `AD-N` usually has a `DEC-` behind it. Neither MUST be written in place of the other, and one MUST
NOT be converted into the other.

## Shape — three sections, and no more required

| Section | States | Required |
|---|---|---|
| **Decision** | One sentence, present tense, quotable into a rule | always |
| **Why** | The context that forced it, in a few lines | always |
| **Cost** | What becomes harder. A decision with only benefits was not thought through | always |
| Alternatives | What else was considered, and why each lost | see below |
| Reversal trigger | The observable condition that makes revisiting this correct | see below |
| Trace | Where it came from, and what it landed in | see below |

The last three MUST be present when the decision reaches a Product Component whose `risk_accepted`
is `low` in `components.yaml`. Everywhere else they are optional, and an empty one MUST be dropped
rather than left as a heading with nothing under it.

**A `DEC-` MUST NOT hold an open question.** Those belong to `.control/questions/`.

**One page, and that is a bound, not a target.** A `DEC-` records **what was chosen and what it cost** —
not how the answer was reached, not the transcript of the reasoning, not every reading of every clause
that was weighed on the way. One real decision reached **124 lines** to record that one invariant does not
reach one artifact; the sentence that mattered was one line and the cost was two.

Three things MUST NOT appear in a `DEC-`, and each of them is the derivation leaking in:

- The search that found the answer — which files were grepped, which clause was read first.
- A meta-note about the decision itself: whether it should have been a `DEC-` at all, whether some other
  mechanism was considered and rejected. If that reasoning matters it is the **Why**; usually it does not
  matter and it is nothing.
- A correction of an earlier draft of the same decision. Drafts are git's.

`Alternatives` is the one place a rejected option belongs, it is a **line each**, and it is required only
where the section table above says so.

## Frontmatter

| Field | Rule |
|---|---|
| `id` | `DEC-NNN`, allocated from `.control/registry/decisions.yaml`, globally. MUST NOT restart per component or per release |
| `status` | `draft` · `accepted` · `applied` · `superseded` · `rejected` |
| `touches` | Empty at `draft`. Filled **when the decision is applied**, with the files it actually changed |
| `type` | Free text, and optional. Written when it is useful — `risk-acceptance`, `course-correction` |
| `supersedes` · `superseded_by` | Both sides of a supersession MUST exist |

**There is no `layer:` and no `component:`.** Both were classifications demanded before anything was
known, and both were guessed as often as they were derived. `touches:` replaces them, and it is filled
from what happened rather than from what was predicted.

The filename is `DEC-NNN-<slug>.md`. It MUST NOT carry a component name — a decision that turns out to
reach a second component would otherwise need renaming, and the rename breaks every link to it.
Filenames MUST obey the cross-OS naming rules in `structure-guide.md`.

## Status — and why `applied` exists

`draft` → `accepted` → `applied`. A change of mind after that produces a **new** `DEC-`.

| Status | Means |
|---|---|
| `draft` | Being argued. It changes nothing, and that is the point — proposing is cheap |
| `accepted` | Ratified by the Product Owner. MAY still be corrected in place |
| `applied` | The documents it governs now say it. **Frozen from here** |
| `superseded` | Replaced. Names its replacement, and the replacement names it |
| `rejected` | Seriously considered and turned down. A real status, and it MUST be used — it is what stops the same argument being had twice |

**Applying is what freezes a decision, not accepting.** From `applied` onward nothing in the file MUST
be touched — not the Decision, not the Cost, not a typo in the Why. Documents cite it, and editing it
destroys the only evidence of what they were changed to match.

Before that, an `accepted` `DEC-` MAY be corrected in place. Nothing has been built on it, so there is
no divergent record to preserve, and **the correction is not recorded anywhere** — the file now reads
correctly and git holds the change. Logging it would be a second home for a fact git already has, and a
piece of document history that would save nobody.

An agent MUST NOT accept its own `DEC-`. When work is blocked waiting on one, the block is reported,
never resolved by self-approval.

## Finding a decision

`.control/generated/decisions.md` carries a flat table of every `DEC-` with its status and what it
touches. It is generated, and MUST NOT be written by hand.

Searching the memlog for decisions is **retired**. The memlog is a run log again — the record of *why*
while an artifact was written, and a source when writing a `DEC-`, never an index of them.

## Where decisions come from

| Trigger | Route |
|---|---|
| A meeting reached one | `wdi-log` intent `meeting` writes the minutes; the decision still needs its own `DEC-` |
| An open question was answered | `wdi-question` closes it; the answer becomes a `DEC-` when it binds |
| `wdi-systematic-debugging` found a root cause in the design | A `DEC-`. It MUST NOT be absorbed as a code patch |
| A planning assumption turned out to be void | `wdi-decision`, which wraps `bmad-correct-course`. The result is a `DEC-` of `type: course-correction` |
| A ticket contradicts an `AD-N` | The ticket stops. This is the one mandatory case |
| `wdi-reconcile` found two documents disagreeing with no clear winner | That is a decision, not drift |

Minutes MUST NOT be treated as a decision record. They say what was discussed; a `DEC-` says what was
chosen and what it cost.

**`SCP-` is retired.** A course correction is a decision, and it is a `DEC-` with
`type: course-correction`. No second code names the same thing.

## Rules

- A `DEC-` MUST be opened **before** the code that depends on it, never written afterwards to explain
  code that already exists.
- The applying pass MUST NOT improvise. When an `accepted` `DEC-` does not say clearly what a document
  has to change, the decision is incomplete and is sent back.
- Applying MUST NOT widen beyond what the decision says. A neighbouring paragraph that now looks wrong
  is a finding to report.
- V8 checks that every `applied` `DEC-` names a non-empty `touches`. It MUST NOT check that a decision
  serves an `FR` or `NFR` — *"the filter works like this"* serves none, and it is exactly the kind of
  decision this guide exists to keep.
- `ADR-NNN` written inside a document frozen before 2026-08-18 is a **retired alias** for `DEC-NNN`
  with the same number. It MUST NOT be read as a second, missing record, and those documents MUST NOT
  be rewritten to change the prefix.
