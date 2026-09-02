---
status: Accepted
---

# Architecture Guide

**Loaded when:** writing or changing the architecture spine, an `AD-N`, or the C4 set

The spine holds the invariants that stop separately built components from diverging. It is not a design
document — one component's design is its `SDD-<pc>.md`. If a statement only affects one component, it does
not belong here.

The spine, the C4 set, `cross-cutting.md`, and the three inventories are all **G3 Blueprint** output, written
by `wdi-blueprint` intent `platform`. All of them exist at every `mode`, including `catalog`: they belong to
the blueprint, and the blueprint is not touched by the depth knob.

## Home

`.how/_platform/ARCHITECTURE-SPINE.md` — a file directly in `_platform/`. The `architecture/` sub-folder is
**repealed**; one file does not earn a folder, and the extra level made the spine harder to find than the
things it constrains.

## Invariants only

An entry earns a place when breaking it in one component would break another. Everything else is a **seed**:
useful as a starting point, not binding.

| Kind of statement | Spine? |
|---|---|
| "Every service authenticates through the same token format" | Yes — invariant |
| "Money is stored as integer minor units, never float" | Yes — invariant |
| "We use version 11 of our database and version 1.23 of our language" | No — seed. It informs, it does not forbid |
| "The repo is laid out as one folder per deployable" | No — seed, and `structure-codebase.md` describes it |
| "The member portal caches its dashboard for 60 seconds" | No — one component's design |

Stack, tree shape, and data shapes are seeds and MUST be marked as such. Writing them as contracts makes the
spine wrong the first time anything is upgraded, and a spine that is wrong in a visible place stops being
read in the places where it is right.

## Every `AD-N` carries three things

| Field | States |
|---|---|
| **Binds** | Which components or containers this holds for. "All" is a valid answer and MUST be written, not left blank |
| **Prevents** | The concrete failure this exists to stop. Written as the thing going wrong, not as a principle |
| **Rule** | One sentence, quotable, checkable. If a reviewer cannot tell whether code obeys it, it is not a rule yet |

An `AD-N` with no **Prevents** is a preference. Preferences belong in
`.constitution/project/codebase-conventions-guide.md`, where nothing has to justify itself.

## The spine stops being touched every ticket

This is the change that ends the tax that was being paid before the information existed.

- **The spine holds invariants and nothing else.** It changes only when an `AD-N` is born or reversed, and
  both are decision events. For a mid-sized product: once at the start, around 6–10 `AD-N`, then almost
  never.
- **A ticket MUST NOT touch the spine.** A ticket that contradicts an `AD-N` **stops** and opens a `DEC-` —
  the one case where recording a decision is still mandatory.
- **Editing an `AD-N` MUST NOT quietly reverse it.** A reversal is a decision, and it goes through
  `wdi-decision` first.
- **An inventory is not the spine.** The three inventories are living registers, derived from code once code
  exists. A plan-versus-reality difference is a validator finding, not a spine amendment.

## `AD-N` versus `DEC-NNN`

`AD-N` is a **living rule**, edited in place as understanding improves. `DEC-NNN` is a **decision event**,
never edited once `applied`, only superseded.

An `AD-N` usually has a `DEC-` behind it: the invariant is what people obey, the decision record is why it
exists and what it cost. The full comparison is in `decision-guide.md` and MUST NOT be restated here.

The spine MUST NOT name a decision's alternatives or its cost. Those live in the `DEC-` behind it; repeating
them here creates a second version that will drift.

## The C4 set, and what else a run produces

`bmad-architecture` runs at **initiative** altitude for the spine. Anything else the run produces at feature
altitude — a deck, a fuller solution document — is a **rendering**, not the spine, and the two MUST NOT be
confused:

| Rendering | Has a slot | What follows |
|---|---|---|
| The **C4 set** — L1, L2, and one L3 per `built: true` container **holding more than one Product Component** | Yes: `.how/_platform/c4-l1-system-context.md` · `c4-l2-containers.md` · `c4-l3-<container>.md` | `wdi-blueprint` lands it, amending rather than overwriting. Once landed it is corpus, and `c4-l2-containers.md` **owns** the container list. The next section owns what a container *is* |
| Deck, solution document, anything else | No | Stays in the run folder, cited by path, never promoted |

**Placement is what makes a C4 binding, and only for what its level owns.** Before placement it is one run's
drawing; after, it is the corpus's description of the system. The spine still wins on any invariant, because
the C4 set describes and the spine forbids. A C4 file MUST NOT be used to justify a rule; a rule that matters
belongs in an `AD-N`.

The C4 set is **living**. It is amended when a container is added or changed — it MUST NOT be regenerated from
scratch, which would drop the annotations three specs of amendment put there.

## What counts as a container, and what does not

Two questions, and **both MUST be yes**:

1. **Does it run its own code or store its own data?** Its own process, its own browser page, its own
   engine — not a folder inside another container's process.
2. **Can it be replaced without rebuilding another container?** It has its own build or publish path.

**Shipping two containers in one release does not merge them.** One atomic deploy swapping a binary and
two browser bundles together is a deployment choice, and a deployment choice MUST NOT be read as an
architectural one. The failure this guards against is the quiet one: a browser bundle with its own
JavaScript filed as "static assets" of the web server, carrying real behaviour with no row, no owner, and
no NFR. Handwritten HTML that runs **no** code of its own is content the web server delivers; the moment
it carries a script, it passes question 1.

### `built` — the one boolean, and its four consequences

A container is inside the boundary whether or not we wrote it. `built:` records which:

| | `built: true` | `built: false` |
|---|---|---|
| An L3 | Yes, where it holds more than one PC | **Never.** No box inside it is ours to draw |
| An `LC` naming it as `container` | Yes | **Never** |
| A heading in `structure-codebase.md` | **Required** | **Never** — no code of ours lives there |
| Listed in a PC's `containers:` | Yes | **Never** — see the matrix below |

`container-built` checks all four. This is what makes the class settled rather than re-argued: a database and a web
server are containers, they carry NFRs, and they still produce no design artifact of ours.

**What IS ours about a `built: false` container MUST have a home outside the C4 set** — its configuration
and any invariant it enforces belong in an `AD-N` or in `cross-cutting.md`. A rule surviving only as a
note beside a C4 box is a rule nobody can find.

### External system — outside the boundary

**The line is who deploys the runtime.** We deploy it, whoever wrote it → container. Someone else
runs it and we call it or configure it through their control plane → external system.

An external system appears at **C4 L1 and nowhere else**. It MUST NOT be registered in `containers`,
MUST NOT be an `LC`'s `container`, and MUST NOT get a heading in the codebase map. What the product
depends on it for lives in `cross-cutting.md` or an integration contract.

### The PC × container matrix

A PC and a container cross, so neither list implies the other — and the crossing is what a builder needs
first: *which container does this promise live in, and is it more than one?*

- The **SSOT is each PC's `containers:`** in `components.yaml`; C4 L2 renders it, and `container-built` fails when the
  two disagree.
- Complete at **G3** for every PC. It is blueprint content, so `mode` does not touch it.
- A PC MUST list every `built: true` container it lives in. Listing only the main one is the error the
  matrix exists to catch.

### Which C4 files exist, and when

`artifact-map.md` owns the schedule: all three at **G3**, at every `mode`. Two conditions belong here.

**L2 MUST be complete** — every container, plus the matrix. **L3 exists once per `built: true` container
holding more than one PC**; a one-PC container needs none because the matrix already places it.

**Not one of the three waits for a spec.** Which container a PC lives in cannot be discovered by a spec,
because a spec picks its tickets from that answer — a spec forced to invent it answers a G3 question with
a fraction of G3's information.

## Cross-cutting

`.how/_platform/cross-cutting.md` holds what is defined once for the whole product, the error envelope first
among them. Every contract references it rather than restating it.

A rule that belongs there MUST NOT also be written as an `AD-N` unless breaking it in one component breaks
another. One fact, one home.

**The platform MAY own things, and owning one costs a row here.** `_platform` is a legitimate owner in every
position that asks which component owns something — a domain entity through `platform_owns`, an inventory row,
an `LC`. Whatever it owns MUST be described under `## Platform-owned` in this file: what it is, its kind, why
no component's promise explains it, who touches it, and the shape every toucher obeys. `entity-one-writer` checks that second
half, because a platform that owns something without documenting it has taken ownership without taking
responsibility.

Four kinds qualify today — data, endpoint, job, screen — and the list is open. What is **not** open is the
test, and `corpus-guide.md` owns it: no single component's promise explains it, **and** more than one
component depends on it. Failing either half, it belongs to a component.

`_platform` is **not** a Product Component — `corpus-guide.md` owns that distinction and the test for when an
entity legitimately belongs here. It has no `mode` and no `risk_accepted`: the documents in this folder exist
at every mode.

## Binding order

Spine first, then the SDD, then the spec's contract. An `SDD-<pc>.md` written before the spine will be rewritten,
because the constraints it was supposed to inherit did not exist yet. A `SPEC.md` written before the SDD has
nothing to project. `AD` ids MUST stay stable so downstream artifacts can cite them.

## Inheritance downward

From `mode: guarded` up, every `AD-N` that reaches a component MUST appear in that component's SDD under
**Inherited Constraints**, quoted rather than paraphrased. Below `guarded` the quoting is not written, and the
spine still binds — an invariant does not stop holding because a document is thin.

## Review is manual here

`bmad-architecture` excludes the spine from `doc_standards` deliberately — the spine is terse by design and
prose polish softens rules that need to stay rigid. Two consequences:

- This guide is installed as `persistent_facts`, not `doc_standards`.
- `bmad-review` over the spine MUST be invoked through `wdi-review` before G3 closes.

## Rules

- The spine MUST stay short enough to be read in one sitting. An `AD-N` nobody remembers is not an invariant,
  it is a document.
- An `AD-N` MUST NOT be added because something feels important. The test is only ever: does breaking this in
  one place break another?
- Structure statements MUST be marked as seeds, and MUST NOT be checked as if they were rules.
- Memlog goes to `.control/memlog/spine.md` via `--path`, never beside the spine.
