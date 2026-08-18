---
type: structure
scope: codebase
verified: '{YYYY-MM-DD}'      # the day the tree was actually read
commit: '{sha}'               # the commit it was read at — staleness is measured against this
---

# Codebase Structure

<!-- TEMPLATE GUIDE — act on these comments, then delete them.

     This file is DESCRIPTIVE. It states what the code tree looks like today. It MUST NOT carry
     naming rules (conventions-guide.md), versions (stack-guide.md), or ratified legacy shapes
     (brownfield-guide.md) — reference them instead.

     Written and refreshed only by `wdi-init` intent `structure`, never by hand. Rules for both maps live in
     .constitution/method/structure-guide.md.

     THE SHAPE: annotated trees, not prose. Folders are complete; files are marked ★ inline and only
     when they earn it. A tree that lists every file is unmaintainable, and an unmaintainable map
     stops being read — that is how every source-tree document before this one died.

     THREE SECTIONS, and the split is by DEPLOYABILITY, not by size or importance:
       Top level   every base folder in the repo root
       Container   runs or deploys on its own — the same word C4 L2 and components.yaml use
       Library     an includable artifact — compiled or imported into something else, never run

     "Container" is the kit's word, defined in templates/c4.md and carried by every LC's `container`
     field. It MUST NOT be swapped for "application", "service", or "app" here — a synonym for a
     term that already has a glossary entry is drift, and `wdi-reconcile` hunts for it. It does not
     mean a Docker image; packaging is a separate question.

     A unit that is neither is not a unit; it stays a line in Top level. When a unit stops being
     separately deployable, it MUST move sections rather than keep its old heading. -->

## Verified

<!-- One line: date, commit SHA, and how the tree was read. If the commit is no longer an ancestor
     of HEAD, this map is stale and MUST be refreshed before a gate reads it. -->

## Top level

<!-- Every base folder in the repo root, COMPLETE — including the dull ones. An unlisted folder is
     the one people misuse, because nothing told them what it was for. Tag each entry so the two
     sections below are predictable: [container] · [lib] · [docs] · [tooling] · [generated]. One
     line of purpose per entry; no second line. -->

```text
{repo-root}/
├── {unit}/                   # [container] what it is answerable for
├── {unit}/                   # [lib] ...
└── {folder}/                 # [docs] ...
```

## Containers

<!-- One subsection per unit that runs or deploys on its own. Repeat the block below verbatim per
     unit; if there is only one, there is still a subsection — a repo grows a second container
     without warning.

     Heading names MUST match the `container` values used in components.yaml, so an LC's container
     can be checked against this map instead of trusted. A container with no code in this repo MUST
     NOT get a subsection — it belongs to c4-l2-containers.md. A folder that builds more than one
     container MUST say which. -->

### {container}

<!-- One line: what it is, and how it ships. Then the tree: folder convention first, ★ on the files
     that earn it. Descend only until directories stop carrying distinct roles, and describe a
     repeating shape ONCE with a placeholder such as <feature>/ rather than per instance. -->

```text
{container}/
├── {entry-file}              # ★ ENTRY: what execution actually does first
├── {folder}/                 # convention: what belongs here
│   └── {file}                # ★ why this one is key
└── {folder}/<feature>/       # the shape every feature repeats
    ├── {sub}/                #   what goes in it
    └── {sub}/                #   ...
```

<!-- One line, only when the unit has one: the authoritative call direction through those folders.
     A builder who gets this wrong writes code that works and is still wrong. Cut if there is none;
     do not invent one to fill the slot. -->

**Flow:** {layer} → {layer} → {layer}

## Libraries

<!-- One subsection per includable artifact — compiled into or imported by something else, never
     deployed on its own. A library is deliberately NOT a container, and MUST NOT appear at C4 L2.

     Same block shape as a container, minus the entry point: a library that has one is a container
     wearing the wrong label. -->

### {library}

<!-- One line: what it holds, and who consumes it. Then the annotated tree. -->

```text
{library}/
├── {folder}/                 # convention: what belongs here
│   └── {file}                # ★ why this one is key
└── {folder}/
```

**Consumed by:** {units}

## Generated

<!-- Anything not written by hand, with its generator: codegen output, vendored trees, migration
     snapshots. A generated folder edited by hand is a defect, so it MUST be named here even when it
     looks like ordinary source. Cut the section if there is none. -->

| Path | Generated by |
| --- | --- |

## Unclaimed

<!-- Folders that exist but no one can state a purpose for. These are findings, not layout. Leave
     them here, named, until they are claimed or deleted — inventing a purpose to empty this section
     is the failure mode it exists to catch. Cut the section only when it is genuinely empty. -->

---

<!-- Keep this legend last, and keep it one line. -->

★ = key file: entry point, wiring root, the single place a rule is enforced, or a file that must be
opened before behaviour in its folder can be changed.
