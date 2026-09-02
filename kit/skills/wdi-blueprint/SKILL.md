---
name: wdi-blueprint
description: Use at G3 Blueprint — the one whole-product portrait, written once. Two intents, catalog and platform. Owns the use case catalogue, actors, domain model, cross-component business rules, the glossary, the spine, C4, cross-cutting, and the three inventories. Never writes a single component's depth.
---

# WDI Blueprint

G3 decides **the whole portrait of the system**: which use cases exist, their entities, their tables, their
endpoints, their screens, and the invariants that bind everything built from them. Once per product.

Two intents, run in this order:

| Intent | Writes | Wraps |
|---|---|---|
| `catalog` | Per `<pc>`: § Actor Register · § UC Catalogue · `03-domain/domain-model.md`. Product level: `.what/business-rules.md` · `.control/product-glossary.md` · `usecases.yaml` | `mattpocock-skills:domain-modeling` |
| `platform` | `.how/_platform/`: the spine · C4 L1/L2/L3 · `cross-cutting.md` · the three inventories. Registry: `containers` | `bmad-architecture` |

**Blueprint content is untouched by `mode` and by `risk_accepted`.** Everything above exists at every mode,
including `catalog`. That is what keeps the order non-circular: `mode` is first needed at G4.

You MUST NOT write a single component's depth — full UC flows, local rules, failure behaviour, contracts. All
of that is `wdi-component` at G4. You MUST NOT write a promise; when the blueprint proves a PRD wrong, that is
`wdi-product`, not a quiet edit here.

## Inputs

| Source | What it answers |
|---|---|
| `.what/_product-brief/brief.md` | The problem, the primary user, the boundary the portrait MUST respect |
| `.what/_prd/*/prd.md` — **every one** | Every promise made: the `FR`/`NFR` the portrait has to cover |
| `.control/registry/components.yaml` | Which components exist, and their `owns:` |
| `.control/product-glossary.md` | Terms already fixed |
| `.control/decisions/` | `accepted` and `applied` decisions an `AD-N` usually sits behind |
| `src/` · `web/` | What actually runs, when this is not a new project |
| `.constitution/method/document/srs-guide.md` · `architecture-guide.md` | The rules the result is checked against |

## Step 1 — Position

- The components MUST already exist. If `components.yaml` holds no `product_components`, route to `wdi-init`
  intent `component` — the slicing is born at the tail of G2, from the brief plus every PRD.
- `catalog` runs before `platform`. The spine is written against a portrait that exists.
- If the spine and C4 set already exist, `platform` is an **amendment**, never a create. A second create
  overwrites what three specs of annotation put there.
- If the ask is one component's mechanism or its full flows, route to `wdi-component`.
- If the ask is what the product promises, route to `wdi-product` — an invariant is not a promise.

## Step 2 — Intent `catalog`, in order

The order is binding, and each step is the input to the next. Writing them out of order produces use cases
whose nouns nobody defined.

1. **Glossary.** Every domain noun, into `.control/product-glossary.md`, alphabetically, each citing the
   document and section its definition came from. You MUST NOT invent a definition — cite a source, or route
   the term to `wdi-question`. Two words meaning one thing is **drift**, and it MUST be resolved to one word
   in the same pass, with the losing synonym corrected in the documents that use it.
2. **UC Catalogue**, per component. One line per use case: `UC-N` · title · actor · the `FR` it satisfies ·
   `critical` yes/no. A title MUST be a sentence a user would say, not a system term.
3. **Actor Register**, per component. It stays in the SRS kernel; it is the SSOT the SDD mirrors.
4. **Domain model** — entities, relations, columns — into `.what/<pc>/03-domain/domain-model.md`. Conceptual;
   database column types belong to `.how/`.
5. **Cross-component business rules** into `.what/business-rules.md`. A rule binding only one component is
   G4 work and MUST NOT be written here.

`critical` means the use case touches **money, personal data, or an irreversible action**. Nothing else. If
the count passes a third of a component's use cases, derive it again — `delivery-flow-guide.md` owns the rule
and it MUST NOT be negotiated.

### Domain modelling is active, and `mattpocock-skills:domain-modeling` is its engine

The domain model is not written by taking dictation. **You MUST invoke
`mattpocock-skills:domain-modeling`** to derive it, the same way the spine goes through
`bmad-architecture` — this skill never does the deriving itself, it positions the engine, verifies the
result against `srs-guide.md`, and lands it in this method's template.

Four behaviours are what the engine is invoked for. Verify each one actually happened before landing
anything; an engine run that produced none of them is a transcription, and the run MUST be reported as such:

1. **A term challenged the moment it conflicted** with what the glossary already defines.
2. **Fuzzy language split** — *"you said account: the Customer or the User?"* Two words for one thing is
   drift and Step 1 catches it. **One word for two things is worse and nothing else catches it**, because
   both readings survive review looking correct.
3. **Relationships stress-tested with invented edge scenarios.** This feeds two things asked for elsewhere
   here: the `critical` derivation, and the branches that become `05-scenarios/` at `deep`.
4. **The model cross-referenced against the code**, where code exists, with every contradiction surfaced.
   `wdi-reconcile` compares documents with documents and `inventory.py` compares the three inventories with
   code — **nothing else compares the domain model with the code.**

#### Where it MUST NOT write, and which of its rules MUST NOT be followed

It writes **as it goes, at the repo root**, by its own instruction — *"update `CONTEXT.md` right there,
don't batch these up"* — creating its folders lazily. So its write location MUST be pointed at
`_bmad-output/` **before** it starts, not corrected after. Four of its artifacts are class C working output
here, and **none MUST be landed**:

| Its artifact | Where the fact goes instead |
|---|---|
| `CONTEXT.md` — its own rule makes it *"a glossary and nothing else"*, so the mapping is exact | `.control/product-glossary.md` |
| `CONTEXT-MAP.md` — where each bounded context lives | `components.yaml` + the two structure maps |
| `docs/adr/` — **Article 3** forbids a `docs/` layer for corpus or rules outright | `.control/decisions/` |
| An ADR file — the name is retired here | a `DEC-` through `wdi-decision` |

**Its ADR test is narrower than ours and MUST NOT be used.** It offers an ADR only when a decision is hard
to reverse **and** surprising **and** the result of a real trade-off. `decision-guide.md` asks one question
instead — *"in three months, is the answer readable from the code?"* — which deliberately keeps the decisions
that sound small. So it will stay silent on decisions this method wants recorded: apply our test to what it
surfaces, and MUST NOT read its silence as *"nothing worth recording happened"*.

#### When it is not installed

`bmad-guide.md` §*When an engine earns being invoked at all* owns the general rule. For this engine: it is a
**plugin, not part of this package's install**, so its absence is a real state and not a defect. Report it
once, name the four behaviours above as the standard the derivation is still held to, and carry them out
here. You MUST NOT block G3 on a missing plugin, and you MUST NOT report its absence as a finding.

#### What lands, whatever produced it

The entity table's `Code name` and `Never called` columns, plus the glossary entry each row cites —
`language-guide.md` owns which language the code name is written in. And one rule holds regardless of engine:
**the conceptual layer stays conceptual.** A column type appearing in `03-domain/` means the model has
quietly become physical, and `templates/model.md` owns that.

**A method term MUST NOT be written into `.constitution/method/method-glossary.md`.** A product term binds one
project; a method term binds every project the method is installed in. Raise it as a proposal, state where it
appeared and why the existing vocabulary does not cover it, and hand it to the owner.

## Step 3 — Parallel where there is a key, serial where there is not

This is not theory. In the previous run, 41 cross-component business rules from seven parallel agents had to
be merged and de-duplicated **serially**, because the target file had no key — and that merge was the most
expensive part of the pass.

> Parallel fan-out is only for output with a natural key. Output that is a shared list with no key MUST be
> written by one agent that reads the whole input.

| Work | Parallel? | Key |
|---|---|---|
| UC catalogue, actors, entities per component | yes | Product Component |
| Glossary, cross-component business rules, the spine | **no** | there is none |
| The three inventories | yes, one agent per source | table · endpoint · screen |

Three guards when running parallel: each agent writes only its own keyed file; shared files are written in one
serial pass afterwards; the owner reviews the merged result, not N agent reports. Open questions from N agents
arrive as **one** ranked batch.

## Step 4 — Intent `platform`

Dispatch `bmad-architecture` at **initiative** altitude for the spine. Do not restate the rules to it — they
arrive through `persistent_facts` in `_bmad/custom/bmad-architecture.toml`, which installs
`architecture-guide.md` there rather than as `doc_standards` deliberately.

Then verify and land:

| # | Check | Fails when |
|---|---|---|
| 1 | Home | The spine landed anywhere but `.how/_platform/ARCHITECTURE-SPINE.md` |
| 2 | Every `AD-N` carries Binds, Prevents, and Rule | One is blank — an `AD-N` with no Prevents is a preference |
| 3 | Every `AD-N` is an invariant | Breaking it in one component would not break another. It is a seed, and MUST be marked as one |
| 4 | Stack, tree, and data shapes marked as seeds | Written as contracts, which makes the spine wrong at the first upgrade |
| 5 | No alternatives or cost in the spine | Those live in the `DEC-` behind it; a second copy drifts |
| 6 | Nothing but invariants | A statement affecting one component only — that is its SDD |
| 7 | Memlog at `.control/memlog/spine.md` | A `.memlog.md` appeared inside `.how/` — `--workspace` was used |

Check 7 MUST be fixed immediately. `memlog-home` rejects a memlog inside the corpus.

**Land the C4 set by amending, never overwriting.** The files are living and already carry annotations,
including a pre-method provenance note that MUST survive. When the incoming set contradicts an annotation
already there, you MUST stop and report it, and MUST NOT resolve it by preferring the newer drawing. Where a
C4 file and the spine disagree, the spine wins and the disagreement MUST be reported. One
`c4-l3-<container>.md` per `built: true` container **holding more than one Product Component**. A
`built: false` container gets no L3 at all, and a one-PC container needs none because the L2 matrix already
places it. **Not one of the three waits for a spec** — `architecture-guide.md` owns that.

**Register the containers** in `containers:` in `components.yaml`, in the same act as landing the L2. It is
not a follow-up.

**And fill every `LC` whose `container:` is empty, in that same act.** Screens registered by `wdi-ux` at
G2 are born without one on purpose — containers do not exist yet — and this is the moment the answer
does. `container-built` starts demanding it as soon as a Product Component lists containers, so filling it here is what
keeps the board clean without anyone tracking a to-do.

Each container MUST carry `built:` — `true` when we write what is inside it, `false` when we deploy
someone else's implementation. It decides whether the container gets an L3, an `LC`, and a heading in the
codebase map (`container-built`). Something whose **runtime we do not deploy** is an external system: it belongs at L1,
and registering it here promises a codebase-map section that will never exist.

**Fill each PC's `containers:` in the same act, and land the matrix at L2** — the registry is the SSOT and
the L2 table renders it. A PC MUST list every `built: true` container it lives in; listing only the main
one is the error the matrix exists to catch. Complete for every PC at G3, untouched by `mode`.

You MUST NOT register a
`product_component` or a `logical_component`.

**Register what `_platform` owns** in the same pass — a domain entity through `platform_owns`, an inventory
row through that inventory's `platform_rows:`, an `LC` through its `component:`. The test is in
`corpus-guide.md` and both halves MUST hold. Each one MUST then be described under `## Platform-owned` in
`cross-cutting.md`, in the same act: `entity-one-writer` checks that second half, because owning something without
documenting it is taking ownership without taking responsibility.

A judgement the pattern cannot derive MUST live in the artifact it governs, not in a script and not in a
skill: an inventory's `platform_rows:` and `states:` are declared in that inventory's own frontmatter, so
re-derivation preserves them. Anywhere else, the next run deletes the owner's decision.

`_platform` is **not** a Product Component. You MUST NOT give it a `mode`, a `risk_accepted`, an SRS, or a
G4, and you MUST NOT move an entity there because its owner is hard to decide.

## Step 5 — The three inventories

They land in `.how/_platform/` with **one owner: this skill.** No negotiation with `wdi-ux`, and no second
copy inside any SDD.

| State | How each is born |
|---|---|
| No code yet | Written as a **plan** — the tables, endpoints, and screens intended. Nothing can be derived, because there is no source |
| Code exists | **Derived first** by `.constitution/method/scripts/inventory.py`, which reads this product's patterns from `.constitution/project/inventory-readers.py`, then compares with the plan. The difference is a **finding**, not hand work. A product with no reader file is told so and nothing is derived — it is never guessed |

An inventory MUST NOT be assembled from a README or from route names that look plausible. Numbers are stable:
a new row takes the next number, never a renumber.

## Step 6 — The roll-up, and what the owner actually reads

Regenerate `.how-rendered/blueprint.md` with `validate.py --generate`. It assembles the UC catalogue, the
actor lists, the domain model, and the three inventories into **one page**.

**That page is what G3 reviews** — not seven files. The catalogue and actors stay in their component kernels as
their permanent home; the roll-up is a view. One fact, one home, one view.

You MUST NOT hand-write anything under `.control/generated/`, `.what-rendered/`, or `.how-rendered/`.

## Step 7 — Review and questions

- No `doc_standards` fires for an SRS or for the spine. Dispatch `wdi-review`, which reads the lens set from
  each component's `risk_accepted`.
- You MUST NOT open G3 on a portrait that has not been through it.
- Every unresolved to-be-confirmed MUST be filed through `wdi-question`, in **one** ranked batch — into
  `assumptions.md` by default, `blocking.md` only through its three tests.
- A decision surfacing while writing is **written into the document as its own content** — stated as what
  now holds, present tense. Never as a parenthetical aside, and never routed to `wdi-decision` merely for
  being a decision: that is only for one with no home here at all, or one touching an `AD-N`.
- An `AD-N` that reverses or narrows an earlier one MUST go through `wdi-decision` first. Editing an `AD-N` in
  place is how a reversal happens with nobody deciding it.

## Step 8 — A PRD that arrives after G3

The blueprint is **living and amended**, not repeated. `wdi-init` intent `component` births the new
components, this skill adds their rows to the catalogue and the three inventories, and **G3 reopens over the
delta only**. The 45-minute session does not run again for one additional initiative.

## Rules

- You MUST NOT write into `.how/<pc>/`, and `design-system.md` in `_platform/` belongs to `wdi-ux`.
- You MUST NOT regenerate the C4 set from scratch. The loss of annotations is invisible in a diff that reads
  as a rewrite.
- You MUST NOT raise `status:`. Status is a stage; the `reviewed:` block is an event.
- You MUST NOT write a definition into `.constitution/` at all — not the method glossary, not a guide.
- When the portrait cannot be drawn because a PRD has not settled what it must cover, say so and stop.
- Memlog: one per Product Component at `.control/memlog/<pc>.md`, plus `.control/memlog/spine.md` for
  `platform`, through `memlog.py --path`. `--workspace` MUST NOT be used.

## Output

Intents run · the catalogue and inventories as counts, per component · glossary terms written, proposed, and
rejected with the rule that rejected each · the `AD-N` that are new or changed · what was amended in the C4
set and what contradicted it · containers registered · plan-versus-code differences reported · whether the
roll-up regenerated and `wdi-review` ran · the one ranked batch of questions.
