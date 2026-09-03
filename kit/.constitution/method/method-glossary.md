---
status: Accepted
---

# Method Glossary

**Loaded when:** a method term is unclear, and before coining a new one.

The words this method uses for **itself**. What the product is about belongs to
`.control/product-glossary.md` instead. A term defined here MUST NOT be redefined there, and the
reverse holds too. The test: would this term still apply on a different product? Yes → here.

## Layers

| Term | Means |
|---|---|
| **Corpus** | The four layers below. `_bmad-output/` is not part of it |
| **`.constitution/`** | How we work. Rules. Rarely changes |
| **`.control/`** | What currently holds and what has been decided. Facts. Changes often. Equals `{project_knowledge}` |
| **`.what/`** | What was promised |
| **`.how/`** | How it is built |
| **Workspace** | `_bmad-output/` — work in progress, committed but not curated |
| **Placement test** | Is this file still true after its spec has passed? Yes → corpus. No → workspace |

## Units

| Term | Means |
|---|---|
| **Product Component** (PC) | A domain slice — the box at C4 L3. Lives in `.what/<pc>/` and `.how/<pc>/`, and its `containers:` says where it runs |
| **Logical Component** (LC) | One addressable unit of build. Registered in `components.yaml` with `type` · `container` · `owner` · `area` |
| **Container** | Something that **runs its own code or stores its own data** and can be replaced without rebuilding another one. The C4 L2 term, and the value of an LC's `container` field. Two questions decide it and both MUST be yes — `architecture-guide.md` owns the test. Shipping two containers in one release does **not** merge them |
| **`built`** | A container's one boolean. `true` when we write what is inside it, `false` when we deploy someone else's implementation. It decides whether the container gets an L3, an `LC`, and a heading in the codebase map — `container-built` checks all three |
| **External system** | Something the product talks to whose **runtime we do not deploy**. It belongs at C4 L1, and MUST NOT be a container, an `LC`'s `container`, or a heading in the codebase map. What we lean on it for lives in `cross-cutting.md` or an integration contract |
| **`_platform`** | **Not a component.** The home for what belongs to no Product Component: the spine, the C4 set, `cross-cutting.md`, the three inventories, and whatever it **owns**. A legitimate value in every position that asks which component owns something — `platform_owns`, an inventory row, an `LC`. Four kinds today: data · endpoint · job · screen. It carries no `mode`, no `risk_accepted`, and no G4 |
| **Library** | An includable artifact — compiled into or imported by something else, never run on its own. Not a container |
| **Slot** | A numbered sub-folder of a PC. `.what/<pc>/` 02–05 is reading order; `.how/<pc>/` 01–06 is ABCE classification. The two numberings do **not** mean the same thing |
| **Kernel** | The `SRS-<pc>.md` or `SDD-<pc>.md` file itself. Content SHOULD stay in it until it grows past roughly 400 lines — a suggestion, not a threshold |

A PC is not a container: a container runs, a PC is a domain. One container holds several PCs, and
one PC may appear in more than one container. Because they cross, neither list implies the other, and
the crossing MUST be written down rather than inferred — that is the PC × container matrix at C4 L2,
rendered from each PC's `containers:`.

## Flow

There is no "stage". The five gates are the only flow vocabulary, and the word **area** is not used at all —
there is only Product Component.

| Term | Means |
|---|---|
| **Gate** | One of five decision points: G1 Problem · G2 Product · G3 Blueprint · G4 Component · G5 Release. Named after what is decided there, not after the work before it |
| **`mode`** | The one knob for **document depth**, and nothing else. `catalog` · `outline` · `guarded` · `deep`, default `catalog`. Two scopes — global in `index.yaml`, per component in `components.yaml`, and the per-component one wins. **No third scope** |
| **`risk_accepted`** | The one field for **review intensity**, and nothing else. `low` · `medium` · `high`. It MUST NOT be derived from `mode`, nor `mode` from it |
| **Blueprint** | The whole-product portrait decided once at G3: one line per use case, table, endpoint, and screen, plus entities, actors, the spine, C4, and cross-component rules. It names a **gate and a skill**, never a document or a folder |
| **Spec** | One unit of delivered work: the tickets that reach one outcome. Opens at G4 or G5, closes at G5, recorded in `specs.yaml`. Its document is `SPEC.md`, **optional at size `S`** — one term, one entry, and the document is named after the unit the way a `DEC-` file is named after its decision |
| **Release** | What a PRD promises. One release MAY span several specs; the relation is data, never inferred from numbering |
| **Spec size** | `S` ≤3 tickets no new FR · `M` 4–12 · `L` >12 or a new container. MAY be raised mid-flight, MUST NOT be lowered. It does **not** choose which gates are active — that is `mode`. It decides two things: whether G4 and G5 merge into one session (`S`), and whether `SPEC.md` is written at all (`M` and up) |
| **Fast Path** | A fix that skips all gates: ≤1 ticket, no FR/UC/`AD-N`/domain-model change, no money, personal data, or third-party integration |
| **Step** | One of the five points inside `wdi-build`'s ship pipeline — plan · build · panel · publish · CI. It is **not** a gate and not a stage, and the word MUST NOT be used for anything at gate altitude |

## Artifacts

| Term | Means |
|---|---|
| **Brief** | One problem, one user, one measure. Singleton, spans releases |
| **PRD** | What is promised for **one initiative**, across every release it touches. FR and NFR numbered from the registry |
| **SRS** | Per PC: what the system must do. `.what/` — slices space, while the PRD slices initiative. It **exists at every `mode`**, carrying the actor list and the use case catalogue |
| **SDD** | Per PC: how it is built. `.how/`. At `mode: catalog` it is a skeleton, and that is a finished state |
| **Inventory** | One of three living registers at product level — tables, endpoints, screens. Written as a plan when there is no code, **derived** from code once there is |
| **Architecture spine** | `ARCHITECTURE-SPINE.md` — invariants as `AD-N`, each carrying Binds · Prevents · Rule. It constrains; it does not describe |
| **C4** | L1 system context · L2 containers · L3 components, one file per container. L1+L2 together are what other methods call the HLD |
| **`DESIGN.md`** | UX per PC, in `.how/<pc>/01-ux/` |
| **`EXPERIENCE.md`** | The user-facing journey, in `.what/<pc>/04-usecases/` |
| **`DEC-`** | One decision worth remembering, numbered globally. Lives in `.control/decisions/`. Recording is **not mandatory**; it freezes at `applied`, not at `accepted` |
| **SPEC** | The document of **one spec**: a projection of `.what/` + `.how/` that MUST NOT contain anything new. Not read by humans, and **not written at size `S`** — there the tickets are the contract |
| **Ticket** | One unit of build: a tracer-bullet vertical slice, complete through every layer, verifiable on its own, sized to one fresh context window. Carries the tickets that **block** it. Status is read from the ticket itself, never copied elsewhere |
| **Structure map** | `.control/structure-codebase.md` and `structure-document.md` — where things actually are today |
| **Memlog** | The record of *why* while an artifact was written. Never copied into a document; a source when writing a `DEC-`. It is a **run log**, and it MUST NOT be searched as an index of decisions — `.control/generated/decisions.md` is that |

## Identifiers

| Code | For |
|---|---|
| `BG-` · `FR-` · `NFR-` · `UJ-` | Business goal · functional requirement · non-functional requirement · user journey |
| `UC-` | Use case |
| `AD-` | An invariant in the architecture spine |
| `DEC-` | A decision |
| `LC-` | A Logical Component |
| `OQ-` | An open question |
| `RTR-` | **Retired.** It was an archived retrospective in `.control/reports/`; the retrospective step and `V19` went together. A frozen `RTR-` file stays where it is |
| `CAP-` | A capability — the planning unit |
| `NT-` | A non-technical fact |
| `BUG-` · `HOT-` | A defect · a hotfix |
| `goal-has-fr`–`container-built` | Validators. `V10` fell and its number is not reused |

IDs are allocated **globally** and never restart per document, per component, or per release. The chain
that must hold end to end: `BG → FR → UC → ticket → test`.

`ADR-` is **retired**. It was renamed to `DEC-` on 2026-08-18 with the numbers unchanged, so `ADR-004`
inside a document frozen before that date is an alias for `DEC-004`, and those documents MUST NOT be
rewritten for the prefix.

## Registry and generated

| Term | Means |
|---|---|
| **Registry** | `.control/registry/` — the source of truth for IDs and plans. Written through `wdi-*` skills |
| **Generated** | `.control/generated/` — derived from the registry. Written by the generator only, by hand **never** |
| **RTM** | Requirements traceability matrix. Generated, never hand-maintained |
| **Validator** | A script that answers what can be counted. It does not replace a gate checklist, which answers what must be judged |

## BMad terms

BMad terms live in a WDI glossary because WDI runs on BMad. Each is defined **as WDI uses it**;
where BMad's own meaning is wider, the narrower one here wins.

| Term | Means |
|---|---|
| **Stories mode** | **Retired.** It was BMad's route — `SPEC.md` + `stories.yaml` produced by `bmad-spec`. The engine layer below G5 no longer runs it; `bmad-guide.md` says what replaced it |
| **Skill class** | `A` living document, straight to the corpus · `B` living but wrongly granular, lands neutral then is placed · `C` spent after its work · `D` no artifact |
| **Companion** | A side file a BMad skill produces next to its main output. The lasting ones are promoted by the distillation table |
| **Distillation** | Promoting what is durable out of `_bmad-output/` before a spec closes. What is not promoted dies with the folder |
| **`persistent_facts`** | Files a skill always reads. Routing alone does not achieve this |
| **`doc_standards`** | Rule files a skill checks its output against. Facts MUST NOT be installed here, and neither MUST anything at `status: Reference` |
| **`{project_knowledge}`** | The config variable pointing at `.control/` |
| **`_bmad/custom/`** | Where every BMad override lives. `.claude/skills/bmad-*/customize.toml` MUST NOT be edited — it is overwritten on update |

## Retired — MUST NOT be used as current

| Retired | Instead |
|---|---|
| `ADR-` | `DEC-` — same numbers, new prefix |
| `ANX-`, and the annex concept | Nothing. Zero annexes were ever born |
| `SCP-` | A `DEC-` of `type: course-correction` |
| `layer:` on a decision | `touches:`, filled from what actually changed |
| "Stage 1"…"Stage 5" as flow vocabulary | The five gates |
| `epics.md` · `sprint-status.yaml` · `bmad-sprint-planning` · `bmad-create-epics-and-stories` · `stories.yaml` | Tickets, each carrying its own status and its blocking edges |
| Validator `V10` | Nothing. Its number is not reused |
| `bmad-help` as the answer to "where am I" | `wdi-help` |
| The skills `wdi-analysis` · `wdi-architecture` · `wdi-design` · `wdi-glossary` · `wdi-structure` · `wdi-apply` · `wdi-correct-course` · `wdi-wave` · `wdi-ship-story` · `wdi-product-brief` · `wdi-meeting` · `wdi-project-log` | The seventeen in `why/README.md`. `why/rationale.md` says which absorbed which, and why |
| An Indonesian synonym for a `mode` value — *ringkas*, *terjaga*, *katalog* as prose | The English value, used as written: `catalog` · `outline` · `guarded` · `deep` |

## Synonyms that MUST NOT be coined

A synonym for a term that already has an entry is drift, and `wdi-reconcile` hunts for it.

| Do not say | Say | Because |
|---|---|---|
| application · app · service, for a deployable | **container** | The term is already defined at C4 L2 and carried by every LC |
| infrastructure · third-party · dependency, for something inside the boundary | **container** with `built: false` | Calling it something else is how a container ends up with no row, no owner, and no NFR |
| container, for something whose runtime we do not deploy | **external system** | It has no `built`, no L3, and no heading. Registering it as a container promises a section of the codebase map that will never exist |
| module · package, for a unit of build | **Logical Component** | `components.yaml` names it, and `lc-registered` resolves against that name |
| epic · sprint, for a batch of work | **spec** | Both belong to the sprint route this method dropped |
| **wave**, for a unit of delivered work | **spec** | Retired when the engine layer below G5 changed. See the retired-alias rule below |
| **story**, for a unit of build | **ticket** | Same retirement. A ticket is a vertical slice that blocks and is blocked; a story was a row in a file BMad owned |
| area, for a domain slice | **Product Component** | The word "area" is not used anywhere in this method |
| platform, for a Product Component | **`_platform`**, and only for what is not one | Registering `_platform` as a PC gives it a `mode`, an SRS, and a G4 it has no use for |
| profile · tier · level, for document depth | **`mode`** | One knob, four values, and no matrix behind it |
| feature, for a domain slice | **Product Component** | A feature is a promise; a PC is a folder pair with an owner |
| requirements document | **PRD** or **SRS** | They cut different axes — time versus space — and merging the names merges the documents |

## Retired terms keep their frozen documents

`wave` and `story` are **retired aliases** of `spec` and `ticket`. A `wave` or a `story` appearing in a
document frozen before the change — a closed `DEC-`, an `RTR-`, minutes, `why/rationale.md`'s record of what
happened — reads as its replacement, and those documents **MUST NOT be rewritten for the term.** This is the
same rule Article 6 already applies to `ADR-NNN` → `DEC-NNN`, and for the same reason: a frozen record that
cites a name is evidence, and rewriting evidence to tidy a vocabulary destroys the thing that made it useful.

What MUST use the new term: every `Accepted` guide, every skill, every registry, and anything written from
here on.

## Rules

- A new method term MUST be added here in the same pass it first appears, not defined where it is
  used. Adding one is a change to the **method itself** — `wdi-blueprint` MAY propose it and MUST NOT
  write it, because a method term binds every project the method is installed in.
- One term MUST NOT have two entries. Two meanings mean two terms.
- A domain term MUST go to `.control/product-glossary.md` instead. If it is unclear which, ask whether the
  term would survive being applied to a different product: yes → here, no → there.
- Common technical terms stay in English when the industry name is the one that matches the code,
  the error message, or the reader's expectation.
