---
name: wdi-log
description: Use when a fact from outside the code has to be recorded — a meeting that finished, or a non-technical fact that constrains what may be built. Two intents, meeting and fact. Routes decisions and open questions to their own skills.
---

# WDI Log

Free of stage and free of role. Two intents, because both record **a fact that came from outside the code** and
neither belongs to any gate.

| Intent | Owns | Home |
|---|---|---|
| `meeting` | What a meeting decided and left open | `.control/meetings/YYYY-MM-DD-<slug>.md` |
| `fact` | A non-technical fact that constrains what may be built, used, or promised | `.control/project-non-technical-log.md` |

They share a shape and a failure mode: both are tempting places to record something that belongs somewhere with
an owner. Neither MAY absorb a decision or an open question.

## Intent `meeting`

### What the note MUST carry

| Section | Content |
|---|---|
| Attendees and date | Who was actually there, not who was invited |
| What was decided | Each decision as one sentence, stated as what now holds |
| What was left open | Each unresolved item, with who can resolve it |
| Action items | Grouped by role, each with an owner |
| `## DEC` | Links to the decisions this meeting produced — filled after `wdi-decision` runs |

The `## DEC` back-link makes the trail run both ways. Minutes whose decisions have no `DEC-`, and a `DEC-` with
no minutes behind it, are both traceability gaps the audit surfaces later at a worse time.

### Rules

- It MUST NOT write the decision itself. That goes to `wdi-decision` intent `open`, which numbers it globally.
  Minutes say what was **discussed**; a `DEC-` says what was **chosen** and what it cost.
- It MUST NOT write to `.what/` or `.how/`. A meeting changes documents only through `wdi-decision` intent
  `apply`.
- It MUST NOT record an open question only in the note. Those go to `wdi-question`, so they land in one of four
  lists rather than scattered across meetings nobody rereads.
- Record what was decided, not what was discussed. A transcript is not minutes, and nobody rereads one.
- A decision recorded with no owner and no consequence MUST be treated as an open question instead. "We agreed
  to look into it" is not a decision.
- Client commitments MUST be recorded verbatim where the wording matters. Paraphrasing a commitment is how a
  scope dispute starts.

## Intent `fact`

`.control/project-non-technical-log.md` is the authority on **what may be recorded** — its content boundary, its
closed category list, and the table of facts belonging to another home. Read it before acting; this skill MUST
NOT restate those rules and MUST NOT override them. What this skill owns is **how** the file is read and written.

### Looking one up

1. Read the In force table in full. It is short by design and MUST NOT be sampled with grep alone — a fact retired
   last week reads as current when only its row is seen.
2. Check No longer in force for the same subject. A superseded entry names its replacement.
3. If the answer is absent, **say it is absent.** You MUST NOT infer a fact from a commit message, from
   `.control/memlog/`, or from a sibling repo and report it as recorded — those are leads for registering, not
   answers.

An entry marked `[UNCONFIRMED]` MUST be reported with that tag attached, never flattened into a plain
fact.

### Registering one

1. Apply the log's content boundary first. A fact that fails it is refused here and MUST NOT be softened to fit —
   say which rule refused it and where it belongs.
2. **Route before writing.** If the fact is a decision expensive to reverse, an open question, a meeting outcome,
   a domain term, or an infrastructure asset detail, its own skill or repo runs first. A row here MAY then hold
   only the consequence for this product, pointing at that home.
3. Assign the next `NT-NNN` from the highest id ever used, including retired ones. An id MUST NOT be reused.
4. Fill every column. `Effect` MUST name something in this repo — a gate, an `FR`, a prerequisite, a file.
   `Source` MUST name a person, a repo and path, or another entry id.
5. A fact whose source is hearsay MUST be written with `[UNCONFIRMED]` **and** filed through
   `wdi-question` in the same run. Recording it and leaving it unowned is the failure this step exists to stop.

**One fact, one row.** A single event producing several facts — a domain bought, and a launch date it makes
possible — MUST become several rows, because they stop holding at different times.

### Updating one

A fact that changed is **never** edited in place, and its row is never deleted.

1. Move the old row to No longer in force, filling `Stopped holding` with the date and `Superseded by` with the new
   id.
2. Register the new fact as a fresh `NT-NNN`.
3. Follow the old row's `Effect` and check whatever it named. A fact that stops holding usually leaves a document
   behind that still assumes it; that document MUST be raised, and if it sits under an `applied` decision, routed
   to `wdi-decision` intent `apply`.

Correcting a typo or a wrong `Source` is not an update in this sense and MAY be edited in place.

## Rules

- Terms MUST match `.control/product-glossary.md`. A note that coins a new domain noun MUST propose it through
  `wdi-blueprint`, not leave two words meaning the same thing.
- This skill MUST NOT write any file other than the two it owns. Every other file it touches is reached through
  the skill that owns it.
- `.control/structure-document.md` MUST NOT be edited to reflect a new entry — it maps folders, not rows, and
  `wdi-init` intent `structure` re-derives it.

## Output

Intent taken · what was recorded, in one line · what was **routed** rather than recorded, and to which skill ·
for `fact`, the `NT-` id and what its `Effect` names.
