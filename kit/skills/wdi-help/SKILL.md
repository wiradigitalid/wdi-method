---
name: wdi-help
description: Use when you need to know where the project stands in the delivery flow and which skill comes next. Answers from this project's five gates, not from BMad's phase column.
---

# WDI Help

`bmad-help` cannot answer "where am I" in this project. Its progress detection globs `output-location`
paths resolved from `resolve_config.py`, so it is blind to every class-A artifact this project redirects
into `.what/` and `.how/`. It also lists two required gates — `epics.md` and `sprint-status.yaml` — that
this project's route never produces, and it is the only BMad skill with no `customize.toml`, so none of
that can be corrected.

This skill replaces it for position and routing. `bmad-help` remains useful for one thing only: questions
about BMad itself.

## Inputs

| Source | What it answers |
|---|---|
| `.control/generated/status` | Which wave is open, which stories sit at which status, which validators are red |
| `.control/registry/index.yaml` | The global `mode`, and the gate map |
| `.control/registry/components.yaml` | Per-component `mode`, `risk_accepted`, and `g4_passed` |
| `.control/registry/waves.yaml` | Wave → release, size, `depends_on` |
| `.constitution/method/document/delivery-flow-guide.md` | The five gates and their checklists |
| `.constitution/method/why/README.md` | The whole shape, when the caller has never seen the method |

You MUST read `.control/generated/status` rather than counting files yourself. It is generated from the
registry; hand-counting produces a second answer that will disagree.

## What to answer

Three things, in this order, and nothing else unless asked:

1. **Where the project stands** — the last gate passed, and which gate is next.
2. **What blocks that gate** — the specific artifact, validator, or blocking question that is not ready.
3. **Which skill to invoke next** — one skill, named, with its intent, and the reason in a clause.

Keep it under fifteen lines. A routing answer that needs scrolling has failed at its job.

## The one thing that changes the answer

**Read the component's `mode` before routing to G4.** A component at `mode: catalog` skips G4 entirely —
routing it to `wdi-component` is wrong, and the next step is `wdi-build`. That is the single most common
mis-route in this flow, because every other gate is the same for every component.

## Routing by what exists

| State | Next |
|---|---|
| No registry, or no global `mode` set | `wdi-init` intent `setup` — nothing has started |
| No `.what/_product-brief/brief.md` | `wdi-problem` — G1 has not started |
| A brief exists, and no PRD covers the area in play | `wdi-product` intent `prd` |
| A PRD covers it but the promise has moved | `wdi-product` intent `update` — never a second PRD for the same area |
| Only the **wording** of an `FR` is wrong | Nobody. Whichever skill is at work fixes it directly; putting it behind a gate is how three earlier corrections were dropped |
| A PRD exists and the interface is a large part of what it promises | `wdi-ux` — optional, and it lands nothing until a `<pc>` exists |
| A PRD exists, no `product_components` yet | `wdi-init` intent `component` — the slicing is born here, at the tail of G2 |
| Components exist, `mode` or `risk_accepted` unset | `wdi-init` intents `mode` and `risk` — both are the owner's, and G4 cannot be read without them |
| Components exist, no UC catalogue or no spine | `wdi-blueprint` — intent `catalog` first, then `platform` |
| The blueprint is complete and G3 has not been held | The gate. Read `.control/generated/blueprint.md`, not seven files |
| G3 passed, a component at `outline`/`guarded`/`deep` has no depth | `wdi-component` |
| G3 passed, the component is at `mode: catalog` | `wdi-build` — G4 is skipped by design |
| Depth done and G4 passed for every component the work touches | `wdi-build` — it opens the wave, runs `bmad-spec`, ships each story, closes the wave |
| A small fix touching no `FR`, `UC`, `AD-N`, or domain model | Fast Path: `bmad-build` directly. It stops and becomes a wave `S` the moment an `FR` is touched |
| A planning assumption turned out void | `wdi-decision` intent `open` — it proposes, and changes nothing |
| An accepted `DEC-` has not reached its documents | `wdi-decision` intent `apply` |
| A bug, a failing test, unexpected behaviour | `wdi-systematic-debugging`, before any fix is proposed |
| Numbers are wanted before the work is committed | `wdi-report` intent `estimate` |

A brief that exists but is thin is still a brief. You MUST NOT route back to `wdi-problem` because a
section reads weakly — route there only when the brief is absent, when a change signal invalidates what
it claims, or when one of its eight required sections is missing outright.

## Rules

- You MUST answer from this project's five gates — G1 Problem · G2 Product · G3 Blueprint · G4 Component ·
  G5 Release. BMad's `phase` column MUST NOT be used; it mixes two conventions and names gates this
  project does not run.
- When a `wdi-*` wrapper exists for a BMad skill, you MUST name the wrapper, never the skill it wraps. The
  wrapper carries the position check and the content checks; routing past it produces an artifact nothing
  verifies. Today every BMad skill this method uses has one: `wdi-problem`, `wdi-product`,
  `wdi-blueprint`, `wdi-build`, `wdi-decision`, `wdi-review`, `wdi-ux`.
- Only `.control/questions/blocking.md` holds a gate. `external.md` holds go-live and MUST NOT be reported
  as blocking a design gate; `assumptions.md` holds nothing.
- You MUST NOT invent progress. If `.control/generated/status` is missing or stale, say so and name
  `validate.py --generate`.
- You MUST NOT run other skills on the user's behalf. Name the skill; let them invoke it.
- When the next step is blocked by a decision rather than by work, route to `wdi-question` or
  `wdi-decision`, not to a producing skill.
- When asked about BMad itself — what a BMad skill does, what it writes, which are deprecated — answer
  from `bmad-skill-register.md`, and only fall back to `bmad-help` for module documentation.
- When the caller has never seen this method, point at `.constitution/method/why/README.md` rather than
  paraphrasing it here.

## When there is no wave open

Say so plainly, then route by the table above. An artifact a later gate produces MUST NOT be reported as
missing — that is not a gap, it is the plan.
