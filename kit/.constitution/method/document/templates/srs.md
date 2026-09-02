---
type: srs
component: '{pc}'
status: draft            # draft · reviewed · locked · superseded
created: '{YYYY-MM-DD}'
satisfies: []            # FR / NFR ids this component carries, from requirements-<slug>.yaml
reviewed:                # `review-trace`. Filled only after wdi-review has actually run
  date: ''               # '{YYYY-MM-DD}'
  sha: ''                # commit it was reviewed at; without the SHA, staleness cannot be measured
  lenses: []             # the set risk_accepted names — NOT a fixed list
---

# SRS — {Product Component}

<!-- TEMPLATE GUIDE — act on these comments, then delete them. Never emit a comment in a finished
     SRS. Section headings stay English; the prose inside is Bahasa Indonesia, with technical terms
     left in English per the controlled vocabulary. -->

<!-- NOT a one-shot document. Despite the IEEE name, this SRS is LIVING: one per Product Component,
     amended every spec, never signed off and frozen. -->

<!-- TWO SKILLS WRITE IT, AT TWO GATES, and every section below says which:
       [G3]  wdi-blueprint intent `catalog`. Exists at EVERY mode, including catalog
       [G4]  wdi-component intent `behaviour`, only as deep as the component's mode

     So this file EXISTS at mode: catalog. It carries the actor list and the use case catalogue, and
     what is absent there is 04-usecases/UC-<n>-<slug>.md — the step-by-step flows.

     `reviewed.lenses` MUST match what this component's risk_accepted names in components.yaml —
     edge-case-hunter at low and medium, structure + prose at high. It is NOT read off `mode`.

     That set is what a FIRST review and a gate-opening review carry. A later re-review runs
     structure + prose, covers only the delta since `sha`, and puts edge-case-hunter back when that
     delta touches money, personal data, an irreversible action, or a third party. wdi-review owns it. -->

## Decision Summary · [G3]

<!-- <=1 page, business language, no jargon lacking a Glossary entry. What the Product Owner reads.
     A summary that cannot be read inside the gate's time budget IS the finding.

     NO DERIVED FACT. `mode`, `risk_accepted`, which `DEC-` bind this file — "none yet" included —
     how many UC or FR there are, and which slots exist are all held elsewhere and MUST NOT be
     stated here. `corpus-guide.md` § A derived fact has exactly one home says where each lives, and
     that the remedy for one already written is DELETION, not correction. -->

## Why · [G3]

<!-- Why this component exists as a separate thing. One paragraph. If it reads the same as another
     component's Why, the boundary is wrong. -->

## Actor Register · [G3]

<!-- SSOT for actors, referenced by the SDD. MUST stay in this kernel, never split into a slot. Two
     actors that turn out to be the same person MUST be merged, and G3 asks exactly this.

     A variant of one actor that differs only in what is shown to them is NOT a second actor. -->

| Actor | Who they are | What they may do |
| --- | --- | --- |

## UC Catalogue · [G3]

UC Catalogue — see `.control/registry/usecases.yaml`, rows where `component: {pc}`.

<!-- A POINTER, not a table. The catalogue's one home is `usecases.yaml`; this section used to carry a
     second copy, and `uc-catalogue-matches` existed only to keep the two agreeing — it once caught 26
     rows that had drifted. The rendered SRS (`.what-rendered/<pc>/SRS-<pc>.md`) and the blueprint
     both show the table, from the registry.

     What is still decided HERE, when wdi-blueprint lands the rows: a title MUST be a sentence a user
     would say, never a system term — G3 asks this as a starred question. `critical` is yes ONLY when
     the use case touches money, personal data, or an irreversible action; more than a third marked
     means the definition was misapplied. -->

## Constraints · [G3]

<!-- What this component MUST work within, and where each comes from — a business rule, a regulation,
     an external system, an applied DEC-, an AD-N. A constraint with no source is an assumption in
     disguise; file it through wdi-question instead. -->

## Non-Goals · [G3]

<!-- What this component explicitly does NOT do, and which component does it instead. This does more
     work than it looks: it is what stops the next builder adding a nearby thing here. -->

## Prerequisite · [G3]

<!-- What MUST already exist before this component can behave as described — another component, an
     external system, a dataset, a credential. A prerequisite waiting on somebody outside belongs in
     .control/questions/external.md, and that file holds go-live only, never a design gate. -->

## Success Signal · [G3]

<!-- How we will know this component works — observable, not aspirational. Scales with stakes: a
     sentence for a small component, a measure with a target for one touching money or personal data. -->

## Assumptions, Risks, and To Be Confirmed · [G3]

<!-- THREE separate lists, and collapsing them loses the owner. An assumption is something we decided
     to believe; a risk is something that may go wrong; a to-be-confirmed is a question with an owner.

     Every to-be-confirmed MUST be filed through wdi-question before the gate opens — into
     assumptions.md by default, blocking.md only through the three tests that file states. -->

### Assumptions

### Risks

### To Be Confirmed

## Gate Checklist · [G3]

<!-- The gate questions as they apply to THIS component, answered yes / no / change. The full list
     lives in delivery-flow-guide.md and MUST NOT be copied here. At mode: catalog only the starred
     questions are asked.

     An answer MUST NOT carry a COUNT of registry rows — "all four use cases are covered" is a claim
     about usecases.yaml that a fifth UC falsifies without touching this file. Answer the question. -->

## Design Reference · [G3]

<!-- One line pointing at the paired SDD, plus any AD-N that binds this component — the spine's
     `binds:` is authored, not derived, so an AD-N citation belongs here.

     APPLIED `DEC-` DO NOT. They are derived from `touches:` and live in .control/generated/decisions.md;
     point at it. A line saying "no applied DEC- binds this component yet" is the worst version — true
     the day it is written, silently false forever after, and it looks like diligence.

     Nothing else: solution shape MUST NOT appear in this document — no framework, no table, no
     endpoint, no class, no queue, no file path. -->

---

## Slots

<!-- All slot content is [G4], written by wdi-component intent `behaviour` and only as deep as the
     component's mode. At catalog every slot stays empty, and that is a finished state.

     Content SHOULD stay in this kernel until the file grows past roughly 400 lines — a suggestion,
     not a threshold. When it must split, the FIRST slot broken out SHOULD be 04-usecases/.

     The numbers are READING ORDER, not classification. This is the opposite of .how/<pc>/, where
     01-06 classify by ABCE. The two MUST NOT be conflated.

     02-rules/       rules-<pc>.md — business rules binding ONLY this component. From mode: outline.
                     A rule that turns out to bind a second component is PROMOTED to
                     .what/business-rules.md through wdi-blueprint, never copied
     03-domain/      domain-model.md — entities, relations, columns. [G3], exists at every mode.
                     state-machines.md — from mode: deep only.
                     NOT a database schema; column types MUST NOT appear here
     04-usecases/    UC-<n>-<slug>.md, one file per full flow. At most 3 at outline and guarded;
                     every critical UC at deep. At most EIGHT steps each — a flow needing more is
                     either two use cases or has started describing implementation
     05-scenarios/   SCN-<nn>-<slug>.md, long branches hanging off one UC. From mode: deep only

     01-requirements/ and supplements/ are REPEALED. The first was permanently empty — FR live in the
     PRD and this document cites them by id. The second existed for the ANX- concept, which is gone.

     THIS SECTION EXPLAINS THE SHAPE, NOT THE CONTENTS. It MUST NOT say which slots exist, which are
     empty, or which are "not written yet". That is `.control/structure-document.md`, derived from the
     tree on disk. One real SDD claimed four of its five slots unwritten while one of them held 223
     lines. -->

## Open Items

<!-- A POINTER, not a copy. Ids only, and the id is enough: whether an OQ- is still open is held by
     .control/questions/, so restating its status here creates a second answer on a slower clock.

     An assumption left here with no id is the failure wdi-question exists to prevent. An id listed
     here that has been answered for weeks is the failure this rule exists to prevent. -->
