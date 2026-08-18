---
status: Accepted
---

# UX Guide

**Loaded when:** running `bmad-ux`, or placing its output

`bmad-ux` produces two documents that belong to **two different layers**. That split is the whole
reason this guide exists: everything else follows from getting it right.

## Two outputs, two layers

| Output | Home | Layer | Answers |
|---|---|---|---|
| `EXPERIENCE.md` | `.what/<pc>/04-usecases/` | Promise | What the user experiences, and what they can get done |
| `DESIGN.md` | `.how/<pc>/01-ux/` | Build | Screens, states, components, and how they are put together |

The test is the usual one. If a sentence would still be true after a full redesign, it is experience
and belongs in `.what/`. If it names a layout, a component, or a token, it is design.

Getting this backwards is expensive in a specific way: a `DESIGN.md` filed under `.what/` makes the
promise layer freeze around one visual solution, and every later redesign then reads as a broken
promise.

## The landing zone

`bmad-ux` is a **class B** skill: it writes to a neutral landing zone at `_bmad-output/ux/`, and
`wdi-ux` — which is what dispatched it — lands the output from there.

- Output MUST land in `_bmad-output/ux/` first. A UX run MUST NOT write directly into `.what/` or
  `.how/`.
- Landing MUST go through `wdi-ux`, which owns `.what/<pc>/04-usecases/` and `.how/<pc>/01-ux/`. No
  other skill MAY land these files.
- Nothing is placed until the run is finalised. Half-placed UX output is worse than unplaced output,
  because it looks distributed.
- A run MAY finish before there is a `<pc>` to place it into — the slicing is born at the **tail of
  G2**, and a UX run belongs to G2 itself. The output then waits in `_bmad-output/ux/`, and `wdi-ux` lands it once
  the component exists. Waiting is the correct state; a home MUST NOT be invented to end it.

`doc_standards` on `bmad-ux` runs `bmad-review` over both documents **at finalize** — that is, before
`wdi-ux` lands them. Reviewing afterwards would mean reviewing two files that no longer sit together.

## Registry consequences

Placement is not finished when the files have moved.

- **Every screen in `DESIGN.md` MUST be registered as an `LC` of type `ui-screen`** in
  `.control/registry/components.yaml`, with its `container`. A screen that exists in the design and not
  in the registry is a change nothing will trace, and V12 catches it **at wave close**.
- A composite that is reused across screens is an `LC` of type `ui-composite`, not a screen.
- Tokens and base components — colour, type scale, spacing, buttons, inputs — MUST go to
  `.how/_platform/design-system.md`, not into any one component's `01-ux/`. They cross Product
  Components by definition.

Registry conversion is part of placement, not a follow-up.

## Vocabulary

Every user-facing noun in either document MUST already exist in `.control/product-glossary.md`, used
verbatim. A new domain noun introduced by a UX run MUST be added through `wdi-blueprint` intent
`catalog` in the same pass, which owns the glossary.

This is where vocabulary drift usually enters the corpus: UX writes the words the user actually sees,
and those words are the ones that stick. When the SRS says `Anggota` and the screen says `Pengguna`,
the screen wins in practice and the corpus starts lying.

## What UX does not decide

- **Requirements.** A UX run that discovers a needed capability has found an `FR`, and it MUST go to
  the PRD through `wdi-product` intent `update` before it is designed.
- **Behaviour.** How the system responds belongs to `SRS-<pc>.md`. `EXPERIENCE.md` says what the user
  perceives, not what the system does internally.
- **Architecture.** A UX need that forces a technology choice MUST become a `DEC-`, not a note in
  `DESIGN.md`.

## Passing G2

`DESIGN.md` is an **attachment** at G2, not the document being read. What the Product Owner actually
reads is `prd.md` and `EXPERIENCE.md` — and G2 gets 45 minutes, twice any other gate, precisely
because it decides two things: what is built, and how it feels to use.

The gate question that catches a weak `EXPERIENCE.md` is checklist item 4: *can I retell the main UX
flow in five sentences without opening the document?* An experience that cannot be retold has not
been decided, only drawn.

Every `[ASSUMPTION]` left in either document at finalize MUST be registered through `wdi-question`
before the gate opens.

## Rules

- You MUST NOT edit content while placing it. If the content needs changing to fit its new home, that
  is a UX revision, and it goes back through `bmad-ux`.
- `EXPERIENCE.md` MUST reference use cases by ID where the chain matters. A journey that maps to no
  `UC` is either a missing use case or a promise nobody made.
- Durable UX decisions — why a pattern was chosen, what was rejected — belong in a `DEC-` or in the
  run's addendum, not as prose inside `DESIGN.md`.
- The UX run folder in `_bmad-output/ux/` MUST NOT be deleted after placement. Intent *update* reads
  it again.
