---
status: Reference
---

# `.constitution/method/` — index

`.constitution/` holds **exactly two folders**, and the folder is what says who owns a file:

| Folder | Owner | `update` | `promote` |
|---|---|---|---|
| `method/` — you are in it | the method | **overwritten** in full | carries it into the package |
| [`../project/`](../project/) | this product | **never touched** — seeded once when absent | never carries it, so your rules cannot be published |

Load [`constitution.md`](constitution.md) and [`../project/constitution.md`](../project/constitution.md)
before acting: Articles 3, 4, 6, 7 are here, Articles 1, 2, 5 are yours. Guides are loaded **lazily** —
only when the task matches, and every guide states when on its own **Loaded when:** line.

Every file here carries a `status:` — Article 4 owns the five values. Only `Accepted` binds;
`Reference` explains and MUST NOT be cited to reject a change. A template carries no status of its
own, because its frontmatter belongs to the artifact it produces.

**A file this product adds MUST go in [`../project/`](../project/), not here** — anything in `method/`
is replaced on the next update, without warning, because that is what `method/` means. This index is
overwritten too.

## `why/` — the explanation, `status: Reference`

Never a rule. When it disagrees with a guide, the guide wins and the disagreement is a defect.

| File | Opened when |
|---|---|
| [`why/README.md`](why/README.md) | You want the whole shape in five minutes — five gates, two settings, sixteen skills, WDI ↔ BMad |
| [`why/artifact-map.md`](why/artifact-map.md) | "Where does this file go", or "does this document exist at my `mode`" |
| [`why/mode-risk-map.md`](why/mode-risk-map.md) | A `mode` and a `risk_accepted` are set and you want the two side by side — all twelve cells |
| [`why/rationale.md`](why/rationale.md) | Before changing a rule, to know what you would break |
| [`why/portability.md`](why/portability.md) | Which files are the method and which are the product; how promote and install move them |

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

## Code rules — in the room, not here

All three are written by the **product**, so they live in [`../project/`](../project/) and no update
touches them at any `status:`. While `Draft`, their contents MAY be read as guidance but MUST NOT be
used to reject a change.

[`stack-guide.md`](../project/codebase-stack-guide.md) · [`conventions-guide.md`](../project/codebase-conventions-guide.md) · [`brownfield-guide.md`](../project/codebase-brownfield-guide.md)

## `scripts/`

`validate.py` — registry gates and the `.control/generated/` generator. `timeline.py` — the time
dimension from git history. `inventory.py` — compares the three inventories against the code
and reports the difference; it MUST NOT patch either side into agreement. It reads no code itself:
the patterns live in `../project/inventory-readers.py`, because comparing is generic and reading a
stack is not. That file ships as a skeleton and `wdi-init` intent `readers` writes it for the repo
in front of it. All three run through `uv run`.
