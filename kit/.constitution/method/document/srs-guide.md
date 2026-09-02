---
status: Accepted
---

# SRS Guide

**Loaded when:** writing, changing, or validating the SRS of a Product Component

An SRS states how the system must **behave** for one Product Component. The PRD promised something to a
user; this says what the system does so that promise holds. It MUST NOT say how the thing is built —
that is `SDD-<pc>.md`.

## Two skills write it, at two gates

| Section | Written at | By |
|---|---|---|
| § Actor Register · § UC Catalogue | G3 Blueprint | `wdi-blueprint` intent `catalog` |
| Everything below, per the component's `mode` | G4 Component | `wdi-component` intent `behaviour` |

**The SRS therefore exists at `mode: catalog`.** It carries the actor list and the use case catalogue,
because both are born at G3 and `mode` does not touch the blueprint. What does not exist at `catalog` is
`04-usecases/UC-<n>-<slug>.md` — the step-by-step flow. Reading "no SRS at `catalog`" is wrong, and it
was an artefact of an earlier table that showed only what varies.

Depth is **read from `mode`**, never computed. Review lenses are **read from `risk_accepted`**, never from
`mode`. Both fields are defined in `delivery-flow-guide.md` and MUST NOT be redefined here.

## No BMad skill writes this

`bmad-prd` writes the PRD, `bmad-architecture` writes the spine, `to-spec` writes the contract. Nothing in BMad
writes an SRS. Three consequences follow, and each MUST be handled deliberately:

| Consequence | What follows |
|---|---|
| No `doc_standards` can fire | `bmad-review` MUST be invoked through `wdi-review`, with the lens set `risk_accepted` names |
| No memlog is created | A decision taken while writing MUST land as a `DEC-` through `wdi-decision`, not as a parenthetical |
| No template enforcement | The shape comes from `templates/srs.md`, applied by `wdi-init` intent `component` at birth |

`bmad-advanced-elicitation` and `bmad-party-mode` MAY be used as thinking aids. They produce no artifact
and MUST NOT be treated as authors.

## Home and life cycle

- `.what/<pc>/SRS-<pc>.md`, with slots `02-rules/` · `03-domain/` · `04-usecases/` · `05-scenarios/`.
- **Living, amended forever.** An SRS MUST NOT be versioned, frozen, or superseded. A component does not
  stop existing because a release shipped.
- `01-requirements/` and `supplements/` are **repealed**. The first was permanently empty — `FR` live in
  the PRD and the SRS cites them. The second existed for `ANX-`, and that concept is gone.

## Writing order

Binding, and each step is the input to the next. The first four happen at G3, the rest at G4:

1. **Glossary** — every domain noun this component uses, into `.control/product-glossary.md`. Never
   defined inline here.
2. **UC Catalogue** — one line per use case: `UC-N` · title · actor · the `FR` it satisfies · `critical`
   yes/no.
3. **Actor Register**.
4. **Domain Model** — entities, relations, columns. A business rule binding a second component goes to
   `.what/business-rules.md`.
5. **UC Specification** — full flows, per `mode`.
6. **Local business rules**, then **State Lifecycle**, then **branch scenarios** — per `mode`.

Writing these out of order produces use cases whose nouns nobody defined. When the pass covers several
components, the order binds **within** each one, not across them.

## Which use cases get a full flow

| `mode` | Full flows |
|---|---|
| `catalog` | none — the catalogue line is the whole record |
| `outline` · `guarded` | the use cases the component exists for, **at most 3** |
| `deep` | every `critical` use case |

A use case is `critical` when it touches **money, personal data, or an irreversible action**. That is the
whole definition; `delivery-flow-guide.md` owns it, including the one-third sanity check.

## Use cases at two altitudes

The same `UC-N` MAY appear twice in the corpus, and the two MUST NOT be merged or made to duplicate each
other:

| | Here, in the SRS | There, in the SDD at `deep` |
|---|---|---|
| Written for | Someone who uses the product | Someone who builds it |
| Basic Flow | **At most eight steps** | As long as the design needs |
| May name | Actors, screens the user sees, domain nouns | Classes, endpoints, tables, transports |
| Answers | What happens | How it happens |

The eight-step cap is not style. A flow needing more steps is either two use cases, or it has started
describing implementation — and the cap makes that visible while it is still cheap to fix.

Branches MUST go to `05-scenarios/` rather than making the UC file fat, and only at `deep`.

## Actor Register is the SSOT

It MUST stay in the SRS kernel, never moved to a slot. The SDD MUST NOT carry a copy of it — a mirror was
once permitted with the rule "not edited on the SDD side", and nothing checked that rule. The rendered SDD
shows the actors it needs from here. A `System` actor MAY be decomposed into the internal components that
play it, but that decomposition belongs to the SDD, and it cites the actor, never restates it.

## Business rules — two homes, one test

| Rule | Home | Born at |
|---|---|---|
| Binds more than one Product Component | `.what/business-rules.md` | G3 |
| Binds only this component | `.what/<pc>/02-rules/rules-<pc>.md` | G4, from `outline` up |

The test is not importance, it is **reach**. A rule written in one component that turns out to bind a
second MUST be promoted, not copied. Two copies of one rule is how components start disagreeing about the
same policy.

## Sections the shape requires

`templates/srs.md` carries the full list. Four MUST NOT be dropped even when they feel thin, because each
is the one that is silently skipped:

| Section | Why it MUST stay |
|---|---|
| **Constraints** | Inherited from the spine's `AD-N` and from the PRD. A constraint discovered at G4 costs a decision |
| **Non-Goals** | What this component explicitly does not do. Absent, it will be assumed to do it |
| **Prerequisite** | What MUST already exist before this component can behave as described |
| **Assumptions, Risks, and To Be Confirmed** | Three separate lists. An assumption is something we decided to believe; a risk may go wrong; a to-be-confirmed is a question with an owner. Collapsing them loses the owner |

Every unresolved to-be-confirmed MUST be filed through `wdi-question` before G3 opens — into
`assumptions.md` by default, and into `blocking.md` only through the three tests that file states.

## The boundary against solution shape

Solution shape MUST NOT appear here. Concretely, the SRS MUST NOT name a framework, a database table, an
HTTP endpoint, a class, a queue, or a file path. Robustness analysis belongs to the SDD, at `deep`.

When writing behaviour surfaces a design decision that cannot wait, it goes to `wdi-decision` — not into
this document as a parenthetical.

The reverse also holds. When G4 or the build discovers behaviour nobody specified, it MUST come back here
**before** the code that implements it; the change-control matrix in `delivery-flow-guide.md` says which
artifacts move.

## Passing the gate

- At **G3**: the actor list, the UC catalogue, and the domain model complete for every component, and the
  roll-up in `.how-rendered/blueprint.md` regenerated. `goal-has-fr`, `fr-has-uc`, `refs-resolve`, and `chain-links` green — `fr-has-uc` is the ★
  question: every `FR` has at least one `UC`, unless it carries `no_uc:` with a stated reason.
- At **G4**: whatever this component's `mode` requires, and nothing beyond it.
- `wdi-review` MUST have run with the lens set `risk_accepted` names for a **first** review or a review
  opening this gate; a later re-review runs the lighter set, and `wdi-review` owns when. The `reviewed:`
  trace is stamped only on components at `risk_accepted` `low` or `medium` — `review-trace`, where absence fails and
  staleness is advisory between gates.
- A `UC` that exists but is wrong passes `fr-has-uc` and fails `wdi-reconcile`. Run it before the gate, not after.
