---
status: Reference
---

# Mode × Risk Map — what the two settings do together

**Opened when:** a `mode` and a `risk_accepted` have been picked for a component and someone asks
*"so what actually changes?"* — or the same question before picking.

This file **explains**. It does not bind — `../document/*-guide.md` does, and where the two disagree the
guide wins and the disagreement is a defect to report.

`../document/delivery-flow-guide.md` defines each field. `artifact-map.md` lists which files exist at each
`mode`. Neither shows the two fields **side by side**, and that is the only gap this file fills.

## This is not a decision matrix

All twelve combinations are legal, and eleven of them need no justification at all. Reading a column MUST
NOT be used to derive `mode` from `risk_accepted`, or the reverse: the whole reason they are two fields is
that documents and reviews are two different mitigations, and a component MAY be **thin on purpose and
reviewed the hardest**. `rationale.md` holds why.

What the table below gives is **consequence**, not recommendation. Two things in it are not free, and both
are named in the guide, not here: `risk_accepted: high` on a component whose `risk_note` names money,
personal data, an irreversible action, a contractual promise, or an un-rollbackable integration needs a
named acceptance in `risk_accepted_by` (`high-risk-named`) — and an outside party who will demand the artifacts as a
deliverable puts the touched component at `mode: deep` **and** `risk_accepted: low`, which is the one cell
the method assigns rather than offers.

## Axis 1 — what moves when only `mode` moves

Cumulative; each row contains the one above. Full per-file manifest in `artifact-map.md`.

| `mode` | Beyond the blueprint, per component | G4 | `critical` |
|---|---|---|---|
| `catalog` | nothing — zero extra files. The SDD stays a skeleton | **skipped entirely** | decides nothing |
| `outline` | `Decision Summary` · the `LC` list · full flow for at most 3 use cases · local business rules | 20' | decides nothing |
| `guarded` | + `Failure Behaviour` for every boundary · `Inherited Constraints` · third-party integration documents · boundary `LC` registered | 20' | decides nothing |
| `deep` | + ABCE robustness analysis · contract spec per endpoint · data dictionary · flow diagrams · state machines · branch scenarios | 30' | **every `critical` UC gets a full flow** |

Untouched at every `mode`: the use case list, the API list, the table list, the screen list, the domain
model, the actor list, the spine, C4 L1–L3, and cross-component business rules. All nine are blueprint
content, born at G3, which the depth knob does not reach.

## Axis 2 — what moves when only `risk_accepted` moves

| `risk_accepted` | Lenses on the documents | On the code | `review-trace` trace on the component's docs |
|---|---|---|---|
| `low` | structure · prose · **edge-case-hunter** | a **two-reviewer panel is required** | demanded |
| `medium` | structure · prose · **edge-case-hunter** | — | demanded |
| `high` | structure · prose | — | not demanded — the risk is already accepted on the record |

**The contract sits outside that last column entirely**, and it is the one artifact this field never
reaches: it always carries `edge-case-hunter`, and `review-trace` always demands `spec_reviewed` on every spec that
carries tickets — `high` included. A spec is not a component, so `risk_accepted` has no say over it. It is
what a builder works from, and a branch missed there surfaces as a bug at G5.

One trace covers the whole spec, never one per ticket. Where `SPEC.md` exists the trace covers it; at size
`S` there is none, and the trace covers the **ticket set as one artifact**.

## The twelve cells

`g4` = the G4 session · `panel` = the two-reviewer code panel · `review-trace` targets assume the file is born.

| `mode` + `risk_accepted` | Owner time at G4 | Document review | Code | Component trace on | Also |
|---|---|---|---|---|---|
| `catalog` + `low` | none — skipped | structure · prose · edge-case-hunter | **panel** | `SRS` only | The cell the split exists for: thin on purpose, reviewed hardest |
| `catalog` + `medium` | none — skipped | structure · prose · edge-case-hunter | — | `SRS` only | The cheapest cell that still hunts edge cases |
| `catalog` + `high` | none — skipped | structure · prose | — | nothing | Nothing in the flow asks what is being staked — only `wdi-init`'s disclosure and `high-risk-named` do |
| `outline` + `low` | 20' | structure · prose · edge-case-hunter | **panel** | `SRS` · `SDD` after G4 | Flows for 3 use cases, checked hard |
| `outline` + `medium` | 20' | structure · prose · edge-case-hunter | — | `SRS` · `SDD` after G4 | — |
| `outline` + `high` | 20' | structure · prose | — | nothing | Flows exist; no lens looks for the branch they miss |
| `guarded` + `low` | 20' | structure · prose · edge-case-hunter | **panel** | `SRS` · `SDD` after G4 | Boundary answers written **and** hunted. The heaviest cell short of `deep` |
| `guarded` + `medium` | 20' | structure · prose · edge-case-hunter | — | `SRS` · `SDD` after G4 | — |
| `guarded` + `high` | 20' | structure · prose | — | nothing | Failure behaviour is written and taken at its word |
| `deep` + `low` | 30' | structure · prose · edge-case-hunter | **panel** | `SRS` · `SDD` after G4 | The floor an outside deliverable is put at. Not a preference there |
| `deep` + `medium` | 30' | structure · prose · edge-case-hunter | — | `SRS` · `SDD` after G4 | — |
| `deep` + `high` | 30' | structure · prose | — | nothing | Depth bought, scrutiny declined. Legal, and worth saying out loud once |

**The trace column is scoped to a component's own documents.** The spec's own trace is left out of it
because it is demanded in **every** cell: `review-trace` asks for `spec_reviewed` carrying `edge-case-hunter` on every
spec with tickets, whatever `risk_accepted` says. Reading a `nothing` in that column as *"no trace is
demanded anywhere in this cell"* is the one misreading it invites, and it is wrong.

## Before the components exist — G1 and G2

The question this section exists to answer: *"at G1 and G2, is every combination treated the same?"*

For `risk_accepted`, yes — and not as a policy choice. **The field has no value yet.** It is born per
component when `wdi-init` intent `component` runs at the **tail of G2**, so nothing before that point can read
it. One consequence worth knowing: the brief and the PRD are artifacts with no component, so their review is
`structure · prose` whatever any component is later set to, and no `reviewed:` trace is written on them at all.

For `mode`, almost — and the exception is real:

| At G1 and G2 | Identical at every setting? |
|---|---|
| What the gate decides, its budget (20' · 45'), how often it runs | **yes** |
| The artifacts: `brief.md` · `_product-brief/addendum.md` · `prd.md` · `_prd/<initiative>/addendum.md` | **yes** — `always` at all four modes |
| Checklist length | **no** — at `catalog` G1 asks 2 of 7 and G2 asks 3 of 7 |

Only the **global** `mode` can be in play there; the per-component one does not exist yet. And among the G2
questions that stop being required at `catalog` is *"which `FR` touch money, personal data, or the client's
reputation?"* — which does not open a hole: `wdi-init` intents `mode` and `risk` MUST read the `FR` falling to
the component and name what is touched before proposing any value. The disclosure moves, it does not vanish.

## Where the two fields actually meet

Four points, and they are the whole reason this file exists. Everywhere else the fields are independent
and each row above is just its axis restated.

1. **The `SDD` review trace is the one demand that reads both fields.** `review-trace` demands it only when
   `risk_accepted` is `low` or `medium` **and** `mode` is above `catalog` **and** `g4_passed` is set. At
   `catalog` the SDD skeleton is its **finished** form, and a trace on thirteen lines of template comments
   is theater.
2. **The `SRS` trace reads only risk.** It is demanded at every `mode`, `catalog` included, because the
   SRS carries the Actor Register and the UC Catalogue — G3 content, born whatever the depth.
3. **The spine's trace is product-wide.** One component at `low` or `medium` anywhere puts
   `ARCHITECTURE-SPINE.md` under `review-trace`, however the other components are set.
4. **`catalog` removes the gate where risk is spoken about.** G4's first ★ question is *"what is being
   staked in this component — and does `risk_accepted` say so out loud?"* At `catalog` that session does
   not happen, so the disclosure at `wdi-init` intent `risk` and the `risk_note` it writes are the only
   place the answer is recorded. That is a consequence, not an argument for raising `mode`: the same
   answer costs one line in `risk_note` and does not need a document to hold it.

Two more mechanics, neither of which reads `risk_accepted`:

- **`spec-after-g4`** — from `outline` up, a spec MUST NOT touch a component whose `g4_passed` is unset. At `catalog`
  the check passes by design, because there is no G4 to pass.
- **G4's second ★ question** — *"which boundary still has no answer for the other side being slow, absent,
  or lying"* — is asked from `guarded` up. It is the question `guarded` exists to buy.

## Changing a cell later

| Move | Costs | Note |
|---|---|---|
| Raising or lowering `mode` | nothing. No justification | Lowering **deletes nothing** — a written file stops being required, and that is all |
| Raising `mode` on a component whose code already runs | the evidence labels in `sdd-guide.md` | What comes out is an **as-built record**, not a design |
| Lowering `risk_accepted` toward `low` | a review that now has to actually run | A stale trace MUST be re-earned, never re-dated — except for a wording-only change, which `wdi-review` lets you re-stamp |
| Raising `risk_accepted` to `high` on a sensitive component | a person and a date in `risk_accepted_by` | `high-risk-named` checks somebody is named, and it discloses rather than vetoes |
