---
name: wdi-explain-to-me
description: Use when the owner has to decide something — an open question, a defect, a design fork, a failing validator, a vague worry — and wants the reading done for them. Investigates, then briefs in six fixed sections, in the owner's language. Writes no file; the decision itself goes to wdi-decision or wdi-question.
disable-model-invocation: true
---

# WDI Explain To Me

The owner names a problem. The result is a **decision briefing**: everything needed to decide, with the
agent doing all of the reading and the owner doing only the deciding.

`disable-model-invocation: true` is deliberate. A briefing is written for a person who has to choose;
a skill that wants one has nothing to choose, and would only be reading its own summary back.

Four asks look alike from the outside and are four skills:

| Ask | Skill |
|---|---|
| "Where am I, what next" | `wdi-help` — position and routing, under fifteen lines |
| "Brief me so I can decide this" | **this skill** — investigation, then a briefing |
| "Record what was decided" | `wdi-decision` |
| "This cannot be decided now" | `wdi-question` |

## Inputs

| Source | What it answers |
|---|---|
| The topic argument | An id (`OQ-12`, `DEC-007`, a defect row, a validator name), a file path, or a sentence |
| `.control/registry/*.yaml` · `.control/generated/status` | What the registry says holds today, and which validators are red |
| `.control/questions/` · `.control/decisions/` | Whether this was asked or decided before, and what is already settled |
| The working documents in `.what/` and `.how/` | The promise and the mechanism the topic touches |
| `validate.py` output · tests · git history · the code | What actually holds, as opposed to what a document claims |

## Step 1 — Investigate

When the topic is too vague to investigate, ask **one** narrowing question first — one, not a list. A
briefing on the wrong topic wastes the owner's five minutes.

Then read the sources that bear on the topic before writing a word: files, registries, validator or test
output, git history. Run what can be run. Done when every claim the briefing will make traces to
something read or executed in this session, with its `file:line` in hand.

## Step 2 — Brief

**Language.** Write in the language the owner is using in the conversation. When that is unclear, use
`policy.doc_language` from `.control/registry/index.yaml`. Method terminology — ids, gate names, the
values of `mode` and `risk_accepted`, validator names — stays English as `language-guide.md` requires;
those are keys, not prose.

**Six sections, fixed in number, order, and meaning.** The headings are given here in English; render
each one in the briefing's language and keep its slot. A briefing that drops, merges, or reorders a
section has changed what the owner can compare it against.

1. **Topic** — what kind of thing this is (an `OQ-`? a defect? a design fork? stale prose?) and the one
   decision it asks for. Two or three sentences.
2. **Background** — how it came to exist and what is already settled. Plain language; gloss any term of
   art in half a sentence where it first appears.
3. **Problem Analysis** — what is actually wrong and why, with evidence. Put a `file:line` citation
   beside each claim; the reader MAY verify, but MUST NOT need to.
4. **Solution Design** — 2–4 options. For each: what changes, what it costs, what breaks or is lost, and
   the size of the work. An option whose downside is missing has not been analysed.
5. **Recommendation** — exactly one, with its reason and the single condition that would flip it.
6. **What Helps You Decide** — the facts worth weighing against each other, then a verdict on the
   owner's own eyes: either state that this briefing is sufficient, or name the exact file, section, or
   screen the owner MUST look at themselves and what to look for there. Reserve that second verdict for
   judgement only the owner can make — taste, risk appetite, a promise to a stakeholder — never for
   legwork the investigation could have done.

Done when the owner could decide from the briefing alone, or knows exactly what to open and why.

## Rules

- Reading time MUST stay under five minutes; push detail into citations, not prose.
- A claim without a source read this session MUST NOT appear in the briefing. Memory is not a source.
- This skill writes **no file** and MUST NOT edit anything. The briefing lives in the conversation. It
  MUST NOT open a `DEC-`, file an `OQ-`, or patch the corpus on the way — a briefing that also changes
  things leaves nothing to decide against.
- You MUST NOT run other skills on the owner's behalf. Name the skill; let them invoke it.

## Output

The six sections, then one line naming where the decision goes once it is made: `wdi-decision` intent
`open` when it is worth remembering, the owning document directly when it is not, or `wdi-question`
when it turns out it cannot be decided yet.
