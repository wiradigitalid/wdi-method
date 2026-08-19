---
status: Accepted
---

# Corpus Guide

**Loaded when:** deciding where a file lives, or creating a new file in the corpus

Four layers and one workspace. Every other guide describes one document; this one answers the question that
comes before all of them — **where does this belong?**

The quick answer for the thing actually in your hand is the "benda di tangan → folder" table in `AGENTS.md`.
It is deliberately there rather than here: it is needed at the moment someone would otherwise have to reason
about what `.what/` and `.how/` mean, and that moment comes before anyone thinks to open a guide. It MUST NOT
be copied into this file.

## The four layers

| Layer | Answers | Lifetime | Written by |
|---|---|---|---|
| `.constitution/` | How we work | Living, rarely changes | Us |
| `.control/` | What currently holds, and what has been decided | Living, changes often | Us + generators |
| `.what/` | What is promised | Living, amended | BMad class A + us |
| `.how/` | How it is built | Living, amended | BMad class A + us |
| `_bmad-output/` | Work in progress | Ends when the work does | BMad class B and C |

`.control/` is the value of `{project_knowledge}` in BMad's configuration. There is no `docs/`.

## The placement test

One question decides everything: **is this file still correct after its wave has passed?**

Yes → the corpus. No → `_bmad-output/`.

`_bmad-output/` is committed but **not curated**. Committing it is what makes citation by path stable, so a
decision or a PRD MAY point into it. Research, brainstorming, forge, and PRFAQ reports are never promoted.

A run folder MUST NOT be deleted **while anything still needs it** — the `update` intents re-read the original
inputs in place. "Never deleted" is not the rule; the rule is a **retirement condition**, and it is below.

## Who lands what

There is no separate placement skill. A skill lands the output of the layer **it owns**, and the landing is
part of producing it — never a follow-up someone else performs.

| Output | Permanent home | Owner |
|---|---|---|
| The spine | `.how/_platform/ARCHITECTURE-SPINE.md` | `wdi-blueprint` |
| C4 L1 · L2 · one L3 per container holding more than one PC | `.how/_platform/c4-l1-system-context.md` · `c4-l2-containers.md` · `c4-l3-<container>.md` | `wdi-blueprint` |
| each container in C4 L2 | a `container` entry in `components.yaml` | `wdi-blueprint` |
| **The three inventories** | `.how/_platform/inventory-db.md` · `inventory-api.md` · `inventory-screen.md` | `wdi-blueprint` |
| The error envelope, and anything else defined once for the product | `.how/_platform/cross-cutting.md` | `wdi-blueprint` |
| UC catalogue · Actor Register · domain model | `.what/<pc>/SRS-<pc>.md` · `03-domain/domain-model.md` | `wdi-blueprint` |
| Business rules binding more than one PC | `.what/business-rules.md` | `wdi-blueprint` |
| A domain term | `.control/product-glossary.md` | `wdi-blueprint` |
| Full UC flows · local rules · state machines · scenarios | `.what/<pc>/` slots `02`–`05` | `wdi-component` intent `behaviour` |
| The SDD and its slots `02`–`06` | `.how/<pc>/` | `wdi-component` intent `design` |
| each Boundary and Control object drawn | an `LC` in `components.yaml` | `wdi-component` intent `design` |
| `EXPERIENCE.md` | `.what/<pc>/04-usecases/` | `wdi-ux` |
| `DESIGN.md` | `.how/<pc>/01-ux/` | `wdi-ux` |
| tokens and base components | `.how/_platform/design-system.md` | `wdi-ux` |
| each screen in `DESIGN.md` | an `LC` of type `ui-screen` in `components.yaml` | `wdi-ux` |
| `RETROSPECTIVE.md` | `RTR-<wave>.md` in `.control/reports/` | `wdi-build`, at wave close |
| `test-summary.md` | test names → `waves.yaml` | `wdi-build` |
| `stack.md` · `conventions.md` · `brownfield.md` | merged into `.constitution/project/codebase-*-guide.md` | `wdi-build`, at wave close |
| A sprint change proposal | a `DEC-` of `type: course-correction` | `wdi-decision` |
| The registry rows and skeletons a new PC needs | `components.yaml` · `.what/<pc>/` · `.how/<pc>/` | `wdi-init` intent `component` |
| `platform_owns` — an entity no component's promise explains | `components.yaml`, plus its description in `cross-cutting.md` | `wdi-blueprint` |
| The two structure maps | `.control/structure-codebase.md` · `structure-document.md` | `wdi-init` intent `structure` |
| An open question | `.control/questions/` — one of four files | `wdi-question` |
| A decision | `.control/decisions/DEC-NNN-<slug>.md` | `wdi-decision` |
| Minutes · a non-technical fact | `.control/meetings/` · `.control/project-non-technical-log.md` | `wdi-log` |

- A skill MUST NOT write into a layer it does not own.
- Registry conversion is part of landing, not a follow-up. A screen that lands in `01-ux/` without its
  `components.yaml` entry has been half-landed, and V12 catches it **at wave close** — which is the
  right moment to be caught, and a bad moment to be surprised.
- Content MUST NOT be edited while it is being landed. If it has to change to fit its new home, that is a
  separate act — say so and stop. Splitting one output across the homes its row names is not editing.
- The C4 set's target files already exist and are **living**. Their owner MUST amend, MUST NOT overwrite; when
  the incoming set contradicts an annotation already there, it MUST stop and report the finding.
- Nothing MAY be landed into a wave that is already closed. The wave is reopened through `wdi-build`, or the
  gap is recorded as an open question.
- An output with **no row** in this table MUST NOT be given a guessed home. It stays in `_bmad-output/`, and
  `wdi-reconcile` reports it — an output with no home is a gap in the method, and MUST surface as one.

## Landing that MUST be confirmed first

Most landings are mechanical and MAY be done without asking. Some change what other people already agreed to,
and those MUST be put to the owner before the file is written — not reported afterwards. The line is drawn by
**what the landing can invalidate**, never by how much text moves:

| | Light — act, then report | Heavy — confirm, then act |
|---|---|---|
| Layer | Stays inside the layer the skill owns | Crosses into another layer's consequences |
| ID chain | No `BG`/`CAP`/`FR`/`NFR`/`UC`/`LC` id is born, renamed, or retired | Any of them is |
| Depth and risk | `mode` and `risk_accepted` unchanged | Either would have to change |
| Existing text | Adds, or replaces content the same skill wrote | Overwrites or contradicts what another skill or a human wrote |
| Registry | Adds the entry its own output requires | Removes or re-points an entry something else already cites |

Any one heavy row makes the whole landing heavy. When confirmation cannot be obtained now, the landing MUST
NOT be split into a light half that goes ahead — half-landed output looks distributed and is worse than output
that waited.

A skill MUST NOT lighten a landing by narrowing what it writes. Dropping the contentious half to stay under
the bar is the same change, made invisible.

## Product Component — the naming and proposal rule

This rule lives here, beside the definition, and **not inside a skill**. If it lived in one skill, the second
skill that needed it would copy it, and the two copies would drift.

> The name of a Product Component MUST be a surface a user could name. A name that states a layer, a service,
> or a pattern MUST be rejected at proposal time, not corrected later. Additions, changes, and removals MUST
> be presented separately, each with the `FR` behind it.

A PC MUST NOT be created because a folder would look tidy. A PC that no `FR` points at is a folder with
nothing inside it.

Birthing is cheap and retiring is not: retiring or renaming a PC that already carries an SRS goes through
`wdi-decision`, never through the skill that births one.

## Product Component, Logical Component, container, `_platform`

Four words that are easy to blur and MUST NOT be:

| Term | Is | Registered in |
|---|---|---|
| **Product Component** | A surface a user can name — what they came to do | `product_components` |
| **Logical Component** | A unit inside the build — a screen, a service, an adapter, an entity | `logical_components` |
| **Container** | Something that runs or ships on its own | `containers` |
| **`_platform`** | **Not a component at all** — the home for what belongs to no Product Component | `platform_owns`, and the `_platform/` folder |

PC and container are **crossing axes**, not a hierarchy: one PC MAY be delivered by several containers, and one
container MAY serve several PCs. An `LC` names its container in a `container:` field, which is what lets
`structure-codebase.md` be checked against the registry rather than trusted.

## `_platform` — what belongs to no Product Component

`_platform` is **not a Product Component**, and it MUST NOT be registered as one. It fails the naming test on
purpose: nobody came to the product to use "the platform". It therefore carries **no `mode`, no
`risk_accepted`, no SRS, no SDD, and no G4** — its documents are the spine, the C4 set, `cross-cutting.md`,
and the three inventories, and all of those exist at every `mode`.

What it does carry is **ownership**. `_platform` is a legitimate value in **every** position that asks
*"which component owns this"* — the `platform_owns:` list for domain entities, the owning-component column
of any inventory row, an `LC`'s `component:` field, and any such column a later artifact adds. One test,
one cost, everywhere; there is no per-artifact special case to negotiate, and a new kind of thing arriving
next year needs no new discussion.

The test, and both halves MUST hold:

> Something belongs to `_platform` when **no single Product Component's promise is the reason it exists**,
> *and* more than one component reads, writes, or depends on it.

Four kinds qualify today and the list is open: **data** (a product-wide setting, the trace of a shared
outbound channel) · **endpoint** (`/health`, `robots.txt` — plumbing no `FR` promises and none should) ·
**job** (a scheduled cleaner whose data belongs to a component but whose machinery does not) · **screen**
(none yet).

Failing either half, it belongs to a Product Component — and the component is found by asking which `FR`
would have to be withdrawn for the entity to stop being needed. Two examples of the trap:

| Entity | Looks platform-shaped | Actually |
|---|---|---|
| `activity_events` | product-wide telemetry, several components write it | **one component** — an `FR` promises somebody can SEE those counts, and withdrawing it is what would make the table unnecessary |
| `email_logs` | one component sends first | **`_platform`** — it is the trace of one outbound channel that order notifications and password recovery both use, and neither promise is why the channel exists |

**One guard, and it is what stops this becoming a drawer:** everything `_platform` owns — in any position —
MUST be described under `## Platform-owned` in `cross-cutting.md`, with its kind and the shape every toucher
obeys. A platform that owns something documents it. V21 checks it, and skips only while that section has not
been born at G3.

That guard is the whole reason `_platform` can be a general answer rather than an escape hatch: reaching for
it costs a row somebody has to write, so it stays cheaper to find the real owner when one exists.

`_platform` has no `FR`, so an `FR` that writes something platform-owned has nothing to point `defers_to` at,
and MUST NOT be asked for one. What replaces "one writer" there is **one documented shape**: it is written the
way `cross-cutting.md` says, and a component wanting it written differently is proposing a change to that file.

Platform ownership sits with `wdi-blueprint` intent `platform`, beside the rest of `_platform/`. `wdi-init`
intent `component` MAY name a candidate and MUST NOT claim one.

**A decision the pattern cannot derive lives in the artifact it governs.** An inventory row owned by
`_platform`, and a route that is a *state* of another screen rather than a screen of its own, are both
judgements — so both are declared in that inventory's own frontmatter (`platform_rows:` and `states:`) and
survive every re-derivation. Putting either outside the file means the next derivation silently deletes the
owner's decision.

## Two axes inside `.what/`

| | `_prd/<initiative>/` | `<pc>/` |
|---|---|---|
| Slices by | **Initiative** — one functional area | **Space** — one Product Component |
| Answers | What is promised to a user | What this component can do |
| Written for | Outside readers — client, sponsor | People building the system |

Both are living. What separates them is **promise versus behaviour**, not lifetime. One functional area MAY
span several components, and one component MAY serve several PRDs, so neither can absorb the other.

**Time is not a folder axis.** Release lives in `CAP.target_release` and in `waves.yaml`.

## Slot numbering means two different things

| Layer | Slots | The number means |
|---|---|---|
| `.what/<pc>/` | `02-rules` · `03-domain` · `04-usecases` · `05-scenarios` | **Reading order** — its rules → the things → how it is used → its branches |
| `.how/<pc>/` | `01-ux` … `06-flows` | **ABCE classification** — Boundary, Control, Entity, behaviour. Not a reading order |

Reading one as the other is the most common misfiling in this corpus, and it is silent: the file lands in a
plausible-looking folder and is simply never found again.

`.what/<pc>/01-requirements/` is **repealed** — permanently empty, because `FR` live in the PRD and the SRS
cites them. `supplements/` beside either kernel is repealed with the `ANX-` concept.

## Splitting slots

- A slot MAY stay empty. Content SHOULD stay in the kernel until that file grows past roughly 400 lines — a
  suggestion, not a threshold, and a file that is clearer split earlier MAY be split earlier.
- The first slot to be split SHOULD be `04-usecases/` — it is always the largest part.
- One use case with many branches MUST put its branches in `05-scenarios/` rather than growing its own file.
- The `Actor Register` MUST stay in the SRS kernel. It is the SSOT the SDD mirrors, and it is short.

## Document codes

| Code | Is |
|---|---|
| `BG-` `CAP-` `FR-` `NFR-` `UJ-` `UC-` | The traceability chain, allocated from `requirements.yaml` and `usecases.yaml` |
| `AD-` | An invariant in the architecture spine — a living rule, edited in place |
| `DEC-` | A decision — an event, frozen when `applied`, only superseded |
| `LC-` | A Logical Component |
| `OQ-` `RTR-` | An open question · an archived retrospective |
| `BUG-` `HOT-` | A defect · a hotfix |
| `NT-` | A non-technical fact |

**Retired, and MUST NOT be coined again:** `ADR-` (renamed to `DEC-` on 2026-08-18; the old prefix inside a
document frozen before that date is an alias for the same number) · `ANX-` (zero annexes were ever born) ·
`SCP-` (a course correction is a `DEC-`) · `BRS-`, `PFQ-`, `RES-` (exploration output is never promoted).

IDs are allocated **globally** and never restart per document, per component, or per release.

### A record of the past MUST NOT be rewritten to match the present

A retired name appearing in a document that **records what happened** is a fact about the past, not
drift, and a sweep MUST NOT rename it. Four kinds, and all four are legitimate:

| Where | What it says | Why it stays |
|---|---|---|
| `.control/decisions/DEC-*.md` — `Applied to`, `Temuan` | *"`wdi-apply` applied this on 2026-08-17"* | It did. Renaming it to today's skill claims a skill that did not exist then did the work |
| `.control/memlog/*.md` | Which skill ran, and what it decided while running | A run log. Rewriting it destroys the only account of how an artifact got that way |
| `.control/questions/answered.md` · `project-non-technical-log.md` | An answer, with its date and who gave it | Closed in place by rule; the wording is part of the record |
| `.what/` and `.how/` frozen before a rename | Prose that cites the old name | Frozen by decision. `ADR-NNN` there is a retired alias for `DEC-NNN` with the same number |

The test is one question: **does this sentence describe what happened, or state what holds?** Describes
→ leave it. States → sweep it.

That distinction is why a sweep can be run repeatedly without churn. Without it, every pass rewrites
the same three dozen historical files and the diff stops carrying information.

File naming that must survive every OS is governed by `structure-guide.md` and MUST NOT be restated here.

## `.constitution/project/` — this product's custom rules

The rest of `.constitution/` **belongs to the method**: it ships in the `wdi-method` package and is
**overwritten** on every `update`. This folder is the only one that is not. `update` seeds it once and
never writes over it again, and `promote` **skips it**, so a rule that names a client cannot reach the
public package.

| Goes here | Does not, and its home |
|---|---|
| A review policy a client requires | product / client name → `index.yaml` `product:` |
| A process rule that came from a contract | code conventions → `.constitution/project/codebase-*-guide.md` |
| A policy that differs from the method default | scope and ownership → `.constitution/project/constitution.md` Art. 1, 2, 5 |
| A prohibition specific to this domain | agent instructions → `AGENTS.md`, outside the marked block |

**A generic rule MUST NOT be moved here.** If it holds in any project it belongs to the package — fix
it there, then `promote`. Using this room to bypass the package is how a method stops being generic
with nobody deciding it, and **an empty room is a valid state**: filling it so that it gets used is the
very failure this rule prevents.

Frontmatter is required and **V27** checks it: `scope: project` · a one-line `purpose:`. A file MAY
narrow or add with nothing further; to **contradict** a generic rule it MUST name that rule in
`overrides:` and carry `decision:` naming the `DEC-` that decided it. A method that can be contradicted
without a decision stops being trustworthy in the next repo.

**Whole files, not marked blocks.** `AGENTS.md` uses a marked block because it is one file;
`.constitution/` has fifty-odd, and blocks inside them would make `update` perform surgery in every
file — one broken marker and either the product's rule is erased or the generic rule freezes.

## Documents that predate the method

A repository that already had documentation keeps it in `_bmad-output/prior-knowledge/`. It follows the same
rules as the rest of `_bmad-output/`: committed, never curated, cited by path, never deleted.

The sorting happens once, at install, and the test is a single question: **is this file already the artifact
one corpus slot asks for, one file for one slot?** Yes → straight into that slot, carrying a provenance line
naming the gate that ratifies it. No → `prior-knowledge/`.

**A file in `prior-knowledge/` MUST NOT be copied into `.what/` or `.how/` afterwards.** It enters the corpus
only through the skill that owns the slot, which reads it as input. This is the rule the whole arrangement
exists for: moving a file is always cheaper than running the stage that should have produced it, so without a
rule the move always wins — and what lands then has no author, no input trail, and no gate behind it.

### Retiring `prior-knowledge/`, and the condition that makes it safe

A prior document is **input**, and input stops being needed once what it was read for is written down. Three
conditions, and **all three MUST hold** before the folder is deleted:

1. **Every promise it carried is mapped.** The old numbering has a complete old → new table, and that table
   lives in the `addendum.md` beside the PRD it maps into — **not** in `prior-knowledge/`, precisely so the
   source can be retired without taking the map with it.
2. **Every live citation into it has been re-pointed or dropped.** A glossary entry, a `risk_note`, an
   `enforced_by` — anything that *states what holds*. Where the fact has a home in code or in `.control/`, the
   citation points there instead.
3. **The retirement is recorded as a `DEC-`.** Deleting source material is expensive to reverse, and the
   answer to *why is it gone* is not readable from the code.

**A citation left inside a record of the past is not condition 2's business.** A `DEC-`'s Trace naming the
document it was derived from, or a memlog naming what a run read, describes what happened — and the rule above
on records of the past applies. Those citations dangle by design, and `wdi-reconcile`'s Evidence check MUST NOT
report them: what makes it harmless is that the substance is already written into the document doing the
citing, so the path is provenance rather than a dependency.

The same three conditions govern `.work/`, with one difference: nothing there was ever authority, so condition
1 is usually already met.

Two consequences that MUST be expected rather than discovered:

- Internal numbering inside a prior document — `FR-3`, `§7` — is **not** a corpus ID. A mapping table MAY be
  written once, and it lives in `prior-knowledge/`, never in `.control/`.
- A file placed straight into a slot MUST lose any claim of authority it makes about itself. In the corpus,
  authority comes from the layer and the gate.

## Rules

- A file MUST NOT be moved between layers by a skill that owns neither end. Anything else is a misplacement,
  and MUST be reported rather than fixed.
- A fact MUST have exactly one home. When two documents state the same thing, one of them MUST become a
  reference — and the copy being replaced MUST be deleted, not left as a courtesy.
- Solution shape MUST NOT appear in `.what/`. Promises MUST NOT appear first in `.how/`.
- Superseded artifacts are not deleted. Their status becomes `superseded` and points at the replacement.
