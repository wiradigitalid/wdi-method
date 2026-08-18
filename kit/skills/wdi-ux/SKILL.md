---
name: wdi-ux
description: Use when UX is produced or landed — dispatching bmad-ux for a PRD scope, then landing DESIGN.md, EXPERIENCE.md, the design system, and the screen registry into the layers they belong to. Optional, and it rides on G2. Never writes UX content itself.
---

# WDI UX

`bmad-ux` writes the UX. This skill decides whether it should run, hands it the scope, checks what
came back, and — because `bmad-ux` is **class B** — lands its output into the two layers it splits
across. No other skill MAY land these files.

Two acts, and a pass MAY do either or both: **run** the UX, and **land** it. They are separated because
they become possible at different moments. A run belongs to G2, where the PRD is fresh. Landing needs a
Product Component to land into, and that list is not born until the tail of G2.

You MUST NOT write or edit `DESIGN.md` or `EXPERIENCE.md` yourself. If a check fails, name what is
missing and re-dispatch — a hand-patched UX document makes the memlog lie about how it got that way.
The content rules are in `ux-guide.md` and MUST NOT be restated here.

## Inputs

| Source | What it answers |
|---|---|
| `.what/_prd/<initiative>/prd.md` | The promises the UX has to make usable — `FR`, `NFR`, `UJ-N` |
| `.what/_product-brief/brief.md` | The primary user, and the boundary the UX MUST respect |
| `.constitution/method/document/ux-guide.md` | The rules the result is checked against |
| `.constitution/method/document/templates/ux.md` | The required shape of each half |
| `.control/registry/components.yaml` | Whether the Product Components and containers a landing needs exist |
| `.constitution/method/document/templates/design-system.md` | The shape of the product-level tokens file |
| `.control/product-glossary.md` | Terms already fixed, so the screens do not invent competing ones |
| `_bmad-output/ux/` | An earlier run — the input to *land*, and to intent *update* |
| `.how/_platform/design-system.md` | Tokens and base components already agreed |

## Step 1 — Position

- UX is **optional**. It earns a run when the interface is a substantial part of what the PRD
  promises; it MUST NOT be run to fill a slot. Say so and stop when a run buys nothing.
- The order is `wdi-product` → `wdi-ux`. A UX run with no PRD in scope is designing a promise nobody
  made; route to `wdi-product` first.
- If the ask is a new capability rather than how an agreed one feels, this is the wrong skill — route
  to `wdi-product` intent `update`.
- If the ask is how the system behaves internally, route to `wdi-blueprint` for the catalogue, or
  `wdi-component` for a full flow.

## Step 2 — Mode

Read `_bmad-output/ux/` and `components.yaml`, then state the mode in one line before acting.

| State | Mode |
|---|---|
| No run for this scope | **run** — Step 3, then Step 5 for whatever is landable |
| A run exists, finalised, nothing landed | **land** — Step 5 only |
| A run exists and the PRD has changed under it | **run** intent *update*, then Step 5 |
| A run exists, landed, and a `<pc>` has since been born | **land** — the deferred half, Step 5 |

## Step 3 — Dispatch

Invoke `bmad-ux` with the detected intent. Do not restate the rules to it — they arrive through
`doc_standards` and `persistent_facts` in `_bmad/custom/bmad-ux.toml`, and a second copy here would
drift.

State the scope as **one PRD initiative**, and name the input files explicitly; the skill globs its
own default locations, which this project redirects. A scope spanning several initiatives MUST be
split into one run each — the run folder is a singleton per scope, and two initiatives in one folder
cannot be landed separately later.

## Step 4 — Verify

Check what came back against the guide. Report every failure; fix none of them by hand.

| # | Check | Fails when |
|---|---|---|
| 1 | Landing zone | Anything was written into `.what/` or `.how/` by the run itself |
| 2 | Two documents, split correctly | A layout, component, or token sits in `EXPERIENCE.md`; a promise sits first in `DESIGN.md` |
| 3 | Journeys reference `UJ-N` | The PRD's journeys were restated under new names |
| 4 | Every screen has an empty and an error state | Only the populated state was designed |
| 5 | Every user-facing noun is in the glossary | A new noun appeared — route it through `wdi-blueprint`, which owns the glossary, in this pass |
| 6 | No new capability | The run designed something no `FR` promises — route to `wdi-product`, and MUST NOT land it |
| 7 | Every `[ASSUMPTION]` filed | An assumption sits in the text with nothing in `.control/questions/` behind it |
| 8 | Memlog at `.control/memlog/ux.md` | A `.memlog.md` appeared inside the corpus — `--workspace` was used |
| 9 | `bmad-review` structure + prose ran at finalize | `doc_standards` did not fire |

Check 8 is the one that MUST be fixed immediately rather than reported. A `.memlog.md` inside `.what/`
or `.how/` is corpus pollution, and V16 rejects it.

## Step 5 — Land, at two speeds

Nothing is landed until the run is finalised. The homes are in `corpus-guide.md`; what is decided
here is **when each one becomes possible**.

| Output | Lands into | Possible once |
|---|---|---|
| Tokens and base components | `.how/_platform/design-system.md` | The run is final — it crosses components by definition |
| `EXPERIENCE.md` | `.what/<pc>/04-usecases/` | The `<pc>` is registered in `components.yaml` |
| `DESIGN.md` | `.how/<pc>/01-ux/` | The `<pc>` is registered **and** its container exists |
| Each screen | an `LC` of type `ui-screen` in `components.yaml` | Same as `DESIGN.md` — an `LC` MUST name its container. Registration is checked at wave close, V12 |

- A half that is not yet landable MUST stay in `_bmad-output/ux/` and be reported as deferred. At G2
  that is the normal outcome, not a failure: the slicing is born at the tail of G2 and containers at G3.
- You MUST NOT create a Product Component or a container to make a landing possible. A PC comes from
  `wdi-init` intent `component` and a container from `wdi-blueprint` intent `platform`.
- One run MAY land across several Product Components. Split by which `<pc>` the content serves; a
  screen whose `<pc>` is ambiguous MUST be raised through `wdi-question`, not assigned by guess.
- Registering the screens is part of landing `DESIGN.md`, in the same act. A screen in `01-ux/`
  without its `components.yaml` entry has been half-landed, and V12 catches it at a worse moment.
- `.how/_platform/` otherwise belongs to `wdi-blueprint`. `design-system.md` is the one file in it you
  own, and it has its own template; you MUST NOT touch any other.
- The run folder MUST NOT be deleted after landing. Intent *update* reads it again.

## Step 6 — Impact

A landed UX changes what other documents can still claim. Check, and **report** — never edit.

| Found | Where it goes |
|---|---|
| A flow the PRD does not promise | `wdi-product` intent `update`, before it is designed |
| A behaviour the SRS never stated | `wdi-blueprint` for a catalogue line, `wdi-component` for a flow |
| A pattern that forces a technology choice | `wdi-decision` — a `DEC-`, not a note in `DESIGN.md` |
| A screen contradicting an `applied` `DEC-` | `wdi-decision` — a new `DEC-`, never an edit to one already applied |

`wdi-reconcile` is the read-only sweep across all layers. Run it rather than reimplementing it.

## Step 7 — Memlog

Everything in a UX pass — the run and the landing — logs to `.control/memlog/ux.md`, through
`memlog.py --path`. `--workspace` MUST NOT be used.

## Rules

- Content MUST NOT be edited while it is being landed. Splitting one document across the homes its
  row names is not editing; changing a sentence to fit its new home is, and it goes back through
  `bmad-ux`.
- You MUST NOT open G2 on UX that has not been through check 9. Gate time is for deciding.
- You MUST NOT raise `status:` as part of landing. Status is a stage; the `reviewed:` block is an
  event, and `wdi-review` writes it.
- You MUST NOT land anything into a wave that is already closed. The wave is reopened through
  `wdi-build`, or the gap is filed through `wdi-question`.
- When the UX concludes the PRD promised something that cannot be made usable, say so and stop. Route
  to `wdi-product`; do not quietly narrow the promise in `EXPERIENCE.md`.

## Output

A short report: mode taken, scope run, the result of all nine checks naming the failures, what landed
and where, what was deferred and what has to exist before it can land, screens registered, impact
found and where it was routed, and open questions raised.
