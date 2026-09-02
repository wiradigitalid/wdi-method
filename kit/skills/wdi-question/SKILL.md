---
name: wdi-question
description: Use when something cannot be decided now and must not be silently assumed. Files it into one of four lists in .control/questions/ by what the reader has to do about it, and closes it in place when the answer arrives.
---

# WDI Question

Free of stage and free of role. The purpose is narrow: make sure an unresolved thing is written down
where it will be seen, instead of becoming an assumption nobody remembers making.

The old single list reached `OQ-146` and stopped being readable. It is now four files in
`.control/questions/`, split by **what the reader has to do about it** — not by subject, and not by
severity.

| File | Holds | Read when |
|---|---|---|
| `blocking.md` | Holds a gate. Target ≤3 per Product Component | Every gate |
| `assumptions.md` | An assumption the agent took itself. One line: the assumption plus the cost of being wrong | Swept once per gate; MAY be skipped |
| `external.md` | Waiting on a file, an action, or a credential from outside. Owner and `by_when` required | Before go-live — **not** at a design gate |
| `answered.md` | Archive. Closed in place, never deleted | Almost never; only to stop a question being reopened |

**Only `blocking.md` holds a gate.** `external.md` holds go-live; `assumptions.md` holds nothing.

## The default class is `assumptions.md`

A question is filed there unless it passes one of three tests. One is enough:

1. It touches money, personal data, or a legal obligation.
2. It changes the wording of an `FR`'s promise.
3. Answering it wrong forces a rewrite of more than one Product Component.

Failing all three, you take the answer yourself — and then one more test decides whether it is
recorded at all.

## The recording threshold — most assumptions MUST NOT be written down

**Two filters, and a line has to pass both.**

**First: it is about the PRODUCT, not about the corpus.** An open question names something undecided
about what is being built — a behaviour, a boundary, a promise, a limit. *"Does the SRS contradict the
SDD"* is not an open question; it is an **edit**, and it goes to whichever skill owns the file. A
question about which document says what has never once changed what gets built, and it is the single
easiest way to fill this list with rows nobody can act on.

**Second: an assumption whose reversal costs less than the conversation about it MUST NOT be recorded.
The shipping default IS the record.**

The test is the `Cost if wrong` column that already exists. If the honest answer is *one setting
changes* · *one default changes* · *a shortcut is added later* — with no rework, no migration, and
nothing already built on it — then there is nothing to decide and nothing to remember. The code says
what was chosen, and it says it more reliably than a line in a list.

This is not a licence to assume quietly. It is the opposite: it protects the list. One real corpus
carried twenty-five open lines, and **six** of them were this class — a default image dimension, how many
quality presets to offer, whether one working folder at a time is enough. Every one had a default already
running and a one-value reversal. Sitting in the same list as six real decisions, they made a
six-item list look like twenty-five items of homework, and the owner stopped reading it.

**The threshold does NOT apply**, and the line is recorded, when being wrong touches money, personal
data, an irreversible action, a third-party contract, or the wording of an `FR`'s promise. Those are
the three tests above, and they always win.

**You MUST NOT register a question as blocking "to be safe."** That habit is what produced 146 ids and
a list nobody read, and the cost is paid at every gate afterwards.

## One batch, per gate, already ranked

Inside a single working pass you do **not** ask. You collect. The batch is delivered once, at the gate,
ranked, and it MUST NOT be dribbled out as each question surfaces.

A healthy batch on `mode: catalog`: **≤3 blocking questions, plus ≤15 one-line assumptions.** A batch
larger than that is a signal about the pass, not about the corpus — say so rather than delivering it
as a list.

When N agents ran in parallel, their questions arrive as **one** ranked batch, never as N reports.

## Every row says whose it is, and whether it can be answered at all

The four files split by **what the reader has to do**. That was not enough: a file can still hold
lines nobody may answer yet beside lines the owner owes today, and then the owner opens it and sees
one flat pile. In the corpus above, of twenty-five open lines exactly **six** were the owner's and
answerable — the other nineteen were frozen, waiting on a measurement, external, or fossil.

So every row carries **`Whose`**, and the vocabulary is closed:

| `Whose` | Means | Who acts |
|---|---|---|
| `owner` | A judgement only the owner can make, and it can be made now | the owner |
| `run: <what>` | The answer comes from running or measuring something, not from an opinion | **you**, not the owner |
| `frozen: DEC-NNN` | An applied decision forbids answering it yet | nobody, until that `DEC-` lifts |

`run:` MUST name what has to be run. "Needs testing" is not a value; `run: capture 5-finding review,
measure handoff time` is. A row that cannot name it is not waiting on a measurement — it is an
`owner` row in disguise.

`frozen:` MUST name a `DEC-` that is `applied` and that actually forbids the work. A freeze covers
**planning as well as building**: where a decision bans new `FR`, new use cases, and a UX pass in a
component, answering a design question there is exactly what it bans. When that `DEC-` lifts or is
superseded, its frozen rows become `owner` rows automatically — no re-triage.

A row whose `Whose` is wrong is worse than a missing row, because it puts work in the wrong person's
lap and it is invisible.

## Registering

| Field | Rule |
|---|---|
| Question | One sentence, answerable. "How should referrals work?" is a topic, not a question |
| Blocks | What cannot proceed — a gate, an `FR`, a ticket, or nothing |
| Whose | `owner` · `run: <what>` · `frozen: DEC-NNN`. See above |
| Owner | Who can answer. A question with no owner is a wish |
| By when | The moment it must be answered, usually a gate |

Ids stay `OQ-`, allocated from the highest ever used including closed ones. An id MUST NOT be reused.

A question whose discussion outgrows one line gets `.control/questions/OQ-NNN-<slug>.md` in the same
folder, from `templates/oq.md`, and the list keeps a one-line pointer. The old home
`.control/supplements/` is gone.

## Closing

An answered question is closed **in place** — the answer written beside it with the date and who
answered — then moved to `answered.md`. You MUST NOT delete the entry.

**A fossil is closed, not answered, and you MUST look for fossils first.** A row questioning a rule, a
layer, or a validator that has since been repealed cannot bite again: it closes with the repeal as its
answer and MUST NOT be put to the owner as a decision. These are free, and a long list usually holds
several — one real corpus was still carrying a question about `parallel-tickets-blocked`'s shape after the layer `parallel-tickets-blocked` runs
on had been retired.

**An answer goes into the document it belongs to, and that is usually the end of it.** An `FR` in the
PRD, a rule in `business-rules.md`, a line in the brief — written there, closed here, done. The closure
routes to `wdi-decision` **only** when the answer has no home in any design document, or contradicts an
`AD-N`. `decision-guide.md` § A decision's first home owns that split, and a `DEC-` is never permission
to edit a document.

This matters most at G1 and G2, where almost nothing is homeless yet: an answer about a brief belongs in
the brief.

## Rules

- You MUST NOT answer the question yourself when the owner is the client or a stakeholder. Drafting a
  proposed answer for them to confirm is useful; recording it as settled is not.
- An `[ASSUMPTION]` tag left in a PRD, an SRS, or an SDD MUST be filed here before that document
  passes its gate. That is precisely the failure this skill exists to prevent.
- A question past its "by when" MUST be raised, not silently carried forward. Carried forward twice is
  a signal that either the owner is wrong or the question is not real.
- A row MUST move between files when its class changes, and MUST NOT be copied into a second one. An
  assumption that turns out to touch money moves to `blocking.md`; it does not appear in both.
- Terms MUST match `.control/product-glossary.md`.

## Output

**The owner's section MUST contain only `owner` rows.** Everything else is reported as a count with one
line saying why it is not theirs — never as a list they have to read past. A report that shows all
nineteen alongside the six is the failure this skill was reshaped to end.

| Section | Contents |
|---|---|
| **Yours, now** | every `owner` row, ranked. This is the list |
| Mine | `run:` count, plus what has to be run |
| Frozen | `frozen:` count, plus which `DEC-` holds them and what lifts it |
| External | `external.md` count. States plainly that it holds no design gate |
| Not recorded | how many assumptions the threshold turned away this pass |

Then: which file each question landed in, and anything routed on to `wdi-decision`.

**"Are we done — no more OQ?" is answerable, and the honest answer is usually no.** Say which third is
the owner's, name what lifts the frozen third, and name what you have to run for the rest. A clean
list is not the goal; a list where every line is somebody's and actionable is.
