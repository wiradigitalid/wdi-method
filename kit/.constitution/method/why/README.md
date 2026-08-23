---
status: Reference
---

# The WDI Method — orientation

**Opened when:** you have never seen this method before, or you have and want the shape back in one reading.

This file **explains**. It does not bind — `../document/*-guide.md` does, and where the two disagree the guide
wins and the disagreement is a defect to report.

Five minutes. Three files in this folder: this one for orientation, `artifact-map.md` for *"where does this
file go"*, `rationale.md` for *"why is it like this"* — open that one before changing a rule, so you know
what you are about to break.

## What the method is

Two methods joined. **WDI** owns the flow, the gates, and the artifacts nobody else writes. **BMad** owns
the writing skills where it has one. Every BMad skill is invoked through a WDI wrapper, never directly: the
wrapper is what checks position, verifies the result against the guide, and lands the memlog.

The whole thing rests on one sentence:

> Owner time is spent at five points. Between them, the agents work alone.

## Five gates

A gate is named for **what is decided there**, never for the work before it.

| Gate | Decides | How often | Budget |
|---|---|---|---|
| **G1 Problem** | What the problem is, whose it is, why it earns work | once | 20' |
| **G2 Product** | What is built, and how it feels to use | once per PRD | 45' |
| **G3 Blueprint** | The whole portrait: which use cases, their entities, tables, endpoints, screens, and the invariants binding them | once per **product** | 45' |
| **G4 Component** | How one Product Component is built, and what the choice costs | once per **component** | 20–30' |
| **G5 Release** | Whether it is done and proven | once per wave | 10' |

**Only G4 changes shape.** The other four are always the same, whatever the settings — and that is what lets
the whole system be held in one head.

## Two settings, and they control different things

| Setting | Where | Controls |
|---|---|---|
| `mode` | globally in `index.yaml`, per component in `components.yaml` | **Document depth**, and only that |
| `risk_accepted` | per component | **Review intensity**, and only that |

`mode` takes `catalog` · `outline` · `guarded` · `deep`, and the default is `catalog`. A component at
`catalog` **skips G4 entirely** — its control moved to G3, where its use cases, tables, endpoints, screens,
domain model, and C4 were all approved.

`risk_accepted` takes `low` · `medium` · `high`, and its direction reads off the name: `high` means *"I
accept a lot of risk here"*, so its review is the lightest.

Keeping them apart is what lets one component be **thin on purpose and reviewed the hardest**. Why that
matters is in `rationale.md`; what each value demands is in `../document/delivery-flow-guide.md`.

## The run, first time through

| # | Step | Run | Gate |
|---|---|---|---|
| 0 | Set up | `wdi-init` intent `setup` — registry scaffolded, global `mode` set, existing documents reported, structure maps derived | — |
| 1 | Discovery and brief | `wdi-problem` | **G1** |
| 2 | PRD, one per initiative | `wdi-product` intent `prd` | **G2** |
| 2b | UX — only when the interface is a large part of the promise | `wdi-ux` | with G2 |
| 3 | Birth the components, set `mode` and `risk_accepted` | `wdi-init` intent `component` | — (tail of G2) |
| 4 | Blueprint | `wdi-blueprint` intent `catalog`, then `platform` | **G3** |
| 5 | One component's depth | `wdi-component` — as deep as its `mode`; **skipped at `catalog`** | **G4** |
| 6 | Build | `wdi-build` — opens the wave, runs `bmad-spec`, ships each story, closes the wave | **G5** |

After step 6 the next component enters at **step 5**, not at the beginning. Steps 0–4 happen once in the
life of the product.

`SPEC.md` and story files are **not read by humans**. The human review surface stops at the PRD, `.what/`,
and `.how/`.

## The run, every time after

| Situation | Run |
|---|---|
| The next component is being taken on | `wdi-init` intent `mode` or `risk` if either needs changing → `wdi-component` → **G4** → `wdi-build` → **G5** |
| That component is at `mode: catalog` | straight to `wdi-build`. G4 is skipped |
| A promise changes where a PRD already exists | `wdi-product` intent `update` — never a second PRD for the same area |
| A new initiative with a different reader | `wdi-product` intent `prd` → `wdi-init` intent `component` if it births components |
| A small fix touching no `FR`, `UC`, `AD-N`, or domain model | Fast Path: `bmad-build` directly. It **stops and becomes a wave `S`** the moment an `FR` is touched |
| A bug, a failing test, unexpected behaviour | `wdi-systematic-debugging`, **before** any fix is proposed |
| A planning assumption turned out void | `wdi-decision` — it wraps `bmad-correct-course`, proposes, and changes nothing itself |
| An estimate or a task list is needed | `wdi-report` intent `estimate` |
| You do not know where you are | `wdi-help` |

## Fifteen skills

Named for the **gate they serve**, so *"which skill do I run"* is answered by *"which gate am I at"*.

**Moment-bound** — running them outside their point is wrong:

| Skill | Its moment |
|---|---|
| `wdi-init` intent `setup` | before G1, once per project |
| `wdi-problem` | G1 |
| `wdi-product` | G2 |
| `wdi-init` intent `component` | tail of G2, and whenever a new PRD births a component |
| `wdi-blueprint` | G3 |
| `wdi-component` | G4 |
| `wdi-build` | G5, one wave per run |

**Anytime** — run the moment the trigger appears, without waiting for a gate:

| Skill | Its trigger |
|---|---|
| `wdi-decision` | A decision worth remembering · a void assumption · an accepted decision to carry into documents |
| `wdi-question` | Something that cannot be decided now |
| `wdi-log` | A meeting finished, or a non-technical fact now binds |
| `wdi-help` | "Where am I, what next" |
| `wdi-reconcile` | Any time. Read-only — it reports, it never edits |
| `wdi-review` | Over any document, any time |
| `wdi-systematic-debugging` | A bug, a failed test, a failed build, unexpected behaviour |
| `wdi-report` | An estimate at the start · progress periodically · before a client update |
| `wdi-init` intents `mode` · `risk` · `structure` | Any time |
| `wdi-ux` | Any time after a PRD exists, if UX is being used |

## Who writes what — WDI and BMad

| Artifact | Written by | Wrapped in |
|---|---|---|
| Product brief | `bmad-product-brief` | `wdi-problem` |
| PRD | `bmad-prd` | `wdi-product` |
| UX | `bmad-ux` | `wdi-ux` |
| Spine + C4 | `bmad-architecture` | `wdi-blueprint` |
| **UC catalogue · actors · entities · business rules** | **nothing in BMad** | `wdi-blueprint` writes it itself |
| **SRS and all of `.what/<pc>/`** | **nothing in BMad** | `wdi-component` writes it itself |
| **SDD and all of `.how/<pc>/`** | **nothing in BMad** | `wdi-component` writes it itself |
| `SPEC.md` + stories | `bmad-spec` | `wdi-build` |
| Code | `bmad-build` · `bmad-build-auto` | `wdi-build` |
| Retrospective | `bmad-retrospective` | `wdi-build` |
| Document review | `bmad-review` | `wdi-review` |
| Course correction | `bmad-correct-course` | `wdi-decision` |

**The bold rows are why this method exists.** BMad stops at the promise and starts again at the mechanism,
and every behaviour in between had no author. Three consequences stick to those artifacts and are handled
deliberately: no `doc_standards` fires a review, no memlog is born on its own, and no template enforces
itself.

## Where things live

| The thing in your hand | Its folder |
|---|---|
| How we work — a rule, a guide, a template | `.constitution/` |
| What currently holds — a decision, a question, a registry, a map | `.control/` |
| What is promised — the brief, a PRD, a use case, a business rule | `.what/` |
| How it is built — the spine, C4, an inventory, an SDD, a contract | `.how/` |
| A skill run's working output | `_bmad-output/` |
| Scratch that empties when the task closes | `.work/` |
| The application | `src/` · `web/` |

The test that settles anything ambiguous: **is this file still correct after its wave has passed?** Yes →
the corpus. No → `_bmad-output/`. In doubt, `../document/corpus-guide.md`.

## Model choice

| Point | Model |
|---|---|
| Decisions — proposing a slicing, wording a `DEC-`, preparing a gate | `opus@high` |
| Writing, derivation, a review-fix pass | `sonnet@high` |
| Code review panel | Reviewers dispatched separately from the builder — the local Agent Rules govern CLI/model pairing |

In a derivation pass, quality comes from the input rather than the model. Running a "find the gap" lens with
the most careful model produces the most gaps, and each one becomes an open question — a cost nobody sees
until the question list has stopped being readable.
