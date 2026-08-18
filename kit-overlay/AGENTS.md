# Agent Rules — {product}

<!-- BEGIN:wdi-method -->
This repo uses **WDI Method**. It wraps BMad; it does not replace it. This marked
block is owned by the WDI Method package and is **replaced on every update**.
Product rules belong **outside** it (extra boundaries, `## Code`, stack notes).
A fact written inside this block will be overwritten.

Product identity lives in `.control/registry/index.yaml` (`product.name`, optional
`product.client`). G1 confirms it. This file MUST NOT become a second source of the name.

## Install and update

BMad first, then WDI Method. In the product repo:

```bash
npx bmad-method install
npx wdi-method
```

No subcommand opens the installer TUI. It detects an existing install and offers
**update**. Non-interactive:

```bash
npx wdi-method install --yes
npx wdi-method update --yes
```

BMad: https://github.com/bmad-code-org/BMAD-METHOD
WDI Method: https://github.com/wiradigitalid/wdi-method

A method file MUST NOT be invented here. If a rule is wrong, fix it in the WDI
Method package, then update.

This file is loaded every session; everything else is loaded **lazily**, only when
the task matches.

## Language

**Two settings decide this, and they live in `.control/registry/index.yaml` under `policy:`.** Both are
free text and both default to English:

| Setting | Governs |
|---|---|
| `doc_language` | The prose of working documents in `.what/` · `.how/` · `.control/` |
| `doc_filename_language` | The slug part of a document filename |

Read those two before writing a document. A technical term the industry writes in English MUST be left in
English whatever the setting says — an equivalent MUST NOT be invented for it.

**These files are always English, whatever the settings say:** `AGENTS.md`, `CLAUDE.md`, and everything
under `.constitution/`. They are agent instructions, and they travel to every repo through the
`wdi-method` package. The one exception is `.constitution/project/`, which is this product's own room.

**Always English and never a setting**, because a script matches them:

- method terminology — `DEC` `SRS` `SDD` `UC` `FR` `AD`, the gate names, the values of `mode` and
  `risk_accepted`
- document code prefixes — `UC-` `DEC-` `SRS-`; only the slug after them follows `doc_filename_language`
- markers — `[NEEDS CONFIRMATION]` `[MISSING]` `[ASSUMED]` `[PARTIAL]`, and `yes`/`no` in a `critical`
  column
- registry values — `mode: catalog`, `status: applied`, `risk_accepted: low`. Used as written in prose
  too: one thing, one name
- code identifiers, database columns, config keys — `language-guide.md` owns these

**A corpus written before these settings existed MUST NOT be migrated for them.** The readers accept more
than one language, so existing documents keep working and only new writing follows the setting.

## The thing in your hand → its folder

Read this instead of reasoning about what `.what/` and `.how/` mean.

| The thing in your hand | Its folder |
|---|---|
| A rule, a guide, a template — how we work | `.constitution/` |
| A rule that binds **only this product** | `.constitution/project/` — `update` never writes over it, `promote` never publishes it |
| The explanation of a rule, never a rule itself | `.constitution/method/` |
| A decision, an open question, a registry, a structure map, minutes | `.control/` |
| The brief, a PRD, a use case, a business rule — what is promised | `.what/` |
| The spine, C4, an inventory, an SDD, a contract — how it is built | `.how/` |
| A skill run's working output, and documents that predate the method | `_bmad-output/` |
| Scratch that empties when the task closes | `.work/` |
| The application | named under `## Code` below |

## Layer boundaries

| Layer | Answers | MUST NOT hold |
|---|---|---|
| `.constitution/` | How we work | State, decisions, product content |
| `.control/` | What currently holds and what has been decided | Rules |
| `.what/` | What is promised | Solution shape — tables, endpoints, technology |
| `.how/` | How it is built | Promises to the user |
| `_bmad-output/` | Work in progress; committed, not curated | Anything still correct after its wave has passed |
| `.work/` | Scratch; emptied when a task closes | Secrets, commercial figures, anything meant as authority |

The placement test: **is this file still correct after its wave has passed?** Yes → the corpus. No →
`_bmad-output/`. In doubt → `document/corpus-guide.md`.

The method does not use a `docs/` layer for corpus or rules. A leftover `docs/` folder is inventory
to sort, not a second home.

## Depth and review intensity — two fields, never merged

| Field | Where | Controls |
|---|---|---|
| `mode` | `index.yaml` globally, `components.yaml` per component | **Document depth**, and only that. `catalog` · `outline` · `guarded` · `deep`; default `catalog` |
| `risk_accepted` | `components.yaml` per component | **Review intensity**, and only that. `low` · `medium` · `high` |

Per-component `mode` wins over global, and there is no third scope — `mode` MUST NOT be overridden per
wave or per `SPEC.md`. A component at `mode: catalog` **skips G4 entirely**. Neither field MUST be
derived from the other: one component MAY be thin on purpose and reviewed the hardest.
`document/delivery-flow-guide.md` owns both; `method/rationale.md` says why they are separate.

## The five gates and the fifteen skills

| Gate | Decides | Skill |
|---|---|---|
| **G1 Problem** | What the problem is, whose it is, why it earns work | `wdi-problem` |
| **G2 Product** | What is built, and how it feels to use | `wdi-product` · optional `wdi-ux` |
| **G3 Blueprint** | The whole portrait, once per product | `wdi-blueprint` |
| **G4 Component** | How one component is built — **skipped at `catalog`** | `wdi-component` |
| **G5 Release** | Whether it is done and proven | `wdi-build` |

Before G1 and at the tail of G2: `wdi-init`, five intents — `setup` · `component` · `mode` · `risk` ·
`structure`.

Any time: `wdi-decision` · `wdi-question` · `wdi-log` · `wdi-help` · `wdi-reconcile` · `wdi-review` ·
`wdi-report` · `wdi-systematic-debugging`.

**No BMad skill is invoked directly.** Each has a wrapper, and the wrapper is what checks position,
verifies the result, and lands the memlog.

## What MUST NOT be done

- A method file MUST NOT be invented or patched here to improve the method. If a rule is wrong, it is
  fixed in the WDI Method package, then brought here with `npx wdi-method update`.
- A file in `_bmad-output/prior-knowledge/` MUST NOT be copied into `.what/` or `.how/`. It enters
  the corpus only through the skill that owns the slot.
- `.control/generated/` MUST NOT be written by hand — it is the output of `validate.py` and
  `timeline.py`.
- The two structure maps in `.control/` MUST NOT be edited by hand — `wdi-init` intent `structure`
  re-derives them.
- A `DEC-` with status `applied` MUST NOT be edited, except to record its supersession — status moves
  to `superseded` and names its replacement. A change of mind produces a new `DEC-`.
- A file in `.constitution/method/` MUST NOT be cited as the reason to reject a change. It is
  `status: Reference` — it explains, it does not bind, and where it disagrees with a guide the guide
  wins and the disagreement is a defect.
- More than the component's `mode` demands MUST NOT be written. Exceeding the depth the owner set is
  not diligence.
- `.claude/skills/bmad-*/customize.toml` MUST NOT be edited — it is overwritten on every BMad update;
  customise through `_bmad/custom/`.

## Routing — load a guide when the task matches

| Task | Load |
|---|---|
| Wanting the whole method in five minutes | `.constitution/method/README.md` |
| About to change a rule, and needing to know what breaks | `.constitution/method/rationale.md` |
| Asking whether a document exists at this `mode`, or where a file goes | `.constitution/method/artifact-map.md` |
| Unsure whether a file may exist in this repo | `.constitution/repo-guide.md` |
| Unsure where a file lives | `.constitution/document/corpus-guide.md` |
| Unsure what a method term means | `.constitution/method-glossary.md` |
| Unsure about a domain term | `.control/product-glossary.md` |
| Looking for a non-technical fact — a domain, an account, a legal entity, a locked date | `.control/project-non-technical-log.md` |
| Naming anything — a code identifier, a file, a database column | `.constitution/language-guide.md` |
| Asking "which gate now, what next" | `.constitution/document/delivery-flow-guide.md` · skill `wdi-help` |
| Setting or changing `mode` or `risk_accepted` | `.constitution/document/delivery-flow-guide.md` · skill `wdi-init` |
| Invoking a BMad skill | `.constitution/document/bmad-guide.md` · `document/bmad-skill-register.md` |
| Writing or reviewing a product brief | `.constitution/document/brief-guide.md` |
| Writing or reviewing a PRD | `.constitution/document/prd-guide.md` |
| Writing or reviewing UX | `.constitution/document/ux-guide.md` |
| Writing or reviewing an SRS | `.constitution/document/srs-guide.md` |
| Writing or reviewing an SDD | `.constitution/document/sdd-guide.md` |
| Writing the spine, an `AD-N`, C4, or one of the three inventories | `.constitution/document/architecture-guide.md` |
| Opening, accepting, or applying a `DEC-` | `.constitution/document/decision-guide.md` |
| Writing or reading a structure map | `.constitution/structure-guide.md` |
| Looking for where code lives, or placing new code | `.control/structure-codebase.md` |
| Looking for where a document lives | `.control/structure-document.md` |
| Writing or reviewing code | `.constitution/codebase/stack-guide.md` · `conventions-guide.md` · `brownfield-guide.md` |

All three `codebase/*-guide.md` start as `status: Draft`. While they are, their contents MAY be read
as guidance but MUST NOT be used to reject a change.

The two structure maps MUST NOT be installed as `doc_standards` — they are facts, not standards. Nor
MUST anything in `.constitution/method/`; `status: Reference` forbids it.

## Bugs, decisions, questions

- A bug, a failing test, or unexpected behaviour → skill `wdi-systematic-debugging`, **before** any
  fix is proposed.
- A decision worth remembering → skill `wdi-decision` → `.control/decisions/`. Recording is **not
  mandatory**: if the answer to *why is it like this* is readable from the code, it MUST NOT be
  recorded. One case is mandatory — contradicting an `AD-N`.
- Something that cannot be decided now → skill `wdi-question` → `.control/questions/`. The default
  class is `assumptions.md`, not `blocking.md`; filing something as blocking "to be safe" is the
  habit that produced unreadable question lists.
- A non-technical fact that constrains the build → skill `wdi-log` intent `fact` →
  `.control/project-non-technical-log.md`.

## Method policy

- A skill MUST NOT be invoked automatically. Name the one that fits and wait for the owner's
  go-ahead — this holds even when the skill's own description says it must be used. Reading a
  skill as reference is fine.
- `.work/` is not production code. It MUST NOT be imported by the application, and MUST be
  excluded when searching for code.
<!-- END:wdi-method -->

## Code

Rewrite this section for the product. Stack, how to run tests, and known pitfalls belong here.
`wdi-init` intent `structure` derives `.control/structure-codebase.md`; do not duplicate that map.
