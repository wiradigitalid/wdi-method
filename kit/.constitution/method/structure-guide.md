---
status: Accepted
---

# Structure Guide

**Loaded when:** writing, reading, or refreshing a structure map — `.control/structure-codebase.md`
or `.control/structure-document.md`.

## Two maps

| Map | Describes | Derived | Refreshed by |
|---|---|---|---|
| `.control/structure-codebase.md` | The code tree: what runs, what it is built from, where new code goes | `wdi-init` intent `structure` | `wdi-init` intent `structure` |
| `.control/structure-document.md` | The corpus tree: which layers and slots actually carry content today | `wdi-init` intent `structure` | `wdi-init` intent `structure` |

Both ship as empty skeletons, so the slot is taken from day one. The first run replaces a skeleton
**wholesale** rather than filling it in; a half-derived map that still carries skeleton headings
cannot be told apart from a stale one. The intent MAY be run read-only — derive, report the drift,
write nothing — and that is the right mode when the caller is unsure.

**The maps live in `.control/`, this guide lives here, and the split is deliberate.** A guide states
a rule that holds before the thing exists; a map states what is currently true. That is the same
line the kit already draws between `decision-guide.md` and `.control/decisions/`, and between
`corpus-guide.md` and `.control/registry/`. The two MUST NOT be merged, and a map MUST NOT be moved
into `.constitution/` because it happens to be read alongside these guides.

Consequence worth knowing: `.control/` is `{project_knowledge}`, so both maps are visible to the
BMad skills that read it. That is intended — a builder that knows where code goes is the point.

## Descriptive, not prescriptive — the line that MUST hold

This is the whole reason the maps can exist without colliding with the guides already in
`.constitution/`.

| Question | Answered by |
|---|---|
| Where does this live, and what is already there? | **structure map** |
| Which layer owns it, and what is it named? | `document/corpus-guide.md` |
| How is code named, and which patterns apply? | `../project/codebase-conventions-guide.md` |
| What is it built with, and on which version? | `../project/codebase-stack-guide.md` |
| Which legacy shapes are ratified rather than fixed? | `../project/codebase-brownfield-guide.md` |

- A structure map MUST NOT restate a naming rule, a layer rule, or a version. It MUST reference the
  guide that owns it.
- A guide MUST NOT carry a directory tree. A tree in a guide goes stale silently, because nothing
  refreshes it.
- Where a map and a guide disagree, the **guide** wins on the rule and the **map** wins on the fact.
  The disagreement itself MUST be reported, not smoothed over — one of the two is lying.

## What a map MUST contain

1. A **Verified** line: date plus the commit the tree was read at.
2. A **top-level tree**: every base folder in the root, complete, one annotated line each.
3. A **section per unit**, each carrying its folder convention as an annotated tree.
4. **Key files marked `★` inline**, inside those trees.

Nothing else. A map that also explains how the system works has become an architecture document,
and `.how/` already owns that.

The form is an **annotated tree**, not prose and not a file table. A tree shows convention and
location in the same glance, and a `★` next to a filename is read at the moment it matters. Both
maps MUST close with the one-line legend for `★`.

## How units are split

Each map splits its sections along the axis its reader is lost on, and the two axes differ:

| Map | Sections | Split by |
|---|---|---|
| `structure-codebase.md` | Containers · Libraries · the non-unit sections below | **Deployability** |
| `structure-document.md` | One per layer that carries content | **Layer** |

For the codebase map the distinction is exact and MUST NOT be softened:

- A **container** runs its own code or stores its own data, and can be replaced without rebuilding
  another one. `architecture-guide.md` owns the two-question test; this map only applies it. The term
  MUST NOT be renamed to "application", "service", or "app" here — a synonym for a term that already
  has a glossary entry is drift, and `wdi-reconcile` hunts for it. It does not mean a Docker image.
- A **library** is an includable artifact — compiled into or imported by something else, never run
  on its own. A library with an entry point is a container wearing the wrong label, and a library
  MUST NOT appear at C4 L2.
- Anything that is neither is not a unit. It stays a line in the top-level tree, or in one of the
  non-unit sections below.
- A unit that stops being separately deployable MUST move sections, not keep its old heading.

### The registry match is one-directional

**Every container heading MUST be a container registered in `components.yaml`. Not every registered
container gets a heading.** Reading it both ways makes the rule unsatisfiable: a `built: false` container
— a database, a web server — MUST be registered, because it runs inside the boundary and carries NFRs,
and MUST NOT get a heading, because no code of ours lives there. So the check is **heading = exactly the
`built: true` containers**, and `container-built` runs it. `c4-l2-containers.md` still owns the list itself.

### Sections that are not units

Containers and Libraries are the unit sections. A map MAY also carry sections for what is not a unit at
all, and these MUST NOT be dressed up as containers to earn a place:

| Section | Holds |
|---|---|
| **Tooling** | Scripts run by a human or by CI, never deployed |
| **Generated** | Output, named with its generator — that is what makes a hand edit visible |
| **Unclaimed** | A folder that exists with no stated purpose. A finding, not a category |

The list is open, the test is not: a section that is neither a unit nor one of these MUST say in one line
why it exists.

## Base folders — complete

- MUST list every base folder that exists, including the ones that look uninteresting. An unlisted
  folder is the one people misuse, because nothing told them what it was for.
- MUST descend only until directories stop carrying distinct roles. A shape that repeats MUST be
  described once, generically, rather than enumerated per instance.
- MUST mark a folder that exists but has no stated purpose as unclaimed instead of inventing one.
  An unclaimed folder is a finding, and `wdi-init` MUST report it.
- MUST NOT list a folder that the architecture implies but no file has created yet.

## Key files — selective

A file earns a `★` only if it passes one of these:

- It is an entry point, a composition root, or where dependencies get wired.
- It is the single place a rule is enforced for the whole tree below it.
- An agent asked to change behaviour in that folder would have to open it first.
- Removing it would change what the folder *is*, not merely what it does.

Everything else MUST be left out. Completeness at file level is what killed every source-tree
document that came before: it is impossible to keep true, so it stops being read.

A folder with no key file MUST still appear in the tree. Folders are complete; files are not.

## Freshness — this is a living document

- The **Verified** line MUST carry a date and a commit SHA. Without the SHA, staleness cannot be
  measured, only felt.
- A map MUST be refreshed when a base folder is born or removed, when a key file moves or is
  renamed, when a project or container is added, or when a key file's role changes.
- **Spec close** carries this hook — it left the ticket-closing checklist along with four other items,
  because a structural change is visible at the end of a spec and guessed at the end of a ticket.
- A map MUST NOT be edited by hand. `wdi-init` intent `structure` re-derives it from the actual tree;
  a hand edit records what someone remembers, and memory is exactly what the map exists to replace.
- A map whose **Verified** commit is no longer an ancestor of `HEAD` SHOULD be treated as stale, and
  MUST be refreshed before a gate that reads it.

## `structure-codebase.md` — specifics

- Born as a skeleton listing only what exists. On an empty repo that is almost nothing, and that is
  correct: writing the tree the spine implies means guessing.
- Each unit's tree MUST show its **folder convention** — including the shape a feature repeats,
  written once with a placeholder, never enumerated per feature.
- Each container MUST mark its entry point and its composition root with `★`. A container whose
  tree has neither has not been read properly.
- Each container SHOULD carry one **Flow** line: the authoritative call direction through its
  folders. A builder who gets that wrong writes code that works and is still wrong. MUST NOT be
  invented where none exists.
- Each library MUST state who consumes it. A library nobody consumes is a finding.
- Generated output MUST be named with its generator, even when it looks like ordinary source — that
  is what makes a hand edit visible.
- MUST NOT carry framework versions, and MUST NOT repeat the suffix list from
  `conventions-guide.md`. Where new code goes is answered by the convention tree itself; how it is
  named is not this file's question.

## `structure-document.md` — specifics

- The four layers and the workspace are fixed by `corpus-guide.md`. This map records which of them
  actually carry content: which Product Component folders exist, which slots have been split out of
  a kernel, which registries are populated.
- MUST reference the placement test rather than restating it, and MUST NOT explain slot numbering —
  `corpus-guide.md` owns both.
- MUST list every Product Component folder that exists in `.what/` or `.how/`, and MUST flag any
  that exists on one side only. A PC with an SRS and no SDD is drift, not layout.
- Product Component folders MUST live in the table, and MUST NOT also be expanded in the per-layer
  trees. Maintaining the same fact in two places is how one of them starts lying.

## File names MUST survive every OS the repo is cloned on

This is the one structural rule that is not about where a file sits but about whether it can exist at
all. It applies to every file any skill in this method creates — corpus documents, generated tables,
spec folders, and code alike.

| Rule | Detail |
|---|---|
| Forbidden characters | `\ / : * ? " < > \|` MUST NOT appear in a file or folder name |
| Substitution | A forbidden character MUST be replaced by `-` or dropped, and the substitution MUST be consistent across the repo |
| Trailing characters | A name MUST NOT end in a space or a `.` — Windows strips both silently, and the read path then no longer matches the write path |
| Length | A single path segment SHOULD stay under 255 characters |

The failure this prevents is not cosmetic. A repository whose branches carry `:` in a filename
**cannot be checked out on Windows at all** — `git checkout` fails outright, and recovering the
content takes per-blob extraction plus a rename map. That has happened in a sibling repo, which is
why this is stated as a rule rather than left to taste.

A name derived from something else — an endpoint path, a URL, a title — MUST be sanitised at the
moment it becomes a filename, and the mapping SHOULD be recorded when it is not reversible by
inspection.

## Writing rules

Inherited from `.constitution/`: normative keyword on every instruction, concise, no duplication,
English, SHOULD stay under 200 lines. A map that outgrows 200 lines is marking files that never
earned a `★` — cut those, never the folders.
