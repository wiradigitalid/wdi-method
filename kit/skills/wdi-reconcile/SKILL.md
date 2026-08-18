---
name: wdi-reconcile
description: Use before a gate, or after a batch of changes, to find drift between .what, .how, and .control — against each other and against the rules in .constitution. Scoped to what the gates already passed have actually produced, and to what each component's mode actually demands. Read-only — it reports, it never edits.
---

# WDI Reconcile

Documents drift apart quietly. An SRS gets amended while its SDD does not; a `DEC-` is accepted and never
applied; a story ships behaviour the use case never described. None of this shows up as an error, which is
why it needs a pass that looks for it on purpose.

This skill is **read-only**. It MUST NOT edit anything. Its output is a report, and every fix it
recommends is performed by another skill.

## Step 1 — Scope by gate, then by `mode`

Two filters, and skipping either produces a report that is red where the plan says it should be.

**By gate.** The corpus is built gate by gate, so most of it is legitimately absent most of the time.
Establish which gate the work stands at — `wdi-help` answers that — and check only what has been passed.

| Gate passed | In scope |
|---|---|
| G1 | `brief.md` |
| G2 | + every `_prd/<initiative>/`, UX output wherever it currently sits, `product_components` with `mode` and `risk_accepted` |
| G3 | + every `.what/<pc>/` § UC Catalogue and § Actor Register, `domain-model.md`, `business-rules.md`, the spine, the C4 set, `containers`, the three inventories |
| G4 | + whatever each component's `mode` demands in `.what/<pc>/` and `.how/<pc>/` |
| G5 | + `SPEC.md`, `waves.yaml`, story files, tests, `defects.yaml`, RTM rows |

**By `mode`.** An artifact a component's `mode` does not demand MUST NOT be reported as missing. A
component at `catalog` has an SDD skeleton and no depth, and that is a **finished** state — G4 is skipped
there. Reporting it as a gap is the failure that would make this pass unusable at the setting most
projects run.

An artifact a **later** gate produces MUST NOT be reported as missing either. That is not drift, it is
the plan. The corpus running ahead of the code is likewise normal and deliberate.

A narrower scope MAY be asked for — one Product Component, one initiative, one layer. State the scope
in one line before checking, and say what it excluded.

## Step 2 — Run the validators first

Run `uv run .constitution/method/scripts/validate.py`, and `uv run .constitution/method/scripts/inventory.py` when code
exists. V1–V24 answer everything that can be **counted**, and you MUST NOT re-derive by reading what they
already report. Carry their findings as they came, then spend the reading on what no validator can see.

`.control/generated/` is their output and MUST NOT be read as an independent source. When it is
missing or stale, say so and name `validate.py --generate` rather than working around it.

## Step 3 — What only a reader can find

| Direction | Question |
|---|---|
| Top-down | Does every `applied` `DEC-` actually appear in the files its `touches` names? |
| Bottom-up | Does anything in `.how/<pc>/` describe behaviour that `.what/<pc>/` never promised? |
| Decisions | Is there an `accepted` `DEC-` that was never applied, or an `applied` one with an empty `touches`? The second is V8; the first no validator can see |
| Chain | `BG → CAP → FR/NFR → UC → story → test` — where does it break? |
| Depth | Does any document carry more than its component's `mode` demands? Over-writing is drift too, and it is the direction nobody looks for |
| Vocabulary | Does any document use a domain noun that `.control/product-glossary.md` does not define, or a synonym for one it does? Detect against the rule in `wdi-blueprint`; MUST NOT keep a second rule here |
| Registry | Does `components.yaml` still describe what the corpus contains — a `<pc>` folder with no entry, an `LC` with no prose in the slot its `type` names, a container in the C4 set but not in `containers`, `owns:` claiming an entity another component also claims |
| Inventory | Do the three inventories still match the code? `inventory.py` answers it; carry its findings rather than re-deriving them |
| **Constitution** | Does an artifact break the rule its own guide states? |
| **Homeless output** | Does anything in `_bmad-output/` have no row in the ownership table in `corpus-guide.md`, or a row whose named owner is not installed? |
| **Evidence** | V24 answers the mechanical half — does every cited path still resolve. What is left for a reader: does the file still **contain** what is cited |

The chain check overlaps the validators on purpose. Validators answer what can be counted; this pass
answers what has to be read — a `UC` that exists and is wrong passes V2 and fails here.

### The Constitution check

The other checks compare documents with each other. This one compares a document with the rule that
governs it, and the four failures worth looking for are the ones no ID chain records:

| Looks like | Rule it breaks |
|---|---|
| Solution shape in `.what/` — a table, an endpoint, a framework | `corpus-guide.md`, and it is the most common one |
| A promise appearing first in `.how/` | The same rule, in the other direction |
| A file in the wrong slot | `.what/` numbers are reading order, `.how/` numbers are ABCE classification |
| A layer written by a skill that does not own it | The ownership table in `corpus-guide.md` |
| A rule stated in a `.constitution/method/` file | `status: Reference` — it explains, it MUST NOT bind |
| A `Reference` file contradicting a guide | The guide wins, and the contradiction is a defect to report |

You MUST NOT invent a rule to fail an artifact against. Every finding here MUST quote the guide it comes
from. A file at `status: Draft` MAY be read as guidance but MUST NOT be used to reject anything — that
holds for all three `.constitution/project/codebase-*-guide.md` — and a file at `status: Reference` MUST NOT be cited to reject
anything at all.

### What the Evidence check is, and what it is not

It checks whether **citations still resolve**. It does **not** check whether the code implements the
corpus, and you MUST NOT widen it into that.

A general corpus-versus-code comparison would be red through the middle of every wave, and a check
that is always red is a check people learn to skip. What is already covered elsewhere MUST NOT be
re-reported here:

| Already answered by | Case |
|---|---|
| A red RTM row | Promised, not built yet |
| V2 · V3 | Documented, never scheduled |
| V4 | A story closed with no named test |
| `inventory.py` | The plan and the code disagreeing about a table, endpoint, or screen |

That leaves exactly one gap, and it is the one this check fills: **a descriptive claim about code
that already exists, which has quietly stopped being true.** A file renamed, a function removed, a
route unregistered — nothing in the ID chain moves, so no validator can see it.

Two properties keep the check healthy:

- It fires **only where a citation exists**. Prose with no cited source produces no finding, so there
  is no flood.
- It is cheap: a path and symbol lookup, not a semantic judgement.

A claim the check proves absent MUST be labelled `[MISSING]` in the document rather than deleted —
see the evidence ladder in `sdd-guide.md`, which owns that rule.

## Output — an action matrix

Each finding gets four fields, and the last two are what make the report usable:

| Field | Content |
|---|---|
| What | The drift, stated concretely with both sides quoted |
| Where | File and section on each side |
| Which is right | Your reading, stated as a judgement, not hidden as a fact |
| Who fixes it | The skill that owns the layer needing the change — `wdi-problem` · `wdi-product` · `wdi-blueprint` · `wdi-component` · `wdi-ux` · `wdi-build` · `wdi-init` · `wdi-decision` · `wdi-question` · `wdi-log` · `wdi-systematic-debugging` · a human |

A finding you cannot assign to a fixer MUST be reported as an open question rather than left as an
observation.

Separate **drift** from **conflict** in the report, because they are answered differently: drift has
a right side and needs carrying across; a conflict has no clearly right side and needs deciding.

## Rules

- You MUST NOT edit. Not a typo, not a heading, not a link. The value of a read-only pass is that its
  report can be trusted to describe the state before anything moved.
- You MUST NOT rank a finding as minor because it is small. Vocabulary drift is small and is the one
  that compounds fastest.
- When two documents disagree and neither is clearly right, that is a decision, not a drift. Route it
  to `wdi-decision` and say so.
- An output with no home MUST be reported as a gap in the method, and its home MUST NOT be guessed. The
  gap has nowhere else to surface. Exploration output — research, brainstorming, forge, PRFAQ — is
  homeless **by rule** and MUST NOT be reported.
- Run before every gate, and after any batch of edits that touched one layer without the other.
  Running it only when something feels wrong defeats it — drift is silent by definition.
