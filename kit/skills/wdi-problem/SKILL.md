---
name: wdi-problem
description: Use at G1 Problem — when the product brief is created, updated, or validated. Checks position and preconditions, dispatches bmad-product-brief, then verifies the result against brief-guide.md and the template. Never writes the brief itself.
---

# WDI Problem

G1 decides **what the problem is, whose it is, and why it earns work.** `bmad-product-brief` writes the
brief; this skill decides whether it should run at all, hands it the right intent, and checks what came
back. Both halves matter: the override TOML controls **where** the artifact lands, and nothing in BMad
checks **what is in it**.

You MUST NOT write or edit `brief.md` yourself. If a check fails, name what is missing and re-dispatch — a
hand-patched brief makes the memlog lie about how it got that way.

## Inputs

| Source | What it answers |
|---|---|
| `.what/_product-brief/brief.md` | Whether a brief already exists, and what intent applies |
| `.constitution/method/document/brief-guide.md` | The rules the result is checked against |
| `.constitution/method/document/templates/brief.md` | The required shape |
| `_bmad-output/brainstorming/` · `forge/` · `planning-artifacts/` | Raw material available to feed in |
| `.control/product-glossary.md` | Terms already fixed, so the brief does not invent competing ones |

## Step 1 — Position

- If `brief.md` exists, the intent is **update** or **validate**, never **create**. A second create would
  overwrite the singleton.
- If a spec is open and the ask is a scope change rather than a problem change, this is the wrong skill.
  Route to `wdi-decision`, which wraps `bmad-correct-course`.
- If the ask is about one initiative rather than the product, route to `wdi-product`.

## Step 2 — Preconditions

None of these block. Each is a question you MUST put to the owner before dispatching, once.

| Check | Why it matters |
|---|---|
| Is there raw material worth feeding in? | Exploration output in `_bmad-output/` is invisible to the skill unless it is named |
| Does the claim rest on outside data? | Market size, competitor, stack choice — those want `bmad-deep-recon` first |
| Is the primary user already obvious? | If not, discovery is not finished and the brief will stall at the gate |

## Step 3 — Dispatch

Invoke `bmad-product-brief` with the detected intent. Do not restate the rules to it — they arrive through
`persistent_facts` and `doc_standards` in `_bmad/custom/bmad-product-brief.toml`. Repeating them here would
create a second copy that drifts.

Name the raw-material files explicitly in the handoff. The skill globs its own output locations, and this
project redirects them.

## Step 4 — Land the Goals

The template's `Goals` section is a pointer: `Goals — see goals.yaml → goals:`. The engine drafts
`BG-N` statements in conversation, but nothing in `bmad-product-brief` writes them anywhere durable —
the returned `brief.md` has no place left to hold them.

Write each goal discussed as a row in `.control/registry/goals.yaml` → `goals:`, with the next
`id` in sequence and its `statement`. Add a `why:` field only when the goal's justification is not
already carried by `The Problem` or `Why` — most goals need no `why:` at all. This step is what
finishes the brief; a pointer to an empty list is not a finished G1 artifact, and you MUST NOT report
it as one.

This is landing, not editing `brief.md` — the rule in the header is about the prose document, not the
registry. Registry conversion is part of producing the artifact, the same way it is for a screen
becoming an `LC` row.

## Step 5 — Verify

Check the returned brief against the guide. Report every failure; fix none of them by hand.

| # | Check | Fails when |
|---|---|---|
| 1 | Home | Anything landed outside `.what/_product-brief/` |
| 2 | Eight required sections present | The template's "drop what does not earn its place" was applied to one of them |
| 3 | Exactly one `primary` in Who This Serves | Zero, or more than one |
| 4 | Goals numbered `BG-N`, landed in the registry, and the brief's own section stays a pointer | A goal's statement was written into the brief instead of, or as well as, the registry row from Step 4 |
| 5 | Success Criteria names exactly one measurable figure, with a timeframe | A mission statement, a mix of signals, or a claim nobody could check without opening the code |
| 6 | Scope Out written as items | Left implicit |
| 7 | No Assumptions or Prerequisites section | Either appeared in the brief instead of being routed through `wdi-question` |
| 8 | Memlog at `.control/memlog/brief.md` | A `.memlog.md` appeared inside `.what/` — `--workspace` was used |
| 9 | No raw material folded in | Research or brainstorming prose copied into the brief instead of cited |
| 10 | No Product Component list | A slicing was written at G1; it belongs to `wdi-init` intent `component`, after G2 |
| 11 | `bmad-review` structure + prose ran | `doc_standards` did not fire |

Check 8 MUST be fixed immediately rather than reported. A `.memlog.md` inside `.what/` is corpus pollution,
and every later run compounds it.

## Rules

- You MUST NOT land anything from `_bmad-output/` into the corpus beyond the brief itself. Every other
  output has its owner in the table in `corpus-guide.md`, and for exploration output the answer is that it
  stays put.
- You MUST NOT delete an exploration run folder after feeding it in. The `update` intents re-read the
  original inputs.
- You MUST NOT open G1 on a brief that has not been through check 11. Gate time is for deciding.
- A brief concluding the idea is not worth building is a **pass**. You MUST report it as one rather than
  offering to rework it.
- Every unresolved `[ASSUMPTION]` MUST be filed through `wdi-question` before the gate opens — into
  `assumptions.md` by default, `blocking.md` only through the three tests that file states.
- When the ask is about the Product Component slicing, this is the wrong skill at any point. Before the list
  exists it belongs to `wdi-init` intent `component`; after G3 a correction goes through `wdi-decision`.

## Output

A short report: intent dispatched, what the brief now claims in one line, the goal rows landed in Step 4,
and the result of all eleven checks — naming the failures, not summarising them away.
