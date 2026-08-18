---
status: Accepted
---

# Delivery Flow Guide

**Loaded when:** opening or closing a gate, opening or closing a wave, setting `mode` or
`risk_accepted`, and any time something already agreed has to change

This is the flow itself: five gates, the one knob that sets document depth, the one field that sets
review intensity, wave sizing, and what happens when a settled thing has to move. Every other guide
describes one document; this one describes the order they arrive in.

## Two fields, and the separation between them is the point

| Field | Where | Controls | Values | Default |
|---|---|---|---|---|
| `mode` | `index.yaml` (global) **and** `components.yaml` (per component) | **Document depth** — only this | `catalog` · `outline` · `guarded` · `deep` | `catalog` |
| `risk_accepted` | `components.yaml`, per component | **Review intensity**, and the risk-acceptance record | `low` · `medium` · `high` | proposed by the agent, confirmed by the owner |

Both belong to the owner. They MUST NOT be merged, and neither MUST be derived from the other.

Merging them makes one legitimate position unsayable: *"this part is risky, I know, and I manage it with
tests and review — not with prose."* If depth were controlled by `risk_accepted`, the only route to a
thin document would be raising `risk_accepted` — which means **lying in the risk record** to buy the
depth you wanted. Recording what is accepted is the entire reason that field exists.

Project size MUST NOT appear as an input anywhere. Size decides how many components there are, not how
deep each one goes.

### `mode` — two scopes, and the per-component one wins

| Scope | Where | Means |
|---|---|---|
| Global | `mode:` in `.control/registry/index.yaml` | The default for every component that does not state its own |
| Per component | `mode:` on the component's row in `components.yaml` | Wins over global. Written only where a component genuinely needs to differ |

Raising and lowering are both **free and need no justification** — it is a preference, and a preference
does not have to be defended.

**There is no third scope.** `mode` MUST NOT be overridden per wave or per `SPEC.md`. A wave MAY cross
several components, so a per-wave override would give one component two different depths depending on
which wave touched it — while the document is one, and living.

> Depth belongs to the component, not to the work.

### The four modes

Each contains everything in the one to its left. Value names are English in YAML **and in prose** — one
thing, one name.

| `mode` | What is written for that component, beyond the blueprint | G4 |
|---|---|---|
| `catalog` | Nothing. Code is written from the use case catalogue, the three inventories, and C4 | **skipped** |
| `outline` | Full flow for the use cases the component exists for — at most 3 · local business rules · `Decision Summary` + the `LC` list in the SDD | 20 min |
| `guarded` | + **`Failure Behaviour` for every boundary** · `Inherited Constraints` · third-party integration documents | 20 min |
| `deep` | + ABCE robustness analysis · a contract spec per endpoint · data dictionary · flow diagrams · state machines · branch scenarios | 30 min |

**A component at `mode: catalog` skips G4 entirely**, and that is what makes a global `catalog` genuinely
fast. Control does not disappear; it moves to G3, where the use cases, tables, endpoints, screens, domain
model, and C4 were all approved.

**`guarded` is the mode most often needed and most often absent.** It buys the single most expensive thing
to lose — the answer to *"what happens if this fails halfway"* for each boundary — without buying the
machinery around it. It stands without ABCE because the boundary list already exists: the API inventory
names the endpoints, the screen inventory names the screens.

Nine things `mode` never touches: the use case list, the API list, the table list, the screen list, the
domain model, the actor list, the spine, C4 L1/L2/L3, and cross-component business rules. All nine belong
to the blueprint at G3, so they exist even at `catalog`. The complete per-file manifest is in
`.constitution/method/why/artifact-map.md`.

**Lowering `mode` deletes nothing.** A file already written stops being required, and that is all.

**Raising `mode` on a component whose code already runs** produces an **as-built record**, not a design.
The evidence labels in `sdd-guide.md` are mandatory there.

### `risk_accepted` — review intensity, never depth

The direction is readable from the field name: `high` means *"I accept a lot of risk here"*, so its review
is the lightest.

`structure` and `prose` are the baseline everywhere. What `risk_accepted` decides is what is **added**:

| Value | Lenses on the documents | On the code |
|---|---|---|
| `low` | `structure` · `prose` · **`edge-case-hunter`** | a two-reviewer panel is **required** |
| `medium` | `structure` · `prose` · **`edge-case-hunter`** | — |
| `high` | `structure` · `prose` | — |

Review lenses are decided here and **nowhere else**. They MUST NOT be read off `mode`: one component MAY
sit at `mode: catalog` and still be reviewed the hardest.

Two things are not free, and `wdi-init` owns the conversation around both: `risk_accepted: high` on a
component touching money, personal data, an irreversible action, a contractual promise, or an
un-rollbackable integration requires a `DEC-` of `type: risk-acceptance` with `risk_accepted_by:` pointing
at it (V23) — and an outside party who will demand the artifacts as a deliverable puts the touched
component at `mode: deep` and `risk_accepted: low` whatever the global setting says.

## Five gates

A gate is named for **what is decided there**, never for the work that precedes it. Owner time is spent at
these five points only; between them the agents work alone.

| Gate | Decides | How often | Budget | Varies by `mode`? |
|---|---|---|---|---|
| **G1 Problem** | What the problem is, whose it is, why it earns work | once | 20' | no |
| **G2 Product** | What is built, and how it feels to use | once per PRD | 45' | no |
| **G3 Blueprint** | The whole portrait: which use cases, their entities, tables, endpoints, screens, and the invariants binding them | **once per product** | 45' | no |
| **G4 Component** | How one Product Component is built, and what the choice costs | **once per Product Component** | 20–30' | **yes — the only one** |
| **G5 Release** | Whether it is done and proven | once per wave | 10' | flags only |

**Only one gate changes shape with `mode`.** That is what makes this holdable in one head: four of the five
are always the same, whatever the setting.

The word "area" is not used anywhere. There is only Product Component.

### What is in the blueprint, and what is not

The most decisive boundary in the method. The previous run broke because "complete" was read as "fully
specified".

| In the blueprint — G3, once | Not in it — G4, per component |
|---|---|
| Actor list | Full UC flows |
| **Use case list**: one line per UC — id, title, actor, the `FR` it satisfies, `critical` | ABCE robustness analysis |
| Domain entities + relations + columns | Failure behaviour per boundary |
| **Table list**: one line per table plus its key columns | Data dictionary per column |
| **Endpoint list**: one line per endpoint | Five-lane contract spec per endpoint |
| **Screen list**: one line per screen | Field detail per form |
| **C4 L1 + L2 + L3** | Sequence and flow diagrams |
| Spine: `AD-N` only | State machines per entity |
| The error envelope and anything else cross-component | A component's local business rules |
| Business rules binding more than one component | Branch scenarios |

**Blueprint content is untouched by `mode` and by `risk_accepted`.** That is what keeps the order
non-circular: `mode` is first needed at G4, and it has been available since the tail of G2.

**G3 is written per component and gated once.** Both are true and it is not a compromise. The UC catalogue,
actors, and entities fall into each `<pc>`, so they parallelise with the component as the key. The gate is
one for the whole product, because its value is seeing the whole picture before choosing which component to
build. Gating per component means approving seven times, each time seeing a seventh of the picture.

Two blueprint contents cannot be per component: a per-component DB inventory is a lie because tables are
shared, and a per-component spine contradicts what a spine is.

**What is reviewed at G3 is the generated roll-up**, `.control/generated/blueprint.md`, not seven files. The
catalogue, actor list, and domain model stay in their component kernels as their permanent home; the roll-up
assembles them into one page to read. One fact, one home, one view.

### `critical` — narrowed, and it decides something only at `deep`

A use case is `critical` when it touches **money, personal data, or an irreversible action.** That is the
whole definition. The two elastic criteria — "the reason this component exists" and "expensive to discover
late" — are **repealed**, because with them every use case passed.

If the count exceeds a third of a component's use cases, the definition was misapplied: derive it again. It
MUST NOT be negotiated.

## Gate checklists

Each question is answered **yes / no / change**. One "no" on a ★ question holds the gate.

**On `mode: catalog`, only the ★ questions are asked** — fourteen across all five gates. The rest stay here
as material, and asking them is never wrong; requiring them is.

### G1 Problem · 20'

1. ★ Who experiences this problem, by name?
2. ★ What single number proves this worked, three months from now?
3. If we do not build it, what breaks or is lost?
4. Who wins and who loses if this ships?
5. What is the most fragile assumption here, and what does being wrong cost?
6. What are we deliberately **not** doing?
7. Is there a cheaper way to the same outcome?

### G2 Product · 45'

1. ★ For each `FR`: without it, can the user still finish their job? (yes → defer or drop)
2. ★ Does every `FR` have a proof of done, in a sentence I understand?
3. ★ Does this still make sense released on its own?
4. Do the `NFR` numbers come from reality or from feeling?
5. Can I retell the main UX flow in five sentences without opening the document?
6. Which `FR` touch money, personal data, or the client's reputation?
7. What changed from what I approved at G1, and why?

### G3 Blueprint · 45'

Read against `.control/generated/blueprint.md`, not against seven files.

1. ★ Is every use case title a sentence a user would say, not a system term?
2. ★ Any `FR` with no use case? (the validator answers this, not an opinion)
3. ★ Do the three inventories and the use case catalogue describe one system — nothing promised with
   nowhere to live, nothing listed that nothing promised?
4. Actor list: is one missing, or are two actually the same person?
5. Does every `AD-N` name the concrete failure it prevents, and would breaking it in one component break
   another?
6. Which business rule am I not sure is right, and who at the client can confirm it?
7. Is there still a term I have to guess the meaning of?

### G4 Component · 20–30'

Skipped entirely at `mode: catalog`.

1. ★ What is being staked in this component — and does `risk_accepted` say so out loud?
2. ★ From `guarded` up: which boundary still has no answer for "the other side is slow, absent, or lying"?
3. ★ What stops us starting tomorrow? (MUST be empty)
4. ★ Validators green **and** the review leaving no open finding? (both — one is fact, one is judgement)
5. Does any choice here lock us to one vendor or technology for more than a year?
6. From the DAG: which story blocks the most other stories?
7. Top risk: who owns it, and what is the pivot trigger to turn or give up?

### G5 Release · 10'

1. ★ Is every RTM row for this wave green?
2. ★ Is every story's acceptance criteria proven by a test, not by an agent's statement?
3. What was dropped from the plan, and where is it recorded?
4. Are new risks found while building in the Risk Register?
5. What one thing made this wave take longer than expected?
6. What does the client need to know before this goes live?
7. What is watched in the first week?

## Units of work — `FR`, wave, `SPEC`, story

| Unit | Is | Lifetime |
|---|---|---|
| `FR-N` | One **feature** — one promise to a user. Born at G2 | permanent, lives across releases |
| wave | One **unit of work**. Opens at G4 or G5, closes at G5 | one slice of work |
| `SPEC.md` | The machine contract for **one wave**. A projection of `.what/` + `.how/`, and MUST NOT contain anything new | one wave |
| story | One piece taken by one builder to a green PR | one wave |

**One wave = one `SPEC` = one tracker Task.** One to one to one, with no compound joins.

A wave's scope is flexible and **ideally one `FR`**, because an `FR` is human-testable from birth — it has a
proof of done. One `FR` MAY span several waves, one wave MAY carry several small neighbouring `FR`, and a
wave MAY be a standalone slice of one large `FR`.

A wave MAY cross several Product Components. One condition: **G4 has passed for every component the wave
touches**, or that component is at `mode: catalog`, whose G4 is skipped by design (V22). That is why G4 and
the wave are deliberately different units — G4 decides *how one component is built*, a wave decides *which
work happens now*.

`SPEC.md` and story files **are not read by humans.** Both are machine contracts, and no review burden MAY
be moved onto them. The human review surface stops at the PRD, `.what/`, and `.how/`.

### Mapping to a tracker

| Jira | WDI | Lifetime |
|---|---|---|
| Epic | Product Component | permanent — an Epic never closes |
| Task | **wave = `SPEC.md`** | one wave |
| Sub-task | story | one wave |
| Fix Version | release | one release |
| Label / custom field | the `CAP-N` and `FR-N` the wave satisfies | — |
| — a document, not an issue | `.what/` · `.how/` · `SPEC.md` | — |

**`FR` is not a Task.** It sits at the level of *promise*, not of *work*: one `FR` MAY be delivered by
stories in two waves, and one story MAY satisfy part of two `FR`. Mapping promise onto work-issue forces a
1:1 that does not exist, and produces Tasks opened at G2 that hang across releases. `FR` travels as a label
on the Task.

**The corpus stays the source of truth; the tracker is a view.** Story status is read from story-file
frontmatter, never copied into two places.

**Parallelism.** Between stories through the `depends_on` and `touches` DAG; between waves through
`depends_on` at wave level. A wave that declares no dependency runs in parallel.

## Wave size, and what it does not decide

| Size | Shape | Effect |
|---|---|---|
| **S** | ≤3 stories, no new `FR` | G4 and G5 merge into one 20-minute session |
| **M** | 4–12 stories | as usual |
| **L** | >12 stories, or a new container | the retrospective runs |

Size is recorded in `waves.yaml`. It MAY be raised mid-flight; it MUST NOT be lowered.

**Size does not choose which gates are active** — that is `mode`'s job. It only governs session merging and
whether the retrospective is required.

**Fast Path** skips every gate. It is available for a fix that changes no `FR`, `UC`, `AD-N`, or domain
model, is at most one story, and touches no money, personal data, or third-party integration. If an `FR`
turns out to be touched, work MUST stop and become a wave `S`.

## Story-closing checklist — three items

Answered as each story finishes, before the next is picked up.

1. A decision worth remembering? → `wdi-decision`. A story that contradicts an `AD-N` **stops** rather than
   closing; that is the one case where recording is mandatory.
2. A trap for the next agent? → recorded where the next agent will read it.
3. Test names matching what `waves.yaml` records?

Five items left this list and did not disappear — they moved to **wave close**, where the information is
actually available: `LC` registration (V12), the `touches` check, SPEC companion distillation, and the
structure-map refresh. Registering an `LC` before a story was `ready-for-dev` demanded the answer at the
moment it was thinnest.

## When something settled has to change

One trigger: **an artifact other people agreed to needs to change.** Run this matrix and reopen the gates it
names.

| What changes | MUST be re-reviewed | Gate reopened |
|---|---|---|
| Business Goal | The whole chain beneath it | G1 |
| `FR` — its **promise** | Related `UC`, decisions naming it, stories not yet `in-progress`, RTM rows | G2 then G3 |
| `FR` — its **wording** only | Nothing. The skill at work fixes it, one Revision History row per pass | none |
| `NFR` | Its enforcing decisions and tests | G4 |
| UX flow | Related use case specifications, stories not yet `in-progress` | G3 |
| Business rule | `UC` using it, related tests | G3 for a cross-component rule, G4 for a local one |
| An `AD-N` | Affected C4 components, stories not yet `in-progress` | G4 |
| Story acceptance criteria | That story's tests, its RTM row | none — the row going green again is enough |

The promise-versus-wording split is owned by `prd-guide.md` and MUST NOT be re-decided here.

- A story already `in-progress` MUST NOT have its contract changed. Stop it, return it to `ready-for-dev`,
  then change it.
- Superseded artifacts are never deleted. Their status becomes `superseded` and points at the replacement.
- A change that cancels more than 30% of a wave's stories MUST go through `wdi-decision`, which wraps
  `bmad-correct-course`, rather than being patched.

**A new PRD arriving after G3 amends the blueprint; it does not repeat it.** The new components are born,
their rows join the catalogue and the three inventories, and **G3 reopens over the delta only**. The
45-minute session does not run again for one additional initiative.

## Roles

| Role | Does | Does not |
|---|---|---|
| Product Owner | Answers the checklists, decides at the five gates, sets `mode` and `risk_accepted`, owns risk | Write artifacts, read machine contracts |
| Agent at G1–G3 | Writes the brief, the PRD, and the blueprint | Decide depth or accept risk |
| Agent at G4 | Writes one component's behaviour and mechanism | Write code |
| Builder | One story through to a green PR | Change `.what/`, `.how/`, or an `applied` decision |
| Review panel | Two different CLI families, neither the builder's | Give a final verdict — findings are adjudicated by the coordinator |

Panel composition and CLI/model selection are governed by the global Agent Rules and MUST NOT be restated
here.
