---
status: Reference
---

# `.constitution/` — index

Method files arrive from the public WDI Method package via `npx wdi-method install`
or `update`. Load [`constitution.md`](constitution.md) before acting. Guides are
loaded **lazily** — only when the task matches, and every guide states when on its
own **Loaded when:** line.

Every file here carries a `status:` — Article 4 owns the five values. Only `Accepted` binds;
`Reference` explains and MUST NOT be cited to reject a change. A template carries no status of its
own, because its frontmatter belongs to the artifact it produces.

A file this product added (one that is not in the snapshot) stays here across `update` and MUST be
listed from `constitution.md` Article 2 or from `AGENTS.md` routing — this index is overwritten on
every update.

## `method/` — the explanation, `status: Reference`

Never a rule. When it disagrees with a guide, the guide wins and the disagreement is a defect.

| File | Opened when |
|---|---|
| [`method/README.md`](method/README.md) | You want the whole shape in five minutes — five gates, two settings, fifteen skills, WDI ↔ BMad |
| [`method/artifact-map.md`](method/artifact-map.md) | "Where does this file go", or "does this document exist at my `mode`" |
| [`method/rationale.md`](method/rationale.md) | Before changing a rule, to know what you would break |
| [`method/portability.md`](method/portability.md) | Which files are the method and which are the product; how promote and install move them |

## Cross-domain

| File | Loaded when |
|---|---|
| [`repo-guide.md`](repo-guide.md) | Adding a file that is neither code nor corpus; the content boundary, `.work/`, cross-repo references |
| [`language-guide.md`](language-guide.md) | Naming anything — a code identifier, a code file, a document file |
| [`method-glossary.md`](method-glossary.md) | Unsure what a method term means — layer, wave, Product Component, ID code |
| [`structure-guide.md`](structure-guide.md) | Writing or checking the two structure maps in `.control/` |

## `document/` — document rules

| File | Governs |
|---|---|
| [`corpus-guide.md`](document/corpus-guide.md) | Where a file lives. Read before the other guides |
| [`delivery-flow-guide.md`](document/delivery-flow-guide.md) | Five gates, `mode`, `risk_accepted`, the gate checklists, units of work, wave size, Fast Path, the story-closing checklist, change control |
| [`bmad-guide.md`](document/bmad-guide.md) | How BMad skills are used here; classes A–D, the read-write map, memlog |
| [`bmad-skill-register.md`](document/bmad-skill-register.md) | The installed BMad skills with the documents each reads and writes |
| [`brief-guide.md`](document/brief-guide.md) · [`prd-guide.md`](document/prd-guide.md) · [`ux-guide.md`](document/ux-guide.md) | The G1 and G2 artifacts |
| [`srs-guide.md`](document/srs-guide.md) · [`sdd-guide.md`](document/sdd-guide.md) | The G3 and G4 artifacts, per Product Component |
| [`architecture-guide.md`](document/architecture-guide.md) | The architecture spine, `AD-N`, C4, and the three inventories |
| [`decision-guide.md`](document/decision-guide.md) | `DEC-`: the one test for recording at all, shape, global numbering, the `draft → accepted → applied` ladder, supersession |
| [`templates/`](document/templates/) | Templates, one per kind of document; they MUST be copied, and MUST NOT be reproduced from memory |

## `codebase/` — code rules

All three are written by the **project**, not the kit. While `Draft`, their contents MAY be read as
guidance but MUST NOT be used to reject a change.

[`stack-guide.md`](codebase/stack-guide.md) · [`conventions-guide.md`](codebase/conventions-guide.md) · [`brownfield-guide.md`](codebase/brownfield-guide.md)

## `scripts/`

`validate.py` — registry gates and the `.control/generated/` generator. `timeline.py` — the time
dimension from git history. `inventory.py` — derives the three inventories from code and reports the
difference against the plan; it MUST NOT patch either side into agreement. All three run through
`uv run`.
