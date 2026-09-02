---
name: wdi-component
description: Use at G4 Component — the depth of one Product Component, as deep as that component's mode and no deeper. Two intents, behaviour and design. Owns .what/<pc>/ slots 02-05 and .how/<pc>/ minus 01-ux. Skipped entirely at mode catalog.
---

# WDI Component

G4 decides **how one Product Component is built, and what the choice costs.** It is the only gate that changes
shape with `mode`, and the only one that runs more than once for a reason other than a new PRD.

| `mode` | This skill |
|---|---|
| `catalog` | **Not run. G4 is skipped.** |
| `outline` | `behaviour` + `design` **as far as § Structure**, and no further |
| `guarded` | `behaviour` + `design` |
| `deep` | `behaviour` + `design` |

This table said `outline` → `behaviour` only until 2026-08-18. It contradicted **Step 4 of this same
skill**, which starts `Decision Summary` and `Structure` "from `outline`", and it contradicted
`delivery-flow-guide.md`, which owns the mapping and lists both for `outline`. Read literally, it would
have left every `outline` component with an SDD that is a template skeleton forever — and `review-trace` would have
been right to keep flagging it.

Read the component's `mode` from its row in `components.yaml`, falling back to `mode:` in `index.yaml`. Read
its `risk_accepted` from the same row; it decides the review lenses and nothing else.

**You MUST NOT write more than the component's `mode` demands.** Writing a section the mode does not ask for is
the failure this gate was rebuilt to stop — it is how 41 of 56 use cases ended up marked `critical` and how the
previous run stalled. Depth is a preference the owner set, and exceeding it is not diligence.

Stage-3 and Stage-4 work were two skills before and are one now, because they are one gate. The boundary
between them is intact and it is **horizontal**: `behaviour` writes what the system does, `design` writes how.

## Inputs

| Source | What it answers |
|---|---|
| `.control/registry/components.yaml` | This component's `mode`, `risk_accepted`, `risk_note`, `owns` |
| `.what/<pc>/SRS-<pc>.md` § UC Catalogue · § Actor Register | Which use cases exist, and which are `critical` |
| `.what/_prd/*/prd.md` | The `FR` this component has to make true |
| `.what/business-rules.md` | Rules that already bind more than one component |
| `.how/_platform/inventory-api.md` · `inventory-screen.md` | **The boundary list.** It is already derived; do not derive it again |
| `.how/_platform/ARCHITECTURE-SPINE.md` | Every `AD-N` that binds this component |
| `.how/_platform/cross-cutting.md` | The error envelope, and anything else decided once |
| `.control/decisions/` | `applied` decisions this must not contradict |
| `.constitution/method/document/srs-guide.md` · `sdd-guide.md` | The rules the result is checked against |
| `src/` · `web/` | Only as evidence when the code already exists. Never as a substitute for the SRS |

## Step 1 — Scope, one component

State it in one line before doing anything. A pass MUST NOT write content for several components: an SDD is per
component by construction, and one pass over two of them inherits the wrong constraints.

| Ask | Scope |
|---|---|
| "Take `<pc>` to G4" | One component, both intents as its `mode` demands |
| "Write the failure behaviour for `<pc>`" | One section of one component |
| "Is our design consistent?" | Read-only across components — that is `wdi-reconcile`. Route there |

## Step 2 — Preconditions

None of these are yours to create.

| Check | When it fails |
|---|---|
| The component is registered with `mode` and `risk_accepted` set | Route to `wdi-init` intents `component`, `mode`, `risk` |
| Its `mode` is not `catalog` | Stop. G4 is skipped, and the work goes straight to `wdi-build` |
| G3 has passed | Route to `wdi-blueprint`. Depth written against a moving portrait is rewritten |
| The spine exists and its `AD-N` are readable | Route to `wdi-blueprint`. You MUST NOT write the spine |
| For `design`: the container this component runs in is registered | Route to `wdi-blueprint`. G3 has passed by now, so the answer exists — an `LC` written here MUST carry it. Only a screen `LC` born at G2 is allowed an empty one, and G3 fills it |

## Step 3 — Intent `behaviour`

Writes `.what/<pc>/`, slots `02`–`05`. You MUST NOT write solution shape: no framework, no table, no endpoint,
no class, no queue, no file path.

| `mode` | Written |
|---|---|
| `outline` · `guarded` | Full flows for the use cases the component exists for, **at most 3**, in `04-usecases/UC-<n>-<slug>.md` · local business rules in `02-rules/rules-<pc>.md` |
| `deep` | + a full flow for **every** `critical` use case · `03-domain/state-machines.md` · `05-scenarios/SCN-<nn>-<slug>.md` |

A flow is at most **eight steps**. A flow needing more is either two use cases or has started describing
implementation, and the cap is what makes that visible while it is still cheap to fix. Branches go to
`05-scenarios/` — at `deep` only — never into a fatter UC file.

A rule that turns out to bind a second component MUST be **promoted** to `.what/business-rules.md` through
`wdi-blueprint`, not copied. Two copies of one rule is how components start disagreeing about the same policy.

## Step 4 — Intent `design`

Writes `.how/<pc>/`. Two carve-outs that are not negotiable: `01-ux/` belongs to `wdi-ux`, and all of
`.how/_platform/` belongs to `wdi-blueprint`. You MUST NOT write into either.

Write in this order, stopping at whatever the `mode` does not reach:

1. **`Decision Summary`** — from `outline`. One page: what this component is built as, and the one or two most
   expensive choices reversed.
2. **`Structure`** — from `outline`. The `LC` list and the direction of their dependencies.
3. **`Inherited Constraints`** — from `guarded`. Every `AD-N` reaching this component, **quoted verbatim**. A
   paraphrase drifts, and the drift is invisible because both texts read reasonably. A design that must deviate
   does not argue here: it goes to `wdi-decision`, and either the spine changes or the design does.
4. **`Failure Behaviour`** — from `guarded`, for **every** boundary. The boundary list is the endpoints and
   screens this component owns in the two platform inventories. Per boundary: what happens when the other side
   is slow, absent, or lying — timeout, retry policy, what the user sees, what gets logged. "Returns an error"
   is not an answer.
5. **`03-integrations/<name>.md`** — from `guarded`, when the component has a third party. It MUST name the
   owner outside the team, and what happens when they change it without telling anyone.
6. **The ABCE pass** — `deep` only, in order: Boundary → Control → Entity → Behaviour. It MUST NOT have
   appeared in the SRS, and below `deep` it MUST NOT be written at all.
7. **`02-contracts/`, `04-components/`, `05-model/data-model.md`, `06-flows/`** — `deep` only. The contract
   inventory comes first and specs carry its stable numbers; every spec answers all five lanes, with `none` and
   a reason where one does not apply. The data model carries a dictionary beside its diagram.

From `guarded` up, every Boundary object MUST become an `LC` in `components.yaml`; at `deep`, Control objects
too. Registration is checked **when the spec closes** — `lc-registered` — not before a ticket is picked up. You MUST
NOT register a `container`, and you MUST NOT register `ui-screen` or `ui-composite`.

## Step 5 — Evidence, and the as-built case

Every technical claim about code that already exists MUST name what was read. The four labels — `[ASSUMED]` ·
`[PARTIAL]` · `[NEEDS CONFIRMATION]` · `[MISSING]` — are mandatory, and their ladder rules are in
`sdd-guide.md`.

**Raising a component's `mode` after its code runs is the case this matters most for.** What you write then is
an **as-built record, not a design**, and you MUST NOT raise a claim to verified without naming the file that
proves it. Two labels MUST be acted on rather than left in the text:

- `[NEEDS CONFIRMATION]` → `wdi-question`, before G4 opens.
- `[MISSING]` → dispositioned as a `BUG-`, a correction, or planned work. It MUST NOT be deleted; the
  sentence is the only surviving evidence that somebody once believed the thing existed.

## Step 6 — Drift

Check against the layer above and the code below, and **report** — never edit the other side.

| Found | Where it goes |
|---|---|
| Depth needs behaviour the catalogue never listed | `wdi-blueprint` — into the catalogue, before any code |
| The catalogue promised behaviour this component cannot deliver | `wdi-product`. Do not quietly narrow it here |
| A contradiction with an `applied` decision or an `AD-N` | `wdi-decision` — a new `DEC-`, never an edit to one already applied |
| A decision that would bind a second component | `wdi-blueprint` — it is an `AD-N`, not an SDD paragraph |
| The code does something this document does not describe | Here, as a labelled claim, or as a `BUG-` when the code is wrong |

`wdi-reconcile` is the read-only sweep across all layers. Run it rather than reimplementing it.

## Step 7 — Review

No `doc_standards` fires for an SRS or an SDD. Dispatch `wdi-review`, which reads the lens set from this
component's `risk_accepted` — `edge-case-hunter` at `low` and `medium`, `structure` + `prose` at `high`, plus a
two-reviewer code panel at `low`. Slots are part of the artifact; reviewing a kernel alone misses where the
branches and contracts live.

You MUST NOT open G4 on depth that has not been through it.

## Rules

- A decision taken while writing is **written into the document as its own content**, stated as what now
  holds. Never as a parenthetical aside — there is no memlog here to catch one. It goes to `wdi-decision`
  only when no design document has a home for it, or it touches an `AD-N`; `decision-guide.md` § A
  decision's first home owns that split.
- You MUST NOT write into `.what/_prd/`, `.what/business-rules.md`, `.how/_platform/`, or `.how/<pc>/01-ux/`.
- You MUST NOT raise `status:`. Status is a stage; the `reviewed:` block is an event.
- You MUST NOT lower or raise the component's `mode` to fit what you want to write. That is `wdi-init`, and it
  is the owner's call.
- The spec's contract is cut **after** this, never before, and it MUST NOT introduce anything these documents do not say.
- Memlog: `.control/memlog/<pc>.md`, through `memlog.py --path`. `--workspace` MUST NOT be used.
- Questions arrive as **one** ranked batch at the gate, not as they surface.

## Output

Component and its `mode` and `risk_accepted` · which intents ran · what was written per slot and **what the
mode deliberately left unwritten** · the `AD-N` inherited · the `LC` registered and their types · evidence
labels outstanding by kind · drift found and where it was routed · whether `wdi-review` ran · the one ranked
batch of questions.
