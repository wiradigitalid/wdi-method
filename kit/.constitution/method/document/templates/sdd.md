---
type: sdd
component: '{pc}'
status: draft            # draft · reviewed · locked · superseded
created: '{YYYY-MM-DD}'
updated: '{YYYY-MM-DD}'
realizes: []             # UC ids this design realizes, from usecases.yaml
binds: []                # AD ids from the spine that bind here
reviewed:                # V13. Filled only after wdi-review has actually run
  date: ''               # '{YYYY-MM-DD}'
  sha: ''                # commit it was reviewed at; without the SHA, staleness cannot be measured
  lenses: []             # the set risk_accepted names — NOT a fixed list
---

# SDD — {Product Component}

<!-- TEMPLATE GUIDE — act on these comments, then delete them. Never emit a comment in a finished
     SDD. Headings stay English; prose is Bahasa Indonesia with technical terms left in English. -->

<!-- NOT an HLD, and NOT a one-shot LLD. What the system consists of belongs to C4 L1-L2; architecture
     constraints belong to ARCHITECTURE-SPINE.md; deployment topology belongs to the devops repository.
     This document is LIVING: one per Product Component, amended every wave. -->

<!-- EVERY SECTION MARKS THE MINIMUM `mode` THAT DEMANDS IT. Below that minimum it MUST NOT be written
     to fill a slot; above it, it is required. Read the component's mode from its row in
     components.yaml, falling back to `mode:` in index.yaml.

     At mode: catalog this file is a SKELETON — this frontmatter and these headings, and nothing else.
     That is a FINISHED state, not an unfinished one: G4 is skipped at catalog, and the code is written
     from the use case catalogue, the three inventories, and C4.

     `reviewed.lenses` MUST match what risk_accepted names, NOT what `mode` says. One component MAY sit
     at catalog and still be reviewed the hardest. -->

## Decision Summary · [outline]

<!-- <=1 page, business language. What this component is built as, and the one or two choices that cost
     the most to reverse. This is what the Product Owner reads at G4. -->

## Structure · [outline]

<!-- The Logical Components and how they depend on each other. Carry the dependency direction — it IS a
     rule, not decoration.

     Every LC named here MUST be registered in .control/registry/components.yaml, and the registration
     is checked WHEN THE WAVE CLOSES — V12 — not before a story is ready-for-dev. The old timing
     demanded the answer at the moment the information was thinnest. -->

| LC | type | Responsibility |
| --- | --- | --- |

## Inherited Constraints · [guarded]

<!-- Every AD-N from ARCHITECTURE-SPINE.md that reaches this component, QUOTED VERBATIM under its
     ORIGINAL id. A paraphrase drifts, and the drift is invisible because both texts read reasonably.

     A local choice contradicting one is a conflict to surface through wdi-decision, never an override
     made here. Below `guarded` this section is absent and the AD-N still binds — an invariant does not
     stop holding because a document is thin. -->

| AD | Quoted rule | How it lands here |
| --- | --- | --- |

## Failure Behaviour · [guarded]

<!-- PER BOUNDARY, and every boundary. This section STANDS WITHOUT the ABCE pass below, and that is
     what makes `guarded` worth having: the boundary list already exists in
     .how/_platform/inventory-api.md and inventory-screen.md, each with an owning-component column.
     Do not derive it again.

     For each: what happens when the thing on the other side is slow, absent, or lying. "Returns an
     error" is not an answer. G4 asks this as a starred question from guarded up.

     A failure mode that turns out to be a PROMISE — a refund path, a partial save — goes to the SRS
     first, and becomes a scenario on the .what side. -->

| Boundary | Slow | Absent | Lying | What the user sees | What is logged |
| --- | --- | --- | --- | --- | --- |

## Robustness Analysis · [deep]

<!-- The ABCE pass, in order: Boundary -> Control -> Entity -> Behaviour. For every UC marked
     `critical` in the paired SRS.

     It MUST NOT have appeared in the SRS, and below `deep` it MUST NOT be written at all. Failure
     Behaviour above does not need it. -->

## Design Notes

<!-- Only what a builder cannot read off compliant code. Rationale lives in the memlog and in DEC-;
     restating it here creates a second version that drifts. Cut this section when it is empty. -->

## Evidence

<!-- Required whenever this document describes code that ALREADY EXISTS — brownfield, and equally when
     a component's `mode` was raised after its code was running. What is written then is an AS-BUILT
     RECORD, not a design.

     Every technical claim MUST name the file that proves it. Four labels, and they are mandatory:
       [ASSUMED]              we decided to believe it; nothing was read that confirms it
       [PARTIAL]             verified for part of the surface — and it MUST say which part is not
       [NEEDS CONFIRMATION]  a question with an owner, filed through wdi-question
       [MISSING]           checked, and the thing described is NOT there

     An unlabelled claim is read as verified. A claim MUST NOT be raised because it survived several
     readings — familiarity is not evidence.

     [MISSING] MUST NOT be deleted. It is the only surviving evidence that somebody once believed the
     thing existed. Each is dispositioned as a BUG-, a correction, or planned work, and an unresolved
     one MUST NOT pass G4. -->

| Claim | Label | Read to decide | Disposition |
| --- | --- | --- | --- |

---

## Slots

<!-- The numbers are ABCE CLASSIFICATION — Boundary, Control, Entity, behaviour — NOT reading order.
     This is the opposite of .what/<pc>/. The two MUST NOT be conflated.

     Content SHOULD stay in this kernel until the file grows past roughly 400 lines — a suggestion, not
     a threshold.

     01-ux/            [deep], or earlier through wdi-ux. Screens and composites; LC types ui-screen,
                       ui-composite. This slot belongs to wdi-ux, not to wdi-component.
                       Base tokens and elements do NOT land here — .how/_platform/design-system.md
     02-contracts/     [deep]. 00-inventory.md FIRST, then one spec per endpoint carrying its stable
                       number. Every spec answers all five lanes — auth, validation, error, rate
                       limiting, idempotency — with `none` and a reason where one does not apply.
                       Error responses reference the envelope in _platform/cross-cutting.md, never
                       restate it. LC type gateway
     03-integrations/  [guarded], when the component consumes a third party. From templates/
                       integration.md. LC type gateway
     04-components/    [deep]. Services and jobs. LC types service, job
     05-model/         [deep]. Schema and storage, INCLUDING the data dictionary per column — a diagram
                       alone does not say what a column means. LC type store
     06-flows/         [deep]. Sequence diagrams ONLY for flows involving money, irreversible state, or
                       a third party. Lane order is fixed once for the project in
                       ../../../project/codebase-conventions-guide.md; the No-op lane rule is REPEALED

     supplements/ is REPEALED along with the ANX- concept it existed for. -->

## Open Items

<!-- Unresolved design questions, each pointing at its row in .control/questions/. -->
