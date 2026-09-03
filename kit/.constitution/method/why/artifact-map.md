---
status: Reference
---

# Artifact Map — what exists, where, and who owns it

**Opened when:** someone asks *"where does this file go"*, or *"does this document exist at my `mode`"*.

This file **explains**. It does not bind — `../document/*-guide.md` does, and where the two disagree the guide
wins and the disagreement is a defect to report.

It answers three questions and nothing else: which files exist at each `mode`, who owns each one, and how
the units of work line up. The **rules** about depth live in `../document/delivery-flow-guide.md`; what is
here is the map. What `mode` and `risk_accepted` do **together**, cell by cell, is in `mode-risk-map.md`.

## The one thing to read first

Nine things exist at **every** `mode`, including `catalog`, because they belong to the blueprint at G3 and
the depth knob does not reach the blueprint:

> the use case list · the API list · the table list with its key columns · the screen list · the domain
> model · the actor list · the spine `AD-N` · C4 L1 + L2 + L3 · cross-component business rules

That is why nobody needs a fifth mode. The request behind wanting one is almost always *"I need at minimum
the use cases, the API, and the database"* — and all three are already in `catalog`.

## What each mode gives you, cumulatively

| `mode` | What you hold |
|---|---|
| `catalog` | The nine above. **Zero extra files per component** |
| `outline` | + `Decision Summary` · the `LC` list per component · full flows for at most 3 use cases · local business rules |
| `guarded` | + `Failure Behaviour` for every boundary · `Inherited Constraints` · third-party integration documents · boundary `LC` registered |
| `deep` | + ABCE robustness analysis · five-lane contract spec per endpoint · data dictionary per column · flow diagrams · state machines · branch scenarios · every `critical` use case gets a full flow |

Marks used below: **always** = present at all four modes, born at G1, G2, or G3 · ✓ = written at that mode
· skeleton = the file exists carrying headings and frontmatter · — = not written at all.

## `.what/`

| File | Holds | Born | `catalog` | `outline` | `guarded` | `deep` |
|---|---|---|---|---|---|---|
| `_product-brief/brief.md` | Problem, users, measure of success, non-goals | G1 | always | always | always | always |
| `_product-brief/addendum.md` | Depth that does not fit the brief's narrative | G1 | always | always | always | always |
| `_prd/<initiative>/prd.md` | `CAP` · `FR` · `NFR` · `UJ` · one proof of done per `FR` | G2 | always | always | always | always |
| `_prd/<initiative>/addendum.md` | Rejected alternatives, option matrices, sizing | G2 | always | always | always | always |
| `<pc>/04-usecases/EXPERIENCE.md` | The user-facing journey | G2, optional | optional | optional | optional | optional |
| `business-rules.md` | `BR-N` binding more than one component | G3 | always | always | always | always |
| **`<pc>/SRS-<pc>.md`** | § Actor Register · **§ UC Catalogue — this is the use case list** · Constraints · Non-Goals · Prerequisite · Assumptions/Risks/TBC | G3 | **always** | always | always | always |
| `<pc>/03-domain/domain-model.md` | Entities · relations · columns | G3 | always | always | always | always |
| `<pc>/02-rules/rules-<pc>.md` | Rules binding only this component | G4 | — | ✓ | ✓ | ✓ |
| `<pc>/04-usecases/UC-<n>-<slug>.md` | One full flow, at most eight steps | G4 | — | max **3** | max **3** | every `critical` UC |
| `<pc>/03-domain/state-machines.md` | The lifecycle of each multi-state entity | G4 | — | — | — | ✓ |
| `<pc>/05-scenarios/SCN-<nn>-<slug>.md` | A branch that does not fit its use case file | G4 | — | — | — | ✓ |

**So `SRS-<pc>.md` exists at `mode: catalog`.** It carries the actor list and the use case catalogue. What
is absent there is the `UC-<n>-<slug>.md` files — the step-by-step flows.

Repealed: `<pc>/01-requirements/` (permanently empty; `FR` live in the PRD and the SRS cites them) and
`<pc>/supplements/` (existed for `ANX-`).

## `.how/`

| File | Holds | Born | `catalog` | `outline` | `guarded` | `deep` |
|---|---|---|---|---|---|---|
| `_platform/ARCHITECTURE-SPINE.md` | `AD-N` — Binds · Prevents · Rule. Invariants only | G3 | always | always | always | always |
| `_platform/c4-l1-system-context.md` | System, outside actors, outside systems | G3 | always | always | always | always |
| `_platform/c4-l2-containers.md` | Containers, their technology, their relations, and the PC × container matrix. **Owns the container list** | G3 | always | always | always | always |
| `_platform/c4-l3-<container>.md` | One file per `built: true` container holding more than one Product Component | G3 | always | always | always | always |
| **`_platform/inventory-db.md`** | **Table list**: `No` · table · owning component · what it holds · **key columns** | G3 | **always** | always | always | always |
| **`_platform/inventory-api.md`** | **Endpoint list**: `No` · method · path · owning component · description · status | G3 | **always** | always | always | always |
| **`_platform/inventory-screen.md`** | **Screen list**: `No` · screen · route · owning component · actor · `UC` served | G3 | **always** | always | always | always |
| `_platform/cross-cutting.md` | One error envelope for the whole product, and the rest of what is shared | G3 | always | always | always | always |
| `_platform/design-system.md` | Tokens and base elements | G2, optional | optional | optional | optional | optional |
| `<pc>/SDD-<pc>.md` § Decision Summary | What this component is built as, and the costliest choices reversed | G4 | skeleton | ✓ | ✓ | ✓ |
| `<pc>/SDD-<pc>.md` § Structure | The `LC` list and their dependency direction | G4 | skeleton | ✓ | ✓ | ✓ |
| `<pc>/SDD-<pc>.md` § Inherited Constraints | The `AD-N` binding this component, quoted not paraphrased | G4 | — | — | ✓ | ✓ |
| **`<pc>/SDD-<pc>.md` § Failure Behaviour** | Per boundary: the other side slow, absent, or lying | G4 | — | — | **✓ every boundary** | ✓ |
| `<pc>/SDD-<pc>.md` § Robustness Analysis | ABCE per `critical` use case | G4 | — | — | — | ✓ |
| `<pc>/03-integrations/<name>.md` | A third party: who owns it, and what happens when they change it | G4 | — | — | ✓ if any | ✓ |
| `<pc>/02-contracts/00-inventory.md` | This component's endpoints, stably numbered | G4 | — | — | — | ✓ |
| `<pc>/02-contracts/<nn>-<resource>.md` | One endpoint, five lanes: auth · validation · error · rate limit · idempotency | G4 | — | — | — | ✓ |
| `<pc>/04-components/<name>.md` | Services and jobs | G4 | — | — | — | ✓ |
| `<pc>/05-model/data-model.md` | Component ERD + **data dictionary per column** | G4 | — | — | — | ✓ |
| `<pc>/06-flows/<nn>-<flow>.md` | Sequence diagram, only for money, irreversible state, or a third party | G4 | — | — | — | ✓ |
| `<pc>/01-ux/<screen>.md` | Screens and composites, **field detail per form** | G4 | — | — | — | ✓, or earlier via `wdi-ux` |

Repealed: `_platform/architecture/` (one file does not earn a folder) and `<pc>/supplements/`.

## Registry and derived files

| File | Holds | Present at |
|---|---|---|
| `.control/registry/goals.yaml` | `BG` | every mode |
| `.control/registry/requirements-<slug>.yaml` | `CAP` · `FR` · `NFR` · `UJ`, one file per PRD initiative | every mode |
| `.control/registry/usecases.yaml` | `UC-N` with `critical` and the `FR` it satisfies | every mode |
| `.control/registry/components.yaml` → `product_components` | Component · `mode` · `risk_accepted` · `risk_note` · `owns` · `g4_passed` | every mode |
| `.control/registry/components.yaml` → `containers` | The containers from C4 L2 | every mode |
| `.control/registry/components.yaml` → `platform_owns` | Entities no Product Component's promise explains. `_platform` is not a component and has no `mode` | every mode |
| `.control/registry/components.yaml` → `logical_components` | `LC` | boundary from `guarded`; boundary + control at `deep` |
| `.control/registry/decisions.yaml` · `specs.yaml` · `defects.yaml` · `risks.yaml` · `index.yaml` | Decisions · work · defects · risks · the global `mode` and gate map | every mode |
| `.how-rendered/blueprint.md` | **The one-page roll-up reviewed at G3** | every mode |
| `.control/generated/decisions.md` | The flat index of every `DEC-` | every mode |
| `.control/generated/estimate.md` | The candidate task table | every mode |
| `.control/generated/rtm` · `status` · `dag` · `components` · `risks` | Traceability and progress | every mode |

## Who owns each file

A skill lands the output of the layer it owns, and landing is part of producing it — never a follow-up
someone else performs. `../document/corpus-guide.md` holds the binding version of this table.

| Owner | Writes |
|---|---|
| `wdi-init` | The registry scaffold, `mode`, `risk_accepted`, component birth, the `SRS`/`SDD` skeletons, the two structure maps |
| `wdi-problem` | `.what/_product-brief/` |
| `wdi-product` | `.what/_prd/<initiative>/` |
| `wdi-blueprint` | `.what/<pc>/` § Actor Register + § UC Catalogue + `03-domain/domain-model.md` · `.what/business-rules.md` · `.control/product-glossary.md` · all of `.how/_platform/` except `design-system.md` |
| `wdi-component` | `.what/<pc>/` slots `02`–`05` · `.how/<pc>/` except `01-ux/` |
| `wdi-ux` | `EXPERIENCE.md` · `.how/<pc>/01-ux/` · `.how/_platform/design-system.md` |
| `wdi-build` | `specs.yaml` · `_bmad-output/specs/` · `src/` · `web/` |
| `wdi-decision` | `.control/decisions/` · `decisions.yaml`, and at apply time whatever `touches` names — through each file's owner |
| `wdi-question` | `.control/questions/` |
| `wdi-log` | `.control/meetings/` · `.control/project-non-technical-log.md` |
| `wdi-report` | `.control/reports/<period>.md` |
| a script | everything in `.control/generated/`, and the three inventories once code exists |

Five skills write **no file at all**, and that is deliberate: `wdi-reconcile`, `wdi-help`, `wdi-explain-to-me`,
`wdi-report` intent `dispatch`, and `wdi-review` apart from one frontmatter block. What reports MUST NOT
also change things — otherwise there is nothing left to check with.

## How the units of work line up

`FR` is a **promise** and permanent; a spec is a **unit of work** and temporary; `SPEC.md` is the machine
contract for one spec — written from size `M` up, and at `S` the tickets are the contract; a ticket is one
vertical slice one builder takes to a green PR.

One spec = one parent issue, and a ticket is an **issue**, not a sub-task, because its blocking edges are
what make the frontier visible in the tracker's own UI. **`FR` is not an issue** — it travels as a label,
because one `FR` can be delivered by tickets in two specs and one ticket can satisfy part of two `FR`.

The binding version of all of this, including why a spec MAY cross components and what has to be true
first, is in `../document/delivery-flow-guide.md`. It is not restated here.

## What needs no template, and why

Stated so the next completeness audit does not report it again:

| File | Why it has no template |
|---|---|
| `.control/generated/*` | Script output. Its shape is code, not a template |
| `.control/reports/<period>.md` | Rendered by `timeline.py` |
| `.control/project-non-technical-log.md` | States its own entry shape in its own header, and there is exactly one such file |
| `SPEC.md` · ticket files | Their shape belongs to `to-spec` and `to-tickets`. WDI owns where they land, not how they read |
| Registry `*.yaml` | Their shape is the comment block at the head of each file, plus the validator |

Everything else in this map has a template in `../document/templates/` — 26 of them, and every row above is
covered by one.
