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

Failing all three, you MUST take the answer yourself and record it as one line — the assumption, and
what it costs if it is wrong.

**You MUST NOT register a question as blocking "to be safe."** That habit is what produced 146 ids and
a list nobody read, and the cost is paid at every gate afterwards.

## One batch, per gate, already ranked

Inside a single working pass you do **not** ask. You collect. The batch is delivered once, at the gate,
ranked, and it MUST NOT be dribbled out as each question surfaces.

A healthy batch on `mode: catalog`: **≤3 blocking questions, plus ≤15 one-line assumptions.** A batch
larger than that is a signal about the pass, not about the corpus — say so rather than delivering it
as a list.

When N agents ran in parallel, their questions arrive as **one** ranked batch, never as N reports.

## Registering

| Field | Rule |
|---|---|
| Question | One sentence, answerable. "How should referrals work?" is a topic, not a question |
| Blocks | What cannot proceed — a gate, an `FR`, a story, or nothing |
| Owner | Who can answer. A question with no owner is a wish |
| By when | The moment it must be answered, usually a gate |

Ids stay `OQ-`, allocated from the highest ever used including closed ones. An id MUST NOT be reused.

A question whose discussion outgrows one line gets `.control/questions/OQ-NNN-<slug>.md` in the same
folder, from `templates/oq.md`, and the list keeps a one-line pointer. The old home
`.control/supplements/` is gone.

## Closing

An answered question is closed **in place** — the answer written beside it with the date and who
answered — then moved to `answered.md`. You MUST NOT delete the entry.

If the answer amounts to a decision that is expensive to reverse, the closure MUST route to
`wdi-decision`. This list records that an answer arrived; a `DEC-` records what was chosen and what it
cost.

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

Which file each question landed in, the blocking ones ranked, the assumptions as one-line rows, and
anything routed on to `wdi-decision`.
