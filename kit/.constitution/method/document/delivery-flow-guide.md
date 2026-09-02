---
status: Accepted
---

# Delivery Flow Guide

**Loaded when:** opening or closing a gate, opening or closing a spec, setting `mode` or
`risk_accepted`, and any time something already agreed has to change

This is the flow itself: five gates, the one knob that sets document depth, the one field that sets
review intensity, spec sizing, and what happens when a settled thing has to move. Every other guide
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

All twelve combinations of the two are legal, and what each one costs is laid out side by side in
`.constitution/method/why/mode-risk-map.md`. It explains and MUST NOT be cited as a rule — this guide is
where both fields are defined.

### `mode` — two scopes, and the per-component one wins

| Scope | Where | Means |
|---|---|---|
| Global | `mode:` in `.control/registry/index.yaml` | The default for every component that does not state its own |
| Per component | `mode:` on the component's row in `components.yaml` | Wins over global. Written only where a component genuinely needs to differ |

Raising and lowering are both **free and need no justification** — it is a preference, and a preference
does not have to be defended.

**There is no third scope.** `mode` MUST NOT be overridden per spec or per `SPEC.md`. A spec MAY cross
several components, so a per-spec override would give one component two different depths depending on
which spec touched it — while the document is one, and living.

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

| Value | First review, and the review before a gate | Every re-review after | On the code |
|---|---|---|---|
| `low` | `structure` · `prose` · **`edge-case-hunter`** | `structure` · `prose` | a two-reviewer panel is **required** |
| `medium` | `structure` · `prose` · **`edge-case-hunter`** | `structure` · `prose` | — |
| `high` | `structure` · `prose` | `structure` · `prose` | — |

The heavy lens is bought **once per artifact and once per gate**, not once per edit. A re-review MUST put
it back when the delta touches money, personal data, an irreversible action, or a third party. And a
review trace has to be fresh **at a gate and at spec close** — between those points a stale trace is
advisory, not a failure. `wdi-review` owns the mechanics of both, including the one case where re-stamping
without re-running is allowed: a change to wording only.

Review lenses are decided here and **nowhere else**. They MUST NOT be read off `mode`: one component MAY
sit at `mode: catalog` and still be reviewed the hardest.

Two things are not free, and `wdi-init` owns the conversation around both: `risk_accepted: high` on a
component touching money, personal data, an irreversible action, a contractual promise, or an
un-rollbackable integration requires a named acceptance in `risk_accepted_by` — a person and a date,
written beside the risk (`high-risk-named`) — and an outside party who will demand the artifacts as a deliverable puts
the touched component at `mode: deep` and `risk_accepted: low` whatever the global setting says.

## Five gates

A gate is named for **what is decided there**, never for the work that precedes it. Owner time is spent at
these five points only; between them the agents work alone.

| Gate | Decides | How often | Budget | The session itself | Its checklist |
|---|---|---|---|---|---|
| **G1 Problem** | What the problem is, whose it is, why it earns work | once | 20' | unchanged | 2 of 7 at `catalog` |
| **G2 Product** | What is built, and how it feels to use | once per PRD | 45' | unchanged | 3 of 7 at `catalog` |
| **G3 Blueprint** | The whole portrait: which use cases, their entities, tables, endpoints, screens, and the invariants binding them | **once per product** | 45' | unchanged | 3 of 7 at `catalog` |
| **G4 Component** | How one Product Component is built, and what the choice costs | **once per Product Component** | 20–30' | **skipped entirely at `catalog`** | 4 of 7, and 30' at `deep` |
| **G5 Release** | Whether it is done and proven | once per spec | 10' | unchanged | 2 of 7 at `catalog` |

Two different things move, and reading them as one is what makes this table easy to get wrong:

- **What a gate decides, how often it runs, and its budget never change.** All five, at every setting.
- **G4 is the only gate that can disappear.** At `catalog` its session does not happen at all; the other four
  always run.
- **Checklist length is the one thing `mode` shortens everywhere.** At `catalog` only the ★ questions are
  required, at G1 and G5 as much as at G4 — see the checklists below.

That is what makes this holdable in one head: four of the five sessions are always there, and the only
question is how long their checklist is.

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

**What is reviewed at G3 is the generated roll-up**, `.how-rendered/blueprint.md`, not seven files. The
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

**On `mode: catalog`, only the ★ questions are required.** There are fourteen ★ across the five gates, but
four of them belong to G4 — which `catalog` skips — so what actually gets asked there is **ten**. The rest
stay here as material, and asking them is never wrong; requiring them is.

Which `mode` the rule reads depends on the gate. **G1 and G2 can only read the global `mode`**, because no
component exists yet and `risk_accepted` has no value at all until `wdi-init` intent `component` runs at the
tail of G2. G4 reads the `mode` of the component in front of it.

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

Read against `.how-rendered/blueprint.md`, not against seven files — every one of the seven questions below is answerable from that page.

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
6. From the DAG: which ticket blocks the most other tickets?
7. Top risk: who owns it, and what is the pivot trigger to turn or give up?

### G5 Release · 10'

1. ★ Is every RTM row for this spec green?
2. ★ Is every ticket's acceptance criteria proven by a test, not by an agent's statement?
3. What was dropped from the plan, and where is it recorded?
4. Are new risks found while building in the Risk Register?
5. What one thing made this spec take longer than expected?
6. What does the client need to know before this goes live?
7. What is watched in the first week?

## Units of work — `FR`, spec, `SPEC`, ticket

| Unit | Is | Lifetime |
|---|---|---|
| `FR-N` | One **feature** — one promise to a user. Born at G2 | permanent, lives across releases |
| spec | One **unit of work**: the tickets that reach one outcome. Opens at G4 or G5, closes at G5 | one slice of work |
| `SPEC.md` | The **document** of one spec: a projection of `.what/` + `.how/` that MUST NOT contain anything new. **Not written at size `S`** | one spec |
| ticket | One **tracer-bullet vertical slice**: complete through every layer, verifiable on its own, sized to one fresh context window, carrying the tickets that block it | one spec |

**One spec = one set of tickets = one parent issue.** One to one to one, with no compound joins. `SPEC.md`
joins that identity from size `M` up; at `S` there is no document and **the tickets are the contract.**

A spec's scope is flexible and **ideally one `FR`**, because an `FR` is human-testable from birth — it has a
proof of done. One `FR` MAY span several specs, one spec MAY carry several small neighbouring `FR`, and a
spec MAY be a standalone slice of one large `FR`.

A spec MAY cross several Product Components. One condition: **G4 has passed for every component the spec
touches**, or that component is at `mode: catalog`, whose G4 is skipped by design (`spec-after-g4`). That is why G4 and
the spec are deliberately different units — G4 decides *how one component is built*, a spec decides *which
work happens now*.

A ticket is **vertical, never horizontal**: it cuts a narrow but complete path through schema, API, UI, and
tests, and a finished one is demoable on its own. A slice of one layer is not a ticket. **The one exception
is a wide refactor** — a mechanical change whose blast radius breaks call sites everywhere at once, where no
vertical slice can land green. That is sequenced **expand → migrate in batches → contract**, each batch its
own ticket blocked by the expand, and the contract blocked by every batch.

`SPEC.md` and ticket files **are not read by humans.** Both are machine contracts, and no review burden MAY
be moved onto them. The human review surface stops at the PRD, `.what/`, and `.how/`.

### Mapping to a tracker

| Tracker | WDI | Lifetime |
|---|---|---|
| **Parent issue** | **spec** | one spec |
| **Issue, carrying native blocking edges** | **ticket** | one spec |
| Fix Version | release | one release |
| Label / custom field | the `CAP-N` and `FR-N` the spec satisfies | — |
| — a document, not an issue | `.what/` · `.how/` · `SPEC.md` | — |

A ticket is an **issue**, not a sub-task, because its blocking edges are what make the frontier visible in
the tracker's own UI — the set of tickets whose blockers are all closed, and therefore takeable now. A
sub-task cannot carry that relation.

**`FR` is not an issue.** It sits at the level of *promise*, not of *work*: one `FR` MAY be delivered by
tickets in two specs, and one ticket MAY satisfy part of two `FR`. Mapping promise onto work-issue forces a
1:1 that does not exist, and produces issues opened at G2 that hang across releases. `FR` travels as a label.

**The corpus stays the source of truth; the tracker is a view.** Ticket status is read from **the ticket
itself**, never copied into two places — and `specs.yaml` holds the **index**, not the bodies: one row per
ticket with `satisfies`, `blocked_by`, `touches`, and its test names. That is what RTM and the validators
read; the ticket's prose stays where the tracker put it.

**Two edge fields, and the difference is not cosmetic.** A spec `depends_on` another spec — an ordering
between units of delivery. A ticket is `blocked_by` other tickets, which is the word the tracker uses for
the same relation and the field the frontier is read from. `no-cycles` walks both graphs; `parallel-tickets-blocked` reads the ticket one.

**Where a ticket lives, and what it is called.** `{spec_folder}/issues/<NN>-<slug>.md`. Only the root is
ours: the folder, the numbering from `01` in dependency order, and the file's shape belong to the engine
that writes them. A ticket's `id` in `specs.yaml` is `<spec-id>-<NN>` — `SPEC-3-01` — because the engine's
number is unique only inside one spec and the RTM needs a key that is unique across the corpus. `ticket-status-one-home` finds
the file from the number at the tail of the id.

**Parallelism.** Between tickets through their blocking edges plus the `touches` check; between specs
through `depends_on` at spec level. A spec that declares no dependency runs in parallel.

## Spec size, and what it does not decide

| Size | Shape | Effect |
|---|---|---|
| **S** | ≤3 tickets, no new `FR` | G4 and G5 merge into one 20-minute session · **`SPEC.md` is not written** — the tickets are the contract |
| **M** | 4–12 tickets | `SPEC.md` written first, because the seams and the testing decisions have to be settled before tickets are cut |
| **L** | >12 tickets, or a new container | as `M`. Its one distinct effect was the retrospective, which is retired, and `V19` with it |

Size is recorded in `specs.yaml`. It MAY be raised mid-flight; it MUST NOT be lowered.

**Size does not choose which gates are active** — that is `mode`'s job. It decides two things: whether G4
and G5 merge into one session (`S`), and whether `SPEC.md` is written at all (`M` and up).

**Fast Path** skips every gate. It is available for a fix that changes no `FR`, `UC`, `AD-N`, or domain
model, is at most one ticket, and touches no money, personal data, or third-party integration. If an `FR`
turns out to be touched, work MUST stop and become a spec `S`.

## Ticket-closing checklist — three items

Answered as each ticket finishes, before the next is picked up.

1. Something the next person needs to know? → **into the document that carries it**, and that is almost
   always where it ends. It reaches `wdi-decision` only when no design document has a home for it —
   `decision-guide.md` § A decision's first home. A ticket contradicting an `AD-N` **stops** rather than
   closing; that is the one case where recording is mandatory.
2. A trap for the next agent? → recorded where the next agent will read it.
3. Test names matching what `specs.yaml` records?

Five items left this list and did not disappear — they moved to **spec close**, where the information is
actually available: `LC` registration (`lc-registered`), the `touches` check, SPEC companion distillation, and the
structure-map refresh. Registering an `LC` before a ticket was `ready-for-agent` demanded the answer at the
moment it was thinnest.

## When something settled has to change

One trigger: **an artifact other people agreed to needs to change.** Run this matrix and reopen the gates it
names.

**Reopening a gate means re-deciding, not re-recording.** The column below names the gate whose *decision*
the change invalidates — the session runs again because the answer might now be different. Where the chain
changes but the decision does not, the documents are **edited in place** and no gate opens or closes. There
is no ceremony to perform, and nothing anywhere records that the change arrived late: the commit does that,
and it does it better than a paragraph.

**A change that arrives during G5 is written as if it had been there from the start.** Present tense, folded
in, not appended and not annotated — `corpus-guide.md` § The corpus is written in the present tense owns
that rule and it is not softened here.

| What changes | MUST be re-reviewed | Gate reopened |
|---|---|---|
| Business Goal | The whole chain beneath it | G1 |
| `FR` — its **promise** | Related `UC`, decisions naming it, tickets not yet started, RTM rows | G2 then G3 |
| `FR` — its **wording** only | Nothing. The skill at work fixes it, one Revision History row per pass | none |
| `NFR` | Its enforcing decisions and tests | G4 |
| UX flow | Related use case specifications, tickets not yet started | G3 |
| Business rule | `UC` using it, related tests | G3 for a cross-component rule, G4 for a local one |
| An `AD-N` | Affected C4 components, tickets not yet started | G4 |
| Ticket acceptance criteria | That ticket's tests, its RTM row | none — the row going green again is enough |

The promise-versus-wording split is owned by `prd-guide.md` and MUST NOT be re-decided here.

**Once the owner has decided, the survey is spent.** The agent reads the chain — `BG`, `CAP`, `FR`, `UC`,
the rules, the `AD-N` — and says **once**, in one place, what the change breaks and what it costs. That is
the warning, and the owner is entitled to it. When they choose anyway, what the survey found becomes
**edits**: not findings, not `OQ-` rows, not a review, and not a second pass raising the same conflicts in
different words. Re-arguing a decision the owner already took is the most expensive thing an agent does in
this method, and it buys nothing that the first warning did not already buy.

The one thing that still stops rather than warns: a change contradicting an `AD-N`. That is an invariant the
architecture rests on, `decision-guide.md` owns it, and the stop is a `DEC-` — one page, then proceed.

- A ticket already **started** MUST NOT have its contract changed. Stop it, return it to
  `ready-for-agent`, then change it.
- Superseded artifacts are never deleted. Their status becomes `superseded` and points at the replacement.
- A change that cancels more than 30% of a spec's tickets MUST go through `wdi-decision`, which wraps
  `bmad-correct-course`, rather than being patched.

**A reopened gate reopens over the DELTA, always.** Never the whole session, and never the whole
checklist — only the questions the change actually put back in play. The budgets in the gate table are
for a gate's **first** run; a reopening costs what the delta costs and usually far less.

This was already true for one case and was never generalised: a new PRD arriving after G3 amends the
blueprint rather than repeating it — the new components are born, their rows join the catalogue and the
three inventories, and G3 reopens over the delta only. One feature added during G5 is the same shape. It
puts its own `FR` and `UC` back in play and nothing else, so it costs a few minutes, not ninety.

## Roles

| Role | Does | Does not |
|---|---|---|
| Product Owner | Answers the checklists, decides at the five gates, sets `mode` and `risk_accepted`, owns risk | Write artifacts, read machine contracts |
| Agent at G1–G3 | Writes the brief, the PRD, and the blueprint | Decide depth or accept risk |
| Agent at G4 | Writes one component's behaviour and mechanism | Write code |
| Builder | One ticket through to a green PR | Change `.what/`, `.how/`, or an `applied` decision |
| Review panel | Reviews the diff independently of the builder | Give a final verdict — findings are adjudicated by the coordinator |

Panel composition and CLI/model selection are governed by the global Agent Rules and MUST NOT be restated
here.
